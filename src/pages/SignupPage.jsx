import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShoppingCart, Mail, Lock, Eye, EyeOff, ArrowRight,
  AlertCircle, User, Store, CheckCircle, MapPin, Zap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const PLATFORMS = ['Meesho', 'Flipkart', 'Amazon India', 'Myntra', 'Snapdeal', 'Other'];
const STATES = [
  'Tamil Nadu', 'Maharashtra', 'Karnataka', 'Gujarat', 'Rajasthan',
  'West Bengal', 'Uttar Pradesh', 'Kerala', 'Punjab', 'Madhya Pradesh',
  'Andhra Pradesh', 'Telangana', 'Odisha', 'Jharkhand', 'Haryana',
];

const passwordRules = [
  { label: 'At least 8 characters', test: v => v.length >= 8 },
  { label: 'One uppercase letter',  test: v => /[A-Z]/.test(v) },
  { label: 'One number',            test: v => /\d/.test(v) },
];

const steps = [
  { number: 1, label: 'Account' },
  { number: 2, label: 'Business' },
  { number: 3, label: 'Preferences' },
];

export default function SignupPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    name: '', email: '', password: '', confirmPassword: '',
    storeName: '', platform: '', state: '',
    categories: [], agreeTerms: false,
  });

  const categories = ['Fashion', 'Electronics', 'Home & Kitchen', 'Beauty', 'Toys', 'Sports', 'Grocery', 'Books'];

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
    setError('');
  };

  const toggleCategory = cat => {
    setForm(f => ({
      ...f,
      categories: f.categories.includes(cat)
        ? f.categories.filter(c => c !== cat)
        : [...f.categories, cat],
    }));
  };

  const validateStep = () => {
    if (step === 1) {
      if (!form.name.trim()) return 'Please enter your full name.';
      if (!form.email.trim()) return 'Please enter your email address.';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return 'Enter a valid email address.';
      if (form.password.length < 8) return 'Password must be at least 8 characters.';
      if (form.password !== form.confirmPassword) return 'Passwords do not match.';
    }
    if (step === 2) {
      if (!form.storeName.trim()) return 'Please enter your store name.';
      if (!form.platform) return 'Please select a platform.';
      if (!form.state) return 'Please select your state.';
    }
    if (step === 3) {
      if (!form.agreeTerms) return 'Please accept the Terms of Service.';
    }
    return '';
  };

  const nextStep = () => {
    const err = validateStep();
    if (err) { setError(err); return; }
    setError('');
    setStep(s => s + 1);
  };

  const handleSubmit = async e => {
    e.preventDefault();
    const err = validateStep();
    if (err) { setError(err); return; }
    setLoading(true);
    await new Promise(r => setTimeout(r, 1400));
    setLoading(false);
    login({ name: form.name, email: form.email, storeName: form.storeName, state: form.state });
    navigate('/dashboard', { replace: true });
  };

  return (
    <div className="min-h-screen bg-dark-900 flex">
      {/* ── Left panel ── */}
      <div className="hidden lg:flex lg:w-5/12 relative flex-col justify-between p-12 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-950 via-dark-700 to-dark-900" />
        <div className="absolute inset-0 bg-hero-glow opacity-50" />
        <div className="absolute top-32 right-8 w-64 h-64 bg-accent-600/15 rounded-full blur-3xl" />
        <div className="absolute bottom-32 left-8 w-48 h-48 bg-primary-600/15 rounded-full blur-3xl" />

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

        {/* Copy */}
        <div className="relative space-y-6">
          <div>
            <h2 className="text-4xl font-black text-white leading-tight mb-4">
              Join 500+ Sellers<br />
              <span className="bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
                Growing with AI
              </span>
            </h2>
            <p className="text-gray-400 text-base leading-relaxed">
              Set up your account in under 3 minutes and start generating hyperlocal campaigns for your region today.
            </p>
          </div>

          {/* Benefits */}
          <div className="space-y-3">
            {[
              'Free forever plan — no credit card needed',
              'Campaign ready in under 5 seconds',
              'Supports 15 Indian state market profiles',
              'Export campaigns to Meesho, Flipkart & more',
              'Real-time weather & festival intelligence',
            ].map(benefit => (
              <div key={benefit} className="flex items-center gap-3">
                <CheckCircle size={16} className="text-emerald-400 shrink-0" />
                <span className="text-sm text-gray-300">{benefit}</span>
              </div>
            ))}
          </div>

          {/* Step indicator visual */}
          <div className="card p-4">
            <p className="text-xs text-gray-500 mb-3">Signup progress</p>
            <div className="flex items-center gap-2">
              {steps.map((s, i) => (
                <div key={s.number} className="flex items-center gap-2 flex-1">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border transition-all
                    ${step > s.number ? 'bg-emerald-500 border-emerald-500 text-white' :
                      step === s.number ? 'bg-primary-600 border-primary-500 text-white' :
                      'bg-transparent border-white/20 text-gray-500'}`}
                  >
                    {step > s.number ? <CheckCircle size={13} /> : s.number}
                  </div>
                  <span className={`text-xs ${step >= s.number ? 'text-gray-300' : 'text-gray-600'}`}>{s.label}</span>
                  {i < steps.length - 1 && (
                    <div className={`flex-1 h-px ${step > s.number ? 'bg-emerald-500/40' : 'bg-white/10'}`} />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="relative text-xs text-gray-600">
          © 2026 TwinCart-AI · Sri Manakula Vinayagar Engineering College
        </div>
      </div>

      {/* ── Right panel (form) ── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 overflow-y-auto">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2.5 mb-8">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-glow-sm">
              <ShoppingCart size={18} className="text-white" />
            </div>
            <span className="text-xl font-bold text-white">TwinCart <span className="text-primary-400">AI</span></span>
          </div>

          {/* Step header */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              {steps.map((s, i) => (
                <div key={s.number} className="flex items-center gap-2">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border transition-all
                    ${step > s.number ? 'bg-emerald-500 border-emerald-500 text-white' :
                      step === s.number ? 'bg-primary-600 border-primary-500 text-white' :
                      'bg-transparent border-white/20 text-gray-600'}`}
                  >
                    {step > s.number ? <CheckCircle size={12} /> : s.number}
                  </div>
                  {i < steps.length - 1 && (
                    <div className={`w-10 h-px ${step > s.number ? 'bg-emerald-500/50' : 'bg-white/10'}`} />
                  )}
                </div>
              ))}
              <span className="ml-2 text-xs text-gray-500">Step {step} of {steps.length}</span>
            </div>

            <h1 className="text-3xl font-black text-white mb-1">
              {step === 1 && 'Create your account'}
              {step === 2 && 'Business details'}
              {step === 3 && 'Preferences'}
            </h1>
            <p className="text-gray-400 text-sm">
              {step === 1 && 'Set up your login credentials'}
              {step === 2 && 'Tell us about your store'}
              {step === 3 && 'Customise your experience'}
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-center gap-2.5 p-3.5 mb-5 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm animate-fade-in">
              <AlertCircle size={16} className="shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* ── STEP 1: Account ── */}
            {step === 1 && (
              <div className="space-y-5 animate-fade-in">
                {/* Full name */}
                <div>
                  <label className="label">Full name</label>
                  <div className="relative">
                    <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                      type="text" name="name" value={form.name}
                      onChange={handleChange}
                      placeholder="Priya Sharma"
                      className="input-field pl-10"
                      autoComplete="name"
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label className="label">Email address</label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                      type="email" name="email" value={form.email}
                      onChange={handleChange}
                      placeholder="you@example.com"
                      className="input-field pl-10"
                      autoComplete="email"
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label className="label">Password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                      type={showPass ? 'text' : 'password'} name="password" value={form.password}
                      onChange={handleChange}
                      placeholder="Create a strong password"
                      className="input-field pl-10 pr-10"
                      autoComplete="new-password"
                    />
                    <button type="button" onClick={() => setShowPass(v => !v)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors">
                      {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {/* Password strength */}
                  {form.password && (
                    <div className="mt-2 space-y-1">
                      {passwordRules.map(rule => (
                        <div key={rule.label} className={`flex items-center gap-2 text-xs transition-colors ${rule.test(form.password) ? 'text-emerald-400' : 'text-gray-500'}`}>
                          <CheckCircle size={11} className={rule.test(form.password) ? 'text-emerald-400' : 'text-gray-600'} />
                          {rule.label}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Confirm password */}
                <div>
                  <label className="label">Confirm password</label>
                  <div className="relative">
                    <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                      type={showConfirm ? 'text' : 'password'} name="confirmPassword" value={form.confirmPassword}
                      onChange={handleChange}
                      placeholder="Repeat your password"
                      className="input-field pl-10 pr-10"
                      autoComplete="new-password"
                    />
                    <button type="button" onClick={() => setShowConfirm(v => !v)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors">
                      {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button type="button" onClick={nextStep} className="btn-primary w-full justify-center py-3.5">
                  Continue <ArrowRight size={17} />
                </button>
              </div>
            )}

            {/* ── STEP 2: Business ── */}
            {step === 2 && (
              <div className="space-y-5 animate-fade-in">
                {/* Store name */}
                <div>
                  <label className="label">Store / Business name</label>
                  <div className="relative">
                    <Store size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                      type="text" name="storeName" value={form.storeName}
                      onChange={handleChange}
                      placeholder="Priya's Fashion Hub"
                      className="input-field pl-10"
                    />
                  </div>
                </div>

                {/* Platform */}
                <div>
                  <label className="label">Primary selling platform</label>
                  <div className="grid grid-cols-3 gap-2">
                    {PLATFORMS.map(p => (
                      <button
                        key={p} type="button"
                        onClick={() => { setForm(f => ({ ...f, platform: p })); setError(''); }}
                        className={`py-2.5 px-3 rounded-xl border text-sm font-medium transition-all
                          ${form.platform === p
                            ? 'bg-primary-600/25 border-primary-500/60 text-primary-300'
                            : 'bg-dark-800 border-white/10 text-gray-400 hover:border-white/25 hover:text-white'}`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>

                {/* State */}
                <div>
                  <label className="label">Operating state</label>
                  <div className="relative">
                    <MapPin size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500 z-10" />
                    <select name="state" value={form.state} onChange={handleChange} className="select-field pl-10">
                      <option value="">Select your state</option>
                      {STATES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button type="button" onClick={() => setStep(1)} className="btn-secondary flex-1 justify-center py-3.5">
                    Back
                  </button>
                  <button type="button" onClick={nextStep} className="btn-primary flex-1 justify-center py-3.5">
                    Continue <ArrowRight size={17} />
                  </button>
                </div>
              </div>
            )}

            {/* ── STEP 3: Preferences ── */}
            {step === 3 && (
              <div className="space-y-5 animate-fade-in">
                {/* Categories */}
                <div>
                  <label className="label">Product categories (select all that apply)</label>
                  <div className="grid grid-cols-2 gap-2">
                    {categories.map(cat => (
                      <button
                        key={cat} type="button"
                        onClick={() => toggleCategory(cat)}
                        className={`py-2.5 px-3 rounded-xl border text-sm font-medium text-left transition-all flex items-center gap-2
                          ${form.categories.includes(cat)
                            ? 'bg-primary-600/25 border-primary-500/60 text-primary-300'
                            : 'bg-dark-800 border-white/10 text-gray-400 hover:border-white/25 hover:text-white'}`}
                      >
                        {form.categories.includes(cat) && <CheckCircle size={13} className="text-primary-400 shrink-0" />}
                        {cat}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Summary card */}
                <div className="card p-4 space-y-2 bg-dark-700/80">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Account Summary</p>
                  {[
                    { label: 'Name',      value: form.name },
                    { label: 'Email',     value: form.email },
                    { label: 'Store',     value: form.storeName },
                    { label: 'Platform',  value: form.platform },
                    { label: 'State',     value: form.state },
                  ].map(row => (
                    <div key={row.label} className="flex justify-between text-sm">
                      <span className="text-gray-500">{row.label}</span>
                      <span className="text-gray-200 font-medium">{row.value || '—'}</span>
                    </div>
                  ))}
                </div>

                {/* Terms */}
                <label className="flex items-start gap-3 cursor-pointer group">
                  <div className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-all
                    ${form.agreeTerms ? 'bg-primary-600 border-primary-500' : 'bg-dark-800 border-white/20 group-hover:border-white/40'}`}
                    onClick={() => setForm(f => ({ ...f, agreeTerms: !f.agreeTerms }))}
                  >
                    {form.agreeTerms && <CheckCircle size={10} className="text-white" />}
                  </div>
                  <input type="checkbox" name="agreeTerms" checked={form.agreeTerms} onChange={handleChange} className="sr-only" />
                  <span className="text-sm text-gray-400">
                    I agree to the{' '}
                    <a href="#" className="text-primary-400 hover:text-primary-300">Terms of Service</a>
                    {' '}and{' '}
                    <a href="#" className="text-primary-400 hover:text-primary-300">Privacy Policy</a>
                  </span>
                </label>

                <div className="flex gap-3">
                  <button type="button" onClick={() => setStep(2)} className="btn-secondary flex-1 justify-center py-3.5">
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary flex-1 justify-center py-3.5 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <span className="spinner w-4 h-4" /> Creating…
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Zap size={16} /> Create Account
                      </span>
                    )}
                  </button>
                </div>
              </div>
            )}
          </form>

          {/* Sign in link */}
          <p className="text-center text-sm text-gray-500 mt-8">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
