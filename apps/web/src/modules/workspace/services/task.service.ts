/**
 * Task Service
 */

import type { Task, TaskStatus, TaskPriority, User, RelatedEntity } from '../types/workspace.types';

export class TaskService {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/tasks') {
    this.baseUrl = baseUrl;
  }

  async getTasks(): Promise<Task[]> {
    return this.getMockTasks();
  }

  async getTask(id: string): Promise<Task | null> {
    const tasks = this.getMockTasks();
    return tasks.find((t) => t.id === id) || null;
  }

  async createTask(data: Partial<Task>): Promise<Task> {
    const task: Task = {
      id: `task-${Date.now()}`,
      title: data.title || 'Nueva tarea',
      description: data.description,
      status: 'todo',
      priority: data.priority || 'medium',
      tags: data.tags || [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    return task;
  }

  async updateTask(id: string, data: Partial<Task>): Promise<Task> {
    const task = await this.getTask(id);
    if (!task) throw new Error('Task not found');
    return { ...task, ...data, updatedAt: new Date() };
  }

  async deleteTask(id: string): Promise<void> {
    console.log('Delete task:', id);
  }

  async moveTask(id: string, newStatus: TaskStatus): Promise<Task> {
    return this.updateTask(id, { status: newStatus });
  }

  private getMockTasks(): Task[] {
    const users: User[] = [
      { id: 'user-1', name: 'Carlos García', email: 'carlos@hospital.com', role: 'Ingeniero' },
      { id: 'user-2', name: 'María López', email: 'maria@hospital.com', role: 'Técnico' },
      { id: 'user-3', name: 'Juan Pérez', email: 'juan@hospital.com', role: 'Coordinador' },
    ];

    return [
      {
        id: 'task-1',
        title: 'Revisar bomba de infusión #BI-004',
        description: 'El usuario reporta error en la pantalla. Verificar conexiones y calibración.',
        status: 'in_progress',
        priority: 'high',
        assignee: users[0],
        reporter: users[2],
        dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
        tags: ['bomba', 'infusión', 'urgente'],
        relatedEntity: { type: 'device', id: 'BI-004', name: 'Bomba de Infusión #BI-004' },
        createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      },
      {
        id: 'task-2',
        title: 'Actualizar certificado de calibración',
        description: 'El certificado del monitor #MON-012 está por vencer. Solicitar recalibración.',
        status: 'todo',
        priority: 'medium',
        assignee: users[1],
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        tags: ['certificado', 'calibración'],
        relatedEntity: { type: 'device', id: 'MON-012', name: 'Monitor #MON-012' },
        createdAt: new Date(Date.now() - 48 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 48 * 60 * 60 * 1000),
      },
      {
        id: 'task-3',
        title: 'Revisar incidente #INC-023',
        description: 'Incidente reportado en UCI. Evaluar causa raíz.',
        status: 'review',
        priority: 'urgent',
        assignee: users[0],
        reporter: users[2],
        dueDate: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000),
        tags: ['incidente', 'UCI', 'crítico'],
        relatedEntity: { type: 'incident', id: 'INC-023', name: 'Incidente #INC-023' },
        createdAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
      },
      {
        id: 'task-4',
        title: 'Mantenimiento preventivo mensual',
        description: 'Ejecutar mantenimiento preventivo de equipos de esterilización.',
        status: 'backlog',
        priority: 'low',
        assignee: users[1],
        dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
        tags: ['preventivo', 'mensual'],
        createdAt: new Date(Date.now() - 72 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 72 * 60 * 60 * 1000),
      },
      {
        id: 'task-5',
        title: 'Actualizar inventario de repuestos',
        description: 'Verificar stock de repuestos para bombas de infusión.',
        status: 'done',
        priority: 'medium',
        assignee: users[2],
        tags: ['inventario', 'repuestos'],
        createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      },
    ];
  }
}

export const taskService = new TaskService();
