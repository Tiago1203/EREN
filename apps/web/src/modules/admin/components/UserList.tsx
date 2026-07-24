'use client';

import type { User } from '../types/admin.types';

interface UserListProps {
  users: User[];
  onUserClick?: (user: User) => void;
  onUserEdit?: (user: User) => void;
}

export function UserList({ users, onUserClick, onUserEdit }: UserListProps) {
  const statusConfig = {
    active: { label: 'Activo', color: 'bg-green-100 text-green-800' },
    inactive: { label: 'Inactivo', color: 'bg-gray-100 text-gray-800' },
    pending: { label: 'Pendiente', color: 'bg-yellow-100 text-yellow-800' },
    suspended: { label: 'Suspendido', color: 'bg-red-100 text-red-800' },
  };

  return (
    <div className="space-y-3">
      {users.map((user) => {
        const status = statusConfig[user.status];
        return (
          <div
            key={user.id}
            className="card p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onUserClick?.(user)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {/* Avatar */}
                <div className="w-12 h-12 rounded-full bg-[var(--primary)] flex items-center justify-center text-white text-lg font-medium">
                  {user.name.charAt(0)}
                </div>
                
                {/* Info */}
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium">{user.name}</h3>
                    <span className={`badge ${status.color}`}>{status.label}</span>
                  </div>
                  <p className="text-sm text-muted">{user.email}</p>
                  {user.department && (
                    <p className="text-xs text-muted mt-1">{user.department}</p>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium">{user.role.name}</p>
                  {user.lastLogin && (
                    <p className="text-xs text-muted">
                      Último acceso: {formatTimeAgo(user.lastLogin)}
                    </p>
                  )}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onUserEdit?.(user);
                  }}
                  className="p-2 hover:bg-[var(--background)] rounded-lg"
                >
                  <svg className="w-5 h-5 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - new Date(date).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 60) return `hace ${minutes} min`;
  if (hours < 24) return `hace ${hours} h`;
  return `hace ${days} d`;
}

export default UserList;
