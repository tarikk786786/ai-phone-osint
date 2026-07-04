import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AI Phone Intelligence OSINT Platform",
    template: "%s | Phone OSINT",
  },
  description:
    "AI-powered phone number intelligence platform. Validate phone numbers, detect carriers, lookup geolocation, and generate AI investigation reports using public OSINT data.",
  keywords: [
    "phone intelligence",
    "OSINT",
    "phone lookup",
    "reverse phone lookup",
    "carrier lookup",
    "phone validation",
    "open source intelligence",
  ],
  authors: [{ name: "AI Phone OSINT" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "AI Phone Intelligence OSINT Platform",
    title: "AI Phone Intelligence OSINT Platform",
    description:
      "AI-powered phone number intelligence platform with public OSINT data gathering.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-blue-950 dark:to-indigo-950 antialiased">
        {children}
      </body>
    </html>
  );
}
