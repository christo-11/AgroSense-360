import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { api } from "../api";
import ResearchWorkspace from "./ResearchWorkspace";

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      idukkiBlackPepperReadiness: vi.fn(),
      researchDocuments: vi.fn(),
      researchModelStatus: vi.fn(),
      researchPredictionHistory: vi.fn(),
    },
  };
});

describe("ResearchWorkspace agricultural evidence", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("shows blocked Idukki black-pepper assessment and evidence blockers", async () => {
    vi.mocked(api.idukkiBlackPepperReadiness).mockResolvedValue({
      status: "evidence_incomplete",
      assessment: "not_computed",
      crop: null,
      district: { id: "district-id", name: "Idukki" },
      crop_profile: null,
      district_associations: [],
      readiness: {
        verified_climate_ranges: false,
        verified_district_association: false,
        georeferenced_soil_samples: false,
        pepper_yield_observations: false,
        climate_suitability_result: false,
      },
      blockers: ["No verified Idukki-black pepper suitability association is available."],
    });
    vi.mocked(api.researchDocuments).mockResolvedValue({ items: [], total: 0, limit: 50, offset: 0 });
    vi.mocked(api.researchModelStatus).mockResolvedValue({ available: false, detail: "No model has been evaluated." });
    vi.mocked(api.researchPredictionHistory).mockResolvedValue({ items: [], total: 0 });

    render(<ResearchWorkspace authenticated />);

    expect(await screen.findByText("Not computed")).toBeTruthy();
    expect(screen.getByText("Evidence still needed")).toBeTruthy();
    expect(screen.getByText("No verified Idukki-black pepper suitability association is available.")).toBeTruthy();
    expect(screen.getByText("climate suitability result")).toBeTruthy();
  });
});
