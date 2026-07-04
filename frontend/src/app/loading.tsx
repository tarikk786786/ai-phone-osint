import { Phone } from "lucide-react";

export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-blue-950 dark:to-indigo-950">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 relative">
          <div className="absolute inset-0 rounded-full border-4 border-slate-200 dark:border-slate-700" />
          <div className="absolute inset-0 rounded-full border-4 border-primary border-t-transparent animate-spin" />
          <Phone className="absolute inset-0 m-auto w-6 h-6 text-primary animate-pulse" />
        </div>
        <div className="text-lg font-medium text-slate-600 dark:text-slate-400 animate-pulse">
          Loading...
        </div>
      </div>
    </div>
  );
}
