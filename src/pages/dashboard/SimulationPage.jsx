import { useState, useEffect } from 'react';
import {
  FlaskConical, Play, RotateCcw, Zap, Calendar,
  CheckCircle, BarChart3, ArrowUpRight, ArrowDownRight,
  Minus, ChevronDown, Info, Clock, AlertCircle, RefreshCw
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, RadialBarChart, RadialBar, Cell
} from 'recharts';
import PageHeader from '../../components/common/PageHeader';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { runSimulation as runSimulationAPI, getRegionalTwins } from '../../services/api';

/* ─── Presets ───────────────────────────────────────────── */
const PRESETS = [
  { label: 'Festival Sale',    icon: '🎉', festivalActive: true,  budgetMultiplier: 1.5, stockOutRisk: 0.1, tempDelta: 0   },
  { label: 'Weather Dip',      icon: '🌧️', festivalActive: false, budgetMultiplier: 1.0, stockOutRisk: 0.2, tempDelta: 8   },
  { label: 'Budget Boost',     icon: '💰', festivalActive: false, budgetMultiplier: 2.0, stockOutRisk: 0.0, tempDelta: 0   },
  { label: 'Stock-out Crisis', icon: '⚠️', festivalActive: false, budgetMultiplier: 1.0, stockOutRisk: 0.8, tempDelta: 0   },
  { label: 'Perfect Storm',    icon: '🌟', festivalActive: true,  budgetMultiplier: 1.8, stockOutRisk: 0.0, tempDelta: 2   },
];

/* ─── Normalise backend result ──────────────────────────── */
function normaliseResult(data) {
  const conv    = data.conversion_rate   ?? data.convRate    ?? data.conv_rate    ?? 0;
  const revIdx  = data.revenue_index     ?? data.revenueIndex ?? data.rev_index   ?? 0;
  const summary = data.driver_summary    ?? data.summary      ?? data.explanation ?? '';

  // Factor breakdown
  const breakdown = data.factor_breakdown ?? data.breakdown ?? [
    { factor: 'Conversion Rate', contribution: +(conv * 100).toFixed(1) },
  ];

  return {
    convRate:     +(conv <= 1 ? conv * 100 : conv).toFixed(1),
    revenueIndex: +revIdx.toFixed(1),
    driverSummary: summary,
    breakdown: breakdown.map(b => ({
      factor:       b.factor        || b.name      || '',
      contribution: b.contribution  ?? b.value     ?? 0,
    })),
    raw: data,
  };
}

/* ─── Sub-components ─────────────────────────────────────── */
function SliderField({ label, value, onChange, min, max, step = 0.01, format, hint }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-300 flex items-center gap-1.5">
          {label}
          {hint && (
            <span className="group relative">
              <Info size={12} className="text-gray-600 cursor-help" />
              <span className="absolute bottom-5 left-1/2 -translate-x-1/2 w-48 p-2 bg-dark-700 border border-white/10 rounded-lg text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">{hint}</span>
            </span>
          )}
        </label>
        <span className="text-sm font-semibold text-primary-300">{format(value)}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-dark-800 rounded-full appearance-none cursor-pointer
          [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
          [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
          [&::-webkit-slider-thumb]:bg-primary-500 [&::-webkit-slider-thumb]:border-2
          [&::-webkit-slider-thumb]:border-primary-300 [&::-webkit-slider-thumb]:cursor-pointer
          [&::-webkit-slider-thumb]:shadow-glow-sm" />
      <div className="flex justify-between mt-1 text-[10px] text-gray-600">
        <span>{format(min)}</span><span>{format(max)}</span>
      </div>
    </div>
  );
}

function DeltaBadge({ value, label }) {
  const pos  = value > 0;
  const zero = value === 0;
  const Icon = zero ? Minus : pos ? ArrowUpRight : ArrowDownRight;
  return (
    <div className="flex items-center justify-between p-2.5 card bg-dark-700/60">
      <span className="text-xs text-gray-500">{label}</span>
      <span className={`flex items-center gap-1 text-xs font-bold ${zero ? 'text-gray-400' : pos ? 'text-emerald-400' : 'text-rose-400'}`}>
        <Icon size={12} />{Math.abs(value)}%
      </span>
    </div>
  );
}

function ResultGauge({ value, max = 100, label, color }) {
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-28">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart cx="50%" cy="50%" innerRadius="65%" outerRadius="100%"
            startAngle={90} endAngle={90 - (360 * Math.min(value, max) / max)}
            data={[{ value: Math.min(value, max) }]}>
            <RadialBar dataKey="value" cornerRadius={6} background={{ fill: 'rgba(255,255,255,0.05)' }}>
              <Cell fill={color} />
            </RadialBar>
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-black text-white">{value}</span>
          <span className="text-[10px] text-gray-500">{label === 'Conv. Rate' ? '%' : 'idx'}</span>
        </div>
      </div>
      <span className="text-xs text-gray-400 mt-2 font-medium">{label}</span>
    </div>
  );
}

/* ─── Page ──────────────────────────────────────────────── */
export default function SimulationPage() {
  const [regionOptions, setRegionOptions] = useState([]);
  const [regionId,      setRegionId]      = useState('');

  const [festivalActive,    setFestivalActive]    = useState(false);
  const [tempDelta,         setTempDelta]         = useState(0);
  const [budgetMultiplier,  setBudgetMultiplier]  = useState(1.0);
  const [stockOutRisk,      setStockOutRisk]      = useState(0.0);

  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');
  const [history, setHistory] = useState([]);

  // Load regions
  useEffect(() => {
    getRegionalTwins().then(data => {
      const list = Array.isArray(data) ? data : data.regions ?? data.data ?? [];
      setRegionOptions(list.map(r => ({ value: r.id || r.region_id, label: r.state || r.name || r.id })));
      if (list.length > 0) setRegionId(list[0].id || list[0].region_id);
    }).catch(() => {});
  }, []);

  const handlePreset = p => {
    setFestivalActive(p.festivalActive);
    setBudgetMultiplier(p.budgetMultiplier);
    setStockOutRisk(p.stockOutRisk);
    setTempDelta(p.tempDelta);
  };

  const handleReset = () => {
    setFestivalActive(false);
    setTempDelta(0);
    setBudgetMultiplier(1.0);
    setStockOutRisk(0.0);
    setResult(null);
    setError('');
  };

  const handleRun = async () => {
    if (!regionId) return;
    setLoading(true);
    setError('');
    try {
      const raw = await runSimulationAPI({
        region_id:              regionId,
        festival_next_week:     festivalActive,
        temperature_delta_c:    tempDelta,
        budget_multiplier:      budgetMultiplier,
        inventory_shortfall_pct: stockOutRisk,
      });
      const sim = normaliseResult(raw);
      setResult(sim);
      const regionLabel = regionOptions.find(r => r.value === regionId)?.label || regionId;
      setHistory(prev => [{
        label: `${regionLabel} · ${festivalActive ? 'Festival' : 'Normal'}`,
        convRate: sim.convRate,
        revenueIndex: sim.revenueIndex,
        time: new Date().toLocaleTimeString(),
      }, ...prev.slice(0, 4)]);
    } catch (e) {
      setError(e.message || 'Simulation request failed.');
    } finally {
      setLoading(false);
    }
  };

  const trend = result
    ? result.convRate >= 65 ? 'positive'
    : result.convRate >= 45 ? 'neutral' : 'negative'
    : null;

  return (
    <div className="page-container">
      <PageHeader
        title="Simulation Engine"
        subtitle="What-if predictions from the backend deterministic engine — under 200ms."
      >
        {result && (
          <span className="badge-success text-xs flex items-center gap-1.5">
            <Clock size={11} /> &lt;200ms
          </span>
        )}
      </PageHeader>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Controls ── */}
        <div className="space-y-5">
          <div className="card p-5 space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <FlaskConical size={15} className="text-primary-400" /> Simulation Parameters
            </h3>

            <div>
              <label className="label">Target Region</label>
              <div className="relative">
                <select value={regionId} onChange={e => setRegionId(e.target.value)} className="select-field text-sm pr-10">
                  {regionOptions.length === 0 && <option value="">Loading…</option>}
                  {regionOptions.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                </select>
                <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
              </div>
            </div>

            <div>
              <label className="label flex items-center gap-1.5">
                <Calendar size={13} className="text-amber-400" /> Festival Active (within 7 days)
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[true, false].map(v => (
                  <button key={String(v)} onClick={() => setFestivalActive(v)}
                    className={`py-2.5 text-sm font-medium rounded-xl border transition-all
                      ${festivalActive === v
                        ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                        : 'bg-dark-800 border-white/10 text-gray-400 hover:border-white/25'}`}>
                    {v ? '🎉 Yes (+25%)' : '✗ No'}
                  </button>
                ))}
              </div>
            </div>

            <SliderField label="Temperature Deviation (ΔT)" value={tempDelta} onChange={setTempDelta}
              min={-10} max={15} step={0.5} format={v => `${v > 0 ? '+' : ''}${v}°C`}
              hint="Deviation from seasonal average. Each degree changes conversion by -0.01." />
            <SliderField label="Budget Multiplier" value={budgetMultiplier} onChange={setBudgetMultiplier}
              min={0.5} max={3.0} step={0.1} format={v => `${v.toFixed(1)}×`}
              hint="Budget relative to baseline. +0.15 per unit above 1." />
            <SliderField label="Stock-out Risk (φ)" value={stockOutRisk} onChange={setStockOutRisk}
              min={0} max={1} step={0.05} format={v => `${(v * 100).toFixed(0)}%`}
              hint="Probability of stock-out. Each 10% reduces conversion by ~5%." />

            <button onClick={handleRun} disabled={loading || !regionId}
              className="btn-primary w-full justify-center py-3.5 disabled:opacity-60">
              {loading ? <><span className="spinner w-4 h-4" /> Simulating…</> : <><Play size={16} /> Run Simulation</>}
            </button>
            <button onClick={handleReset} className="btn-ghost w-full justify-center text-sm">
              <RotateCcw size={14} /> Reset
            </button>
          </div>

          {/* Presets */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-white mb-3">Scenario Presets</h3>
            <div className="space-y-2">
              {PRESETS.map(p => (
                <button key={p.label} onClick={() => handlePreset(p)}
                  className="w-full flex items-center gap-3 p-3 card-hover text-left">
                  <span className="text-lg">{p.icon}</span>
                  <span className="text-sm text-gray-300 font-medium">{p.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ── Results ── */}
        <div className="lg:col-span-2 space-y-5">
          {!result && !loading && !error && (
            <div className="card min-h-[460px] flex flex-col items-center justify-center gap-4 p-8">
              <div className="w-16 h-16 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
                <FlaskConical size={32} className="text-primary-400 opacity-60" />
              </div>
              <div className="text-center">
                <p className="text-base font-semibold text-gray-300">Configure & Run</p>
                <p className="text-sm text-gray-500 mt-1 max-w-xs">Adjust sliders or pick a preset, then hit Run Simulation to call the backend engine.</p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center mt-1">
                {PRESETS.slice(0, 3).map(p => (
                  <button key={p.label} onClick={() => handlePreset(p)}
                    className="badge bg-dark-800 border-white/10 text-gray-400 hover:text-white hover:border-white/25 transition-all cursor-pointer text-xs py-1 px-2.5">
                    {p.icon} {p.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {error && !loading && (
            <div className="card p-6 border-red-500/30 bg-red-500/10 flex items-start gap-3">
              <AlertCircle size={18} className="text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-300">Simulation failed</p>
                <p className="text-xs text-red-400 mt-1">{error}</p>
                <p className="text-xs text-gray-500 mt-2">Ensure the backend is running on port 8000.</p>
              </div>
              <button onClick={handleRun} className="ml-auto btn-ghost text-xs text-red-400"><RefreshCw size={13} /></button>
            </div>
          )}

          {loading && (
            <div className="card min-h-[460px] flex flex-col items-center justify-center gap-4 p-8">
              <LoadingSpinner size="lg" text="Calling backend simulation engine…" />
            </div>
          )}

          {result && !loading && (
            <div className="space-y-5 animate-fade-in">
              {/* Gauges */}
              <div className="card p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="section-title text-lg">Simulation Results</h3>
                    <p className="section-subtitle">Live prediction from backend engine</p>
                  </div>
                  <span className={`badge text-xs font-semibold border
                    ${trend === 'positive' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                      trend === 'neutral'  ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
                      'bg-rose-500/20 text-rose-300 border-rose-500/30'}`}>
                    {trend === 'positive' ? '✓ Strong' : trend === 'neutral' ? '~ Moderate' : '↓ Weak'}
                  </span>
                </div>
                <div className="flex items-center justify-around">
                  <ResultGauge value={result.convRate}     max={100} label="Conv. Rate"    color="#6366f1" />
                  <div className="w-px h-24 bg-white/10" />
                  <ResultGauge value={result.revenueIndex} max={200} label="Revenue Index" color="#d946ef" />
                </div>
              </div>

              {/* Breakdown chart */}
              {result.breakdown.length > 0 && (
                <div className="card p-6">
                  <h3 className="section-title text-lg mb-1">Factor Breakdown</h3>
                  <p className="section-subtitle mb-5">Contribution of each variable to the final conversion rate</p>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={result.breakdown} margin={{ top: 5, right: 15, bottom: 0, left: -15 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="factor" tick={{ fill: '#6b7280', fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} />
                      <Tooltip
                        contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12, fontSize: 12 }}
                        labelStyle={{ color: '#fff' }} formatter={v => [`${v}%`, 'Contribution']}
                        cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                      <Bar dataKey="contribution" radius={[4, 4, 0, 0]}>
                        {result.breakdown.map((entry, i) => (
                          <Cell key={i} fill={entry.contribution >= 0 ? '#6366f1' : '#ef4444'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Driver summary */}
              {result.driverSummary && (
                <div className="card p-5">
                  <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <Zap size={14} className="text-primary-400" /> Driver Summary
                  </h3>
                  <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">{result.driverSummary}</p>
                </div>
              )}

              {/* History */}
              {history.length > 1 && (
                <div className="card p-5">
                  <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <BarChart3 size={14} className="text-primary-400" /> Run History
                  </h3>
                  <div className="space-y-2">
                    {history.map((h, i) => (
                      <div key={i} className="flex items-center justify-between p-3 card bg-dark-700/60 text-xs">
                        <div>
                          <p className="text-gray-300 font-medium">{h.label}</p>
                          <p className="text-gray-600 mt-0.5">{h.time}</p>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-white font-bold">{h.convRate}%</p>
                            <p className="text-gray-500">Conv.</p>
                          </div>
                          <div className="text-right">
                            <p className="text-primary-400 font-bold">{h.revenueIndex}</p>
                            <p className="text-gray-500">Rev. Idx</p>
                          </div>
                        </div>
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
  );
}
