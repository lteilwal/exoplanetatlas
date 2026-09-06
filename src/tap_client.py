"""
NASA Exoplanet Archive Table Access Protocol Client.

HTTP client for querying the NASA Exoplanet Archive
synchronous TAP endpoint via ADQL/SQL

Reference:
    https://exoplanetarchive.ipac.caltech.edu/docs/TAP/TAPclient.html
"""
from __future__ import annotations

import logging
import time
from io import StringIO
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import requests

from . import config
from .schema import build_curated_select_clause

logger = logging.getLogger(__name__)


class TAPError(RuntimeError):
    """Raised when the NASA TAP service returns an error or request fails."""


def build_query(
    table: Optional[str] = None,
    select: Optional[str] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
    curated_only: bool = False,
) -> str:
    """
    Construct a validated ADQL (Astronomical Data Query Language) query string.

    Parameters
    ----------
    table : str, optional
        Target table name. Defaults to config.DEFAULT_TABLE ('pscomppars').
    select : str, optional
        Custom SELECT clause. If omitted and curated_only=True, selects all
        columns in the curated schema; otherwise selects '*'.
    where : str, optional
        WHERE condition filter (without the 'WHERE' keyword).
    order_by : str, optional
        ORDER BY column/expression (without the 'ORDER BY' keywords).
        Defaults to 'pl_name'.
    limit : int, optional
        Row count limit (uses ADQL TOP syntax). None or <= 0 means unlimited.
    curated_only : bool, default False
        If True and select is None, automatically builds a SELECT clause
        containing all columns from the curated schema.

    Returns
    -------
    str
        Constructed ADQL query string.
    """
    table_name = table or config.DEFAULT_TABLE

    if select:
        columns_part = select.strip()
    elif curated_only:
        columns_part = build_curated_select_clause()
    else:
        columns_part = "*"

    top_clause = f"TOP {limit} " if limit and limit > 0 else ""
    query = f"SELECT {top_clause}{columns_part} FROM {table_name}"

    if where:
        query += f" WHERE {where.strip()}"

    order = order_by if order_by is not None else "pl_name"
    if order:
        query += f" ORDER BY {order.strip()}"

    return query


def fetch_csv(
    query: str,
    timeout_seconds: Optional[int] = None,
    retries: Optional[int] = None,
    backoff_seconds: Optional[float] = None,
) -> str:
    """
    Execute an ADQL query via NASA Exoplanet Archive TAP/sync and return raw CSV text.

    Parameters
    ----------
    query : str
        ADQL query string.
    timeout_seconds : int, optional
        HTTP request timeout in seconds.
    retries : int, optional
        Number of retry attempts on transient network/server failures.
    backoff_seconds : float, optional
        Initial backoff delay in seconds for exponential backoff.

    Returns
    -------
    str
        Raw CSV string.

    Raises
    ------
    TAPError
        If the TAP server returns an error code, error XML payload, or fails all retries.
    """
    timeout = timeout_seconds or config.HTTP_TIMEOUT_SECONDS
    max_retries = retries if retries is not None else config.HTTP_RETRIES
    backoff = backoff_seconds if backoff_seconds is not None else config.HTTP_BACKOFF_SECONDS

    url = config.NASA_TAP_URL
    headers = {
        "User-Agent": config.HTTP_USER_AGENT,
        "Accept": "text/csv, text/plain",
    }
    payload = {
        "query": query,
        "format": "csv",
    }

    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(1, max_retries + 2):
        try:
            logger.debug(f"Executing TAP query (attempt {attempt}/{max_retries + 1}): {query[:120]}...")
            start_time = time.time()
            response = session.post(url, data=payload, timeout=timeout)
            elapsed = time.time() - start_time

            # Check HTTP status
            if response.status_code == 200:
                response_text = response.text

                # Check if TAP returned an XML error within a 200 OK wrapper
                if response_text.lstrip().startswith("<?xml") and ("<VOTABLE" in response_text or "<INFO name=\"QUERY_STATUS\" value=\"ERROR\"" in response_text):
                    error_msg = response_text[:1000].strip()
                    raise TAPError(f"TAP service returned an error document: {error_msg}")

                logger.info(
                    f"TAP query successful ({len(response_text) / 1024:.1f} KB in {elapsed:.2f}s)"
                )
                return response_text

            # Handle 5xx server errors with retry
            if 500 <= response.status_code < 600:
                if attempt <= max_retries:
                    sleep_time = backoff * (2 ** (attempt - 1))
                    logger.warning(
                        f"TAP server error HTTP {response.status_code}. Retrying in {sleep_time:.1f}s..."
                    )
                    time.sleep(sleep_time)
                    continue

            # 4xx client errors or exhausted retries
            error_snippet = response.text[:1000].strip()
            raise TAPError(
                f"TAP request failed with HTTP status {response.status_code}: {error_snippet}"
            )

        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt <= max_retries:
                sleep_time = backoff * (2 ** (attempt - 1))
                logger.warning(
                    f"Network error on TAP query (attempt {attempt}/{max_retries + 1}): {exc}. "
                    f"Retrying in {sleep_time:.1f}s..."
                )
                time.sleep(sleep_time)
            else:
                raise TAPError(
                    f"TAP query failed after {max_retries + 1} attempts due to network error: {exc}"
                ) from exc

    raise TAPError("Unexpected exit from TAP query retry loop")


def query_to_dataframe(query: str, **kwargs: Any) -> pd.DataFrame:
    """
    Execute an ADQL query and parse the CSV output into a Pandas DataFrame.

    Parameters
    ----------
    query : str
        ADQL query string.
    **kwargs : Any
        Passed to `fetch_csv`.

    Returns
    -------
    pd.DataFrame
        DataFrame containing query results with untruncated columns.
    """
    csv_text = fetch_csv(query, **kwargs)

    # Read CSV without truncating or automatic type coercion that destroys precision
    df = pd.read_csv(
        StringIO(csv_text),
        low_memory=False,
        keep_default_na=True,
        na_values=["", "null", "NULL", "NaN", "None"],
    )

    logger.info(f"Loaded DataFrame: {df.shape[0]} rows x {df.shape[1]} columns")
    return df


def fetch_raw_data(
    output_path: Optional[str | Path] = None,
    query: Optional[str] = None,
    curated_only: bool = False,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """
    High-level ingestion helper: query TAP, write raw CSV to disk, and return DataFrame.

    Parameters
    ----------
    output_path : str or Path, optional
        Destination filepath for the raw CSV. Defaults to config.RAW_CSV_FILE.
    query : str, optional
        Custom ADQL query. If None, builds a query using curated_only and limit settings.
    curated_only : bool, default False
        If True and query is None, queries only the curated schema columns (~85 columns)
        for high-speed retrieval.
    limit : int, optional
        Optional row limit for test/debug queries.

    Returns
    -------
    pd.DataFrame
        Raw fetched DataFrame.
    """
    config.ensure_directories()
    target_path = Path(output_path) if output_path else config.RAW_CSV_FILE

    if query is None:
        query = build_query(curated_only=curated_only, limit=limit)

    logger.info(f"Fetching raw exoplanet data from NASA TAP service")
    logger.debug(f"Executed query: {query}")

    df = query_to_dataframe(query)

    # Ensure parent directory exists and save raw data
    target_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_path, index=False)
    logger.info(f"Raw data successfully saved to: {target_path} ({df.shape[0]} rows)")

    return df