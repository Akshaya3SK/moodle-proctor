import { FiBell, FiClock, FiSearch, FiUser } from "react-icons/fi";
import { alerts } from "@mock/data";

export const TopNavbar = () => {
  const activeAlerts = alerts.length;

  return (
    <header className="flex items-center justify-between glass-surface px-4 py-3">
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
          <span className="hidden md:inline">Current Exam:</span>
          <span className="font-medium text-slate-200">Physics Midterm - Group A</span>
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="uppercase tracking-[0.18em] text-[10px] text-emerald-400">
            Live
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center gap-2 text-xs text-slate-400">
          <FiClock className="h-3.5 w-3.5" />
          <span>Remaining Time:</span>
          <span className="font-semibold text-slate-100">01:23:18</span>
        </div>

        <div className="hidden sm:flex items-center gap-2 glass-surface px-2 py-1 rounded-full">
          <FiSearch className="h-3.5 w-3.5 text-slate-500" />
          <input
            placeholder="Search student, ID, exam..."
            className="bg-transparent border-none outline-none text-xs w-40 text-slate-200 placeholder:text-slate-500"
          />
        </div>

        <button className="relative h-9 w-9 flex items-center justify-center rounded-full bg-slate-900/80 border border-slate-700/70 hover:border-accent.blue/60 transition-colors">
          <FiBell className="h-4 w-4 text-slate-300" />
          {activeAlerts > 0 && (
            <span className="absolute -top-0.5 -right-0.5 h-4 min-w-[16px] rounded-full bg-red-500 text-[10px] font-semibold flex items-center justify-center px-0.5">
              {activeAlerts}
            </span>
          )}
        </button>

        <div className="flex items-center gap-2 pl-3 border-l border-slate-800/90">
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-sky-500 to-emerald-400 flex items-center justify-center text-xs font-semibold">
            T
          </div>
          <div className="hidden sm:flex flex-col">
            <span className="text-xs font-medium text-slate-100">Dr. Alice Nguyen</span>
            <span className="text-[10px] text-slate-500 flex items-center gap-1">
              <FiUser className="h-3 w-3" />
              Proctor
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

