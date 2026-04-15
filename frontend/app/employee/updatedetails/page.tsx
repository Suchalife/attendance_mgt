"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import IndustrialLayout from "../../components/IndustrialLayout";

const DEPARTMENTS = ["Sorting", "Shredding", "Processing", "Packaging", "Logistics", "Quality Control", "Administration"];
const BRANCHES = ["CHN-01 (Chennai)", "BLR-02 (Bangalore)", "HYD-03 (Hyderabad)", "MUM-04 (Mumbai)"];

interface Employee {
  _id?: string;
  employeeId: string;
  employeeName: string;
  email: string;
  department: string;
  role: string;
  branch: string;
  phoneNumber: string;
}

export default function UpdateDetailsPage() {
  const router = useRouter();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [selected, setSelected] = useState<Employee | null>(null);
  const [form, setForm] = useState<Partial<Employee>>({});
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const userType = "manager";

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/employees", {
        headers: { "X-User-Type": "manager" },
      });
      const data = await res.json();
      if (data.success) setEmployees(data.employees || []);
    } catch {}
  };

  const selectEmployee = (emp: Employee) => { setSelected(emp); setForm({ ...emp }); setStatus(""); setDeleteConfirm(false); };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected) return;
    setLoading(true);
    setStatus("Updating...");
    try {
      const res = await fetch(`http://127.0.0.1:5000/api/employees/${selected.employeeId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", "X-User-Type": "manager" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (data.success) {
        setStatus("Employee details updated successfully");
        loadEmployees();
        setSelected({ ...selected, ...form as Employee });
      } else { setStatus(data.error || "Update failed"); }
    } catch { setStatus("Connection error"); }
    setLoading(false);
  };

  const handleDelete = async () => {
    if (!selected || !deleteConfirm) { setDeleteConfirm(true); return; }
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:5000/api/employees/${selected.employeeId}`, {
        method: "DELETE",
        headers: { "X-User-Type": "manager" },
      });
      const data = await res.json();
      if (data.success) {
        setSelected(null); setForm({});
        loadEmployees();
        setStatus("Employee removed");
      } else { setStatus(data.error || "Delete failed"); }
    } catch { setStatus("Connection error"); }
    setLoading(false);
    setDeleteConfirm(false);
  };

  const filtered = employees.filter(e =>
    e.employeeName?.toLowerCase().includes(search.toLowerCase()) ||
    e.employeeId?.toLowerCase().includes(search.toLowerCase()) ||
    e.department?.toLowerCase().includes(search.toLowerCase())
  );

  const inputStyle = { width: "100%", padding: "11px 14px", background: "#f0f4f7", border: "none", borderRadius: 8, fontSize: 13, color: "#171c1f", outline: "none", fontFamily: "'Inter', sans-serif" };
  const labelStyle = { fontSize: 10, fontWeight: 700, color: "#424754", letterSpacing: "0.1em", textTransform: "uppercase" as const, display: "block" as const, marginBottom: 6 };

  return (
    <IndustrialLayout activeNav="registration" pageTitle="Employee Management" userType={userType as any}>
      <div style={{ padding: "32px 32px", display: "grid", gridTemplateColumns: "320px 1fr", gap: 24, height: "calc(100vh - 64px)" }}>

        {/* Left: Employee List */}
        <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 4px rgba(23,28,31,0.06)", display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", borderBottom: "1px solid #f0f4f7" }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, color: "#171c1f", marginBottom: 12 }}>Employee Directory</h3>
            <div style={{ position: "relative" }}>
              <span className="material-symbols-outlined" style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", fontSize: 16, color: "#94a3b8" }}>search</span>
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search employees..."
                style={{ width: "100%", padding: "8px 12px 8px 34px", background: "#f0f4f7", border: "none", borderRadius: 8, fontSize: 12, outline: "none", fontFamily: "'Inter', sans-serif" }} />
            </div>
          </div>
          <div style={{ flex: 1, overflowY: "auto" }}>
            {filtered.length === 0 ? (
              <div style={{ padding: 24, textAlign: "center", color: "#94a3b8", fontSize: 12 }}>No employees found</div>
            ) : filtered.map((emp, i) => (
              <div key={i} onClick={() => selectEmployee(emp)}
                style={{
                  padding: "12px 20px", cursor: "pointer", borderBottom: "1px solid #f6fafd",
                  background: selected?.employeeId === emp.employeeId ? "#eff6ff" : "transparent",
                  borderLeft: selected?.employeeId === emp.employeeId ? "3px solid #0058be" : "3px solid transparent",
                  transition: "all 0.15s",
                }}
                onMouseEnter={e => { if (selected?.employeeId !== emp.employeeId) (e.currentTarget as HTMLElement).style.background = "#f6fafd"; }}
                onMouseLeave={e => { if (selected?.employeeId !== emp.employeeId) (e.currentTarget as HTMLElement).style.background = "transparent"; }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 32, height: 32, borderRadius: 8, background: "#f0f4f7", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16, color: "#424754" }}>person</span>
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <p style={{ fontSize: 12, fontWeight: 700, color: "#171c1f", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{emp.employeeName}</p>
                    <p style={{ fontSize: 10, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.04em" }}>{emp.employeeId} · {emp.department}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div style={{ padding: "12px 20px", borderTop: "1px solid #f0f4f7", fontSize: 11, color: "#64748b", fontWeight: 600 }}>
            {filtered.length} / {employees.length} employees
          </div>
        </div>

        {/* Right: Edit Form */}
        <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 4px rgba(23,28,31,0.06)", overflow: "auto" }}>
          {!selected ? (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", color: "#94a3b8" }}>
              <span className="material-symbols-outlined" style={{ fontSize: 56 }}>manage_accounts</span>
              <p style={{ fontSize: 14, fontWeight: 600, marginTop: 12 }}>Select an employee to edit</p>
              <p style={{ fontSize: 12, marginTop: 4 }}>Choose from the directory on the left</p>
            </div>
          ) : (
            <div style={{ padding: 32 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 800, color: "#171c1f" }}>{selected.employeeName}</h2>
                  <p style={{ fontSize: 13, color: "#64748b", marginTop: 2 }}>{selected.employeeId} · {selected.department}</p>
                </div>
                {userType === "manager" && (
                  <button onClick={handleDelete}
                    style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 16px", background: deleteConfirm ? "#ba1a1a" : "#ffdad6", color: deleteConfirm ? "#fff" : "#ba1a1a", border: "none", borderRadius: 8, fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>delete</span>
                    {deleteConfirm ? "Confirm Delete" : "Remove Employee"}
                  </button>
                )}
              </div>

              <form onSubmit={handleUpdate}>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 20, marginBottom: 28 }}>
                  <div>
                    <label style={labelStyle}>Employee ID</label>
                    <input value={form.employeeId || ""} disabled
                      style={{ ...inputStyle, background: "#f6fafd", color: "#94a3b8", cursor: "not-allowed" }} />
                  </div>
                  <div>
                    <label style={labelStyle}>Full Name</label>
                    <input value={form.employeeName || ""} onChange={e => setForm(p => ({ ...p, employeeName: e.target.value }))}
                      style={inputStyle}
                      onFocus={e => { e.currentTarget.style.background = "#fff"; e.currentTarget.style.boxShadow = "0 2px 0 0 #0058be"; }}
                      onBlur={e => { e.currentTarget.style.background = "#f0f4f7"; e.currentTarget.style.boxShadow = "none"; }}
                    />
                  </div>
                  <div>
                    <label style={labelStyle}>Email</label>
                    <input type="email" value={form.email || ""} onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                      style={inputStyle}
                      onFocus={e => { e.currentTarget.style.background = "#fff"; e.currentTarget.style.boxShadow = "0 2px 0 0 #0058be"; }}
                      onBlur={e => { e.currentTarget.style.background = "#f0f4f7"; e.currentTarget.style.boxShadow = "none"; }}
                    />
                  </div>
                  <div>
                    <label style={labelStyle}>Role / Designation</label>
                    <input value={form.role || ""} onChange={e => setForm(p => ({ ...p, role: e.target.value }))}
                      style={inputStyle}
                      onFocus={e => { e.currentTarget.style.background = "#fff"; e.currentTarget.style.boxShadow = "0 2px 0 0 #0058be"; }}
                      onBlur={e => { e.currentTarget.style.background = "#f0f4f7"; e.currentTarget.style.boxShadow = "none"; }}
                    />
                  </div>
                  <div>
                    <label style={labelStyle}>Department</label>
                    <div style={{ position: "relative" }}>
                      <select value={form.department || ""} onChange={e => setForm(p => ({ ...p, department: e.target.value }))}
                        style={{ ...inputStyle, paddingRight: 36, appearance: "none", cursor: "pointer" }}>
                        {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
                      </select>
                      <span className="material-symbols-outlined" style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", fontSize: 16, color: "#94a3b8", pointerEvents: "none" }}>expand_more</span>
                    </div>
                  </div>
                  <div>
                    <label style={labelStyle}>Branch</label>
                    <div style={{ position: "relative" }}>
                      <select value={form.branch || ""} onChange={e => setForm(p => ({ ...p, branch: e.target.value }))}
                        style={{ ...inputStyle, paddingRight: 36, appearance: "none", cursor: "pointer" }}>
                        {BRANCHES.map(b => <option key={b}>{b}</option>)}
                      </select>
                      <span className="material-symbols-outlined" style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", fontSize: 16, color: "#94a3b8", pointerEvents: "none" }}>expand_more</span>
                    </div>
                  </div>
                  <div>
                    <label style={labelStyle}>Phone Number</label>
                    <input type="tel" value={form.phoneNumber || ""} onChange={e => setForm(p => ({ ...p, phoneNumber: e.target.value }))}
                      placeholder="+91 99999 99999"
                      style={inputStyle}
                      onFocus={e => { e.currentTarget.style.background = "#fff"; e.currentTarget.style.boxShadow = "0 2px 0 0 #0058be"; }}
                      onBlur={e => { e.currentTarget.style.background = "#f0f4f7"; e.currentTarget.style.boxShadow = "none"; }}
                    />
                  </div>
                </div>

                <div style={{ display: "flex", gap: 12 }}>
                  <button type="submit" disabled={loading}
                    style={{ padding: "12px 32px", background: loading ? "#94a3b8" : "#0058be", color: "#fff", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer" }}>
                    {loading ? "Saving..." : "Save Changes"}
                  </button>
                  <button type="button" onClick={() => setForm({ ...selected })}
                    style={{ padding: "12px 32px", background: "#f0f4f7", color: "#424754", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                    Discard
                  </button>
                  {userType === "manager" && (
                    <button type="button" onClick={() => router.push("/employee/registrationform")}
                      style={{ padding: "12px 32px", background: "#f0fdf4", color: "#006947", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: "pointer", marginLeft: "auto" }}>
                      Re-enroll Biometrics
                    </button>
                  )}
                </div>
              </form>

              {status && (
                <div style={{ marginTop: 20, padding: "12px 16px", borderRadius: 8, fontSize: 13, background: status.includes("success") || status.includes("updated") ? "#f0fdf4" : "#fff1f2", color: status.includes("success") || status.includes("updated") ? "#006947" : "#ba1a1a" }}>
                  {status}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </IndustrialLayout>
  );
}