"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Search, Filter, ArrowUpRight, RefreshCw, FolderKanban } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function CasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");

  const loadCases = async () => {
    setLoading(true);
    try {
      let url = "/cases?limit=100";
      if (statusFilter) url += `&status=${statusFilter}`;
      if (categoryFilter) url += `&failure_category=${categoryFilter}`;
      const res = await fetchApi<any[]>(url);
      setCases(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, [statusFilter, categoryFilter]);

  const filtered = cases.filter(c =>
    c.case_ref.toLowerCase().includes(search.toLowerCase()) ||
    (c.customer?.name || "").toLowerCase().includes(search.toLowerCase()) ||
    (c.failure_category || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Recovery Cases</h2>
          <p className="text-sm text-slate-500 mt-1">
            Active and historical payment recovery cases managed by the autonomous agent engine.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search case ref, customer..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="RECOVERED">Recovered</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="ESCALATED">Escalated</option>
            <option value="STOPPED">Stopped</option>
            <option value="FAILED">Failed</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none"
          >
            <option value="">All Categories</option>
            <option value="TRANSIENT_NETWORK">Transient Network</option>
            <option value="INSUFFICIENT_FUNDS">Insufficient Funds</option>
            <option value="AUTHENTICATION_REQUIRED">Auth Required</option>
            <option value="CARD_EXPIRED">Card Expired</option>
            <option value="PERMANENT_HARD_DECLINE">Hard Decline</option>
            <option value="FRAUD_OR_STOLEN">Fraud / Stolen</option>
          </select>

          <button
            onClick={loadCases}
            className="p-2 bg-white border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
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
                <th className="px-6 py-4">Recovery Prob.</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Intervention Action</th>
                <th className="px-6 py-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-slate-400">
                    Loading cases from database...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-8 text-center text-slate-400">
                    No cases match the selected filters.
                  </td>
                </tr>
              ) : (
                filtered.map((c) => {
                  const probPct = Math.round(c.recovery_probability * 100);
                  let probBadge = "bg-rose-50 text-rose-700 border-rose-200";
                  if (probPct >= 70) probBadge = "bg-emerald-50 text-emerald-700 border-emerald-200";
                  else if (probPct >= 40) probBadge = "bg-amber-50 text-amber-700 border-amber-200";

                  let statusBadge = "bg-slate-100 text-slate-700";
                  if (c.status === "RECOVERED") statusBadge = "bg-emerald-50 text-emerald-700 border border-emerald-200";
                  else if (c.status === "ESCALATED") statusBadge = "bg-amber-50 text-amber-700 border border-amber-200";
                  else if (c.status === "STOPPED") statusBadge = "bg-rose-50 text-rose-700 border border-rose-200";
                  else if (c.status === "IN_PROGRESS") statusBadge = "bg-blue-50 text-blue-700 border border-blue-200";

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
                        <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${statusBadge}`}>
                          {c.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-700">{c.recommended_action || "ANALYZING"}</td>
                      <td className="px-6 py-4 text-right">
                        <Link
                          href={`/cases/${c.id}`}
                          className="text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center"
                        >
                          View <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
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
