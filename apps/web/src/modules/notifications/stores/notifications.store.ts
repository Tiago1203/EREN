'use client';

import { create } from 'zustand';
import type { Notification, NotificationsState } from '../types/notifications.types';

interface NotificationsStore extends NotificationsState {
  // Actions
  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState: NotificationsState = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
};

export const useNotificationsStore = create<NotificationsStore>((set) => ({
  ...initialState,

  setNotifications: (notifications) => set({
    notifications,
    unreadCount: notifications.filter((n) => !n.read).length,
  }),

  addNotification: (notification) => set((state) => ({
    notifications: [notification, ...state.notifications],
    unreadCount: state.unreadCount + (notification.read ? 0 : 1),
  })),

  markAsRead: (id) => set((state) => {
    const notification = state.notifications.find((n) => n.id === id);
    if (!notification || notification.read) return state;

    return {
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    };
  }),

  markAllAsRead: () => set((state) => ({
    notifications: state.notifications.map((n) => ({ ...n, read: true })),
    unreadCount: 0,
  })),

  removeNotification: (id) => set((state) => {
    const notification = state.notifications.find((n) => n.id === id);
    return {
      notifications: state.notifications.filter((n) => n.id !== id),
      unreadCount: notification && !notification.read
        ? Math.max(0, state.unreadCount - 1)
        : state.unreadCount,
    };
  }),

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
