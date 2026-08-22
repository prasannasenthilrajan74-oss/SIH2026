const API_BASE = "http://localhost:8000/api";

function getHeaders() {
  const token = localStorage.getItem("mplads_token");
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  setToken(token: string) {
    localStorage.setItem("mplads_token", token);
  },

  clearToken() {
    localStorage.removeItem("mplads_token");
  },

  async login(username: string, password: string): Promise<string> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Authentication failed");
    }
    const data = await res.json();
    this.setToken(data.access_token);
    return data.access_token;
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error("Session expired");
    return res.json();
  },

  async getUsers() {
    const res = await fetch(`${API_BASE}/auth/users`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async getOverview() {
    const res = await fetch(`${API_BASE}/dashboard/overview`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
    return res.json();
  },

  async getHeatmap() {
    const res = await fetch(`${API_BASE}/dashboard/heatmap`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async getWorks(filters: Record<string, any> = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.append(k, String(v));
    });
    const res = await fetch(`${API_BASE}/works/?${params.toString()}`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async getWorkDetails(id: string) {
    const res = await fetch(`${API_BASE}/works/${id}`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error("Project not found");
    return res.json();
  },

  async getWorkPayments(id: string) {
    const res = await fetch(`${API_BASE}/works/${id}/payments`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async getWorkDocuments(id: string) {
    const res = await fetch(`${API_BASE}/works/${id}/documents`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async getWorkSimilar(id: string) {
    const res = await fetch(`${API_BASE}/works/${id}/similar`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async getRules() {
    const res = await fetch(`${API_BASE}/rules/`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async updateRule(id: string, body: Record<string, any>) {
    const res = await fetch(`${API_BASE}/rules/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getHeaders()
      },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error("Failed to update rule");
    return res.json();
  },

  async triggerRulesEvaluation() {
    const res = await fetch(`${API_BASE}/rules/evaluate`, {
      method: "POST",
      headers: getHeaders()
    });
    return res.json();
  },

  async getAlerts(filters: Record<string, any> = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.append(k, String(v));
    });
    const res = await fetch(`${API_BASE}/alerts/?${params.toString()}`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async updateAlertStatus(id: number, status: string) {
    const res = await fetch(`${API_BASE}/alerts/${id}/status`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getHeaders()
      },
      body: JSON.stringify({ status })
    });
    return res.json();
  },

  async getInvestigations(status?: string) {
    const url = status ? `${API_BASE}/investigations/?status=${status}` : `${API_BASE}/investigations/`;
    const res = await fetch(url, {
      headers: getHeaders()
    });
    return res.json();
  },

  async createInvestigation(workId: string, priority: string = "MEDIUM", assignedTo?: number) {
    const res = await fetch(`${API_BASE}/investigations/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getHeaders()
      },
      body: JSON.stringify({ work_id: workId, priority, assigned_to: assignedTo })
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Failed to initiate case");
    }
    return res.json();
  },

  async updateInvestigation(id: number, body: Record<string, any>) {
    const res = await fetch(`${API_BASE}/investigations/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...getHeaders()
      },
      body: JSON.stringify(body)
    });
    return res.json();
  },

  async getAgencies() {
    const res = await fetch(`${API_BASE}/agencies/`, {
      headers: getHeaders()
    });
    return res.json();
  },

  async uploadDocument(file: File, documentType: string, workId?: string) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", documentType);
    if (workId) formData.append("work_id", workId);

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      headers: getHeaders(),
      body: formData
    });
    if (!res.ok) throw new Error("Document upload failed");
    return res.json();
  },

  async queryAI(query: string) {
    const res = await fetch(`${API_BASE}/ai/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getHeaders()
      },
      body: JSON.stringify({ query })
    });
    if (!res.ok) throw new Error("AI query failed");
    return res.json();
  },

  async downloadDatabaseBackup() {
    const res = await fetch(`${API_BASE}/system/download-db`, {
      headers: getHeaders()
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Failed to download backup");
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mplads_sentinel_backup.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
};
