"use client";

import { useEffect, useState } from "react";
import { MapPin, AlertTriangle } from "lucide-react";

interface PhoneMapProps {
  latitude?: number | null;
  longitude?: number | null;
  confidence?: string;
  source?: string;
  address?: string;
}

export default function PhoneMap({
  latitude,
  longitude,
  confidence,
  source,
  address,
}: PhoneMapProps) {
  const [MapComponent, setMapComponent] = useState<React.ReactNode | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (latitude == null || longitude == null) return;

    const initMap = async () => {
      try {
        const L = await import("leaflet");
        await import("leaflet/dist/leaflet.css");

        // Fix default marker icon
        delete (L.Icon.Default.prototype as Record<string, unknown>)._getIconUrl;
        L.Icon.Default.mergeOptions({
          iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
          iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
          shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
        });

        const { MapContainer, TileLayer, Marker, Popup } = await import("react-leaflet");

        setMapComponent(
          <MapContainer
            center={[latitude, longitude]}
            zoom={10}
            className="w-full h-full rounded-xl z-10"
            key={`${latitude}-${longitude}`}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <Marker position={[latitude, longitude]}>
              <Popup>
                <div className="text-sm">
                  <strong>Estimated Location</strong>
                  <br />
                  {address && <>{address}<br /></>}
                  {latitude.toFixed(4)}, {longitude.toFixed(4)}
                  <br />
                  <span className="text-xs text-slate-500">
                    Source: {source || "Unknown"} | Confidence: {confidence || "estimated"}
                  </span>
                </div>
              </Popup>
            </Marker>
          </MapContainer>
        );
      } catch (err) {
        setError("Failed to load map component");
      }
    };

    initMap();
  }, [latitude, longitude, address, source, confidence]);

  if (error) {
    return (
      <div className="flex items-center justify-center h-48 bg-slate-100 dark:bg-slate-800 rounded-xl text-sm text-slate-500">
        <AlertTriangle className="w-4 h-4 mr-2" />
        {error}
      </div>
    );
  }

  if (latitude == null || longitude == null) {
    return (
      <div className="flex flex-col items-center justify-center h-48 bg-slate-100 dark:bg-slate-800 rounded-xl text-sm text-slate-400">
        <MapPin className="w-8 h-8 mb-2 text-slate-300" />
        No location data available
      </div>
    );
  }

  return (
    <div className="w-full h-64 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 relative">
      {MapComponent || (
        <div className="flex items-center justify-center h-full bg-slate-100 dark:bg-slate-800">
          <div className="animate-pulse text-sm text-slate-400">Loading map...</div>
        </div>
      )}
      <div className="absolute bottom-2 left-2 z-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm px-2 py-1 rounded text-xs text-slate-500">
        {source || "OSM"} · {confidence || "estimated"}
      </div>
    </div>
  );
}
