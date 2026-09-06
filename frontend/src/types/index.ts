/**
 * Exoplanet Atlas TypeScript Data Types.
 * Matches backend schemas from Stage 2 and AI layer.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface StatsResponse {
  total_planets: number;
  total_systems: number;
  total_stars: number;
  multi_planet_systems: number;
  planet_class_distribution: Record<string, number>;
  habitability_zone_distribution: Record<string, number>;
  discovery_method_distribution: Record<string, number>;
  discovery_timeline: Record<string, number>;
}

export interface Discovery {
  id: number;
  planet_id: number;
  discovery_method: string;
  discovery_year: number | null;
  discovery_facility: string | null;
  discovery_instrument: string | null;
  discovery_locale: string | null;
  publication_date: string | null;
  reference_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface StarSummary {
  id: number;
  system_id: number;
  name: string;
  spectral_type: string | null;
  effective_temp_k: number | null;
  radius_solar: number | null;
  mass_solar: number | null;
  metallicity_dex: number | null;
  surface_gravity_logg: number | null;
  luminosity_log_solar: number | null;
  age_gyr: number | null;
  density_g_cm3: number | null;
  rotation_period_days: number | null;
  v_sin_i_km_s: number | null;
  radial_velocity_km_s: number | null;
  hd_id: string | null;
  hip_id: string | null;
  tic_id: string | null;
  gaia_dr2_id: string | null;
  gaia_dr3_id: string | null;
}

export interface PlanetSummary {
  id: number;
  system_id: number;
  star_id: number | null;
  name: string;
  planet_letter: string | null;
  is_controversial: boolean;
  orbital_period_days: number | null;
  semi_major_axis_au: number | null;
  eccentricity: number | null;
  inclination_deg: number | null;
  longitude_periastron_deg: number | null;
  periastron_passage_days: number | null;
  radius_earth: number | null;
  radius_jupiter: number | null;
  mass_earth: number | null;
  mass_jupiter: number | null;
  best_mass_earth: number | null;
  best_mass_jupiter: number | null;
  mass_provenance: string | null;
  msini_earth: number | null;
  msini_jupiter: number | null;
  density_g_cm3: number | null;
  equilibrium_temp_k: number | null;
  insolation_earth: number | null;
  transit_duration_hours: number | null;
  transit_depth_percent: number | null;
  transit_midpoint_days: number | null;
  impact_parameter: number | null;
  ratio_planet_to_star_radius: number | null;
  radial_velocity_amplitude_m_s: number | null;
  planet_class: string | null;
  habitability_zone_est: string | null;
  tran_flag: boolean;
  rv_flag: boolean;
  ttv_flag: boolean;
  ptv_flag: boolean;
  ast_flag: boolean;
  micro_flag: boolean;
  ima_flag: boolean;
  discovery: Discovery | null;
}

export interface SystemSummary {
  id: number;
  name: string;
  ra: number | null;
  dec: number | null;
  distance_pc: number | null;
  parallax_mas: number | null;
  proper_motion_mas_yr: number | null;
  proper_motion_ra: number | null;
  proper_motion_dec: number | null;
  star_count: number | null;
  planet_count: number | null;
  moon_count: number | null;
  is_circumbinary: boolean | null;
  v_mag: number | null;
  b_mag: number | null;
  j_mag: number | null;
  h_mag: number | null;
  k_mag: number | null;
  gaia_mag: number | null;
  tess_mag: number | null;
  kepler_mag: number | null;
}

export interface PlanetDetail extends PlanetSummary {
  created_at: string;
  updated_at: string;
  discovery: Discovery | null;
  star: StarSummary | null;
  system: SystemSummary | null;
}

export interface StarDetail extends StarSummary {
  created_at: string;
  updated_at: string;
  planets: PlanetSummary[];
}

export interface SystemDetail extends SystemSummary {
  created_at: string;
  updated_at: string;
  stars: StarSummary[];
  planets: PlanetSummary[];
}

export interface CatalogFilterParams {
  page?: number;
  page_size?: number;
  search?: string;
  planet_class?: string;
  habitability_zone_est?: string;
  discovery_method?: string;
  discovery_year?: number;
  discovery_facility?: string;
  min_radius_earth?: number;
  max_radius_earth?: number;
  min_mass_earth?: number;
  max_mass_earth?: number;
  min_period_days?: number;
  max_period_days?: number;
  min_equilibrium_temp_k?: number;
  max_equilibrium_temp_k?: number;
  min_distance_pc?: number;
  max_distance_pc?: number;
  system_name?: string;
  star_name?: string;
  sort_by?: string;
  order?: "asc" | "desc";
}

export interface PlanetAISummaryResponse {
  planet_name: string;
  summary: string;
  key_facts: string[];
  tools_used?: string[];
  source: string;
}

export interface PlanetQARequest {
  question: string;
}

export interface PlanetQAResponse {
  planet_name: string;
  question: string;
  answer: string;
  confidence: string;
  tools_used?: string[];
  data_points_used: string[];
}

export interface AIChatRequest {
  message: string;
  context_planet?: string;
}

export interface AIChatResponse {
  message: string;
  response: string;
  tools_used: string[];
  source: string;
}
