export default function StampBadge({ label }: { label: string }) {
  return (
    <span className="stamp inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-seal">
      {label}
    </span>
  );
}
