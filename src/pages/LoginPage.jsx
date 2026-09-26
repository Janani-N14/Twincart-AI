import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  ShoppingCart, Mail, Lock, Eye, EyeOff, ArrowRight,
  AlertCircle, Globe, Brain, TrendingUp, Zap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const highlights = [
  { icon: Globe,      text: '15 Regional Market Twins' },
  { icon: Brain,      text: '9-Agent LangGraph Pipeline' },
  { icon: TrendingUp, text: 'XGBoost Demand Forecasting' },
  { icon: Zap,        text: 'Campaigns in 3–5 Seconds' },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/dashboard';

  const [form, setForm] = useState({ email: '', password: '' });
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = e => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setError('Please fill in all fields.');
      return;
    }
    setLoading(true);
    // Simulate API call
    await new Promise(r => setTimeout(r, 1200));
    setLoading(false);
    // Mock auth — accept any non-empty creds
    login({ name: form.email.split('@')[0], email: form.email });
    navigate(from, { replace: true });
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 800));
    setLoading(false);
    login({ name: 'Demo Seller', email: 'demo@twincart.ai' });
    navigate('/dashboard', { replace: true });
  };

  return (
    <div className="min-h-screen bg-dark-900 flex">
      {/* ── Left panel ── */}
      <div className="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-12 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-950 via-dark-700 to-dark-900" />
        <div className="absolute inset-0 bg-hero-glow opacity-60" />
        <div className="absolute top-20 right-10 w-72 h-72 bg-accent-600/15 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-10 w-60 h-60 bg-primary-600/15 rounded-full blur-3xl" />

        {/* Logo */}
        <div className="relative flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-glow-sm">
            <ShoppingCart size={20} className="text-white" />
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-xl font-bold text-white">TwinCart</span>
            <span className="text-[10px] font-semibold px-1.5 py-0.5 bg-primary-500/20 text-primary-300 rounded-md border border-primary-500/30">AI</span>
          </div>
        </div>

        {/* Main copy */}
        <div className="relative space-y-8">
          <div>
            <h2 className="text-4xl font-black text-white leading-tight mb-4">
              Hyperlocal AI for<br />
              <span className="bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
                Bharat Commerce
              </span>
            </h2>
            <p className="text-gray-400 text-base leading-relaxed">
              Generate culturally resonant campaigns for every Indian state — powered by digital twins, multi-agent AI, and real-time market intelligence.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {highlights.map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-2.5 p-3 rounded-xl bg-white/5 border border-white/10">
                <Icon size={16} className="text-primary-400 shrink-0" />
                <span className="text-sm text-gray-300">{text}</span>
              </div>
            ))}
          </div>

          {/* Animated pipeline preview */}
          <div className="card p-4 space-y-2">
            <p className="text-xs text-gray-500 font-medium mb-3">Live pipeline status</p>
            {[
              { label: 'Trend Detection',    w: 'w-full',  color: 'from-sky-600 to-sky-500' },
              { label: 'Festival Analysis',  w: 'w-4/5',   color: 'from-emerald-600 to-emerald-500' },
              { label: 'Demand Forecasting', w: 'w-3/4',   color: 'from-primary-600 to-primary-500' },
              { label: 'Campaign Output',    w: 'w-2/3',   color: 'from-accent-600 to-accent-500' },
            ].map(row => (
              <div key={row.label} className="flex items-center gap-3">
                <span className="text-xs text-gray-500 w-36 shrink-0">{row.label}</span>
                <div className="flex-1 h-1.5 bg-dark-800 rounded-full overflow-hidden">
                  <div className={`h-full bg-gradient-to-r ${row.color} ${row.w} rounded-full`} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="relative text-xs text-gray-600">
          © 2026 TwinCart-AI · Sri Manakula Vinayagar Engineering College
        </div>
      </div>

      {/* ── Right panel (form) ── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2.5 mb-10">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-glow-sm">
              <ShoppingCart size={18} className="text-white" />
            </div>
            <span className="text-xl font-bold text-white">TwinCart <span className="text-primary-400">AI</span></span>
          </div>

          <div className="mb-8">
            <h1 className="text-3xl font-black text-white mb-2">Welcome back</h1>
            <p className="text-gray-400">Sign in to your seller dashboard</p>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2.5 p-3.5 mb-6 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm animate-fade-in">
              <AlertCircle size={16} className="shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="label">Email address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  className="input-field pl-10"
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="label mb-0">Password</label>
                <a href="#" className="text-xs text-primary-400 hover:text-primary-300 transition-colors">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type={showPass ? 'text' : 'password'}
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  className="input-field pl-10 pr-10"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(v => !v)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center text-base py-3.5 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="spinner w-4 h-4" /> Signing in…
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Sign In <ArrowRight size={17} />
                </span>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-xs text-gray-500">or</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          {/* Demo login */}
          <button
            onClick={handleDemoLogin}
            disabled={loading}
            className="btn-secondary w-full justify-center py-3.5 disabled:opacity-60"
          >
            <Zap size={16} className="text-primary-400" />
            Continue with Demo Account
          </button>

          {/* Sign up link */}
          <p className="text-center text-sm text-gray-500 mt-8">
            Don't have an account?{' '}
            <Link to="/signup" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              Create one free
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
