"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import IndustrialLayout from "../../components/IndustrialLayout";

const DEPARTMENTS = ["Sorting", "Shredding", "Processing", "Packaging", "Logistics", "Quality Control", "Administration"];

interface RecognizedEmployee {
  employeeId: string;
  employeeName: string;
  department: string;
  confidence: number;
  time: string;
  status: "present" | "unknown";
}

interface SessionStats {
  shiftCoverage: number;
  totalCheckedIn: number;
  lateArrivals: number;
  flaggedEvents: number;
}

export default function StartSessionPage() {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const [department, setDepartment] = useState(DEPARTMENTS[0]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [recognized, setRecognized] = useState<RecognizedEmployee[]>([]);
  const [stats, setStats] = useState<SessionStats>({ shiftCoverage: 0, totalCheckedIn: 0, lateArrivals: 0, flaggedEvents: 0 });
  const [status, setStatus] = useState("System online — configure session and start");
  const [time, setTime] = useState("");

  useEffect(() => {
    startCamera();
    const tick = setInterval(() => setTime(new Date().toLocaleTimeString("en-GB")), 1000);
    return () => {
      clearInterval(tick);
      stopCamera();
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; }
    } catch { setStatus("Camera unavailable — check permissions"); }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
  };

  const startSession = async () => {
    setStatus("Starting attendance session...");
    try {
      const res = await fetch("http://127.0.0.1:5000/api/attendance/create_session", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-Type": "manager" },
        body: JSON.stringify({ department, shift: "Day Shift" }),
      });
      const data = await res.json();
      if (data.success) {
        setSessionId(data.sessionId);
        setIsRunning(true);
        setStatus("Session active — scanning for employees...");
        intervalRef.current = setInterval(captureAndRecognize, 3000);
      } else {
        setStatus(data.error || "Failed to start session");
      }
    } catch { setStatus("Connection error"); }
  };

  const stopSession = async () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setIsRunning(false);
    setStatus("Session ended");
  };

  const captureAndRecognize = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0);
    const imageData = canvas.toDataURL("image/jpeg", 0.8);
    try {
      const res = await fetch("http://127.0.0.1:5000/api/attendance/real-mark", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-Type": "manager" },
        body: JSON.stringify({ sessionId, image: imageData }),
      });
      const data = await res.json();
      if (data.recognized?.length) {
        const newEntries: RecognizedEmployee[] = data.recognized.map((r: any) => ({
          employeeId: r.employeeId || r.employee_id,
          employeeName: r.employeeName || r.employee_name,
          department: r.department || department,
          confidence: Math.round((r.confidence || 0) * 100),
          time: new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }),
          status: "present",
        }));
        setRecognized(prev => {
          const ids = new Set(prev.map(p => p.employeeId));
          const fresh = newEntries.filter(e => !ids.has(e.employeeId));
          const updated = [...fresh, ...prev].slice(0, 20);
          setStats({
            shiftCoverage: Math.min(100, Math.round(updated.length / 10 * 100)),
            totalCheckedIn: updated.filter(u => u.status === "present").length,
            lateArrivals: data.lateArrivals || 0,
            flaggedEvents: data.unknown?.length || 0,
          });
          return updated;
        });
      }
    } catch {}
  }, [sessionId, department]);

  return (
    <IndustrialLayout activeNav="attendance" pageTitle="Live Attendance" userType="manager">
      <div style={{ padding: "24px 32px" }}>

        {/* Filter Controls */}
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-end", justifyContent: "space-between", gap: 16, marginBottom: 28 }}>
          <div style={{ display: "flex", gap: 20 }}>
            <div>
              <label style={{ fontSize: 10, fontWeight: 700, color: "#424754", letterSpacing: "0.1em", textTransform: "uppercase", display: "block", marginBottom: 8 }}>Department</label>
              <div style={{ position: "relative" }}>
                <select value={department} onChange={e => setDepartment(e.target.value)} disabled={isRunning}
                  style={{ minWidth: 200, padding: "10px 36px 10px 14px", background: "#f0f4f7", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 500, color: "#171c1f", appearance: "none", cursor: isRunning ? "not-allowed" : "pointer", fontFamily: "'Inter', sans-serif" }}>
                  {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
                </select>
                <span className="material-symbols-outlined" style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", fontSize: 18, color: "#94a3b8", pointerEvents: "none" }}>expand_more</span>
              </div>
            </div>
            <div>
              <label style={{ fontSize: 10, fontWeight: 700, color: "#424754", letterSpacing: "0.1em", textTransform: "uppercase", display: "block", marginBottom: 8 }}>Shift</label>
              <div style={{ padding: "10px 16px", background: "#f0f4f7", borderRadius: 8, fontSize: 13, fontWeight: 600, color: "#424754" }}>Day Shift (Fixed)</div>
            </div>
          </div>

          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            {isRunning && (
              <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 14px", background: "rgba(0,105,71,0.08)", borderRadius: 6 }}>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#006947", display: "inline-block", animation: "pulse 1.5s infinite" }} />
                <span style={{ fontSize: 11, fontWeight: 700, color: "#006947", letterSpacing: "0.1em", textTransform: "uppercase" }}>System Online</span>
              </div>
            )}
            {!isRunning ? (
              <button onClick={startSession} style={{
                display: "flex", alignItems: "center", gap: 8,
                background: "#0058be", color: "#fff", border: "none", borderRadius: 8,
                padding: "12px 28px", fontSize: 13, fontWeight: 700, cursor: "pointer", letterSpacing: "0.04em",
              }}>
                <span className="material-symbols-outlined" style={{ fontSize: 20 }}>play_circle</span>
                Start Attendance
              </button>
            ) : (
              <button onClick={stopSession} style={{
                display: "flex", alignItems: "center", gap: 8,
                background: "#ba1a1a", color: "#fff", border: "none", borderRadius: 8,
                padding: "12px 28px", fontSize: 13, fontWeight: 700, cursor: "pointer",
              }}>
                <span className="material-symbols-outlined" style={{ fontSize: 20 }}>stop_circle</span>
                Stop Session
              </button>
            )}
          </div>
        </div>

        {/* Main Grid: Camera + Employee List */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 24, marginBottom: 24 }}>
          {/* Camera Feed */}
          <div style={{ background: "#fff", borderRadius: 12, overflow: "hidden", boxShadow: "0 2px 12px rgba(23,28,31,0.08)" }}>
            <div style={{ padding: "12px 16px", background: "#f0f4f7", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div style={{ width: 10, height: 10, borderRadius: "50%", background: isRunning ? "#ba1a1a" : "#94a3b8", animation: isRunning ? "pulse 1s infinite" : "none" }} />
                <span style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#171c1f" }}>
                  {isRunning ? "CAM-01 : LIVE RECOGNITION" : "CAM-01 : STANDBY"}
                </span>
              </div>
              <span style={{ fontSize: 11, fontFamily: "monospace", color: "#64748b" }}>{time}</span>
            </div>
            <div style={{ position: "relative", background: "#000" }}>
              <video ref={videoRef} autoPlay muted playsInline style={{ width: "100%", display: "block", maxHeight: 420, objectFit: "cover", opacity: 0.9 }} />
              <canvas ref={canvasRef} style={{ display: "none" }} />
              {/* HUD Overlay */}
              <div style={{ position: "absolute", bottom: 16, left: 16, right: 16, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
                <div style={{ background: "rgba(255,255,255,0.85)", backdropFilter: "blur(16px)", padding: "10px 16px", borderRadius: 8, borderWidth: 1, borderStyle: "solid", borderColor: "rgba(255,255,255,0.3)" }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#424754", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 2 }}>Status</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "#171c1f" }}>{status}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "flex-end" }}>
                  {isRunning && (
                    <div style={{ background: "rgba(255,255,255,0.85)", backdropFilter: "blur(16px)", padding: "6px 12px", borderRadius: 20, display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#006947" }} />
                      <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase" }}>Scanning active</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Recognized Employees */}
          <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 2px 12px rgba(23,28,31,0.06)", display: "flex", flexDirection: "column", maxHeight: 520 }}>
            <div style={{ padding: "16px 20px 12px", borderBottom: "1px solid #f0f4f7" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 style={{ fontSize: 13, fontWeight: 700 }}>Recognized Employees</h3>
                <span style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                  {isRunning ? "Live Stream" : "Paused"}
                </span>
              </div>
              <p style={{ fontSize: 11, color: "#94a3b8", marginTop: 2 }}>{recognized.length} detected this session</p>
            </div>
            <div style={{ flex: 1, overflowY: "auto", padding: 8 }}>
              {recognized.length === 0 ? (
                <div style={{ padding: 32, textAlign: "center", color: "#94a3b8" }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 40 }}>face</span>
                  <p style={{ fontSize: 12, marginTop: 8 }}>{isRunning ? "Waiting for recognition..." : "Start session to begin"}</p>
                </div>
              ) : recognized.map((emp, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 12, padding: "10px 12px",
                  borderRadius: 8, marginBottom: 4, cursor: "default",
                  background: emp.status === "unknown" ? "rgba(186,26,26,0.04)" : "transparent",
                  transition: "background 0.15s",
                }}
                  onMouseEnter={e => { if (emp.status !== "unknown") (e.currentTarget as HTMLElement).style.background = "#f0f4f7"; }}
                  onMouseLeave={e => { if (emp.status !== "unknown") (e.currentTarget as HTMLElement).style.background = "transparent"; }}
                >
                  <div style={{ position: "relative" }}>
                    <div style={{ width: 36, height: 36, borderRadius: 8, background: emp.status === "unknown" ? "#ffdad6" : "#f0f4f7", display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <span className="material-symbols-outlined" style={{ fontSize: 18, color: emp.status === "unknown" ? "#ba1a1a" : "#424754" }}>
                        {emp.status === "unknown" ? "person_off" : "person"}
                      </span>
                    </div>
                    <div style={{ position: "absolute", bottom: -2, right: -2, width: 10, height: 10, borderRadius: "50%", border: "2px solid #fff", background: emp.status === "unknown" ? "#ba1a1a" : "#006947" }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span style={{ fontSize: 12, fontWeight: 700, color: emp.status === "unknown" ? "#ba1a1a" : "#171c1f", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {emp.employeeName}
                      </span>
                      <span style={{ fontSize: 10, color: "#94a3b8", flexShrink: 0, marginLeft: 8 }}>{emp.time}</span>
                    </div>
                    <p style={{ fontSize: 10, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.06em" }}>{emp.employeeId} · {emp.department}</p>
                  </div>
                  <div style={{
                    padding: "2px 6px", borderRadius: 4, fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em",
                    background: emp.status === "unknown" ? "#ba1a1a" : "rgba(111,251,190,0.15)",
                    color: emp.status === "unknown" ? "#fff" : "#006947",
                  }}>
                    {emp.status === "unknown" ? "Unknown" : "Present"}
                  </div>
                </div>
              ))}
            </div>
            <div style={{ padding: "10px 20px", background: "#f0f4f7" }}>
              <button onClick={() => router.push("/employee/view-attendance")} style={{ width: "100%", fontSize: 11, fontWeight: 700, color: "#0058be", background: "none", border: "none", cursor: "pointer", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                View Full History
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
          {[
            { label: "Shift Coverage", value: `${stats.shiftCoverage}%`, sub: isRunning ? "live" : "offline", color: "#0058be" },
            { label: "Total Checked-In", value: stats.totalCheckedIn, sub: "this session", color: "#006947" },
            { label: "Late Arrivals", value: stats.lateArrivals, sub: stats.lateArrivals > 5 ? "Critical" : "Normal", color: "#b45309" },
            { label: "Flagged Events", value: stats.flaggedEvents, sub: "Unknown faces", color: "#ba1a1a" },
          ].map((s, i) => (
            <div key={i} style={{
              background: "#fff", borderRadius: 10, padding: "20px 20px",
              borderLeft: `4px solid ${s.color}`, boxShadow: "0 1px 4px rgba(23,28,31,0.06)",
              display: "flex", flexDirection: "column", justifyContent: "space-between", height: 100,
            }}>
              <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "#94a3b8" }}>{s.label}</span>
              <div>
                <span style={{ fontSize: 32, fontWeight: 800, color: "#171c1f" }}>{s.value}</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: s.color, marginLeft: 8 }}>{s.sub}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </IndustrialLayout>
  );
}