"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Users,
  Activity,
  Phone,
  Shield,
  BarChart3,
  Lock,
  ChevronRight,
} from "lucide-react";

interface Stats {
  total_users: number;
  total_lookups: number;
  lookups_today: number;
  top_users: { username: string; lookups: number }[];
}

export default function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch stats (mock for now)
    setTimeout(() => {
      setStats({
        total_users: 42,
        total_lookups: 1257,
        lookups_today: 18,
        top_users: [
          { username: "analyst1", lookups: 234 },
          { username: "researcher42", lookups: 156 },
          { username: "security_pro", lookups: 89 },
        ],
      });
      setLoading(false);
    }, 500);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-blue-950 dark:to-indigo-950">
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 dark:bg-slate-950/70 border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lock className="w-5 h-5 text-primary" />
            <span className="font-bold">Admin Panel</span>
          </div>
          <a href="/dashboard" className="text-sm text-slate-500 hover:text-primary transition-colors">
            ← Back to Dashboard
          </a>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold mb-2">System Administration</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-8">
            Manage users, monitor usage, and configure system settings.
          </p>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl animate-pulse" />
              ))}
            </div>
          ) : stats ? (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Users className="w-5 h-5 text-primary" />
                    <span className="text-sm text-slate-500">Total Users</span>
                  </div>
                  <div className="text-3xl font-bold">{stats.total_users}</div>
                </div>

                <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Phone className="w-5 h-5 text-primary" />
                    <span className="text-sm text-slate-500">Total Lookups</span>
                  </div>
                  <div className="text-3xl font-bold">{stats.total_lookups}</div>
                </div>

                <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Activity className="w-5 h-5 text-primary" />
                    <span className="text-sm text-slate-500">Lookups Today</span>
                  </div>
                  <div className="text-3xl font-bold">{stats.lookups_today}</div>
                </div>
              </div>

              {/* Top Users */}
              <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  Top Users
                </h2>
                <div className="space-y-3">
                  {stats.top_users.map((user, i) => (
                    <div
                      key={user.username}
                      className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-slate-400">#{i + 1}</span>
                        <span className="font-medium">{user.username}</span>
                      </div>
                      <span className="text-sm text-slate-500">{user.lookups} lookups</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : null}
        </motion.div>
      </main>
    </div>
  );
}
