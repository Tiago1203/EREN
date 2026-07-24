'use client';

import { useState } from 'react';
import { TaskCard } from './TaskCard';
import type { Task, TaskStatus, TaskPriority } from '../types/workspace.types';

interface TaskBoardProps {
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  onTaskMove?: (taskId: string, newStatus: TaskStatus) => void;
}

export function TaskBoard({ tasks, onTaskClick, onTaskMove }: TaskBoardProps) {
  const [draggedTask, setDraggedTask] = useState<Task | null>(null);

  const columns: { id: TaskStatus; label: string; color: string }[] = [
    { id: 'backlog', label: 'Backlog', color: 'bg-gray-100' },
    { id: 'todo', label: 'Por Hacer', color: 'bg-blue-100' },
    { id: 'in_progress', label: 'En Progreso', color: 'bg-yellow-100' },
    { id: 'review', label: 'Revisión', color: 'bg-purple-100' },
    { id: 'done', label: 'Completado', color: 'bg-green-100' },
  ];

  const getTasksByStatus = (status: TaskStatus) =>
    tasks.filter((task) => task.status === status);

  const handleDragStart = (task: Task) => {
    setDraggedTask(task);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, status: TaskStatus) => {
    e.preventDefault();
    if (draggedTask && draggedTask.status !== status) {
      onTaskMove?.(draggedTask.id, status);
    }
    setDraggedTask(null);
  };

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((column) => {
        const columnTasks = getTasksByStatus(column.id);
        return (
          <div
            key={column.id}
            className={`flex-shrink-0 w-72 ${column.color} rounded-lg p-2`}
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, column.id)}
          >
            <div className="flex items-center justify-between mb-3 px-2">
              <h3 className="font-semibold text-sm">{column.label}</h3>
              <span className="text-xs bg-white px-2 py-0.5 rounded-full">
                {columnTasks.length}
              </span>
            </div>
            <div className="space-y-2 min-h-[200px]">
              {columnTasks.map((task) => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={() => handleDragStart(task)}
                >
                  <TaskCard task={task} onClick={() => onTaskClick?.(task)} />
                </div>
              ))}
              {columnTasks.length === 0 && (
                <div className="p-4 text-center text-sm text-muted border-2 border-dashed border-gray-200 rounded-lg">
                  Sin tareas
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default TaskBoard;
