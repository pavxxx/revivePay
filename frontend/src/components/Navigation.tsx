"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  ShieldAlert,
  FolderKanban,
  Zap,
  Users,
  CreditCard,
  Repeat,
  FileText,
  AlertTriangle,
  BarChart3,
  History,
  Settings,
  Play,
  CheckCircle2,
  Cpu,
  UserCheck
} from "lucide-react";
import { fetchApi } from "@/lib/api";

const NAV_ITEMS = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Risk Monitor", href: "/risk-monitor", icon: ShieldAlert },
  { name: "Recovery Cases", href: "/cases", icon: FolderKanban },
  { name: "Actions", href: "/actions", icon: Zap },
  { name: "Customers", href: "/customers", icon: Users },
  { name: "Payments", href: "/payments", icon: CreditCard },
  { name: "Subscriptions", href: "/subscriptions", icon: Repeat },
  { name: "Invoices", href: "/invoices", icon: FileText },
  { name: "Escalations", href: "/escalations", icon: AlertTriangle },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Audit Trail", href: "/audit", icon: History },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-neutral-800 text-neutral-200 flex flex-col min-h-screen border-r border-neutral-700 shrink-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-neutral-700 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-neutral-700 border border-neutral-600 flex items-center justify-center text-white font-bold text-xl shadow-xs">
          R
        </div>
        <div>
          <h1 className="font-bold text-white text-lg tracking-tight leading-none">RevivePay</h1>
          <p className="text-xs text-neutral-400 font-medium mt-1">Autonomous Revenue Recovery</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                isActive
                  ? "bg-neutral-700 text-white shadow-xs font-semibold border border-neutral-600"
                  : "text-neutral-300 hover:text-white hover:bg-neutral-700/50"
              }`}
            >
              <Icon className={`w-4 h-4 mr-3 shrink-0 ${isActive ? "text-white" : "text-neutral-400"}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Profile Footer */}
      <div className="p-4 border-t border-neutral-700 flex items-center justify-between bg-neutral-900/80">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="w-8 h-8 rounded-full bg-neutral-700 border border-neutral-600 flex items-center justify-center text-white text-xs font-semibold shrink-0">
            MO
          </div>
          <div className="truncate">
            <p className="text-xs font-semibold text-white truncate">Merchant Ops Admin</p>
            <p className="text-[11px] text-neutral-400 truncate">admin@revivepay.io</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function TopHeader() {
  const router = useRouter();
  const [isRunning, setIsRunning] = useState(false);
  const [lastBatchMsg, setLastBatchMsg] = useState<string | null>(null);

  const handleRunDemoBatch = async () => {
    try {
      setIsRunning(true);
      setLastBatchMsg(null);
      const res: any = await fetchApi("/batches/run?batch_size=500", { method: "POST" });
      setLastBatchMsg(`Batch ${res.batch_ref} completed! Processed 500 events (Recovered: ₹${res.revenue_recovered?.toLocaleString()})`);
      router.refresh();
    } catch (err: any) {
      console.error(err);
      setLastBatchMsg("Failed to run demo batch.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      <div className="flex items-center space-x-4">
        {/* Environment Label Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold">
          <Cpu className="w-3.5 h-3.5 text-slate-600" />
          <span>ENVIRONMENT:</span>
          <span className="text-slate-900 font-bold">SIMULATION / RAZORPAY TEST MODE</span>
        </div>
        
        {/* Subtitle note */}
        <span className="text-xs text-slate-400 hidden lg:inline">
          Deterministic ML models & policy guardrails active
        </span>
      </div>

      <div className="flex items-center space-x-4">
        {lastBatchMsg && (
          <span className="text-xs text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200 font-medium animate-pulse">
            {lastBatchMsg}
          </span>
        )}

        <button
          onClick={handleRunDemoBatch}
          disabled={isRunning}
          className="flex items-center space-x-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-xl text-xs font-semibold transition-all disabled:opacity-50 shadow-xs cursor-pointer"
        >
          <Play className={`w-3.5 h-3.5 text-slate-300 ${isRunning ? "animate-spin" : ""}`} />
          <span>{isRunning ? "Processing 500 Events..." : "Run Demo Batch (500 Events)"}</span>
        </button>
      </div>
    </header>
  );
}
