import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import {
  TrendingUp, BarChart3, Target, Percent,
  IndianRupee, Globe, Calendar, Download
} from 'lucide-react';
import StatCard from '../../components/common/StatCard';
import PageHeader from '../../components/common/PageHeader';

const monthlyData = [
  { month: 'Jan', revenue: 42000, campaigns: 12, conversion: 58 },
  { month: 'Feb', revenue: 55000, campaigns: 18, conversion: 63 },
  { month: 'Mar', revenue: 48000, campaigns: 14, conversion: 61 },
  { month: 'Apr', revenue: 61000, campaigns: 22, conversion: 65 },
  { month: 'May', revenue: 73000, campaigns: 28, conversion: 70 },
  { month: 'Jun', revenue: 68000, campaigns: 25, conversion: 67 },
  { month: 'Jul', revenue: 85000, campaigns: 34, conversion: 72 },
  { month: 'Aug', revenue: 91000, campaigns: 40, conversion: 75 },
];

const stateRevenue = [
  { state: 'Tamil Nadu', revenue: 91000 },
  { state: 'Maharashtra', revenue: 74000 },
  { state: 'Karnataka', revenue: 61000 },
  { state: 'Gujarat', revenue: 53000 },
  { state: 'Rajasthan', revenue: 42000 },
  { state: 'West Bengal', revenue: 38000 },
  { state: 'Kerala', revenue: 35000 },
];

const radarData = [
  { metric: 'Campaign Quality', value: 85 },
  { metric: 'Forecast Accuracy', value: 82 },
  { metric: 'Conv. Rate', value: 75 },
  { metric: 'Cache Hit Rate', value: 65 },
  { metric: 'Agent Speed', value: 90 },
  { metric: 'Regional Coverage', value: 73 },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-dark-700 border border-white/15 rounded-xl p-3 text-xs shadow-card">
      <p className="text-gray-400 mb-1 font-medium">{label}</p>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-gray-300 capitalize">{p.name}:</span>
          <span className="text-white font-semibold">
            {p.name === 'revenue' ? `₹${(p.value/1000).toFixed(0)}k` :
             p.name === 'conversion' ? `${p.value}%` : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function AnalyticsPage() {
  return (
    <div className="page-container">
      <PageHeader
        title="Analytics"
        subtitle="Platform-wide performance metrics and trend analysis."
      >
        <button className="btn-secondary text-sm py-2">
          <Calendar size={15} /> Last 8 Months
        </button>
        <button className="btn-primary text-sm py-2">
          <Download size={15} /> Export Report
        </button>
      </PageHeader>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Revenue"   value="₹5.23L"  subtitle="8-month total"     icon={IndianRupee} trend="up"   trendValue="+18.4%"     color="primary" />
        <StatCard title="Campaigns Run"   value="193"     subtitle="All regions"        icon={BarChart3}   trend="up"   trendValue="+34 MoM"    color="accent"  />
        <StatCard title="Avg Conv. Rate"  value="67.3%"   subtitle="Across campaigns"   icon={Percent}     trend="up"   trendValue="+4.1%"      color="emerald" />
        <StatCard title="Regions Active"  value="11"      subtitle="Of 15 state twins"  icon={Globe}       trend="up"   trendValue="4 new"      color="sky"     />
      </div>

      {/* Revenue trend */}
      <div className="card p-6">
        <h3 className="section-title text-lg mb-1">Revenue Trend</h3>
        <p className="section-subtitle mb-6">Monthly revenue across all active regions</p>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={monthlyData} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
            <defs>
              <linearGradient id="aRevGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0}    />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${v/1000}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2.5} fill="url(#aRevGrad)" name="revenue" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Campaigns + Conversion */}
      <div className="grid lg:grid-cols-2 gap-5">
        <div className="card p-6">
          <h3 className="section-title text-lg mb-1">Campaigns per Month</h3>
          <p className="section-subtitle mb-6">Total campaigns generated by the AI pipeline</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={monthlyData} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
              <Bar dataKey="campaigns" name="campaigns" fill="#d946ef" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h3 className="section-title text-lg mb-1">Conversion Rate Trend</h3>
          <p className="section-subtitle mb-6">Average conversion rate over time</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={monthlyData} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} domain={[50, 80]} tickFormatter={v => `${v}%`} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="conversion" stroke="#10b981" strokeWidth={2.5} dot={{ fill: '#10b981', r: 4 }} name="conversion" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* State revenue + Radar */}
      <div className="grid lg:grid-cols-3 gap-5">
        <div className="card p-6 lg:col-span-2">
          <h3 className="section-title text-lg mb-1">Revenue by State</h3>
          <p className="section-subtitle mb-6">Top performing market twins</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={stateRevenue} layout="vertical" margin={{ top: 0, right: 20, bottom: 0, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${v/1000}k`} />
              <YAxis type="category" dataKey="state" tick={{ fill: '#9ca3af', fontSize: 11 }} axisLine={false} tickLine={false} width={90} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
              <Bar dataKey="revenue" name="revenue" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h3 className="section-title text-lg mb-1">Platform Score</h3>
          <p className="section-subtitle mb-4">AI performance across 6 dimensions</p>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData} cx="50%" cy="50%">
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: '#6b7280', fontSize: 9 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar name="Score" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
