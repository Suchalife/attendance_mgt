"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Props {
  children: React.ReactNode;
  activeNav?: "dashboard" | "registration" | "biometric" | "attendance" | "reports";
  pageTitle?: string;
  userType?: "employee" | "manager";
}

const NAV_ITEMS = [
  { key: "dashboard",    icon: "dashboard",       label: "Dashboard" },
  { key: "registration", icon: "person_add",       label: "Employee Registration" },
  { key: "biometric",    icon: "fingerprint",      label: "Biometric Enrollment" },
  { key: "attendance",   icon: "event_available",  label: "Attendance" },
  { key: "reports",      icon: "analytics",        label: "Reports" },
];

export default function IndustrialLayout({ children, activeNav, pageTitle, userType = "manager" }: Props) {
  const router = useRouter();
  const [today, setToday] = useState("");

  useEffect(() => {
    setToday(new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }));
  }, []);

  const navigate = (key: string) => {
    const routes: Record<string, string> = {
      dashboard:    "/manager/dashboard",
      registration: "/employee/registrationform",
      biometric:    "/employee/registrationform",
      attendance:   "/manager/start-session",
      reports:      "/employee/view-attendance",
    };
    router.push(routes[key] || "/manager/dashboard");
  };

  return (
    <div style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* ── Sidebar ── */}
      <aside
        style={{
          background: "#1f2a37",
          width: 256,
          height: "100vh",
          position: "fixed",
          left: 0,
          top: 0,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          paddingTop: 24,
          paddingBottom: 24,
          zIndex: 50,
          boxShadow: "4px 0 24px rgba(0,0,0,0.25)",
        }}
      >
        {/* Brand */}
        <div style={{ padding: "0 24px", marginBottom: 32 }}>
          <div style={{ width: 36, height: 36, background: "#0058be", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 12 }}>
            <span className="material-symbols-outlined" style={{ color: "#fff", fontSize: 20 }}>factory</span>
          </div>
          <h1 style={{ fontSize: 15, fontWeight: 800, color: "#fff", letterSpacing: "0.15em", textTransform: "uppercase", lineHeight: 1.2 }}>
            Industrial Intelligence
          </h1>
          <p style={{ fontSize: 11, color: "#94a3b8", marginTop: 4, letterSpacing: "0.02em" }}>Recycling Ops · AMS</p>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: 2 }}>
          {NAV_ITEMS.map(item => {
            const isActive = activeNav === item.key;
            return (
              <button
                key={item.key}
                onClick={() => navigate(item.key)}
                style={{
                  display: "flex", alignItems: "center", gap: 12,
                  padding: "10px 16px", margin: "0 8px",
                  borderRadius: 6, fontSize: 13, fontWeight: 500,
                  letterSpacing: "-0.01em", background: isActive ? "#0058be" : "transparent",
                  color: isActive ? "#fff" : "#94a3b8",
                  border: "none", cursor: "pointer",
                  transition: "background 0.15s, color 0.15s", textAlign: "left",
                }}
                onMouseEnter={e => { if (!isActive) { (e.currentTarget as HTMLElement).style.background = "#171c1f"; (e.currentTarget as HTMLElement).style.color = "#fff"; } }}
                onMouseLeave={e => { if (!isActive) { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.color = "#94a3b8"; } }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 20, fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}>
                  {item.icon}
                </span>
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Bottom info */}
        <div style={{ borderTop: "1px solid rgba(148,163,184,0.2)", paddingTop: 16, padding: "16px 24px 0" }}>
          <p style={{ fontSize: 11, color: "#475569", fontWeight: 600 }}>Admin</p>
          <p style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em" }}>Manager</p>
        </div>
      </aside>

      {/* ── Top App Bar ── */}
      <header
        style={{
          position: "fixed", top: 0, left: 256, right: 0, height: 64,
          background: "#f0f4f7", display: "flex", alignItems: "center",
          justifyContent: "space-between", padding: "0 32px", zIndex: 40,
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <h2 style={{ fontSize: 13, fontWeight: 700, color: "#0058be", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            {pageTitle || "Dashboard"}
          </h2>
          {today && (
            <>
              <div style={{ width: 1, height: 16, background: "#c2c6d6" }} />
              <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>{today}</span>
            </>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: "50%",
            background: "#0058be", display: "flex", alignItems: "center", justifyContent: "center",
            color: "#fff", fontSize: 14, fontWeight: 700,
          }}>A</div>
          <div>
            <p style={{ fontSize: 12, fontWeight: 700, color: "#171c1f" }}>Admin</p>
            <p style={{ fontSize: 10, color: "#64748b" }}>Manager</p>
          </div>
        </div>
      </header>

      {/* ── Page Content ── */}
      <main style={{ marginLeft: 256, paddingTop: 64, minHeight: "100vh", background: "#f6fafd" }}>
        {children}
      </main>
    </div>
  );
}
