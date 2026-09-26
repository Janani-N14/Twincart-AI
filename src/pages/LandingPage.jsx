import { Link } from 'react-router-dom';
import {
  ArrowRight, Globe, Users, Megaphone, FlaskConical,
  MessageSquareText, BarChart3, Zap, ShieldCheck, Brain,
  TrendingUp, Star, ChevronRight, Play, CheckCircle,
  Map, Cpu, Image, Activity, Database, Clock
} from 'lucide-react';
import LandingNav from '../components/common/LandingNav';
import Footer from '../components/layout/Footer';

/* ─── DATA ─────────────────────────────────────────────── */
const features = [
  {
    icon: Globe,
    title: 'Regional Digital Twins',
    description: 'Encode 15 Indian state-level market twins with price sensitivity, active festivals, climate signals, and top product categories for hyperlocal targeting.',
    badge: 'Digital Twin',
  },
  {
    icon: Users,
    title: 'Customer Segment Twins',
    description: 'Model four canonical segments — Students, Professionals, Homemakers, Budget Shoppers — with income brackets and behavioural profiles.',
    badge: 'AI Segments',
  },
  {
    icon: Brain,
    title: '9-Agent LangGraph Pipeline',
    description: 'Parallel fan-out/fan-in orchestration with trend detection, weather & festival intelligence, catalog gap detection, and demand forecasting.',
    badge: 'Multi-Agent',
  },
  {
    icon: Megaphone,
    title: 'Campaign Generator',
    description: 'Generate 3–5 culturally resonant campaign copy lines enriched with customer segment profiles, channel budgets, and visual banner briefs.',
    badge: 'Creative AI',
  },
  {
    icon: FlaskConical,
    title: 'What-If Simulation',
    description: 'Deterministic conversion-rate and revenue-index predictions under 200 ms. Explore festival, weather, budget, and inventory scenarios instantly.',
    badge: 'Simulation',
  },
  {
    icon: MessageSquareText,
    title: 'Seller Intelligence',
    description: 'Free-form Q&A with structured JSON responses, confidence ratings, and semantic caching at cosine similarity ≥ 0.92 for instant repeat answers.',
    badge: 'LLM Q&A',
  },
  {
    icon: TrendingUp,
    title: 'XGBoost Demand Forecasting',
    description: 'R² = 0.82 on 5,000 synthetic Indian sales records. Temporal feature engineering, early stopping, and sub-100 ms inference.',
    badge: 'ML Forecasting',
  },
  {
    icon: Image,
    title: 'SDXL Poster Generation',
    description: 'Stable Diffusion XL generates photorealistic 768×768 campaign posters with region-specific aesthetics and culturally contextualised prompts.',
    badge: 'Generative AI',
  },
  {
    icon: Zap,
    title: 'Dual-Layer Caching',
    description: 'TTL cache + semantic vector cache reduces redundant LLM API calls by ~65%, keeping costs low on Groq free-tier 30 RPM ceiling.',
    badge: 'Performance',
  },
];

const steps = [
  {
    number: '01',
    icon: Map,
    title: 'Select Your Region & Segment',
    description: 'Choose from 15 Indian state-level market twins and one of four customer segment profiles to anchor your campaign context.',
  },
  {
    number: '02',
    icon: Cpu,
    title: 'Agents Analyse in Parallel',
    description: 'Trend detection, weather & festival intelligence, and catalog gap agents run concurrently, then fan-in to the demand forecaster.',
  },
  {
    number: '03',
    icon: Megaphone,
    title: 'Campaign is Synthesised',
    description: 'The creative LLM produces copy, banner briefs, channel budget allocations, and an explainability summary in 3–5 seconds.',
  },
  {
    number: '04',
    icon: Activity,
    title: 'Simulate & Optimise',
    description: 'Run what-if scenarios on budget, festival timing, and inventory to optimise conversion before launching your campaign.',
  },
];

const stats = [
  { value: '15', label: 'State Market Twins', sub: 'Covering major Indian states' },
  { value: '9',  label: 'Specialised Agents',  sub: 'LangGraph pipeline nodes' },
  { value: '3–5s', label: 'End-to-End Latency', sub: 'Full campaign generation' },
  { value: '~65%', label: 'Cache Hit Rate',     sub: 'Reduced LLM API calls' },
  { value: '0.82', label: 'Forecast R²',        sub: 'XGBoost on Indian data' },
  { value: '<200ms', label: 'Simulation Speed', sub: 'What-if engine latency' },
];

const testimonials = [
  {
    name: 'Priya Sharma',
    role: 'Meesho Seller, Jaipur',
    avatar: 'PS',
    rating: 5,
    text: 'TwinCart-AI completely changed how I plan Diwali campaigns. The regional twin for Rajasthan nailed the local festival context — my sales went up 40% that season.',
  },
  {
    name: 'Ravi Kumar',
    role: 'Flipkart Seller, Coimbatore',
    avatar: 'RK',
    rating: 5,
    text: 'The demand forecasting agent caught a catalog gap in electronics before I even noticed. Saved me from overstocking and redirected budget to accessories that actually sold.',
  },
  {
    name: 'Anjali Menon',
    role: 'Amazon India Seller, Kochi',
    avatar: 'AM',
    rating: 5,
    text: 'I love that it generates campaign copy in Tamil automatically. No more paying an agency for regional translations — and the cultural relevance is spot on.',
  },
];

const plans = [
  {
    name: 'Starter',
    price: '₹0',
    period: 'forever',
    description: 'Perfect for new sellers exploring hyperlocal AI.',
    features: ['5 state twins', '2 segment profiles', '10 campaigns/month', 'Basic simulation', 'Community support'],
    cta: 'Get Started Free',
    highlight: false,
  },
  {
    name: 'Growth',
    price: '₹999',
    period: '/month',
    description: 'For active sellers scaling across multiple regions.',
    features: ['15 state twins', '4 segment profiles', '100 campaigns/month', 'Full simulation engine', 'SDXL poster generation', 'Priority LLM queue', 'Email support'],
    cta: 'Start Growth Plan',
    highlight: true,
  },
  {
    name: 'Pro',
    price: '₹2,999',
    period: '/month',
    description: 'For power sellers and agencies at scale.',
    features: ['All 28 states + UTs', 'Custom segments', 'Unlimited campaigns', 'Kafka real-time feeds', 'A/B testing loop', 'API access', 'Dedicated support'],
    cta: 'Go Pro',
    highlight: false,
  },
];

/* ─── COMPONENTS ────────────────────────────────────────── */
function GradientOrb({ className }) {
  return (
    <div className={`absolute rounded-full blur-3xl opacity-20 pointer-events-none ${className}`} />
  );
}

function FeatureCard({ icon: Icon, title, description, badge }) {
  return (
    <div className="card-hover p-6 group animate-fade-in">
      <div className="flex items-start justify-between mb-4">
        <div className="w-10 h-10 rounded-xl bg-primary-500/15 border border-primary-500/25 flex items-center justify-center group-hover:bg-primary-500/25 transition-colors">
          <Icon size={20} className="text-primary-400" />
        </div>
        <span className="badge-primary text-[10px]">{badge}</span>
      </div>
      <h3 className="text-base font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
    </div>
  );
}

function StepCard({ number, icon: Icon, title, description, isLast }) {
  return (
    <div className="flex items-start gap-4">
      <div className="flex flex-col items-center">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-600 to-accent-600 flex items-center justify-center shadow-glow-sm shrink-0">
          <Icon size={22} className="text-white" />
        </div>
        {!isLast && <div className="w-px flex-1 bg-gradient-to-b from-primary-500/40 to-transparent mt-2 min-h-[48px]" />}
      </div>
      <div className="pb-10">
        <span className="text-xs font-bold text-primary-400 tracking-widest">{number}</span>
        <h3 className="text-lg font-semibold text-white mt-1 mb-2">{title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed max-w-sm">{description}</p>
      </div>
    </div>
  );
}

function StatBadge({ value, label, sub }) {
  return (
    <div className="flex flex-col items-center text-center p-6">
      <span className="text-4xl font-black gradient-text mb-1">{value}</span>
      <span className="text-sm font-semibold text-white">{label}</span>
      <span className="text-xs text-gray-500 mt-0.5">{sub}</span>
    </div>
  );
}

function TestimonialCard({ name, role, avatar, rating, text }) {
  return (
    <div className="card p-6 flex flex-col gap-4">
      <div className="flex items-center gap-1">
        {Array.from({ length: rating }).map((_, i) => (
          <Star key={i} size={13} className="text-amber-400 fill-amber-400" />
        ))}
      </div>
      <p className="text-sm text-gray-300 leading-relaxed flex-1">"{text}"</p>
      <div className="flex items-center gap-3 pt-2 border-t border-white/10">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
          {avatar}
        </div>
        <div>
          <p className="text-sm font-semibold text-white">{name}</p>
          <p className="text-xs text-gray-500">{role}</p>
        </div>
      </div>
    </div>
  );
}

function PlanCard({ name, price, period, description, features, cta, highlight }) {
  return (
    <div className={`relative flex flex-col rounded-2xl p-7 transition-all duration-300
      ${highlight
        ? 'bg-gradient-to-b from-primary-600/30 to-primary-900/20 border-2 border-primary-500/60 shadow-glow-md scale-[1.02]'
        : 'card hover:border-white/20'
      }`}
    >
      {highlight && (
        <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
          <span className="px-3 py-1 bg-primary-500 text-white text-xs font-bold rounded-full shadow-glow-sm">
            Most Popular
          </span>
        </div>
      )}
      <h3 className="text-lg font-bold text-white">{name}</h3>
      <div className="flex items-end gap-1 mt-3 mb-1">
        <span className="text-4xl font-black text-white">{price}</span>
        <span className="text-sm text-gray-400 mb-1">{period}</span>
      </div>
      <p className="text-sm text-gray-400 mb-6">{description}</p>
      <ul className="space-y-2.5 flex-1 mb-7">
        {features.map(f => (
          <li key={f} className="flex items-center gap-2.5 text-sm text-gray-300">
            <CheckCircle size={15} className="text-emerald-400 shrink-0" />
            {f}
          </li>
        ))}
      </ul>
      <Link
        to="/signup"
        className={highlight ? 'btn-primary justify-center' : 'btn-secondary justify-center'}
      >
        {cta} <ArrowRight size={15} />
      </Link>
    </div>
  );
}

/* ─── PAGE ──────────────────────────────────────────────── */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-dark-900 overflow-x-hidden">
      <LandingNav />

      {/* ── HERO ── */}
      <section className="relative min-h-screen flex items-center justify-center pt-24 pb-20 px-6">
        <GradientOrb className="w-[700px] h-[500px] bg-primary-600 -top-32 left-1/2 -translate-x-1/2" />
        <GradientOrb className="w-[400px] h-[400px] bg-accent-600 top-1/2 right-10" />
        <GradientOrb className="w-[300px] h-[300px] bg-primary-800 bottom-0 left-10" />

        <div className="relative max-w-5xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-500/15 border border-primary-500/30 text-primary-300 text-sm font-medium mb-8 animate-fade-in">
            <Zap size={13} className="text-primary-400" />
            Hyperlocal AI for Bharat Commerce
            <ChevronRight size={13} />
          </div>

          {/* Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black text-white leading-tight tracking-tight animate-slide-up">
            Digital Twins for<br />
            <span className="gradient-text">Every Indian Market</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-gray-400 leading-relaxed max-w-2xl mx-auto animate-slide-up">
            TwinCart-AI orchestrates 9 specialised LLM agents over 15 state-level market twins to deliver
            hyperlocal campaign copy, demand forecasts, and what-if simulations — in under 5 seconds.
          </p>

          {/* CTAs */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up">
            <Link to="/signup" className="btn-primary text-base px-8 py-4">
              Start for Free <ArrowRight size={18} />
            </Link>
            <a href="#how-it-works" className="btn-secondary text-base px-8 py-4">
              <Play size={16} className="fill-current" /> See How It Works
            </a>
          </div>

          {/* Social proof */}
          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-gray-500 animate-fade-in">
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                {['PS','RK','AM','NK','VL'].map((init, i) => (
                  <div key={i} className="w-7 h-7 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 border-2 border-dark-900 flex items-center justify-center text-[9px] font-bold text-white">
                    {init}
                  </div>
                ))}
              </div>
              <span>500+ sellers trust TwinCart</span>
            </div>
            <span className="hidden sm:block text-gray-700">|</span>
            <div className="flex items-center gap-1.5">
              {Array.from({length:5}).map((_,i)=>(
                <Star key={i} size={13} className="text-amber-400 fill-amber-400" />
              ))}
              <span>4.9 / 5 rating</span>
            </div>
            <span className="hidden sm:block text-gray-700">|</span>
            <span className="flex items-center gap-1.5">
              <ShieldCheck size={14} className="text-emerald-400" /> Open Source on GitHub
            </span>
          </div>
        </div>
      </section>

      {/* ── STATS TICKER ── */}
      <section id="stats" className="border-y border-white/10 bg-dark-800/40 backdrop-blur-sm py-2">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 divide-x divide-white/10">
          {stats.map(s => <StatBadge key={s.label} {...s} />)}
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="badge-primary mb-4 inline-flex">Platform Capabilities</span>
            <h2 className="text-4xl lg:text-5xl font-black text-white">
              Everything a Bharat Seller Needs
            </h2>
            <p className="mt-4 text-gray-400 text-lg max-w-2xl mx-auto">
              One platform combining digital twins, multi-agent AI, ML forecasting, and generative creative tools — purpose-built for India's Tier-2/Tier-3 markets.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map(f => <FeatureCard key={f.title} {...f} />)}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className="py-24 px-6 bg-dark-800/30">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <span className="badge-primary mb-4 inline-flex">How It Works</span>
              <h2 className="text-4xl font-black text-white mb-4">
                From Region Selection<br />to Live Campaign
              </h2>
              <p className="text-gray-400 mb-10 leading-relaxed">
                Our nine-agent LangGraph pipeline runs in parallel fan-out, synthesises insights through a fan-in demand forecaster, then produces complete campaign assets in a sequential tail — all in 3–5 seconds.
              </p>
              <div className="space-y-0">
                {steps.map((step, i) => (
                  <StepCard key={step.number} {...step} isLast={i === steps.length - 1} />
                ))}
              </div>
            </div>

            {/* Pipeline visual */}
            <div className="relative hidden lg:block">
              <div className="card p-8 space-y-3">
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-6">Live Pipeline</div>

                {/* Phase 1 - parallel */}
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {[
                    { icon: TrendingUp, label: 'Trend Detection', color: 'text-sky-400', bg: 'bg-sky-500/10 border-sky-500/20' },
                    { icon: Activity,   label: 'Weather & Festival', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
                    { icon: Database,   label: 'Catalog Gap', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
                  ].map(node => (
                    <div key={node.label} className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border ${node.bg}`}>
                      <node.icon size={16} className={node.color} />
                      <span className="text-[10px] text-center text-gray-400 leading-tight">{node.label}</span>
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-slow" />
                    </div>
                  ))}
                </div>

                {/* Fan-in arrow */}
                <div className="flex justify-center">
                  <div className="w-px h-6 bg-gradient-to-b from-primary-500 to-transparent" />
                </div>

                {/* Demand Forecaster */}
                <div className="flex items-center gap-3 p-3 rounded-xl bg-primary-500/10 border border-primary-500/20">
                  <Brain size={18} className="text-primary-400 shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-primary-300">Demand Forecasting Agent</p>
                    <div className="progress-bar mt-1.5 w-full"><div className="progress-fill w-3/4" /></div>
                  </div>
                  <Clock size={12} className="text-gray-500" />
                </div>

                {/* Sequential */}
                <div className="flex justify-center">
                  <div className="w-px h-4 bg-gradient-to-b from-primary-500 to-transparent" />
                </div>
                {[
                  { icon: Megaphone,       label: 'Campaign Generator',  pct: 'w-full' },
                  { icon: Image,           label: 'Banner Studio',        pct: 'w-4/5' },
                  { icon: BarChart3,       label: 'Budget Optimizer',     pct: 'w-2/3' },
                  { icon: ShieldCheck,     label: 'Explainability',       pct: 'w-5/6' },
                ].map((node, i) => (
                  <div key={node.label}>
                    <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
                      <node.icon size={16} className="text-primary-400 shrink-0" />
                      <div className="flex-1">
                        <p className="text-xs text-gray-300">{node.label}</p>
                        <div className="progress-bar mt-1 w-full"><div className={`progress-fill ${node.pct}`} /></div>
                      </div>
                    </div>
                    {i < 3 && <div className="flex justify-center"><div className="w-px h-3 bg-white/10" /></div>}
                  </div>
                ))}

                <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center gap-1.5"><CheckCircle size={13} className="text-emerald-400" /> Campaign Ready</span>
                  <span className="text-primary-400 font-semibold">~3.8s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ── */}
      <section id="testimonials" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <span className="badge-primary mb-4 inline-flex">Testimonials</span>
            <h2 className="text-4xl font-black text-white">Trusted by Bharat Sellers</h2>
            <p className="mt-4 text-gray-400 max-w-xl mx-auto">
              See how sellers across India's Tier-2 and Tier-3 cities use TwinCart-AI to win their regional markets.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map(t => <TestimonialCard key={t.name} {...t} />)}
          </div>
        </div>
      </section>

      {/* ── PRICING ── */}
      <section id="pricing" className="py-24 px-6 bg-dark-800/30">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <span className="badge-primary mb-4 inline-flex">Pricing</span>
            <h2 className="text-4xl font-black text-white">Simple, Honest Pricing</h2>
            <p className="mt-4 text-gray-400 max-w-xl mx-auto">
              Start free and scale as you grow. No hidden fees, no surprise bills.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 items-center">
            {plans.map(p => <PlanCard key={p.name} {...p} />)}
          </div>
        </div>
      </section>

      {/* ── FINAL CTA ── */}
      <section className="py-24 px-6 relative overflow-hidden">
        <GradientOrb className="w-[600px] h-[400px] bg-primary-700 left-1/2 -translate-x-1/2 top-0" />
        <div className="relative max-w-3xl mx-auto text-center">
          <h2 className="text-4xl lg:text-5xl font-black text-white mb-5">
            Ready to Sell Smarter<br />
            <span className="gradient-text">Across Every State?</span>
          </h2>
          <p className="text-gray-400 text-lg mb-10">
            Join hundreds of Bharat sellers who use TwinCart-AI to generate hyperlocal campaigns, forecast demand, and simulate outcomes — all in one platform.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup" className="btn-primary text-base px-10 py-4">
              Create Free Account <ArrowRight size={18} />
            </Link>
            <Link to="/login" className="btn-secondary text-base px-10 py-4">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
