import type { Metrics } from "../interfaces";

export default function MetricsGrid({ metrics }: { metrics: Metrics }) {
  return (
    <div className="metrics-grid">
      {Object.entries(metrics).map(([k, v]) => (
        <div key={k} className="metric-card">
          <div className="metric-title">
            {k.replace(/([A-Z])/g, " $1")}
          </div>
          <div className="metric-value">
            {typeof v === "number"
              ? v.toLocaleString(undefined, { maximumFractionDigits: 2 })
              : v}
            {(k.toLowerCase().includes("rate") ||
              k.toLowerCase().includes("return") ||
              k.toLowerCase().includes("drawdown"))
              ? "%"
              : ""}
          </div>
        </div>
      ))}
    </div>
  );
}