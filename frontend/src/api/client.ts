/**
 * Typed API Client for Exoplanet Atlas Backend Service.
 */
import {
  CatalogFilterParams,
  PaginatedResponse,
  PlanetAISummaryResponse,
  PlanetDetail,
  PlanetQAResponse,
  PlanetSummary,
  StarDetail,
  StarSummary,
  StatsResponse,
  SystemDetail,
  SystemSummary,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

function buildQueryString(params: Record<string, any>): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, String(value));
    }
  }
  const str = query.toString();
  return str ? `?${str}` : "";
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    let message = `API request failed with status ${response.status}`;
    try {
      const parsed = JSON.parse(errorBody);
      if (parsed.detail) {
        message = parsed.detail;
      }
    } catch {
      // Use fallback message
    }
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  // Stats
  async getStats(): Promise<StatsResponse> {
    return request<StatsResponse>("/stats");
  },

  // Planets
  async getPlanets(params: CatalogFilterParams = {}): Promise<PaginatedResponse<PlanetSummary>> {
    const qs = buildQueryString(params);
    return request<PaginatedResponse<PlanetSummary>>(`/planets${qs}`);
  },

  async getPlanet(idOrName: string): Promise<PlanetDetail> {
    const encoded = encodeURIComponent(idOrName.trim());
    return request<PlanetDetail>(`/planets/${encoded}`);
  },

  // AI Summaries & Grounded Q&A
  async getPlanetAiSummary(planetName: string): Promise<PlanetAISummaryResponse> {
    const encoded = encodeURIComponent(planetName.trim());
    return request<PlanetAISummaryResponse>(`/ai/planets/${encoded}/summary`);
  },

  async askPlanetAiQuestion(planetName: string, question: string): Promise<PlanetQAResponse> {
    const encoded = encodeURIComponent(planetName.trim());
    return request<PlanetQAResponse>(`/ai/planets/${encoded}/qa`, {
      method: "POST",
      body: JSON.stringify({ question }),
    });
  },

  async chatAi(message: string, contextPlanet?: string): Promise<{ message: string; response: string; tools_used: string[]; source: string }> {
    return request("/ai/chat", {
      method: "POST",
      body: JSON.stringify({ message, context_planet: contextPlanet }),
    });
  },

  // Systems
  async getSystems(params: {
    page?: number;
    page_size?: number;
    search?: string;
    min_planets?: number;
    max_distance_pc?: number;
    is_circumbinary?: boolean;
    sort_by?: string;
    order?: "asc" | "desc";
  } = {}): Promise<PaginatedResponse<SystemSummary>> {
    const qs = buildQueryString(params);
    return request<PaginatedResponse<SystemSummary>>(`/systems${qs}`);
  },

  async getSystem(idOrName: string): Promise<SystemDetail> {
    const encoded = encodeURIComponent(idOrName.trim());
    return request<SystemDetail>(`/systems/${encoded}`);
  },

  // Stars
  async getStars(params: {
    page?: number;
    page_size?: number;
    search?: string;
    spectral_type?: string;
    min_mass_solar?: number;
    max_mass_solar?: number;
    min_temp_k?: number;
    max_temp_k?: number;
    sort_by?: string;
    order?: "asc" | "desc";
  } = {}): Promise<PaginatedResponse<StarSummary>> {
    const qs = buildQueryString(params);
    return request<PaginatedResponse<StarSummary>>(`/stars${qs}`);
  },

  async getStar(idOrName: string): Promise<StarDetail> {
    const encoded = encodeURIComponent(idOrName.trim());
    return request<StarDetail>(`/stars/${encoded}`);
  },
};
