import { useState, useEffect } from 'react';
import {
  Globe, Search, MapPin, Thermometer, Tag,
  CalendarDays, TrendingUp, ChevronRight, X,
  IndianRupee, Users, Megaphone, Star, Filter,
  RefreshCw, AlertCircle
} from 'lucide-react';
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip
} from 'recharts';
import PageHeader from '../../components/common/PageHeader';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getRegionalTwins } from '../../services/api';

/* ─── UI helpers ─────────────────────────────────────────── */
const CARD_STYLES = [
  { color: 'from-rose-600/25 to-rose-800/10',     border: 'border-rose-500/25',    accent: 'text-rose-400'    },
  { color: 'from-blue-600/25 to-blue-800/10',     border: 'border-blue-500/25',    accent: 'text-blue-400'    },
  { color: 'from-amber-600/25 to-amber-800/10',   border: 'border-amber-500/25',   accent: 'text-amber-400'   },
  { color: 'from-purple-600/25 to-purple-800/10', border: 'border-purple-500/25',  accent: 'text-purple-400'  },
  { color: 'from-orange-600/25 to-orange-800/10', border: 'border-orange-500/25',  accent: 'text-orange-400'  },
  { color: 'from-teal-600/25 to-teal-800/10',     border: 'border-teal-500/25',    accent: 'text-teal-400'    },
  { color: 'from-emerald-600/25 to-emerald-800/10',border:'border-emerald-500/25', accent: 'text-emerald-400' },
  { color: 'from-yellow-600/25 to-yellow-800/10', border: 'border-yellow-500/25',  accent: 'text-yellow-400'  },
  { color: 'from-sky-600/25 to-sky-800/10',       border: 'border-sky-500/25',     accent: 'text-sky-400'     },
  { color: 'from-indigo-600/25 to-indigo-800/10', border: 'border-indigo-500/25',  accent: 'text-indigo-400'  },
  { color: 'from-pink-600/25 to-pink-800/10',     border: 'border-pink-500/25',    accent: 'text-pink-400'    },
  { color: 'from-lime-600/25 to-lime-800/10',     border: 'border-lime-500/25',    accent: 'text-lime-400'    },
  { color: 'from-cyan-600/25 to-cyan-800/10',     border: 'border-cyan-500/25',    accent: 'text-cyan-400'    },
  { color: 'from-violet-600/25 to-violet-800/10', border: 'border-violet-500/25',  accent: 'text-violet-400'  },
  { color: 'from-red-600/25 to-red-800/10',       border: 'border-red-500/25',     accent: 'text-red-400'     },
];

/* Normalise backend response → UI shape */
function normaliseRegion(r, idx) {
  const style = CARD_STYLES[idx % CARD_STYLES.length];
  return {
    id:              r.id || r.region_id || String(idx),
    state:           r.state || r.name || r.region_name || 'Unknown',
    capital:         r.capital || '—',
    language:        r.language || r.primary_language || '—',
    climate:         r.climate || r.climate_type || '—',
    priceSensitivity: r.price_sensitivity ?? r.priceSensitivity ?? 0.65,
    avgTemp:         r.avg_temperature_c ?? r.avgTemp ?? 27,
    topCategories:   r.top_categories   ?? r.topCategories   ?? [],
    festivals:       (r.festivals ?? []).map(f => ({
      name:   f.name,
      month:  f.month || f.timing || '',
      impact: f.retail_impact || f.impact || 'Medium',
    })),
    demandIndex:     r.demand_index   ?? r.demandIndex   ?? 60,
    campaigns:       r.campaign_count ?? r.campaigns     ?? 0,
    revenue:         r.revenue        ?? 0,
    tags:            r.tags           ?? [],
    ...style,
  };
}

const impactColor = {
  'Very High': 'badge-danger',
  'High':      'badge-warning',
  'Medium':    'badge-primary',
};

const psSentiment = ps =>
  ps >= 0.75 ? { label: 'Very Sensitive', cls: 'text-red-400'     } :
  ps >= 0.60 ? { label: 'Sensitive',      cls: 'text-amber-400'   } :
               { label: 'Moderate',       cls: 'text-emerald-400' };

/* ─── Detail Drawer ─────────────────────────────────────── */
function RegionDrawer({ region, onClose }) {
  const barData = (region.topCategories || []).map((cat, i) => ({
    name: cat, demand: [82, 75, 68, 55, 48][i] ?? 50,
  }));
  const ps = psSentiment(region.priceSensitivity);

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-dark-800 border-l border-white/10 h-full overflow-y-auto animate-slide-in-right">
        <div className={`p-6 bg-gradient-to-br ${region.color} border-b border-white/10`}>
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <MapPin size={16} className={region.accent} />
                <span className="text-xs text-gray-400">{region.capital}</span>
              </div>
              <h2 className="text-2xl font-black text-white">{region.state}</h2>
              <p className="text-sm text-gray-400 mt-1">{region.language} · {region.climate}</p>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-xl transition-colors">
              <X size={18} className="text-gray-400" />
            </button>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            {region.tags.map(t => <span key={t} className="badge-primary text-xs">{t}</span>)}
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Demand Index', value: region.demandIndex,                         icon: TrendingUp   },
              { label: 'Campaigns',    value: region.campaigns,                           icon: Megaphone    },
              { label: 'Revenue',      value: `₹${(region.revenue/1000).toFixed(0)}k`,   icon: IndianRupee  },
            ].map(m => (
              <div key={m.label} className="card p-3 text-center">
                <m.icon size={16} className={`${region.accent} mx-auto mb-1`} />
                <p className="text-lg font-bold text-white">{m.value}</p>
                <p className="text-[10px] text-gray-400 mt-0.5">{m.label}</p>
              </div>
            ))}
          </div>

          <div className="card p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-white">Price Sensitivity Index</span>
              <span className={`text-sm font-bold ${ps.cls}`}>{ps.label}</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${region.priceSensitivity * 100}%` }} />
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>Low (0.0)</span>
              <span className={`font-semibold ${ps.cls}`}>{region.priceSensitivity.toFixed(2)}</span>
              <span>High (1.0)</span>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 card">
            <Thermometer size={18} className="text-orange-400" />
            <div>
              <p className="text-sm font-semibold text-white">Avg. Temperature</p>
              <p className="text-xs text-gray-400">Annual mean: {region.avgTemp}°C — {region.climate}</p>
            </div>
            <span className="ml-auto text-2xl font-bold text-orange-400">{region.avgTemp}°</span>
          </div>

          {barData.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-white mb-3">Category Demand Index</p>
              <ResponsiveContainer width="100%" height={140}>
                <BarChart data={barData} layout="vertical" margin={{ left: 0, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} axisLine={false} tickLine={false} width={100} />
                  <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                  <Bar dataKey="demand" fill="#6366f1" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {region.festivals.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <CalendarDays size={15} className="text-primary-400" /> Active Festivals
              </p>
              <div className="space-y-2">
                {region.festivals.map(f => (
                  <div key={f.name} className="flex items-center justify-between p-3 card bg-dark-700/80">
                    <div>
                      <p className="text-sm font-medium text-white">{f.name}</p>
                      <p className="text-xs text-gray-500">{f.month}</p>
                    </div>
                    <span className={impactColor[f.impact] || 'badge-primary'}>{f.impact}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Region Card ───────────────────────────────────────── */
function RegionCard({ region, onClick }) {
  const ps = psSentiment(region.priceSensitivity);
  return (
    <div onClick={onClick} className={`card-hover p-5 bg-gradient-to-br ${region.color} ${region.border} cursor-pointer group`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-9 h-9 rounded-xl bg-dark-800/60 border ${region.border} flex items-center justify-center`}>
            <Globe size={17} className={region.accent} />
          </div>
          <div>
            <p className="font-semibold text-white text-sm">{region.state}</p>
            <p className="text-xs text-gray-500 flex items-center gap-1"><MapPin size={9} /> {region.capital}</p>
          </div>
        </div>
        <ChevronRight size={15} className="text-gray-600 group-hover:text-gray-300 group-hover:translate-x-0.5 transition-all" />
      </div>

      <div className="flex flex-wrap gap-1.5 mb-4">
        {region.tags.map(t => (
          <span key={t} className="badge bg-dark-800/60 border border-white/10 text-gray-400 text-[10px]">{t}</span>
        ))}
      </div>

      <div className="flex items-center gap-4 mb-4">
        <div className="w-16 h-16 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart cx="50%" cy="50%" innerRadius="55%" outerRadius="100%"
              startAngle={90} endAngle={90 - (360 * region.demandIndex / 100)}
              data={[{ value: region.demandIndex }]}>
              <RadialBar dataKey="value" cornerRadius={4} fill="#6366f1" background={{ fill: 'rgba(255,255,255,0.05)' }} />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>
        <div>
          <p className="text-2xl font-black text-white">{region.demandIndex}</p>
          <p className="text-xs text-gray-500">Demand Index</p>
          <p className={`text-xs font-medium mt-0.5 ${ps.cls}`}>{ps.label}</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-white/10">
        <div className="text-center">
          <p className="text-sm font-bold text-white">{region.campaigns}</p>
          <p className="text-[10px] text-gray-500">Campaigns</p>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold text-white">₹{(region.revenue/1000).toFixed(0)}k</p>
          <p className="text-[10px] text-gray-500">Revenue</p>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold text-white">{region.festivals.length}</p>
          <p className="text-[10px] text-gray-500">Festivals</p>
        </div>
      </div>
    </div>
  );
}

/* ─── Page ──────────────────────────────────────────────── */
export default function RegionalTwinsPage() {
  const [regions, setRegions]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState('');
  const [search, setSearch]     = useState('');
  const [sortBy, setSortBy]     = useState('demandIndex');
  const [filterPS, setFilterPS] = useState('all');
  const [selected, setSelected] = useState(null);

  const fetchRegions = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getRegionalTwins();
      const list = Array.isArray(data) ? data : data.regions ?? data.data ?? [];
      setRegions(list.map(normaliseRegion));
    } catch (e) {
      setError(e.message || 'Failed to load regions from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRegions(); }, []);

  const filtered = regions
    .filter(r =>
      r.state.toLowerCase().includes(search.toLowerCase()) ||
      r.language.toLowerCase().includes(search.toLowerCase()) ||
      r.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
    )
    .filter(r => {
      if (filterPS === 'high')   return r.priceSensitivity >= 0.75;
      if (filterPS === 'medium') return r.priceSensitivity >= 0.60 && r.priceSensitivity < 0.75;
      if (filterPS === 'low')    return r.priceSensitivity < 0.60;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'demandIndex') return b.demandIndex - a.demandIndex;
      if (sortBy === 'revenue')     return b.revenue - a.revenue;
      if (sortBy === 'campaigns')   return b.campaigns - a.campaigns;
      if (sortBy === 'ps')          return b.priceSensitivity - a.priceSensitivity;
      return 0;
    });

  return (
    <div className="page-container">
      <PageHeader
        title="Regional Digital Twins"
        subtitle="Indian state-level market twins with cultural, climate & festival context."
      >
        <button onClick={fetchRegions} className="btn-ghost text-sm" disabled={loading}>
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
        <span className="badge-primary">{regions.length} Regions</span>
      </PageHeader>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <LoadingSpinner size="lg" text="Loading regional twins from backend…" />
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="card p-5 border-red-500/30 bg-red-500/10 flex items-center gap-3">
          <AlertCircle size={18} className="text-red-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-red-300">Backend connection failed</p>
            <p className="text-xs text-red-400 mt-0.5">{error}</p>
          </div>
          <button onClick={fetchRegions} className="ml-auto btn-ghost text-xs text-red-400">Retry</button>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Summary bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Total Twins',       value: regions.length,                                                      icon: Globe,        color: 'text-primary-400'  },
              { label: 'Avg Demand Index',  value: regions.length ? Math.round(regions.reduce((s,r)=>s+r.demandIndex,0)/regions.length) : 0, icon: TrendingUp, color: 'text-emerald-400' },
              { label: 'Festivals Tracked', value: regions.reduce((s,r)=>s+r.festivals.length,0),                       icon: CalendarDays, color: 'text-amber-400'    },
              { label: 'Total Campaigns',   value: regions.reduce((s,r)=>s+r.campaigns,0),                              icon: Megaphone,    color: 'text-accent-400'   },
            ].map(m => (
              <div key={m.label} className="card p-4 flex items-center gap-3">
                <m.icon size={20} className={m.color} />
                <div>
                  <p className="text-xl font-bold text-white">{m.value}</p>
                  <p className="text-xs text-gray-500">{m.label}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
              <input value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search by state, language, or tag…" className="input-field pl-10 py-2.5" />
              {search && (
                <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white">
                  <X size={14} />
                </button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Filter size={15} className="text-gray-500" />
              <select value={filterPS} onChange={e => setFilterPS(e.target.value)} className="select-field py-2.5 w-44 text-sm">
                <option value="all">All Sensitivity</option>
                <option value="high">High (≥0.75)</option>
                <option value="medium">Medium (0.60–0.75)</option>
                <option value="low">Low (&lt;0.60)</option>
              </select>
              <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="select-field py-2.5 w-44 text-sm">
                <option value="demandIndex">Sort: Demand Index</option>
                <option value="revenue">Sort: Revenue</option>
                <option value="campaigns">Sort: Campaigns</option>
                <option value="ps">Sort: Price Sensitivity</option>
              </select>
            </div>
          </div>

          <p className="text-sm text-gray-500">
            Showing <span className="text-white font-medium">{filtered.length}</span> of {regions.length} regions
          </p>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map(r => <RegionCard key={r.id} region={r} onClick={() => setSelected(r)} />)}
            {filtered.length === 0 && (
              <div className="col-span-full flex flex-col items-center justify-center py-16 text-gray-500">
                <Globe size={36} className="mb-3 opacity-30" />
                <p className="text-base font-medium">No regions match your search</p>
                <button onClick={() => { setSearch(''); setFilterPS('all'); }} className="mt-3 text-sm text-primary-400 hover:text-primary-300">Clear filters</button>
              </div>
            )}
          </div>
        </>
      )}

      {selected && <RegionDrawer region={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
