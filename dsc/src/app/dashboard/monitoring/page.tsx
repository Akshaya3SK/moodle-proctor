import { AlertPanel } from "@components/AlertPanel";
import { StudentsGrid } from "@components/StudentsGrid";

export default function LiveMonitoringPage() {
  return (
    <>
      <StudentsGrid />
      <AlertPanel />
    </>
  );
}

