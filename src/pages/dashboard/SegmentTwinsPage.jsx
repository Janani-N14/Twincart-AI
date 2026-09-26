import { useState, useEffect } from 'react';
import {
  Users, GraduationCap, Briefcase, Home, ShoppingBag,
  IndianRupee, TrendingUp, Smartphone, ChevronRight, X,
  Tag, Star, Target, Megaphone, Heart, Clock, RefreshCw, AlertCircle
} from 'lucide-react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip
} from 'recharts';
import PageHeader from '../../components/common/PageHeader';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getSegmentTwins } from '../../services/api';

/* ─── Static UI meta per segment id ─────────────────────── */
const SEGMENT_META = {
  students:    { icon: GraduationCap, color: 'from-sky-600/25 to-sky-900/10',      border: 'border-sky-500/30',     accent: 'text-sky-400'     },
  working:     { icon: Briefcase,     color: 'from-primary-600/25 to-primary-900/10', border: 'border-primary-500/30', accent: 'text-primary-400' },
  homemakers:  { icon: Home,          color: 'from-rose-600/25 to-rose-900/10',     border: 'border-rose-500/30',    accent: 'text-rose-400'    },
  budget:      { icon: ShoppingBag,   color: 'from-emerald-600/25 to-emerald-900/10',border:'border-emerald-500/30', accent: 'text-emerald-400' },
};
const FALLBACK_META = { icon: Users, color: 'from-gray-600/25 to-gray-900/10', border: 'border-gray-500/30', accent: 'text-gray-400' };

function getMeta(id) {
  const key = (id || '').toLowerCase().replace(/[\s_-]/g, '');
  if (key.includes('student'))   return SEGMENT_META.students;
  if (key.includes('work') || key.includes('professional')) return SEGMENT_META.working;
  if (key.includes('home') || key.includes('maker'))        return SEGMENT_META.homemakers;
  if (key.includes('budget'))    return SEGMENT_META.budget;
  return FALLBACK_META;
}

function normaliseSegment(s) {
  const meta = getMeta(s.id || s.segment_id || s.name || '');
  return {
    id:               s.id || s.segment_id || s.name,
    label:            s.name || s.label || s.segment_name || s.id,
    ageRange:         s.age_range        || s.ageRange        || '—',
    incomeRange:      s.income_range     || s.incomeRange     || '—',
    priceSensitivity: s.price_sensitivity ?? s.priceSensitivity ?? 0.65,
    size:             s.market_size      || s.size             || '—',
    description:      s.description      || '',
    topCategories:    s.top_categories   || s.topCategories    || [],
    preferredChannels:s.preferred_channels || s.preferredChannels || [],
    peakShoppingTime: s.peak_shopping_time || s.peakShoppingTime || '—',
    avgOrderValue:    s.avg_order_value  || s.avgOrderValue    || '—',
    campaigns:        s.campaign_count   || s.campaigns        || 0,
    convRate:         s.conversion_rate  ?? s.convRate         ?? 0.60,
    motivators:       s.motivators       || [],
    painPoints:       s.pain_points      || s.painPoints       || [],
    behavioural:      s.behavioural_profile || s.behavioural   || [
      { trait: 'Price Sensitivity', value: Math.round((s.price_sensitivity ?? 0.65) * 100) },
    ],
    categoryDemand:   (s.top_categories || s.topCategories || []).map((cat, i) => ({
      category: cat,
      demand:   [92, 82, 72, 65, 58][i] ?? 50,
    })),
    ...meta,
  };
}

/* ─── Segment Drawer ─────────────────────────────────────── */
function SegmentDrawer({ segment, onClose }) {
  const Icon = segment.icon;
  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-dark-800 border-l border-white/10 h-full overflow-y-auto animate-slide-in-right">
        <div className={`p-6 bg-gradient-to-br ${segment.color} border-b border-white/10`}>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 rounded-2xl bg-dark-800/60 border ${segment.border} flex items-center justify-center`}>
                <Icon size={24} className={segment.accent} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-white">{segment.label}</h2>
                <p className="text-sm text-gray-400 mt-0.5">Age {segment.ageRange} · {segment.size} users</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-xl transition-colors">
              <X size={18} className="text-gray-400" />
            </button>
          </div>
          {segment.description && (
            <p className="text-sm text-gray-300 mt-4 leading-relaxed">{segment.description}</p>
          )}
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Income Range',    value: segment.incomeRange,                             icon: IndianRupee },
              { label: 'Avg Order Value', value: segment.avgOrderValue,                           icon: ShoppingBag },
              { label: 'Campaigns Run',   value: segment.campaigns,                               icon: Megaphone   },
              { label: 'Conv. Rate',      value: `${(segment.convRate*100).toFixed(0)}%`,         icon: Target      },
            ].map(m => (
              <div key={m.label} className="card p-3 flex items-center gap-2.5">
                <m.icon size={16} className={segment.accent} />
                <div>
                  <p className="text-sm font-bold text-white">{m.value}</p>
                  <p className="text-[10px] text-gray-500">{m.label}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="card p-4">
            <div className="flex justify-between mb-2">
              <span className="text-sm font-semibold text-white">Price Sensitivity</span>
              <span className={`text-sm font-bold ${segment.accent}`}>{(segment.priceSensitivity * 100).toFixed(0)}%</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${segment.priceSensitivity * 100}%` }} />
            </div>
          </div>

          {segment.behavioural.length > 1 && (
            <div>
              <p className="text-sm font-semibold text-white mb-3">Behavioural Profile</p>
              <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={segment.behavioural} cx="50%" cy="50%">
                  <PolarGrid stroke="rgba(255,255,255,0.1)" />
                  <PolarAngleAxis dataKey="trait" tick={{ fill: '#6b7280', fontSize: 9 }} />
                  <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {segment.categoryDemand.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-white mb-3">Category Demand</p>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={segment.categoryDemand} layout="vertical" margin={{ left: 0, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" domain={[0,100]} tick={{ fill:'#6b7280',fontSize:10}} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="category" tick={{fill:'#9ca3af',fontSize:11}} axisLine={false} tickLine={false} width={70} />
                  <Tooltip contentStyle={{background:'#1a1a2e',border:'1px solid rgba(255,255,255,0.1)',borderRadius:12,fontSize:12}} cursor={{fill:'rgba(255,255,255,0.04)'}} />
                  <Bar dataKey="demand" fill="#6366f1" radius={[0,4,4,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {segment.preferredChannels.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <Smartphone size={14} className={segment.accent} /> Preferred Channels
              </p>
              <div className="flex flex-wrap gap-2">
                {segment.preferredChannels.map(c => <span key={c} className="badge-primary text-xs">{c}</span>)}
              </div>
            </div>
          )}

          {segment.peakShoppingTime !== '—' && (
            <div className="flex items-center gap-3 p-4 card">
              <Clock size={16} className="text-amber-400" />
              <div>
                <p className="text-sm font-semibold text-white">Peak Shopping Time</p>
                <p className="text-xs text-gray-400">{segment.peakShoppingTime}</p>
              </div>
            </div>
          )}

          {(segment.motivators.length > 0 || segment.painPoints.length > 0) && (
            <div className="grid grid-cols-2 gap-4">
              {segment.motivators.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Heart size={11} className="text-emerald-400" /> Motivators
                  </p>
                  <ul className="space-y-1.5">
                    {segment.motivators.map(m => (
                      <li key={m} className="flex items-start gap-2 text-xs text-gray-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />{m}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {segment.painPoints.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Target size={11} className="text-rose-400" /> Pain Points
                  </p>
                  <ul className="space-y-1.5">
                    {segment.painPoints.map(p => (
                      <li key={p} className="flex items-start gap-2 text-xs text-gray-300">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />{p}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Segment Card ──────────────────────────────────────── */
function SegmentCard({ segment, onClick, isSelected }) {
  const Icon = segment.icon;
  return (
    <div onClick={onClick}
      className={`card-hover p-6 bg-gradient-to-br ${segment.color} ${segment.border} cursor-pointer group ${isSelected ? 'ring-2 ring-primary-500/60' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-2xl bg-dark-800/60 border ${segment.border} flex items-center justify-center`}>
          <Icon size={24} className={segment.accent} />
        </div>
        <ChevronRight size={16} className="text-gray-600 group-hover:text-gray-300 group-hover:translate-x-0.5 transition-all" />
      </div>
      <h3 className="text-lg font-bold text-white mb-1">{segment.label}</h3>
      {segment.description && <p className="text-xs text-gray-400 mb-4 leading-relaxed line-clamp-2">{segment.description}</p>}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">Age Range</span>
          <span className="text-gray-200 font-medium">{segment.ageRange}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">Income</span>
          <span className="text-gray-200 font-medium text-right max-w-[60%]">{segment.incomeRange}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">Market Size</span>
          <span className={`font-bold ${segment.accent}`}>{segment.size}</span>
        </div>
        <div>
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-gray-500">Price Sensitivity</span>
            <span className="font-semibold text-white">{(segment.priceSensitivity * 100).toFixed(0)}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${segment.priceSensitivity * 100}%` }} />
          </div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-white/10">
        <div className="text-center">
          <p className="text-sm font-bold text-white">{segment.campaigns}</p>
          <p className="text-[10px] text-gray-500">Campaigns</p>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold text-white">{(segment.convRate * 100).toFixed(0)}%</p>
          <p className="text-[10px] text-gray-500">Conv. Rate</p>
        </div>
        <div className="text-center">
          <p className="text-sm font-bold text-white">{segment.avgOrderValue}</p>
          <p className="text-[10px] text-gray-500">Avg Order</p>
        </div>
      </div>
    </div>
  );
}

/* ─── Page ──────────────────────────────────────────────── */
export default function SegmentTwinsPage() {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState('');
  const [selected, setSelected] = useState(null);

  const fetchSegments = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getSegmentTwins();
      const list = Array.isArray(data) ? data : data.segments ?? data.data ?? [];
      setSegments(list.map(normaliseSegment));
    } catch (e) {
      setError(e.message || 'Failed to load segments from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSegments(); }, []);

  const totalCampaigns = segments.reduce((s, seg) => s + seg.campaigns, 0);
  const avgConv = segments.length
    ? (segments.reduce((s, seg) => s + seg.convRate, 0) / segments.length * 100).toFixed(1)
    : '0';

  return (
    <div className="page-container">
      <PageHeader
        title="Customer Segment Twins"
        subtitle="Canonical Indian buyer profiles with behavioural, income, and channel intelligence."
      >
        <button onClick={fetchSegments} className="btn-ghost text-sm" disabled={loading}>
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
        <span className="badge-primary">{segments.length} Segments</span>
      </PageHeader>

      {loading && (
        <div className="flex items-center justify-center py-20">
          <LoadingSpinner size="lg" text="Loading segment twins from backend…" />
        </div>
      )}

      {error && !loading && (
        <div className="card p-5 border-red-500/30 bg-red-500/10 flex items-center gap-3">
          <AlertCircle size={18} className="text-red-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-red-300">Backend connection failed</p>
            <p className="text-xs text-red-400 mt-0.5">{error}</p>
          </div>
          <button onClick={fetchSegments} className="ml-auto btn-ghost text-xs text-red-400">Retry</button>
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Total Segments',  value: segments.length, icon: Users,      color: 'text-primary-400' },
              { label: 'Market Reach',    value: '705M+',         icon: TrendingUp, color: 'text-emerald-400' },
              { label: 'Total Campaigns', value: totalCampaigns,  icon: Megaphone,  color: 'text-accent-400'  },
              { label: 'Avg Conv. Rate',  value: `${avgConv}%`,   icon: Target,     color: 'text-amber-400'   },
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

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {segments.map(s => (
              <SegmentCard key={s.id} segment={s}
                onClick={() => setSelected(s)} isSelected={selected?.id === s.id} />
            ))}
          </div>

          {/* Channel matrix */}
          {segments.length > 0 && (
            <div className="card p-6">
              <h3 className="section-title text-lg mb-1">Preferred Channel Matrix</h3>
              <p className="section-subtitle mb-5">Which segments respond to which channels</p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 text-xs font-medium text-gray-500 uppercase tracking-wider w-40">Channel</th>
                      {segments.map(s => (
                        <th key={s.id} className="text-center py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                          <div className="flex flex-col items-center gap-1">
                            <s.icon size={14} className={s.accent} />
                            {s.label.split(' ')[0]}
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {['WhatsApp','Instagram','Facebook','Google Ads','Email','YouTube','Push Notifications','SMS'].map(channel => (
                      <tr key={channel} className="hover:bg-white/3 transition-colors">
                        <td className="py-3 text-gray-300 font-medium">{channel}</td>
                        {segments.map(s => {
                          const preferred = s.preferredChannels.some(c =>
                            c.toLowerCase().includes(channel.toLowerCase()) ||
                            channel.toLowerCase().includes(c.toLowerCase())
                          );
                          return (
                            <td key={s.id} className="py-3 text-center">
                              {preferred
                                ? <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/30">
                                    <Star size={10} className="text-emerald-400 fill-emerald-400" />
                                  </span>
                                : <span className="inline-block w-2 h-2 rounded-full bg-gray-800 mx-auto" />
                              }
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {selected && <SegmentDrawer segment={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
