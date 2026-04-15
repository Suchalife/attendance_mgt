"use client";
import { useEffect, useRef, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import IndustrialLayout from "../../components/IndustrialLayout";

const TOTAL_PHOTOS = 5;

function BiometricContent() {
  const router = useRouter();
  const params = useSearchParams();
  const employeeId = params.get("employeeId") || "";
  const employeeName = params.get("name") || employeeId;

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [photos, setPhotos] = useState<string[]>([]);
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [status, setStatus] = useState<{ msg: string; ok: boolean } | null>(null);
  const [countdown, setCountdown] = useState<number | null>(null);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  const startCamera = async () => {
    setCameraError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: "user" } });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setCameraOn(true);
    } catch {
      setCameraError("Camera access denied. Please allow camera permission and try again.");
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    setCameraOn(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current || photos.length >= TOTAL_PHOTOS) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.85);
    setPhotos(prev => [...prev, dataUrl]);
  };

  const captureWithCountdown = () => {
    if (countdown !== null) return;
    let c = 3;
    setCountdown(c);
    const interval = setInterval(() => {
      c -= 1;
      if (c === 0) {
        clearInterval(interval);
        setCountdown(null);
        capturePhoto();
      } else {
        setCountdown(c);
      }
    }, 1000);
  };

  const removePhoto = (idx: number) => {
    setPhotos(prev => prev.filter((_, i) => i !== idx));
  };

  const handleSubmit = async () => {
    if (photos.length !== TOTAL_PHOTOS) return;
    setSubmitting(true);
    setStatus(null);
    try {
      const res = await fetch("http://127.0.0.1:5000/api/register-employee", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-Type": "manager" },
        body: JSON.stringify({ employeeId, phase: "biometric", images: photos }),
      });
      const data = await res.json();
      if (data.success) {
        stopCamera();
        setStatus({ msg: "Biometric enrollment complete! Employee is now ready for face recognition.", ok: true });
      } else {
        setStatus({ msg: data.error || "Enrollment failed", ok: false });
      }
    } catch {
      setStatus({ msg: "Connection error — check if server is running", ok: false });
    } finally {
      setSubmitting(false);
    }
  };

  const remaining = TOTAL_PHOTOS - photos.length;

  return (
    <IndustrialLayout activeNav="registration" pageTitle="Biometric Enrollment" userType="manager">
      <div style={{ padding: "32px", maxWidth: 960 }}>
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 22, fontWeight: 800, color: "#171c1f" }}>Biometric Enrollment</h2>
          <p style={{ fontSize: 13, color: "#64748b", marginTop: 4 }}>
            Enrolling: <strong>{employeeName}</strong> ({employeeId}) — Capture {TOTAL_PHOTOS} clear face photos
          </p>
        </div>

        {status?.ok ? (
          <div style={{ background: "#fff", borderRadius: 12, padding: 48, textAlign: "center", boxShadow: "0 1px 4px rgba(23,28,31,0.06)" }}>
            <span className="material-symbols-outlined" style={{ fontSize: 64, color: "#006947" }}>verified_user</span>
            <h3 style={{ fontSize: 18, fontWeight: 800, color: "#171c1f", marginTop: 16 }}>Enrollment Complete</h3>
            <p style={{ fontSize: 13, color: "#64748b", marginTop: 8, marginBottom: 28 }}>{status.msg}</p>
            <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
              <button onClick={() => router.push("/employee/registrationform")}
                style={{ padding: "12px 28px", background: "#f0f4f7", color: "#424754", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                Register Another
              </button>
              <button onClick={() => router.push("/manager/dashboard")}
                style={{ padding: "12px 28px", background: "#0058be", color: "#fff", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                Go to Dashboard
              </button>
            </div>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 24 }}>

            {/* Camera */}
            <div style={{ background: "#fff", borderRadius: 12, padding: 24, boxShadow: "0 1px 4px rgba(23,28,31,0.06)" }}>
              <div style={{ position: "relative", background: "#0f172a", borderRadius: 10, overflow: "hidden", aspectRatio: "4/3", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <video ref={videoRef} autoPlay playsInline muted
                  style={{ width: "100%", height: "100%", objectFit: "cover", display: cameraOn ? "block" : "none" }} />
                <canvas ref={canvasRef} style={{ display: "none" }} />

                {!cameraOn && !cameraError && (
                  <div style={{ color: "#94a3b8", textAlign: "center" }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 48 }}>videocam</span>
                    <p style={{ fontSize: 13, marginTop: 8 }}>Starting camera...</p>
                  </div>
                )}
                {cameraError && (
                  <div style={{ color: "#fca5a5", textAlign: "center", padding: 24 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 48 }}>videocam_off</span>
                    <p style={{ fontSize: 13, marginTop: 8 }}>{cameraError}</p>
                    <button onClick={startCamera}
                      style={{ marginTop: 12, padding: "8px 20px", background: "#0058be", color: "#fff", border: "none", borderRadius: 8, fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
                      Retry
                    </button>
                  </div>
                )}

                {/* Countdown overlay */}
                {countdown !== null && (
                  <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.45)" }}>
                    <span style={{ fontSize: 96, fontWeight: 900, color: "#fff" }}>{countdown}</span>
                  </div>
                )}

                {/* Face guide overlay */}
                {cameraOn && countdown === null && (
                  <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
                    <div style={{ width: 180, height: 220, border: "2px dashed rgba(255,255,255,0.4)", borderRadius: "50%", boxShadow: "0 0 0 9999px rgba(0,0,0,0.2)" }} />
                  </div>
                )}

                {/* Photo count badge */}
                {cameraOn && (
                  <div style={{ position: "absolute", top: 12, right: 12, background: "rgba(0,0,0,0.6)", color: "#fff", borderRadius: 20, padding: "4px 12px", fontSize: 12, fontWeight: 700 }}>
                    {photos.length} / {TOTAL_PHOTOS}
                  </div>
                )}
              </div>

              <div style={{ marginTop: 16, display: "flex", gap: 12 }}>
                <button
                  onClick={captureWithCountdown}
                  disabled={!cameraOn || photos.length >= TOTAL_PHOTOS || countdown !== null}
                  style={{
                    flex: 1, padding: "14px", background: photos.length >= TOTAL_PHOTOS ? "#94a3b8" : "#0058be",
                    color: "#fff", border: "none", borderRadius: 10, fontSize: 14, fontWeight: 700,
                    cursor: photos.length >= TOTAL_PHOTOS || !cameraOn ? "not-allowed" : "pointer",
                    display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                  }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 20 }}>camera</span>
                  {countdown !== null ? `Capturing in ${countdown}...` : photos.length >= TOTAL_PHOTOS ? "All photos captured" : `Capture Photo ${photos.length + 1}`}
                </button>
              </div>

              <p style={{ fontSize: 11, color: "#94a3b8", marginTop: 10, textAlign: "center" }}>
                Position face inside the oval guide. Vary angles slightly for better accuracy.
              </p>
            </div>

            {/* Right panel: thumbnails + submit */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ background: "#fff", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(23,28,31,0.06)", flex: 1 }}>
                <h3 style={{ fontSize: 12, fontWeight: 700, color: "#424754", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 14 }}>
                  Captured Photos ({photos.length}/{TOTAL_PHOTOS})
                </h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {Array.from({ length: TOTAL_PHOTOS }).map((_, i) => (
                    <div key={i} style={{ position: "relative", aspectRatio: "1", borderRadius: 8, overflow: "hidden", background: "#f0f4f7", border: "2px solid", borderColor: photos[i] ? "#0058be" : "#e2e8f0" }}>
                      {photos[i] ? (
                        <>
                          <img src={photos[i]} alt={`Photo ${i + 1}`} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                          <button onClick={() => removePhoto(i)}
                            style={{ position: "absolute", top: 4, right: 4, width: 22, height: 22, background: "rgba(186,26,26,0.9)", color: "#fff", border: "none", borderRadius: "50%", fontSize: 14, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", lineHeight: 1 }}>
                            ×
                          </button>
                          <div style={{ position: "absolute", bottom: 4, left: 4, background: "rgba(0,88,190,0.85)", color: "#fff", borderRadius: 4, fontSize: 10, fontWeight: 700, padding: "2px 6px" }}>
                            {i + 1}
                          </div>
                        </>
                      ) : (
                        <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 4 }}>
                          <span className="material-symbols-outlined" style={{ fontSize: 24, color: "#cbd5e1" }}>add_a_photo</span>
                          <span style={{ fontSize: 10, color: "#94a3b8", fontWeight: 600 }}>Photo {i + 1}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {remaining > 0 && (
                  <p style={{ fontSize: 11, color: "#94a3b8", marginTop: 12, textAlign: "center" }}>
                    {remaining} more photo{remaining > 1 ? "s" : ""} needed
                  </p>
                )}
              </div>

              <button
                onClick={handleSubmit}
                disabled={photos.length !== TOTAL_PHOTOS || submitting}
                style={{
                  padding: "16px", background: photos.length === TOTAL_PHOTOS && !submitting ? "#006947" : "#94a3b8",
                  color: "#fff", border: "none", borderRadius: 10, fontSize: 14, fontWeight: 800,
                  cursor: photos.length === TOTAL_PHOTOS && !submitting ? "pointer" : "not-allowed",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                }}>
                <span className="material-symbols-outlined" style={{ fontSize: 20 }}>fingerprint</span>
                {submitting ? "Processing..." : photos.length === TOTAL_PHOTOS ? "Complete Enrollment" : `Capture ${remaining} More`}
              </button>

              {status && !status.ok && (
                <div style={{ padding: "12px 16px", borderRadius: 8, fontSize: 12, background: "#fff1f2", color: "#ba1a1a", display: "flex", gap: 8, alignItems: "flex-start" }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16, flexShrink: 0, marginTop: 1 }}>error</span>
                  {status.msg}
                </div>
              )}

              <button onClick={() => router.push("/manager/dashboard")}
                style={{ padding: "10px", background: "#f0f4f7", color: "#424754", border: "none", borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: "pointer" }}>
                Skip for now
              </button>
            </div>
          </div>
        )}
      </div>
    </IndustrialLayout>
  );
}

export default function BiometricPage() {
  return (
    <Suspense fallback={null}>
      <BiometricContent />
    </Suspense>
  );
}
