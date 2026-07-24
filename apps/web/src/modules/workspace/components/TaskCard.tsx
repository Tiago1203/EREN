'use client';

import type { Task } from '../types/workspace.types';

interface TaskCardProps {
  task: Task;
  onClick?: () => void;
}

export function TaskCard({ task, onClick }: TaskCardProps) {
  const priorityConfig = {
    low: { label: 'Baja', color: 'bg-gray-100 text-gray-600' },
    medium: { label: 'Media', color: 'bg-blue-100 text-blue-600' },
    high: { label: 'Alta', color: 'bg-orange-100 text-orange-600' },
    urgent: { label: 'Urgente', color: 'bg-red-100 text-red-600' },
  };

  const priority = priorityConfig[task.priority];

  return (
    <div
      className="card p-3 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-2">
        <span className={`badge ${priority.color} text-xs`}>
          {priority.label}
        </span>
        {task.dueDate && (
          <DueDateBadge dueDate={task.dueDate} />
        )}
      </div>

      <h3 className="font-medium text-sm mb-2 line-clamp-2">{task.title}</h3>

      {task.relatedEntity && (
        <div className="flex items-center gap-1 text-xs text-muted mb-2">
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <span className="truncate">{task.relatedEntity.name}</span>
        </div>
      )}

      <div className="flex items-center justify-between">
        {task.assignee && (
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[var(--primary)] flex items-center justify-center text-white text-xs">
              {task.assignee.name.charAt(0)}
            </div>
          </div>
        )}
        {task.tags.length > 0 && (
          <div className="flex gap-1">
            {task.tags.slice(0, 2).map((tag) => (
              <span key={tag} className="text-xs px-1.5 py-0.5 bg-[var(--background)] rounded text-muted">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function DueDateBadge({ dueDate }: { dueDate: Date }) {
  const now = new Date();
  const due = new Date(dueDate);
  const diff = due.getTime() - now.getTime();
  const days = Math.floor(diff / 86400000);

  let colorClass = 'text-gray-500';
  if (days < 0) colorClass = 'text-red-600';
  else if (days <= 1) colorClass = 'text-orange-600';
  else if (days <= 3) colorClass = 'text-yellow-600';

  return (
    <span className={`text-xs ${colorClass}`}>
      {days < 0 ? 'Vencida' : days === 0 ? 'Hoy' : days === 1 ? 'Mañana' : `${days}d`}
    </span>
  );
}

export default TaskCard;
