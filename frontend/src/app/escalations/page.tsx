"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, OctagonX, ArrowUpRight, ShieldCheck, User } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function EscalationsPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState<string | null>(null);

  const loadEscalations = async () => {
    setLoading(true);
    try {
      const res = await fetchApi<any[]>("/cases?is_escalated=true&limit=50");
      setCases(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEscalations();
  }, []);

  const handleAction = async (caseId: string, action: "approve" | "escalate" | "stop") => {
    setSubmittingId(caseId);
    try {
      await fetchApi(`/cases/${caseId}/${action}`, { method: "POST" });
      await loadEscalations();
    } catch (err: any) {
      alert(`Action failed: ${err.message}`);
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Escalations Queue</h2>
        <p className="text-sm text-slate-500 mt-1">
          High-value payments or retry-limit breaches flagged by the policy guardrail engine requiring merchant ops authorization.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400">Loading escalations queue...</div>
      ) : cases.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-xs space-y-3">
          <ShieldCheck className="w-12 h-12 text-emerald-500 mx-auto" />
          <h3 className="text-lg font-bold text-slate-900">No Pending Escalations</h3>
          <p className="text-xs text-slate-500">All payment recovery cases are operating automatically within policy guardrails.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {cases.map((c) => {
            const probPct = Math.round(c.recovery_probability * 100);
            return (
              <div key={c.id} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-blue-600 text-sm">{c.case_ref}</span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                      ESCALATED
                    </span>
                  </div>
                  <span className="text-lg font-black text-slate-900">₹{c.amount_at_risk.toLocaleString()}</span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex items-center justify-between text-slate-600">
                    <span>Customer:</span>
                    <span className="font-semibold text-slate-900">{c.customer?.name || "Customer"}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-600">
                    <span>Failure Category:</span>
                    <span className="font-semibold text-slate-900">{c.failure_category}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-600">
                    <span>ML Recovery Prob:</span>
                    <span className="font-bold text-blue-600">{probPct}%</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-600">
                    <span>Prior Retries:</span>
                    <span className="font-semibold text-slate-900">{c.retry_count} / 3</span>
                  </div>
                </div>

                {/* Escalation Reason Box */}
                <div className="bg-amber-50/80 border border-amber-200 p-3 rounded-xl text-xs space-y-1">
                  <span className="font-bold text-amber-900 block flex items-center">
                    <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600" />
                    Escalation Trigger Reason:
                  </span>
                  <p className="text-amber-800 font-medium leading-relaxed">
                    {c.escalation_reason || "Flagged for manual review."}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-2 pt-2 border-t border-slate-100">
                  <button
                    onClick={() => handleAction(c.id, "approve")}
                    disabled={submittingId === c.id}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-50 flex items-center justify-center space-x-1"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approve & Retry</span>
                  </button>
                  <button
                    onClick={() => handleAction(c.id, "stop")}
                    disabled={submittingId === c.id}
                    className="flex-1 bg-rose-600 hover:bg-rose-700 text-white py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-50 flex items-center justify-center space-x-1"
                  >
                    <OctagonX className="w-3.5 h-3.5" />
                    <span>Stop Case</span>
                  </button>
                  <Link
                    href={`/cases/${c.id}`}
                    className="p-2 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors"
                    title="Inspect Audit Timeline"
                  >
                    <ArrowUpRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
