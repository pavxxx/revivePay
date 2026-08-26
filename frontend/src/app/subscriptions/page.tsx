"use client";

import { useEffect, useState } from "react";
import { Repeat } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function SubscriptionsPage() {
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi<any[]>("/payments?limit=100")
      .then(res => setPayments(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const subPayments = payments.filter(p => p.subscription_id);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Recurring Subscriptions</h2>
        <p className="text-sm text-slate-500 mt-1">
          Automated subscription renewal recovery and past-due account interventions.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Subscription ID</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Recurring Amount</th>
                <th className="px-6 py-4">Billing Interval</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">Loading subscriptions...</td></tr>
              ) : subPayments.length === 0 ? (
                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">No past-due subscriptions logged.</td></tr>
              ) : (
                subPayments.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-mono font-semibold text-slate-900">{p.subscription_id}</td>
                    <td className="px-6 py-4 text-slate-900 font-semibold">{p.customer?.name || "Customer"}</td>
                    <td className="px-6 py-4 text-slate-900 font-bold">₹{p.amount.toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-600">Monthly Autopay</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                        PAST_DUE
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
