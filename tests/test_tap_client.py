"""Unit tests for src/tap_client.py."""
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import requests

from src.tap_client import TAPError, build_query, fetch_csv, query_to_dataframe


class TestTapClient(unittest.TestCase):
    """Test TAP client query building, HTTP logic, and error handling."""

    def test_build_query_defaults(self):
        """Test default query building."""
        query = build_query()
        self.assertEqual(query, "SELECT * FROM pscomppars ORDER BY pl_name")

    def test_build_query_with_parameters(self):
        """Test query building with where clause, order by, and limit."""
        query = build_query(
            table="pscomppars",
            where="tran_flag = 1",
            order_by="sy_dist ASC",
            limit=50,
        )
        self.assertEqual(
            query,
            "SELECT TOP 50 * FROM pscomppars WHERE tran_flag = 1 ORDER BY sy_dist ASC",
        )

    def test_build_query_curated_only(self):
        """Test building curated query."""
        query = build_query(curated_only=True, limit=10)
        self.assertTrue(query.startswith("SELECT TOP 10 pl_name,"))
        self.assertIn("FROM pscomppars", query)

    @patch("requests.Session.post")
    def test_fetch_csv_success(self, mock_post):
        """Test successful CSV fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "pl_name,hostname,pl_orbper\nKepler-186 f,Kepler-186,129.9\n"
        mock_post.return_value = mock_response

        csv_text = fetch_csv("SELECT pl_name FROM pscomppars", retries=0)
        self.assertIn("Kepler-186 f", csv_text)

    @patch("requests.Session.post")
    def test_fetch_csv_tap_xml_error_handling(self, mock_post):
        """Test handling of XML error returned with HTTP 200."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<?xml version='1.0'?><VOTABLE><INFO name=\"QUERY_STATUS\" value=\"ERROR\">Syntax error</INFO></VOTABLE>"
        mock_post.return_value = mock_response

        with self.assertRaises(TAPError):
            fetch_csv("SELECT INVALID FROM pscomppars", retries=0)

    @patch("requests.Session.post")
    def test_fetch_csv_http_400_error(self, mock_post):
        """Test handling of HTTP 400 bad request error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Query syntax error"
        mock_post.return_value = mock_response

        with self.assertRaises(TAPError):
            fetch_csv("SELECT * FROM non_existent_table", retries=0)

    @patch("requests.Session.post")
    def test_query_to_dataframe_parsing(self, mock_post):
        """Test DataFrame parsing from CSV text."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = (
            "pl_name,hostname,pl_orbper,pl_rade\n"
            "TRAPPIST-1 e,TRAPPIST-1,6.099,0.92\n"
            "TRAPPIST-1 f,TRAPPIST-1,9.206,1.04\n"
        )
        mock_post.return_value = mock_response

        df = query_to_dataframe("SELECT * FROM pscomppars", retries=0)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ["pl_name", "hostname", "pl_orbper", "pl_rade"])
        self.assertEqual(df.iloc[0]["pl_name"], "TRAPPIST-1 e")


if __name__ == "__main__":
    unittest.main()

