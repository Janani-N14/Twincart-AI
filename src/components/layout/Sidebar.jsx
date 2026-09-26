import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Globe, Users, Megaphone,
  FlaskConical, MessageSquareText, ShoppingCart,
  ChevronRight, Zap, BarChart3, X
} from 'lucide-react';

const navItems = [
  {
    group: 'Overview',
    items: [
      { label: 'Dashboard',       to: '/dashboard',                   icon: LayoutDashboard },
    ]
  },
  {
    group: 'Digital Twins',
    items: [
      { label: 'Regional Twins',  to: '/dashboard/regional-twins',    icon: Globe },
      { label: 'Segment Twins',   to: '/dashboard/segment-twins',     icon: Users },
    ]
  },
  {
    group: 'AI Tools',
    items: [
      { label: 'Campaign Generator', to: '/dashboard/campaigns',      icon: Megaphone },
      { label: 'Simulation Engine',  to: '/dashboard/simulation',     icon: FlaskConical },
      { label: 'Seller Intelligence',to: '/dashboard/seller-intel',   icon: MessageSquareText },
    ]
  },
  {
    group: 'Analytics',
    items: [
      { label: 'Analytics',       to: '/dashboard/analytics',         icon: BarChart3 },
    ]
  },
];

export default function Sidebar({ open, onClose }) {
  const location = useLocation();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar panel */}
      <aside className={`
        fixed top-0 left-0 h-full w-64 bg-dark-800 border-r border-white/10
        flex flex-col z-30 transition-transform duration-300
        ${open ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
      `}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-white/10 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-glow-sm">
              <ShoppingCart size={16} className="text-white" />
            </div>
            <div>
              <span className="text-base font-bold text-white tracking-tight">TwinCart</span>
              <span className="ml-1 text-[10px] font-semibold px-1.5 py-0.5 bg-primary-500/20 text-primary-300 rounded-md">AI</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-500 hover:text-white hover:bg-white/10 rounded-lg transition-all lg:hidden"
          >
            <X size={16} />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {navItems.map(group => (
            <div key={group.group}>
              <p className="text-[10px] font-semibold tracking-widest text-gray-600 uppercase px-3 mb-2">
                {group.group}
              </p>
              <ul className="space-y-0.5">
                {group.items.map(item => (
                  <li key={item.to}>
                    <NavLink
                      to={item.to}
                      end={item.to === '/dashboard'}
                      onClick={onClose}
                      className={({ isActive }) =>
                        isActive ? 'nav-item-active' : 'nav-item'
                      }
                    >
                      <item.icon size={17} />
                      <span className="flex-1">{item.label}</span>
                      <ChevronRight size={13} className="opacity-40" />
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        {/* Bottom promo card */}
        <div className="px-3 pb-4 shrink-0">
          <div className="card p-4 bg-gradient-to-br from-primary-600/20 to-accent-600/10 border-primary-500/20">
            <div className="flex items-center gap-2 mb-2">
              <Zap size={14} className="text-primary-400" />
              <span className="text-xs font-semibold text-primary-300">Pro Plan</span>
            </div>
            <p className="text-xs text-gray-400 mb-3">Unlock all 28 states, real-time data feeds & priority LLM.</p>
            <button className="w-full text-xs font-semibold py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg transition-colors">
              Upgrade Now
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
