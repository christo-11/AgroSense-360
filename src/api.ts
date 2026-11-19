const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Integration = {
  configured: boolean;
  status: string;
  detail: string;
};

export type PlatformStatus = {
  api: "online" | "offline";
  database: "connected" | "unavailable";
  public_demo_mode: boolean;
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
  boundary: GeoJSONBoundary;
  created_at: string;
};

export type DashboardSummary = {
  farm_count: number;
  plot_count: number;
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
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
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
  dashboardSummary: () => request<DashboardSummary>("/api/v1/dashboard/summary"),
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
  createPlot: (farmId: string, plot: { name: string; crop?: string | null; boundary: GeoJSONBoundary }) =>
    request<Plot>(`/api/v1/farms/${encodeURIComponent(farmId)}/plots`, {
      method: "POST",
      body: JSON.stringify(plot),
    }),
  updatePlot: (
    farmId: string,
    plotId: string,
    changes: { name?: string; crop?: string | null; boundary?: GeoJSONBoundary },
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
    const result = await request<{ access_token: string }>("/api/v1/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: email, password }),
    });
    sessionStorage.setItem("agrosense_token", result.access_token);
  },
  register: (email: string, password: string) =>
    request<{ id: string }>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  signOut: () => sessionStorage.removeItem("agrosense_token"),
};
