"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import IndustrialLayout from "../../components/IndustrialLayout";

const DEPARTMENTS = ["All Departments", "Sorting", "Shredding", "Processing", "Packaging", "Logistics", "Quality Control", "Administration"];

interface Record {
  employeeId: string;
  employeeName: string;
  department: string;
  daysPresent: number;
  workingDays: number;
  attendanceRate: number;
  _id?: string;
}

export default function ViewAttendancePage() {
  const router = useRouter();
  const [records, setRecords] = useState<Record[]>([]);
  const [filtered, setFiltered] = useState<Record[]>([]);
  const [loading, setLoading] = useState(true);
  const [department, setDepartment] = useState("All Departments");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const perPage = 10;
  const userType = "manager";

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    let result = records;
    if (department !== "All Departments") result = result.filter(r => r.department === department);
    if (search) result = result.filter(r => r.employeeName.toLowerCase().includes(search.toLowerCase()) || r.employeeId.toLowerCase().includes(search.toLowerCase()));
    setFiltered(result);
    setPage(1);
  }, [records, department, search]);

  const loadData = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/api/attendance/summary", {
        headers: { "X-User-Type": "manager" },
      });
      const data = await res.json();
      if (data.success) setRecords(data.summary || []);
    } catch {}
    setLoading(false);
  };

  const exportCSV = () => {
    const header = "Employee ID,Full Name,Department,Days Present,Working Days,Attendance %\n";
    const rows = filtered.map(r => `${r.employeeId},${r.employeeName},${r.department},${r.daysPresent},${r.workingDays},${r.attendanceRate}%`).join("\n");
    const blob = new Blob([header + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "attendance_report.csv"; a.click();
  };

  const pageContent = filtered.slice((page - 1) * perPage, page * perPage);
  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));

  const getRateColor = (rate: number) => rate >= 90 ? "#006947" : rate >= 75 ? "#b45309" : "#ba1a1a";

  return (
    <IndustrialLayout activeNav="reports" pageTitle="Attendance Reports" userType={userType as any}>
      <div style={{ padding: "32px 32px" }}>

        {/* Filters */}
        <div style={{ background: "#fff", borderRadius: 12, padding: "20px 24px", boxShadow: "0 1px 4px rgba(23,28,31,0.06)", marginBottom: 24 }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 16, alignItems: "flex-end" }}>
            <div style={{ flex: 1, minWidth: 200 }}>
              <label style={{ fontSize: 10, fontWeight: 700, color: "#424754", letterSpacing: "0.1em", textTransform: "uppercase", display: "block", marginBottom: 8 }}>Search Employee</label>
              <div style={{ position: "relative" }}>
                <span className="material-symbols-outlined" style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", fontSize: 18, color: "#94a3b8" }}>search</span>
                <input
                  value={search} onChange={e => setSearch(e.target.value)}
                  placeholder="Name or Employee ID..."
                  style={{ width: "100%", padding: "10px 16px 10px 40px", background: "#f0f4f7", border: "none", borderRadius: 8, fontSize: 13, color: "#171c1f", outline: "none", fontFamily: "'Inter', sans-serif" }}
                />
              </div>
            </div>
            <div style={{ minWidth: 200 }}>
              <label style={{ fontSize: 10, fontWeight: 700, color: "#424754", letterSpacing: "0.1em", textTransform: "uppercase", display: "block", marginBottom: 8 }}>Department</label>
              <div style={{ position: "relative" }}>
                <select value={department} onChange={e => setDepartment(e.target.value)}
                  style={{ minWidth: 200, padding: "10px 36px 10px 14px", background: "#f0f4f7", border: "none", borderRadius: 8, fontSize: 13, color: "#171c1f", appearance: "none", cursor: "pointer", fontFamily: "'Inter', sans-serif" }}>
                  {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
                </select>
                <span className="material-symbols-outlined" style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", fontSize: 18, color: "#94a3b8", pointerEvents: "none" }}>expand_more</span>
              </div>
            </div>
            <button onClick={loadData}
              style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 24px", background: "#f0f4f7", border: "none", borderRadius: 8, fontSize: 12, fontWeight: 700, color: "#424754", cursor: "pointer", height: 42, transition: "background 0.2s" }}
              onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "#0058be"}
              onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "#f0f4f7"}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>filter_list</span>
              Refresh
            </button>
          </div>
        </div>

        {/* Table */}
        <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 4px rgba(23,28,31,0.06)", overflow: "hidden" }}>
          {/* Table Header */}
          <div style={{ padding: "16px 24px", background: "#f0f4f7", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ fontSize: 12, fontWeight: 700, color: "#171c1f", textTransform: "uppercase", letterSpacing: "0.1em" }}>Employee Attendance Record</h3>
            <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, fontWeight: 600, color: "#64748b" }}>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#006947", display: "inline-block" }} />
              {filtered.length} Employees
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #f0f4f7" }}>
                  {["Employee ID", "Full Name", "Department", "Days Present", "Attendance %", "Action"].map(h => (
                    <th key={h} style={{ padding: "14px 24px", textAlign: "left", fontSize: 10, fontWeight: 800, color: "#424754", textTransform: "uppercase", letterSpacing: "0.08em" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={6} style={{ padding: 48, textAlign: "center", color: "#94a3b8", fontSize: 13 }}>Loading attendance records...</td></tr>
                ) : pageContent.length === 0 ? (
                  <tr><td colSpan={6} style={{ padding: 48, textAlign: "center", color: "#94a3b8", fontSize: 13 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 40, display: "block", marginBottom: 8 }}>search_off</span>
                    No records found
                  </td></tr>
                ) : pageContent.map((r, i) => {
                  const rate = r.attendanceRate || (r.workingDays ? Math.round(r.daysPresent / r.workingDays * 100) : 0);
                  const rateColor = getRateColor(rate);
                  return (
                    <tr key={i} style={{ borderBottom: "1px solid #f6fafd", transition: "background 0.15s", cursor: "default" }}
                      onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "#f6fafd"}
                      onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}
                    >
                      <td style={{ padding: "14px 24px", fontSize: 12, fontWeight: 700, color: "#0058be", letterSpacing: "0.04em" }}>{r.employeeId}</td>
                      <td style={{ padding: "14px 24px", fontSize: 13, fontWeight: 500, color: "#171c1f" }}>{r.employeeName}</td>
                      <td style={{ padding: "14px 24px" }}>
                        <span style={{ background: "#f0f4f7", fontSize: 10, fontWeight: 700, padding: "3px 8px", borderRadius: 4, color: "#424754", textTransform: "uppercase", letterSpacing: "0.04em" }}>{r.department}</span>
                      </td>
                      <td style={{ padding: "14px 24px", fontSize: 13, fontWeight: 600, color: "#171c1f" }}>{r.daysPresent} / {r.workingDays || "—"}</td>
                      <td style={{ padding: "14px 24px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <div style={{ width: 64, height: 4, background: "#f0f4f7", borderRadius: 2, overflow: "hidden" }}>
                            <div style={{ height: "100%", width: `${Math.min(100, rate)}%`, background: rateColor, borderRadius: 2 }} />
                          </div>
                          <span style={{ fontSize: 12, fontWeight: 700, color: rateColor }}>{rate}%</span>
                        </div>
                      </td>
                      <td style={{ padding: "14px 24px" }}>
                        <button title="View Details"
                          style={{ background: "none", border: "none", cursor: "pointer", color: "#94a3b8", transition: "color 0.15s" }}
                          onMouseEnter={e => (e.currentTarget as HTMLElement).style.color = "#0058be"}
                          onMouseLeave={e => (e.currentTarget as HTMLElement).style.color = "#94a3b8"}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: 20 }}>visibility</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination + Export */}
          <div style={{ padding: "16px 24px", borderTop: "1px solid #f0f4f7", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={exportCSV} style={{
                display: "flex", alignItems: "center", gap: 6, padding: "8px 16px",
                background: "#f0f4f7", border: "none", borderRadius: 6,
                fontSize: 11, fontWeight: 700, color: "#424754", cursor: "pointer",
                textTransform: "uppercase", letterSpacing: "0.08em",
              }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>description</span>
                Export CSV
              </button>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <span style={{ fontSize: 12, color: "#64748b", fontWeight: 500 }}>Page {page} of {totalPages}</span>
              <div style={{ display: "flex", gap: 4 }}>
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                  style={{ width: 32, height: 32, borderRadius: 6, border: "1px solid #f0f4f7", display: "flex", alignItems: "center", justifyContent: "center", cursor: page === 1 ? "not-allowed" : "pointer", background: "#fff", color: page === 1 ? "#e2e8f0" : "#424754" }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>chevron_left</span>
                </button>
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                  style={{ width: 32, height: 32, borderRadius: 6, border: "1px solid #f0f4f7", display: "flex", alignItems: "center", justifyContent: "center", cursor: page === totalPages ? "not-allowed" : "pointer", background: "#fff", color: page === totalPages ? "#e2e8f0" : "#424754" }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 18 }}>chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </IndustrialLayout>
  );
}
