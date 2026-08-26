"use client";

import { useEffect, useState } from "react";
import { Users, Search } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function CustomersPage() {
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi<any[]>("/payments?limit=100")
      .then(res => setPayments(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const customers = Array.from(
    new Map(payments.filter(p => p.customer).map(p => [p.customer.id, p.customer])).values()
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Customers Directory</h2>
        <p className="text-sm text-slate-500 mt-1">
          Profiles, payment history stats, tenure, and historical success rates.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Email</th>
                <th className="px-6 py-4">Tenure</th>
                <th className="px-6 py-4">Historical Success Rate</th>
                <th className="px-6 py-4">Avg Txn Amount</th>
                <th className="px-6 py-4">Total / Success / Failed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-slate-400">Loading customers...</td></tr>
              ) : (
                customers.map((c: any) => (
                  <tr key={c.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-900">{c.name}</td>
                    <td className="px-6 py-4 text-slate-600">{c.email}</td>
                    <td className="px-6 py-4 text-slate-700">{c.tenure_days} days</td>
                    <td className="px-6 py-4 font-bold text-emerald-600">
                      {Math.round((c.historical_success_rate || 0.8) * 100)}%
                    </td>
                    <td className="px-6 py-4 text-slate-900 font-bold">₹{c.avg_txn_amount.toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-600">
                      {c.total_payments} total ({c.successful_payments} succ / {c.failed_payments} fail)
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
