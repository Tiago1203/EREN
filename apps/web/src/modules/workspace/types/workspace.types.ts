/**
 * Tipos para el módulo Workspace
 */

export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type ActivityType = 'created' | 'updated' | 'deleted' | 'commented' | 'assigned' | 'completed';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee?: User;
  reporter?: User;
  dueDate?: Date;
  tags: string[];
  relatedEntity?: RelatedEntity;
  comments?: Comment[];
  attachments?: Attachment[];
  createdAt: Date;
  updatedAt: Date;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role?: string;
}

export interface RelatedEntity {
  type: 'work_order' | 'incident' | 'device' | 'article';
  id: string;
  name: string;
}

export interface Comment {
  id: string;
  content: string;
  author: User;
  createdAt: Date;
}

export interface Attachment {
  id: string;
  name: string;
  url: string;
  type: string;
  size: number;
}

export interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description?: string;
  user: User;
  timestamp: Date;
  entityType?: string;
  entityId?: string;
  metadata?: Record<string, unknown>;
}

export interface TaskFilters {
  status?: TaskStatus[];
  priority?: TaskPriority[];
  assigneeId?: string;
  tags?: string[];
}

export interface WorkspaceState {
  tasks: Task[];
  activities: Activity[];
  selectedTask: Task | null;
  loading: boolean;
  error: string | null;
}
