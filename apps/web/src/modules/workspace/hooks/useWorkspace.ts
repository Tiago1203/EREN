'use client';

import { useCallback, useEffect } from 'react';
import { useWorkspaceStore } from '../stores/workspace.store';
import { taskService } from '../services/task.service';
import { activityService } from '../services/activity.service';
import type { Task, TaskStatus } from '../types/workspace.types';

export interface UseWorkspaceReturn {
  tasks: Task[];
  selectedTask: Task | null;
  loading: boolean;
  error: string | null;
  loadTasks: () => Promise<void>;
  loadActivities: () => Promise<void>;
  createTask: (data: Partial<Task>) => Promise<Task>;
  updateTask: (id: string, data: Partial<Task>) => Promise<void>;
  moveTask: (id: string, newStatus: TaskStatus) => Promise<void>;
  selectTask: (task: Task | null) => void;
}

export function useWorkspace(): UseWorkspaceReturn {
  const {
    tasks,
    activities,
    selectedTask,
    loading,
    error,
    setTasks,
    addTask,
    updateTask: storeUpdateTask,
    moveTask: storeMoveTask,
    setSelectedTask,
    setActivities,
    setLoading,
    setError,
  } = useWorkspaceStore();

  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await taskService.getTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading tasks');
    } finally {
      setLoading(false);
    }
  }, [setTasks, setLoading, setError]);

  const loadActivities = useCallback(async () => {
    try {
      const data = await activityService.getActivities();
      setActivities(data);
    } catch (err) {
      console.error('Error loading activities:', err);
    }
  }, [setActivities]);

  const createTask = useCallback(async (data: Partial<Task>) => {
    const task = await taskService.createTask(data);
    addTask(task);
    return task;
  }, [addTask]);

  const updateTask = useCallback(async (id: string, data: Partial<Task>) => {
    try {
      const updated = await taskService.updateTask(id, data);
      storeUpdateTask(id, updated);
    } catch (err) {
      console.error('Error updating task:', err);
    }
  }, [storeUpdateTask]);

  const moveTask = useCallback(async (id: string, newStatus: TaskStatus) => {
    try {
      await taskService.moveTask(id, newStatus);
      storeMoveTask(id, newStatus);
    } catch (err) {
      console.error('Error moving task:', err);
    }
  }, [storeMoveTask]);

  const selectTask = useCallback((task: Task | null) => {
    setSelectedTask(task);
  }, [setSelectedTask]);

  useEffect(() => {
    loadTasks();
    loadActivities();
  }, []);

  return {
    tasks,
    selectedTask,
    loading,
    error,
    loadTasks,
    loadActivities,
    createTask,
    updateTask,
    moveTask,
    selectTask,
  };
}
