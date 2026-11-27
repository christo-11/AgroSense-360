import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { api } from "../api";
import DataIntelligenceDashboard from "./DataIntelligenceDashboard";

vi.mock("../api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      dataIntelligenceSummary: vi.fn(),
      dataIntelligenceSources: vi.fn(),
      dataIntelligenceAcquisitions: vi.fn(),
      dataIntelligenceQuality: vi.fn(),
      dataIntelligenceTrainingEligibility: vi.fn(),
      dataIntelligenceCatalogue: vi.fn(),
      dataIntelligenceProvenance: vi.fn(),
    },
  };
});

const summary = {
  total_sources: 1,
  portfolio_status_counts: { APPROVED_PORTFOLIO_RESEARCH_ONLY: 1 },
  commercial_approval_counts: { CONDITIONAL: 1 },
  inventory_acquisition_counts: { acquired: 1 },
  acquisition_status_counts: { PROVENANCE_CONFLICT: 1 },
  archive_integrity_status_counts: { FAILED: 1 },
  data_quality_status_counts: { QUALITY_REJECTED: 1 },
  manifest_request_count: 2,
  manifest_reported_success_count: 2,
  training_eligible_count: 0,
  weather_decision: "NEEDS_MORE_DATA",
  weather_training_status: "REJECT_FOR_TRAINING",
  metadata_warnings: ["Exact CDS request parameters remain unconfirmed."],
  validation_warnings: ["Exact CDS request parameters remain unconfirmed."],
};

const source = {
  id: "era5_land",
  name: "Copernicus ERA5-Land",
  publisher: "ECMWF / Copernicus Climate Data Store",
  license: "Licence to Use Copernicus Products",
  dataset_version: null,
  version_status: "ACQUIRED_VERSION_UNPINNED",
  portfolio_status: "APPROVED_PORTFOLIO_RESEARCH_ONLY",
  commercial_approval_status: "CONDITIONAL",
  commercial_use_status: "CONDITIONAL",
  inventory_acquisition_status: "acquired",
  acquisition_status: "PROVENANCE_CONFLICT",
  archive_integrity_status: "FAILED",
  data_quality_status: "QUALITY_REJECTED",
  validation_warnings: ["Archive size does not match the manifest."],
  last_checked: "2026-11-19",
};

const artifact = {
  request_number: 1,
  filename: "era5_land_request_1.zip",
  request_status: "Successful (reported by user; MHT not independently inspected)",
  retrieved_at: "2026-11-20T02:22:48.871335+00:00",
  size_bytes: 647003080,
  actual_size_bytes: 647003079,
  sha256: "337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441",
  checksum_verified: false,
  content_length_verified: true,
  zip_crc_valid: true,
  zip_format_valid: true,
  acquisition_status: "PROVENANCE_CONFLICT",
  archive_integrity_status: "FAILED",
  data_quality_status: "QUALITY_REJECTED",
  status_explanation: "The inventory and archive evidence disagree.",
  validation_warnings: ["Actual archive size does not match the manifest."],
};

function resolveDashboardRequests() {
  vi.mocked(api.dataIntelligenceSummary).mockResolvedValue(summary);
  vi.mocked(api.dataIntelligenceSources).mockResolvedValue({
    items: [source],
    total: 1,
    limit: 100,
    offset: 0,
  });
  vi.mocked(api.dataIntelligenceAcquisitions).mockResolvedValue({
    items: [{
      id: source.id,
      name: source.name,
      inventory_status: "acquired",
      acquisition_status: "PROVENANCE_CONFLICT",
      archive_integrity_status: "FAILED",
      data_quality_status: "QUALITY_REJECTED",
      status_explanation: "The inventory and archive evidence disagree.",
      validation_warnings: ["Archive size does not match the manifest."],
      artifacts: [artifact],
    }],
    total: 1,
    limit: 100,
    offset: 0,
    validation_warnings: ["Archive size does not match the manifest."],
  });
  vi.mocked(api.dataIntelligenceQuality).mockResolvedValue({
    overall_decision: "NEEDS_MORE_DATA",
    overall_training_status: "REJECT_FOR_TRAINING",
    archives: [{
      request_number: 1,
      decision: "NEEDS_MORE_DATA",
      training_status: "REJECT_FOR_TRAINING",
      dynamic_timestamp_count: 2,
      coverage_start_utc: "2024-01-03T03:00:00Z",
      coverage_end_utc: "2024-01-03T06:00:00Z",
      observed_gap_hours: [3],
      global_grid_missing_fraction: 0.6586984082916898,
      missingness_scope: "Global-grid estimate; not a Kerala-specific missingness rate.",
      warning: "Insufficient temporal coverage; do not use this archive for training.",
    }],
  });
  vi.mocked(api.dataIntelligenceTrainingEligibility).mockResolvedValue({
    total_sources: 1,
    eligible_count: 0,
    items: {
      items: [{
        id: source.id,
        name: source.name,
        eligible_for_training: false,
        status: "INELIGIBLE",
        reasons: ["The inspected data quality report rejects this source for training."],
      }],
      total: 1,
      limit: 100,
      offset: 0,
    },
    note: "Signed provenance is still required.",
  });
  vi.mocked(api.dataIntelligenceCatalogue).mockResolvedValue({
    districts_total: 14,
    crop_categories_total: 4,
    crops_total: 31,
    crop_profiles_total: 31,
    verified_crop_profiles: 0,
    crop_profile_coverage_percent: 100,
    crop_varieties_total: 0,
    districts_with_suitability: 0,
    district_crop_associations_total: 0,
    district_suitability_coverage_percent: 0,
  });
  vi.mocked(api.dataIntelligenceProvenance).mockResolvedValue({
    items: [{
      id: source.id,
      name: source.name,
      publisher: source.publisher,
      license: source.license,
      dataset_version: null,
      version_status: "ACQUIRED_VERSION_UNPINNED",
      last_checked: source.last_checked,
      acquisition_status: "PROVENANCE_CONFLICT",
      archive_integrity_status: "FAILED",
      data_quality_status: "QUALITY_REJECTED",
      validation_warnings: ["Archive size does not match the manifest."],
      artifacts: [artifact],
    }],
    total: 1,
    limit: 100,
    offset: 0,
  });
}

function resolveEmptyDashboardRequests() {
  vi.mocked(api.dataIntelligenceSummary).mockResolvedValue({
    total_sources: 0,
    portfolio_status_counts: {},
    commercial_approval_counts: {},
    inventory_acquisition_counts: {},
    acquisition_status_counts: {},
    archive_integrity_status_counts: {},
    data_quality_status_counts: {},
    manifest_request_count: 0,
    manifest_reported_success_count: 0,
    training_eligible_count: 0,
    weather_decision: "NEEDS_MORE_DATA",
    weather_training_status: "REJECT_FOR_TRAINING",
    metadata_warnings: [],
    validation_warnings: [],
  });
  vi.mocked(api.dataIntelligenceSources).mockResolvedValue({ items: [], total: 0, limit: 100, offset: 0 });
  vi.mocked(api.dataIntelligenceAcquisitions).mockResolvedValue({
    items: [],
    total: 0,
    limit: 100,
    offset: 0,
    validation_warnings: [],
  });
  vi.mocked(api.dataIntelligenceQuality).mockResolvedValue({
    overall_decision: "NEEDS_MORE_DATA",
    overall_training_status: "REJECT_FOR_TRAINING",
    archives: [],
  });
  vi.mocked(api.dataIntelligenceTrainingEligibility).mockResolvedValue({
    total_sources: 0,
    eligible_count: 0,
    items: { items: [], total: 0, limit: 100, offset: 0 },
    note: "",
  });
  vi.mocked(api.dataIntelligenceCatalogue).mockResolvedValue({
    districts_total: 0,
    crop_categories_total: 0,
    crops_total: 0,
    crop_profiles_total: 0,
    verified_crop_profiles: 0,
    crop_profile_coverage_percent: null,
    crop_varieties_total: 0,
    districts_with_suitability: 0,
    district_crop_associations_total: 0,
    district_suitability_coverage_percent: null,
  });
  vi.mocked(api.dataIntelligenceProvenance).mockResolvedValue({ items: [], total: 0, limit: 100, offset: 0 });
}

describe("DataIntelligenceDashboard", () => {
  beforeEach(resolveDashboardRequests);
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("shows a loading state while the evidence requests are pending", () => {
    vi.mocked(api.dataIntelligenceSummary).mockReturnValue(new Promise(() => {}));

    render(<DataIntelligenceDashboard />);

    expect(screen.getByRole("status").textContent).toContain("Loading data intelligence evidence");
  });

  it("renders real-data status sections without presenting predictions", async () => {
    render(<DataIntelligenceDashboard />);

    expect(await screen.findByText("Dataset source inventory")).toBeTruthy();
    expect(screen.getByText("2 dynamic weather timestamps")).toBeTruthy();
    expect(screen.getByText("Coverage: 2024-01-03 03:00 UTC to 2024-01-03 06:00 UTC")).toBeTruthy();
    expect(screen.getByText("31")).toBeTruthy();
    expect(screen.getByText(/counts existing rows only/)).toBeTruthy();
    expect(screen.getByText("The inspected data quality report rejects this source for training.")).toBeTruthy();
    expect(screen.getAllByText("Provenance conflict").length).toBeGreaterThan(0);
    expect(screen.getByText("Exact CDS request parameters remain unconfirmed.")).toBeTruthy();
    expect(screen.getAllByText("Archive size does not match the manifest.")).toHaveLength(1);
    expect(screen.getByText(/does not generate crop predictions or recommendations/)).toBeTruthy();
  });

  it("uses acquisition metadata for an interactive source inventory chart", async () => {
    vi.mocked(api.dataIntelligenceSummary).mockResolvedValue({
      ...summary,
      total_sources: 2,
      acquisition_status_counts: { PROVENANCE_CONFLICT: 1, ACQUIRED_VERIFIED: 1 },
    });
    vi.mocked(api.dataIntelligenceSources).mockResolvedValue({
      items: [
        source,
        { ...source, id: "other-source", name: "Other source", acquisition_status: "ACQUIRED_VERIFIED" },
      ],
      total: 2,
      limit: 100,
      offset: 0,
    });

    render(<DataIntelligenceDashboard />);

    const statusBar = await screen.findByRole("button", { name: "Filter inventory by Provenance conflict (1)" });
    expect(screen.getByText(/Counts describe registered source metadata only/)).toBeTruthy();

    fireEvent.click(statusBar);

    expect(statusBar.getAttribute("aria-pressed")).toBe("true");
    expect(screen.getByText("1 of 2 records shown")).toBeTruthy();
    expect(screen.queryByText("Other source")).toBeNull();
  });

  it("renders acquisition data when it is the only successful API section", async () => {
    vi.mocked(api.dataIntelligenceSummary).mockRejectedValue(new Error("Service unavailable."));
    vi.mocked(api.dataIntelligenceSources).mockRejectedValue(new Error("Service unavailable."));
    vi.mocked(api.dataIntelligenceQuality).mockRejectedValue(new Error("Service unavailable."));
    vi.mocked(api.dataIntelligenceTrainingEligibility).mockRejectedValue(new Error("Service unavailable."));
    vi.mocked(api.dataIntelligenceCatalogue).mockRejectedValue(new Error("Service unavailable."));
    vi.mocked(api.dataIntelligenceProvenance).mockRejectedValue(new Error("Service unavailable."));

    render(<DataIntelligenceDashboard />);

    expect(await screen.findByText("era5_land_request_1.zip")).toBeTruthy();
    expect(screen.getByText("Some dashboard sections are unavailable.")).toBeTruthy();
    expect(screen.queryByText("Data intelligence could not be loaded.")).toBeNull();
  });

  it("keeps the empty state when every API section succeeds with no records", async () => {
    resolveEmptyDashboardRequests();

    render(<DataIntelligenceDashboard />);

    expect(await screen.findByText("No dataset sources are registered.")).toBeTruthy();
    expect(screen.getByText("No acquisition entries are available.")).toBeTruthy();
    expect(screen.queryByText("Data intelligence could not be loaded.")).toBeNull();
  });

  it("shows successful data and a partial error when some API sections fail", async () => {
    vi.mocked(api.dataIntelligenceSources).mockRejectedValue(new Error("Service unavailable."));
    vi.mocked(api.dataIntelligenceQuality).mockRejectedValue(new Error("Service unavailable."));

    render(<DataIntelligenceDashboard />);

    expect(await screen.findByText("Dataset source inventory")).toBeTruthy();
    expect(screen.getByText("era5_land_request_1.zip")).toBeTruthy();
    expect(screen.getByText("Some dashboard sections are unavailable.")).toBeTruthy();
    expect(screen.queryByText("Data intelligence could not be loaded.")).toBeNull();
  });

  it("shows a retryable error when every dashboard endpoint fails", async () => {
    const apiMethods = [
      api.dataIntelligenceSummary,
      api.dataIntelligenceSources,
      api.dataIntelligenceAcquisitions,
      api.dataIntelligenceQuality,
      api.dataIntelligenceTrainingEligibility,
      api.dataIntelligenceCatalogue,
      api.dataIntelligenceProvenance,
    ];
    for (const method of apiMethods) {
      vi.mocked(method).mockRejectedValue(new Error("Service unavailable."));
    }

    render(<DataIntelligenceDashboard />);

    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain("Data intelligence could not be loaded.");
    expect(screen.getByRole("button", { name: "Retry" })).toBeTruthy();
  });
});
