'use client';

import type { Activity } from '../types/workspace.types';

interface ActivityFeedProps {
  activities: Activity[];
  loading?: boolean;
}

export function ActivityFeed({ activities, loading }: ActivityFeedProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="flex gap-3 animate-pulse">
            <div className="w-8 h-8 bg-gray-200 rounded-full" />
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-muted">
        No hay actividad reciente
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <ActivityItem key={activity.id} activity={activity} />
      ))}
    </div>
  );
}

interface ActivityItemProps {
  activity: Activity;
}

function ActivityItem({ activity }: ActivityItemProps) {
  const typeConfig = {
    created: { icon: '➕', color: 'text-green-600' },
    updated: { icon: '✏️', color: 'text-blue-600' },
    deleted: { icon: '🗑️', color: 'text-red-600' },
    commented: { icon: '💬', color: 'text-purple-600' },
    assigned: { icon: '👤', color: 'text-orange-600' },
    completed: { icon: '✅', color: 'text-green-600' },
  };

  const config = typeConfig[activity.type];
  const timeAgo = getTimeAgo(activity.timestamp);

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-[var(--background)] flex items-center justify-center flex-shrink-0">
        <span>{config.icon}</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">{activity.user.name}</span>
          <span className="text-xs text-muted">{timeAgo}</span>
        </div>
        <p className="text-sm text-muted mt-0.5">
          <span className="font-medium">{activity.title}</span>
          {activity.description && `: ${activity.description}`}
        </p>
      </div>
    </div>
  );
}

function getTimeAgo(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - new Date(date).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Ahora';
  if (minutes < 60) return `Hace ${minutes}m`;
  if (hours < 24) return `Hace ${hours}h`;
  return `Hace ${days}d`;
}

export default ActivityFeed;
