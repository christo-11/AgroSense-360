import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { api, type Crop, type CropProfile, type Farm, type Plot } from "../api";
import FarmWorkspace from "./FarmWorkspace";

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      crops: vi.fn(),
      cropProfile: vi.fn(),
      currentWeather: vi.fn(),
      districts: vi.fn(),
      weatherForecast: vi.fn(),
      plots: vi.fn(),
      createFarm: vi.fn(),
      createPlot: vi.fn(),
      updatePlot: vi.fn(),
    },
  };
});

const crop: Crop = {
  id: "crop-cardamom",
  common_name: "Cardamom",
  slug: "cardamom",
  scientific_name: null,
  category: { id: "spices", name: "Plantation and spices", slug: "plantation-and-spices", display_order: 1 },
  verification_status: "pending",
  updated_at: "2026-01-01T00:00:00Z",
};

const farm: Farm = {
  id: "farm-1",
  name: "Home farm",
  location: null,
  boundary: null,
  created_at: "2026-01-01T00:00:00Z",
};

const plot: Plot = {
  id: "plot-1",
  farm_id: farm.id,
  name: "Plot 1",
  crop: "Cardamom",
  crop_id: crop.id,
  area_value: 2,
  area_unit: "acres",
  latitude: 9.85,
  longitude: 76.97,
  boundary: null,
  created_at: "2026-01-01T00:00:00Z",
};

const pendingProfile: CropProfile = {
  crop_id: crop.id,
  temperature_min_celsius: null,
  temperature_max_celsius: null,
  rainfall_min_mm_year: null,
  rainfall_max_mm_year: null,
  soil_type: null,
  soil_ph_min: null,
  soil_ph_max: null,
  planting_season: null,
  irrigation_requirements: null,
  fertilizer_recommendations: null,
  cultivation_practices: null,
  plant_spacing_min_cm: null,
  plant_spacing_max_cm: null,
  growth_duration_min_days: null,
  growth_duration_max_days: null,
  harvesting_information: null,
  common_pests_diseases: [],
  expected_yield_min: null,
  expected_yield_max: null,
  expected_yield_unit: null,
  sources: [],
  verification_status: "pending",
  last_updated_at: "2026-01-01T00:00:00Z",
};

function renderWorkspace(farms: Farm[] = []) {
  return render(
    <FarmWorkspace
      authenticated
      farms={farms}
      loading={false}
      loadError=""
      onRefresh={async () => undefined}
      onNotice={vi.fn()}
      onRequestSignIn={vi.fn()}
    />,
  );
}

describe("FarmWorkspace plot dashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.crops).mockResolvedValue({ items: [crop], total: 1, limit: 100, offset: 0 });
    vi.mocked(api.districts).mockResolvedValue({
      items: [{ id: "idukki", name: "Idukki", slug: "idukki", state_name: "Kerala" }],
      total: 1,
      limit: 100,
      offset: 0,
    });
    vi.mocked(api.plots).mockResolvedValue([]);
    vi.mocked(api.createFarm).mockResolvedValue(farm);
    vi.mocked(api.createPlot).mockResolvedValue(plot);
    vi.mocked(api.currentWeather).mockResolvedValue({
      provider: "Open-Meteo",
      source_url: "https://open-meteo.com/",
      attribution: "Weather model estimate · CC BY 4.0",
      data_kind: "current_model_estimate",
      time_standard: "UTC",
      latitude: 9.85,
      longitude: 76.97,
      timestamp: "2026-11-24T05:30",
      requested_at: "2026-11-24T05:30:05Z",
      units: { temperature_2m: "°C", relative_humidity_2m: "%", precipitation: "mm", wind_speed_10m: "km/h" },
      values: { temperature_2m: 27.1, relative_humidity_2m: 78, precipitation: 0.2, wind_speed_10m: 4.5 },
      cached_for_seconds: 600,
    });
    vi.mocked(api.weatherForecast).mockResolvedValue({
      provider: "Open-Meteo",
      source_url: "https://open-meteo.com/",
      attribution: "Weather data by Open-Meteo.com; API data CC BY 4.0. Forecast model estimates, not observations.",
      data_kind: "forecast_model_estimate",
      time_standard: "UTC",
      latitude: 9.85,
      longitude: 76.97,
      requested_at: "2026-11-25T04:30:00Z",
      timezone: "UTC",
      units: { temperature_2m: "°C", relative_humidity_2m: "%", precipitation: "mm", wind_speed_10m: "km/h" },
      records: [],
      daily_units: { temperature_2m_min: "°C", temperature_2m_max: "°C", precipitation_sum: "mm", wind_speed_10m_max: "km/h" },
      daily_records: [{
        date: "2026-11-25",
        values: {
          temperature_2m_min: 22,
          temperature_2m_max: 31,
          precipitation_sum: 3.2,
          precipitation_probability_max: 50,
          wind_speed_10m_max: 12,
        },
      }],
      cached_for_seconds: 600,
    });
    vi.mocked(api.cropProfile).mockResolvedValue(pendingProfile);
  });

  afterEach(cleanup);

  it("adds a crop plot with area and device-selected location only", async () => {
    const getCurrentPosition = vi.fn((success: PositionCallback) => {
      success({
        coords: { latitude: 9.85, longitude: 76.97 } as GeolocationCoordinates,
      } as GeolocationPosition);
    });
    Object.defineProperty(navigator, "geolocation", {
      configurable: true,
      value: { getCurrentPosition },
    });

    renderWorkspace();
    fireEvent.click(screen.getByRole("button", { name: "Add plot" }));
    await screen.findByRole("option", { name: "Cardamom" });
    fireEvent.change(screen.getByLabelText("Crop"), { target: { value: crop.id } });
    fireEvent.change(screen.getByPlaceholderText("e.g. 2"), { target: { value: "1.5" } });
    fireEvent.change(screen.getByLabelText("Area unit"), { target: { value: "hectares" } });
    fireEvent.click(screen.getByRole("button", { name: /Use this device/ }));
    await screen.findByText(/Plot location selected and ready to save/);
    expect(screen.queryByLabelText("Latitude")).toBeNull();
    expect(screen.queryByLabelText("Longitude")).toBeNull();
    expect(screen.queryByText(/GeoJSON/)).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Save plot" }));
    await waitFor(() => expect(api.createPlot).toHaveBeenCalledOnce());
    expect(api.createFarm).toHaveBeenCalledWith("My farm", "");
    expect(api.createPlot).toHaveBeenCalledWith(farm.id, {
      crop_id: crop.id,
      area_value: 1.5,
      area_unit: "hectares",
      latitude: 9.85,
      longitude: 76.97,
    });
  });

  it("shows plot-specific attributed weather and withholds unverified advice", async () => {
    vi.mocked(api.plots).mockResolvedValue([plot]);
    renderWorkspace([farm]);

    expect(await screen.findByRole("heading", { name: "Cardamom" })).toBeTruthy();
    expect(await screen.findByText("27.1 °C")).toBeTruthy();
    expect(screen.getByText("0.2 mm")).toBeTruthy();
    expect(screen.getByText(/Current conditions/)).toBeTruthy();
    expect(screen.getByText("Model estimate", { exact: true })).toBeTruthy();
    expect(screen.getByText("Crop health is not assessed; no verified plot-level health evidence is available.")).toBeTruthy();
    expect(screen.getByText("No verified crop recommendations are available.")).toBeTruthy();
    expect(api.currentWeather).toHaveBeenCalledWith(9.85, 76.97);
  });

  it("loads the attributed seven-day model forecast for the saved plot", async () => {
    vi.mocked(api.plots).mockResolvedValue([plot]);
    renderWorkspace([farm]);

    fireEvent.click(await screen.findByRole("button", { name: "Show 7-day forecast" }));

    expect(await screen.findByText("7-day forecast · model estimates")).toBeTruthy();
    expect(screen.getByText("22° / 31°C")).toBeTruthy();
    expect(screen.getByText("Rain 3.2 mm")).toBeTruthy();
    expect(screen.getByText(/Weather data by Open-Meteo.com; API data CC BY 4.0/)).toBeTruthy();
    expect(api.weatherForecast).toHaveBeenCalledWith(9.85, 76.97);
  });
});
