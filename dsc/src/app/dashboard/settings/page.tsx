export default function SettingsPage() {
  return (
    <section className="glass-surface rounded-xl px-4 py-4">
      <h2 className="text-sm font-semibold text-slate-100 tracking-tight mb-1.5">
        Settings
      </h2>
      <p className="text-xs text-slate-500 mb-4">
        Basic placeholder for future configuration of AI sensitivity, layout presets, and exam policies.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-300">
        <div className="rounded-lg bg-slate-950/70 border border-slate-800/80 px-3 py-3">
          <p className="font-medium mb-1">AI Sensitivity</p>
          <p className="text-[11px] text-slate-500">
            Configure how aggressively AI flags suspicious behaviors such as gaze deviation
            and secondary devices.
          </p>
        </div>
        <div className="rounded-lg bg-slate-950/70 border border-slate-800/80 px-3 py-3">
          <p className="font-medium mb-1">Layout Presets</p>
          <p className="text-[11px] text-slate-500">
            Define custom CCTV-style layouts and favorite student tiles for quick access.
          </p>
        </div>
      </div>
    </section>
  );
}

