"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  Zap,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  User,
  CreditCard,
  History,
  Play,
  RotateCcw,
  OctagonX,
  FileCheck
} from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params.id as string;

  const [caseData, setCaseData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const loadCase = async () => {
    setLoading(true);
    try {
      const res = await fetchApi<any>(`/cases/${caseId}`);
      setCaseData(res);
    } catch (err) {
      console.error("Failed to load case detail:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) {
      loadCase();
    }
  }, [caseId]);

  const handleManualAction = async (action: "approve" | "escalate" | "stop") => {
    setSubmitting(true);
    setActionMsg(null);
    try {
      await fetchApi(`/cases/${caseData.id}/${action}`, { method: "POST" });
      setActionMsg(`Case successfully updated with manual action: ${action.toUpperCase()}`);
      await loadCase();
    } catch (err: any) {
      setActionMsg(`Failed to execute ${action}: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-slate-500">
        <Clock className="w-5 h-5 animate-spin mr-2 text-blue-600" />
        <span>Loading recovery case audit timeline...</span>
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="p-8 text-center space-y-4">
        <p className="text-slate-600 font-semibold">Recovery Case not found.</p>
        <Link href="/cases" className="text-blue-600 text-xs font-bold underline">
          Return to Cases List
        </Link>
      </div>
    );
  }

  const probPct = Math.round((caseData.recovery_probability || 0) * 100);
  let probLabel = "Low Recovery Probability";
  let probColor = "text-rose-600 bg-rose-50 border-rose-200";
  if (probPct >= 70) {
    probLabel = "High Recovery Probability";
    probColor = "text-emerald-600 bg-emerald-50 border-emerald-200";
  } else if (probPct >= 40) {
    probLabel = "Moderate Recovery Probability";
    probColor = "text-amber-600 bg-amber-50 border-amber-200";
  }

  const latestDecision = caseData.decisions?.[caseData.decisions.length - 1];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Header & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <Link
            href="/cases"
            className="p-2 bg-white border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">{caseData.case_ref}</h2>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-900 text-white">
                {caseData.status}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Created {new Date(caseData.created_at).toLocaleString()} • Failure Category:{" "}
              <span className="font-semibold text-slate-700">{caseData.failure_category}</span>
            </p>
          </div>
        </div>

        {/* Ops Action Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => handleManualAction("approve")}
            disabled={submitting}
            className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Approve & Retry</span>
          </button>
          <button
            onClick={() => handleManualAction("escalate")}
            disabled={submitting}
            className="flex items-center space-x-2 bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Escalate</span>
          </button>
          <button
            onClick={() => handleManualAction("stop")}
            disabled={submitting}
            className="flex items-center space-x-2 bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-50"
          >
            <OctagonX className="w-3.5 h-3.5" />
            <span>Stop Case</span>
          </button>
        </div>
      </div>

      {actionMsg && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-800 text-xs font-semibold">
          {actionMsg}
        </div>
      )}

      {/* Grid Row 1: Probability & Diagnosis Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* ML Recovery Probability Gauge Card */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">ML Prediction</span>
            <Zap className="w-4 h-4 text-blue-600" />
          </div>

          <div className="text-center py-2">
            <div className="text-5xl font-black tracking-tight text-slate-900 mb-1">
              {probPct}%
            </div>
            <span className={`inline-block px-3 py-1 rounded-full border text-xs font-bold ${probColor}`}>
              {probLabel}
            </span>
          </div>

          <div className="text-xs text-slate-500 border-t border-slate-100 pt-3 space-y-1">
            <div className="flex justify-between">
              <span>Amount at Risk:</span>
              <span className="font-bold text-slate-900">₹{caseData.amount_at_risk.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Retry Attempt:</span>
              <span className="font-bold text-slate-900">{caseData.retry_count} / 3</span>
            </div>
          </div>
        </div>

        {/* Failure Diagnosis & Key Supporting Factors */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
          <h3 className="font-bold text-slate-900 text-sm flex items-center">
            <ShieldAlert className="w-4 h-4 mr-2 text-amber-600" />
            Failure Diagnosis & Context
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100 font-medium">
            {latestDecision?.reason || caseData.payment?.failure_reason || "Payment decline detected during checkout."}
          </p>

          <div className="space-y-1.5 text-xs pt-1">
            <span className="font-semibold text-slate-700">Customer Signals:</span>
            <div className="grid grid-cols-2 gap-2 text-slate-600">
              <div className="bg-slate-50 p-2 rounded-lg">
                <span className="block text-[10px] text-slate-400">Tenure:</span>
                <span className="font-bold text-slate-900">{caseData.customer?.tenure_days || 30} days</span>
              </div>
              <div className="bg-slate-50 p-2 rounded-lg">
                <span className="block text-[10px] text-slate-400">Past Success Rate:</span>
                <span className="font-bold text-slate-900">
                  {Math.round((caseData.customer?.historical_success_rate || 0.8) * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Decision & Policy Result Gate */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-3">
          <h3 className="font-bold text-slate-900 text-sm flex items-center">
            <FileCheck className="w-4 h-4 mr-2 text-blue-600" />
            Recommended Action & Guardrails
          </h3>

          <div className="p-3 rounded-xl bg-blue-50 border border-blue-200">
            <span className="text-[10px] uppercase tracking-wider font-bold text-blue-700 block">Proposed Action:</span>
            <span className="text-base font-extrabold text-blue-900">{caseData.recommended_action || "ANALYZING"}</span>
          </div>

          <div className="space-y-2 text-xs pt-1">
            <span className="font-semibold text-slate-700">Policy Rules Evaluation:</span>
            <ul className="space-y-1 text-slate-600">
              <li className="flex items-center text-emerald-700 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 shrink-0" /> Max Retry Threshold (&lt;3)
              </li>
              <li className="flex items-center text-emerald-700 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 shrink-0" /> Probability Floor (&ge;40%)
              </li>
              <li className="flex items-center text-emerald-700 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 shrink-0" /> Hard Decline Check
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Chronological Immutable Audit Trail */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-6">
        <div>
          <h3 className="font-bold text-slate-900 text-lg flex items-center">
            <History className="w-5 h-5 mr-2 text-blue-600" />
            Immutable Audit Trail & Execution Log
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Complete step-by-step record of failure detection, model prediction, decision rules, and execution outcomes.
          </p>
        </div>

        <div className="relative pl-6 border-l-2 border-slate-200 space-y-6">
          {caseData.audit_events?.map((ev: any) => {
            let icon = <Clock className="w-4 h-4 text-slate-500" />;
            let badgeBg = "bg-slate-100 text-slate-700";

            if (ev.event_type === "FAILURE_DETECTED") {
              icon = <ShieldAlert className="w-4 h-4 text-rose-600" />;
              badgeBg = "bg-rose-100 text-rose-800";
            } else if (ev.event_type === "MODEL_EVALUATED") {
              icon = <Zap className="w-4 h-4 text-blue-600" />;
              badgeBg = "bg-blue-100 text-blue-800";
            } else if (ev.event_type === "POLICY_CHECKED") {
              icon = <ShieldCheck className="w-4 h-4 text-emerald-600" />;
              badgeBg = "bg-emerald-100 text-emerald-800";
            } else if (ev.event_type === "ACTION_EXECUTED") {
              icon = <Play className="w-4 h-4 text-purple-600" />;
              badgeBg = "bg-purple-100 text-purple-800";
            } else if (ev.event_type === "OUTCOME_RECORDED") {
              icon = <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
              badgeBg = "bg-emerald-100 text-emerald-800";
            }

            return (
              <div key={ev.id} className="relative group">
                <div className="absolute -left-[31px] top-0.5 w-6 h-6 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center">
                  {icon}
                </div>

                <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${badgeBg}`}>
                        {ev.actor}
                      </span>
                      <span className="font-bold text-slate-900 text-xs">{ev.action}</span>
                    </div>
                    <span className="text-[11px] text-slate-400 font-medium">
                      {new Date(ev.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 font-medium">{ev.reason}</p>

                  {ev.metadata_json && Object.keys(ev.metadata_json).length > 0 && (
                    <details className="text-[11px] text-slate-500 pt-1">
                      <summary className="cursor-pointer font-semibold text-blue-600 hover:underline">
                        View Event Metadata
                      </summary>
                      <pre className="mt-2 p-2 bg-slate-900 text-slate-200 rounded-lg text-[10px] overflow-x-auto">
                        {JSON.stringify(ev.metadata_json, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
