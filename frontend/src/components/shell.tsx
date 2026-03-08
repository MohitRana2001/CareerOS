import Link from "next/link";
import { BriefcaseBusiness, FileUser, LayoutDashboard, Sparkles } from "lucide-react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/resumes", label: "Resumes", icon: FileUser },
  { href: "/tailor-runs", label: "Tailoring", icon: Sparkles },
  { href: "/applications", label: "Applications", icon: BriefcaseBusiness },
];

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl gap-6 px-4 py-6 md:px-8">
      <aside className="card hidden w-64 shrink-0 p-4 md:block">
        <h2 className="mb-4 text-lg font-semibold">CareerOS</h2>
        <nav className="space-y-2">
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} className="flex items-center gap-2 rounded-lg px-3 py-2 hover:bg-black/5">
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="flex-1">{children}</main>
    </div>
  );
}
