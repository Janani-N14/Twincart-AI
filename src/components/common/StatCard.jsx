import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function StatCard({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'primary' }) {
  const colorMap = {
    primary: 'from-primary-500/20 to-primary-600/5 border-primary-500/20 text-primary-400',
    accent:  'from-accent-500/20 to-accent-600/5 border-accent-500/20 text-accent-400',
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20 text-emerald-400',
    amber:   'from-amber-500/20 to-amber-600/5 border-amber-500/20 text-amber-400',
    rose:    'from-rose-500/20 to-rose-600/5 border-rose-500/20 text-rose-400',
    sky:     'from-sky-500/20 to-sky-600/5 border-sky-500/20 text-sky-400',
  };

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;
  const trendColor = trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-gray-400';

  return (
    <div className={`stat-card bg-gradient-to-br ${colorMap[color]} border rounded-2xl`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-xl bg-dark-800/60 border ${colorMap[color].split(' ').find(c => c.startsWith('border'))}`}>
            <Icon size={20} className={colorMap[color].split(' ').pop()} />
          </div>
        )}
      </div>
      {trendValue && (
        <div className={`flex items-center gap-1 text-xs font-medium ${trendColor}`}>
          <TrendIcon size={13} />
          <span>{trendValue}</span>
        </div>
      )}
    </div>
  );
}
