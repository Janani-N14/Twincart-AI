import { useState, useRef, useEffect } from 'react';
import {
  MessageSquareText, Send, Brain, User, Sparkles,
  ThumbsUp, ThumbsDown, Copy, CheckCircle, Zap,
  TrendingUp, Globe, Tag, RefreshCw, Clock,
  ChevronRight, Lightbulb, Star, AlertCircle
} from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';
import { askSellerIntelligence, getRegionalTwins, getSegmentTwins } from '../../services/api';

const SUGGESTED = [
  { icon: TrendingUp, text: 'What is the best category to sell in Tamil Nadu during Pongal?' },
  { icon: Globe,      text: 'Which Indian states have the highest demand for electronics?' },
  { icon: Tag,        text: 'How should I price products for Budget Shoppers in Rajasthan?' },
  { icon: Sparkles,   text: 'What campaign copy works best for homemakers on Meesho?' },
  { icon: Star,       text: 'What are the top festival seasons for fashion sales in Maharashtra?' },
  { icon: Brain,      text: 'How do I reduce catalog gaps in my Flipkart store?' },
];

/* ─── normalise backend response ─────────────────────────── */
function normaliseAnswer(data) {
  const answer     = data.answer     || data.response    || data.text       || JSON.stringify(data);
  const confidence = data.confidence ?? data.confidence_score ?? 0.80;
  const cached     = data.cached     ?? data.from_cache   ?? false;
  const tags       = data.tags       || data.keywords     || [];
  const relatedTopics = data.related_topics || data.related || data.follow_up_topics || [];
  return { answer, confidence, cached, tags, relatedTopics };
}

/* ─── Message components ─────────────────────────────────── */
function UserMessage({ text }) {
  return (
    <div className="flex items-start gap-3 justify-end">
      <div className="max-w-[75%] px-4 py-3 bg-primary-600/30 border border-primary-500/30 rounded-2xl rounded-tr-sm">
        <p className="text-sm text-gray-100 leading-relaxed">{text}</p>
      </div>
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
        <User size={14} />
      </div>
    </div>
  );
}

function AIMessage({ response, isLoading, isError }) {
  const [copied, setCopied] = useState(false);
  const [liked,  setLiked]  = useState(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(response?.answer || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-700 to-accent-700 border border-primary-500/40 flex items-center justify-center shrink-0">
          <Brain size={14} className="text-white" />
        </div>
        <div className="card px-5 py-4 inline-flex items-center gap-3">
          <div className="flex gap-1">
            {[0,1,2].map(i => (
              <span key={i} className="w-2 h-2 rounded-full bg-primary-400 animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }} />
            ))}
          </div>
          <span className="text-sm text-gray-400">Querying backend seller intelligence…</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-dark-700 border border-red-500/40 flex items-center justify-center shrink-0">
          <AlertCircle size={14} className="text-red-400" />
        </div>
        <div className="card p-4 border-red-500/20 bg-red-500/5 max-w-[85%]">
          <p className="text-sm text-red-300 font-medium mb-1">Backend request failed</p>
          <p className="text-xs text-red-400">{response?.answer}</p>
          <p className="text-xs text-gray-600 mt-2">Make sure backend is running: <code className="text-gray-400">uvicorn app.main:app --reload</code></p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-700 to-accent-700 border border-primary-500/40 flex items-center justify-center shrink-0">
        <Brain size={14} className="text-white" />
      </div>
      <div className="flex-1 min-w-0 space-y-3">
        <div className="card p-5 max-w-[90%]">
          <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
            {response.answer.split('\n').map((line, i) => (
              <p key={i} className={line.startsWith('**') ? 'font-semibold text-white mt-3 mb-1' : 'mb-1'}>
                {line.replace(/\*\*/g, '')}
              </p>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-gray-500">
            <Sparkles size={11} className="text-primary-400" />
            <span>Confidence: <span className="text-primary-300 font-semibold">{(response.confidence * 100).toFixed(0)}%</span></span>
          </div>
          {response.cached && (
            <span className="badge bg-emerald-500/15 text-emerald-400 border-emerald-500/25 text-[10px]">
              <Zap size={9} /> Semantic Cache Hit
            </span>
          )}
          {response.tags.map(tag => <span key={tag} className="badge-primary text-[10px]">{tag}</span>)}
        </div>

        {response.relatedTopics?.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
            <span>Related:</span>
            {response.relatedTopics.map(t => (
              <span key={t} className="flex items-center gap-1 text-primary-400 hover:text-primary-300 cursor-pointer transition-colors">
                <ChevronRight size={10} /> {t}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2">
          <button onClick={handleCopy} className="btn-ghost text-xs py-1 px-2.5 gap-1.5">
            {copied ? <CheckCircle size={12} className="text-emerald-400" /> : <Copy size={12} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          <button onClick={() => setLiked(true)}
            className={`btn-ghost text-xs py-1 px-2.5 gap-1.5 ${liked === true ? 'text-emerald-400' : ''}`}>
            <ThumbsUp size={12} /> Helpful
          </button>
          <button onClick={() => setLiked(false)}
            className={`btn-ghost text-xs py-1 px-2.5 gap-1.5 ${liked === false ? 'text-rose-400' : ''}`}>
            <ThumbsDown size={12} />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Page ──────────────────────────────────────────────── */
export default function SellerIntelligencePage() {
  const [messages,  setMessages]  = useState([]);
  const [input,     setInput]     = useState('');
  const [loading,   setLoading]   = useState(false);
  const [regionId,  setRegionId]  = useState('');
  const [segmentId, setSegmentId] = useState('');
  const [regionOptions,  setRegionOptions]  = useState([]);
  const [segmentOptions, setSegmentOptions] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load optional context dropdowns
  useEffect(() => {
    Promise.all([getRegionalTwins(), getSegmentTwins()]).then(([rData, sData]) => {
      const rList = Array.isArray(rData) ? rData : rData.regions ?? rData.data ?? [];
      const sList = Array.isArray(sData) ? sData : sData.segments ?? sData.data ?? [];
      setRegionOptions(rList.map(r => ({ value: r.id || r.region_id, label: r.state || r.name || r.id })));
      setSegmentOptions(sList.map(s => ({ value: s.id || s.segment_id, label: s.name || s.label || s.id })));
    }).catch(() => {});
  }, []);

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return;
    const q = text.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', text: q }]);
    setLoading(true);
    setMessages(prev => [...prev, { type: 'ai', loading: true }]);

    try {
      const raw = await askSellerIntelligence(q, regionId || null, segmentId || null);
      const resp = normaliseAnswer(raw);
      setMessages(prev => [...prev.slice(0, -1), { type: 'ai', response: resp }]);
    } catch (e) {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { type: 'ai', error: true, response: { answer: e.message || 'Request failed.' } },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  return (
    <div className="page-container h-full">
      <PageHeader
        title="Seller Intelligence"
        subtitle="Free-form Q&A powered by the backend LLM agent with semantic caching."
      >
        {messages.length > 0 && (
          <button onClick={() => setMessages([])} className="btn-ghost text-sm">
            <RefreshCw size={14} /> Clear Chat
          </button>
        )}
      </PageHeader>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* ── Sidebar ── */}
        <div className="space-y-4">
          {/* Optional context */}
          <div className="card p-5 space-y-3">
            <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
              <Globe size={14} className="text-primary-400" /> Context (optional)
            </h3>
            <div>
              <label className="label text-xs">Region</label>
              <select value={regionId} onChange={e => setRegionId(e.target.value)} className="select-field text-xs py-2">
                <option value="">All regions</option>
                {regionOptions.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
            <div>
              <label className="label text-xs">Segment</label>
              <select value={segmentId} onChange={e => setSegmentId(e.target.value)} className="select-field text-xs py-2">
                <option value="">All segments</option>
                {segmentOptions.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
          </div>

          {/* Suggestions */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Lightbulb size={14} className="text-amber-400" /> Try Asking
            </h3>
            <div className="space-y-2">
              {SUGGESTED.map(({ icon: Icon, text }) => (
                <button key={text} onClick={() => sendMessage(text)} disabled={loading}
                  className="w-full flex items-start gap-2.5 p-3 card-hover text-left group disabled:opacity-50">
                  <Icon size={13} className="text-primary-400 mt-0.5 shrink-0 group-hover:text-primary-300" />
                  <span className="text-xs text-gray-400 group-hover:text-gray-200 leading-relaxed transition-colors">{text}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Cache stats */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <Zap size={14} className="text-primary-400" /> Backend Cache Stats
            </h3>
            <div className="space-y-3">
              {[
                { label: 'Semantic Cache',         value: '~65%',    sub: 'LLM call reduction'    },
                { label: 'Similarity Threshold',   value: '0.92',    sub: 'Cosine similarity'     },
                { label: 'Cache TTL',              value: '6h',      sub: 'Campaign results'      },
                { label: 'Embedding Model',        value: 'MiniLM',  sub: 'all-MiniLM-L6-v2'     },
                { label: 'LLM Provider',           value: 'Groq',    sub: 'LangGraph agent'       },
              ].map(s => (
                <div key={s.label} className="flex justify-between items-center">
                  <div>
                    <p className="text-xs text-gray-400">{s.label}</p>
                    <p className="text-[10px] text-gray-600">{s.sub}</p>
                  </div>
                  <span className="text-sm font-bold text-primary-300">{s.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Chat window ── */}
        <div className="lg:col-span-3 flex flex-col card overflow-hidden" style={{ minHeight: '600px' }}>
          <div className="px-5 py-4 border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-700 to-accent-700 border border-primary-500/40 flex items-center justify-center">
                <Brain size={15} className="text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white">TwinCart Seller Intelligence</p>
                <p className="text-xs text-gray-500 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-slow" />
                  Groq LLM · Semantic cache active · Backend at :8000
                </p>
              </div>
            </div>
            <span className="badge-primary text-[10px]">
              <Clock size={9} /> &lt;2s cold · &lt;50ms cached
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center gap-4 py-12">
                <div className="w-16 h-16 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
                  <MessageSquareText size={32} className="text-primary-400 opacity-60" />
                </div>
                <div className="text-center">
                  <p className="text-base font-semibold text-gray-300">Ask Anything About Your Market</p>
                  <p className="text-sm text-gray-500 mt-1 max-w-sm">
                    Questions go directly to the backend LangGraph Seller Intelligence agent with semantic caching.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center mt-2">
                  {SUGGESTED.slice(0, 3).map(s => (
                    <button key={s.text} onClick={() => sendMessage(s.text)}
                      className="text-xs px-3 py-1.5 card-hover text-gray-400 hover:text-gray-200 transition-colors">
                      {s.text.substring(0, 35)}…
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i}>
                {msg.type === 'user' && <UserMessage text={msg.text} />}
                {msg.type === 'ai' && (
                  <AIMessage response={msg.response} isLoading={msg.loading} isError={msg.error} />
                )}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div className="p-4 border-t border-white/10">
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <textarea value={input} onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about regions, pricing, festivals, categories…"
                  rows={1} disabled={loading}
                  className="input-field resize-none pr-4 py-3 text-sm leading-relaxed"
                  style={{ minHeight: '48px', maxHeight: '120px' }} />
              </div>
              <button onClick={() => sendMessage(input)} disabled={!input.trim() || loading}
                className="btn-primary py-3 px-4 disabled:opacity-50 disabled:cursor-not-allowed shrink-0">
                <Send size={16} />
              </button>
            </div>
            <p className="text-[10px] text-gray-600 mt-2 px-1">
              Enter to send · Shift+Enter for newline · Semantic cache threshold: cosine ≥ 0.92
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
