import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { api, ApiError } from "./api";
import App from "./App";

vi.mock("./api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./api")>();
  return {
    ...actual,
    api: {
      ...actual.api,
      status: vi.fn(),
      adminSummary: vi.fn(),
      farms: vi.fn(),
      dashboardSummary: vi.fn(),
      signIn: vi.fn(),
      register: vi.fn(),
      changePassword: vi.fn(),
      signOut: vi.fn(),
    },
  };
});

vi.mock("./components/FarmWorkspace", () => ({ default: () => null }));
vi.mock("./components/CropExplorer", () => ({
  default: () => <label>Search crops<input id="crop-search" aria-label="Search crops" /></label>,
}));
vi.mock("./components/DataIntelligenceDashboard", () => ({ default: () => null }));
vi.mock("./components/MarketWorkspace", () => ({ default: () => <div>Market price filters</div> }));
vi.mock("./components/AdminWorkspace", () => ({ default: () => <h2>Admin dashboard</h2> }));
vi.mock("./components/FarmTwin", () => ({ default: () => null }));
vi.mock("./components/PortfolioDemo", () => ({
  PortfolioDataSources: () => null,
  PortfolioLanding: () => null,
  ProjectArchitecture: () => null,
}));

describe("App navigation", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.clearAllMocks();
    vi.mocked(api.status).mockResolvedValue({
      api: "online",
      database: "connected",
      public_demo_mode: false,
      integrations: {},
      models: {},
    });
    vi.mocked(api.adminSummary).mockResolvedValue({
      users: 1,
      farms: 0,
      plots: 0,
      districts: 14,
      crops: 0,
      verified_crop_profiles: 0,
      verified_district_associations: 0,
      source_references: 0,
      integrations: {},
      models: {},
    });
    vi.mocked(api.farms).mockResolvedValue([]);
    vi.mocked(api.dashboardSummary).mockResolvedValue({ farm_count: 0, plot_count: 0 });
    vi.mocked(api.signIn).mockImplementation(async () => {
      sessionStorage.setItem("agrosense_token", "test-token");
      return false;
    });
    vi.mocked(api.register).mockResolvedValue({ id: "test-user" });
    vi.mocked(api.changePassword).mockResolvedValue({ status: "password_changed" });
    vi.mocked(api.signOut).mockImplementation(() => sessionStorage.removeItem("agrosense_token"));
    Object.defineProperty(window, "matchMedia", {
      configurable: true,
      value: vi.fn().mockReturnValue({ matches: false }),
    });
  });

  afterEach(cleanup);

  function renderAuthenticatedApp() {
    sessionStorage.setItem("agrosense_token", "test-token");
    return render(<App />);
  }

  it("opens and closes the mobile navigation when a section is selected", async () => {
    renderAuthenticatedApp();
    await screen.findByRole("navigation", { name: "Main navigation" });

    fireEvent.click(screen.getByRole("button", { name: "Open menu" }));
    expect(screen.getByRole("button", { name: "Close menu" }).getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByRole("button", { name: "Close navigation" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Crop catalogue" }));

    expect(screen.getByRole("button", { name: "Crop catalogue" }).getAttribute("aria-current")).toBe("page");
    expect(screen.getByRole("button", { name: "Open menu" }).getAttribute("aria-expanded")).toBe("false");
    expect(screen.queryByRole("button", { name: "Close navigation" })).toBeNull();
  });

  it("routes search to the catalogue and focuses its search field", async () => {
    renderAuthenticatedApp();
    await screen.findByRole("navigation", { name: "Main navigation" });

    fireEvent.click(screen.getByRole("button", { name: "Search crop catalogue" }));

    const searchField = await screen.findByRole("textbox", { name: "Search crops" });
    await waitFor(() => expect(document.activeElement).toBe(searchField));
  });

  it("requires authentication before showing dashboard pages", async () => {
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Welcome to AgroSense" })).toBeTruthy();
    expect(screen.queryByRole("navigation", { name: "Main navigation" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Markets" })).toBeNull();
  });

  it("opens the market prices module", async () => {
    renderAuthenticatedApp();
    await screen.findByRole("navigation", { name: "Main navigation" });

    fireEvent.click(screen.getByRole("button", { name: "Markets" }));

    expect(await screen.findByText("Market price filters")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Markets" }).getAttribute("aria-current")).toBe("page");
  });

  it("shows the admin dashboard only when the server confirms allowlisted access", async () => {
    sessionStorage.setItem("agrosense_token", "test-token");
    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: "Admin" }));

    expect(await screen.findByRole("heading", { name: "Admin dashboard" })).toBeTruthy();
    expect(api.adminSummary).toHaveBeenCalledOnce();
  });

  it("signs in through the existing API and opens the dashboard", async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "farmer@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "a-secure-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("navigation", { name: "Main navigation" })).toBeTruthy();
    expect(api.signIn).toHaveBeenCalledWith("farmer@example.com", "a-secure-password");
    expect(sessionStorage.getItem("agrosense_token")).toBe("test-token");
  });

  it("shows incorrect-credential errors on the login page", async () => {
    vi.mocked(api.signIn).mockRejectedValueOnce(new ApiError("Incorrect email or password.", 401));
    render(<App />);
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "farmer@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "wrong-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("alert")).toHaveProperty("textContent", "Incorrect email or password.");
  });

  it("shows a clear message when the login API cannot be reached", async () => {
    vi.mocked(api.signIn).mockRejectedValueOnce(new TypeError("Failed to fetch"));
    render(<App />);
    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "farmer@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "a-secure-password" } });
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("alert")).toHaveProperty(
      "textContent",
      "Could not connect to AgroSense. Check the API connection and try again.",
    );
  });

  it("clears the token and returns to login when the farmer logs out", async () => {
    renderAuthenticatedApp();
    expect(await screen.findByRole("navigation", { name: "Main navigation" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Log out" }));

    expect(await screen.findByRole("heading", { name: "Welcome to AgroSense" })).toBeTruthy();
    expect(screen.queryByRole("navigation", { name: "Main navigation" })).toBeNull();
    expect(sessionStorage.getItem("agrosense_token")).toBeNull();
  });

  it("restores a saved session after the app is mounted again", async () => {
    renderAuthenticatedApp();

    expect(await screen.findByRole("navigation", { name: "Main navigation" })).toBeTruthy();
    expect(sessionStorage.getItem("agrosense_token")).toBe("test-token");
    expect(api.farms).toHaveBeenCalled();
  });
});
