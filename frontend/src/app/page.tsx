"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  DollarSign,
  TrendingUp,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  Search,
  Filter,
  RefreshCw,
  Zap
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from "recharts";
import { fetchApi } from "@/lib/api";

const STATUS_COLORS: Record<string, string> = {
  RECOVERED: "#10b981", // emerald
  IN_PROGRESS: "#3b82f6", // blue
  ESCALATED: "#f59e0b", // amber
  STOPPED: "#f43f5e", // rose
  FAILED: "#64748b", // slate
};

export default function OverviewPage() {
  const [summary, setSummary] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [failures, setFailures] = useState<any[]>([]);
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, trendRes, failRes, caseRes] = await Promise.all([
        fetchApi<any>("/dashboard/summary"),
        fetchApi<any[]>("/dashboard/recovery-trends?days=30"),
        fetchApi<any[]>("/analytics/failures"),
        fetchApi<any[]>("/cases?limit=10")
      ]);
      setSummary(sumRes);
      setTrends(trendRes);
      setFailures(failRes);
      setCases(caseRes);
    } catch (err) {
      console.error("Failed to load overview data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading || !summary) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-3 text-slate-500">
          <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
          <span className="text-sm font-medium">Computing revenue metrics from database...</span>
        </div>
      </div>
    );
  }

  // Pie chart data
  const pieData = [
    { name: "Recovered", value: summary.recovered_cases_count, color: STATUS_COLORS.RECOVERED },
    { name: "Active", value: summary.active_cases_count, color: STATUS_COLORS.IN_PROGRESS },
    { name: "Escalated", value: summary.escalated_cases_count, color: STATUS_COLORS.ESCALATED },
    { name: "Stopped", value: summary.stopped_cases_count, color: STATUS_COLORS.STOPPED },
    { name: "Failed", value: summary.failed_cases_count, color: STATUS_COLORS.FAILED },
  ].filter(d => d.value > 0);

  const filteredCases = cases.filter(c =>
    c.case_ref.toLowerCase().includes(search.toLowerCase()) ||
    (c.customer?.name || "").toLowerCase().includes(search.toLowerCase()) ||
    (c.failure_category || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
            Overview — Recover more revenue. Automate intelligently.
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Real-time revenue recovery metrics computed directly from database audit records.
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search case, customer..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>
          <button
            onClick={loadData}
            className="p-2 bg-white border border-slate-200 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors cursor-pointer"
            title="Refresh database state"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Card 1: Revenue at Risk */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Revenue at Risk</span>
            <div className="w-9 h-9 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
            ₹{summary.revenue_at_risk.toLocaleString()}
          </div>
          <div className="flex items-center text-xs text-slate-500 space-x-1">
            <span className="font-semibold text-slate-700">{summary.total_cases_count}</span>
            <span>total failure cases logged</span>
          </div>
        </div>

        {/* Card 2: Revenue Recovered */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Revenue Recovered</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-emerald-600 tracking-tight">
            ₹{summary.revenue_recovered.toLocaleString()}
          </div>
          <div className="flex items-center text-xs text-emerald-700 font-medium space-x-1">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{summary.recovered_cases_count} payments successfully recovered</span>
          </div>
        </div>

        {/* Card 3: Recovery Rate */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Recovery Rate</span>
            <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <Zap className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {summary.recovery_rate}%
          </div>
          <div className="flex items-center text-xs text-slate-500 space-x-1">
            <span>Attempt success rate:</span>
            <span className="font-semibold text-slate-700">{summary.attempt_success_rate}%</span>
          </div>
        </div>

        {/* Card 4: Active Cases */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Cases</span>
            <div className="w-9 h-9 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {summary.active_cases_count}
          </div>
          <div className="flex items-center text-xs text-amber-700 font-medium space-x-2">
            <span>{summary.escalated_cases_count} Escalated</span>
            <span>•</span>
            <span>{summary.stopped_cases_count} Stopped</span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Line Chart: 30D Revenue Recovery Trend */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Revenue at Risk vs. Recovered (30 Days)</h3>
              <p className="text-xs text-slate-500">Daily tracked revenue performance from DB audit logs</p>
            </div>
          </div>
          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <XAxis dataKey="date" tickLine={false} axisLine={{ stroke: '#e2e8f0' }} tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tickLine={false} axisLine={{ stroke: '#e2e8f0' }} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '12px' }}
                  formatter={(val: any) => [`₹${Number(val).toLocaleString()}`, '']}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="at_risk" name="Revenue at Risk" stroke="#f43f5e" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="recovered" name="Revenue Recovered" stroke="#10b981" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Donut Chart: Case Status Breakdown */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Case Status Distribution</h3>
            <p className="text-xs text-slate-500">Live breakdown of all case statuses</p>
          </div>
          <div className="h-56 w-full relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', color: '#fff', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center space-x-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-slate-600 font-medium">{item.name}:</span>
                <span className="font-bold text-slate-900">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bar Chart & Recent Cases Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bar Chart: Top Failure Reasons */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Top Failure Categories</h3>
            <p className="text-xs text-slate-500">Distribution of revenue loss by root cause</p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={failures} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                <XAxis type="number" tickLine={false} axisLine={{ stroke: '#e2e8f0' }} tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis type="category" dataKey="category" tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#475569' }} width={90} />
                <Tooltip formatter={(val: any) => [`₹${Number(val).toLocaleString()}`, 'Amount at Risk']} />
                <Bar dataKey="amount" fill="#3b82f6" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Recovery Cases Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Recent Recovery Cases</h3>
              <p className="text-xs text-slate-500">Click any row to inspect decision reasoning & policy checks</p>
            </div>
            <Link href="/cases" className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center">
              View All Cases <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-y border-slate-100 text-slate-500 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="px-4 py-3">Case ID</th>
                  <th className="px-4 py-3">Customer</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Failure Category</th>
                  <th className="px-4 py-3">Probability</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {filteredCases.map((c) => {
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
                    <tr
                      key={c.id}
                      className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3 font-semibold text-blue-600">
                        <Link href={`/cases/${c.id}`}>{c.case_ref}</Link>
                      </td>
                      <td className="px-4 py-3 text-slate-800 font-semibold">{c.customer?.name || "Customer"}</td>
                      <td className="px-4 py-3 text-slate-900 font-bold">₹{c.amount_at_risk.toLocaleString()}</td>
                      <td className="px-4 py-3 text-slate-600">{c.failure_category}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2.5 py-1 rounded-full border text-[11px] font-bold ${probBadge}`}>
                          {probPct}%
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${statusBadge}`}>
                          {c.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-600 font-medium">
                        {c.recommended_action || "ANALYZING"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
