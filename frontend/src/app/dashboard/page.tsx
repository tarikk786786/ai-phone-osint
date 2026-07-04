"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
  Smartphone,
  Wifi,
  Signal,
  Hash,
  Radar,
  Target,
  Crosshair,
  Fingerprint,
  Database,
  Layers,
  Zap,
  BarChart3,
  ShieldAlert,
  UserX,
  Share2,
  ArrowRight,
} from "lucide-react";

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

interface LocationToolResult {
  success: boolean;
  data: Record<string, unknown>;
  sources_used: string[];
  message: string;
}

// ── Tool Tab Configuration ─────────────────────────────

type ToolTab = "phone" | "cell-tower" | "imei" | "ip" | "wifi" | "area-code" | "multi" | "osint";

const toolTabs: { id: ToolTab; label: string; icon: React.ElementType; description: string; color: string }[] = [
  { id: "phone", label: "Phone Lookup", icon: Phone, description: "Full phone intelligence", color: "from-blue-500 to-blue-600" },
  { id: "multi", label: "Multi-Source GPS", icon: Layers, description: "10+ sources aggregated", color: "from-purple-500 to-purple-600" },
  { id: "cell-tower", label: "Cell Tower", icon: Signal, description: "MCC/MNC/LAC/CID", color: "from-green-500 to-green-600" },
  { id: "imei", label: "IMEI Lookup", icon: Fingerprint, description: "Device identification", color: "from-orange-500 to-orange-600" },
  { id: "ip", label: "IP Geolocation", icon: Globe, description: "IP to location", color: "from-cyan-500 to-cyan-600" },
  { id: "wifi", label: "WiFi BSSID", icon: Wifi, description: "WiFi AP geolocation", color: "from-pink-500 to-pink-600" },
  { id: "area-code", label: "Area Code", icon: Hash, description: "Area code mapping", color: "from-teal-500 to-teal-600" },
  { id: "osint", label: "OSINT Scan", icon: Radar, description: "15+ public sources", color: "from-red-500 to-red-600" },
];

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
      <div className="text-sm font-medium text-right max-w-[60%] truncate">
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
        <div className={`h-2 rounded-full transition-all duration-500 ${getColor()}`} style={{ width: `${score}%` }} />
      </div>
      <div className="text-xs font-medium text-right">{getLabel()}</div>
    </div>
  );
}

function ToolResultCard({ title, icon: Icon, children }: { title: string; icon: React.ElementType; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm"
    >
      <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
        <Icon className="w-5 h-5 text-primary" /> {title}
      </h2>
      {children}
    </motion.div>
  );
}

// ── Main Page ──────────────────────────────────────────

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<ToolTab>("phone");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LookupResult | LocationToolResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  // Phone Lookup state
  const [phoneInput, setPhoneInput] = useState("");
  const [country, setCountry] = useState("");
  const [includeAi, setIncludeAi] = useState(true);
  const [includeOsint, setIncludeOsint] = useState(true);
  const [includeGeo, setIncludeGeo] = useState(true);

  // Cell Tower state
  const [mcc, setMcc] = useState("");
  const [mnc, setMnc] = useState("");
  const [lac, setLac] = useState("");
  const [cellId, setCellId] = useState("");

  // IMEI state
  const [imeiInput, setImeiInput] = useState("");

  // IP state
  const [ipInput, setIpInput] = useState("");

  // WiFi state
  const [bssidInput, setBssidInput] = useState("");
  const [signalStrength, setSignalStrength] = useState("-50");

  // Area Code state
  const [areaCodePhone, setAreaCodePhone] = useState("");

  const toggleDark = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  const handleLookup = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let url = "";
      let params = new URLSearchParams();

      switch (activeTab) {
        case "phone":
          if (!phoneInput.trim()) { setLoading(false); return; }
          url = `/api/v1/lookup/lookup`;
          params.set("phone", phoneInput.trim());
          if (country) params.set("country", country);
          if (!includeOsint) params.set("include_osint", "false");
          if (!includeGeo) params.set("include_geolocation", "false");
          if (!includeAi) params.set("include_ai", "false");
          break;

        case "cell-tower":
          if (!mcc || !mnc || !lac || !cellId) { setLoading(false); return; }
          url = `/api/v1/location/cell-tower`;
          params.set("mcc", mcc);
          params.set("mnc", mnc);
          params.set("lac", lac);
          params.set("cell_id", cellId);
          break;

        case "imei":
          if (!imeiInput.trim()) { setLoading(false); return; }
          url = `/api/v1/location/imei`;
          params.set("imei", imeiInput.trim());
          break;

        case "ip":
          if (!ipInput.trim()) { setLoading(false); return; }
          url = `/api/v1/location/ip`;
          params.set("ip", ipInput.trim());
          break;

        case "wifi":
          if (!bssidInput.trim()) { setLoading(false); return; }
          url = `/api/v1/location/wifi`;
          params.set("bssid", bssidInput.trim());
          params.set("signal", signalStrength);
          break;

        case "area-code":
          if (!areaCodePhone.trim()) { setLoading(false); return; }
          url = `/api/v1/location/area-code`;
          params.set("phone", areaCodePhone.trim());
          if (country) params.set("country", country);
          break;

        case "multi":
          if (!phoneInput.trim()) { setLoading(false); return; }
          url = `/api/v1/location/multi-source`;
          params.set("phone", phoneInput.trim());
          if (country) params.set("country", country);
          break;

        case "osint":
          if (!phoneInput.trim()) { setLoading(false); return; }
          url = `/api/v1/lookup/lookup`;
          params.set("phone", phoneInput.trim());
          params.set("include_ai", "false");
          break;
      }

      const res = await fetch(`${url}?${params}`);
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.error || data.message || "Lookup failed");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Network error");
    } finally {
      setLoading(false);
    }
  };

  const getPlaceholder = () => {
    switch (activeTab) {
      case "cell-tower": return "Enter MCC/MNC/LAC/CID below";
      case "imei": return "Enter 15-digit IMEI number (e.g. 353456789012345)";
      case "ip": return "Enter IP address (e.g. 8.8.8.8)";
      case "wifi": return "Enter WiFi BSSID MAC address (e.g. AA:BB:CC:DD:EE:FF)";
      case "area-code": return "Enter phone number to lookup area code";
      default: return "+1 (555) 123-4567";
    }
  };

  const renderInput = () => {
    switch (activeTab) {
      case "cell-tower":
        return (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <input type="text" value={mcc} onChange={e => setMcc(e.target.value)} placeholder="MCC" className="px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm text-center" />
            <input type="text" value={mnc} onChange={e => setMnc(e.target.value)} placeholder="MNC" className="px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm text-center" />
            <input type="text" value={lac} onChange={e => setLac(e.target.value)} placeholder="LAC" className="px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm text-center" />
            <input type="text" value={cellId} onChange={e => setCellId(e.target.value)} placeholder="Cell ID" className="px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm text-center" />
          </div>
        );
      case "wifi":
        return (
          <div className="space-y-3">
            <input type="text" value={bssidInput} onChange={e => setBssidInput(e.target.value)} placeholder="WiFi BSSID (AA:BB:CC:DD:EE:FF)" className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm" />
            <div className="flex gap-3">
              <div className="flex-1">
                <label className="text-xs text-slate-500 mb-1 block">Signal (dBm)</label>
                <input type="text" value={signalStrength} onChange={e => setSignalStrength(e.target.value)} placeholder="-50" className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm text-center" />
              </div>
            </div>
          </div>
        );
      case "imei":
        return <input type="text" value={imeiInput} onChange={e => setImeiInput(e.target.value)} placeholder={getPlaceholder()} className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm" />;
      case "ip":
        return <input type="text" value={ipInput} onChange={e => setIpInput(e.target.value)} placeholder={getPlaceholder()} className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm" />;
      case "area-code":
        return <input type="text" value={areaCodePhone} onChange={e => setAreaCodePhone(e.target.value)} placeholder={getPlaceholder()} className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm" onKeyDown={e => e.key === "Enter" && handleLookup()} />;
      default:
        return (
          <div className="flex-1 relative">
            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input type="text" value={phoneInput} onChange={e => setPhoneInput(e.target.value)} placeholder={getPlaceholder()} className="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all text-sm" onKeyDown={e => e.key === "Enter" && handleLookup()} />
          </div>
        );
    }
  };

  const renderPhoneInput = () => {
    if (["phone", "multi", "osint"].includes(activeTab)) {
      return (
        <>
          {renderInput()}
          <input type="text" value={country} onChange={e => setCountry(e.target.value.toUpperCase())} placeholder="CC" maxLength={2} className="w-full sm:w-20 px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-sm text-center uppercase" />
        </>
      );
    }
    return renderInput();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-blue-950 dark:to-indigo-950">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 dark:bg-slate-950/70 border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2">
            <Phone className="w-5 h-5 text-primary" />
            <span className="font-bold">PhoneOSINT</span>
          </a>
          <div className="flex items-center gap-3">
            <button onClick={toggleDark} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            <a href="/" className="text-sm text-slate-500 hover:text-primary transition-colors">Home</a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Tool Tabs */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <div className="flex overflow-x-auto gap-2 pb-2 scrollbar-hide">
            {toolTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setResult(null); setError(null); }}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all ${
                  activeTab === tab.id
                    ? `bg-gradient-to-r ${tab.color} text-white shadow-lg`
                    : "bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-primary/30"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Search Section */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
            <h1 className="text-2xl font-bold mb-1">
              {toolTabs.find(t => t.id === activeTab)?.label}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
              {toolTabs.find(t => t.id === activeTab)?.description}
            </p>

            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-3">
                {renderPhoneInput()}
                <button
                  onClick={handleLookup}
                  disabled={loading}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-primary/20"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  {loading ? "Analyzing..." : "Lookup"}
                </button>
              </div>

              {/* Advanced Options for Phone Lookup */}
              {activeTab === "phone" && (
                <div>
                  <button onClick={() => setAdvancedOpen(!advancedOpen)} className="flex items-center gap-1 text-xs text-slate-500 hover:text-primary transition-colors">
                    <ChevronDown className={`w-3 h-3 transition-transform ${advancedOpen ? "rotate-180" : ""}`} />
                    Advanced Options
                  </button>
                  {advancedOpen && (
                    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="flex flex-wrap gap-4 mt-3">
                      <label className="flex items-center gap-2 text-sm">
                        <input type="checkbox" checked={includeOsint} onChange={e => setIncludeOsint(e.target.checked)} className="rounded border-slate-300 text-primary focus:ring-primary" />
                        OSINT Gathering
                      </label>
                      <label className="flex items-center gap-2 text-sm">
                        <input type="checkbox" checked={includeGeo} onChange={e => setIncludeGeo(e.target.checked)} className="rounded border-slate-300 text-primary focus:ring-primary" />
                        Geolocation
                      </label>
                      <label className="flex items-center gap-2 text-sm">
                        <input type="checkbox" checked={includeAi} onChange={e => setIncludeAi(e.target.checked)} className="rounded border-slate-300 text-primary focus:ring-primary" />
                        AI Report
                      </label>
                    </motion.div>
                  )}
                </div>
              )}
            </div>

            {error && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {error}
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Results */}
        <AnimatePresence mode="wait">
          {result && (
            <motion.div key={activeTab} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
              {/* Phone Lookup Results */}
              {activeTab === "phone" && "data" in result && (
                <>
                  <ToolResultCard title="Validation Results" icon={Phone}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
                      <DataRow label="Status" value={(result.data as PhoneData).is_valid ? "Valid" : "Invalid"} icon={(result.data as PhoneData).is_valid ? CheckCircle2 : XCircle} />
                      <DataRow label="E.164 Format" value={(result.data as PhoneData).e164 as string} icon={Globe} />
                      <DataRow label="Country" value={`${(result.data as PhoneData).country_name} (${(result.data as PhoneData).country_iso})`} icon={Globe} />
                      <DataRow label="Location (Area)" value={(result.data as PhoneData).location as string} icon={MapPin} />
                      <DataRow label="Carrier" value={(result.data as PhoneData).carrier as string} />
                      <DataRow label="Line Type" value={(result.data as PhoneData).line_type as string} />
                      <DataRow label="International" value={(result.data as PhoneData).formatted_international as string} />
                      <DataRow label="National" value={(result.data as PhoneData).formatted_national as string} />
                      <DataRow label="Timezones" value={((result.data as PhoneData).timezones as string[])?.join(", ") || null} icon={Clock} />
                      <DataRow label="Country Code" value={(result.data as PhoneData).country_code ? `+${(result.data as PhoneData).country_code}` : null} />
                    </div>
                  </ToolResultCard>

                  {(result.data.spam_score !== null || result.osint) && (
                    <ToolResultCard title="Risk Assessment" icon={Shield}>
                      <RiskMeter score={result.data.spam_score as number} />
                    </ToolResultCard>
                  )}

                  {(result as LookupResult).geolocation && (
                    <ToolResultCard title="Estimated Location" icon={MapPin}>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Latitude</span><span className="font-mono">{(result as LookupResult).geolocation?.latitude}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Longitude</span><span className="font-mono">{(result as LookupResult).geolocation?.longitude}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Confidence</span><span className="capitalize font-medium">{(result as LookupResult).geolocation?.confidence as string}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Source</span><span>{(result as LookupResult).geolocation?.source as string}</span></div>
                          {(result as LookupResult).geolocation?.address && (
                            <div className="mt-2 p-2 bg-slate-50 dark:bg-slate-800 rounded text-xs text-slate-600 dark:text-slate-400">{(result as LookupResult).geolocation?.address as string}</div>
                          )}
                          <div className="p-2 bg-amber-50 dark:bg-amber-950/20 rounded text-xs text-amber-600 dark:text-amber-400">
                            ⚠️ Location is estimated from area code / carrier region, not GPS tracking.
                          </div>
                        </div>
                        <div className="min-h-[200px]">
                          <PhoneMap latitude={(result as LookupResult).geolocation?.latitude as number} longitude={(result as LookupResult).geolocation?.longitude as number} confidence={(result as LookupResult).geolocation?.confidence as string} source={(result as LookupResult).geolocation?.source as string} address={(result as LookupResult).geolocation?.address as string} />
                        </div>
                      </div>
                    </ToolResultCard>
                  )}

                  {(result as LookupResult).osint && (
                    <ToolResultCard title="OSINT Findings" icon={Globe}>
                      <div className="space-y-3">
                        {((result as LookupResult).osint?.social_media as Array<{platform: string; found: boolean; url: string}>)?.map((sm, i) => (
                          <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                            <span className="text-sm capitalize">{sm.platform}</span>
                            <span className={`text-xs ${sm.found ? "text-green-600" : "text-slate-400"}`}>{sm.found ? "Presence detected" : "No public profile"}</span>
                          </div>
                        ))}
                      </div>
                    </ToolResultCard>
                  )}

                  {(result as LookupResult).ai_report && (
                    <ToolResultCard title="AI Investigation Report" icon={Brain}>
                      <div className="flex items-center gap-3 mb-4 text-xs text-slate-500">
                        <span>Model: {(result as LookupResult).ai_report?.model_used as string}</span>
                        <span>•</span>
                        <span>Confidence: {((result as LookupResult).ai_report?.confidence_level as string)?.toUpperCase()}</span>
                      </div>
                      {(result as LookupResult).ai_report?.summary && (
                        <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800 mb-4">
                          <h3 className="text-sm font-semibold mb-1">Executive Summary</h3>
                          <p className="text-sm text-slate-600 dark:text-slate-400">{(result as LookupResult).ai_report?.summary as string}</p>
                        </div>
                      )}
                      {(result as LookupResult).ai_report?.recommendations && ((result as LookupResult).ai_report?.recommendations as string[]).length > 0 && (
                        <div>
                          <h3 className="text-sm font-semibold mb-2">Recommendations</h3>
                          <ul className="space-y-1">
                            {((result as LookupResult).ai_report?.recommendations as string[]).map((rec, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400"><span className="text-primary mt-0.5">•</span>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {(result as LookupResult).ai_report?.disclaimer && (
                        <div className="mt-4 p-3 rounded-lg bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 text-xs text-amber-600 dark:text-amber-400">{(result as LookupResult).ai_report?.disclaimer as string}</div>
                      )}
                    </ToolResultCard>
                  )}
                </>
              )}

              {/* Location Tool Results (Cell Tower, IMEI, IP, WiFi, Area Code, Multi) */}
              {["cell-tower", "imei", "ip", "wifi", "area-code", "multi"].includes(activeTab) && "data" in result && (
                <>
                  <ToolResultCard title={`${toolTabs.find(t => t.id === activeTab)?.label} Result`} icon={toolTabs.find(t => t.id === activeTab)?.icon || Target}>
                    {activeTab === "multi" && (result as LocationToolResult).sources_used?.length > 0 && (
                      <div className="mb-4 p-3 bg-purple-50 dark:bg-purple-950/20 rounded-lg border border-purple-200 dark:border-purple-800">
                        <div className="flex items-center gap-2 text-sm font-medium text-purple-700 dark:text-purple-400 mb-2">
                          <Layers className="w-4 h-4" /> {result.data.all_sources ? (result.data.all_sources as Array<{source: string}>).length : 0} Sources Aggregated
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {(result.data.all_sources as Array<{source: string}>)?.map((s, i) => (
                            <span key={i} className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded text-xs">{s.source}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
                      {activeTab === "imei" && (
                        <>
                          <DataRow label="Valid" value={result.data.is_valid ? "Yes ✓" : "No ✗"} icon={CheckCircle2} />
                          <DataRow label="TAC" value={result.data.tac as string} icon={Fingerprint} />
                          <DataRow label="Brand" value={result.data.brand as string} icon={Smartphone} />
                          <DataRow label="Manufacturer" value={result.data.manufacturer as string} />
                          <DataRow label="Model" value={result.data.model as string} />
                          <DataRow label="Device Name" value={result.data.device_name as string} />
                          <DataRow label="Device Type" value={result.data.device_type as string} />
                          <DataRow label="OS" value={result.data.os as string} />
                          <DataRow label="Release Date" value={result.data.release_date as string} icon={Clock} />
                          <DataRow label="Stolen" value={result.data.is_stolen === true ? "Yes ⚠️" : result.data.is_stolen === false ? "No" : null} icon={ShieldAlert} />
                          <DataRow label="Blacklisted" value={result.data.blacklisted === true ? "Yes ⚠️" : result.data.blacklisted === false ? "No" : null} icon={Shield} />
                          <DataRow label="Source" value={result.data.source as string} icon={Database} />
                        </>
                      )}

                      {activeTab === "ip" && (
                        <>
                          <DataRow label="IP" value={result.data.ip as string} icon={Globe} />
                          <DataRow label="Country" value={result.data.country as string} icon={Globe} />
                          <DataRow label="Region" value={result.data.region as string} />
                          <DataRow label="City" value={result.data.city as string} icon={MapPin} />
                          <DataRow label="Latitude" value={result.data.latitude as unknown as string} icon={Crosshair} />
                          <DataRow label="Longitude" value={result.data.longitude as unknown as string} />
                          <DataRow label="Postal Code" value={result.data.postal_code as string} />
                          <DataRow label="Timezone" value={result.data.timezone as string} icon={Clock} />
                          <DataRow label="ISP" value={result.data.isp as string} />
                          <DataRow label="Org" value={result.data.org as string} />
                          <DataRow label="AS Number" value={result.data.as_number as string} />
                          <DataRow label="Proxy/VPN" value={result.data.proxy ? "Yes ⚠️" : "No"} icon={ShieldAlert} />
                          <DataRow label="Hosting" value={result.data.hosting ? "Yes" : "No"} />
                          <DataRow label="Source" value={result.data.source as string} icon={Database} />
                        </>
                      )}

                      {(activeTab === "cell-tower" || activeTab === "wifi" || activeTab === "area-code" || activeTab === "multi") && (
                        <>
                          <DataRow label="Latitude" value={result.data.latitude as unknown as string} icon={MapPin} />
                          <DataRow label="Longitude" value={result.data.longitude as unknown as string} icon={Crosshair} />
                          <DataRow label="Address" value={result.data.address as string} />
                          <DataRow label="City" value={result.data.city as string} />
                          <DataRow label="State" value={result.data.state as string} />
                          <DataRow label="Country" value={result.data.country as string} icon={Globe} />
                          <DataRow label="Postal Code" value={result.data.postal_code as string} />
                          <DataRow label="Source" value={result.data.source as string} icon={Database} />
                          <DataRow label="Confidence" value={result.data.confidence as string} icon={Shield} />
                          <DataRow label="Accuracy" value={result.data.accuracy_km ? `~${result.data.accuracy_km} km` : null} icon={Target} />
                        </>
                      )}
                    </div>

                    {/* Map for location results */}
                    {result.data.latitude && result.data.longitude && (
                      <div className="mt-4">
                        <PhoneMap latitude={result.data.latitude as number} longitude={result.data.longitude as number} confidence={result.data.confidence as string} source={result.data.source as string} address={result.data.address as string} />
                      </div>
                    )}
                  </ToolResultCard>

                  {activeTab === "multi" && result.data.all_sources && (
                    <ToolResultCard title="All Sources Detail" icon={Database}>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-200 dark:border-slate-700">
                              <th className="text-left py-2 px-3 text-slate-500 font-medium">Source</th>
                              <th className="text-left py-2 px-3 text-slate-500 font-medium">Latitude</th>
                              <th className="text-left py-2 px-3 text-slate-500 font-medium">Longitude</th>
                              <th className="text-left py-2 px-3 text-slate-500 font-medium">Accuracy</th>
                            </tr>
                          </thead>
                          <tbody>
                            {(result.data.all_sources as Array<{source: string; latitude: number; longitude: number; accuracy_km: number}>)?.map((s, i) => (
                              <tr key={i} className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                                <td className="py-2 px-3 font-medium">{s.source}</td>
                                <td className="py-2 px-3 font-mono text-xs">{s.latitude?.toFixed(4)}</td>
                                <td className="py-2 px-3 font-mono text-xs">{s.longitude?.toFixed(4)}</td>
                                <td className="py-2 px-3">{s.accuracy_km ? `~${s.accuracy_km} km` : "N/A"}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </ToolResultCard>
                  )}
                </>
              )}

              {/* OSINT Results */}
              {activeTab === "osint" && "data" in result && "osint" in result && (
                <>
                  <ToolResultCard title="Phone Validation" icon={Phone}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
                      <DataRow label="Valid" value={(result.data as PhoneData).is_valid ? "Yes" : "No"} icon={CheckCircle2} />
                      <DataRow label="E.164" value={(result.data as PhoneData).e164 as string} />
                      <DataRow label="Country" value={`${(result.data as PhoneData).country_name} (${(result.data as PhoneData).country_iso})`} icon={Globe} />
                      <DataRow label="Carrier" value={(result.data as PhoneData).carrier as string} />
                      <DataRow label="Line Type" value={(result.data as PhoneData).line_type as string} />
                      <DataRow label="Location" value={(result.data as PhoneData).location as string} icon={MapPin} />
                    </div>
                  </ToolResultCard>

                  {(result as LookupResult).osint && (
                    <>
                      <ToolResultCard title="Spam & Risk Analysis" icon={ShieldAlert}>
                        <RiskMeter score={(result as LookupResult).osint?.spam_score as number} />
                        {(result as LookupResult).osint?.spam_sources && ((result as LookupResult).osint?.spam_sources as string[]).length > 0 && (
                          <div className="mt-3">
                            <span className="text-xs text-slate-500">Detected in:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {((result as LookupResult).osint?.spam_sources as string[]).map((s) => (
                                <span key={s} className="px-2 py-0.5 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 rounded text-xs">{s}</span>
                              ))}
                            </div>
                          </div>
                        )}
                        {(result as LookupResult).osint?.spam_details && ((result as LookupResult).osint?.spam_details as Array<{source: string; keywords_found: string[]}>)?.length > 0 && (
                          <div className="mt-4 space-y-2">
                            <h3 className="text-sm font-semibold">Spam Details</h3>
                            {((result as LookupResult).osint?.spam_details as Array<{source: string; keywords_found: string[]}>)?.map((d, i) => (
                              <div key={i} className="p-2 bg-slate-50 dark:bg-slate-800 rounded text-xs">
                                <span className="font-medium">{d.source}:</span> {d.keywords_found?.join(", ")}
                              </div>
                            ))}
                          </div>
                        )}
                      </ToolResultCard>

                      <ToolResultCard title="Social Media Presence" icon={Share2}>
                        <div className="space-y-2">
                          {((result as LookupResult).osint?.social_media as Array<{platform: string; found: boolean; url: string}>)?.map((sm, i) => (
                            <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                              <span className="text-sm capitalize">{sm.platform}</span>
                              <div className="flex items-center gap-2">
                                <span className={`text-xs ${sm.found ? "text-green-600" : "text-slate-400"}`}>{sm.found ? "✓ Found" : "Not found"}</span>
                                {sm.url && <a href={sm.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline"><ExternalLink className="w-3 h-3" /></a>}
                              </div>
                            </div>
                          ))}
                        </div>
                      </ToolResultCard>
                    </>
                  )}
                </>
              )}

              {/* Export */}
              <div className="flex flex-wrap gap-3">
                <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                  <Download className="w-4 h-4" /> Export JSON
                </button>
                <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                  <FileText className="w-4 h-4" /> Export PDF
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Available Tools Info */}
        {!result && !loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="mt-8">
            <h2 className="text-lg font-semibold mb-4">Available Location Finder Tools</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {toolTabs.map((tab) => (
                <div
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className="group p-4 bg-white dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:border-primary/30 transition-all duration-300 cursor-pointer"
                >
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${tab.color} flex items-center justify-center mb-3 text-white`}>
                    <tab.icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-semibold text-sm mb-1">{tab.label}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{tab.description}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
