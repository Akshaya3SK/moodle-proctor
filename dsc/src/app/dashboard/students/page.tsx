import { students } from "@mock/data";
import { StatusBadge } from "@components/StatusBadge";

export default function StudentsPage() {
  return (
    <section className="glass-surface rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex flex-col">
          <h2 className="text-sm font-semibold text-slate-100 tracking-tight">
            Students
          </h2>
          <p className="text-[11px] text-slate-500">
            All students registered for the current examination session.
          </p>
        </div>
        <span className="text-[11px] text-slate-400">
          Total: <span className="font-semibold text-slate-100">{students.length}</span>
        </span>
      </div>

      <div className="overflow-x-auto scroll-thin">
        <table className="min-w-full text-xs">
          <thead className="bg-slate-950/80 border-b border-slate-800/80">
            <tr className="text-[11px] text-slate-400 uppercase tracking-[0.16em]">
              <th className="text-left px-4 py-2 font-normal">Student Name</th>
              <th className="text-left px-4 py-2 font-normal">Student ID</th>
              <th className="text-left px-4 py-2 font-normal">Exam</th>
              <th className="text-left px-4 py-2 font-normal">Status</th>
              <th className="text-left px-4 py-2 font-normal">Connection</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student, idx) => (
              <tr
                key={student.id}
                className={["border-b border-slate-900/60", idx % 2 === 0 ? "bg-slate-950/40" : ""].join(
                  " "
                )}
              >
                <td className="px-4 py-2.5 text-slate-100 text-xs whitespace-nowrap">
                  {student.name}
                </td>
                <td className="px-4 py-2.5 text-slate-300 text-[11px] whitespace-nowrap">
                  {student.id}
                </td>
                <td className="px-4 py-2.5 text-[11px] text-slate-300 whitespace-nowrap">
                  {student.exam}
                </td>
                <td className="px-4 py-2.5">
                  <StatusBadge status={student.status} />
                </td>
                <td className="px-4 py-2.5 text-[11px] text-slate-300">
                  {student.connection}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

