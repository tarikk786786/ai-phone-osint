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
            Validate phone numbers, detect carriers, estimate geolocation, and
            generate AI investigation reports — all from publicly available data.
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
              href="https://github.com"
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
    title: "Geolocation Estimate",
    description: "Estimated location from area codes and public telecom databases (NOT GPS).",
    color: "from-emerald-500 to-emerald-600",
  },
  {
    icon: Shield,
    title: "Spam & Risk Analysis",
    description: "Check public spam databases and assign a risk score to suspicious numbers.",
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

function HowItWorksSection() {
  const steps = [
    {
      icon: Search,
      title: "Enter a Phone Number",
      description: "Input any phone number in international or local format.",
    },
    {
      icon: Database,
      title: "Intelligence Gathering",
      description: "Automated validation, carrier lookup, OSINT checks, and geolocation estimation.",
    },
    {
      icon: Brain,
      title: "AI Analysis",
      description: "Optional AI-powered investigation report with risk assessment and recommendations.",
    },
    {
      icon: FileText,
      title: "Export & Share",
      description: "Export results as PDF, CSV, or JSON. Share via API.",
    },
  ];

  return (
    <section id="how-it-works" className="py-20 px-4 bg-white/50 dark:bg-slate-900/50">
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
            { icon: Shield, value: "99.9%", label: "Validation Accuracy" },
            { icon: Users, value: "Open Source", label: "Community Driven" },
            { icon: Activity, value: "Real-time", label: "Analysis" },
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
                This tool uses only publicly available information and public telecom datasets.
                It does NOT determine real-time GPS locations. All geolocation data is estimated
                from area codes and carrier regions. Use only for lawful purposes such as
                security research, fraud prevention, and publicly available intelligence gathering.
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
              AI-powered phone number intelligence platform for OSINT research.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Product</h4>
            <div className="space-y-2 text-sm text-slate-500">
              <a href="#features" className="block hover:text-primary transition-colors">Features</a>
              <a href="#" className="block hover:text-primary transition-colors">API</a>
              <a href="#" className="block hover:text-primary transition-colors">Documentation</a>
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
              <a href="https://github.com" className="flex items-center gap-1 hover:text-primary transition-colors">
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
      <HowItWorksSection />
      <DisclaimerSection />
      <Footer />
    </div>
  );
}
