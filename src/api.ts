const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Integration = {
  configured: boolean;
  status: string;
  detail: string;
};

export type CurrentWeatherResponse = {
  provider: string;
  source_url: string;
  attribution: string;
  data_kind: "current_model_estimate";
  time_standard: "UTC";
  latitude: number;
  longitude: number;
  timestamp: string;
  requested_at: string;
  units: Record<string, string>;
  values: Record<string, number | null>;
  cached_for_seconds: number;
};

export type PlatformStatus = {
  api: "online" | "offline";
  database: "connected" | "unavailable";
  public_demo_mode: boolean;
  integrations: Record<string, Integration>;
  models: Record<string, Integration>;
};

export type AdminSummary = {
  users: number;
  farms: number;
  plots: number;
  districts: number;
  crops: number;
  verified_crop_profiles: number;
  verified_district_associations: number;
  source_references: number;
  integrations: Record<string, Integration>;
  models: Record<string, Integration>;
};

export type GeoJSONPosition = [number, number];
export type GeoJSONPolygonCoordinates = GeoJSONPosition[][];

export type GeoJSONBoundary = {
  type: "Polygon";
  coordinates: GeoJSONPolygonCoordinates;
} | {
  type: "MultiPolygon";
  coordinates: GeoJSONPolygonCoordinates[];
};

export type Farm = {
  id: string;
  name: string;
  location: string | null;
  boundary: GeoJSONBoundary | null;
  created_at: string;
};

export type Plot = {
  id: string;
  farm_id: string;
  name: string;
  crop: string | null;
  crop_id: string | null;
  area_value: number | null;
  area_unit: "acres" | "hectares" | null;
  latitude: number | null;
  longitude: number | null;
  boundary: GeoJSONBoundary | null;
  created_at: string;
};

export type DashboardSummary = {
  farm_count: number;
  plot_count: number;
};

export type WeatherRecord = {
  timestamp: string;
  values: Record<string, number | null>;
};

export type WeatherResponse = {
  provider: string;
  source_url: string;
  attribution: string;
  data_kind: "historical_gridded_estimate" | "forecast_model_estimate";
  time_standard: "UTC";
  latitude: number;
  longitude: number;
  requested_at: string;
  timezone?: string;
  units: Record<string, string>;
  records: WeatherRecord[];
  daily_units?: Record<string, string>;
  daily_records?: Array<{
    date: string;
    values: Record<string, number | null>;
  }>;
  cached_for_seconds: number;
};

export type MarketPriceRecord = {
  commodity: string;
  market: string;
  state: string;
  district: string;
  variety: string | null;
  market_date: string;
  prices: {
    minimum: number | null;
    maximum: number | null;
    modal: number | null;
  };
};

export type MarketPricesResponse = {
  provider: string;
  source_url: string;
  attribution: string;
  license: string;
  data_kind: "daily_market_reported_prices";
  state: string;
  commodity: string;
  district: string | null;
  currency: string;
  price_unit: string;
  requested_at: string;
  source_updated_at: string | null;
  records: MarketPriceRecord[];
  cached_for_seconds: number;
};

export type MonthlyClimateResponse = {
  provider: string;
  source_url: string;
  attribution: string;
  data_kind: "multi_year_monthly_gridded_estimate";
  time_standard: string;
  source_datasets: string[];
  latitude: number;
  longitude: number;
  start_year: number;
  end_year: number;
  units: Record<string, string>;
  records: Array<{
    month: number;
    values: Record<string, number | null>;
    years_with_data: Record<string, number>;
  }>;
  cached_for_seconds: number;
  limitation: string;
};

export type IdukkiPepperReadiness = {
  status: "evidence_incomplete";
  assessment: "not_computed";
  crop: { id: string; name: string; scientific_name: string | null; verification_status: VerificationStatus } | null;
  district: { id: string; name: string } | null;
  crop_profile: {
    verification_status: VerificationStatus;
    temperature_min_celsius: number | null;
    temperature_max_celsius: number | null;
    rainfall_min_mm_year: number | null;
    rainfall_max_mm_year: number | null;
    soil_type: string | null;
    soil_ph_min: number | null;
    soil_ph_max: number | null;
    sources: Array<{ title: string; publisher: string; url: string; license: string | null }>;
  } | null;
  district_associations: Array<{
    suitability_status: "suitable" | "not_suitable" | "under_review";
    verification_status: VerificationStatus;
    variety: string | null;
    sources: Array<{ title: string; publisher: string; url: string; license: string | null }>;
  }>;
  readiness: {
    verified_climate_ranges: boolean;
    verified_district_association: boolean;
    georeferenced_soil_samples: boolean;
    pepper_yield_observations: boolean;
    climate_suitability_result: boolean;
  };
  blockers: string[];
};

export type ResearchDocument = {
  id: string;
  filename: string;
  content_type: string;
  sha256: string;
  uploaded_at: string;
  page_count: number;
  extraction_method: "text" | "text+ocr";
};

export type ResearchCitation = {
  document_id: string;
  filename: string;
  page: number;
  citation: string;
};

export type ResearchModelStatus = {
  available: boolean;
  model_id?: string;
  model_type?: string;
  feature_columns?: string[];
  target_column?: string;
  split_strategy?: string;
  training_rows?: number;
  holdout_rows?: number;
  metrics?: Record<string, number | null>;
  limitations?: string[];
  detail?: string;
};

export type DataIntelligenceSummary = {
  total_sources: number;
  portfolio_status_counts: Record<string, number>;
  commercial_approval_counts: Record<string, number>;
  inventory_acquisition_counts: Record<string, number>;
  acquisition_status_counts: Record<string, number>;
  archive_integrity_status_counts: Record<string, number>;
  data_quality_status_counts: Record<string, number>;
  manifest_request_count: number;
  manifest_reported_success_count: number;
  training_eligible_count: number;
  weather_decision: string;
  weather_training_status: string;
  metadata_warnings: string[];
  validation_warnings: string[];
};

export type VerificationStatus = "pending" | "verified" | "rejected";
export type Page<T> = {
  items: T[];
  total: number;
  limit: number;
  offset: number;
};

export type District = {
  id: string;
  name: string;
  slug: string;
  state_name: string;
};

export type CropCategory = {
  id: string;
  name: string;
  slug: string;
  display_order: number;
};

export type AgriculturalSource = {
  id: string;
  title: string;
  publisher: string;
  url: string;
  license: string | null;
  accessed_on: string | null;
  notes: string | null;
};

export type Crop = {
  id: string;
  common_name: string;
  slug: string;
  scientific_name: string | null;
  category: CropCategory;
  verification_status: VerificationStatus;
  updated_at: string;
};

export type CropProfile = {
  crop_id: string;
  temperature_min_celsius: number | null;
  temperature_max_celsius: number | null;
  rainfall_min_mm_year: number | null;
  rainfall_max_mm_year: number | null;
  soil_type: string | null;
  soil_ph_min: number | null;
  soil_ph_max: number | null;
  planting_season: string | null;
  irrigation_requirements: string | null;
  fertilizer_recommendations: string | null;
  cultivation_practices: string | null;
  plant_spacing_min_cm: number | null;
  plant_spacing_max_cm: number | null;
  growth_duration_min_days: number | null;
  growth_duration_max_days: number | null;
  harvesting_information: string | null;
  common_pests_diseases: string[];
  expected_yield_min: number | null;
  expected_yield_max: number | null;
  expected_yield_unit: string | null;
  sources: AgriculturalSource[];
  verification_status: VerificationStatus;
  last_updated_at: string;
};

export type CropVariety = {
  id: string;
  crop_id: string;
  name: string;
  scientific_name: string | null;
  description: string | null;
  sources: AgriculturalSource[];
  verification_status: VerificationStatus;
  last_updated_at: string;
};

export type DistrictCropAssociation = {
  id: string;
  district_id: string;
  crop_id: string;
  crop_name: string;
  variety_id: string | null;
  variety_name: string | null;
  suitability_status: "suitable" | "not_suitable" | "under_review";
  verification_status: VerificationStatus;
  notes: string | null;
  sources: AgriculturalSource[];
  last_updated_at: string;
};

export type DataSourceSummary = {
  id: string;
  name: string;
  publisher: string;
  license: string | null;
  dataset_version: string | null;
  version_status: string;
  portfolio_status: string;
  commercial_approval_status: string;
  commercial_use_status: string;
  inventory_acquisition_status: string;
  acquisition_status: string;
  archive_integrity_status: string;
  data_quality_status: string;
  validation_warnings: string[];
  last_checked: string | null;
};

export type DataSourceArtifact = {
  request_number: number;
  filename: string;
  request_status: string;
  retrieved_at: string | null;
  size_bytes: number | null;
  actual_size_bytes: number | null;
  sha256: string | null;
  checksum_verified: boolean;
  content_length_verified: boolean | null;
  zip_crc_valid: boolean | null;
  zip_format_valid: boolean | null;
  acquisition_status: string;
  archive_integrity_status: string;
  data_quality_status: string;
  status_explanation: string;
  validation_warnings: string[];
};

export type DataSourceAcquisition = {
  id: string;
  name: string;
  inventory_status: string;
  acquisition_status: string;
  archive_integrity_status: string;
  data_quality_status: string;
  status_explanation: string;
  validation_warnings: string[];
  artifacts: DataSourceArtifact[];
};

export type DataSourceAcquisitionPage = Page<DataSourceAcquisition> & {
  validation_warnings: string[];
};

export type WeatherArchiveQuality = {
  request_number: number;
  decision: string;
  training_status: string;
  dynamic_timestamp_count: number;
  coverage_start_utc: string | null;
  coverage_end_utc: string | null;
  observed_gap_hours: number[];
  global_grid_missing_fraction: number;
  missingness_scope: string;
  warning: string;
};

export type DataQualityResponse = {
  overall_decision: string;
  overall_training_status: string;
  archives: WeatherArchiveQuality[];
};

export type TrainingEligibilityItem = {
  id: string;
  name: string;
  eligible_for_training: boolean;
  status: string;
  reasons: string[];
};

export type TrainingEligibilityResponse = {
  total_sources: number;
  eligible_count: number;
  items: Page<TrainingEligibilityItem>;
  note: string;
};

export type CatalogueCompletenessResponse = {
  districts_total: number;
  crop_categories_total: number;
  crops_total: number;
  crop_profiles_total: number;
  verified_crop_profiles: number;
  crop_profile_coverage_percent: number | null;
  crop_varieties_total: number;
  districts_with_suitability: number;
  district_crop_associations_total: number;
  district_suitability_coverage_percent: number | null;
};

export type DataProvenanceItem = {
  id: string;
  name: string;
  publisher: string;
  license: string | null;
  dataset_version: string | null;
  version_status: string;
  last_checked: string | null;
  acquisition_status: string;
  archive_integrity_status: string;
  data_quality_status: string;
  validation_warnings: string[];
  artifacts: DataSourceArtifact[];
};

export class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

function token() {
  return sessionStorage.getItem("agrosense_token");
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (typeof init.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const authToken = token();
  if (authToken) headers.set("Authorization", `Bearer ${authToken}`);
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    const message = typeof detail === "string"
      ? detail
      : Array.isArray(detail)
        ? detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join("; ")
        : `Request failed (${response.status})`;
    throw new ApiError(message, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  status: () => request<PlatformStatus>("/api/v1/status"),
  adminSummary: () => request<AdminSummary>("/api/v1/admin/summary"),
  historicalWeather: (latitude: number, longitude: number, startDate: string, endDate: string) => {
    const params = new URLSearchParams({
      latitude: String(latitude),
      longitude: String(longitude),
      start_date: startDate,
      end_date: endDate,
    });
    return request<WeatherResponse>(`/api/v1/weather/history?${params}`);
  },
  currentWeather: (latitude: number, longitude: number) => {
    const params = new URLSearchParams({ latitude: String(latitude), longitude: String(longitude) });
    return request<CurrentWeatherResponse>(`/api/v1/weather/current?${params}`);
  },
  weatherForecast: (latitude: number, longitude: number) => {
    const params = new URLSearchParams({ latitude: String(latitude), longitude: String(longitude) });
    return request<WeatherResponse>(`/api/v1/weather/forecast?${params}`);
  },
  marketPrices: (commodity: string, district?: string) => {
    const params = new URLSearchParams({ commodity, limit: "20" });
    if (district) params.set("district", district);
    return request<MarketPricesResponse>(`/api/v1/markets/prices?${params}`);
  },
  monthlyClimate: (latitude: number, longitude: number, startYear: number, endYear: number) => {
    const params = new URLSearchParams({
      latitude: String(latitude),
      longitude: String(longitude),
      start_year: String(startYear),
      end_year: String(endYear),
    });
    return request<MonthlyClimateResponse>(`/api/v1/weather/climate-monthly?${params}`);
  },
  idukkiBlackPepperReadiness: () =>
    request<IdukkiPepperReadiness>("/api/v1/agricultural-research/idukki-black-pepper"),
  researchDocuments: (limit = 50, offset = 0) =>
    request<{ items: ResearchDocument[]; total: number; limit: number; offset: number }>(
      `/api/v1/research/documents?limit=${limit}&offset=${offset}`,
    ),
  uploadResearchDocument: (file: File, ocr = false) => {
    const body = new FormData();
    body.append("file", file);
    body.append("ocr", String(ocr));
    return request<ResearchDocument>("/api/v1/research/documents", { method: "POST", body });
  },
  deleteResearchDocument: (documentId: string) =>
    request<void>(`/api/v1/research/documents/${encodeURIComponent(documentId)}`, { method: "DELETE" }),
  answerResearch: (query: string, limit = 5) =>
    request<{
      answer: string;
      mode: string;
      citations: ResearchCitation[];
      warning: string | null;
    }>("/api/v1/research/answer", {
      method: "POST",
      body: JSON.stringify({ query, limit }),
    }),
  researchModelStatus: () => request<ResearchModelStatus>("/api/v1/research/ml/status"),
  trainResearchModel: (form: FormData) =>
    request<ResearchModelStatus>("/api/v1/research/ml/train", { method: "POST", body: form }),
  predictResearchModel: (features: Record<string, number | string | null>) =>
    request<{
      model_id: string;
      target: string;
      prediction: number;
      predicted_at: string;
      warning: string;
    }>("/api/v1/research/ml/predict", {
      method: "POST",
      body: JSON.stringify({ features }),
    }),
  researchPredictionHistory: () =>
    request<{ items: Array<Record<string, unknown>>; total: number }>("/api/v1/research/ml/history"),
  dashboardSummary: () => request<DashboardSummary>("/api/v1/dashboard/summary"),
  dataIntelligenceSummary: () =>
    request<DataIntelligenceSummary>("/api/v1/data-intelligence/summary"),
  dataIntelligenceSources: (limit = 50, offset = 0) =>
    request<Page<DataSourceSummary>>(
      `/api/v1/data-intelligence/sources?limit=${limit}&offset=${offset}`,
    ),
  dataIntelligenceAcquisitions: (limit = 50, offset = 0) =>
    request<DataSourceAcquisitionPage>(
      `/api/v1/data-intelligence/acquisitions?limit=${limit}&offset=${offset}`,
    ),
  dataIntelligenceQuality: () =>
    request<DataQualityResponse>("/api/v1/data-intelligence/quality"),
  dataIntelligenceTrainingEligibility: (limit = 50, offset = 0) =>
    request<TrainingEligibilityResponse>(
      `/api/v1/data-intelligence/training-eligibility?limit=${limit}&offset=${offset}`,
    ),
  dataIntelligenceCatalogue: () =>
    request<CatalogueCompletenessResponse>(
      "/api/v1/data-intelligence/catalogue-completeness",
    ),
  dataIntelligenceProvenance: (limit = 50, offset = 0) =>
    request<Page<DataProvenanceItem>>(
      `/api/v1/data-intelligence/provenance?limit=${limit}&offset=${offset}`,
    ),
  districts: (limit = 50, offset = 0) =>
    request<Page<District>>(`/api/v1/districts?limit=${limit}&offset=${offset}`),
  cropCategories: (limit = 50, offset = 0) =>
    request<Page<CropCategory>>(`/api/v1/crop-categories?limit=${limit}&offset=${offset}`),
  crops: (filters: { categoryId?: string; search?: string; limit?: number; offset?: number } = {}) => {
    const params = new URLSearchParams();
    if (filters.categoryId) params.set("category_id", filters.categoryId);
    if (filters.search?.trim()) params.set("search", filters.search.trim());
    params.set("limit", String(filters.limit ?? 50));
    params.set("offset", String(filters.offset ?? 0));
    return request<Page<Crop>>(`/api/v1/crops?${params.toString()}`);
  },
  crop: (cropId: string) => request<Crop>(`/api/v1/crops/${encodeURIComponent(cropId)}`),
  cropProfile: (cropId: string) =>
    request<CropProfile>(`/api/v1/crops/${encodeURIComponent(cropId)}/profile`),
  cropVarieties: (cropId: string, limit = 50, offset = 0) =>
    request<Page<CropVariety>>(
      `/api/v1/crops/${encodeURIComponent(cropId)}/varieties?limit=${limit}&offset=${offset}`,
    ),
  districtCrops: (districtId: string, limit = 50, offset = 0) =>
    request<Page<DistrictCropAssociation>>(
      `/api/v1/districts/${encodeURIComponent(districtId)}/crops?limit=${limit}&offset=${offset}`,
    ),
  farms: () => request<Farm[]>("/api/v1/farms"),
  farm: (farmId: string) => request<Farm>(`/api/v1/farms/${encodeURIComponent(farmId)}`),
  createFarm: (name: string, location: string, boundary?: GeoJSONBoundary | null) =>
    request<Farm>("/api/v1/farms", {
      method: "POST",
      body: JSON.stringify({ name, location, boundary }),
    }),
  updateFarm: (farmId: string, changes: { name?: string; location?: string | null; boundary?: GeoJSONBoundary | null }) =>
    request<Farm>(`/api/v1/farms/${encodeURIComponent(farmId)}`, {
      method: "PATCH",
      body: JSON.stringify(changes),
    }),
  deleteFarm: (farmId: string) =>
    request<void>(`/api/v1/farms/${encodeURIComponent(farmId)}`, { method: "DELETE" }),
  plots: (farmId: string) =>
    request<Plot[]>(`/api/v1/farms/${encodeURIComponent(farmId)}/plots`),
  createPlot: (farmId: string, plot: {
    name?: string;
    crop?: string | null;
    crop_id?: string | null;
    area_value?: number | null;
    area_unit?: "acres" | "hectares" | null;
    latitude?: number | null;
    longitude?: number | null;
    boundary?: GeoJSONBoundary | null;
  }) =>
    request<Plot>(`/api/v1/farms/${encodeURIComponent(farmId)}/plots`, {
      method: "POST",
      body: JSON.stringify(plot),
    }),
  updatePlot: (
    farmId: string,
    plotId: string,
    changes: {
      name?: string;
      crop?: string | null;
      crop_id?: string | null;
      area_value?: number | null;
      area_unit?: "acres" | "hectares" | null;
      latitude?: number | null;
      longitude?: number | null;
      boundary?: GeoJSONBoundary | null;
    },
  ) =>
    request<Plot>(
      `/api/v1/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}`,
      { method: "PATCH", body: JSON.stringify(changes) },
    ),
  deletePlot: (farmId: string, plotId: string) =>
    request<void>(
      `/api/v1/farms/${encodeURIComponent(farmId)}/plots/${encodeURIComponent(plotId)}`,
      { method: "DELETE" },
    ),
  signIn: async (email: string, password: string) => {
    const result = await request<{ access_token: string; must_change_password: boolean }>("/api/v1/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    });
    sessionStorage.setItem("agrosense_token", result.access_token);
    return result.must_change_password;
  },
  changePassword: (newPassword: string) =>
    request<{ status: string }>("/api/v1/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ new_password: newPassword }),
    }),
  register: (email: string, password: string) =>
    request<{ id: string }>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  signOut: () => sessionStorage.removeItem("agrosense_token"),
};
