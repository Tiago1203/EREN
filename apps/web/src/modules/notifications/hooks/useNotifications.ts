'use client';

import { useCallback, useEffect } from 'react';
import { useNotificationsStore } from '../stores/notifications.store';
import { notificationService } from '../services/notification.service';
import type { Notification } from '../types/notifications.types';

export interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  loadNotifications: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  removeNotification: (id: string) => Promise<void>;
}

export function useNotifications(): UseNotificationsReturn {
  const {
    notifications,
    unreadCount,
    loading,
    error,
    setNotifications,
    addNotification,
    markAsRead: storeMarkAsRead,
    markAllAsRead: storeMarkAllAsRead,
    removeNotification: storeRemove,
    setLoading,
    setError,
  } = useNotificationsStore();

  const loadNotifications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await notificationService.getNotifications();
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading notifications');
    } finally {
      setLoading(false);
    }
  }, [setNotifications, setLoading, setError]);

  const markAsRead = useCallback(async (id: string) => {
    try {
      await notificationService.markAsRead(id);
      storeMarkAsRead(id);
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  }, [storeMarkAsRead]);

  const markAllAsRead = useCallback(async () => {
    try {
      await notificationService.markAllAsRead();
      storeMarkAllAsRead();
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  }, [storeMarkAllAsRead]);

  const removeNotification = useCallback(async (id: string) => {
    try {
      await notificationService.deleteNotification(id);
      storeRemove(id);
    } catch (err) {
      console.error('Error removing notification:', err);
    }
  }, [storeRemove]);

  useEffect(() => {
    loadNotifications();
  }, []);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    loadNotifications,
    markAsRead,
    markAllAsRead,
    removeNotification,
  };
}
