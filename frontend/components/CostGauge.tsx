import { Estimate } from "@/lib/types";
import { formatINR } from "@/lib/format";

const TIER_COLOR: Record<Estimate["confidence_label"], string> = {
  high: "#0E6B5C",
  medium: "#C98A1B",
  low: "#B23A2E",
};

export default function CostGauge({ estimate }: { estimate: Estimate }) {
  // Domain gives a little headroom past the max so the range doesn't
  // touch the very edge of the ruler.
  const domainMax = Math.max(estimate.cost_max * 1.15, 1);
  const pct = (v: number) => Math.min((v / domainMax) * 100, 100);

  const minPct = pct(estimate.cost_min);
  const maxPct = pct(estimate.cost_max);
  const avgPct = pct(estimate.cost_avg);
  const color = TIER_COLOR[estimate.confidence_label];

  const ticks = [0, 0.25, 0.5, 0.75, 1];

  return (
    <div
      className="w-full max-w-sm"
      role="img"
      aria-label={`Cost range from ${formatINR(estimate.cost_min)} to ${formatINR(
        estimate.cost_max
      )}, typical cost ${formatINR(estimate.cost_avg)}`}
    >
      {/* Typical-cost callout, floating above its position on the ruler */}
      <div className="relative h-14">
        <div
          className="absolute -translate-x-1/2 flex flex-col items-center"
          style={{ left: `${avgPct}%` }}
        >
          <span className="text-[11px] uppercase tracking-wide text-ink-soft whitespace-nowrap">
            Typical
          </span>
          <span className="font-mono text-lg font-bold whitespace-nowrap" style={{ color }}>
            {formatINR(estimate.cost_avg)}
          </span>
        </div>
      </div>

      {/* The ruler itself */}
      <div className="relative h-3 rounded-full bg-line">
        {/* verified range highlight */}
        <div
          className="absolute top-0 h-3 rounded-full"
          style={{
            left: `${minPct}%`,
            width: `${Math.max(maxPct - minPct, 1.5)}%`,
            backgroundColor: color,
            opacity: 0.85,
          }}
        />
        {/* typical-cost pin */}
        <div
          className="absolute -top-1 -translate-x-1/2 w-5 h-5 rounded-full bg-white border-[3px]"
          style={{ left: `${avgPct}%`, borderColor: color }}
        />
        {/* scale ticks */}
        {ticks.map((t) => (
          <div
            key={t}
            className="absolute top-4 w-px h-2 bg-ink-soft/30"
            style={{ left: `${t * 100}%` }}
          />
        ))}
      </div>

      {/* min / max labels anchored under their actual position */}
      <div className="relative h-8 mt-1">
        <div className="absolute -translate-x-1/2 text-center" style={{ left: `${minPct}%` }}>
          <div className="text-[11px] uppercase tracking-wide text-ink-soft whitespace-nowrap">Low end</div>
          <div className="font-mono text-sm font-semibold text-ink whitespace-nowrap">
            {formatINR(estimate.cost_min)}
          </div>
        </div>
        <div className="absolute -translate-x-1/2 text-center" style={{ left: `${maxPct}%` }}>
          <div className="text-[11px] uppercase tracking-wide text-ink-soft whitespace-nowrap">High end</div>
          <div className="font-mono text-sm font-semibold text-ink whitespace-nowrap">
            {formatINR(estimate.cost_max)}
          </div>
        </div>
      </div>
    </div>
  );
}
