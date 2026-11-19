import type { Integration } from "../api";

export default function StatusPill({ item }: { item: Integration | undefined }) {
  const ready = item?.status === "ready";
  const label = ready
    ? "Connected"
    : item?.status === "configured"
      ? "Credentials set"
      : item?.status === "unavailable"
        ? "Unavailable"
        : "Status unknown";
  return (
    <span className={`status-pill ${ready ? "is-ready" : "is-offline"}`}>
      <span className="status-dot" />
      {label}
    </span>
  );
}
