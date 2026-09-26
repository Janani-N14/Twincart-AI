import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCart, Menu, X } from 'lucide-react';

const links = [
  { label: 'Features', href: '#features' },
  { label: 'How it Works', href: '#how-it-works' },
  { label: 'Stats', href: '#stats' },
  { label: 'Testimonials', href: '#testimonials' },
];

export default function LandingNav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled ? 'bg-dark-900/90 backdrop-blur-md border-b border-white/10 py-3' : 'bg-transparent py-5'
    }`}>
      <div className="max-w-7xl mx-auto px-6 lg:px-8 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-glow-sm">
            <ShoppingCart size={18} className="text-white" />
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-xl font-bold text-white tracking-tight">TwinCart</span>
            <span className="text-[10px] font-semibold px-1.5 py-0.5 bg-primary-500/20 text-primary-300 rounded-md border border-primary-500/30">AI</span>
          </div>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {links.map(l => (
            <a key={l.label} href={l.href} className="btn-ghost text-sm">
              {l.label}
            </a>
          ))}
        </nav>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-3">
          <Link to="/login" className="btn-ghost text-sm">Sign in</Link>
          <Link to="/signup" className="btn-primary text-sm py-2 px-4">Get Started</Link>
        </div>

        {/* Mobile */}
        <button
          onClick={() => setMenuOpen(v => !v)}
          className="md:hidden p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg"
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-dark-800/95 backdrop-blur-md border-t border-white/10 px-6 py-4 space-y-1 animate-slide-up">
          {links.map(l => (
            <a
              key={l.label}
              href={l.href}
              onClick={() => setMenuOpen(false)}
              className="block py-2.5 text-sm text-gray-300 hover:text-white"
            >
              {l.label}
            </a>
          ))}
          <div className="pt-3 flex flex-col gap-2 border-t border-white/10 mt-3">
            <Link to="/login" onClick={() => setMenuOpen(false)} className="btn-secondary text-sm justify-center">Sign in</Link>
            <Link to="/signup" onClick={() => setMenuOpen(false)} className="btn-primary text-sm justify-center">Get Started</Link>
          </div>
        </div>
      )}
    </header>
  );
}
