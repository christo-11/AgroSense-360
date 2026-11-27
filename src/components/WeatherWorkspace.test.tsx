import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { api } from "../api";
import WeatherWorkspace from "./WeatherWorkspace";

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      historicalWeather: vi.fn(),
      monthlyClimate: vi.fn(),
      weatherForecast: vi.fn(),
    },
  };
});

describe("WeatherWorkspace", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders attributed NASA history after a location request", async () => {
    vi.mocked(api.historicalWeather).mockResolvedValue({
      provider: "NASA POWER",
      source_url: "https://power.larc.nasa.gov/",
      attribution: "Gridded estimates, not direct observations.",
      data_kind: "historical_gridded_estimate",
      time_standard: "UTC",
      latitude: 10,
      longitude: 76,
      requested_at: "2024-01-03T02:00:00Z",
      units: { T2M: "degC" },
      records: [{ timestamp: "2024-01-03T00:00:00Z", values: { T2M: 27.3 } }],
      cached_for_seconds: 21600,
    });
    render(<WeatherWorkspace authenticated onRequestSignIn={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Latitude"), { target: { value: "10" } });
    fireEvent.change(screen.getByLabelText("Longitude"), { target: { value: "76" } });
    fireEvent.click(screen.getByRole("button", { name: "Load NASA POWER history" }));

    expect(await screen.findByText(/Historical daily estimates/)).toBeTruthy();
    expect(screen.getByText("27.3")).toBeTruthy();
    expect(screen.getByText(/not direct observations/)).toBeTruthy();
    expect(api.historicalWeather).toHaveBeenCalledWith(
      10,
      76,
      expect.any(String),
      expect.any(String),
    );
  });

  it("shows a provider error and a sign-in prompt without hiding existing controls", async () => {
    const requestSignIn = vi.fn();
    vi.mocked(api.historicalWeather).mockRejectedValue(new Error("Weather provider unavailable."));
    render(<WeatherWorkspace authenticated={false} onRequestSignIn={requestSignIn} />);
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(requestSignIn).toHaveBeenCalledOnce();

    render(<WeatherWorkspace authenticated onRequestSignIn={requestSignIn} />);
    fireEvent.change(screen.getAllByLabelText("Latitude")[1], { target: { value: "10" } });
    fireEvent.change(screen.getAllByLabelText("Longitude")[1], { target: { value: "76" } });
    fireEvent.click(screen.getAllByRole("button", { name: "Load NASA POWER history" })[1]);
    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("Weather provider unavailable."));
  });

  it("renders a source-attributed monthly climate summary", async () => {
    vi.mocked(api.monthlyClimate).mockResolvedValue({
      provider: "NASA POWER",
      source_url: "https://power.larc.nasa.gov/",
      attribution: "Gridded monthly means, not ground observations.",
      data_kind: "multi_year_monthly_gridded_estimate",
      time_standard: "LST",
      source_datasets: ["MERRA2"],
      latitude: 10,
      longitude: 76,
      start_year: 1996,
      end_year: 2025,
      units: { T2M: "degC" },
      records: Array.from({ length: 12 }, (_, index) => ({
        month: index + 1,
        values: { T2M: index === 0 ? 26.4 : null },
        years_with_data: { T2M: index === 0 ? 30 : 0 },
      })),
      cached_for_seconds: 86400,
      limitation: "Descriptive context only.",
    });
    render(<WeatherWorkspace authenticated onRequestSignIn={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Latitude"), { target: { value: "10" } });
    fireEvent.change(screen.getByLabelText("Longitude"), { target: { value: "76" } });
    fireEvent.click(screen.getByRole("button", { name: "Load monthly climate" }));

    expect(await screen.findByText(/Monthly climate context/)).toBeTruthy();
    expect(screen.getByText("January")).toBeTruthy();
    expect(screen.getByText("26.4")).toBeTruthy();
    expect(screen.getByText(/Descriptive context only/)).toBeTruthy();
    expect(api.monthlyClimate).toHaveBeenCalledWith(
      10,
      76,
      expect.any(Number),
      expect.any(Number),
    );
  });
});
