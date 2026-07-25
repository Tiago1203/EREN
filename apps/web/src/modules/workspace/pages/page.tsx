'use client';

import { useState } from 'react';
import { useWorkspace } from '../hooks/useWorkspace';
import { TaskBoard } from '../components/TaskBoard';
import { ActivityFeed } from '../components/ActivityFeed';
import type { Task, TaskStatus } from '../types/workspace.types';

export default function WorkspacePage() {
  const {
    tasks,
    selectedTask,
    loading,
    error,
    moveTask,
    selectTask,
  } = useWorkspace();

  const [view, setView] = useState<'board' | 'list'>('board');

  const handleTaskMove = async (taskId: string, newStatus: TaskStatus) => {
    await moveTask(taskId, newStatus);
  };

  const handleTaskClick = (task: Task) => {
    selectTask(task);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)]">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Workspace</h1>
            <p className="text-sm text-muted mt-1">
              {tasks.length} tareas · {tasks.filter(t => t.status !== 'done').length} activas
            </p>
          </div>

          <div className="flex items-center gap-2">
            {/* View Toggle */}
            <div className="flex border border-[var(--border)] rounded-lg overflow-hidden">
              <button
                onClick={() => setView('board')}
                className={`px-3 py-1.5 text-sm ${
                  view === 'board'
                    ? 'bg-[var(--primary)] text-white'
                    : 'bg-[var(--card)] hover:bg-[var(--background)]'
                }`}
              >
                Tablero
              </button>
              <button
                onClick={() => setView('list')}
                className={`px-3 py-1.5 text-sm ${
                  view === 'list'
                    ? 'bg-[var(--primary)] text-white'
                    : 'bg-[var(--card)] hover:bg-[var(--background)]'
                }`}
              >
                Lista
              </button>
            </div>

            {/* New Task Button */}
            <button className="btn-primary">
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Nueva Tarea
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Main Content */}
        <div className="flex-1 overflow-auto p-4">
          {loading ? (
            <div className="flex gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="w-72 flex-shrink-0">
                  <div className="bg-gray-100 rounded-lg p-2">
                    <div className="h-6 bg-gray-200 rounded w-20 mb-3" />
                    <div className="space-y-2">
                      {[1, 2].map((j) => (
                        <div key={j} className="h-24 bg-white rounded-lg animate-pulse" />
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : view === 'board' ? (
            <TaskBoard
              tasks={tasks}
              onTaskClick={handleTaskClick}
              onTaskMove={handleTaskMove}
            />
          ) : (
            <div className="space-y-2">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="card p-4 hover:shadow-md cursor-pointer"
                  onClick={() => handleTaskClick(task)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="badge bg-gray-100">{task.status.replace('_', ' ')}</span>
                      <h3 className="font-medium">{task.title}</h3>
                    </div>
                    <div className="flex items-center gap-3">
                      {task.assignee && (
                        <span className="text-sm text-muted">{task.assignee.name}</span>
                      )}
                      {task.dueDate && (
                        <span className="text-sm text-muted">
                          {new Date(task.dueDate).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar - Activity Feed */}
        <div className="w-80 border-l border-[var(--border)] bg-[var(--card)] overflow-y-auto p-4">
          <h2 className="font-semibold mb-4">Actividad Reciente</h2>
          <ActivityFeed activities={[]} loading={loading} />
        </div>
      </div>

      {/* Task Detail Modal */}
      {selectedTask && (
        <TaskModal task={selectedTask} onClose={() => selectTask(null)} />
      )}
    </div>
  );
}

interface TaskModalProps {
  task: Task;
  onClose: () => void;
}

function TaskModal({ task, onClose }: TaskModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-[var(--card)] rounded-lg shadow-xl w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">{task.title}</h2>
          <button onClick={onClose} className="p-2 hover:bg-[var(--background)] rounded-lg">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {task.description && (
          <p className="text-muted mb-4">{task.description}</p>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted">Estado</p>
            <p className="font-medium capitalize">{task.status.replace('_', ' ')}</p>
          </div>
          <div>
            <p className="text-sm text-muted">Prioridad</p>
            <p className="font-medium capitalize">{task.priority}</p>
          </div>
          {task.assignee && (
            <div>
              <p className="text-sm text-muted">Asignado</p>
              <p className="font-medium">{task.assignee.name}</p>
            </div>
          )}
          {task.dueDate && (
            <div>
              <p className="text-sm text-muted">Fecha límite</p>
              <p className="font-medium">{new Date(task.dueDate).toLocaleDateString()}</p>
            </div>
          )}
        </div>

        {task.tags.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-muted mb-2">Tags</p>
            <div className="flex flex-wrap gap-2">
              {task.tags.map((tag) => (
                <span key={tag} className="px-2 py-1 text-sm bg-[var(--background)] rounded">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end gap-2">
          <button onClick={onClose} className="btn-secondary">
            Cerrar
          </button>
          <button className="btn-primary">
            Editar Tarea
          </button>
        </div>
      </div>
    </div>
  );
}
