import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShoppingCart, Bell, Search, ChevronDown,
  LogOut, User, Settings, Menu, X
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar({ onMenuClick, sidebarOpen }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const notifications = [
    { id: 1, text: 'Campaign generated for Tamil Nadu', time: '2m ago', unread: true },
    { id: 2, text: 'Demand forecast updated for Diwali season', time: '1h ago', unread: true },
    { id: 3, text: 'Simulation run completed successfully', time: '3h ago', unread: false },
    { id: 4, text: 'New catalog gap detected in Electronics', time: '1d ago', unread: false },
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <header className="h-16 border-b border-white/10 bg-dark-800/80 backdrop-blur-md flex items-center justify-between px-4 lg:px-6 sticky top-0 z-30">
      {/* Left */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-all lg:hidden"
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        <div className="hidden sm:flex items-center gap-2 bg-dark-700/60 border border-white/10 rounded-xl px-3 py-2 w-56 lg:w-72">
          <Search size={15} className="text-gray-500 shrink-0" />
          <input
            type="text"
            placeholder="Search regions, campaigns…"
            className="bg-transparent text-sm text-gray-300 placeholder-gray-500 outline-none w-full"
          />
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => { setNotifOpen(v => !v); setDropdownOpen(false); }}
            className="relative p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-xl transition-all"
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-primary-500 rounded-full text-[10px] font-bold flex items-center justify-center text-white">
                {unreadCount}
              </span>
            )}
          </button>

          {notifOpen && (
            <div className="absolute right-0 top-12 w-80 bg-dark-700 border border-white/10 rounded-2xl shadow-card overflow-hidden z-50 animate-slide-up">
              <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
                <span className="text-sm font-semibold text-white">Notifications</span>
                <span className="badge-primary">{unreadCount} new</span>
              </div>
              <div className="divide-y divide-white/5 max-h-72 overflow-y-auto">
                {notifications.map(n => (
                  <div key={n.id} className={`px-4 py-3 hover:bg-white/5 transition-colors ${n.unread ? 'bg-primary-500/5' : ''}`}>
                    <div className="flex items-start gap-3">
                      {n.unread && <span className="mt-1.5 w-2 h-2 rounded-full bg-primary-400 shrink-0" />}
                      {!n.unread && <span className="mt-1.5 w-2 h-2 rounded-full bg-transparent shrink-0" />}
                      <div>
                        <p className="text-sm text-gray-200">{n.text}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{n.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="px-4 py-3 border-t border-white/10">
                <button className="text-xs text-primary-400 hover:text-primary-300 font-medium">
                  Mark all as read
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => { setDropdownOpen(v => !v); setNotifOpen(false); }}
            className="flex items-center gap-2 px-3 py-2 hover:bg-white/10 rounded-xl transition-all"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-sm font-bold">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium text-white leading-none">{user?.name || 'Seller'}</p>
              <p className="text-xs text-gray-500 mt-0.5">{user?.email || ''}</p>
            </div>
            <ChevronDown size={14} className={`text-gray-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 top-14 w-52 bg-dark-700 border border-white/10 rounded-2xl shadow-card overflow-hidden z-50 animate-slide-up">
              <div className="px-4 py-3 border-b border-white/10">
                <p className="text-sm font-semibold text-white">{user?.name || 'Seller'}</p>
                <p className="text-xs text-gray-500">{user?.email || ''}</p>
              </div>
              <div className="py-1">
                <Link
                  to="/dashboard/settings"
                  onClick={() => setDropdownOpen(false)}
                  className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <User size={15} /> Profile
                </Link>
                <Link
                  to="/dashboard/settings"
                  onClick={() => setDropdownOpen(false)}
                  className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <Settings size={15} /> Settings
                </Link>
              </div>
              <div className="py-1 border-t border-white/10">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                >
                  <LogOut size={15} /> Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
