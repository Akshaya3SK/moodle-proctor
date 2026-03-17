import { examReports } from "@mock/data";

export const ReportTable = () => {
  return (
    <section className="glass-surface rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex flex-col">
          <h2 className="text-sm font-semibold text-slate-100 tracking-tight">
            Exam Reports
          </h2>
          <p className="text-[11px] text-slate-500">
            Post-exam evidence packages and AI summaries.
          </p>
        </div>
        <span className="text-[11px] text-slate-400">
          Total: <span className="font-semibold text-slate-100">{examReports.length}</span>
        </span>
      </div>

      <div className="overflow-x-auto scroll-thin">
        <table className="min-w-full text-xs">
          <thead className="bg-slate-950/80 border-b border-slate-800/80">
            <tr className="text-[11px] text-slate-400 uppercase tracking-[0.16em]">
              <th className="text-left px-4 py-2 font-normal">Student</th>
              <th className="text-left px-4 py-2 font-normal">Exam</th>
              <th className="text-left px-4 py-2 font-normal">Alerts</th>
              <th className="text-left px-4 py-2 font-normal">Upload Status</th>
              <th className="text-right px-4 py-2 font-normal">Actions</th>
            </tr>
          </thead>
          <tbody>
            {examReports.map((report, idx) => (
              <tr
                key={report.id}
                className={["border-b border-slate-900/60", idx % 2 === 0 ? "bg-slate-950/40" : ""].join(
                  " "
                )}
              >
                <td className="px-4 py-2.5 text-slate-100 text-xs whitespace-nowrap">
                  {report.studentName}
                </td>
                <td className="px-4 py-2.5 text-slate-300 text-[11px] whitespace-nowrap">
                  {report.exam}
                </td>
                <td className="px-4 py-2.5 text-[11px] text-slate-200">
                  {report.alertsCount}
                </td>
                <td className="px-4 py-2.5">
                  <span
                    className={[
                      "inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium border",
                      report.uploadStatus === "Completed"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/40"
                        : report.uploadStatus === "Processing"
                        ? "bg-sky-500/10 text-sky-300 border-sky-500/40"
                        : report.uploadStatus === "Pending"
                        ? "bg-amber-500/10 text-amber-300 border-amber-500/40"
                        : "bg-red-500/10 text-red-400 border-red-500/40"
                    ].join(" ")}
                  >
                    {report.uploadStatus}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-right whitespace-nowrap">
                  <button className="text-[11px] text-sky-300 hover:text-sky-200 mr-3">
                    View
                  </button>
                  <button className="text-[11px] text-slate-300 hover:text-slate-100">
                    Download
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

