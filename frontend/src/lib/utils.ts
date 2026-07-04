import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function formatPhone(phone: string): string {
  // International format display
  if (phone.startsWith("+")) {
    return phone;
  }
  return `+${phone}`;
}

export function getRiskColor(score: number | null | undefined): string {
  if (!score && score !== 0) return "bg-gray-100 text-gray-800";
  if (score >= 70) return "bg-red-100 text-red-800";
  if (score >= 40) return "bg-yellow-100 text-yellow-800";
  return "bg-green-100 text-green-800";
}

export function getRiskLabel(score: number | null | undefined): string {
  if (!score && score !== 0) return "Unknown";
  if (score >= 70) return "High Risk";
  if (score >= 40) return "Medium Risk";
  return "Low Risk";
}
