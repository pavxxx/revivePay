"use client";

import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function InvoicesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi<any[]>("/cases?limit=50")
      .then(res => setCases(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Invoices Recovery Monitor</h2>
        <p className="text-sm text-slate-500 mt-1">
          Unpaid invoice collection and payment link dispatch tracking.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Invoice Ref</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Amount Due</th>
                <th className="px-6 py-4">Recovery Action</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">Loading invoice recovery list...</td></tr>
              ) : (
                cases.slice(0, 15).map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-mono font-semibold text-blue-600">INV-{c.case_ref.slice(-8)}</td>
                    <td className="px-6 py-4 text-slate-900 font-semibold">{c.customer?.name || "Customer"}</td>
                    <td className="px-6 py-4 text-slate-900 font-bold">₹{c.amount_at_risk.toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-700">{c.recommended_action || "RETRY"}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        c.status === "RECOVERED" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-slate-100 text-slate-700"
                      }`}>
                        {c.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
