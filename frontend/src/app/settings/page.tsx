"use client";

import { useState } from "react";
import { Settings, ShieldCheck, Save, Lock, AlertCircle, RefreshCw } from "lucide-react";

export default function SettingsPage() {
  const [maxRetries, setMaxRetries] = useState(3);
  const [probFloor, setProbFloor] = useState(0.40);
  const [maxAmount, setMaxAmount] = useState(50000);
  const [cooldown, setCooldown] = useState(24);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedMsg("Policy Guardrail Rules updated and applied across all active autonomous agents.");
    setTimeout(() => setSavedMsg(null), 4000);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Policy Engine & Guardrail Rules</h2>
        <p className="text-sm text-slate-500 mt-1">
          Configure safety rules and mandatory policy gates evaluated prior to any automated payment intervention.
        </p>
      </div>

      {savedMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
          {savedMsg}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs space-y-6">
          <h3 className="font-bold text-slate-900 text-base flex items-center border-b border-slate-100 pb-3">
            <ShieldCheck className="w-5 h-5 mr-2 text-emerald-600" />
            Mandatory Guardrail Thresholds
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Rule 1: Max Automated Retries */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-800">
                Max Automated Retries Limit
              </label>
              <input
                type="number"
                min={1}
                max={5}
                value={maxRetries}
                onChange={(e) => setMaxRetries(Number(e.target.value))}
                className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              <p className="text-[11px] text-slate-500">
                Maximum number of automated payment retry attempts per case before escalating to merchant ops.
              </p>
            </div>

            {/* Rule 2: Minimum Probability Floor */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-800">
                Probability Automation Floor (P(Recovery))
              </label>
              <input
                type="number"
                step="0.05"
                min={0.10}
                max={0.90}
                value={probFloor}
                onChange={(e) => setProbFloor(Number(e.target.value))}
                className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              <p className="text-[11px] text-slate-500">
                Cases with predicted probability below this floor (e.g. &lt;0.40) are immediately STOPPED or ESCALATED.
              </p>
            </div>

            {/* Rule 3: High Amount Threshold */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-800">
                High-Value Transaction Auto-Action Threshold (INR)
              </label>
              <input
                type="number"
                step={5000}
                value={maxAmount}
                onChange={(e) => setMaxAmount(Number(e.target.value))}
                className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              <p className="text-[11px] text-slate-500">
                Transactions &ge; this amount (e.g. ₹50,000) automatically require human ops review and approval.
              </p>
            </div>

            {/* Rule 4: Cooldown Period */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-800">
                Retry Cooldown Hours
              </label>
              <input
                type="number"
                min={1}
                max={72}
                value={cooldown}
                onChange={(e) => setCooldown(Number(e.target.value))}
                className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              <p className="text-[11px] text-slate-500">
                Mandatory waiting window between consecutive retries for soft decline categories (e.g. Insufficient Funds).
              </p>
            </div>
          </div>

          {/* Rule 5: Permanent Failure Categories */}
          <div className="pt-4 border-t border-slate-100 space-y-2">
            <label className="block text-xs font-bold text-slate-800">
              Permanent Failure Categories (Immediate Hard Stop)
            </label>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-3 py-1 bg-rose-100 border border-rose-200 text-rose-800 rounded-full font-bold">
                PERMANENT_HARD_DECLINE
              </span>
              <span className="px-3 py-1 bg-rose-100 border border-rose-200 text-rose-800 rounded-full font-bold">
                FRAUD_OR_STOLEN
              </span>
              <span className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full font-medium">
                + Add Custom Reason Category
              </span>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>Save Guardrail Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
}
