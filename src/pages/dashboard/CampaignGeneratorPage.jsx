import { useState, useEffect } from 'react';
import {
  Megaphone, Zap, Globe, Users, ChevronDown,
  Copy, RefreshCw, CheckCircle, Sparkles,
  Image, BarChart3, Brain, Tag,
  TrendingUp, Clock, Star, AlertCircle
} from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { generateCampaign, getRegionalTwins, getSegmentTwins } from '../../services/api';

/* ─── Pipeline steps (visual only — real timing comes from backend) ── */
const PIPELINE_STEPS = [
  'Trend Detection', 'Weather & Festival', 'Catalog Gap',
  'Demand Forecasting', 'Campaign Generator', 'Banner Studio',
  'Budget Optimizer', 'Explainability',
];

/* ─── Normalise backend response ─────────────────────────── */
function normaliseCampaign(data) {
  // copy_lines or campaign_copy or lines array
  const copyLines =
    data.copy_lines   ?? data.campaign_copy ?? data.copy ?? data.lines ??
    (data.campaign?.copy_lines) ?? [];

  // banner_briefs or banners array
  const bannerBriefs =
    data.banner_briefs ?? data.banners ?? data.visual_briefs ??
    (data.campaign?.banner_briefs) ?? [];

  // budget_allocation object or channel_budget
  const budgetAllocation =
    data.budget_allocation ?? data.channel_budget ?? data.budget ??
    (data.campaign?.budget_allocation) ?? {};

  // demand_index object
  const demandIndex =
    data.demand_index ?? data.demand ?? (data.campaign?.demand_index) ?? {};

  // explanation string
  const explainability =
    data.explanation ?? data.explainability ?? data.rationale ??
    data.explanation_log?.join(' ') ?? '';

  const latency = data.latency_s ?? data.latency ?? data.generation_time ?? '~3–5';

  return { copyLines, bannerBriefs, budgetAllocation, demandIndex, explainability, latency };
}

/* ─── Sub-components ─────────────────────────────────────── */
function SelectField({ label, value, onChange, options, placeholder, loading: ld }) {
  return (
    <div>
      <label className="label">{label}</label>
      <div className="relative">
        <select value={value} onChange={e => onChange(e.target.value)}
          className="select-field pr-10 text-sm" disabled={ld}>
          <option value="">{ld ? 'Loading…' : placeholder}</option>
          {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
      </div>
    </div>
  );
}

function CopyLineCard({ line, index }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => { navigator.clipboard.writeText(line); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (
    <div className="flex items-start gap-3 p-4 card bg-dark-700/80 group hover:border-primary-500/30 transition-all">
      <span className="w-6 h-6 rounded-full bg-primary-500/20 border border-primary-500/30 flex items-center justify-center text-xs font-bold text-primary-400 shrink-0 mt-0.5">{index + 1}</span>
      <p className="flex-1 text-sm text-gray-200 leading-relaxed">{line}</p>
      <button onClick={handleCopy} className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-white/10 rounded-lg">
        {copied ? <CheckCircle size={14} className="text-emerald-400" /> : <Copy size={14} className="text-gray-400" />}
      </button>
    </div>
  );
}

function BannerBriefCard({ brief, index }) {
  const palette = brief.palette || brief.color_palette || brief.colors || [];
  const headline = brief.headline || brief.title || '';
  const subtext  = brief.subtext  || brief.subtitle || brief.description || '';
  const cta      = brief.cta      || brief.call_to_action || 'Shop Now';
  const imagery  = brief.imagery  || brief.image_hint || '';
  return (
    <div className="card p-5 space-y-3">
      <div className="flex items-center justify-between">
        <span className="badge-primary text-xs">Banner {index + 1}</span>
        <div className="flex gap-1">
          {palette.map((c, i) => <span key={i} className="w-4 h-4 rounded-full border border-white/20" style={{ background: c }} />)}
        </div>
      </div>
      <div>
        <p className="text-sm font-bold text-white">{headline}</p>
        {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
      </div>
      <div className="flex items-center justify-between pt-2 border-t border-white/10">
        <span className="inline-flex items-center gap-1.5 text-xs px-3 py-1 bg-primary-600/20 border border-primary-500/30 rounded-lg text-primary-300 font-medium">CTA: {cta}</span>
        {imagery && (
          <span className="flex items-center gap-1 text-xs text-gray-500">
            <Image size={11} />
            <span className="truncate max-w-[140px]" title={imagery}>{imagery.substring(0, 30)}…</span>
          </span>
        )}
      </div>
    </div>
  );
}

function BudgetBar({ channel, pct }) {
  const colors = {
    'social_media': 'from-primary-600 to-primary-500', 'social media': 'from-primary-600 to-primary-500',
    'search_ads':   'from-accent-600 to-accent-500',   'search ads':   'from-accent-600 to-accent-500',
    'push_notifications':'from-sky-600 to-sky-500',    'push notifications':'from-sky-600 to-sky-500',
    'email':        'from-emerald-600 to-emerald-500',
    'influencer':   'from-amber-600 to-amber-500',
  };
  const label = channel.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  const key = channel.toLowerCase();
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-400 w-40 shrink-0 capitalize">{label}</span>
      <div className="flex-1 h-2.5 bg-dark-800 rounded-full overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${colors[key] || 'from-primary-600 to-primary-500'} rounded-full transition-all duration-700`}
          style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-semibold text-white w-10 text-right">{typeof pct === 'number' ? pct.toFixed(0) : pct}%</span>
    </div>
  );
}

function PipelineProgress({ step }) {
  return (
    <div className="space-y-2.5">
      {PIPELINE_STEPS.map((s, i) => (
        <div key={s} className="flex items-center gap-3">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 border transition-all duration-300
            ${i < step ? 'bg-emerald-500 border-emerald-500' : i === step ? 'bg-primary-600 border-primary-400 animate-pulse' : 'bg-transparent border-white/20'}`}>
            {i < step
              ? <CheckCircle size={12} className="text-white" />
              : <span className="text-[9px] text-gray-400">{i + 1}</span>}
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className={`text-xs transition-colors ${i <= step ? 'text-gray-200' : 'text-gray-600'}`}>{s}</span>
              {i < step  && <span className="text-[10px] text-emerald-400">✓ Done</span>}
              {i === step && <span className="text-[10px] text-primary-400 animate-pulse">Running…</span>}
            </div>
            {i === step && (
              <div className="mt-1 h-1 bg-dark-800 rounded-full overflow-hidden">
                <div className="h-full bg-primary-500 rounded-full animate-pulse" style={{ width: '60%' }} />
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── Page ──────────────────────────────────────────────── */
export default function CampaignGeneratorPage() {
  const [regionOptions,  setRegionOptions]  = useState([]);
  const [segmentOptions, setSegmentOptions] = useState([]);
  const [optionsLoading, setOptionsLoading] = useState(true);

  const [regionId,  setRegionId]  = useState('');
  const [segmentId, setSegmentId] = useState('');

  const [loading,      setLoading]      = useState(false);
  const [pipelineStep, setPipelineStep] = useState(-1);
  const [result,       setResult]       = useState(null);
  const [error,        setError]        = useState('');
  const [activeTab,    setActiveTab]    = useState('copy');
  const [allCopied,    setAllCopied]    = useState(false);

  /* Load region + segment options from backend */
  useEffect(() => {
    (async () => {
      setOptionsLoading(true);
      try {
        const [rData, sData] = await Promise.all([getRegionalTwins(), getSegmentTwins()]);
        const rList = Array.isArray(rData) ? rData : rData.regions ?? rData.data ?? [];
        const sList = Array.isArray(sData) ? sData : sData.segments ?? sData.data ?? [];
        setRegionOptions(rList.map(r => ({
          value: r.id || r.region_id,
          label: r.state || r.name || r.region_name || r.id,
        })));
        setSegmentOptions(sList.map(s => ({
          value: s.id || s.segment_id,
          label: s.name || s.label || s.segment_name || s.id,
        })));
      } catch (e) {
        // silently fall back to empty — user can still type
      } finally {
        setOptionsLoading(false);
      }
    })();
  }, []);

  const canGenerate = regionId;

  const animatePipeline = async () => {
    // Animate steps while waiting for the real API call
    const durations = [700, 500, 600, 900, 1000, 600, 500, 400];
    for (let i = 0; i < PIPELINE_STEPS.length; i++) {
      setPipelineStep(i);
      await new Promise(r => setTimeout(r, durations[i]));
    }
    setPipelineStep(PIPELINE_STEPS.length);
  };

  const handleGenerate = async () => {
    if (!canGenerate) return;
    setLoading(true);
    setResult(null);
    setError('');
    setPipelineStep(0);

    // Run animation and real API call in parallel
    const [_, apiResult] = await Promise.allSettled([
      animatePipeline(),
      generateCampaign(regionId, segmentId || null),
    ]);

    if (apiResult.status === 'fulfilled') {
      setResult(normaliseCampaign(apiResult.value));
      setActiveTab('copy');
    } else {
      setError(apiResult.reason?.message || 'Backend request failed.');
    }
    setLoading(false);
  };

  const handleCopyAll = () => {
    if (!result?.copyLines?.length) return;
    navigator.clipboard.writeText(result.copyLines.join('\n'));
    setAllCopied(true);
    setTimeout(() => setAllCopied(false), 2000);
  };

  const tabs = [
    { id: 'copy',    label: 'Copy Lines',     icon: Megaphone  },
    { id: 'banners', label: 'Banner Briefs',  icon: Image      },
    { id: 'budget',  label: 'Budget Split',   icon: BarChart3  },
    { id: 'explain', label: 'Explainability', icon: Brain      },
  ];

  const selectedRegionLabel = regionOptions.find(r => r.value === regionId)?.label || regionId;
  const selectedSegmentLabel = segmentOptions.find(s => s.value === segmentId)?.label || segmentId;

  return (
    <div className="page-container">
      <PageHeader
        title="Campaign Generator"
        subtitle="Generate hyperlocal campaign copy, banner briefs and budget allocation via the 9-agent LangGraph pipeline."
      >
        {result && (
          <span className="badge-success text-xs flex items-center gap-1.5">
            <Clock size={11} /> Generated in {result.latency}s
          </span>
        )}
      </PageHeader>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Config panel ── */}
        <div className="space-y-5">
          <div className="card p-6 space-y-5">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles size={16} className="text-primary-400" />
              <h3 className="text-sm font-semibold text-white">Campaign Configuration</h3>
            </div>

            <SelectField label="Target Region" value={regionId} onChange={setRegionId}
              options={regionOptions} placeholder="Select a region…" loading={optionsLoading} />
            <SelectField label="Customer Segment (optional)" value={segmentId} onChange={setSegmentId}
              options={[{ value: '', label: 'All segments' }, ...segmentOptions]}
              placeholder="All segments" loading={optionsLoading} />

            <button onClick={handleGenerate} disabled={!canGenerate || loading}
              className="btn-primary w-full justify-center py-3.5 disabled:opacity-50 disabled:cursor-not-allowed">
              {loading
                ? <><span className="spinner w-4 h-4" /> Running Pipeline…</>
                : <><Zap size={16} /> Generate Campaign</>}
            </button>

            {!canGenerate && <p className="text-xs text-gray-500 text-center">Select a region to generate</p>}
          </div>

          {/* Pipeline progress */}
          {(loading || result) && (
            <div className="card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Brain size={15} className="text-primary-400" />
                <h3 className="text-sm font-semibold text-white">Pipeline Progress</h3>
              </div>
              <PipelineProgress step={pipelineStep} />
              {result && (
                <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                    <CheckCircle size={13} /> Complete
                  </span>
                  <span className="text-gray-500">{result.latency}s</span>
                </div>
              )}
            </div>
          )}

          {/* Demand index */}
          {result && Object.keys(result.demandIndex).length > 0 && (
            <div className="card p-6">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp size={15} className="text-primary-400" />
                <h3 className="text-sm font-semibold text-white">Demand Index</h3>
              </div>
              <div className="space-y-3">
                {Object.entries(result.demandIndex).map(([cat, val]) => (
                  <div key={cat}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="text-gray-400 capitalize">{cat.replace(/_/g,' ')}</span>
                      <span className="font-semibold text-white">{val}</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${Math.min(val, 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Results panel ── */}
        <div className="lg:col-span-2">
          {!result && !loading && !error && (
            <div className="card h-full min-h-[500px] flex flex-col items-center justify-center gap-4 p-8">
              <div className="w-16 h-16 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
                <Megaphone size={32} className="text-primary-400 opacity-60" />
              </div>
              <div className="text-center">
                <p className="text-base font-semibold text-gray-300">Ready to Generate</p>
                <p className="text-sm text-gray-500 mt-1 max-w-xs">
                  Select a region and optionally a segment, then hit Generate to run the real 9-agent LangGraph pipeline.
                </p>
              </div>
            </div>
          )}

          {error && !loading && (
            <div className="card p-6 border-red-500/30 bg-red-500/10 flex items-start gap-3">
              <AlertCircle size={18} className="text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-300">Generation failed</p>
                <p className="text-xs text-red-400 mt-1">{error}</p>
                <p className="text-xs text-gray-500 mt-2">Make sure the backend is running: <code className="text-gray-400">uvicorn app.main:app --reload</code></p>
              </div>
            </div>
          )}

          {loading && !result && (
            <div className="card min-h-[500px] flex flex-col items-center justify-center gap-6 p-8">
              <LoadingSpinner size="lg" text="Orchestrating 9-agent pipeline…" />
              <div className="text-center space-y-1">
                <p className="text-sm text-gray-400">Calling backend at localhost:8000</p>
                <p className="text-xs text-gray-600">Trend · Weather · Festival · Catalog Gap · XGBoost · LLM</p>
              </div>
            </div>
          )}

          {result && (
            <div className="card overflow-hidden animate-fade-in">
              {/* Header */}
              <div className="p-5 border-b border-white/10 bg-gradient-to-r from-primary-600/15 to-accent-600/10">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <CheckCircle size={15} className="text-emerald-400" />
                      <span className="text-sm font-semibold text-white">Campaign Generated — Live Backend</span>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className="badge-primary"><Globe size={10} /> {selectedRegionLabel}</span>
                      {selectedSegmentLabel && <span className="badge-purple"><Users size={10} /> {selectedSegmentLabel}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={handleGenerate} className="btn-ghost text-xs py-1.5 px-3">
                      <RefreshCw size={13} /> Regenerate
                    </button>
                    <button onClick={handleCopyAll} className="btn-ghost text-xs py-1.5 px-3">
                      {allCopied ? <CheckCircle size={13} className="text-emerald-400" /> : <Copy size={13} />}
                      {allCopied ? 'Copied!' : 'Copy All'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-white/10 overflow-x-auto">
                {tabs.map(tab => (
                  <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-5 py-3.5 text-sm font-medium whitespace-nowrap transition-all border-b-2
                      ${activeTab === tab.id
                        ? 'border-primary-500 text-primary-300 bg-primary-500/5'
                        : 'border-transparent text-gray-500 hover:text-gray-300 hover:bg-white/5'}`}>
                    <tab.icon size={15} /> {tab.label}
                  </button>
                ))}
              </div>

              <div className="p-5">
                {activeTab === 'copy' && (
                  <div className="space-y-3 animate-fade-in">
                    <p className="text-xs text-gray-500 mb-4">
                      {result.copyLines.length} campaign lines from the LLM creative agent.
                    </p>
                    {result.copyLines.length > 0
                      ? result.copyLines.map((line, i) => <CopyLineCard key={i} line={line} index={i} />)
                      : <p className="text-sm text-gray-500 text-center py-8">No copy lines returned from backend.</p>
                    }
                  </div>
                )}

                {activeTab === 'banners' && (
                  <div className="space-y-4 animate-fade-in">
                    <p className="text-xs text-gray-500 mb-4">Visual banner briefs from the Banner Studio agent.</p>
                    {result.bannerBriefs.length > 0
                      ? result.bannerBriefs.map((brief, i) => <BannerBriefCard key={i} brief={brief} index={i} />)
                      : <p className="text-sm text-gray-500 text-center py-8">No banner briefs returned.</p>
                    }
                    <div className="card p-4 bg-amber-500/5 border-amber-500/20">
                      <div className="flex items-start gap-2">
                        <Star size={14} className="text-amber-400 mt-0.5 shrink-0" />
                        <p className="text-xs text-gray-400">
                          Use <span className="text-white font-medium">POST /api/training/generate-poster</span> to render these briefs into SDXL 768×768 posters.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'budget' && (
                  <div className="animate-fade-in">
                    <p className="text-xs text-gray-500 mb-5">Budget allocation from the Budget Optimizer agent — normalised to 100%.</p>
                    {Object.keys(result.budgetAllocation).length > 0
                      ? <div className="space-y-4">
                          {Object.entries(result.budgetAllocation).map(([ch, pct]) => (
                            <BudgetBar key={ch} channel={ch} pct={typeof pct === 'number' ? pct : parseFloat(pct)} />
                          ))}
                        </div>
                      : <p className="text-sm text-gray-500 text-center py-8">No budget data returned.</p>
                    }
                  </div>
                )}

                {activeTab === 'explain' && (
                  <div className="animate-fade-in space-y-4">
                    <p className="text-xs text-gray-500">Explanation synthesised by the Explainability agent from the pipeline log.</p>
                    <div className="card p-5 bg-dark-700/80">
                      <div className="flex items-start gap-3">
                        <Brain size={18} className="text-primary-400 shrink-0 mt-0.5" />
                        <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                          {result.explainability || 'No explanation returned by the pipeline.'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
