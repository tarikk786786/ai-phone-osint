"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import {
  Search,
  Phone,
  Globe,
  Shield,
  MapPin,
  Clock,
  Download,
  ChevronDown,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  Brain,
  FileText,
  ExternalLink,
  Sun,
  Moon,
} from "lucide-react";

// Dynamic import for Leaflet map (SSR disabled)
const PhoneMap = dynamic(() => import("@/components/maps/PhoneMap"), {
  ssr: false,
  loading: () => (
    <div className="h-64 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse flex items-center justify-center text-sm text-slate-400">
      Loading map...
    </div>
  ),
});

// ── Types ──────────────────────────────────────────────

interface PhoneData {
  is_valid: boolean;
  is_possible: boolean;
  country_code: number | null;
  country_iso: string | null;
  country_name: string | null;
  location: string | null;
  carrier: string | null;
  line_type: string | null;
  timezones: string[];
  formatted_international: string | null;
  formatted_national: string | null;
  e164: string | null;
  [key: string]: unknown;
}

interface LookupResult {
  success: boolean;
  data: Record<string, unknown>;
  osint?: Record<string, unknown>;
  geolocation?: Record<string, unknown>;
  ai_report?: Record<string, unknown>;
  lookup_id?: string;
  message?: string;
}

// ── Helper Components ──────────────────────────────────

function StatusBadge({ valid }: { valid: boolean }) {
  if (valid) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
        <CheckCircle2 className="w-3 h-3" /> Valid
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
      <XCircle className="w-3 h-3" /> Invalid
    </span>
  );
}

function DataRow({ label, value, icon: Icon }: { label: string; value: string | null | undefined; icon?: React.ElementType }) {
  return (
    <div className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
      <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
        {Icon && <Icon className="w-4 h-4" />}
        {label}
      </div>
      <div className="text-sm font-medium text-right">
        {value || <span className="text-slate-300 dark:text-slate-600">N/A</span>}
      </div>
    </div>
  );
}

function RiskMeter({ score }: { score: number | null | undefined }) {
  if (score === null || score === undefined) return null;

  const getColor = () => {
    if (score >= 70) return "bg-red-500";
    if (score >= 40) return "bg-yellow-500";
    return "bg-green-500";
  };

  const getLabel = () => {
    if (score >= 70) return "High Risk";
    if (score >= 40) return "Medium Risk";
    return "Low Risk";
  };

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-500">Risk Score</span>
        <span className="font-medium">{score}/100</span>
      </div>
      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${getColor()}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <div className="text-xs font-medium text-right">{getLabel()}</div>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────

export default function DashboardPage() {
  const [phoneInput, setPhoneInput] = useState("");
  const [country, setCountry] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LookupResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [includeAi, setIncludeAi] = useState(true);
  const [includeOsint, setIncludeOsint] = useState(true);
  const [includeGeo, setIncludeGeo] = useState(true);

  const toggleDark = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleLookup = async () => {
    if (!phoneInput.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params = new URLSearchParams({ phone: phoneInput.trim() });
      if (country) params.set("country", country);
      if (!includeOsint) params.set("include_osint", "false");
      if (!includeGeo) params.set("include_geolocation", "false");
      if (!includeAi) params.set("include_ai", "false");

      const res = await fetch(`/api/v1/lookup/lookup?${params}`);
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.error || "Lookup failed");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-blue-950 dark:to-indigo-950">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 dark:bg-slate-950/70 border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2">
            <Phone className="w-5 h-5 text-primary" />
            <span className="font-bold">PhoneOSINT</span>
          </a>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleDark}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <a
              href="/"
              className="text-sm text-slate-500 hover:text-primary transition-colors"
            >
              Home
            </a>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Search Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
            <h1 className="text-2xl font-bold mb-1">Phone Intelligence Lookup</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
              Enter a phone number to validate, detect carrier, estimate location, and gather OSINT data.
            </p>

            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="flex-1 relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={phoneInput}
                    onChange={(e) => setPhoneInput(e.target.value)}
                    placeholder="+1 (555) 123-4567"
                    className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm"
                    onKeyDown={(e) => e.key === "Enter" && handleLookup()}
                  />
                </div>
                <input
                  type="text"
                  value={country}
                  onChange={(e) => setCountry(e.target.value.toUpperCase())}
                  placeholder="Country (e.g. US)"
                  maxLength={2}
                  className="w-full sm:w-28 px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm text-center uppercase"
                />
                <button
                  onClick={handleLookup}
                  disabled={loading || !phoneInput.trim()}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-primary/20"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Search className="w-5 h-5" />
                  )}
                  {loading ? "Analyzing..." : "Lookup"}
                </button>
              </div>

              {/* Advanced Options */}
              <div>
                <button
                  onClick={() => setAdvancedOpen(!advancedOpen)}
                  className="flex items-center gap-1 text-xs text-slate-500 hover:text-primary transition-colors"
                >
                  <ChevronDown className={`w-3 h-3 transition-transform ${advancedOpen ? "rotate-180" : ""}`} />
                  Advanced Options
                </button>
                {advancedOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="flex flex-wrap gap-4 mt-3"
                  >
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={includeOsint}
                        onChange={(e) => setIncludeOsint(e.target.checked)}
                        className="rounded border-slate-300 text-primary focus:ring-primary"
                      />
                      OSINT Gathering
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={includeGeo}
                        onChange={(e) => setIncludeGeo(e.target.checked)}
                        className="rounded border-slate-300 text-primary focus:ring-primary"
                      />
                      Geolocation
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={includeAi}
                        onChange={(e) => setIncludeAi(e.target.checked)}
                        className="rounded border-slate-300 text-primary focus:ring-primary"
                      />
                      AI Report
                    </label>
                  </motion.div>
                )}
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-400 flex items-center gap-2"
              >
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {error}
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Results */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Validation Summary */}
            <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Phone className="w-5 h-5 text-primary" /> Validation Results
                </h2>
                {result.lookup_id && (
                  <span className="text-xs text-slate-400">ID: {result.lookup_id.slice(0, 8)}...</span>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
                <DataRow
                  label="Status"
                  value={result.data.is_valid ? "Valid" : "Invalid"}
                  icon={result.data.is_valid ? CheckCircle2 : XCircle}
                />
                <DataRow label="E.164 Format" value={result.data.e164 as string} icon={Globe} />
                <DataRow label="Country" value={`${result.data.country_name} (${result.data.country_iso})`} icon={Globe} />
                <DataRow label="Location (Area)" value={result.data.location as string} icon={MapPin} />
                <DataRow label="Carrier" value={result.data.carrier as string} />
                <DataRow label="Line Type" value={result.data.line_type as string} />
                <DataRow label="International" value={result.data.formatted_international as string} />
                <DataRow label="National" value={result.data.formatted_national as string} />
                <DataRow label="Timezones" value={(result.data.timezones as string[])?.join(", ") || null} icon={Clock} />
                <DataRow label="Country Code" value={result.data.country_code ? `+${result.data.country_code}` : null} />
              </div>
            </div>

            {/* Risk & Geolocation Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Risk Assessment */}
              {(result.data.spam_score !== null || result.osint) && (
                <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
                  <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-primary" /> Risk Assessment
                  </h2>
                  <RiskMeter score={result.data.spam_score as number} />
                  {result.osint?.spam_sources && (result.osint.spam_sources as string[]).length > 0 && (
                    <div className="mt-3">
                      <span className="text-xs text-slate-500">Sources:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {(result.osint.spam_sources as string[]).map((s) => (
                          <span key={s} className="px-2 py-0.5 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 rounded text-xs">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Geolocation */}
              {result.geolocation && (
                <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
                  <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                    <MapPin className="w-5 h-5 text-primary" /> Estimated Location
                  </h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">Latitude</span>
                        <span className="font-mono">{result.geolocation.latitude}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">Longitude</span>
                        <span className="font-mono">{result.geolocation.longitude}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">Confidence</span>
                        <span className="capitalize font-medium">{result.geolocation.confidence as string}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">Source</span>
                        <span>{result.geolocation.source as string}</span>
                      </div>
                      {result.geolocation.address && (
                        <div className="mt-2 p-2 bg-slate-50 dark:bg-slate-800 rounded text-xs text-slate-600 dark:text-slate-400">
                          {result.geolocation.address as string}
                        </div>
                      )}
                      <div className="p-2 bg-amber-50 dark:bg-amber-950/20 rounded text-xs text-amber-600 dark:text-amber-400">
                        ⚠️ Location is estimated from area code / carrier region, not GPS tracking.
                      </div>
                    </div>
                    <div className="min-h-[200px]">
                      <PhoneMap
                        latitude={result.geolocation.latitude as number}
                        longitude={result.geolocation.longitude as number}
                        confidence={result.geolocation.confidence as string}
                        source={result.geolocation.source as string}
                        address={result.geolocation.address as string}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* OSINT Findings */}
            {result.osint && (
              <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
                <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                  <Globe className="w-5 h-5 text-primary" /> OSINT Findings
                </h2>
                <div className="space-y-3">
                  {result.osint.social_media && (result.osint.social_media as Array<{platform: string; found: boolean; url: string}>).map((sm, i) => (
                    <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                      <span className="text-sm capitalize">{sm.platform}</span>
                      <span className={`text-xs ${sm.found ? "text-green-600" : "text-slate-400"}`}>
                        {sm.found ? "Presence detected" : "No public profile"}
                      </span>
                    </div>
                  ))}
                  {(!result.osint.social_media || (result.osint.social_media as unknown[]).length === 0) && (
                    <p className="text-sm text-slate-400">No public social media associations found.</p>
                  )}
                </div>
              </div>
            )}

            {/* AI Report */}
            {result.ai_report && (
              <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
                <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
                  <Brain className="w-5 h-5 text-primary" /> AI Investigation Report
                </h2>

                <div className="flex items-center gap-3 mb-4 text-xs text-slate-500">
                  <span>Model: {result.ai_report.model_used as string}</span>
                  <span>•</span>
                  <span>Confidence: {(result.ai_report.confidence_level as string)?.toUpperCase()}</span>
                </div>

                {/* Summary */}
                {result.ai_report.summary && (
                  <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800 mb-4">
                    <h3 className="text-sm font-semibold mb-1">Executive Summary</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{result.ai_report.summary as string}</p>
                  </div>
                )}

                {/* Risk Assessment */}
                {result.ai_report.risk_assessment && (
                  <div className="mb-4">
                    <h3 className="text-sm font-semibold mb-2">Risk Assessment</h3>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                        <div className="text-xs text-slate-500">Score</div>
                        <div className="text-lg font-bold">{(result.ai_report.risk_assessment as Record<string, unknown>).score as string || "N/A"}</div>
                      </div>
                      <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                        <div className="text-xs text-slate-500">Level</div>
                        <div className="text-lg font-bold capitalize">{(result.ai_report.risk_assessment as Record<string, unknown>).level as string || "N/A"}</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {result.ai_report.recommendations && (result.ai_report.recommendations as string[]).length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold mb-2">Recommendations</h3>
                    <ul className="space-y-1">
                      {(result.ai_report.recommendations as string[]).map((rec, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                          <span className="text-primary mt-0.5">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Disclaimer */}
                {result.ai_report.disclaimer && (
                  <div className="mt-4 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 text-xs text-amber-600 dark:text-amber-400">
                    {result.ai_report.disclaimer as string}
                  </div>
                )}
              </div>
            )}

            {/* Export */}
            <div className="flex flex-wrap gap-3">
              <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                <Download className="w-4 h-4" /> Export JSON
              </button>
              <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                <FileText className="w-4 h-4" /> Export PDF
              </button>
              <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                <ExternalLink className="w-4 h-4" /> View API Response
              </button>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
