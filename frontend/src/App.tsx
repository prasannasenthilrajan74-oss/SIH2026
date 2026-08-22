import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldAlert, ShieldCheck, Activity, Layers, FileText, 
  Settings, UserCheck, MessageSquare, AlertTriangle, 
  MapPin, CheckCircle, Search, LogOut, ArrowRight, 
  TrendingUp, IndianRupee, Clock, Briefcase, FileSearch, 
  HelpCircle, ChevronRight, RefreshCw, Send, PlusCircle
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  Legend, ResponsiveContainer, PieChart, Pie, Cell, 
  LineChart, Line 
} from 'recharts';
import L from 'leaflet';
import { api } from './services/api';

// --- TYPES ---
interface User {
  id: number;
  username: string;
  role_name: string;
  state?: string;
  district?: string;
  constituency?: string;
}

interface RiskScores {
  overall_score: number;
  financial_risk: number;
  delay_risk: number;
  cost_risk: number;
  duplicate_risk: number;
  payment_risk: number;
  compliance_risk: number;
  document_risk: number;
  geographic_risk: number;
  factors: string[];
}

interface Work {
  id: string;
  description: string;
  category: string;
  work_type: string;
  mp_name: string;
  constituency: string;
  state_code?: string;
  district_code?: string;
  block?: string;
  village?: string;
  latitude?: number;
  longitude?: number;
  recommendation_date?: string;
  sanction_date?: string;
  expected_completion_date?: string;
  actual_completion_date?: string;
  status: string;
  implementing_agency_id?: number;
  estimated_cost: number;
  sanctioned_amount: number;
  expenditure: number;
  physical_progress: number;
  financial_progress: number;
  implementing_agency_name?: string;
  risk_scores?: RiskScores;
}

interface Alert {
  id: number;
  work_id: string;
  alert_type: string;
  severity: string;
  score: number;
  reason: string;
  evidence?: any;
  status: string;
  created_at: string;
  work_description?: string;
}

interface Rule {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: string;
  condition_expression: string;
  threshold: number;
  enabled: boolean;
}

interface InvestigationAction {
  id: number;
  performed_by_name: string;
  action: string;
  notes?: string;
  timestamp: string;
}

interface Investigation {
  id: number;
  work_id: string;
  work_description?: string;
  assigned_to_name?: string;
  assigned_to_id?: number;
  priority: string;
  status: string;
  findings?: string;
  action_taken?: string;
  resolution_state?: string;
  created_at: string;
  resolved_at?: string;
  actions: InvestigationAction[];
}

interface Agency {
  id: number;
  name: string;
  completion_rate: number;
  average_delay_days: number;
  average_cost_deviation: number;
  risk_score: number;
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [usernameInput, setUsernameInput] = useState('admin');
  const [passwordInput, setPasswordInput] = useState('admin123');
  const [loginError, setLoginError] = useState('');
  
  // Navigation
  const [activeTab, setActiveTab] = useState('Overview');
  const [selectedWorkId, setSelectedWorkId] = useState<string | null>(null);
  
  // Global Filters
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [globalSearch, setGlobalSearch] = useState('');
  
  // Chatbot state
  const [chatMinimized, setChatMinimized] = useState(true);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{ sender: 'bot' | 'user'; text: string; sources?: any[] }>>([
    { sender: 'bot', text: 'Hello! I am Sentinel AI. How can I assist you with MPLADS project auditing today?' }
  ]);

  // Auth bootstrap
  useEffect(() => {
    const token = localStorage.getItem("mplads_token");
    if (token) {
      bootstrapSession();
    }
  }, []);

  const bootstrapSession = async () => {
    try {
      const user = await api.getMe();
      setCurrentUser(user);
      setIsAuthenticated(true);
    } catch (e) {
      api.clearToken();
      setIsAuthenticated(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    try {
      await api.login(usernameInput, passwordInput);
      await bootstrapSession();
    } catch (err: any) {
      setLoginError(err.message || "Invalid username or password");
    }
  };

  const handleLogout = () => {
    api.clearToken();
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  if (!isAuthenticated) {
    return (
      <div className="login-screen">
        <form className="login-card" onSubmit={handleLogin}>
          <div className="login-logo">
            <ShieldAlert size={36} className="logo-icon" />
            <h1>MPLADS Sentinel AI</h1>
          </div>
          <div style={{ textAlign: 'center', marginBottom: '20px', color: '#94a3b8', fontSize: '11px', marginTop: '-15px' }}>
            "From Passive Monitoring to Proactive Governance"
          </div>
          
          {loginError && (
            <div style={{ color: 'var(--danger-color)', backgroundColor: 'var(--danger-light)', border: '1px solid #fee2e2', padding: '10px', borderRadius: 'var(--border-radius-md)', marginBottom: '16px', fontSize: '12.5px', fontWeight: '500' }}>
              {loginError}
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Username</label>
            <input 
              type="text" 
              className="form-control" 
              value={usernameInput} 
              onChange={e => setUsernameInput(e.target.value)} 
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="form-control" 
              value={passwordInput} 
              onChange={e => setPasswordInput(e.target.value)} 
              required
            />
          </div>

          <button type="submit" className="btn btn-primary btn-block">
            Access Command Center <ArrowRight size={16} />
          </button>

          <div className="login-demo-helper">
            <p><strong>Demo Roles Quick Credentials:</strong></p>
            <div className="demo-account-list">
              <span className="demo-account-tag" onClick={() => { setUsernameInput('admin'); setPasswordInput('admin123'); }}>Ministry Admin</span>
              <span className="demo-account-tag" onClick={() => { setUsernameInput('state_nodal'); setPasswordInput('state123'); }}>State Nodal</span>
              <span className="demo-account-tag" onClick={() => { setUsernameInput('district_auth'); setPasswordInput('district123'); }}>District Auth</span>
              <span className="demo-account-tag" onClick={() => { setUsernameInput('mp_viewer'); setPasswordInput('mp123'); }}>MP / constituency</span>
              <span className="demo-account-tag" onClick={() => { setUsernameInput('investigator'); setPasswordInput('investigator123'); }}>Investigator</span>
            </div>
          </div>
        </form>
      </div>
    );
  }

  const handleSearchSubmit = (val: string) => {
    setGlobalSearch(val);
    setActiveTab('Risk Monitor');
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <div className="sidebar">
        <div className="sidebar-header">
          <ShieldAlert size={28} className="logo-icon" />
          <div>
            <div className="app-title">Sentinel AI</div>
            <div className="app-tagline">MPLADS Governance</div>
          </div>
        </div>

        <div className="sidebar-nav">
          <div className={`nav-item ${activeTab === 'Overview' ? 'active' : ''}`} onClick={() => { setActiveTab('Overview'); setSelectedWorkId(null); }}>
            <Activity size={16} /> Overview Dashboard
          </div>
          <div className={`nav-item ${activeTab === 'Risk Monitor' ? 'active' : ''}`} onClick={() => { setActiveTab('Risk Monitor'); setSelectedWorkId(null); }}>
            <ShieldAlert size={16} /> Risk Monitor
          </div>
          <div className={`nav-item ${activeTab === 'Documents' ? 'active' : ''}`} onClick={() => { setActiveTab('Documents'); setSelectedWorkId(null); }}>
            <FileText size={16} /> Documents & OCR
          </div>
          <div className={`nav-item ${activeTab === 'Investigations' ? 'active' : ''}`} onClick={() => { setActiveTab('Investigations'); setSelectedWorkId(null); }}>
            <UserCheck size={16} /> Case Investigations
          </div>
          <div className={`nav-item ${activeTab === 'Rules Config' ? 'active' : ''}`} onClick={() => { setActiveTab('Rules Config'); setSelectedWorkId(null); }}>
            <Settings size={16} /> Detection Rules
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="user-profile-info">
            <span className="profile-username">{currentUser?.username}</span>
            <span className="profile-role">{currentUser?.role_name}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Log Out">
            <LogOut size={16} />
          </button>
        </div>
      </div>

      {/* Main Panel */}
      <div className="main-wrapper">
        <div className="top-bar">
          <div className="page-title-container">
            <span className="page-title">{selectedWorkId ? "Project 360 view" : activeTab}</span>
          </div>

          <div className="global-search-container">
            <input 
              type="text" 
              className="search-input" 
              placeholder="Search ID, MP, or description..." 
              onKeyDown={e => {
                if (e.key === 'Enter') handleSearchSubmit((e.target as HTMLInputElement).value);
              }}
            />
            <Search size={14} className="search-icon" />
          </div>
        </div>

        {/* Global filter bar */}
        {!selectedWorkId && activeTab !== 'Rules Config' && activeTab !== 'Documents' && (
          <div className="global-filter-bar">
            <span style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Scope filters:</span>
            {currentUser?.role_name === 'Ministry Administrator' && (
              <select className="filter-select" value={selectedState} onChange={e => { setSelectedState(e.target.value); setSelectedDistrict(''); }}>
                <option value="">All States</option>
                <option value="DL">Delhi</option>
                <option value="TN">Tamil Nadu</option>
                <option value="MH">Maharashtra</option>
                <option value="KA">Karnataka</option>
              </select>
            )}

            {(currentUser?.role_name === 'Ministry Administrator' || currentUser?.role_name === 'State Nodal Authority') && (
              <select className="filter-select" value={selectedDistrict} onChange={e => setSelectedDistrict(e.target.value)}>
                <option value="">All Districts</option>
                {(!selectedState || selectedState === 'TN') && <option value="CH">Chennai</option>}
                {(!selectedState || selectedState === 'TN') && <option value="CO">Coimbatore</option>}
                {(!selectedState || selectedState === 'DL') && <option value="CD">Central Delhi</option>}
                {(!selectedState || selectedState === 'DL') && <option value="ND">New Delhi</option>}
                {(!selectedState || selectedState === 'MH') && <option value="MU">Mumbai</option>}
                {(!selectedState || selectedState === 'MH') && <option value="PU">Pune</option>}
                {(!selectedState || selectedState === 'KA') && <option value="BU">Bangalore</option>}
                {(!selectedState || selectedState === 'KA') && <option value="MY">Mysore</option>}
              </select>
            )}

            <select className="filter-select" value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)}>
              <option value="">All Categories</option>
              <option value="Drinking Water">Drinking Water</option>
              <option value="Education">Education</option>
              <option value="Health & Family Welfare">Health & Family Welfare</option>
              <option value="Roads, Pathways and Bridges">Roads & Bridges</option>
              <option value="Sanitation & Public Health">Sanitation & Health</option>
              <option value="Sports Facilities">Sports Facilities</option>
            </select>

            <select className="filter-select" value={selectedStatus} onChange={e => setSelectedStatus(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="Sanctioned">Sanctioned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Completed">Completed</option>
            </select>

            {(selectedState || selectedDistrict || selectedCategory || selectedStatus || globalSearch) && (
              <button 
                style={{ fontSize: '11px', color: 'var(--danger-color)', cursor: 'pointer', background: 'none', border: 'none', fontWeight: '600' }}
                onClick={() => { setSelectedState(''); setSelectedDistrict(''); setSelectedCategory(''); setSelectedStatus(''); setGlobalSearch(''); }}
              >
                Clear filters
              </button>
            )}
          </div>
        )}

        {/* Tab switcher body */}
        <div className="content-body">
          {selectedWorkId ? (
            <Project360Page workId={selectedWorkId} onClose={() => setSelectedWorkId(null)} onNavigateProject={(id) => setSelectedWorkId(id)} />
          ) : activeTab === 'Overview' ? (
            <OverviewTab 
              state={selectedState} 
              district={selectedDistrict} 
              category={selectedCategory} 
              status={selectedStatus} 
              onSelectProject={setSelectedWorkId} 
            />
          ) : activeTab === 'Risk Monitor' ? (
            <RiskMonitorTab 
              state={selectedState} 
              district={selectedDistrict} 
              category={selectedCategory} 
              status={selectedStatus} 
              search={globalSearch}
              onSelectProject={setSelectedWorkId} 
            />
          ) : activeTab === 'Documents' ? (
            <DocumentsTab onSelectProject={setSelectedWorkId} />
          ) : activeTab === 'Investigations' ? (
            <InvestigationsTab onSelectProject={setSelectedWorkId} currentUser={currentUser} />
          ) : activeTab === 'Rules Config' ? (
            <RulesTab currentUser={currentUser} />
          ) : null}
        </div>
      </div>

      {/* Floating chatbot widget */}
      <ChatbotWidget 
        minimized={chatMinimized} 
        setMinimized={setChatMinimized} 
        input={chatInput} 
        setInput={setChatInput} 
        messages={chatMessages} 
        setMessages={setChatMessages} 
        onSelectProject={setSelectedWorkId}
      />
    </div>
  );
}

// --- OVERVIEW TAB COMPONENT ---
function OverviewTab({ state, district, category, status, onSelectProject }: any) {
  const [metrics, setMetrics] = useState<any>(null);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<L.Map | null>(null);
  const markerClusterGroup = useRef<L.FeatureGroup | null>(null);

  useEffect(() => {
    fetchMetrics();
    fetchHeatmap();
  }, [state, district, category, status]);

  const fetchMetrics = async () => {
    try {
      const data = await api.getOverview();
      setMetrics(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchHeatmap = async () => {
    try {
      const data = await api.getHeatmap();
      setHeatmapData(data);
    } catch (e) {
      console.error(e);
    }
  };

  // Initialize Map
  useEffect(() => {
    if (!mapRef.current) return;
    
    if (!mapInstance.current) {
      // Standard India coordinates: 20.5937, 78.9629
      mapInstance.current = L.map(mapRef.current, {
        center: [20.5937, 78.9629],
        zoom: 4,
        attributionControl: false
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
      }).addTo(mapInstance.current);

      markerClusterGroup.current = L.featureGroup().addTo(mapInstance.current);
    }

    // Clear previous markers
    const currentCluster = markerClusterGroup.current;
    if (currentCluster) {
      currentCluster.clearLayers();
    }

    // Add markers based on heatmapData
    if (heatmapData.length > 0 && currentCluster && mapInstance.current) {
      let bounds = L.latLngBounds([]);
      let count = 0;

      heatmapData.forEach(w => {
        if (w.latitude && w.longitude) {
          // Color based on risk score
          const score = w.risk_score;
          const color = score >= 85 ? 'var(--danger-color)' : (score >= 70 ? 'var(--warning-color)' : (score >= 45 ? '#f59e0b' : 'var(--success-color)'));
          
          const marker = L.circleMarker([w.latitude, w.longitude], {
            radius: score >= 85 ? 8 : (score >= 70 ? 7 : 5),
            fillColor: color,
            color: '#ffffff',
            weight: 1.5,
            fillOpacity: 0.8
          });

          const popupContent = `
            <div style="font-family: 'Inter', sans-serif; padding: 4px;">
              <strong style="color: var(--primary-color)">${w.work_id}</strong><br/>
              <span style="font-size:12px; color:var(--text-secondary)">${w.description.substring(0,60)}...</span><br/>
              <div style="margin-top:6px; display:flex; align-items:center; justify-content:space-between">
                <span style="padding: 2px 6px; font-size:10px; font-weight:700; border-radius:4px; color:#ffffff; background-color:${color}">RISK SCORE: ${score.toFixed(1)}</span>
                <button onclick="window.dispatchEvent(new CustomEvent('inspect-project', {detail: '${w.work_id}'}))" style="background-color: var(--secondary-color); color:#ffffff; border:none; padding:4px 8px; font-size:10px; font-weight:bold; border-radius:4px; cursor:pointer">Inspect</button>
              </div>
            </div>
          `;

          marker.bindPopup(popupContent);
          currentCluster.addLayer(marker);
          bounds.extend([w.latitude, w.longitude]);
          count++;
        }
      });

      // Fit bounds if we have coordinates
      if (count > 0) {
        mapInstance.current.fitBounds(bounds, { maxZoom: 8, padding: [30, 30] });
      }
    }
  }, [heatmapData]);

  // Handle map popups inspect button
  useEffect(() => {
    const handleInspect = (e: Event) => {
      const customEvent = e as CustomEvent;
      onSelectProject(customEvent.detail);
    };
    window.addEventListener('inspect-project', handleInspect);
    return () => window.removeEventListener('inspect-project', handleInspect);
  }, []);

  if (!metrics) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px' }}><RefreshCw className="animate-spin" /> Fetching platform analytics...</div>;
  }

  // Formatting lakhs/crores
  const formatCost = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    return `₹${(val / 100000).toFixed(1)} Lakh`;
  };

  const COLORS = ['#1d4ed8', '#0284c7', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#6366f1'];

  return (
    <div>
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-card-title">Total Allocated Works</span>
          <span className="stat-card-value">{metrics.total_works}</span>
          <span className="stat-card-subtitle">{metrics.completed_works} Completed | {metrics.ongoing_works} Active</span>
          <div className="stat-card-accent-bar blue"></div>
        </div>

        <div className="stat-card">
          <span className="stat-card-title">Sanctioned Amount</span>
          <span className="stat-card-value">{formatCost(metrics.total_sanctioned_amount)}</span>
          <span className="stat-card-subtitle">Expenditure: {formatCost(metrics.total_expenditure)}</span>
          <div className="stat-card-accent-bar blue"></div>
        </div>

        <div className="stat-card">
          <span className="stat-card-title">Delayed Projects</span>
          <span className="stat-card-value">{metrics.delayed_works}</span>
          <span className="stat-card-subtitle">Exceeding expected deadlines</span>
          <div className="stat-card-accent-bar orange"></div>
        </div>

        <div className="stat-card">
          <span className="stat-card-title">High-Risk Flagged</span>
          <span className="stat-card-value">{metrics.high_risk_works}</span>
          <span className="stat-card-subtitle">
            <span style={{ color: 'var(--danger-color)', fontWeight: 'bold' }}>{metrics.critical_risk_works} Critical</span> priority alerts
          </span>
          <div className="stat-card-accent-bar red"></div>
        </div>
      </div>

      <div className="grid-2-1">
        {/* Map view */}
        <div className="card" style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
          <div className="card-header">
            <span className="card-title"><MapPin size={16} /> Geospatial Risk Analysis Map</span>
            <span className="badge red">Live heatmap</span>
          </div>
          <div className="card-body" style={{ flex: 1, padding: 0, position: 'relative' }}>
            <div ref={mapRef} style={{ width: '100%', height: '100%' }}></div>
          </div>
        </div>

        {/* Risk overview sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="card">
            <div className="card-header">
              <span className="card-title"><ShieldAlert size={16} /> Anomaly Warning Alerts</span>
            </div>
            <div className="card-body" style={{ padding: '16px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--border-radius-md)' }}>
                  <span>Duplicate Candidates</span>
                  <span className="badge red" style={{ fontWeight: 'bold' }}>{metrics.duplicate_alerts}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--border-radius-md)' }}>
                  <span>Excess Cost Outliers</span>
                  <span className="badge orange" style={{ fontWeight: 'bold' }}>{metrics.cost_alerts}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--border-radius-md)' }}>
                  <span>Document Discrepancies</span>
                  <span className="badge orange" style={{ fontWeight: 'bold' }}>{metrics.doc_alerts}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--border-radius-md)' }}>
                  <span>Total Critical Warnings</span>
                  <span className="badge red" style={{ fontWeight: 'bold', backgroundColor: 'var(--danger-color)', color: '#ffffff' }}>{metrics.critical_alerts}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title"><Briefcase size={16} /> Top-Risk Implementing Agencies</span>
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Agency</th>
                      <th>Risk Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.agency_rankings && metrics.agency_rankings.map((a: any, idx: number) => (
                      <tr key={idx}>
                        <td style={{ fontWeight: '500', fontSize: '12px' }}>{a.agency_name.split('(')[0]}</td>
                        <td>
                          <span className={`badge ${a.risk_score >= 60 ? 'red' : 'orange'}`}>{a.risk_score.toFixed(1)}/100</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <span className="card-title"><TrendingUp size={16} /> Category Expense Allocation</span>
          </div>
          <div className="card-body" style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.category_breakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  nameKey="category"
                  label={({ name, percent }) => `${(name || '').substring(0, 15)} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="sanctioned_amount"
                >
                  {metrics.category_breakdown.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCost(Number(value))} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title"><Activity size={16} /> District Risk Scores Ranking</span>
          </div>
          <div className="card-body" style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={metrics.district_rankings}
                margin={{ top: 10, right: 10, left: 10, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="district_name" angle={-15} textAnchor="end" interval={0} style={{ fontSize: '11px' }} />
                <YAxis style={{ fontSize: '11px' }} domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="avg_risk_score" fill="var(--primary-color)" name="Avg Risk Index">
                  {metrics.district_rankings && metrics.district_rankings.map((entry: any, index: number) => {
                    const color = entry.avg_risk_score >= 65 ? 'var(--danger-color)' : 'var(--primary-color)';
                    return <Cell key={`cell-${index}`} fill={color} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- RISK MONITOR TAB (PRIORITY QUEUE) ---
function RiskMonitorTab({ state, district, category, status, search, onSelectProject }: any) {
  const [works, setWorks] = useState<Work[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [riskFilter, setRiskFilter] = useState('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const limit = 15;

  useEffect(() => {
    setPage(0);
    fetchWorks();
  }, [state, district, category, status, riskFilter, search]);

  useEffect(() => {
    fetchWorks();
  }, [page]);

  const fetchWorks = async () => {
    setLoading(true);
    try {
      const res = await api.getWorks({
        state_code: state,
        district_code: district,
        category: category,
        status: status,
        risk_level: riskFilter,
        search: search,
        limit: limit,
        offset: page * limit
      });
      setWorks(res.works);
      setTotalCount(res.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 85) return 'red';
    if (score >= 70) return 'orange';
    if (score >= 45) return 'gray'; // Yellow in system is gold, badge is orange/gray
    return 'green';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 85) return 'CRITICAL';
    if (score >= 70) return 'HIGH';
    if (score >= 45) return 'MEDIUM';
    return 'LOW';
  };

  return (
    <div className="card">
      <div className="card-header" style={{ padding: '12px 20px' }}>
        <span className="card-title"><ShieldAlert size={16} /> Government Auditing & Investigation Priority Queue</span>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select className="filter-select" value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
            <option value="">All Risk Levels</option>
            <option value="CRITICAL">🔴 Critical Risk (85+)</option>
            <option value="HIGH">🟠 High Risk (70+)</option>
            <option value="MEDIUM">🟡 Medium Risk (45+)</option>
            <option value="LOW">🟢 Low Risk (&lt;45)</option>
          </select>
        </div>
      </div>

      <div className="card-body" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '250px' }}><RefreshCw className="animate-spin" /> Fetching projects...</div>
        ) : works.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>No flagged projects match your query filters.</div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Project ID</th>
                  <th>Description</th>
                  <th>Constituency</th>
                  <th style={{ textAlign: 'right' }}>Sanctioned Amt</th>
                  <th style={{ textAlign: 'center' }}>Phys / Fin %</th>
                  <th>ML Anomaly Index</th>
                  <th>Warnings Triggered</th>
                  <th style={{ width: '80px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {works.map(w => {
                  const score = w.risk_scores?.overall_score || 0.0;
                  const factorCount = w.risk_scores?.factors.length || 0;
                  
                  return (
                    <tr key={w.id}>
                      <td style={{ fontWeight: '700', color: 'var(--primary-color)' }}>{w.id}</td>
                      <td>
                        <div style={{ fontWeight: '600', fontSize: '13px' }}>{w.description}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                          Cat: {w.category} | Agency: {w.implementing_agency_name || "N/A"}
                        </div>
                      </td>
                      <td style={{ fontSize: '12px' }}>
                        <div>{w.mp_name}</div>
                        <div style={{ color: 'var(--text-secondary)' }}>{w.constituency}</div>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold' }}>
                        ₹{(w.sanctioned_amount / 100000).toFixed(1)}L
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '12px', fontWeight: '600' }}>{w.physical_progress.toFixed(0)}% / {w.financial_progress.toFixed(0)}%</div>
                        <div style={{ width: '80px', margin: '4px auto 0' }} className="progress-bar-container">
                          <div 
                            className={`progress-bar-fill ${w.physical_progress >= 70 ? 'green' : (w.physical_progress >= 30 ? 'orange' : 'red')}`} 
                            style={{ width: `${w.physical_progress}%` }}
                          />
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${getRiskColor(score)}`} style={{ fontWeight: 'bold', fontSize: '11px' }}>
                          {score.toFixed(1)} ({getRiskLabel(score)})
                        </span>
                      </td>
                      <td>
                        {factorCount > 0 ? (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                            {w.risk_scores?.factors.slice(0, 2).map((f, i) => (
                              <span key={i} style={{ fontSize: '10px', padding: '2px 6px', backgroundColor: '#f1f5f9', border: '1px solid var(--border-color)', borderRadius: '4px', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={f}>
                                {f.split(':')[0]}
                              </span>
                            ))}
                            {factorCount > 2 && <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>+{factorCount - 2} more</span>}
                          </div>
                        ) : (
                          <span style={{ fontSize: '11px', color: 'var(--success-color)' }}>✓ Normal performance</span>
                        )}
                      </td>
                      <td>
                        <button 
                          className="btn btn-secondary" 
                          style={{ padding: '4px 10px', fontSize: '11px' }}
                          onClick={() => onSelectProject(w.id)}
                        >
                          Audit <ChevronRight size={12} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card-header" style={{ padding: '10px 20px', borderTop: '1px solid var(--border-color)', borderBottom: 'none', backgroundColor: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          Showing {page * limit + 1}-{Math.min(totalCount, (page + 1) * limit)} of {totalCount} projects
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-secondary" style={{ padding: '4px 10px' }} disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
          <button className="btn btn-secondary" style={{ padding: '4px 10px' }} disabled={(page + 1) * limit >= totalCount} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}

// --- PROJECT 360 & INVESTIGATION DETAIL PAGE ---
function Project360Page({ workId, onClose, onNavigateProject }: { workId: string, onClose: () => void, onNavigateProject: (id: string) => void }) {
  const [work, setWork] = useState<Work | null>(null);
  const [payments, setPayments] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [duplicates, setDuplicates] = useState<any[]>([]);
  const [backtrackData, setBacktrackData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'risk' | 'backtrack' | 'payments' | 'documents' | 'duplicates' | 'investigation'>('risk');
  const [loading, setLoading] = useState(true);
  
  // Case management states
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [assignedTo, setAssignedTo] = useState<number | ''>('');
  const [priority, setPriority] = useState('MEDIUM');
  const [status, setStatus] = useState('Detected');
  const [findings, setFindings] = useState('');
  const [actionTaken, setActionTaken] = useState('');
  const [resolutionState, setResolutionState] = useState('');
  const [updatingCase, setUpdatingCase] = useState(false);

  // Map elements
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const leafletMap = useRef<L.Map | null>(null);

  useEffect(() => {
    fetchProjectDetails();
  }, [workId]);

  const fetchProjectDetails = async () => {
    setLoading(true);
    try {
      const wDetails = await api.getWorkDetails(workId);
      setWork(wDetails);
      
      const payList = await api.getWorkPayments(workId);
      setPayments(payList);

      const docList = await api.getWorkDocuments(workId);
      setDocuments(docList);

      const dupList = await api.getWorkSimilar(workId);
      setDuplicates(dupList);

      const bData = await api.getWorkControlledBacktrack(workId).catch(() => null);
      setBacktrackData(bData);

      // Fetch case investigation status
      const cases = await api.getInvestigations();
      const projectCase = cases.find((c: any) => c.work_id === workId);
      if (projectCase) {
        setInvestigation(projectCase);
        setAssignedTo(projectCase.assigned_to_id || '');
        setPriority(projectCase.priority);
        setStatus(projectCase.status);
        setFindings(projectCase.findings || '');
        setActionTaken(projectCase.action_taken || '');
        setResolutionState(projectCase.resolution_state || '');
      } else {
        setInvestigation(null);
        setAssignedTo('');
        setPriority('MEDIUM');
        setStatus('Detected');
        setFindings('');
        setActionTaken('');
        setResolutionState('');
      }

      // Fetch officers list for assignment dropdown
      const users = await api.getUsers();
      const officers = users.filter((u: User) => u.role_name === "Investigation Officer" || u.role_name === "District Authority");
      setAllUsers(officers);

    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Map initialization in Project 360
  useEffect(() => {
    if (loading || !work || !mapContainerRef.current) return;

    if (work.latitude && work.longitude) {
      if (!leafletMap.current) {
        leafletMap.current = L.map(mapContainerRef.current, {
          center: [work.latitude, work.longitude],
          zoom: 13,
          attributionControl: false
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(leafletMap.current);

        const score = work.risk_scores?.overall_score || 0.0;
        const color = score >= 85 ? 'var(--danger-color)' : (score >= 70 ? 'var(--warning-color)' : 'var(--secondary-color)');
        
        L.marker([work.latitude, work.longitude]).addTo(leafletMap.current)
          .bindPopup(`<strong>${work.id}</strong><br/>${work.description.substring(0,40)}...`)
          .openPopup();
      } else {
        leafletMap.current.setView([work.latitude, work.longitude], 13);
      }
    }
  }, [loading, work]);

  const handleCreateCase = async () => {
    setUpdatingCase(true);
    try {
      const newCase = await api.createInvestigation(workId, priority, assignedTo ? Number(assignedTo) : undefined);
      setInvestigation(newCase);
      alert("Investigation case opened successfully.");
    } catch (err: any) {
      alert(err.message || "Failed to create case");
    } finally {
      setUpdatingCase(false);
    }
  };

  const handleUpdateCase = async () => {
    if (!investigation) return;
    setUpdatingCase(true);
    try {
      const updated = await api.updateInvestigation(investigation.id, {
        status,
        assigned_to: assignedTo ? Number(assignedTo) : null,
        findings,
        action_taken: actionTaken,
        resolution_state: resolutionState
      });
      setInvestigation(updated);
      alert("Investigation case updated successfully.");
    } catch (err: any) {
      alert(err.message || "Failed to update case");
    } finally {
      setUpdatingCase(false);
    }
  };

  if (loading || !work) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px' }}><RefreshCw className="animate-spin" /> Compiling 360-degree data profile...</div>;
  }

  const score = work.risk_scores?.overall_score || 0.0;
  const isCritical = score >= 70;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <button className="btn btn-secondary" onClick={onClose}>&larr; Back to queue</button>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-secondary" onClick={fetchProjectDetails}><RefreshCw size={14} /> Refresh</button>
          {!investigation && (
            <button className="btn btn-primary" style={{ backgroundColor: 'var(--danger-color)' }} onClick={() => { setActiveTab('investigation'); handleCreateCase(); }}>
              <PlusCircle size={14} /> Open Investigation Case
            </button>
          )}
        </div>
      </div>

      {/* Hero header */}
      <div className="card" style={{ borderLeft: `6px solid ${score >= 85 ? 'var(--danger-color)' : (score >= 70 ? 'var(--warning-color)' : 'var(--success-color)')}` }}>
        <div className="card-body" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <h1 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--primary-color)' }}>{work.id}</h1>
                <span className="badge gray" style={{ fontSize: '10px' }}>{work.status}</span>
              </div>
              <p style={{ fontSize: '15px', fontWeight: '600', marginBottom: '10px' }}>{work.description}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                <span><strong>MP:</strong> {work.mp_name} ({work.constituency})</span>
                <span><strong>District:</strong> {work.district_code}</span>
                <span><strong>Implementing Agency:</strong> {work.implementing_agency_name || 'N/A'}</span>
              </div>
            </div>

            <div className={`risk-indicator-box ${score >= 85 ? 'red' : (score >= 70 ? 'orange' : (score >= 45 ? 'yellow' : 'green'))}`} style={{ flexDirection: 'column', alignItems: 'center', padding: '12px 24px' }}>
              <span style={{ fontSize: '10px', fontWeight: 'bold', textTransform: 'uppercase', opacity: 0.8 }}>OVERALL RISK</span>
              <span style={{ fontSize: '24px', fontWeight: '800' }}>{score.toFixed(1)}/100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Progress metrics row */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-card-title">Sanctioned cost</span>
          <span className="stat-card-value">₹{(work.sanctioned_amount / 100000).toFixed(2)} Lakh</span>
          <span className="stat-card-subtitle">Estimated cost: ₹{(work.estimated_cost / 100000).toFixed(2)}L</span>
          <div className="stat-card-accent-bar blue"></div>
        </div>

        <div className="stat-card">
          <span className="stat-card-title">Actual Expenditure</span>
          <span className="stat-card-value">₹{(work.expenditure / 100000).toFixed(2)} Lakh</span>
          <span className="stat-card-subtitle">Financial progress: {work.financial_progress.toFixed(0)}%</span>
          <div className="stat-card-accent-bar blue"></div>
        </div>

        <div className="stat-card">
          <span className="stat-card-title">Physical Progress</span>
          <span className="stat-card-value">{work.physical_progress.toFixed(0)}%</span>
          <span className="stat-card-subtitle">Work site completion index</span>
          <div className="stat-card-accent-bar green"></div>
        </div>

        <div className="stat-card">
          <span className="stat-card-title">Project duration</span>
          <span className="stat-card-value">
            {work.sanction_date && work.expected_completion_date ? 
              `${Math.round((new Date(work.expected_completion_date).getTime() - new Date(work.sanction_date).getTime()) / (1000 * 3600 * 24 * 30))} months` : 
              'N/A'}
          </span>
          <span className="stat-card-subtitle">Sanction: {work.sanction_date || 'N/A'}</span>
          <div className="stat-card-accent-bar blue"></div>
        </div>
      </div>

      <div className="grid-2-1">
        {/* Detail view tabs */}
        <div>
          <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid var(--border-color)', marginBottom: '16px' }}>
            <button className={`btn ${activeTab === 'risk' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }} onClick={() => setActiveTab('risk')}>
              Risk Analysis & AI Explanations
            </button>
            <button className={`btn ${activeTab === 'backtrack' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }} onClick={() => setActiveTab('backtrack')}>
              Controlled Root-Cause ({backtrackData?.primary_attribution === 'AGENCY_CONCENTRATION' ? 'Agency Risk' : (backtrackData?.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'District Risk' : 'Isolated')})
            </button>
            <button className={`btn ${activeTab === 'payments' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }} onClick={() => setActiveTab('payments')}>
              Payment Audits ({payments.length})
            </button>
            <button className={`btn ${activeTab === 'documents' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }} onClick={() => setActiveTab('documents')}>
              OCR Documents ({documents.length})
            </button>
            <button className={`btn ${activeTab === 'duplicates' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }} onClick={() => setActiveTab('duplicates')}>
              Duplicate Candidates ({duplicates.length})
            </button>
            <button className={`btn ${activeTab === 'investigation' ? 'btn-primary' : 'btn-secondary'}`} style={{ padding: '8px 16px', fontSize: '12px' }} onClick={() => setActiveTab('investigation')}>
              Investigation Case ({investigation ? 'Active' : 'Unassigned'})
            </button>
          </div>

          <div className="card">
            <div className="card-body">
              {/* Tab: Controlled Root Cause Backtracking */}
              {activeTab === 'backtrack' && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--primary-color)' }}>CONTROLLED VARIABLE ROOT-CAUSE ATTRIBUTION</h3>
                    {backtrackData && (
                      <span className={`badge ${backtrackData.primary_attribution === 'AGENCY_CONCENTRATION' ? 'red' : (backtrackData.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'orange' : 'gray')}`} style={{ fontSize: '11px', fontWeight: 'bold' }}>
                        {backtrackData.primary_attribution}
                      </span>
                    )}
                  </div>

                  {!backtrackData ? (
                    <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-secondary)' }}><RefreshCw className="animate-spin" /> Evaluating controlled peer comparisons...</div>
                  ) : (
                    <div>
                      <div style={{ padding: '16px', backgroundColor: backtrackData.primary_attribution === 'AGENCY_CONCENTRATION' ? 'var(--danger-light)' : '#f8fafc', borderLeft: `4px solid ${backtrackData.primary_attribution === 'AGENCY_CONCENTRATION' ? 'var(--danger-color)' : 'var(--secondary-color)'}`, borderRadius: 'var(--border-radius-sm)', marginBottom: '20px' }}>
                        <div style={{ fontWeight: '700', fontSize: '13px', marginBottom: '6px' }}>{backtrackData.summary}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                          This attribution is derived by isolating variables — holding District, Category, and Time Period equal across comparable project peer groups to eliminate environmental confounds.
                        </div>
                      </div>

                      {backtrackData.agency_controlled_analysis && (
                        <div className="card" style={{ marginBottom: '16px', border: '1px solid var(--border-color)' }}>
                          <div className="card-header" style={{ padding: '10px 16px', backgroundColor: '#f1f5f9' }}>
                            <span className="card-title" style={{ fontSize: '12px' }}>Agency Level Controlled Peer Comparison ({backtrackData.agency_controlled_analysis.agency_name})</span>
                          </div>
                          <div className="card-body" style={{ padding: '16px' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '14px' }}>
                              <div style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
                                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>This Agency Rate</div>
                                <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--danger-color)' }}>{backtrackData.agency_controlled_analysis.controlled_comparison?.agency_anomaly_rate}%</div>
                                <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>({backtrackData.agency_controlled_analysis.controlled_comparison?.agency_flagged_count}/{backtrackData.agency_controlled_analysis.controlled_comparison?.agency_total_projects} projects)</div>
                              </div>
                              <div style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
                                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Peer Baseline Rate</div>
                                <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--primary-color)' }}>{backtrackData.agency_controlled_analysis.controlled_comparison?.peer_baseline_rate}%</div>
                                <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>(sample: {backtrackData.agency_controlled_analysis.controlled_comparison?.peer_sample_size} peer projects)</div>
                              </div>
                              <div style={{ backgroundColor: '#ffffff', padding: '12px', borderRadius: '6px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
                                <div style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Controlled Multiplier</div>
                                <div style={{ fontSize: '18px', fontWeight: '800', color: backtrackData.agency_controlled_analysis.controlled_comparison?.multiplier_ratio >= 2.0 ? 'var(--danger-color)' : 'var(--warning-color)' }}>
                                  {backtrackData.agency_controlled_analysis.controlled_comparison?.multiplier_ratio}x
                                </div>
                                <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>vs Controlled Peers</div>
                              </div>
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--text-primary)', marginBottom: '8px' }}>
                              <strong>Attribution Reasoning:</strong> {backtrackData.agency_controlled_analysis.attribution_summary}
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--secondary-color)', fontWeight: '600' }}>
                              <strong>Recommendation:</strong> {backtrackData.agency_controlled_analysis.recommendation}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              {/* Tab 1: Risk Explanations */}
              {activeTab === 'risk' && (
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '12px', color: 'var(--primary-color)' }}>AI RISK EXPLANATION ENGINE</h3>
                  
                  {work.risk_scores?.factors && work.risk_scores.factors.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
                      {work.risk_scores.factors.map((f, i) => {
                        const isCriticalFactor = f.startsWith('CRITICAL') || f.startsWith('RED');
                        const isWarning = f.startsWith('WARNING');
                        return (
                          <div 
                            key={i} 
                            style={{ 
                              padding: '12px', 
                              backgroundColor: isCriticalFactor ? 'var(--danger-light)' : (isWarning ? 'var(--warning-light)' : 'var(--info-light)'),
                              borderLeft: `4px solid ${isCriticalFactor ? 'var(--danger-color)' : (isWarning ? 'var(--warning-color)' : 'var(--info-color)')}`,
                              borderRadius: 'var(--border-radius-sm)',
                              fontSize: '12.5px',
                              fontWeight: '500',
                              color: isCriticalFactor ? 'var(--danger-color)' : (isWarning ? 'var(--warning-color)' : 'var(--primary-color)')
                            }}
                          >
                            {f}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div style={{ padding: '16px', backgroundColor: 'var(--success-light)', color: 'var(--success-color)', borderLeft: '4px solid var(--success-color)', borderRadius: 'var(--border-radius-sm)', marginBottom: '24px', fontWeight: '500' }}>
                      ✓ Analysis complete. No suspicious indicators or compliance discrepancies identified on this project.
                    </div>
                  )}

                  <h3 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '12px', color: 'var(--primary-color)' }}>COMPONENT RISK PROFILE INDEX</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {[
                      { name: 'Financial Progress Mismatch', val: work.risk_scores?.financial_risk || 0 },
                      { name: 'Overdue Delay Indicator', val: work.risk_scores?.delay_risk || 0 },
                      { name: 'Comparative Cost Risk', val: work.risk_scores?.cost_risk || 0 },
                      { name: 'Duplicate Similarity Rating', val: work.risk_scores?.duplicate_risk || 0 },
                      { name: 'Payment Speed & Concentation', val: work.risk_scores?.payment_risk || 0 },
                      { name: 'Document Audit Score', val: work.risk_scores?.document_risk || 0 },
                      { name: 'Geospatial Density Check', val: work.risk_scores?.geographic_risk || 0 }
                    ].map((idx, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
                        <span style={{ fontSize: '12px', flex: '1' }}>{idx.name}</span>
                        <div style={{ width: '120px' }} className="progress-bar-container">
                          <div className={`progress-bar-fill ${idx.val >= 70 ? 'red' : (idx.val >= 40 ? 'orange' : 'green')}`} style={{ width: `${idx.val}%` }}></div>
                        </div>
                        <span style={{ width: '45px', textAlign: 'right', fontWeight: 'bold', fontSize: '12px' }}>{idx.val.toFixed(0)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 2: Payments Audit */}
              {activeTab === 'payments' && (
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '12px', color: 'var(--primary-color)' }}>DISBURSEMENT TIMELINE AUDIT</h3>
                  {payments.length === 0 ? (
                    <div style={{ color: 'var(--text-secondary)', padding: '20px', textAlign: 'center' }}>No payments found in registry for this project.</div>
                  ) : (
                    <div>
                      {/* Interactive payments timeline overlay */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '24px' }}>
                        <div style={{ position: 'absolute', left: '8px', top: '4px', bottom: '4px', width: '2px', backgroundColor: 'var(--border-color)' }}></div>
                        {payments.map((p, idx) => (
                          <div key={p.id} style={{ position: 'relative' }}>
                            <div style={{ position: 'absolute', left: '-20px', top: '4px', width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--secondary-color)', border: '2px solid #ffffff' }}></div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div>
                                <span style={{ fontWeight: '700', color: 'var(--primary-color)' }}>₹{p.amount.toLocaleString()}</span>
                                <span style={{ fontSize: '11px', color: 'var(--text-secondary)', marginLeft: '12px' }}>Type: {p.payment_type || 'Milestone'}</span>
                              </div>
                              <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{p.payment_date}</span>
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Ref: {p.transaction_ref || 'N/A'}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: OCR Documents */}
              {activeTab === 'documents' && (
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '12px', color: 'var(--primary-color)' }}>OCR EXTRACTION CROSS-VALIDATION</h3>
                  {documents.length === 0 ? (
                    <div style={{ color: 'var(--text-secondary)', padding: '20px', textAlign: 'center' }}>No documents uploaded. Go to "Documents & OCR" tab to upload order PDFs.</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {documents.map((d, i) => (
                        <div key={d.id} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--border-radius-md)', padding: '12px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                            <span style={{ fontWeight: 'bold', color: 'var(--primary-color)' }}>{d.file_name}</span>
                            <span className={`badge ${d.consistency_score >= 90 ? 'green' : 'orange'}`}>Consistency: {d.consistency_score?.toFixed(1)}%</span>
                          </div>
                          
                          {/* Extracted fields highlights */}
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '12px', backgroundColor: 'var(--bg-color)', padding: '8px', borderRadius: '4px', marginBottom: '10px' }}>
                            <div><strong>Extracted Work ID:</strong> {d.extracted_data?.work_id || 'Not found'}</div>
                            <div><strong>Extracted Cost:</strong> ₹{d.extracted_data?.sanctioned_amount?.toLocaleString() || 'N/A'}</div>
                            <div><strong>Extracted Date:</strong> {d.extracted_data?.sanction_date || 'N/A'}</div>
                            <div><strong>Extracted Agency:</strong> {d.extracted_data?.agency?.substring(0,30) || 'N/A'}</div>
                          </div>

                          <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                            <strong>Extracted Text snippet:</strong> <em>"{d.ocr_text?.substring(0, 150)}..."</em>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 4: Similar Duplicate candidates */}
              {activeTab === 'duplicates' && (
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '12px', color: 'var(--primary-color)' }}>INTELLIGENT DUPLICATE SEARCH ENGINE</h3>
                  {duplicates.length === 0 ? (
                    <div style={{ color: 'var(--success-color)', padding: '20px', textAlign: 'center', fontWeight: '600' }}>✓ No potential duplicates found in the same district matching descriptions or coordinates.</div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                        The following works have suspiciously similar features (descriptions, proximity coordinates, amounts).
                      </p>
                      {duplicates.map((d, i) => (
                        <div key={i} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--border-radius-md)', padding: '12px', backgroundColor: d.duplicate_probability >= 85 ? 'var(--danger-light)' : 'transparent' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                            <span style={{ fontWeight: '700', color: 'var(--primary-color)', cursor: 'pointer', textDecoration: 'underline' }} onClick={() => onNavigateProject(d.work_id)}>
                              {d.work_id}
                            </span>
                            <span className={`badge ${d.duplicate_probability >= 85 ? 'red' : 'orange'}`}>
                              Match: {d.duplicate_probability.toFixed(0)}%
                            </span>
                          </div>
                          <div style={{ fontWeight: '500', fontSize: '12.5px', marginBottom: '6px' }}>{d.description}</div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                            <span><strong>Proximity:</strong> {d.distance_km} km away</span>
                            <span><strong>Text Match:</strong> {d.text_similarity * 100}%</span>
                            <span><strong>Cost Similarity:</strong> {d.cost_similarity * 100}%</span>
                            <span><strong>MP:</strong> {d.mp_name}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Tab 5: Case Investigation */}
              {activeTab === 'investigation' && (
                <div>
                  <h3 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '12px', color: 'var(--primary-color)' }}>INVESTIGATION CASE MANAGEMENT</h3>
                  
                  {!investigation ? (
                    <div>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '12.5px', marginBottom: '16px' }}>
                        No open case exists for this project. Initiating a case assigns it to an investigator for audit action.
                      </p>
                      <div className="form-group">
                        <label className="form-label">Set Priority Level</label>
                        <select className="form-control" value={priority} onChange={e => setPriority(e.target.value)}>
                          <option value="CRITICAL">🔴 Critical Priority</option>
                          <option value="HIGH">🟠 High Priority</option>
                          <option value="MEDIUM">🟡 Medium Priority</option>
                          <option value="LOW">🟢 Low Priority</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label className="form-label">Assign Investigator / Officer</label>
                        <select className="form-control" value={assignedTo} onChange={e => setAssignedTo(e.target.value ? Number(e.target.value) : '')}>
                          <option value="">Choose Officer...</option>
                          {allUsers.map(u => (
                            <option key={u.id} value={u.id}>{u.username} ({u.role_name})</option>
                          ))}
                        </select>
                      </div>

                      <button className="btn btn-primary" onClick={handleCreateCase} disabled={updatingCase}>
                        {updatingCase ? 'Opening...' : 'Open Case File'}
                      </button>
                    </div>
                  ) : (
                    <div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                        <div className="form-group">
                          <label className="form-label">Investigation Status</label>
                          <select className="form-control" value={status} onChange={e => setStatus(e.target.value)}>
                            <option value="Detected">Detected</option>
                            <option value="Under Review">Under Review</option>
                            <option value="Assigned">Assigned</option>
                            <option value="Evidence Requested">Evidence Requested</option>
                            <option value="Resolved">Resolved</option>
                          </select>
                        </div>
                        
                        <div className="form-group">
                          <label className="form-label">Resolution Outcome (if Resolved)</label>
                          <select className="form-control" value={resolutionState} onChange={e => setResolutionState(e.target.value)}>
                            <option value="">Select Outcome...</option>
                            <option value="False Positive">False Positive (Normal)</option>
                            <option value="Verified Normal">Verified Normal</option>
                            <option value="Corrective Action Required">Corrective Action Required</option>
                            <option value="Escalated">Escalated</option>
                            <option value="Investigation Ongoing">Investigation Ongoing</option>
                          </select>
                        </div>
                      </div>

                      <div className="form-group">
                        <label className="form-label">Reassign Officer</label>
                        <select className="form-control" value={assignedTo} onChange={e => setAssignedTo(e.target.value ? Number(e.target.value) : '')}>
                          <option value="">Unassigned</option>
                          {allUsers.map(u => (
                            <option key={u.id} value={u.id}>{u.username} ({u.role_name})</option>
                          ))}
                        </select>
                      </div>

                      <div className="form-group">
                        <label className="form-label">Investigator Findings Summary</label>
                        <textarea className="form-control" rows={3} value={findings} onChange={e => setFindings(e.target.value)} placeholder="Type findings summary..."></textarea>
                      </div>

                      <div className="form-group">
                        <label className="form-label">Actions Taken / Resolution Notes</label>
                        <textarea className="form-control" rows={3} value={actionTaken} onChange={e => setActionTaken(e.target.value)} placeholder="Describe corrective actions taken..."></textarea>
                      </div>

                      <button className="btn btn-primary" onClick={handleUpdateCase} disabled={updatingCase}>
                        {updatingCase ? 'Saving...' : 'Save Case File'}
                      </button>

                      {/* Audit Log Trail */}
                      <h4 style={{ fontSize: '13px', fontWeight: 'bold', marginTop: '24px', marginBottom: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '6px' }}>CASE AUDIT TRAIL LOG</h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                        {investigation.actions && investigation.actions.map(act => (
                          <div key={act.id} style={{ padding: '6px 10px', backgroundColor: 'var(--bg-color)', borderRadius: '4px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', color: 'var(--primary-color)' }}>
                              <span>{act.action}</span>
                              <span>{new Date(act.timestamp).toLocaleDateString()}</span>
                            </div>
                            <div style={{ color: 'var(--text-secondary)' }}>By: {act.performed_by_name}</div>
                            {act.notes && <div style={{ marginTop: '4px', fontStyle: 'italic' }}>Notes: {act.notes}</div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right column: Map and actions summary */}
        <div>
          <div className="card" style={{ height: '300px', display: 'flex', flexDirection: 'column', marginBottom: '20px' }}>
            <div className="card-header">
              <span className="card-title"><MapPin size={16} /> GIS Project Site Proximity</span>
            </div>
            <div className="card-body" style={{ flex: 1, padding: 0 }}>
              {work.latitude && work.longitude ? (
                <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }}></div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)', padding: '20px', textAlign: 'center', fontSize: '12px' }}>
                  No geolocation coordinates provided for this work. Geographic risk cannot be evaluated.
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title"><CheckCircle size={16} /> Audit Status Checklist</span>
            </div>
            <div className="card-body" style={{ padding: '16px', fontSize: '12.5px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input type="checkbox" checked={payments.length > 0} readOnly />
                  <span>Payments Disbursed: {payments.length} txn</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input type="checkbox" checked={documents.length > 0} readOnly />
                  <span>Sanction PDF uploaded: {documents.length > 0 ? 'Yes' : 'No'}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input type="checkbox" checked={duplicates.length === 0} readOnly />
                  <span>Duplicate Checks: {duplicates.length > 0 ? 'Flagged' : 'Clear'}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input type="checkbox" checked={work.latitude !== null} readOnly />
                  <span>GIS Coordinates Registered</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- DOCUMENTS & OCR UPLOAD TAB ---
function DocumentsTab({ onSelectProject }: any) {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('Sanction Order');
  const [workIdInput, setWorkIdInput] = useState('');
  const [uploading, setUploading] = useState(false);
  const [recentDocs, setRecentDocs] = useState<any[]>([]);
  const [extractedData, setExtractedData] = useState<any | null>(null);

  useEffect(() => {
    fetchRecentDocs();
  }, []);

  const fetchRecentDocs = async () => {
    try {
      const cases = await api.getOverview(); // quick list fallback
      // Since backend doesn't have a direct documents query endpoint without work IDs,
      // we can fetch works that have documents or handle it.
      // For demo purposes, we will query a few works' documents or list them if we store globally.
      // Let's call works API and get their documents.
      const res = await api.getWorks({ limit: 10 });
      const docs: any[] = [];
      for (const w of res.works) {
        const wDocs = await api.getWorkDocuments(w.id);
        wDocs.forEach((d: any) => docs.push({ ...d, work_desc: w.description }));
      }
      docs.sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime());
      setRecentDocs(docs);
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a PDF document first.");
      return;
    }
    setUploading(true);
    setExtractedData(null);
    try {
      const res = await api.uploadDocument(file, docType, workIdInput || undefined);
      setExtractedData(res);
      alert("Document uploaded and processed successfully.");
      fetchRecentDocs();
    } catch (err: any) {
      alert(err.message || "Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="grid-2-1">
      <div>
        <form className="card" onSubmit={handleUpload}>
          <div className="card-header">
            <span className="card-title"><PlusCircle size={16} /> Upload Project Sanction Orders & Estimates</span>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label className="form-label">Document Category</label>
              <select className="form-control" value={docType} onChange={e => setDocType(e.target.value)}>
                <option value="Sanction Order">Sanction Order</option>
                <option value="Administrative Approval">Administrative Approval</option>
                <option value="Technical Estimate">Technical Estimate</option>
                <option value="Completion Certificate">Completion Certificate</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Link Project ID (Optional - Auto extracted if empty)</label>
              <input type="text" className="form-control" placeholder="e.g. MPLADS-2026-0005" value={workIdInput} onChange={e => setWorkIdInput(e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Select Sanction PDF</label>
              <input type="file" className="form-control" accept=".pdf" onChange={handleFileChange} required />
            </div>

            <button type="submit" className="btn btn-primary" disabled={uploading}>
              {uploading ? 'Processing OCR & AI Extraction...' : 'Upload & Run Audit'}
            </button>
          </div>
        </form>

        {extractedData && (
          <div className="card">
            <div className="card-header">
              <span className="card-title"><FileSearch size={16} /> Extracted Metadata & Consistency Checks</span>
              <span className={`badge ${extractedData.consistency_score >= 90 ? 'green' : 'orange'}`}>Consistency Score: {extractedData.consistency_score}%</span>
            </div>
            <div className="card-body">
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                Values extracted from PDF Order compared directly with the system database.
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div style={{ padding: '10px', backgroundColor: 'var(--bg-color)', borderRadius: '4px' }}>
                  <strong>Extracted Work ID:</strong>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: 'var(--primary-color)' }}>{extractedData.extracted_data?.work_id || 'Not Found'}</div>
                </div>
                <div style={{ padding: '10px', backgroundColor: 'var(--bg-color)', borderRadius: '4px' }}>
                  <strong>Extracted Amount:</strong>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: 'var(--primary-color)' }}>₹{extractedData.extracted_data?.sanctioned_amount?.toLocaleString() || 'N/A'}</div>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Raw Document Content (OCR)</label>
                <div style={{ padding: '12px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--border-radius-md)', maxHeight: '150px', overflowY: 'auto', fontSize: '11px', fontFamily: 'monospace' }}>
                  {extractedData.ocr_text}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div>
        <div className="card">
          <div className="card-header">
            <span className="card-title"><FileText size={16} /> Recent Upload Logs</span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {recentDocs.length === 0 ? (
              <div style={{ color: 'var(--text-secondary)', padding: '20px', textAlign: 'center' }}>No recent document logs found.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {recentDocs.slice(0, 8).map(d => (
                  <div key={d.id} style={{ padding: '12px', borderBottom: '1px solid var(--border-color)', fontSize: '12.5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', marginBottom: '4px' }}>
                      <span style={{ color: 'var(--secondary-color)', cursor: 'pointer', textDecoration: 'underline' }} onClick={() => onSelectProject(d.work_id)}>
                        {d.work_id}
                      </span>
                      <span className={`badge ${d.consistency_score >= 90 ? 'green' : 'orange'}`} style={{ fontSize: '10px' }}>
                        {d.consistency_score?.toFixed(0)}%
                      </span>
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {d.file_name}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      Uploaded: {new Date(d.upload_date).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// --- INVESTIGATIONS QUEUE TAB ---
function InvestigationsTab({ onSelectProject, currentUser }: { onSelectProject: (id: string) => void, currentUser: User | null }) {
  const [cases, setCases] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchCases();
  }, [statusFilter]);

  const fetchCases = async () => {
    setLoading(true);
    try {
      const data = await api.getInvestigations(statusFilter || undefined);
      setCases(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    if (priority === "CRITICAL") return "red";
    if (priority === "HIGH") return "orange";
    if (priority === "MEDIUM") return "blue";
    return "gray";
  };

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title"><UserCheck size={16} /> Open Case Files & Audits</span>
        <select className="filter-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="Detected">Detected</option>
          <option value="Under Review">Under Review</option>
          <option value="Assigned">Assigned</option>
          <option value="Evidence Requested">Evidence Requested</option>
          <option value="Resolved">Resolved</option>
        </select>
      </div>

      <div className="card-body" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px' }}><RefreshCw className="animate-spin" /> Fetching cases...</div>
        ) : cases.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>No open investigation cases match current filter.</div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Project ID</th>
                  <th>Description</th>
                  <th>Assigned Officer</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Created Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {cases.map(c => (
                  <tr key={c.id}>
                    <td style={{ fontWeight: '700' }}>CASE-{c.id}</td>
                    <td style={{ fontWeight: '700', color: 'var(--secondary-color)' }}>{c.work_id}</td>
                    <td style={{ fontSize: '13px' }}>
                      <div style={{ fontWeight: '600' }}>{c.work_description}</div>
                      {c.resolution_state && <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Resolution: <strong>{c.resolution_state}</strong></div>}
                    </td>
                    <td style={{ fontSize: '12.5px', fontWeight: '500' }}>{c.assigned_to_name || <em style={{ color: 'var(--text-secondary)' }}>Unassigned</em>}</td>
                    <td>
                      <span className={`badge ${getPriorityColor(c.priority)}`}>{c.priority}</span>
                    </td>
                    <td>
                      <span className="badge gray">{c.status}</span>
                    </td>
                    <td style={{ fontSize: '12px' }}>{new Date(c.created_at).toLocaleDateString()}</td>
                    <td>
                      <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '11px' }} onClick={() => onSelectProject(c.work_id)}>
                        Manage Case
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// --- RULES ENGINE TAB ---
function RulesTab({ currentUser }: { currentUser: any }) {
  const [rules, setRules] = useState<Rule[]>([]);
  const [evaluating, setEvaluating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  const handleDownloadBackup = async () => {
    setDownloading(true);
    try {
      await api.downloadDatabaseBackup();
    } catch (e: any) {
      alert(e.message || "Failed to download backup.");
    } finally {
      setDownloading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const data = await api.getRules();
      setRules(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleRule = async (id: string, currentStatus: boolean) => {
    try {
      const updated = await api.updateRule(id, { enabled: !currentStatus });
      setRules(rules.map(r => r.id === id ? updated : r));
    } catch (e) {
      alert("Failed to toggle rule");
    }
  };

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    try {
      const res = await api.triggerRulesEvaluation();
      alert(res.message || "Rules evaluation complete.");
    } catch (e) {
      alert("Failed to run rules engine evaluation.");
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="card-title"><Settings size={16} /> Compliance Rules Configurations</span>
        <div style={{ display: 'flex', gap: '10px' }}>
          {(currentUser?.role_name === "Ministry Administrator" || currentUser?.role_name === "State Nodal Authority") && (
            <button className="btn btn-secondary" onClick={handleDownloadBackup} disabled={downloading}>
              {downloading ? 'Downloading...' : 'Export Database Backup'}
            </button>
          )}
          <button className="btn btn-primary" onClick={handleRunEvaluation} disabled={evaluating}>
            {evaluating ? 'Running Analysis...' : 'Evaluate Rules Engine'}
          </button>
        </div>
      </div>

      <div className="card-body" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '200px' }}><RefreshCw className="animate-spin" /> Fetching rules...</div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rule ID</th>
                  <th>Rule Name</th>
                  <th>Description</th>
                  <th>Severity</th>
                  <th>Condition Code</th>
                  <th style={{ width: '80px', textAlign: 'center' }}>Enabled</th>
                </tr>
              </thead>
              <tbody>
                {rules.map(r => (
                  <tr key={r.id}>
                    <td style={{ fontWeight: '700' }}>{r.id}</td>
                    <td style={{ fontWeight: '600' }}>{r.name}</td>
                    <td style={{ fontSize: '12.5px', color: 'var(--text-secondary)' }}>{r.description}</td>
                    <td>
                      <span className={`badge ${r.severity === "CRITICAL" ? 'red' : (r.severity === "HIGH" ? 'orange' : 'gray')}`}>{r.severity}</span>
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '11px', backgroundColor: 'var(--bg-color)', padding: '6px' }}>{r.condition_expression}</td>
                    <td style={{ textAlign: 'center' }}>
                      <input type="checkbox" checked={r.enabled} onChange={() => handleToggleRule(r.id, r.enabled)} style={{ cursor: 'pointer', width: '16px', height: '16px' }} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// --- CHATBOT WIDGET ---
function ChatbotWidget({ minimized, setMinimized, input, setInput, messages, setMessages, onSelectProject }: any) {
  const [sending, setSending] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, minimized]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userText = input.trim();
    setInput('');
    setSending(true);

    // Add user message
    setMessages((prev: any) => [...prev, { sender: 'user', text: userText }]);

    try {
      const res = await api.queryAI(userText);
      setMessages((prev: any) => [...prev, { sender: 'bot', text: res.answer, sources: res.sources }]);
    } catch (err) {
      setMessages((prev: any) => [...prev, { sender: 'bot', text: "Sorry, I encountered an issue querying the database assistant. Please verify your connection." }]);
    } finally {
      setSending(false);
    }
  };

  if (minimized) {
    return (
      <div className="ai-chatbot-widget minimized" onClick={() => setMinimized(false)}>
        <div className="chatbot-header" style={{ height: '100%', borderRadius: 'var(--border-radius-lg)', cursor: 'pointer' }}>
          <span className="chatbot-header-title"><MessageSquare size={16} /> Chat Assistant</span>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-chatbot-widget">
      <div className="chatbot-header">
        <span className="chatbot-header-title"><MessageSquare size={16} /> Sentinel AI Assistant</span>
        <button 
          style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '11px', fontWeight: 'bold' }} 
          onClick={() => setMinimized(true)}
        >
          Hide
        </button>
      </div>

      <div className="chatbot-body">
        {messages.map((m: any, idx: number) => (
          <div key={idx} className={`chat-msg ${m.sender}`}>
            <div>{m.text}</div>
            {m.sources && m.sources.length > 0 && (
              <div className="chat-sources">
                <strong>Referenced records:</strong>
                <div style={{ marginTop: '2px' }}>
                  {m.sources.map((s: any, i: number) => (
                    <span 
                      key={i} 
                      className="chat-source-link" 
                      onClick={() => {
                        const idMatch = s.link.split('/').pop();
                        if (idMatch) onSelectProject(idMatch);
                      }}
                    >
                      {s.title}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      <form className="chatbot-footer" onSubmit={handleSendMessage}>
        <input 
          type="text" 
          className="chatbot-input" 
          placeholder="Ask about delayed works, high risk..." 
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={sending}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '6px 12px' }} disabled={sending}>
          <Send size={12} />
        </button>
      </form>
    </div>
  );
}
