"use client";

import { useEffect, useState } from "react";
import { CreditCard, Search, RefreshCw } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function PaymentsPage() {
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi<any[]>("/payments?limit=100")
      .then(res => setPayments(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Payment Transactions</h2>
        <p className="text-sm text-slate-500 mt-1">
          Raw payment transactions ingested from payment gateways and Razorpay Webhooks.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Payment Ref</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Method</th>
                <th className="px-6 py-4">Failure Reason</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr><td colSpan={7} className="px-6 py-8 text-center text-slate-400">Loading payments...</td></tr>
              ) : (
                payments.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-mono font-semibold text-slate-900">{p.payment_ref}</td>
                    <td className="px-6 py-4 text-slate-900 font-semibold">{p.customer?.name || "Customer"}</td>
                    <td className="px-6 py-4 text-slate-900 font-bold">₹{p.amount.toLocaleString()}</td>
                    <td className="px-6 py-4 text-slate-600">{p.payment_method}</td>
                    <td className="px-6 py-4 text-slate-600">{p.failure_reason || "-"}</td>
                    <td className="px-6 py-4 text-slate-700 font-semibold">{p.failure_category}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        p.status === "SUCCESS" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"
                      }`}>
                        {p.status}
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
