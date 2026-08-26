"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Zap, ArrowUpRight, CheckCircle2, XCircle, Clock } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function ActionsPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi<any[]>("/cases?limit=100")
      .then(res => setCases(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const casesWithAttempts = cases.filter(c => c.attempts && c.attempts.length > 0);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Executed Recovery Actions</h2>
        <p className="text-sm text-slate-500 mt-1">
          Detailed log of automated payment retries, customer notifications, and intervention attempts.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Case Ref</th>
                <th className="px-6 py-4">Attempt #</th>
                <th className="px-6 py-4">Action Type</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Payment Reference</th>
                <th className="px-6 py-4 text-right">Case Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-400">Loading actions log...</td></tr>
              ) : casesWithAttempts.length === 0 ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-400">No executed recovery actions logged yet.</td></tr>
              ) : (
                casesWithAttempts.flatMap((c) =>
                  c.attempts.map((att: any) => (
                    <tr key={att.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-4 font-bold text-blue-600">
                        <Link href={`/cases/${c.id}`}>{c.case_ref}</Link>
                      </td>
                      <td className="px-6 py-4 font-semibold text-slate-700">#{att.attempt_number}</td>
                      <td className="px-6 py-4 font-bold text-slate-900">{att.action_type}</td>
                      <td className="px-6 py-4 text-slate-900 font-bold">₹{c.amount_at_risk.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          att.status === "SUCCESS" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"
                        }`}>
                          {att.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500 font-mono text-[11px]">{att.payment_reference || "N/A"}</td>
                      <td className="px-6 py-4 text-right">
                        <Link href={`/cases/${c.id}`} className="text-blue-600 font-semibold inline-flex items-center">
                          Inspect <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
                        </Link>
                      </td>
                    </tr>
                  ))
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
