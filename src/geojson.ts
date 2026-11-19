import type { GeoJSONBoundary, GeoJSONPolygonCoordinates, GeoJSONPosition } from "./api";

function isPosition(value: unknown): value is GeoJSONPosition {
  return Array.isArray(value)
    && value.length === 2
    && value.every((coordinate) => typeof coordinate === "number" && Number.isFinite(coordinate))
    && value[0] >= -180
    && value[0] <= 180
    && value[1] >= -90
    && value[1] <= 90;
}

function isPolygonCoordinates(value: unknown): value is GeoJSONPolygonCoordinates {
  return Array.isArray(value) && value.length > 0 && value.every((ring) => {
    if (!Array.isArray(ring) || ring.length < 4 || !ring.every(isPosition)) return false;
    const first = ring[0];
    const last = ring[ring.length - 1];
    return first[0] === last[0] && first[1] === last[1];
  });
}

export function isGeoJSONBoundary(value: unknown): value is GeoJSONBoundary {
  if (!value || typeof value !== "object" || !("type" in value) || !("coordinates" in value)) {
    return false;
  }
  if (value.type === "Polygon") return isPolygonCoordinates(value.coordinates);
  return value.type === "MultiPolygon"
    && Array.isArray(value.coordinates)
    && value.coordinates.length > 0
    && value.coordinates.every(isPolygonCoordinates);
}

export function parseBoundaryJson(raw: string, required: boolean): GeoJSONBoundary | null {
  if (!raw.trim()) {
    if (required) throw new Error("A GeoJSON plot boundary is required.");
    return null;
  }

  let value: unknown;
  try {
    value = JSON.parse(raw);
  } catch {
    throw new Error("Boundary must be valid GeoJSON JSON.");
  }
  if (!isGeoJSONBoundary(value)) {
    throw new Error("Use a closed GeoJSON Polygon or MultiPolygon with WGS84 [longitude, latitude] coordinates.");
  }
  return value;
}

export function boundaryToPolygons(boundary: GeoJSONBoundary): GeoJSONPolygonCoordinates[] {
  return boundary.type === "Polygon" ? [boundary.coordinates] : boundary.coordinates;
}

export function formatBoundary(boundary: GeoJSONBoundary | null): string {
  return boundary ? JSON.stringify(boundary, null, 2) : "";
}
