"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { History, Search, Filter, RefreshCw, Cpu, ShieldCheck, Zap, ArrowUpRight } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function AuditTrailPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("");
  const [actorFilter, setActorFilter] = useState("");

  const loadAuditEvents = async () => {
    setLoading(true);
    try {
      let url = "/audit?limit=200";
      if (eventTypeFilter) url += `&event_type=${eventTypeFilter}`;
      if (actorFilter) url += `&actor=${actorFilter}`;
      const res = await fetchApi<any[]>(url);
      setEvents(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditEvents();
  }, [eventTypeFilter, actorFilter]);

  const filtered = events.filter(e =>
    (e.action || "").toLowerCase().includes(search.toLowerCase()) ||
    (e.reason || "").toLowerCase().includes(search.toLowerCase()) ||
    (e.case_id || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Immutable Audit Trail</h2>
          <p className="text-sm text-slate-500 mt-1">
            Complete cryptographic audit history of every failure detected, ML prediction, decision evaluation, policy check, and payment retry.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search audit action, reason..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none"
            />
          </div>

          <select
            value={eventTypeFilter}
            onChange={(e) => setEventTypeFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none"
          >
            <option value="">All Event Types</option>
            <option value="FAILURE_DETECTED">Failure Detected</option>
            <option value="MODEL_EVALUATED">Model Evaluated</option>
            <option value="DECISION_MADE">Decision Made</option>
            <option value="POLICY_CHECKED">Policy Checked</option>
            <option value="ACTION_EXECUTED">Action Executed</option>
            <option value="OUTCOME_RECORDED">Outcome Recorded</option>
            <option value="CASE_ESCALATED">Case Escalated</option>
            <option value="CASE_STOPPED">Case Stopped</option>
          </select>

          <select
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none"
          >
            <option value="">All Actors</option>
            <option value="SYSTEM">System</option>
            <option value="ML_MODEL">ML Model</option>
            <option value="DECISION_ENGINE">Decision Engine</option>
            <option value="POLICY_ENGINE">Policy Engine</option>
            <option value="PAYMENT_SERVICE">Payment Service</option>
            <option value="HUMAN_OPERATOR">Human Operator</option>
          </select>

          <button
            onClick={loadAuditEvents}
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
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">Actor</th>
                <th className="px-6 py-4">Event Type</th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4">Reason / Reasoning</th>
                <th className="px-6 py-4">Policy Result</th>
                <th className="px-6 py-4 text-right">Case Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400">Loading audit log stream...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400">No audit events found.</td>
                </tr>
              ) : (
                filtered.map((ev) => {
                  let badgeColor = "bg-slate-100 text-slate-700";
                  if (ev.actor === "ML_MODEL") badgeColor = "bg-blue-100 text-blue-800 border-blue-200";
                  else if (ev.actor === "POLICY_ENGINE") badgeColor = "bg-emerald-100 text-emerald-800 border-emerald-200";
                  else if (ev.actor === "DECISION_ENGINE") badgeColor = "bg-purple-100 text-purple-800 border-purple-200";
                  else if (ev.actor === "HUMAN_OPERATOR") badgeColor = "bg-amber-100 text-amber-800 border-amber-200";

                  return (
                    <tr key={ev.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-4 text-slate-500 font-mono text-[11px]">
                        {new Date(ev.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-1 rounded-full border text-[10px] font-bold ${badgeColor}`}>
                          {ev.actor}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-bold text-slate-900">{ev.event_type}</td>
                      <td className="px-6 py-4 text-slate-800 font-semibold">{ev.action}</td>
                      <td className="px-6 py-4 text-slate-600 max-w-xs truncate">{ev.reason || "-"}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-800">
                          {ev.policy_result || "N/A"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {ev.case_id ? (
                          <Link href={`/cases/${ev.case_id}`} className="text-blue-600 font-semibold inline-flex items-center">
                            Case <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
                          </Link>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
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
