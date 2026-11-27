import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { api } from "../api";
import MarketWorkspace from "./MarketWorkspace";

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      crops: vi.fn(),
      districts: vi.fn(),
      marketPrices: vi.fn(),
    },
  };
});

describe("MarketWorkspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.crops).mockResolvedValue({ items: [], total: 0, limit: 100, offset: 0 });
    vi.mocked(api.districts).mockResolvedValue({ items: [], total: 0, limit: 100, offset: 0 });
  });

  afterEach(cleanup);

  it("shows provider errors and offers a retry without inventing prices", async () => {
    vi.mocked(api.marketPrices).mockRejectedValue(new Error("Market prices are unavailable: configure an authorized data.gov.in API key."));
    render(<MarketWorkspace authenticated fixedCommodity="Black pepper" />);

    fireEvent.click(screen.getByRole("button", { name: "Find market prices" }));

    expect((await screen.findByRole("alert")).textContent).toMatch(/configure an authorized data.gov.in API key/);
    expect(screen.getByRole("button", { name: "Retry" })).toBeTruthy();
    expect(screen.queryByText(/₹/)).toBeNull();
  });

  it("renders source-reported market values with their market date", async () => {
    vi.mocked(api.marketPrices).mockResolvedValue({
      provider: "AGMARKNET via data.gov.in",
      source_url: "https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi",
      attribution: "Source: Government of India, AGMARKNET / data.gov.in.",
      license: "Resource-specific reuse terms require operator verification.",
      data_kind: "daily_market_reported_prices",
      state: "Kerala",
      commodity: "Black pepper",
      district: "Idukki",
      currency: "INR",
      price_unit: "per quintal",
      requested_at: "2026-11-25T04:30:00Z",
      source_updated_at: "2026-11-25",
      cached_for_seconds: 3600,
      records: [{
        commodity: "Black pepper",
        market: "Thodupuzha",
        state: "Kerala",
        district: "Idukki",
        variety: null,
        market_date: "2026-11-24",
        prices: { minimum: 40000, maximum: 42000, modal: 41000 },
      }],
    });
    render(<MarketWorkspace authenticated fixedCommodity="Black pepper" />);

    fireEvent.click(screen.getByRole("button", { name: "Find market prices" }));

    expect(await screen.findByText("Thodupuzha")).toBeTruthy();
    expect(screen.getByText(/₹40,000/)).toBeTruthy();
    expect(screen.getByText(/24 Nov 2026/)).toBeTruthy();
    expect(screen.getByText(/not real-time quotes/)).toBeTruthy();
    await waitFor(() => expect(api.marketPrices).toHaveBeenCalledWith("Black pepper", undefined));
  });
});
