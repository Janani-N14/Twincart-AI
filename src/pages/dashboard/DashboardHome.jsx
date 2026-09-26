import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  TrendingUp, Globe, Megaphone, FlaskConical,
  Users, Brain, ArrowRight, CheckCircle, Clock,
  Zap, BarChart3, Activity, AlertTriangle, RefreshCw,
  ShoppingBag, Target, IndianRupee, Percent
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart,
  Pie, Cell, Legend
} from 'recharts';
import { useAuth } from '../../context/AuthContext';
import StatCard from '../../components/common/StatCard';
import PageHeader from '../../components/common/PageHeader';
import { healthCheck, getRegionalTwins, getSegmentTwins } from '../../services/api';

/* ─── Mock data ─────────────────────────────────────────── */
const salesData = [
  { month: 'Jan', revenue: 42000, campaigns: 12, forecast: 44000 },
  { month: 'Feb', revenue: 55000, campaigns: 18, forecast: 52000 },
  { month: 'Mar', revenue: 48000, campaigns: 14, forecast: 50000 },
  { month: 'Apr', revenue: 61000, campaigns: 22, forecast: 63000 },
  { month: 'May', revenue: 73000, campaigns: 28, forecast: 70000 },
  { month: 'Jun', revenue: 68000, campaigns: 25, forecast: 72000 },
  { month: 'Jul', revenue: 85000, campaigns: 34, forecast: 82000 },
  { month: 'Aug', revenue: 91000, campaigns: 40, forecast: 88000 },
];

const channelData = [
  { name: 'Social Media', value: 38, color: '#6366f1' },
  { name: 'Search Ads',   value: 27, color: '#d946ef' },
  { name: 'Push Notif.',  value: 16, color: '#06b6d4' },
  { name: 'Email',        value: 12, color: '#10b981' },
  { name: 'Influencer',   value: 7,  color: '#f59e0b' },
];

const regionPerformance = [
  { region: 'Tamil Nadu',  campaigns: 24, convRate: 0.72, revenue: 91000 },
  { region: 'Maharashtra', campaigns: 18, convRate: 0.65, revenue: 74000 },
  { region: 'Karnataka',   campaigns: 15, convRate: 0.68, revenue: 61000 },
  { region: 'Gujarat',     campaigns: 12, convRate: 0.61, revenue: 53000 },
  { region: 'Rajasthan',   campaigns: 9,  convRate: 0.58, revenue: 42000 },
];

const recentActivity = [
  { id: 1, type: 'campaign',   icon: Megaphone,   text: 'Campaign generated for Tamil Nadu — Homemakers', time: '2m ago',  status: 'success' },
  { id: 2, type: 'forecast',   icon: TrendingUp,  text: 'Demand forecast updated for Diwali season',      time: '18m ago', status: 'success' },
  { id: 3, type: 'simulation', icon: FlaskConical, text: 'What-if simulation: +15% budget scenario run',  time: '1h ago',  status: 'success' },
  { id: 4, type: 'gap',        icon: AlertTriangle, text: 'Catalog gap detected in Electronics — Kerala', time: '3h ago',  status: 'warning' },
  { id: 5, type: 'campaign',   icon: Megaphone,   text: 'Campaign generated for Karnataka — Students',    time: '5h ago',  status: 'success' },
  { id: 6, type: 'intel',      icon: Brain,       text: 'Seller Q&A answered: "Best category for Onam"',  time: '1d ago',  status: 'success' },
];

const agentStatus = [
  { name: 'Trend Detection',      latency: '0.8s',  status: 'active',   load: 72 },
  { name: 'Weather & Festival',   latency: '0.3s',  status: 'active',   load: 45 },
  { name: 'Catalog Gap',          latency: '0.9s',  status: 'active',   load: 60 },
  { name: 'Demand Forecasting',   latency: '1.2s',  status: 'active',   load: 85 },
  { name: 'Campaign Generator',   latency: '1.8s',  status: 'active',   load: 91 },
  { name: 'Banner Studio',        latency: '0.5s',  status: 'active',   load: 55 },
  { name: 'Budget Optimizer',     latency: '0.4s',  status: 'active',   load: 38 },
  { name: 'Explainability',       latency: '0.3s',  status: 'active',   load: 30 },
  { name: 'Seller Intelligence',  latency: '1.1s',  status: 'idle',     load: 15 },
];

/* ─── Sub-components ────────────────────────────────────── */
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-dark-700 border border-white/15 rounded-xl p-3 text-xs shadow-card">
      <p className="text-gray-400 mb-2 font-medium">{label}</p>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-gray-300">{p.name}:</span>
          <span className="text-white font-semibold">
            {p.name === 'revenue' || p.name === 'forecast' ? `₹${(p.value/1000).toFixed(0)}k` : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

const PieTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-dark-700 border border-white/15 rounded-xl p-3 text-xs shadow-card">
      <p className="text-white font-semibold">{payload[0].name}</p>
      <p className="text-primary-400">{payload[0].value}% budget share</p>
    </div>
  );
};

function AgentStatusRow({ name, latency, status, load }) {
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-white/5 last:border-0">
      <span className={`w-2 h-2 rounded-full shrink-0 ${status === 'active' ? 'bg-emerald-400 animate-pulse-slow' : 'bg-gray-600'}`} />
      <span className="text-sm text-gray-300 flex-1 truncate">{name}</span>
      <span className="text-xs text-gray-500 w-10 text-right">{latency}</span>
      <div className="w-20 h-1.5 bg-dark-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${load > 80 ? 'bg-amber-500' : 'bg-primary-500'}`}
          style={{ width: `${load}%` }}
        />
      </div>
      <span className="text-xs text-gray-500 w-8 text-right">{load}%</span>
    </div>
  );
}

function QuickActionCard({ icon: Icon, label, desc, to, color }) {
  const colorMap = {
    primary: 'from-primary-600/20 to-primary-800/10 border-primary-500/25 hover:border-primary-400/50 text-primary-400',
    accent:  'from-accent-600/20 to-accent-800/10 border-accent-500/25 hover:border-accent-400/50 text-accent-400',
    emerald: 'from-emerald-600/20 to-emerald-800/10 border-emerald-500/25 hover:border-emerald-400/50 text-emerald-400',
    sky:     'from-sky-600/20 to-sky-800/10 border-sky-500/25 hover:border-sky-400/50 text-sky-400',
  };
  return (
    <Link to={to} className={`card-hover p-5 bg-gradient-to-br ${colorMap[color]} group flex flex-col gap-3`}>
      <div className={`w-10 h-10 rounded-xl bg-dark-800/60 border border-current/20 flex items-center justify-center`}>
        <Icon size={20} className="text-current" />
      </div>
      <div>
        <p className="text-sm font-semibold text-white">{label}</p>
        <p className="text-xs text-gray-400 mt-0.5">{desc}</p>
      </div>
      <div className="flex items-center gap-1 text-xs font-medium text-current">
        Open <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
      </div>
    </Link>
  );
}

/* ─── Page ──────────────────────────────────────────────── */
export default function DashboardHome() {
  const { user } = useAuth();
  const [refreshing, setRefreshing]         = useState(false);
  const [backendStatus, setBackendStatus]   = useState('checking'); // 'online' | 'offline' | 'checking'
  const [regionCount,  setRegionCount]      = useState('—');
  const [segmentCount, setSegmentCount]     = useState('—');

  const checkBackend = async () => {
    try {
      await healthCheck();
      setBackendStatus('online');
    } catch {
      setBackendStatus('offline');
    }
    try {
      const rData = await getRegionalTwins();
      const list  = Array.isArray(rData) ? rData : rData.regions ?? rData.data ?? [];
      setRegionCount(list.length);
    } catch {}
    try {
      const sData = await getSegmentTwins();
      const list  = Array.isArray(sData) ? sData : sData.segments ?? sData.data ?? [];
      setSegmentCount(list.length);
    } catch {}
  };

  useEffect(() => { checkBackend(); }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await checkBackend();
    setRefreshing(false);
  };

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="page-container">
      <PageHeader
        title={`${greeting}, ${user?.name || 'Seller'} 👋`}
        subtitle="Here's your TwinCart-AI intelligence overview for today."
      >
        <div className="flex items-center gap-2">
          <span className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border font-medium
            ${backendStatus === 'online'   ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' :
              backendStatus === 'offline'  ? 'bg-red-500/15 text-red-400 border-red-500/30' :
              'bg-gray-500/15 text-gray-400 border-gray-500/30'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${backendStatus === 'online' ? 'bg-emerald-400 animate-pulse-slow' : backendStatus === 'offline' ? 'bg-red-400' : 'bg-gray-400 animate-pulse'}`} />
            Backend {backendStatus === 'checking' ? 'checking…' : backendStatus}
          </span>
        </div>
        <button
          onClick={handleRefresh}
          className="btn-ghost text-sm"
        >
          <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
          Refresh
        </button>
        <Link to="/dashboard/campaigns" className="btn-primary text-sm py-2">
          <Zap size={15} /> Generate Campaign
        </Link>
      </PageHeader>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Revenue"
          value="₹5.23L"
          subtitle="Last 8 months"
          icon={IndianRupee}
          trend="up"
          trendValue="+18.4% vs last period"
          color="primary"
        />
        <StatCard
          title="Campaigns Run"
          value="193"
          subtitle="Across 11 regions"
          icon={Megaphone}
          trend="up"
          trendValue="+34 this month"
          color="accent"
        />
        <StatCard
          title="Avg. Conv. Rate"
          value="67.3%"
          subtitle="Across all campaigns"
          icon={Percent}
          trend="up"
          trendValue="+4.1% improvement"
          color="emerald"
        />
        <StatCard
          title="Active Regions"
          value={`${regionCount} / ${segmentCount === '—' ? '—' : 4}`}
          subtitle="Twins live from backend"
          icon={Globe}
          trend="up"
          trendValue={`${segmentCount} segments`}
          color="sky"
        />
      </div>

      {/* ── Charts row ── */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Revenue + Forecast chart */}
        <div className="card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="section-title text-lg">Revenue vs Forecast</h3>
              <p className="section-subtitle">Actual revenue against XGBoost demand forecast</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-gray-400">
                <span className="w-3 h-0.5 bg-primary-400 rounded" /> Actual
              </span>
              <span className="flex items-center gap-1.5 text-gray-400">
                <span className="w-3 h-0.5 bg-accent-400 rounded" style={{borderStyle:'dashed'}} /> Forecast
              </span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={salesData} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
              <defs>
                <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="fcGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#d946ef" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#d946ef" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false}
                tickFormatter={v => `₹${v/1000}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="revenue"  stroke="#6366f1" strokeWidth={2} fill="url(#revGrad)" name="revenue" />
              <Area type="monotone" dataKey="forecast" stroke="#d946ef" strokeWidth={2} fill="url(#fcGrad)" strokeDasharray="5 3" name="forecast" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Channel budget pie */}
        <div className="card p-6">
          <div className="mb-5">
            <h3 className="section-title text-lg">Channel Budget Split</h3>
            <p className="section-subtitle">Recommended allocation</p>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={channelData} cx="50%" cy="50%" innerRadius={45} outerRadius={70}
                paddingAngle={3} dataKey="value">
                {channelData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} stroke="transparent" />
                ))}
              </Pie>
              <Tooltip content={<PieTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-2">
            {channelData.map(c => (
              <div key={c.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ background: c.color }} />
                  <span className="text-gray-400">{c.name}</span>
                </div>
                <span className="text-gray-200 font-medium">{c.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Campaign bar chart + Agent status ── */}
      <div className="grid lg:grid-cols-2 gap-5">
        {/* Campaigns per month bar */}
        <div className="card p-6">
          <div className="mb-5">
            <h3 className="section-title text-lg">Campaigns Generated</h3>
            <p className="section-subtitle">Monthly campaign output volume</p>
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={salesData} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
              <Bar dataKey="campaigns" name="campaigns" fill="#6366f1" radius={[4, 4, 0, 0]}>
                {salesData.map((_, i) => (
                  <Cell key={i} fill={i === salesData.length - 1 ? '#d946ef' : '#6366f1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Agent status panel */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="section-title text-lg">Agent Pipeline Status</h3>
              <p className="section-subtitle">9-node LangGraph health</p>
            </div>
            <span className="badge-success">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              {backendStatus === 'online' ? 'All Active' : backendStatus === 'offline' ? 'Offline' : 'Checking…'}
            </span>
          </div>
          <div className="space-y-0 max-h-56 overflow-y-auto pr-1">
            {agentStatus.map(a => <AgentStatusRow key={a.name} {...a} />)}
          </div>
        </div>
      </div>

      {/* ── Region performance table + recent activity ── */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Region table */}
        <div className="card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="section-title text-lg">Regional Performance</h3>
              <p className="section-subtitle">Top performing market twins</p>
            </div>
            <Link to="/dashboard/regional-twins" className="btn-ghost text-xs">
              View All <ArrowRight size={12} />
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 pb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Region</th>
                  <th className="text-right py-2 pb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Campaigns</th>
                  <th className="text-right py-2 pb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Conv. Rate</th>
                  <th className="text-right py-2 pb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                  <th className="text-right py-2 pb-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {regionPerformance.map(r => (
                  <tr key={r.region} className="hover:bg-white/3 transition-colors">
                    <td className="py-3 font-medium text-white">{r.region}</td>
                    <td className="py-3 text-right text-gray-300">{r.campaigns}</td>
                    <td className="py-3 text-right">
                      <span className={`font-semibold ${r.convRate >= 0.7 ? 'text-emerald-400' : r.convRate >= 0.6 ? 'text-amber-400' : 'text-gray-400'}`}>
                        {(r.convRate * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="py-3 text-right text-gray-300">₹{(r.revenue / 1000).toFixed(0)}k</td>
                    <td className="py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-20 h-1.5 bg-dark-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary-600 to-accent-500 rounded-full"
                            style={{ width: `${(r.revenue / 91000) * 100}%` }}
                          />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent activity */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="section-title text-lg">Recent Activity</h3>
              <p className="section-subtitle">Latest platform events</p>
            </div>
          </div>
          <div className="space-y-0">
            {recentActivity.map(item => (
              <div key={item.id} className="flex items-start gap-3 py-2.5 border-b border-white/5 last:border-0">
                <div className={`mt-0.5 p-1.5 rounded-lg shrink-0 ${item.status === 'warning' ? 'bg-amber-500/15' : 'bg-primary-500/15'}`}>
                  <item.icon size={13} className={item.status === 'warning' ? 'text-amber-400' : 'text-primary-400'} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-300 leading-snug line-clamp-2">{item.text}</p>
                  <p className="text-[10px] text-gray-600 mt-1 flex items-center gap-1">
                    <Clock size={9} /> {item.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Quick actions ── */}
      <div>
        <h3 className="section-title text-lg mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickActionCard icon={Megaphone}      label="Generate Campaign"     desc="Create hyperlocal campaign copy"         to="/dashboard/campaigns"    color="primary" />
          <QuickActionCard icon={FlaskConical}   label="Run Simulation"        desc="What-if scenario analysis"              to="/dashboard/simulation"   color="accent"  />
          <QuickActionCard icon={Globe}          label="Explore Regions"       desc="Browse 15 state market twins"           to="/dashboard/regional-twins" color="sky"  />
          <QuickActionCard icon={Brain}          label="Ask Seller Intel"      desc="Free-form AI Q&A for your store"        to="/dashboard/seller-intel" color="emerald" />
        </div>
      </div>
    </div>
  );
}
