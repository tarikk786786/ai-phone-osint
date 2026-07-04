"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Phone,
  Shield,
  Globe,
  MapPin,
  Brain,
  Download,
  Search,
  ChevronRight,
  Star,
  Github,
  FileText,
  Users,
  Lock,
  Database,
  Activity,
  Signal,
  Fingerprint,
  Wifi,
  Hash,
  Layers,
  Radar,
  Target,
  Smartphone,
  Crosshair,
  Zap,
  ShieldAlert,
} from "lucide-react";

// ── Components ─────────────────────────────────────────

function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-white/70 dark:bg-slate-950/70 border-b border-slate-200/50 dark:border-slate-800/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <Phone className="w-6 h-6 text-primary" />
            <span className="font-bold text-lg bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              PhoneOSINT
            </span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-slate-600 hover:text-primary dark:text-slate-400 dark:hover:text-primary transition-colors">
              Features
            </a>
            <a href="#tools" className="text-sm text-slate-600 hover:text-primary dark:text-slate-400 dark:hover:text-primary transition-colors">
              Location Tools
            </a>
            <a href="#how-it-works" className="text-sm text-slate-600 hover:text-primary dark:text-slate-400 dark:hover:text-primary transition-colors">
              How it works
            </a>
            <a href="#docs" className="text-sm text-slate-600 hover:text-primary dark:text-slate-400 dark:hover:text-primary transition-colors">
              API
            </a>
            <a
              href="/dashboard"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-all"
            >
              Get Started
              <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}

function HeroSection() {
  return (
    <section className="relative pt-32 pb-20 px-4 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 pointer-events-none" />
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />

      <div className="max-w-4xl mx-auto text-center relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full text-sm text-primary mb-8">
            <Star className="w-4 h-4" />
            <span>Open Source Intelligence Platform</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
            AI-Powered{" "}
            <span className="bg-gradient-to-r from-primary via-blue-500 to-accent bg-clip-text text-transparent">
              Phone Intelligence
            </span>
          </h1>

          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Validate phone numbers, detect carriers, locate devices via cell towers,
            IMEI, WiFi, IP geolocation, and generate AI investigation reports — all from
            publicly available data using 10+ OSINT tools.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-white rounded-xl text-lg font-semibold hover:bg-primary/90 transition-all shadow-lg shadow-primary/25 hover:shadow-primary/40"
            >
              <Search className="w-5 h-5" />
              Try Phone Lookup
            </a>
            <a
              href="https://github.com/tarikk786786/ai-phone-osint"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-lg font-medium hover:bg-slate-50 dark:hover:bg-slate-700 transition-all"
            >
              <Github className="w-5 h-5" />
              View on GitHub
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

const features = [
  {
    icon: Phone,
    title: "Phone Validation",
    description: "Validate and parse phone numbers from 200+ countries using Google's libphonenumber.",
    color: "from-blue-500 to-blue-600",
  },
  {
    icon: Globe,
    title: "Carrier Detection",
    description: "Detect carrier, line type (mobile/VoIP/landline), and porting status.",
    color: "from-teal-500 to-teal-600",
  },
  {
    icon: MapPin,
    title: "Multi-Source Geolocation",
    description: "Aggregate location from 10+ sources: OpenCellID, Nominatim, OpenCage, Mozilla LS, and more.",
    color: "from-emerald-500 to-emerald-600",
  },
  {
    icon: Shield,
    title: "Spam & Risk Analysis",
    description: "Check 8+ spam databases and assign risk scores using community-sourced data.",
    color: "from-red-500 to-red-600",
  },
  {
    icon: Brain,
    title: "AI Investigation Reports",
    description: "Generate detailed reports using OpenAI, Gemini, DeepSeek, or local models.",
    color: "from-purple-500 to-purple-600",
  },
  {
    icon: Download,
    title: "Export & API",
    description: "Export to PDF, CSV, JSON. Full REST API with API key authentication.",
    color: "from-orange-500 to-orange-600",
  },
];

function FeaturesSection() {
  return (
    <section id="features" className="py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold mb-4">
            Everything you need for phone intelligence
          </h2>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Comprehensive phone number analysis using only public and lawful data sources.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="group relative p-6 bg-white dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:border-primary/30 transition-all duration-300"
            >
              <div
                className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 text-white`}
              >
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

const locationTools = [
  {
    icon: Layers,
    title: "Multi-Source Aggregation",
    description: "Combine 10+ geolocation sources for the best accuracy: OpenCellID, Nominatim, OpenCage, Mozilla LS, ip-api, Google Maps, carrier regions.",
    sources: "10+ sources",
    accuracy: "Best available",
    color: "from-purple-500 to-purple-600",
  },
  {
    icon: Signal,
    title: "Cell Tower Geolocation",
    description: "Locate devices using MCC/MNC/LAC/CID cell tower data via OpenCellID and Mozilla Location Service databases.",
    sources: "OpenCellID, Mozilla LS",
    accuracy: "100m - 5km",
    color: "from-green-500 to-green-600",
  },
  {
    icon: Fingerprint,
    title: "IMEI Device Lookup",
    description: "Identify device make, model, brand, and manufacturer from IMEI number. Check blacklist and stolen status.",
    sources: "IMEI Database APIs",
    accuracy: "Device-level",
    color: "from-orange-500 to-orange-600",
  },
  {
    icon: Globe,
    title: "IP Geolocation",
    description: "Geolocate any IP address using 3 free APIs: ip-api.com, ipwho.is, ipinfo.io. Detect proxy/VPN status.",
    sources: "ip-api, ipwho.is, ipinfo",
    accuracy: "City-level",
    color: "from-cyan-500 to-cyan-600",
  },
  {
    icon: Wifi,
    title: "WiFi BSSID Geolocation",
    description: "Locate devices via WiFi access point MAC addresses using Mozilla Location Service WiFi API.",
    sources: "Mozilla Location Service",
    accuracy: "10m - 100m",
    color: "from-pink-500 to-pink-600",
  },
  {
    icon: Hash,
    title: "Area Code Mapping",
    description: "Estimate location from phone area codes using built-in database covering US, UK, India, and more.",
    sources: "Built-in DB + Nominatim",
    accuracy: "City-level",
    color: "from-teal-500 to-teal-600",
  },
  {
    icon: Radar,
    title: "OSINT Phone Scan",
    description: "Scan 8+ spam databases and check 10 social platforms for phone number intelligence.",
    sources: "15+ public sources",
    accuracy: "Community-sourced",
    color: "from-red-500 to-red-600",
  },
  {
    icon: Crosshair,
    title: "Reverse Geocoding",
    description: "Convert GPS coordinates to human-readable addresses using Nominatim (OpenStreetMap).",
    sources: "Nominatim/OSM",
    accuracy: "Address-level",
    color: "from-indigo-500 to-indigo-600",
  },
  {
    icon: ShieldAlert,
    title: "Spam & Fraud Detection",
    description: "Check 8+ spam databases including spamcalls.net, truecaller.com, tellows.com, and more.",
    sources: "8+ spam databases",
    accuracy: "Community-sourced",
    color: "from-rose-500 to-rose-600",
  },
];

function LocationToolsSection() {
  return (
    <section id="tools" className="py-20 px-4 bg-white/50 dark:bg-slate-900/50">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full text-sm text-green-600 dark:text-green-400 mb-6">
            <MapPin className="w-4 h-4" />
            <span>11 Location Finder Tools</span>
          </div>
          <h2 className="text-4xl font-bold mb-4">
            All Mobile Location Finder Tools
          </h2>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
            Integrated from the best open-source OSINT tools on GitHub.
            Cell tower triangulation, IMEI lookup, WiFi geolocation, IP tracking, and more.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {locationTools.map((tool, i) => (
            <motion.div
              key={tool.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="group relative p-6 bg-white dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:border-primary/30 transition-all duration-300"
            >
              <div
                className={`w-12 h-12 rounded-lg bg-gradient-to-br ${tool.color} flex items-center justify-center mb-4 text-white`}
              >
                <tool.icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{tool.title}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-3">
                {tool.description}
              </p>
              <div className="flex items-center gap-3 text-xs text-slate-500">
                <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded">{tool.sources}</span>
                <span className="px-2 py-0.5 bg-primary/10 text-primary rounded">{tool.accuracy}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorksSection() {
  const steps = [
    {
      icon: Search,
      title: "Enter Data",
      description: "Input a phone number, IMEI, IP address, cell tower info, or WiFi BSSID.",
    },
    {
      icon: Database,
      title: "Multi-Source Lookup",
      description: "Automated queries to 10+ public databases in parallel for best accuracy.",
    },
    {
      icon: Brain,
      title: "AI Analysis",
      description: "Optional AI-powered investigation report with risk assessment and recommendations.",
    },
    {
      icon: FileText,
      title: "Export & Share",
      description: "Export results as PDF, CSV, or JSON. Full REST API available.",
    },
  ];

  return (
    <section id="how-it-works" className="py-20 px-4">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold mb-4">How it works</h2>
          <p className="text-xl text-slate-600 dark:text-slate-400">
            From phone number to comprehensive intelligence report in seconds.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="text-center"
            >
              <div className="relative">
                <div className="w-16 h-16 mx-auto rounded-full bg-primary/10 border-2 border-primary/20 flex items-center justify-center mb-4">
                  <step.icon className="w-7 h-7 text-primary" />
                </div>
                {i < steps.length - 1 && (
                  <div className="hidden md:block absolute top-8 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-primary/30 to-transparent" />
                )}
              </div>
              <div className="text-sm font-semibold text-primary mb-2">Step {i + 1}</div>
              <h3 className="font-semibold mb-2">{step.title}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function StatsSection() {
  return (
    <section className="py-16 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { icon: Phone, value: "200+", label: "Countries Supported" },
            { icon: MapPin, value: "10+", label: "Location Sources" },
            { icon: Users, value: "Open Source", label: "Community Driven" },
            { icon: Zap, value: "Real-time", label: "Analysis" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <stat.icon className="w-8 h-8 mx-auto text-primary mb-2" />
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="text-sm text-slate-500">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function DisclaimerSection() {
  return (
    <section className="py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="p-6 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800">
          <div className="flex items-start gap-3">
            <Lock className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
            <div>
              <h3 className="font-semibold text-amber-800 dark:text-amber-300 mb-2">
                Ethical & Legal Use Only
              </h3>
              <p className="text-sm text-amber-700 dark:text-amber-400 leading-relaxed">
                This tool uses publicly available information and public telecom datasets to provide
                comprehensive phone intelligence. It aggregates data from 10+ location sources including
                cell tower databases (OpenCellID), WiFi BSSID geolocation, IP geolocation (ip-api, ipwho.is),
                area code mapping, carrier region analysis, IMEI device lookup, and multi-source aggregation.
                All geolocation data is estimated from public sources and should be verified through official
                channels. Use responsibly for lawful purposes such as security research, fraud prevention,
                and publicly available intelligence gathering.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="py-12 px-4 border-t border-slate-200 dark:border-slate-800">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Phone className="w-5 h-5 text-primary" />
              <span className="font-bold">PhoneOSINT</span>
            </div>
            <p className="text-sm text-slate-500">
              AI-powered phone number intelligence platform with 11 location finder tools.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Product</h4>
            <div className="space-y-2 text-sm text-slate-500">
              <a href="#features" className="block hover:text-primary transition-colors">Features</a>
              <a href="#tools" className="block hover:text-primary transition-colors">Location Tools</a>
              <a href="/dashboard" className="block hover:text-primary transition-colors">Dashboard</a>
            </div>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Legal</h4>
            <div className="space-y-2 text-sm text-slate-500">
              <a href="#" className="block hover:text-primary transition-colors">Privacy</a>
              <a href="#" className="block hover:text-primary transition-colors">Terms</a>
              <a href="#" className="block hover:text-primary transition-colors">License (MIT)</a>
            </div>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Community</h4>
            <div className="space-y-2 text-sm text-slate-500">
              <a href="https://github.com/tarikk786786/ai-phone-osint" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 hover:text-primary transition-colors">
                <Github className="w-4 h-4" /> GitHub
              </a>
              <a href="#" className="block hover:text-primary transition-colors">Report Issue</a>
            </div>
          </div>
        </div>
        <div className="text-center text-sm text-slate-400 pt-8 border-t border-slate-200 dark:border-slate-800">
          © {new Date().getFullYear()} AI Phone Intelligence OSINT Platform. MIT Licensed.
        </div>
      </div>
    </footer>
  );
}

// ── Page ────────────────────────────────────────────────

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <LocationToolsSection />
      <HowItWorksSection />
      <DisclaimerSection />
      <Footer />
    </div>
  );
}
