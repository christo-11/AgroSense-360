import { useEffect, useState } from "react";
import type {
  AgriculturalSource,
  Crop,
  CropCategory,
  CropProfile,
  CropVariety,
  District,
  DistrictCropAssociation,
} from "../api";
import { api } from "../api";

function VerificationBadge({ status }: { status: string }) {
  const label = status === "verified" ? "Verified" : status === "rejected" ? "Rejected" : "Pending verification";
  return <span className={`verification-badge verification-${status}`}>{label}</span>;
}

function SourceReferences({ sources }: { sources: AgriculturalSource[] }) {
  if (sources.length === 0) {
    return <p className="catalog-muted">No source references recorded.</p>;
  }
  return (
    <ul className="source-reference-list">
      {sources.map((source) => (
        <li key={source.id}>
          <a href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
          <span>{source.publisher}{source.license ? ` · ${source.license}` : ""}</span>
          {source.accessed_on && <small>Accessed {source.accessed_on}</small>}
        </li>
      ))}
    </ul>
  );
}

function profileValue(profile: CropProfile, field: string): string {
  const value = profile[field as keyof CropProfile];
  if (value === null || value === undefined || value === "") return "Not documented";
  if (Array.isArray(value)) return value.length > 0 ? value.join(", ") : "Not documented";
  if (typeof value === "number") return String(value);
  return String(value);
}

function rangeValue(minimum: number | null, maximum: number | null, unit: string): string {
  if (minimum === null && maximum === null) return "Not documented";
  if (minimum === null) return `Up to ${maximum} ${unit}`;
  if (maximum === null) return `From ${minimum} ${unit}`;
  return `${minimum}–${maximum} ${unit}`;
}

function associationLabel(association: DistrictCropAssociation): string {
  if (association.verification_status !== "verified") {
    return association.verification_status === "rejected" ? "Rejected" : "Pending verification — not a recommendation";
  }
  return association.suitability_status === "suitable"
    ? "Verified suitable"
    : association.suitability_status === "not_suitable"
      ? "Verified not suitable"
      : "Under review";
}

export default function CropExplorer() {
  const [districts, setDistricts] = useState<District[]>([]);
  const [categories, setCategories] = useState<CropCategory[]>([]);
  const [catalogError, setCatalogError] = useState("");
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [categoryId, setCategoryId] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropsTotal, setCropsTotal] = useState(0);
  const [cropsLoading, setCropsLoading] = useState(false);
  const [cropsError, setCropsError] = useState("");
  const [selectedCropId, setSelectedCropId] = useState("");
  const [selectedCrop, setSelectedCrop] = useState<Crop | null>(null);
  const [profile, setProfile] = useState<CropProfile | null>(null);
  const [varieties, setVarieties] = useState<CropVariety[]>([]);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");
  const [selectedDistrictId, setSelectedDistrictId] = useState("");
  const [districtAssociations, setDistrictAssociations] = useState<DistrictCropAssociation[]>([]);
  const [districtLoading, setDistrictLoading] = useState(false);
  const [districtError, setDistrictError] = useState("");

  useEffect(() => {
    let active = true;
    setCatalogLoading(true);
    void Promise.all([api.districts(100), api.cropCategories(100)]).then(([districtPage, categoryPage]) => {
      if (!active) return;
      setDistricts(districtPage.items);
      setCategories(categoryPage.items);
      setCatalogError("");
    }).catch((error: unknown) => {
      if (active) setCatalogError(error instanceof Error ? error.message : "Could not load the agricultural catalogue.");
    }).finally(() => {
      if (active) setCatalogLoading(false);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    setCropsLoading(true);
    setCropsError("");
    setSelectedCropId("");
    setSelectedCrop(null);
    setProfile(null);
    setVarieties([]);
    void api.crops({ categoryId: categoryId || undefined, search, limit: 50, offset: 0 }).then((page) => {
      if (!active) return;
      setCrops(page.items);
      setCropsTotal(page.total);
    }).catch((error: unknown) => {
      if (active) {
        setCrops([]);
        setCropsTotal(0);
        setCropsError(error instanceof Error ? error.message : "Could not load crops.");
      }
    }).finally(() => {
      if (active) setCropsLoading(false);
    });
    return () => { active = false; };
  }, [categoryId, search]);

  useEffect(() => {
    if (!selectedCropId) {
      setSelectedCrop(null);
      setProfile(null);
      setVarieties([]);
      setDetailError("");
      return;
    }

    let active = true;
    setDetailLoading(true);
    setDetailError("");
    void Promise.all([
      api.crop(selectedCropId),
      api.cropProfile(selectedCropId),
      api.cropVarieties(selectedCropId, 100),
    ]).then(([crop, cropProfile, varietyPage]) => {
      if (!active) return;
      setSelectedCrop(crop);
      setProfile(cropProfile);
      setVarieties(varietyPage.items);
    }).catch((error: unknown) => {
      if (active) {
        setSelectedCrop(null);
        setProfile(null);
        setVarieties([]);
        setDetailError(error instanceof Error ? error.message : "Could not load crop details.");
      }
    }).finally(() => {
      if (active) setDetailLoading(false);
    });
    return () => { active = false; };
  }, [selectedCropId]);

  useEffect(() => {
    if (!selectedDistrictId) {
      setDistrictAssociations([]);
      setDistrictError("");
      setDistrictLoading(false);
      return;
    }

    let active = true;
    setDistrictLoading(true);
    setDistrictError("");
    void api.districtCrops(selectedDistrictId, 100).then((page) => {
      if (active) setDistrictAssociations(page.items);
    }).catch((error: unknown) => {
      if (active) {
        setDistrictAssociations([]);
        setDistrictError(error instanceof Error ? error.message : "Could not load district associations.");
      }
    }).finally(() => {
      if (active) setDistrictLoading(false);
    });
    return () => { active = false; };
  }, [selectedDistrictId]);

  async function loadMoreCrops() {
    setCropsLoading(true);
    setCropsError("");
    try {
      const page = await api.crops({
        categoryId: categoryId || undefined,
        search,
        limit: 50,
        offset: crops.length,
      });
      setCrops((current) => [...current, ...page.items]);
    } catch (error) {
      setCropsError(error instanceof Error ? error.message : "Could not load more crops.");
    } finally {
      setCropsLoading(false);
    }
  }

  const currentDistrict = districts.find((district) => district.id === selectedDistrictId);

  return (
    <section className="crop-explorer">
      <div className="catalog-heading">
        <div>
          <div className="eyebrow"><span className="live-dot" /> KERALA AGRICULTURAL MASTER CATALOGUE</div>
          <h2>Districts, crops & verified profiles</h2>
          <p>Unverified profile fields and district associations are shown as pending, not as cultivation advice.</p>
        </div>
        <label className="district-filter">
          <span>Explore a district</span>
          <select
            value={selectedDistrictId}
            onChange={(event) => setSelectedDistrictId(event.target.value)}
            disabled={catalogLoading}
          >
            <option value="">Select a Kerala district</option>
            {districts.map((district) => <option key={district.id} value={district.id}>{district.name}</option>)}
          </select>
        </label>
      </div>

      {catalogLoading && <p className="catalog-state" role="status">Loading districts and crop categories…</p>}
      {catalogError && <p className="catalog-error" role="alert">{catalogError}</p>}

      <div className="catalog-filters">
        <label>
          Crop category
          <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)} disabled={catalogLoading}>
            <option value="">All categories</option>
            {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
          </select>
        </label>
        <form onSubmit={(event) => { event.preventDefault(); setSearch(searchInput.trim()); }}>
          <label htmlFor="crop-search">Search crops</label>
          <div>
            <input id="crop-search" value={searchInput} onChange={(event) => setSearchInput(event.target.value)} maxLength={120} />
            <button type="submit" className="button button-secondary">Search</button>
          </div>
        </form>
        <span className="catalog-result-count">{cropsTotal} catalogue entries</span>
      </div>

      {cropsError && <p className="catalog-error" role="alert">{cropsError}</p>}
      {cropsLoading && <p className="catalog-state" role="status">Loading crops…</p>}
      {!cropsLoading && !cropsError && crops.length === 0 && (
        <div className="catalog-empty"><strong>No crops found</strong><span>Try another search or category.</span></div>
      )}
      {crops.length > 0 && (
        <div className="crop-catalog-layout">
          <div>
            <div className="crop-card-grid">
              {crops.map((crop) => (
                <button
                  type="button"
                  key={crop.id}
                  className={`crop-card ${crop.id === selectedCropId ? "is-selected" : ""}`}
                  onClick={() => setSelectedCropId(crop.id)}
                  aria-pressed={crop.id === selectedCropId}
                >
                  <span className="crop-card-top"><strong>{crop.common_name}</strong><VerificationBadge status={crop.verification_status} /></span>
                  <span>{crop.category.name}</span>
                  <small>{crop.scientific_name ?? "Scientific name pending verification"}</small>
                </button>
              ))}
            </div>
            {crops.length < cropsTotal && (
              <button type="button" className="button button-secondary load-more" onClick={() => void loadMoreCrops()} disabled={cropsLoading}>
                {cropsLoading ? "Loading…" : "Load more"}
              </button>
            )}
          </div>

          <aside className="district-explorer glass-card" aria-label="District crop explorer">
            <div className="catalog-panel-heading">
              <div><h3>{currentDistrict?.name ?? "District crop explorer"}</h3><p>{currentDistrict ? "Recorded crop associations" : "Choose a district to inspect sourced associations."}</p></div>
            </div>
            {districtLoading && <p className="catalog-state" role="status">Loading district associations…</p>}
            {districtError && <p className="catalog-error" role="alert">{districtError}</p>}
            {currentDistrict && !districtLoading && !districtError && districtAssociations.length === 0 && (
              <div className="catalog-empty compact"><strong>No sourced associations recorded</strong><span>This does not mean crops are unsuitable; no district-specific records are available yet.</span></div>
            )}
            {districtAssociations.length > 0 && (
              <ul className="district-crop-list">
                {districtAssociations.map((association) => (
                  <li key={association.id}>
                    <button type="button" onClick={() => setSelectedCropId(association.crop_id)}>{association.crop_name}</button>
                    {association.variety_name && <span>{association.variety_name}</span>}
                    <VerificationBadge status={association.verification_status} />
                    <small>{associationLabel(association)}</small>
                    <SourceReferences sources={association.sources} />
                  </li>
                ))}
              </ul>
            )}
          </aside>
        </div>
      )}

      {detailLoading && <p className="catalog-state" role="status">Loading crop profile and varieties…</p>}
      {detailError && <p className="catalog-error" role="alert">{detailError}</p>}
      {selectedCrop && profile && (
        <article className="crop-detail glass-card">
          <header className="crop-detail-header">
            <div>
              <span className="crop-category-label">{selectedCrop.category.name}</span>
              <h3>{selectedCrop.common_name}</h3>
              <p>{selectedCrop.scientific_name ?? "Scientific name not yet verified"}</p>
            </div>
            <VerificationBadge status={profile.verification_status} />
          </header>
          <p className="profile-updated">Profile last updated: {new Date(profile.last_updated_at).toLocaleDateString()}</p>
          <div className="profile-grid">
            <div><strong>Suitable temperature</strong><span>{rangeValue(profile.temperature_min_celsius, profile.temperature_max_celsius, "°C")}</span></div>
            <div><strong>Annual rainfall</strong><span>{rangeValue(profile.rainfall_min_mm_year, profile.rainfall_max_mm_year, "mm/year")}</span></div>
            <div><strong>Soil type</strong><span>{profileValue(profile, "soil_type")}</span></div>
            <div><strong>Soil pH</strong><span>{rangeValue(profile.soil_ph_min, profile.soil_ph_max, "pH")}</span></div>
            <div><strong>Planting season</strong><span>{profileValue(profile, "planting_season")}</span></div>
            <div><strong>Irrigation</strong><span>{profileValue(profile, "irrigation_requirements")}</span></div>
            <div><strong>Fertilizer</strong><span>{profileValue(profile, "fertilizer_recommendations")}</span></div>
            <div><strong>Cultivation practices</strong><span>{profileValue(profile, "cultivation_practices")}</span></div>
            <div><strong>Plant spacing</strong><span>{rangeValue(profile.plant_spacing_min_cm, profile.plant_spacing_max_cm, "cm")}</span></div>
            <div><strong>Growth duration</strong><span>{rangeValue(profile.growth_duration_min_days, profile.growth_duration_max_days, "days")}</span></div>
            <div><strong>Harvesting</strong><span>{profileValue(profile, "harvesting_information")}</span></div>
            <div><strong>Common pests and diseases</strong><span>{profileValue(profile, "common_pests_diseases")}</span></div>
            <div><strong>Expected yield</strong><span>{rangeValue(profile.expected_yield_min, profile.expected_yield_max, profile.expected_yield_unit ?? "unit not specified")}</span></div>
          </div>
          {profile.verification_status !== "verified" && (
            <p className="pending-profile-note" role="note">This profile is not verified. Blank fields are intentionally not estimated or recommended.</p>
          )}
          <section className="profile-sources">
            <h4>Sources</h4>
            <SourceReferences sources={profile.sources} />
          </section>
          <section className="profile-varieties">
            <h4>Varieties</h4>
            {varieties.length === 0
              ? <p className="catalog-muted">No variety records are available.</p>
              : (
                <ul>
                  {varieties.map((variety) => (
                    <li key={variety.id}>
                      <div><strong>{variety.name}</strong><VerificationBadge status={variety.verification_status} /></div>
                      <p>{variety.scientific_name ?? variety.description ?? "No additional verified details recorded."}</p>
                      <SourceReferences sources={variety.sources} />
                    </li>
                  ))}
                </ul>
              )}
          </section>
        </article>
      )}
    </section>
  );
}
