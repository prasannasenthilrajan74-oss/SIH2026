import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldAlert, ShieldCheck, Activity, Layers, FileText, 
  Settings, UserCheck, MessageSquare, AlertTriangle, 
  MapPin, CheckCircle, Search, LogOut, ArrowRight, 
  TrendingUp, IndianRupee, Clock, Briefcase, FileSearch, 
  HelpCircle, ChevronRight, RefreshCw, Send, PlusCircle,
  Cpu, Bot, Building2, Download, Zap, Server, Database
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  Legend, ResponsiveContainer, PieChart, Pie, Cell, 
  LineChart, Line, AreaChart, Area, ComposedChart, RadarChart, Radar, PolarGrid, PolarAngleAxis, LabelList
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
  primary_attribution?: string;
  backtrack_summary?: string;
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
      <div className="login-screen-premium">
        {/* Left Panel — Branding */}
        <div className="login-brand-panel">
          <div className="login-brand-content">
            <div className="login-brand-logo">
              <ShieldAlert size={48} />
            </div>
            <h1 className="login-brand-title">MPLADS Sentinel AI</h1>
            <p className="login-brand-tagline">"From Passive Monitoring to Proactive Governance"</p>
            <div className="login-feature-list">
              <div className="login-feature-item">
                <div className="login-feature-icon"><Activity size={18} /></div>
                <div>
                  <div className="login-feature-title">AI Risk Intelligence</div>
                  <div className="login-feature-desc">Isolation Forest anomaly detection with Explainable AI scoring</div>
                </div>
              </div>
              <div className="login-feature-item">
                <div className="login-feature-icon"><Layers size={18} /></div>
                <div>
                  <div className="login-feature-title">Root-Cause Backtracking</div>
                  <div className="login-feature-desc">Controlled variable attribution to isolate agency vs district risk</div>
                </div>
              </div>
              <div className="login-feature-item">
                <div className="login-feature-icon"><FileText size={18} /></div>
                <div>
                  <div className="login-feature-title">OCR Document Verification</div>
                  <div className="login-feature-desc">Automated cross-validation of PDFs against structured records</div>
                </div>
              </div>
              <div className="login-feature-item">
                <div className="login-feature-icon"><MapPin size={18} /></div>
                <div>
                  <div className="login-feature-title">Geospatial Heatmapping</div>
                  <div className="login-feature-desc">Real-time GIS-based geographic risk concentration maps</div>
                </div>
              </div>
            </div>
            <div className="login-brand-badge">SIH Problem Statement 26102 · MoSPI DIID</div>
          </div>
        </div>

        {/* Right Panel — Login Form */}
        <div className="login-form-panel">
          <form className="login-form-card" onSubmit={handleLogin}>
            <div className="login-form-header">
              <h2>Command Center Access</h2>
              <p>Authenticate to enter the governance intelligence platform</p>
            </div>

            {loginError && (
              <div style={{ color: 'var(--danger-color)', backgroundColor: 'var(--danger-light)', border: '1px solid #fee2e2', padding: '12px 16px', borderRadius: 'var(--border-radius-md)', marginBottom: '20px', fontSize: '13px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={16} /> {loginError}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Username</label>
              <input 
                type="text" 
                className="form-control" 
                value={usernameInput} 
                onChange={e => setUsernameInput(e.target.value)} 
                placeholder="Enter your username"
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
                placeholder="Enter your password"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block" style={{ padding: '14px', fontSize: '14px', fontWeight: '700', letterSpacing: '0.5px' }}>
              <Zap size={16} /> Access Command Center
            </button>

            <div className="login-demo-helper">
              <p><strong>Demo Accounts:</strong></p>
              <div className="demo-account-list">
                <span className="demo-account-tag" onClick={() => { setUsernameInput('admin'); setPasswordInput('admin123'); }}>Ministry Admin</span>
                <span className="demo-account-tag" onClick={() => { setUsernameInput('state_nodal'); setPasswordInput('state123'); }}>State Nodal</span>
                <span className="demo-account-tag" onClick={() => { setUsernameInput('district_auth'); setPasswordInput('district123'); }}>District Auth</span>
                <span className="demo-account-tag" onClick={() => { setUsernameInput('mp_viewer'); setPasswordInput('mp123'); }}>MP Viewer</span>
                <span className="demo-account-tag" onClick={() => { setUsernameInput('investigator'); setPasswordInput('investigator123'); }}>Investigator</span>
              </div>
            </div>
          </form>
        </div>
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
            <Activity size={16} /> {currentUser?.role_name === 'MP / Constituency Viewer' ? 'Constituency Overview' : currentUser?.role_name === 'Investigation Officer' ? 'Priority Queue' : currentUser?.role_name === 'District Authority' ? 'Action Dashboard' : 'Overview Dashboard'}
          </div>
          <div className={`nav-item ${activeTab === 'Risk Monitor' ? 'active' : ''}`} onClick={() => { setActiveTab('Risk Monitor'); setSelectedWorkId(null); }}>
            <ShieldAlert size={16} /> Risk Monitor
          </div>
          
          {/* Hide Backtracking & Agency Intelligence for MP / Constituency Viewer */}
          {currentUser?.role_name !== 'MP / Constituency Viewer' && (
            <>
              <div className={`nav-item ${activeTab === 'Root-Cause Backtracking' ? 'active' : ''}`} onClick={() => { setActiveTab('Root-Cause Backtracking'); setSelectedWorkId(null); }}>
                <Layers size={16} /> Root-Cause Backtracking
              </div>
              <div className={`nav-item ${activeTab === 'Agency Intelligence' ? 'active' : ''}`} onClick={() => { setActiveTab('Agency Intelligence'); setSelectedWorkId(null); }}>
                <Building2 size={16} /> Agency Intelligence
              </div>
            </>
          )}

          <div className={`nav-item ${activeTab === 'Documents' ? 'active' : ''}`} onClick={() => { setActiveTab('Documents'); setSelectedWorkId(null); }}>
            <FileText size={16} /> Documents & OCR
          </div>
          <div className={`nav-item ${activeTab === 'Investigations' ? 'active' : ''}`} onClick={() => { setActiveTab('Investigations'); setSelectedWorkId(null); }}>
            <UserCheck size={16} /> Case Investigations
          </div>

          {/* Hide Detection Rules for MP / Constituency Viewer */}
          {currentUser?.role_name !== 'MP / Constituency Viewer' && (
            <div className={`nav-item ${activeTab === 'Rules Config' ? 'active' : ''}`} onClick={() => { setActiveTab('Rules Config'); setSelectedWorkId(null); }}>
              <Settings size={16} /> Detection Rules {currentUser?.role_name !== 'Ministry Administrator' ? '(View Only)' : ''}
            </div>
          )}

          <div className={`nav-item ${activeTab === 'AI Assistant' ? 'active' : ''}`} onClick={() => { setActiveTab('AI Assistant'); setSelectedWorkId(null); }}>
            <Bot size={16} /> AI Assistant
          </div>
        </div>

        <div className="sidebar-footer">
          <SystemStatusWidget />
          <div className="sidebar-footer-user">
            <div className="user-profile-info">
              <span className="profile-username">{currentUser?.username}</span>
              <span className="profile-role">{currentUser?.role_name}</span>
            </div>
            <button className="logout-btn" onClick={handleLogout} title="Log Out">
              <LogOut size={16} />
            </button>
          </div>
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
              currentUser={currentUser}
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
          ) : activeTab === 'Root-Cause Backtracking' ? (
            <BacktrackingTab 
              state={selectedState} 
              district={selectedDistrict} 
              category={selectedCategory} 
              status={selectedStatus} 
              search={globalSearch}
              onSelectProject={setSelectedWorkId} 
            />
          ) : activeTab === 'Agency Intelligence' ? (
            <AgencyIntelligenceTab onSelectProject={setSelectedWorkId} />
          ) : activeTab === 'Documents' ? (
            <DocumentsTab onSelectProject={setSelectedWorkId} />
          ) : activeTab === 'Investigations' ? (
            <InvestigationsTab onSelectProject={setSelectedWorkId} currentUser={currentUser} />
          ) : activeTab === 'Rules Config' ? (
            <RulesTab currentUser={currentUser} />
          ) : activeTab === 'AI Assistant' ? (
            <AIAssistantTab
              input={chatInput}
              setInput={setChatInput}
              messages={chatMessages}
              setMessages={setChatMessages}
              onSelectProject={setSelectedWorkId}
            />
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
function OverviewTab({ state, district, category, status, onSelectProject, currentUser }: any) {
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

  const formatCost = (val: number) => {
    if (!val) return '₹0';
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    return `₹${(val / 100000).toFixed(1)} Lakh`;
  };

  const COLORS = ['#1d4ed8', '#0284c7', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#6366f1'];

  return (
    <div>
      {/* District Authority: Action Required Widget */}
      {currentUser?.role_name === 'District Authority' && metrics && (
        <div style={{ marginBottom: '20px', padding: '16px 20px', background: 'linear-gradient(135deg, #fff5f5 0%, #fee2e2 100%)', borderRadius: 'var(--border-radius-lg)', border: '1px solid #fca5a5' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '15px', fontWeight: '800', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={18} /> Action Required Today ({metrics.critical_alerts || 0} Critical Alerts in {currentUser?.district || 'District'})
            </span>
            <span style={{ fontSize: '12px', fontWeight: '600', color: '#991b1b' }}>Operational Review Queue</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
            <div style={{ backgroundColor: '#ffffff', padding: '10px 14px', borderRadius: 'var(--border-radius-md)', border: '1px solid #fecaca' }}>
              <div style={{ fontSize: '11px', color: '#991b1b', fontWeight: 'bold' }}>CRITICAL WORKS</div>
              <div style={{ fontSize: '20px', fontWeight: '800', color: '#dc2626' }}>{metrics.critical_alerts || 0}</div>
            </div>
            <div style={{ backgroundColor: '#ffffff', padding: '10px 14px', borderRadius: 'var(--border-radius-md)', border: '1px solid #fed7aa' }}>
              <div style={{ fontSize: '11px', color: '#9a3412', fontWeight: 'bold' }}>COST ANOMALIES</div>
              <div style={{ fontSize: '20px', fontWeight: '800', color: '#ea580c' }}>{metrics.cost_alerts || 0}</div>
            </div>
            <div style={{ backgroundColor: '#ffffff', padding: '10px 14px', borderRadius: 'var(--border-radius-md)', border: '1px solid #fef08a' }}>
              <div style={{ fontSize: '11px', color: '#854d0e', fontWeight: 'bold' }}>DELAYED PROJECTS</div>
              <div style={{ fontSize: '20px', fontWeight: '800', color: '#d97706' }}>{metrics.delayed_works || 0}</div>
            </div>
            <div style={{ backgroundColor: '#ffffff', padding: '10px 14px', borderRadius: 'var(--border-radius-md)', border: '1px solid #fed7aa' }}>
              <div style={{ fontSize: '11px', color: '#9a3412', fontWeight: 'bold' }}>DUPLICATE CANDIDATES</div>
              <div style={{ fontSize: '20px', fontWeight: '800', color: '#c2410c' }}>{metrics.duplicate_alerts || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* MP / Constituency Viewer: Outcomes Header */}
      {currentUser?.role_name === 'MP / Constituency Viewer' && (
        <div style={{ marginBottom: '20px', padding: '16px 20px', background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)', borderRadius: 'var(--border-radius-lg)', border: '1px solid #86efac' }}>
          <div style={{ fontSize: '15px', fontWeight: '800', color: '#166534', marginBottom: '4px' }}>
            Constituency Progress & Outcomes ({currentUser?.constituency || 'MP Constituency'})
          </div>
          <div style={{ fontSize: '12.5px', color: '#15803d' }}>
            High-level summary of MPLADS infrastructure recommendations, sanctions, and completion status.
          </div>
        </div>
      )}

      {/* Overview header with refresh button */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--primary-color)' }}>
          {currentUser?.role_name === 'MP / Constituency Viewer' ? 'Constituency Summary' : currentUser?.role_name === 'District Authority' ? 'District Action Center' : 'Platform Intelligence Overview'}
        </h2>
        {currentUser?.role_name === 'Ministry Administrator' && (
          <button 
            className="btn btn-secondary" 
            style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}
            onClick={async () => {
              try {
                const res = await api.refreshRiskScores();
                alert(res.message || 'Risk scores refreshed!');
                fetchMetrics();
              } catch (e: any) {
                alert(e.message || 'Refresh failed — check role permissions.');
              }
            }}
          >
            <RefreshCw size={14} /> Refresh AI Scores
          </button>
        )}
      </div>

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
          <div className="card-body" style={{ height: '320px' }}>
            {(() => {
              const districtScores = (metrics.district_rankings || []).map((d: any) => Number(d.avg_risk_score) || 0);
              const minScore = districtScores.length ? Math.max(0, Math.floor(Math.min(...districtScores) - 4)) : 0;
              const maxScore = districtScores.length ? Math.min(100, Math.ceil(Math.max(...districtScores) + 3)) : 100;
              return (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={metrics.district_rankings}
                    margin={{ top: 20, right: 10, left: 10, bottom: 25 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="district_name" angle={-15} textAnchor="end" interval={0} style={{ fontSize: '11px' }} />
                    <YAxis style={{ fontSize: '11px' }} domain={[minScore, maxScore]} />
                    <Tooltip formatter={(val: any) => [`${Number(val).toFixed(1)}/100`, 'Avg Risk Score']} />
                    <Bar dataKey="avg_risk_score" fill="var(--primary-color)" name="Avg Risk Index" radius={[4, 4, 0, 0]}>
                      <LabelList dataKey="avg_risk_score" position="top" formatter={(val: any) => Number(val).toFixed(1)} style={{ fontSize: '10px', fontWeight: 'bold', fill: '#1e293b' }} />
                      {metrics.district_rankings && metrics.district_rankings.map((entry: any, index: number) => {
                        const color = entry.avg_risk_score >= 65 ? 'var(--danger-color)' : 'var(--primary-color)';
                        return <Cell key={`cell-${index}`} fill={color} />;
                      })}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              );
            })()}
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
                  <th>Root Cause</th>
                  <th>Warnings Triggered</th>
                  <th style={{ width: '80px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {works.map(w => {
                  const score = w.risk_scores?.overall_score || 0.0;
                  const factorCount = w.risk_scores?.factors?.length || 0;
                  
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
                        <span className={`badge ${
                          w.primary_attribution === 'AGENCY_CONCENTRATION' ? 'red' : 
                          w.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'orange' : 
                          w.primary_attribution === 'ISOLATED_CASE' ? 'blue' : 'green'
                        }`} style={{ fontWeight: '600', fontSize: '10.5px' }}>
                          {w.primary_attribution === 'AGENCY_CONCENTRATION' ? 'Agency Risk' : 
                           w.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'District Risk' : 
                           w.primary_attribution === 'ISOLATED_CASE' ? 'Isolated Case' : 'Normal'}
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

// --- ROOT-CAUSE BACKTRACKING TAB COMPONENT ---
function BacktrackingTab({ state, district, category, status, search, onSelectProject }: any) {
  const [works, setWorks] = useState<Work[]>([]);
  const [allWorksForStats, setAllWorksForStats] = useState<Work[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [attributionFilter, setAttributionFilter] = useState('');
  
  // Pagination
  const [page, setPage] = useState(0);
  const limit = 12;

  // Selected work for root-cause detailed drawer
  const [selectedBacktrackWorkId, setSelectedBacktrackWorkId] = useState<string | null>(null);
  const [backtrackDetail, setBacktrackDetail] = useState<any>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    setPage(0);
    fetchWorks();
  }, [state, district, category, status, attributionFilter, search]);

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
        search: search,
        limit: 200,
        offset: 0
      });
      
      const worksList = Array.isArray(res) ? res : (res?.works || []);
      setAllWorksForStats(worksList);
      
      let filtered = worksList;
      if (attributionFilter) {
        filtered = filtered.filter((w: Work) => w.primary_attribution === attributionFilter);
      }
      
      setTotalCount(filtered.length);
      setWorks(filtered.slice(page * limit, (page + 1) * limit));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (workId: string) => {
    setSelectedBacktrackWorkId(workId);
    setLoadingDetail(true);
    setBacktrackDetail(null);
    try {
      const data = await api.getWorkControlledBacktrack(workId);
      setBacktrackDetail(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingDetail(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 85) return 'red';
    if (score >= 70) return 'orange';
    if (score >= 45) return 'gray';
    return 'green';
  };

  // Stats Calculations
  const totalChecked = allWorksForStats.length;
  const flaggedProjects = allWorksForStats.filter(w => w.primary_attribution && w.primary_attribution !== 'NORMAL_CASE');
  const totalFlagged = flaggedProjects.length;
  
  const agencyCount = flaggedProjects.filter(w => w.primary_attribution === 'AGENCY_CONCENTRATION').length;
  const districtCount = flaggedProjects.filter(w => w.primary_attribution === 'DISTRICT_CONCENTRATION').length;
  const isolatedCount = flaggedProjects.filter(w => w.primary_attribution === 'ISOLATED_CASE').length;
  
  const agencyPercent = totalFlagged > 0 ? ((agencyCount / totalFlagged) * 100).toFixed(0) : '0';
  const districtPercent = totalFlagged > 0 ? ((districtCount / totalFlagged) * 100).toFixed(0) : '0';
  const isolatedPercent = totalFlagged > 0 ? ((isolatedCount / totalFlagged) * 100).toFixed(0) : '0';

  const chartData = [
    { name: 'Agency Risk', value: agencyCount, color: 'var(--danger-color)' },
    { name: 'District Risk', value: districtCount, color: 'var(--warning-color)' },
    { name: 'Isolated Case', value: isolatedCount, color: '#3b82f6' }
  ].filter(d => d.value > 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top dashboard section */}
      <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: '20px' }}>
        
        {/* Left: Metrics Cards */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '20px' }}>
          <div className="card-header" style={{ padding: 0, borderBottom: 'none', marginBottom: '16px' }}>
            <span className="card-title" style={{ fontSize: '15px' }}><Activity size={16} /> Portfolio Attribution Summary</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            {/* Total Checked */}
            <div style={{ padding: '16px', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-color)', background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)' }}>
              <div style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>Total Scope Projects</div>
              <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--primary-color)' }}>{totalChecked}</div>
              <div style={{ fontSize: '10.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>{totalFlagged} anomalous (≥30 threshold)</div>
            </div>

            {/* Agency Concentration */}
            <div style={{ padding: '16px', borderRadius: 'var(--border-radius-md)', border: '1px solid #fee2e2', background: 'linear-gradient(135deg, #fff5f5 0%, #fee2e2 100%)' }}>
              <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#b91c1c', textTransform: 'uppercase', marginBottom: '4px' }}>Agency Risk Concentration</div>
              <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--danger-color)' }}>{agencyCount} <span style={{ fontSize: '13px', fontWeight: '600', color: '#b91c1c' }}>({agencyPercent}%)</span></div>
              <div style={{ fontSize: '10.5px', color: '#7f1d1d', marginTop: '4px' }}>Root cause: unique agency elevation</div>
            </div>

            {/* District Concentration */}
            <div style={{ padding: '16px', borderRadius: 'var(--border-radius-md)', border: '1px solid #fef3c7', background: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)' }}>
              <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#b45309', textTransform: 'uppercase', marginBottom: '4px' }}>District Risk Concentration</div>
              <div style={{ fontSize: '24px', fontWeight: '800', color: '#d97706' }}>{districtCount} <span style={{ fontSize: '13px', fontWeight: '600', color: '#b45309' }}>({districtPercent}%)</span></div>
              <div style={{ fontSize: '10.5px', color: '#78350f', marginTop: '4px' }}>Root cause: local admin clusters</div>
            </div>

            {/* Isolated Cases */}
            <div style={{ padding: '16px', borderRadius: 'var(--border-radius-md)', border: '1px solid #dbeafe', background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)' }}>
              <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#1d4ed8', textTransform: 'uppercase', marginBottom: '4px' }}>Isolated Anomalies</div>
              <div style={{ fontSize: '24px', fontWeight: '800', color: '#2563eb' }}>{isolatedCount} <span style={{ fontSize: '13px', fontWeight: '600', color: '#1d4ed8' }}>({isolatedPercent}%)</span></div>
              <div style={{ fontSize: '10.5px', color: '#1e3a8a', marginTop: '4px' }}>Root cause: project-specific variables</div>
            </div>
          </div>
        </div>

        {/* Right: Breakdown Chart */}
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div className="card-header" style={{ padding: 0, width: '100%', borderBottom: 'none', marginBottom: '10px' }}>
            <span className="card-title" style={{ fontSize: '15px' }}><Layers size={16} /> Attribution Distribution</span>
          </div>
          
          {totalFlagged > 0 ? (
            <div style={{ width: '100%', height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ width: '50%', height: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value} projects`, 'Attribution']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div style={{ width: '45%', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '3px', backgroundColor: 'var(--danger-color)' }} />
                  <span>Agency Concentration ({agencyCount})</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '3px', backgroundColor: 'var(--warning-color)' }} />
                  <span>District Nodal Risk ({districtCount})</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '3px', backgroundColor: '#3b82f6' }} />
                  <span>Isolated Anomalies ({isolatedCount})</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '40px 0', fontSize: '13px' }}>
              No risk anomalies detected within the current scope filters.
            </div>
          )}
        </div>
      </div>

      {/* Audit priority table list */}
      <div className="card">
        <div className="card-header" style={{ padding: '12px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="card-title"><Layers size={16} /> Portfolio Attribution Queue</span>
          <select 
            className="filter-select" 
            value={attributionFilter} 
            onChange={e => setAttributionFilter(e.target.value)}
            style={{ width: '220px' }}
          >
            <option value="">All Attributions</option>
            <option value="AGENCY_CONCENTRATION">🔴 Agency Concentration</option>
            <option value="DISTRICT_CONCENTRATION">🟠 District Nodal Risk</option>
            <option value="ISOLATED_CASE">🔵 Isolated Case</option>
            <option value="NORMAL_CASE">🟢 Normal / No Risk</option>
          </select>
        </div>

        <div className="card-body" style={{ padding: 0 }}>
          {loading ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '250px' }}><RefreshCw className="animate-spin" /> Fetching backtracking analysis...</div>
          ) : works.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>No works match the selected root-cause filter.</div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Project ID</th>
                    <th>Description</th>
                    <th>MP / Constituency</th>
                    <th style={{ textAlign: 'right' }}>Sanctioned Amt</th>
                    <th>Anomaly Index</th>
                    <th>Root-Cause Attribution</th>
                    <th>Summary</th>
                    <th style={{ width: '120px', textAlign: 'center' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {works.map(w => {
                    const score = w.risk_scores?.overall_score || 0.0;
                    
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
                        <td>
                          <span className={`badge ${getRiskColor(score)}`} style={{ fontWeight: 'bold', fontSize: '10.5px' }}>
                            {score.toFixed(1)}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${
                            w.primary_attribution === 'AGENCY_CONCENTRATION' ? 'red' : 
                            w.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'orange' : 
                            w.primary_attribution === 'ISOLATED_CASE' ? 'blue' : 'green'
                          }`} style={{ fontWeight: '600', fontSize: '10.5px' }}>
                            {w.primary_attribution === 'AGENCY_CONCENTRATION' ? 'Agency Risk' : 
                             w.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'District Risk' : 
                             w.primary_attribution === 'ISOLATED_CASE' ? 'Isolated Case' : 'Normal'}
                          </span>
                        </td>
                        <td style={{ fontSize: '12px', color: 'var(--text-secondary)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={w.backtrack_summary || ''}>
                          {w.backtrack_summary}
                        </td>
                        <td style={{ textAlign: 'center' }}>
                          <button 
                            className="btn btn-secondary" 
                            style={{ padding: '4px 10px', fontSize: '11px' }}
                            onClick={() => handleViewDetail(w.id)}
                          >
                            Peer Details
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

      {/* Details drawer Overlay panel */}
      {selectedBacktrackWorkId && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: '450px',
          height: '100vh',
          backgroundColor: '#ffffff',
          boxShadow: '-4px 0 20px rgba(0,0,0,0.15)',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          fontFamily: 'Inter, sans-serif'
        }}>
          {/* Drawer Header */}
          <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--primary-color)', color: '#ffffff' }}>
            <span style={{ fontWeight: '700', fontSize: '15px' }}>Project Root-Cause Details</span>
            <button 
              onClick={() => { setSelectedBacktrackWorkId(null); setBacktrackDetail(null); }}
              style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '18px', fontWeight: 'bold' }}
            >
              ✕
            </button>
          </div>
          
          {/* Drawer Content */}
          <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
            {loadingDetail ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <RefreshCw className="animate-spin" style={{ marginBottom: '10px' }} />
                <span>Performing controlled peer analysis...</span>
              </div>
            ) : backtrackDetail ? (
              <div>
                <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '8px', color: 'var(--primary-color)' }}>{backtrackDetail.work_id}</div>
                <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: '1.5' }}>{backtrackDetail.description}</p>
                
                <div style={{
                  padding: '12px 16px',
                  backgroundColor: backtrackDetail.primary_attribution === 'AGENCY_CONCENTRATION' ? 'var(--danger-light)' : (backtrackDetail.primary_attribution === 'DISTRICT_CONCENTRATION' ? '#fffbeb' : '#f8fafc'),
                  borderLeft: `4px solid ${
                    backtrackDetail.primary_attribution === 'AGENCY_CONCENTRATION' ? 'var(--danger-color)' : (backtrackDetail.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'var(--warning-color)' : '#64748b')
                  }`,
                  borderRadius: '4px',
                  marginBottom: '20px'
                }}>
                  <div style={{ fontWeight: '700', fontSize: '12px', color: backtrackDetail.primary_attribution === 'AGENCY_CONCENTRATION' ? 'var(--danger-color)' : (backtrackDetail.primary_attribution === 'DISTRICT_CONCENTRATION' ? '#b45309' : '#334155'), textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
                    {backtrackDetail.primary_attribution === 'AGENCY_CONCENTRATION' ? 'Agency Concentration Anomaly' : (backtrackDetail.primary_attribution === 'DISTRICT_CONCENTRATION' ? 'District Concentration Anomaly' : 'Isolated Project Anomaly')}
                  </div>
                  <div style={{ fontSize: '12.5px', fontWeight: '500', lineHeight: '1.4' }}>{backtrackDetail.summary}</div>
                </div>

                {/* Itemized Purchased Goods & Vendor Bill Audit Card */}
                {backtrackDetail.itemized_purchase_audit && (
                  <div className="card" style={{ marginBottom: '16px', border: '1px solid #cbd5e1', boxShadow: '0 2px 4px rgba(0,0,0,0.04)', backgroundColor: '#ffffff' }}>
                    <div className="card-header" style={{ padding: '10px 14px', fontSize: '13px', fontWeight: 'bold', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f1f5f9' }}>
                      <span style={{ color: '#0f172a' }}><FileText size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Purchased Goods & Itemized Bill Audit</span>
                      <a
                        href={`http://localhost:8000/api/documents/${backtrackDetail.itemized_purchase_audit.document_id}/file`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-primary"
                        style={{ fontSize: '11px', padding: '4px 10px', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
                      >
                        <FileText size={12} /> View Purchase Bill PDF
                      </a>
                    </div>
                    <div className="card-body" style={{ padding: '14px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                        <div><strong>Contractor / Vendor:</strong> {backtrackDetail.itemized_purchase_audit.vendor_name || 'TechLine IT & Lab Equipment Solutions'}</div>
                        <div><strong>Total Purchase Value:</strong> <span style={{ color: 'var(--primary-color)', fontWeight: 'bold' }}>₹{backtrackDetail.itemized_purchase_audit.total_sanctioned_amount?.toLocaleString()}</span></div>
                      </div>

                      <table style={{ width: '100%', fontSize: '11px', borderCollapse: 'collapse', marginTop: '6px' }}>
                        <thead>
                          <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #cbd5e1', textAlign: 'left' }}>
                            <th style={{ padding: '6px' }}>Purchased Item & Model Specifications</th>
                            <th style={{ padding: '6px' }}>Quantity</th>
                            <th style={{ padding: '6px' }}>Unit Cost</th>
                            <th style={{ padding: '6px', textAlign: 'right' }}>Total Price</th>
                          </tr>
                        </thead>
                        <tbody>
                          {backtrackDetail.itemized_purchase_audit.items?.map((itm: any, i: number) => (
                            <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                              <td style={{ padding: '6px', fontWeight: '500' }}>{itm.name}</td>
                              <td style={{ padding: '6px', color: 'var(--text-secondary)' }}>{itm.qty}</td>
                              <td style={{ padding: '6px', color: 'var(--text-secondary)' }}>{itm.unit_cost}</td>
                              <td style={{ padding: '6px', textAlign: 'right', fontWeight: 'bold' }}>{itm.total_cost}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Multi-Signal Composite Risk Summary (#6) */}
                {backtrackDetail.multi_signal_summary && (
                  <div className="card" style={{ marginBottom: '16px', border: '1px solid var(--primary-light)', background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)', boxShadow: 'none' }}>
                    <div className="card-header" style={{ padding: '10px 14px', fontSize: '12px', fontWeight: 'bold', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#e2e8f0' }}>
                      <span><ShieldAlert size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Multi-Signal Risk Agreement</span>
                      <span className={`badge ${
                        backtrackDetail.multi_signal_summary.composite_confidence === 'HIGH_CONFIDENCE_FLAG' ? 'red' :
                        backtrackDetail.multi_signal_summary.composite_confidence === 'MODERATE_CONFIDENCE_FLAG' ? 'orange' :
                        backtrackDetail.multi_signal_summary.composite_confidence === 'ELEVATED_SINGLE_SIGNAL' ? 'blue' : 'green'
                      }`} style={{ fontSize: '10px', fontWeight: 'bold' }}>
                        {backtrackDetail.multi_signal_summary.confidence_label}
                      </span>
                    </div>
                    <div className="card-body" style={{ padding: '12px', fontSize: '11px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                        <div style={{ padding: '6px 8px', borderRadius: '4px', background: backtrackDetail.multi_signal_summary.signals.agency_peer_comparison.status === 'HIGH' ? '#fee2e2' : '#ffffff', border: '1px solid var(--border-color)' }}>
                          <strong>Agency vs Peer:</strong> {backtrackDetail.multi_signal_summary.signals.agency_peer_comparison.multiplier}x ({backtrackDetail.multi_signal_summary.signals.agency_peer_comparison.status})
                        </div>
                        <div style={{ padding: '6px 8px', borderRadius: '4px', background: backtrackDetail.multi_signal_summary.signals.district_peer_comparison.status === 'HIGH' ? '#fef3c7' : '#ffffff', border: '1px solid var(--border-color)' }}>
                          <strong>District vs State:</strong> {backtrackDetail.multi_signal_summary.signals.district_peer_comparison.multiplier}x ({backtrackDetail.multi_signal_summary.signals.district_peer_comparison.status})
                        </div>
                        <div style={{ padding: '6px 8px', borderRadius: '4px', background: backtrackDetail.multi_signal_summary.signals.national_external_baseline.status === 'FLAGGED' ? '#fee2e2' : '#ffffff', border: '1px solid var(--border-color)' }}>
                          <strong>National Baseline:</strong> {backtrackDetail.multi_signal_summary.signals.national_external_baseline.multiplier}x ({backtrackDetail.multi_signal_summary.signals.national_external_baseline.status})
                        </div>
                        <div style={{ padding: '6px 8px', borderRadius: '4px', background: backtrackDetail.multi_signal_summary.signals.temporal_self_drift.status === 'FLAGGED' ? '#fef3c7' : '#ffffff', border: '1px solid var(--border-color)' }}>
                          <strong>Self-Trend Shift:</strong> +{backtrackDetail.multi_signal_summary.signals.temporal_self_drift.shift_pct}% ({backtrackDetail.multi_signal_summary.signals.temporal_self_drift.status})
                        </div>
                      </div>
                      <div style={{ padding: '6px 8px', borderRadius: '4px', background: backtrackDetail.multi_signal_summary.signals.vendor_network_concentration.status === 'FLAGGED' ? '#fee2e2' : '#ffffff', border: '1px solid var(--border-color)' }}>
                        <strong>Vendor Network:</strong> {backtrackDetail.multi_signal_summary.signals.vendor_network_concentration.vendor_name} across {backtrackDetail.multi_signal_summary.signals.vendor_network_concentration.agencies_spanned} agencies ({backtrackDetail.multi_signal_summary.signals.vendor_network_concentration.status})
                      </div>
                    </div>
                  </div>
                )}

                {/* Agency analysis details */}
                {backtrackDetail.agency_controlled_analysis && (
                  <div className="card" style={{ marginBottom: '16px', border: '1px solid var(--border-color)', boxShadow: 'none' }}>
                    <div className="card-header" style={{ padding: '10px 14px', fontSize: '12.5px', fontWeight: 'bold', backgroundColor: '#f8fafc' }}>
                      Agency Performance Context (Median & IQR Peer Engine)
                    </div>
                    <div className="card-body" style={{ padding: '14px' }}>
                      <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '10px' }}>
                        Agency: <span style={{ color: 'var(--primary-color)' }}>{backtrackDetail.agency_controlled_analysis.agency_name}</span>
                      </div>
                      
                      {backtrackDetail.agency_controlled_analysis.controlled_comparison && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', textAlign: 'center', marginBottom: '12px' }}>
                          <div style={{ padding: '8px', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                            <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--danger-color)' }}>
                              {backtrackDetail.agency_controlled_analysis.controlled_comparison.agency_anomaly_rate}%
                            </div>
                            <div style={{ fontSize: '9px', color: 'var(--text-secondary)' }}>Agency Rate</div>
                          </div>
                          <div style={{ padding: '8px', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                            <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--primary-color)' }}>
                              {backtrackDetail.agency_controlled_analysis.controlled_comparison.peer_baseline_rate}%
                            </div>
                            <div style={{ fontSize: '9px', color: 'var(--text-secondary)' }}>Peer Baseline (Median: {backtrackDetail.agency_controlled_analysis.controlled_comparison.peer_median_score || 0})</div>
                          </div>
                          <div style={{ padding: '8px', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                            <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--danger-color)' }}>
                              {backtrackDetail.agency_controlled_analysis.controlled_comparison.multiplier_ratio}x
                            </div>
                            <div style={{ fontSize: '9px', color: 'var(--text-secondary)' }}>Multiplier</div>
                          </div>
                        </div>
                      )}
                      
                      <div style={{ fontSize: '11.5px', marginBottom: '8px', lineHeight: '1.4' }}>
                        <strong>Attribution:</strong> {backtrackDetail.agency_controlled_analysis.attribution_summary}
                      </div>
                      <div style={{ fontSize: '11.5px', color: 'var(--primary-color)', lineHeight: '1.4' }}>
                        <strong>Audit Rec:</strong> {backtrackDetail.agency_controlled_analysis.recommendation}
                      </div>
                    </div>
                  </div>
                )}

                {/* District analysis details */}
                {backtrackDetail.district_controlled_analysis && (
                  <div className="card" style={{ marginBottom: '16px', border: '1px solid var(--border-color)', boxShadow: 'none' }}>
                    <div className="card-header" style={{ padding: '10px 14px', fontSize: '12.5px', fontWeight: 'bold', backgroundColor: '#f8fafc' }}>
                      District Performance Context
                    </div>
                    <div className="card-body" style={{ padding: '14px' }}>
                      <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '10px' }}>
                        District: <span style={{ color: 'var(--primary-color)' }}>{backtrackDetail.district_controlled_analysis.district_name}</span>
                      </div>
                      
                      {backtrackDetail.district_controlled_analysis.controlled_comparison && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', textAlign: 'center', marginBottom: '12px' }}>
                          <div style={{ padding: '8px', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                            <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--warning-color)' }}>
                              {backtrackDetail.district_controlled_analysis.controlled_comparison.district_anomaly_rate}%
                            </div>
                            <div style={{ fontSize: '9px', color: 'var(--text-secondary)' }}>District Rate</div>
                          </div>
                          <div style={{ padding: '8px', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                            <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--primary-color)' }}>
                              {backtrackDetail.district_controlled_analysis.controlled_comparison.state_peer_rate}%
                            </div>
                            <div style={{ fontSize: '9px', color: 'var(--text-secondary)' }}>State Baseline</div>
                          </div>
                          <div style={{ padding: '8px', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                            <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--warning-color)' }}>
                              {backtrackDetail.district_controlled_analysis.controlled_comparison.multiplier_ratio}x
                            </div>
                            <div style={{ fontSize: '9px', color: 'var(--text-secondary)' }}>Multiplier</div>
                          </div>
                        </div>
                      )}
                      
                      <div style={{ fontSize: '11.5px', marginBottom: '8px', lineHeight: '1.4' }}>
                        <strong>Attribution:</strong> {backtrackDetail.district_controlled_analysis.attribution_summary}
                      </div>
                    </div>
                  </div>
                )}

                {/* Residual Limitation Notice Footer Banner (#7) */}
                <div style={{ padding: '12px', backgroundColor: '#fffbe6', border: '1px solid #ffe58f', borderRadius: '6px', fontSize: '10.5px', color: '#8c6b00', marginTop: '16px', lineHeight: '1.4' }}>
                  <strong>ℹ️ Platform Residual Limitation Notice:</strong> Statistical anomaly detection compares variance across peer groups, national baselines, and temporal trends. Uniform, system-wide collusion that is constant across all agencies, districts, and time periods cannot be identified purely via statistical algorithms.
                </div>
                
                {/* Actions */}
                <div style={{ marginTop: '24px', display: 'flex', gap: '10px' }}>
                  <button 
                    className="btn btn-primary" 
                    style={{ flex: 1, padding: '10px' }}
                    onClick={() => {
                      onSelectProject(backtrackDetail.work_id);
                      setSelectedBacktrackWorkId(null);
                      setBacktrackDetail(null);
                    }}
                  >
                    Open Project 360
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '40px 0' }}>Failed to retrieve backtracking details.</div>
            )}
          </div>
        </div>
      )}
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
                  
                  {/* BarChart visualization of 8 sub-scores */}
                  <div style={{ marginBottom: '20px' }}>
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart
                        data={[
                          { name: 'Financial', value: work.risk_scores?.financial_risk || 0 },
                          { name: 'Delay', value: work.risk_scores?.delay_risk || 0 },
                          { name: 'Cost', value: work.risk_scores?.cost_risk || 0 },
                          { name: 'Duplicate', value: work.risk_scores?.duplicate_risk || 0 },
                          { name: 'Payment', value: work.risk_scores?.payment_risk || 0 },
                          { name: 'Compliance', value: work.risk_scores?.compliance_risk || 0 },
                          { name: 'Document', value: work.risk_scores?.document_risk || 0 },
                          { name: 'Geographic', value: work.risk_scores?.geographic_risk || 0 },
                        ]}
                        margin={{ top: 5, right: 10, left: -10, bottom: 5 }}
                        layout="vertical"
                      >
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} />
                        <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={70} />
                        <Tooltip formatter={(val: any) => [`${Number(val).toFixed(1)}/100`, 'Score']} />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                          {[
                            work.risk_scores?.financial_risk || 0,
                            work.risk_scores?.delay_risk || 0,
                            work.risk_scores?.cost_risk || 0,
                            work.risk_scores?.duplicate_risk || 0,
                            work.risk_scores?.payment_risk || 0,
                            work.risk_scores?.compliance_risk || 0,
                            work.risk_scores?.document_risk || 0,
                            work.risk_scores?.geographic_risk || 0,
                          ].map((val, i) => (
                            <Cell key={i} fill={val === 0 ? 'transparent' : val >= 70 ? '#ef4444' : val >= 40 ? '#f59e0b' : '#10b981'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Download Risk Report button */}
                  <button
                    className="btn btn-secondary"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', marginTop: '8px' }}
                    onClick={() => {
                      const rs = work.risk_scores;
                      const lines = [
                        `MPLADS SENTINEL AI — RISK REPORT`,
                        `Generated: ${new Date().toLocaleString()}`,
                        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
                        `Project ID     : ${work.id}`,
                        `Description    : ${work.description}`,
                        `Status         : ${work.status}`,
                        `MP             : ${work.mp_name} (${work.constituency})`,
                        `District       : ${work.district_code}`,
                        `Agency         : ${work.implementing_agency_name || 'N/A'}`,
                        ``,
                        `FINANCIAL SUMMARY`,
                        `Sanctioned     : ₹${(work.sanctioned_amount / 100000).toFixed(2)} Lakh`,
                        `Expenditure    : ₹${(work.expenditure / 100000).toFixed(2)} Lakh`,
                        `Fin. Progress  : ${work.financial_progress.toFixed(0)}%`,
                        `Phy. Progress  : ${work.physical_progress.toFixed(0)}%`,
                        ``,
                        `RISK SCORES`,
                        `Overall Risk   : ${rs?.overall_score?.toFixed(1) || 'N/A'} / 100`,
                        `Financial Risk : ${rs?.financial_risk?.toFixed(1) || 'N/A'}`,
                        `Delay Risk     : ${rs?.delay_risk?.toFixed(1) || 'N/A'}`,
                        `Cost Risk      : ${rs?.cost_risk?.toFixed(1) || 'N/A'}`,
                        `Duplicate Risk : ${rs?.duplicate_risk?.toFixed(1) || 'N/A'}`,
                        `Payment Risk   : ${rs?.payment_risk?.toFixed(1) || 'N/A'}`,
                        `Compliance Risk: ${rs?.compliance_risk?.toFixed(1) || 'N/A'}`,
                        `Document Risk  : ${rs?.document_risk?.toFixed(1) || 'N/A'}`,
                        `Geographic Risk: ${rs?.geographic_risk?.toFixed(1) || 'N/A'}`,
                        ``,
                        `AI RISK FACTORS`,
                        ...(rs?.factors || ['No risk factors detected']),
                        ``,
                        `Root-Cause Attribution: ${work.primary_attribution || 'N/A'}`,
                        `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
                        `MPLADS Sentinel AI | SIH PS 26102 | MoSPI DIID`,
                      ];
                      const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url; a.download = `risk_report_${work.id}.txt`;
                      document.body.appendChild(a); a.click(); a.remove();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    <Download size={14} /> Download Risk Report
                  </button>
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
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('Sanction Order');
  const [workIdInput, setWorkIdInput] = useState('');
  const [uploading, setUploading] = useState(false);

  // Inspection Drawer state
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [docExtractions, setDocExtractions] = useState<any | null>(null);
  const [loadingExtractions, setLoadingExtractions] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, [typeFilter]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.getAllDocuments({ document_type: typeFilter || undefined });
      setDocuments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleInspectDoc = async (id: number) => {
    setSelectedDocId(id);
    setLoadingExtractions(true);
    setDocExtractions(null);
    try {
      const res = await api.getDocumentExtractions(id);
      setDocExtractions(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingExtractions(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a PDF document first.");
      return;
    }
    setUploading(true);
    try {
      const res = await api.uploadDocument(file, docType, workIdInput || undefined);
      alert(`Document '${res.file_name}' uploaded successfully! AI Consistency Score: ${res.consistency_score}%`);
      setShowUploadModal(false);
      setFile(null);
      setWorkIdInput('');
      fetchDocuments();
      if (res.id) handleInspectDoc(res.id);
    } catch (err: any) {
      alert(err.message || "Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  // Filter calculations
  const filteredDocs = documents.filter(d => {
    const matchesSearch = !search || 
      (d.file_name && d.file_name.toLowerCase().includes(search.toLowerCase())) ||
      (d.work_id && d.work_id.toLowerCase().includes(search.toLowerCase()));
    
    const matchesStatus = !statusFilter || 
      (statusFilter === 'VERIFIED' && d.consistency_score >= 90) ||
      (statusFilter === 'MISMATCH' && d.consistency_score < 90);

    return matchesSearch && matchesStatus;
  });

  const totalDocs = documents.length;
  const verifiedDocs = documents.filter(d => d.consistency_score >= 90).length;
  const mismatchDocs = documents.filter(d => d.consistency_score < 90).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Header Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1.2fr', gap: '16px' }}>
        <div className="card" style={{ padding: '16px', background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)' }}>
          <div style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>Total Agency Uploads</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--primary-color)' }}>{totalDocs}</div>
          <div style={{ fontSize: '10.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>Repository PDF documents</div>
        </div>

        <div className="card" style={{ padding: '16px', background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)', border: '1px solid #bbf7d0' }}>
          <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#15803d', textTransform: 'uppercase', marginBottom: '4px' }}>100% Verified Orders</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: '#16a34a' }}>{verifiedDocs}</div>
          <div style={{ fontSize: '10.5px', color: '#166534', marginTop: '4px' }}>Passed DB cross-validation</div>
        </div>

        <div className="card" style={{ padding: '16px', background: 'linear-gradient(135deg, #fff5f5 0%, #fee2e2 100%)', border: '1px solid #fecaca' }}>
          <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#b91c1c', textTransform: 'uppercase', marginBottom: '4px' }}>Discrepancy Mismatches</div>
          <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--danger-color)' }}>{mismatchDocs}</div>
          <div style={{ fontSize: '10.5px', color: '#7f1d1d', marginTop: '4px' }}>Score &lt;90% (OCR Alert)</div>
        </div>

        <div className="card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: '#ffffff' }}>
          <button 
            className="btn btn-primary" 
            style={{ width: '100%', padding: '12px', fontSize: '13px', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            onClick={() => setShowUploadModal(true)}
          >
            <PlusCircle size={18} /> Upload Agency PDF Document
          </button>
        </div>
      </div>

      {/* Main Repository Table Card */}
      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} style={{ color: 'var(--primary-color)' }} />
            <span className="card-title" style={{ fontSize: '15px' }}>Agency Uploaded File Repository & OCR Audits</span>
          </div>

          {/* Filter controls */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <div style={{ position: 'relative' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
              <input 
                type="text" 
                className="form-control" 
                placeholder="Search file or Work ID..." 
                value={search} 
                onChange={e => setSearch(e.target.value)} 
                style={{ paddingLeft: '30px', fontSize: '12px', width: '200px' }}
              />
            </div>

            <select className="filter-select" value={typeFilter} onChange={e => setTypeFilter(e.target.value)} style={{ fontSize: '12px' }}>
              <option value="">All Document Categories</option>
              <option value="Sanction Order">Sanction Order</option>
              <option value="Utilization Certificate">Utilization Certificate (UC)</option>
              <option value="Work Order">Work Order</option>
              <option value="Invoice">Invoice</option>
              <option value="Inspection Report">Inspection Report</option>
            </select>

            <select className="filter-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={{ fontSize: '12px' }}>
              <option value="">All Verification Statuses</option>
              <option value="VERIFIED">100% Verified Only</option>
              <option value="MISMATCH">Discrepancy Alerts (&lt;90%)</option>
            </select>
          </div>
        </div>

        <div className="card-body" style={{ padding: 0 }}>
          {loading ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <RefreshCw className="animate-spin" style={{ marginBottom: '8px' }} />
              <div>Loading agency document repository...</div>
            </div>
          ) : filteredDocs.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              No uploaded files found matching the selected filter criteria.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Doc ID</th>
                    <th>Document File Name</th>
                    <th>Document Category</th>
                    <th>Associated Work ID</th>
                    <th>Upload Timestamp</th>
                    <th>AI Consistency Score</th>
                    <th style={{ textAlign: 'center' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDocs.slice(0, 50).map(d => (
                    <tr key={d.id}>
                      <td style={{ fontWeight: 'bold', fontSize: '12px' }}>#{d.id}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <FileText size={16} style={{ color: 'var(--primary-color)', flexShrink: 0 }} />
                          <span style={{ fontWeight: '600', fontSize: '12.5px' }}>{d.file_name}</span>
                        </div>
                      </td>
                      <td>
                        <span className="badge blue" style={{ fontSize: '10.5px' }}>
                          {d.document_type}
                        </span>
                      </td>
                      <td>
                        {d.work_id ? (
                          <span 
                            style={{ color: 'var(--primary-color)', fontWeight: 'bold', cursor: 'pointer', textDecoration: 'underline', fontSize: '12px' }}
                            onClick={() => onSelectProject(d.work_id)}
                          >
                            {d.work_id}
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>Unlinked</span>
                        )}
                      </td>
                      <td style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>
                        {new Date(d.upload_date).toLocaleDateString()} {new Date(d.upload_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td>
                        <span className={`badge ${d.consistency_score >= 90 ? 'green' : 'red'}`} style={{ fontWeight: 'bold', fontSize: '11px' }}>
                          {d.consistency_score >= 90 ? `✅ Verified (${d.consistency_score.toFixed(0)}%)` : `⚠️ Mismatch (${d.consistency_score.toFixed(0)}%)`}
                        </span>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                          <button 
                            className="btn btn-secondary" 
                            style={{ padding: '4px 8px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}
                            onClick={() => handleInspectDoc(d.id)}
                          >
                            <FileSearch size={13} /> OCR Inspection
                          </button>
                          <a 
                            href={`http://localhost:8000/api/documents/${d.id}/file`} 
                            target="_blank" 
                            rel="noreferrer"
                            className="btn btn-secondary" 
                            style={{ padding: '4px 8px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
                          >
                            <Download size={13} /> View PDF
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* OCR & Cross-Validation Inspection Drawer */}
      {selectedDocId && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: '520px',
          height: '100vh',
          backgroundColor: '#ffffff',
          boxShadow: '-4px 0 20px rgba(0,0,0,0.2)',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          fontFamily: 'Inter, sans-serif'
        }}>
          <div style={{ padding: '16px 20px', backgroundColor: 'var(--primary-color)', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: '700', fontSize: '15px' }}><FileSearch size={18} style={{ verticalAlign: 'middle', marginRight: '6px' }} /> OCR Extractions & Discrepancies</span>
            <button onClick={() => setSelectedDocId(null)} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '18px', fontWeight: 'bold' }}>✕</button>
          </div>

          <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
            {loadingExtractions ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                <RefreshCw className="animate-spin" /> Processing document OCR analysis...
              </div>
            ) : docExtractions ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ padding: '12px', backgroundColor: docExtractions.consistency_score >= 90 ? '#f0fdf4' : '#fff5f5', borderLeft: `4px solid ${docExtractions.consistency_score >= 90 ? '#16a34a' : 'var(--danger-color)'}`, borderRadius: '4px' }}>
                  <div style={{ fontWeight: '700', fontSize: '13px', color: docExtractions.consistency_score >= 90 ? '#166534' : 'var(--danger-color)' }}>
                    AI Cross-Validation Score: {docExtractions.consistency_score.toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {docExtractions.consistency_score >= 90 ? 'All extracted fields strictly match system database records.' : 'Discrepancies detected between document OCR extractions and database records.'}
                  </div>
                </div>

                {/* Structured Extractions Table */}
                <div className="card" style={{ border: '1px solid var(--border-color)', boxShadow: 'none' }}>
                  <div className="card-header" style={{ padding: '10px 14px', fontSize: '12.5px', fontWeight: 'bold', backgroundColor: '#f8fafc' }}>
                    Cross-Validation Comparison Audit
                  </div>
                  <div className="card-body" style={{ padding: 0 }}>
                    {docExtractions.validations && docExtractions.validations.length > 0 ? (
                      <table className="data-table" style={{ fontSize: '11.5px' }}>
                        <thead>
                          <tr>
                            <th>Field</th>
                            <th>DB Record</th>
                            <th>Extracted Value</th>
                            <th>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {docExtractions.validations.map((v: any, idx: number) => (
                            <tr key={idx}>
                              <td style={{ fontWeight: 'bold' }}>{v.field}</td>
                              <td>{String(v.db_val)}</td>
                              <td>{String(v.extracted_val)}</td>
                              <td>
                                <span className={`badge ${v.status === 'MATCH' ? 'green' : 'red'}`} style={{ fontSize: '10px' }}>
                                  {v.status === 'MATCH' ? '✅ Match' : '❌ Mismatch'}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div style={{ padding: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>No validation mismatches detected.</div>
                    )}
                  </div>
                </div>

                {/* Structured Data JSON */}
                <div className="card" style={{ border: '1px solid var(--border-color)', boxShadow: 'none' }}>
                  <div className="card-header" style={{ padding: '10px 14px', fontSize: '12.5px', fontWeight: 'bold', backgroundColor: '#f8fafc' }}>
                    Extracted Structured Entities
                  </div>
                  <div className="card-body" style={{ padding: '12px', backgroundColor: '#1e293b', color: '#f8fafc', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px', maxHeight: '160px', overflowY: 'auto' }}>
                    <pre>{JSON.stringify(docExtractions.extracted_data, null, 2)}</pre>
                  </div>
                </div>

                {/* Raw OCR Text */}
                <div className="card" style={{ border: '1px solid var(--border-color)', boxShadow: 'none' }}>
                  <div className="card-header" style={{ padding: '10px 14px', fontSize: '12.5px', fontWeight: 'bold', backgroundColor: '#f8fafc' }}>
                    Raw Document Text (PDF OCR)
                  </div>
                  <div className="card-body" style={{ padding: '12px', backgroundColor: '#f8fafc', fontFamily: 'monospace', fontSize: '11px', maxHeight: '180px', overflowY: 'auto', whiteSpace: 'pre-wrap', border: '1px solid var(--border-color)', borderRadius: '4px' }}>
                    {docExtractions.ocr_text || 'No raw text extracted.'}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* Upload Agency PDF Modal */}
      {showUploadModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="card" style={{ width: '480px', backgroundColor: '#ffffff', borderRadius: '8px', padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ fontWeight: 'bold', fontSize: '16px', color: 'var(--primary-color)' }}>Upload Agency PDF Document</span>
              <button onClick={() => setShowUploadModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px' }}>✕</button>
            </div>
            
            <form onSubmit={handleUploadSubmit}>
              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Document Category</label>
                <select className="form-control" value={docType} onChange={e => setDocType(e.target.value)} required>
                  <option value="Sanction Order">Sanction Order</option>
                  <option value="Utilization Certificate">Utilization Certificate (UC)</option>
                  <option value="Work Order">Work Order</option>
                  <option value="Invoice">Invoice</option>
                  <option value="Inspection Report">Inspection Report</option>
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Associated Work ID (e.g. MPLADS-2026-0005)</label>
                <input type="text" className="form-control" placeholder="Leave empty for auto-extraction" value={workIdInput} onChange={e => setWorkIdInput(e.target.value)} />
              </div>

              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label">Select PDF Document File</label>
                <input type="file" className="form-control" accept=".pdf" onChange={handleFileChange} required />
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowUploadModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={uploading}>
                  {uploading ? 'Processing OCR Extraction...' : 'Upload & Run AI Audit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
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

  const isInvestigator = currentUser?.role_name === "Investigation Officer";

  return (
    <div className="card">
      {isInvestigator && (
        <div style={{ padding: '12px 16px', backgroundColor: '#f0fdf4', borderBottom: '1px solid #bbf7d0', color: '#166534', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <UserCheck size={16} />
          <span><strong>Investigator Priority Queue:</strong> Welcome, Officer {currentUser?.username}. Below are active cases assigned for evidence gathering, cross-validation, and resolution.</span>
        </div>
      )}
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

  const isAdmin = currentUser?.role_name === "Ministry Administrator";

  return (
    <div className="card">
      {!isAdmin && (
        <div style={{ padding: '12px 16px', backgroundColor: '#eff6ff', borderBottom: '1px solid #bfdbfe', color: '#1e40af', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={16} />
          <span><strong>View-Only Mode:</strong> Rule configurations and risk weights are managed nationally by the Ministry Administrator to maintain uniform evaluation across all states.</span>
        </div>
      )}
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="card-title"><Settings size={16} /> Compliance Rules Configurations</span>
        <div style={{ display: 'flex', gap: '10px' }}>
          {isAdmin && (
            <button className="btn btn-secondary" onClick={handleDownloadBackup} disabled={downloading}>
              {downloading ? 'Downloading...' : 'Export Database Backup'}
            </button>
          )}
          {isAdmin && (
            <button className="btn btn-primary" onClick={handleRunEvaluation} disabled={evaluating}>
              {evaluating ? 'Running Analysis...' : 'Evaluate Rules Engine'}
            </button>
          )}
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
                      <input 
                        type="checkbox" 
                        checked={r.enabled} 
                        disabled={!isAdmin} 
                        onChange={() => isAdmin && handleToggleRule(r.id, r.enabled)} 
                        style={{ cursor: isAdmin ? 'pointer' : 'not-allowed', width: '16px', height: '16px' }} 
                      />
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

// --- SYSTEM STATUS WIDGET (sidebar footer) ---
function SystemStatusWidget() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    api.getSystemStats().then(setStats).catch(() => {});
  }, []);

  if (!stats) return null;

  const mlColor = stats.ml_status === 'Operational' ? '#10b981' : (stats.ml_status === 'Partial' ? '#f59e0b' : '#ef4444');

  return (
    <div className="system-status-widget">
      <div className="system-status-header">
        <Server size={12} />
        <span>System Status</span>
        <span className="system-status-dot" style={{ backgroundColor: mlColor }}></span>
      </div>
      <div className="system-status-rows">
        <div className="system-status-row">
          <span>ML Engine</span>
          <span style={{ color: mlColor, fontWeight: '700' }}>{stats.ml_status}</span>
        </div>
        <div className="system-status-row">
          <span>Coverage</span>
          <span>{stats.ml_coverage_pct}%</span>
        </div>
        <div className="system-status-row">
          <span>Active Alerts</span>
          <span style={{ color: stats.critical_alerts > 0 ? '#ef4444' : 'inherit' }}>{stats.active_alerts}</span>
        </div>
        <div className="system-status-row">
          <span>DB</span>
          <span style={{ color: '#10b981' }}>{stats.db_status}</span>
        </div>
      </div>
    </div>
  );
}

// --- AGENCY INTELLIGENCE TAB ---
function AgencyIntelligenceTab({ onSelectProject }: any) {
  const [agencies, setAgencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<string>('risk_score');
  const [filter, setFilter] = useState('');

  useEffect(() => {
    api.getAgencyPerformance()
      .then(data => { setAgencies(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const COLORS = ['#ef4444', '#f59e0b', '#0284c7', '#10b981', '#6366f1', '#ec4899', '#14b8a6'];

  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px' }}><RefreshCw className="animate-spin" /> Loading agency data...</div>;
  }

  const sorted = [...agencies]
    .filter(a => a.name.toLowerCase().includes(filter.toLowerCase()))
    .sort((a, b) => b[sortKey] - a[sortKey]);

  const topAgencies = sorted.slice(0, 7);

  const riskBuckets = [
    { label: 'Critical (≥80)', count: agencies.filter(a => a.risk_score >= 80).length, color: '#ef4444' },
    { label: 'High (60-80)', count: agencies.filter(a => a.risk_score >= 60 && a.risk_score < 80).length, color: '#f59e0b' },
    { label: 'Medium (40-60)', count: agencies.filter(a => a.risk_score >= 40 && a.risk_score < 60).length, color: '#0284c7' },
    { label: 'Low (<40)', count: agencies.filter(a => a.risk_score < 40).length, color: '#10b981' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--primary-color)' }}>Agency Intelligence Dashboard</h2>
        <span className="badge blue">{agencies.length} Agencies Tracked</span>
      </div>

      {/* Summary stat cards */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <span className="stat-card-title">Total Agencies</span>
          <span className="stat-card-value">{agencies.length}</span>
          <span className="stat-card-subtitle">Implementing agencies in DB</span>
          <div className="stat-card-accent-bar blue"></div>
        </div>
        <div className="stat-card">
          <span className="stat-card-title">Critical Risk Agencies</span>
          <span className="stat-card-value" style={{ color: 'var(--danger-color)' }}>{riskBuckets[0].count}</span>
          <span className="stat-card-subtitle">Risk score ≥ 80</span>
          <div className="stat-card-accent-bar red"></div>
        </div>
        <div className="stat-card">
          <span className="stat-card-title">Avg Completion Rate</span>
          <span className="stat-card-value">{agencies.length > 0 ? (agencies.reduce((s, a) => s + a.completion_rate, 0) / agencies.length).toFixed(1) : 0}%</span>
          <span className="stat-card-subtitle">Across all agencies</span>
          <div className="stat-card-accent-bar green"></div>
        </div>
        <div className="stat-card">
          <span className="stat-card-title">Avg Delay (Days)</span>
          <span className="stat-card-value" style={{ color: 'var(--warning-color)' }}>
            {agencies.length > 0 ? (agencies.reduce((s, a) => s + a.average_delay_days, 0) / agencies.length).toFixed(0) : 0}
          </span>
          <span className="stat-card-subtitle">Average across agencies</span>
          <div className="stat-card-accent-bar orange"></div>
        </div>
      </div>

      <div className="grid-2-1">
        {/* Chart: Top agencies by risk score */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Building2 size={16} /> Top Agencies by Risk Score</span>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={topAgencies} margin={{ top: 5, right: 15, left: -10, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-30} textAnchor="end" />
                <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
                <Tooltip
                  formatter={(val: any, name: string) => [Number(val).toFixed(1), name === 'risk_score' ? 'Risk Score' : 'Completion Rate']}
                />
                <Legend verticalAlign="top" height={30} />
                <Bar dataKey="risk_score" name="risk_score" radius={[4,4,0,0]}>
                  {topAgencies.map((a, i) => (
                    <Cell key={i} fill={a.risk_score >= 80 ? '#ef4444' : a.risk_score >= 60 ? '#f59e0b' : '#0284c7'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right side: risk bucket pie + list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="card">
            <div className="card-header">
              <span className="card-title">Risk Distribution</span>
            </div>
            <div className="card-body">
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={riskBuckets} dataKey="count" nameKey="label" cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3}>
                    {riskBuckets.map((b, i) => <Cell key={i} fill={b.color} />)}
                  </Pie>
                  <Tooltip formatter={(val: any, name: string) => [val, name]} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', fontSize: '11px' }}>
                {riskBuckets.map((b, i) => (
                  <span key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: b.color, display: 'inline-block' }}></span>
                    {b.label}: <strong>{b.count}</strong>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agency Table */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <span className="card-title">Agency Performance Table</span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <input
              type="text"
              className="search-input"
              placeholder="Filter by name..."
              value={filter}
              onChange={e => setFilter(e.target.value)}
              style={{ width: '180px', fontSize: '12px' }}
            />
            <select className="filter-select" value={sortKey} onChange={e => setSortKey(e.target.value)}>
              <option value="risk_score">Sort: Risk Score ↓</option>
              <option value="average_delay_days">Sort: Avg Delay ↓</option>
              <option value="average_cost_deviation">Sort: Cost Deviation ↓</option>
              <option value="completion_rate">Sort: Completion Rate ↓</option>
            </select>
          </div>
        </div>
        <div className="card-body" style={{ padding: 0 }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Agency Name</th>
                <th>Projects</th>
                <th>Risk Score</th>
                <th>Completion Rate</th>
                <th>Avg Delay (days)</th>
                <th>Cost Deviation</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((a, i) => (
                <tr key={a.id}>
                  <td style={{ fontWeight: '600', color: 'var(--primary-color)' }}>{a.name}</td>
                  <td>{a.project_count}</td>
                  <td>
                    <span className={`badge ${a.risk_score >= 80 ? 'red' : a.risk_score >= 60 ? 'orange' : 'green'}`}>
                      {a.risk_score.toFixed(1)}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="progress-bar-container" style={{ width: '60px' }}>
                        <div className={`progress-bar-fill ${a.completion_rate >= 80 ? 'green' : a.completion_rate >= 50 ? 'orange' : 'red'}`} style={{ width: `${Math.min(100, a.completion_rate)}%` }}></div>
                      </div>
                      <span style={{ fontSize: '11px' }}>{a.completion_rate.toFixed(0)}%</span>
                    </div>
                  </td>
                  <td style={{ color: a.average_delay_days > 30 ? 'var(--danger-color)' : 'inherit' }}>
                    {a.average_delay_days.toFixed(0)} days
                  </td>
                  <td style={{ color: Math.abs(a.average_cost_deviation) > 20 ? 'var(--danger-color)' : 'inherit' }}>
                    {a.average_cost_deviation > 0 ? '+' : ''}{a.average_cost_deviation.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// --- AI ASSISTANT TAB (full-page promoted chatbot) ---
function AIAssistantTab({ input, setInput, messages, setMessages, onSelectProject }: any) {
  const [sending, setSending] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const SUGGESTED = [
    'Which projects have the highest risk score today?',
    'Show me delayed works in Chennai district',
    'Which agency has the most anomalies?',
    'List critical alerts for Tamil Nadu',
    'What is the average risk score by category?',
    'Find duplicate works in New Delhi',
  ];

  useEffect(() => {
    if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (queryText: string) => {
    if (!queryText.trim() || sending) return;
    setSending(true);
    setMessages((prev: any[]) => [...prev, { sender: 'user', text: queryText }]);
    setInput('');
    try {
      const res = await api.queryAI(queryText);
      const answer = res.answer || res.response || 'I could not find specific data for that query. Try rephrasing.';
      const sources = res.sources || res.results || [];
      setMessages((prev: any[]) => [...prev, { sender: 'bot', text: answer, sources }]);
    } catch {
      setMessages((prev: any[]) => [...prev, { sender: 'bot', text: 'System error: could not process request. Please check your query or try again.' }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 160px)', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '16px', fontWeight: '800', color: 'var(--primary-color)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bot size={20} /> Sentinel AI Assistant
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Ask natural language questions about MPLADS projects, risk scores, agencies, and anomalies.
          </p>
        </div>
        <button className="btn btn-secondary" style={{ fontSize: '12px' }} onClick={() => setMessages([{ sender: 'bot', text: 'Hello! I am Sentinel AI. How can I assist you with MPLADS project auditing today?' }])}>
          Clear History
        </button>
      </div>

      {/* Suggested queries */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {SUGGESTED.map((q, i) => (
          <button
            key={i}
            className="btn btn-secondary"
            style={{ fontSize: '11px', padding: '5px 10px', borderRadius: '20px' }}
            onClick={() => handleSend(q)}
            disabled={sending}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat messages */}
      <div className="card" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <div className="card-body" style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {messages.map((m: any, i: number) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: m.sender === 'user' ? 'flex-end' : 'flex-start', gap: '4px' }}>
              <div style={{
                maxWidth: '75%',
                padding: '10px 14px',
                borderRadius: m.sender === 'user' ? '16px 16px 4px 16px' : '4px 16px 16px 16px',
                backgroundColor: m.sender === 'user' ? 'var(--primary-color)' : 'var(--card-bg)',
                color: m.sender === 'user' ? '#ffffff' : 'var(--text-primary)',
                fontSize: '13px',
                lineHeight: '1.5',
                border: m.sender === 'bot' ? '1px solid var(--border-color)' : 'none',
                boxShadow: '0 1px 4px rgba(0,0,0,0.08)'
              }}>
                {m.sender === 'bot' && <Bot size={14} style={{ marginRight: '6px', opacity: 0.7, verticalAlign: 'middle' }} />}
                {m.text}
              </div>
              {m.sources && m.sources.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '75%' }}>
                  {m.sources.slice(0, 5).map((s: any, si: number) => (
                    <button
                      key={si}
                      className="btn btn-secondary"
                      style={{ fontSize: '10px', padding: '3px 8px', borderRadius: '12px' }}
                      onClick={() => onSelectProject(s.work_id || s.id)}
                    >
                      {s.work_id || s.id}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {sending && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '12px' }}>
              <RefreshCw size={12} className="animate-spin" /> Sentinel AI is thinking...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input area */}
        <form
          style={{ padding: '12px 16px', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '8px', alignItems: 'center' }}
          onSubmit={e => { e.preventDefault(); handleSend(input); }}
        >
          <input
            type="text"
            className="form-control"
            placeholder="Ask Sentinel AI anything about MPLADS data..."
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={sending}
            style={{ flex: 1, fontSize: '13px' }}
          />
          <button type="submit" className="btn btn-primary" disabled={sending} style={{ padding: '10px 20px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Send size={14} /> Send
          </button>
        </form>
      </div>
    </div>
  );
}
