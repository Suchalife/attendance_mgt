"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import IndustrialLayout from "../../components/IndustrialLayout";

const DEPARTMENTS = ["Sorting", "Shredding", "Processing", "Packaging", "Logistics", "Quality Control", "Administration"];
const BRANCHES = ["CHN-01 (Chennai)", "BLR-02 (Bangalore)", "HYD-03 (Hyderabad)", "MUM-04 (Mumbai)"];

const EMPTY_FORM = { employeeId: "", employeeName: "", email: "", role: "", phoneNumber: "", department: DEPARTMENTS[0], branch: BRANCHES[0] };

export default function RegistrationPage() {
  const router = useRouter();
  const [form, setForm] = useState(EMPTY_FORM);
  const [status, setStatus] = useState<{ msg: string; ok: boolean } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch("http://127.0.0.1:5000/api/register-employee", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-Type": "manager" },
        body: JSON.stringify({ ...form, shift: "Day" }),
      });
      const data = await res.json();
      if (data.success) {
        router.push(`/employee/biometric?employeeId=${encodeURIComponent(form.employeeId)}&name=${encodeURIComponent(form.employeeName)}`);
      } else {
        setStatus({ msg: data.error || "Registration failed", ok: false });
      }
    } catch {
      setStatus({ msg: "Connection error — check if server is running", ok: false });
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: "100%", padding: "12px 16px", background: "#f0f4f7", border: "none",
    borderRadius: 8, fontSize: 13, color: "#171c1f", outline: "none",
    fontFamily: "'Inter', sans-serif",
  };
  const labelStyle = {
    fontSize: 11, fontWeight: 700, color: "#424754", letterSpacing: "0.08em",
    textTransform: "uppercase" as const, display: "block" as const, marginBottom: 8,
  };
  const onFocus = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.currentTarget.style.background = "#fff";
    e.currentTarget.style.boxShadow = "0 2px 0 0 #0058be";
  };
  const onBlur = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.currentTarget.style.background = "#f0f4f7";
    e.currentTarget.style.boxShadow = "none";
  };

  return (
    <IndustrialLayout activeNav="registration" pageTitle="Employee Registration" userType="manager">
      <div style={{ padding: "32px 32px", maxWidth: 900 }}>

        <div style={{ marginBottom: 28 }}>
          <h2 style={{ fontSize: 22, fontWeight: 800, color: "#171c1f" }}>Register New Employee</h2>
          <p style={{ fontSize: 13, color: "#64748b", marginTop: 4 }}>Add new personnel to the industrial management system.</p>
        </div>

        <div style={{ background: "#fff", borderRadius: 12, padding: 32, boxShadow: "0 1px 4px rgba(23,28,31,0.06)" }}>
          <form onSubmit={handleSave}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24, marginBottom: 32 }}>

              {/* Text fields */}
              {[
                { key: "employeeId",   label: "Employee ID",        placeholder: "EMP-2024-001", type: "text",  required: true  },
                { key: "employeeName", label: "Full Name",           placeholder: "Legal full name",             type: "text",  required: true  },
                { key: "email",        label: "Email Address",       placeholder: "employee@ecorecycle.com",     type: "email", required: true  },
                { key: "role",         label: "Role / Designation",  placeholder: "e.g. Senior Technician",     type: "text",  required: false },
                { key: "phoneNumber",  label: "Phone Number",        placeholder: "+91 99999 99999",            type: "tel",   required: false },
              ].map(f => (
                <div key={f.key}>
                  <label style={labelStyle}>{f.label}</label>
                  <input
                    type={f.type}
                    required={f.required}
                    value={(form as any)[f.key]}
                    onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                    placeholder={f.placeholder}
                    style={inputStyle}
                    onFocus={onFocus}
                    onBlur={onBlur}
                  />
                </div>
              ))}

              {/* Department */}
              <div>
                <label style={labelStyle}>Department</label>
                <div style={{ position: "relative" }}>
                  <select
                    value={form.department}
                    onChange={e => setForm(p => ({ ...p, department: e.target.value }))}
                    style={{ ...inputStyle, paddingRight: 36, appearance: "none", cursor: "pointer" }}
                    onFocus={onFocus} onBlur={onBlur}
                  >
                    {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
                  </select>
                  <span className="material-symbols-outlined" style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", fontSize: 18, color: "#94a3b8", pointerEvents: "none" }}>expand_more</span>
                </div>
              </div>

              {/* Branch */}
              <div>
                <label style={labelStyle}>Branch</label>
                <div style={{ position: "relative" }}>
                  <select
                    value={form.branch}
                    onChange={e => setForm(p => ({ ...p, branch: e.target.value }))}
                    style={{ ...inputStyle, paddingRight: 36, appearance: "none", cursor: "pointer" }}
                    onFocus={onFocus} onBlur={onBlur}
                  >
                    {BRANCHES.map(b => <option key={b}>{b}</option>)}
                  </select>
                  <span className="material-symbols-outlined" style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", fontSize: 18, color: "#94a3b8", pointerEvents: "none" }}>expand_more</span>
                </div>
              </div>

            </div>

            {/* Actions */}
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: "12px 36px", background: loading ? "#94a3b8" : "#0058be",
                  color: "#fff", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700,
                  cursor: loading ? "not-allowed" : "pointer",
                }}
              >
                {loading ? "Registering..." : "Register Employee"}
              </button>
              <button
                type="button"
                onClick={() => { setForm(EMPTY_FORM); setStatus(null); }}
                style={{ padding: "12px 36px", background: "#f0f4f7", color: "#424754", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: "pointer" }}
              >
                Clear
              </button>
              <button
                type="button"
                onClick={() => router.push("/manager/dashboard")}
                style={{ padding: "12px 36px", background: "#f0f4f7", color: "#424754", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: "pointer", marginLeft: "auto" }}
              >
                ← Dashboard
              </button>
            </div>
          </form>

          {status && (
            <div style={{
              marginTop: 20, padding: "14px 18px", borderRadius: 8, fontSize: 13, fontWeight: 500,
              background: status.ok ? "#f0fdf4" : "#fff1f2",
              color: status.ok ? "#006947" : "#ba1a1a",
              display: "flex", alignItems: "center", gap: 10,
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                {status.ok ? "check_circle" : "error"}
              </span>
              {status.msg}
            </div>
          )}
        </div>
      </div>
    </IndustrialLayout>
  );
}
