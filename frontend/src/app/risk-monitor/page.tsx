"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ShieldAlert, ArrowUpRight, Filter, Search, Zap } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function RiskMonitorPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<"probability" | "amount">("probability");

  useEffect(() => {
    fetchApi<any[]>("/cases?limit=100")
      .then(res => setCases(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const atRiskCases = cases.filter(c => c.status !== "RECOVERED");
  const sorted = [...atRiskCases].sort((a, b) => {
    if (sortBy === "probability") return b.recovery_probability - a.recovery_probability;
    return b.amount_at_risk - a.amount_at_risk;
  });

  const totalAtRisk = atRiskCases.reduce((sum, c) => sum + c.amount_at_risk, 0);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Risk Monitor</h2>
          <p className="text-sm text-slate-500 mt-1">
            Prioritized monitor of all active revenue at risk, highlighting highest recovery opportunities.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-xs text-slate-500 font-semibold">Sort by:</span>
          <button
            onClick={() => setSortBy("probability")}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold cursor-pointer border ${
              sortBy === "probability"
                ? "bg-blue-600 text-white border-blue-600 shadow-xs"
                : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
            }`}
          >
            Highest Probability
          </button>
          <button
            onClick={() => setSortBy("amount")}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold cursor-pointer border ${
              sortBy === "amount"
                ? "bg-blue-600 text-white border-blue-600 shadow-xs"
                : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
            }`}
          >
            Highest Amount
          </button>
        </div>
      </div>

      {/* Overview Banner */}
      <div className="bg-gradient border border-rose-200 bg-rose-50/50 rounded-2xl p-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-2xl bg-rose-100 border border-rose-200 flex items-center justify-center text-rose-600">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-rose-800">Total Outstanding At-Risk Revenue</span>
            <div className="text-3xl font-extrabold text-slate-900">₹{totalAtRisk.toLocaleString()}</div>
          </div>
        </div>
        <div className="text-right text-xs text-slate-600 font-medium hidden sm:block">
          <div><span className="font-bold text-slate-900">{atRiskCases.length}</span> active cases currently monitored</div>
          <div>Policy safety rules actively protecting revenue</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Case Reference</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Amount at Risk</th>
                <th className="px-6 py-4">Failure Category</th>
                <th className="px-6 py-4">ML Recovery Prob.</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Inspect Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400">Loading risk matrix...</td>
                </tr>
              ) : (
                sorted.map((c) => {
                  const probPct = Math.round(c.recovery_probability * 100);
                  let probBadge = "bg-rose-50 text-rose-700 border-rose-200";
                  if (probPct >= 70) probBadge = "bg-emerald-50 text-emerald-700 border-emerald-200";
                  else if (probPct >= 40) probBadge = "bg-amber-50 text-amber-700 border-amber-200";

                  return (
                    <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-4 font-bold text-blue-600">
                        <Link href={`/cases/${c.id}`}>{c.case_ref}</Link>
                      </td>
                      <td className="px-6 py-4 text-slate-900 font-semibold">{c.customer?.name || "Customer"}</td>
                      <td className="px-6 py-4 text-slate-900 font-bold">₹{c.amount_at_risk.toLocaleString()}</td>
                      <td className="px-6 py-4 text-slate-600">{c.failure_category}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-1 rounded-full border text-[11px] font-bold ${probBadge}`}>
                          {probPct}%
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-100 text-slate-800">
                          {c.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link href={`/cases/${c.id}`} className="text-blue-600 font-semibold inline-flex items-center">
                          View Policy <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
