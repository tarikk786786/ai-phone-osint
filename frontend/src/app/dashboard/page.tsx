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
  ShieldAlert,
  Share2,
  Sparkles,
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

interface UniversalSearchResult {
  success: boolean;
  input_type: string;
  detected_value: string;
  results: Record<string, unknown>;
  sources_used: string[];
  tools_run: string[];
  message: string;
}

// ── Tool Tab Configuration ─────────────────────────────

type ToolTab = "universal" | "phone" | "cell-tower" | "imei" | "ip" | "wifi" | "area-code" | "multi" | "osint";

const toolTabs: { id: ToolTab; label: string; icon: React.ElementType; description: string; color: string }[] = [
  { id: "universal", label: "Universal Search", icon: Sparkles, description: "Auto-detect & run ALL tools", color: "from-violet-500 to-purple-600" },
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

// ── Universal Search Result Renderer ───────────────────

function UniversalSearchResults({ result }: { result: UniversalSearchResult }) {
  const r = result.results;
  const inputType = result.input_type;

  return (
    <div className="space-y-6">
      {/* Input Type Badge */}
      <ToolResultCard title="Input Detected" icon={Sparkles}>
        <div className="flex items-center gap-3 mb-4">
          <span className="px-3 py-1 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-full text-sm font-medium capitalize">
            {inputType.replace('_', ' ')}
          </span>
          <span className="text-sm text-slate-500">{result.detected_value}</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <div className="text-xs text-slate-500 mb-1">Tools Executed</div>
            <div className="text-lg font-bold">{result.tools_run.length}</div>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <div className="text-xs text-slate-500 mb-1">Sources Used</div>
            <div className="text-lg font-bold">{result.sources_used.length}</div>
          </div>
        </div>
      </ToolResultCard>

      {/* Summary */}
      {r.summary && (
        <ToolResultCard title="Summary" icon={Database}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.summary as Record<string, unknown>).map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
        </ToolResultCard>
      )}

      {/* Phone Validation */}
      {r.phone_validation && (
        <ToolResultCard title="Phone Validation" icon={Phone}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.phone_validation as Record<string, unknown>).filter(([k]) => typeof (r.phone_validation as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
        </ToolResultCard>
      )}

      {/* Geolocation */}
      {r.geolocation && (
        <ToolResultCard title="Multi-Source Geolocation" icon={MapPin}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.geolocation as Record<string, unknown>).filter(([k]) => !['all_sources'].includes(k) && typeof (r.geolocation as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
          {(r.geolocation as Record<string, unknown>).latitude && (r.geolocation as Record<string, unknown>).longitude && (
            <div className="mt-4">
              <PhoneMap
                latitude={(r.geolocation as Record<string, unknown>).latitude as number}
                longitude={(r.geolocation as Record<string, unknown>).longitude as number}
                confidence={(r.geolocation as Record<string, unknown>).confidence as string}
                source={(r.geolocation as Record<string, unknown>).source as string}
              />
            </div>
          )}
        </ToolResultCard>
      )}

      {/* IMEI Lookup */}
      {r.imei_lookup && (
        <ToolResultCard title="IMEI Device Lookup" icon={Fingerprint}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.imei_lookup as Record<string, unknown>).filter(([k]) => !['raw_data'].includes(k) && typeof (r.imei_lookup as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
        </ToolResultCard>
      )}

      {/* IP Geolocation */}
      {r.ip_geolocation && (
        <ToolResultCard title="IP Geolocation" icon={Globe}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.ip_geolocation as Record<string, unknown>).filter(([k]) => !['raw_data'].includes(k) && typeof (r.ip_geolocation as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
          {(r.ip_geolocation as Record<string, unknown>).latitude && (r.ip_geolocation as Record<string, unknown>).longitude && (
            <div className="mt-4">
              <PhoneMap
                latitude={(r.ip_geolocation as Record<string, unknown>).latitude as number}
                longitude={(r.ip_geolocation as Record<string, unknown>).longitude as number}
                confidence="estimated"
                source={(r.ip_geolocation as Record<string, unknown>).source as string}
              />
            </div>
          )}
        </ToolResultCard>
      )}

      {/* WiFi Geolocation */}
      {r.wifi_geolocation && (
        <ToolResultCard title="WiFi BSSID Geolocation" icon={Wifi}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.wifi_geolocation as Record<string, unknown>).filter(([k]) => !['access_points', 'cell_towers'].includes(k) && typeof (r.wifi_geolocation as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
          {(r.wifi_geolocation as Record<string, unknown>).latitude && (r.wifi_geolocation as Record<string, unknown>).longitude && (
            <div className="mt-4">
              <PhoneMap
                latitude={(r.wifi_geolocation as Record<string, unknown>).latitude as number}
                longitude={(r.wifi_geolocation as Record<string, unknown>).longitude as number}
                confidence={(r.wifi_geolocation as Record<string, unknown>).confidence as string}
                source={(r.wifi_geolocation as Record<string, unknown>).source as string}
              />
            </div>
          )}
        </ToolResultCard>
      )}

      {/* Domain Resolution */}
      {r.domain_resolution && (
        <ToolResultCard title="Domain Resolution" icon={Globe}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.domain_resolution as Record<string, unknown>).filter(([k]) => !['raw_data'].includes(k) && typeof (r.domain_resolution as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
        </ToolResultCard>
      )}

      {/* OSINT Scan */}
      {r.osint_scan && (
        <ToolResultCard title="OSINT Intelligence Scan" icon={Radar}>
          <div className="space-y-3">
            {(r.osint_scan as Record<string, unknown>).social_media && ((r.osint_scan as Record<string, unknown>).social_media as Array<{platform: string; found: boolean; url: string}>)?.map((sm, i) => (
              <div key={i} className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                <span className="text-sm capitalize">{sm.platform}</span>
                <span className={`text-xs ${sm.found ? "text-green-600" : "text-slate-400"}`}>{sm.found ? "✓ Found" : "Not found"}</span>
              </div>
            ))}
          </div>
        </ToolResultCard>
      )}

      {/* Reverse Geocode */}
      {r.reverse_geocode && (
        <ToolResultCard title="Address Lookup" icon={MapPin}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.reverse_geocode as Record<string, unknown>).filter(([k]) => !['all_sources'].includes(k) && typeof (r.reverse_geocode as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
          {(r.reverse_geocode as Record<string, unknown>).latitude && (r.reverse_geocode as Record<string, unknown>).longitude && (
            <div className="mt-4">
              <PhoneMap
                latitude={(r.reverse_geocode as Record<string, unknown>).latitude as number}
                longitude={(r.reverse_geocode as Record<string, unknown>).longitude as number}
                confidence={(r.reverse_geocode as Record<string, unknown>).confidence as string}
                source={(r.reverse_geocode as Record<string, unknown>).source as string}
                address={(r.reverse_geocode as Record<string, unknown>).address as string}
              />
            </div>
          )}
        </ToolResultCard>
      )}

      {/* Area Code */}
      {r.area_code && (
        <ToolResultCard title="Area Code Location" icon={Hash}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
            {Object.entries(r.area_code as Record<string, unknown>).filter(([k]) => !['all_sources'].includes(k) && typeof (r.area_code as Record<string, unknown>)[k] !== 'object').map(([key, value]) => (
              <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
            ))}
          </div>
          {(r.area_code as Record<string, unknown>).latitude && (r.area_code as Record<string, unknown>).longitude && (
            <div className="mt-4">
              <PhoneMap
                latitude={(r.area_code as Record<string, unknown>).latitude as number}
                longitude={(r.area_code as Record<string, unknown>).longitude as number}
                confidence={(r.area_code as Record<string, unknown>).confidence as string}
                source={(r.area_code as Record<string, unknown>).source as string}
              />
            </div>
          )}
        </ToolResultCard>
      )}

      {/* Sources Used */}
      <ToolResultCard title="Data Sources" icon={Database}>
        <div className="flex flex-wrap gap-2">
          {result.sources_used.map((source, i) => (
            <span key={i} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium">
              {source}
            </span>
          ))}
        </div>
      </ToolResultCard>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<ToolTab>("universal");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LookupResult | LocationToolResult | UniversalSearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  // Universal Search state
  const [universalInput, setUniversalInput] = useState("");

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
        case "universal":
          if (!universalInput.trim()) { setLoading(false); return; }
          url = `/api/v1/location/universal-search`;
          params.set("q", universalInput.trim());
          if (country) params.set("country", country);
          break;

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
      case "universal": return "Enter phone, IMEI, IP, WiFi BSSID, domain, or coordinates (e.g. +14155552671, 353456789012345, 8.8.8.8, AA:BB:CC:DD:EE:FF, example.com)";
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
      case "universal":
        return (
          <div className="flex-1 relative">
            <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-violet-500" />
            <input
              type="text"
              value={universalInput}
              onChange={e => setUniversalInput(e.target.value)}
              placeholder={getPlaceholder()}
              className="w-full pl-10 pr-4 py-3 rounded-xl border-2 border-violet-300 dark:border-violet-600 bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500 transition-all text-sm"
              onKeyDown={e => e.key === "Enter" && handleLookup()}
            />
          </div>
        );
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

  const getSearchButtonColor = () => {
    if (activeTab === "universal") return "bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 shadow-violet-500/25";
    return "bg-primary hover:bg-primary/90 shadow-primary/20";
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
          <div className={`bg-white dark:bg-slate-800/50 rounded-2xl border p-6 shadow-sm ${
            activeTab === "universal" ? "border-violet-200 dark:border-violet-700" : "border-slate-200 dark:border-slate-700"
          }`}>
            <h1 className="text-2xl font-bold mb-1">
              {toolTabs.find(t => t.id === activeTab)?.label}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
              {toolTabs.find(t => t.id === activeTab)?.description}
              {activeTab === "universal" && " - Just type anything and we'll figure out what it is!"}
            </p>

            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-3">
                {renderPhoneInput()}
                <button
                  onClick={handleLookup}
                  disabled={loading}
                  className={`inline-flex items-center justify-center gap-2 px-6 py-3 text-white rounded-xl font-medium hover:disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg ${getSearchButtonColor()}`}
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  {loading ? "Analyzing..." : activeTab === "universal" ? "Search Everything" : "Lookup"}
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
              {/* Universal Search Results */}
              {activeTab === "universal" && "input_type" in result && (
                <UniversalSearchResults result={result as UniversalSearchResult} />
              )}

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

                  {(result.data.spam_score !== null || (result as LookupResult).osint) && (
                    <ToolResultCard title="Risk Assessment" icon={Shield}>
                      <RiskMeter score={result.data.spam_score as number} />
                    </ToolResultCard>
                  )}

                  {(result as LookupResult).geolocation && (
                    <ToolResultCard title="Estimated Location" icon={MapPin}>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Latitude</span><span className="font-mono">{(result as LookupResult).geolocation?.latitude as string}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Longitude</span><span className="font-mono">{(result as LookupResult).geolocation?.longitude as string}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Confidence</span><span className="capitalize font-medium">{(result as LookupResult).geolocation?.confidence as string}</span></div>
                          <div className="flex justify-between text-sm"><span className="text-slate-500">Source</span><span>{(result as LookupResult).geolocation?.source as string}</span></div>
                        </div>
                        <div className="min-h-[200px]">
                          <PhoneMap latitude={(result as LookupResult).geolocation?.latitude as number} longitude={(result as LookupResult).geolocation?.longitude as number} confidence={(result as LookupResult).geolocation?.confidence as string} source={(result as LookupResult).geolocation?.source as string} />
                        </div>
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

              {/* Location Tool Results */}
              {["cell-tower", "imei", "ip", "wifi", "area-code", "multi"].includes(activeTab) && "data" in result && (
                <ToolResultCard title={`${toolTabs.find(t => t.id === activeTab)?.label} Result`} icon={toolTabs.find(t => t.id === activeTab)?.icon || Target}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-1">
                    {Object.entries(result.data).filter(([k]) => !['all_sources', 'raw_data'].includes(k) && typeof result.data[k] !== 'object').map(([key, value]) => (
                      <DataRow key={key} label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} value={String(value ?? 'N/A')} />
                    ))}
                  </div>
                  {result.data.latitude && result.data.longitude && (
                    <div className="mt-4">
                      <PhoneMap latitude={result.data.latitude as number} longitude={result.data.longitude as number} confidence={result.data.confidence as string} source={result.data.source as string} />
                    </div>
                  )}
                </ToolResultCard>
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
