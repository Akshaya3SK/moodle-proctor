import { AlertPanel } from "@components/AlertPanel";
import { ReportTable } from "@components/ReportTable";
import { StudentsGrid } from "@components/StudentsGrid";

export default function DashboardOverviewPage() {
  return (
    <>
      <StudentsGrid />
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <AlertPanel />
        <ReportTable />
      </div>
    </>
  );
}

