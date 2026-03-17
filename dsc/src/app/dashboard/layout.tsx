import { Sidebar } from "@components/Sidebar";
import { TopNavbar } from "@components/TopNavbar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex gap-4 mt-2">
      <Sidebar />
      <div className="flex-1 flex flex-col gap-4">
        <TopNavbar />
        <main className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.9fr),minmax(280px,0.9fr)] gap-4">
          <div className="flex flex-col gap-4">{children}</div>
        </main>
      </div>
    </div>
  );
}

