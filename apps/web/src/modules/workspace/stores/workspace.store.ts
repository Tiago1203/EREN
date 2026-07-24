'use client';

import { create } from 'zustand';
import type { Task, Activity, WorkspaceState, TaskStatus } from '../types/workspace.types';

interface WorkspaceStore extends WorkspaceState {
  // Actions - Tasks
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, update: Partial<Task>) => void;
  removeTask: (id: string) => void;
  moveTask: (id: string, newStatus: TaskStatus) => void;
  setSelectedTask: (task: Task | null) => void;

  // Actions - Activities
  setActivities: (activities: Activity[]) => void;
  addActivity: (activity: Activity) => void;

  // Actions - State
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Actions - Reset
  reset: () => void;
}

const initialState: WorkspaceState = {
  tasks: [],
  activities: [],
  selectedTask: null,
  loading: false,
  error: null,
};

export const useWorkspaceStore = create<WorkspaceStore>((set) => ({
  ...initialState,

  // Tasks
  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
  updateTask: (id, update) => set((state) => ({
    tasks: state.tasks.map((t) => (t.id === id ? { ...t, ...update } : t)),
    selectedTask: state.selectedTask?.id === id
      ? { ...state.selectedTask, ...update }
      : state.selectedTask,
  })),
  removeTask: (id) => set((state) => ({
    tasks: state.tasks.filter((t) => t.id !== id),
    selectedTask: state.selectedTask?.id === id ? null : state.selectedTask,
  })),
  moveTask: (id, newStatus) => set((state) => ({
    tasks: state.tasks.map((t) =>
      t.id === id ? { ...t, status: newStatus } : t
    ),
  })),
  setSelectedTask: (task) => set({ selectedTask: task }),

  // Activities
  setActivities: (activities) => set({ activities }),
  addActivity: (activity) => set((state) => ({
    activities: [activity, ...state.activities],
  })),

  // State
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Reset
  reset: () => set(initialState),
}));
