import type { Farm, Plot } from "../api";
import { boundaryToPolygons } from "../geojson";

type Props = {
  farm: Farm;
  plots: Plot[];
  selectedPlotId: string | null;
  onSelectPlot: (plotId: string) => void;
};

type Feature = {
  id: string;
  name: string;
  boundary: NonNullable<Farm["boundary"]>;
  kind: "farm" | "plot";
  selected: boolean;
};

const width = 720;
const height = 330;
const padding = 44;

export default function GeoBoundaryMap({ farm, plots, selectedPlotId, onSelectPlot }: Props) {
  const features: Feature[] = [
    ...(farm.boundary ? [{
      id: farm.id,
      name: `${farm.name} boundary`,
      boundary: farm.boundary,
      kind: "farm" as const,
      selected: false,
    }] : []),
    ...plots.map((plot) => ({
      id: plot.id,
      name: plot.name,
      boundary: plot.boundary,
      kind: "plot" as const,
      selected: plot.id === selectedPlotId,
    })),
  ];

  if (features.length === 0) {
    return (
      <div className="geo-map-empty" role="status">
        <strong>No mapped boundaries</strong>
        <span>Add a farm or plot GeoJSON boundary to view its coordinates here.</span>
      </div>
    );
  }

  let minLongitude = Number.POSITIVE_INFINITY;
  let maxLongitude = Number.NEGATIVE_INFINITY;
  let minLatitude = Number.POSITIVE_INFINITY;
  let maxLatitude = Number.NEGATIVE_INFINITY;
  for (const feature of features) {
    for (const polygon of boundaryToPolygons(feature.boundary)) {
      for (const ring of polygon) {
        for (const [longitude, latitude] of ring) {
          minLongitude = Math.min(minLongitude, longitude);
          maxLongitude = Math.max(maxLongitude, longitude);
          minLatitude = Math.min(minLatitude, latitude);
          maxLatitude = Math.max(maxLatitude, latitude);
        }
      }
    }
  }
  const longitudeFactor = Math.max(Math.abs(Math.cos(((minLatitude + maxLatitude) / 2) * Math.PI / 180)), 0.00001);
  const projectedMinLongitude = minLongitude * longitudeFactor;
  const projectedMaxLongitude = maxLongitude * longitudeFactor;
  const longitudeSpan = Math.max(projectedMaxLongitude - projectedMinLongitude, 0.00001);
  const latitudeSpan = Math.max(maxLatitude - minLatitude, 0.00001);
  const scale = Math.min((width - padding * 2) / longitudeSpan, (height - padding * 2) / latitudeSpan);

  function project([longitude, latitude]: [number, number]): [number, number] {
    return [
      width / 2 + (longitude * longitudeFactor - (projectedMinLongitude + projectedMaxLongitude) / 2) * scale,
      height / 2 - (latitude - (minLatitude + maxLatitude) / 2) * scale,
    ];
  }

  function pathFor(boundary: Feature["boundary"]): string {
    return boundaryToPolygons(boundary).map((polygon) =>
      polygon.map((ring) => {
        const [first, ...rest] = ring;
        const start = project(first);
        return `M ${start[0]} ${start[1]} ${rest.map((position) => {
          const [x, y] = project(position);
          return `L ${x} ${y}`;
        }).join(" ")} Z`;
      }).join(" "),
    ).join(" ");
  }

  return (
    <div className="geo-map">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="group"
        aria-label={`Coordinate map for ${farm.name}`}
      >
        <text x={width / 2} y={18} textAnchor="middle" className="geo-map-title">
          WGS84 coordinates · longitude and latitude
        </text>
        {[0, 1, 2, 3, 4].map((step) => {
          const longitude = minLongitude + step * (maxLongitude - minLongitude) / 4;
          const latitude = maxLatitude - step * latitudeSpan / 4;
          const centerLatitude = (minLatitude + maxLatitude) / 2;
          const centerLongitude = (minLongitude + maxLongitude) / 2;
          const x = project([longitude, centerLatitude])[0];
          const y = project([centerLongitude, latitude])[1];
          return (
            <g key={step} className="geo-grid">
              <line x1={x} y1={padding} x2={x} y2={height - padding} />
              <line x1={padding} y1={y} x2={width - padding} y2={y} />
              <text x={x} y={height - 15} textAnchor="middle">{longitude.toFixed(5)}</text>
              <text x={padding - 7} y={y + 3} textAnchor="end">{latitude.toFixed(5)}</text>
            </g>
          );
        })}
        {features.map((feature) => (
          <path
            key={`${feature.kind}-${feature.id}`}
            d={pathFor(feature.boundary)}
            className={`geo-boundary geo-boundary-${feature.kind}${feature.selected ? " is-selected" : ""}`}
            fillRule="evenodd"
            role={feature.kind === "plot" ? "button" : undefined}
            tabIndex={feature.kind === "plot" ? 0 : undefined}
            aria-label={feature.kind === "plot" ? `Select ${feature.name} on map` : feature.name}
            onClick={feature.kind === "plot" ? () => onSelectPlot(feature.id) : undefined}
            onKeyDown={feature.kind === "plot" ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelectPlot(feature.id);
              }
            } : undefined}
          />
        ))}
      </svg>
      <div className="geo-map-legend">
        {farm.boundary && <span><i className="geo-legend-farm" /> Farm boundary</span>}
        {plots.map((plot) => (
          <button
            type="button"
            key={plot.id}
            className={plot.id === selectedPlotId ? "is-selected" : ""}
            onClick={() => onSelectPlot(plot.id)}
          >
            <i className="geo-legend-plot" /> {plot.name}
          </button>
        ))}
      </div>
      <p className="geo-map-disclaimer">Boundary view only; no basemap or external map service is used.</p>
    </div>
  );
}
