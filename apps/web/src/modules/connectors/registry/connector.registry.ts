/**
 * Connector Registry
 * Patrón Registry para gestión de conectores
 */

import type { Connector, ConnectorConfig, SyncResult, HealthStatus } from '../types/connector.types';

export class ConnectorRegistry {
  private static instance: ConnectorRegistry;
  private connectors: Map<string, Connector> = new Map();
  private configs: Map<string, ConnectorConfig> = new Map();

  private constructor() {}

  static getInstance(): ConnectorRegistry {
    if (!ConnectorRegistry.instance) {
      ConnectorRegistry.instance = new ConnectorRegistry();
    }
    return ConnectorRegistry.instance;
  }

  register(connector: Connector, config: ConnectorConfig): void {
    this.connectors.set(connector.id, connector);
    this.configs.set(connector.id, config);
  }

  unregister(id: string): void {
    this.connectors.delete(id);
    this.configs.delete(id);
  }

  get(id: string): Connector | null {
    return this.connectors.get(id) || null;
  }

  getConfig(id: string): ConnectorConfig | null {
    return this.configs.get(id) || null;
  }

  list(): Connector[] {
    return Array.from(this.connectors.values());
  }

  listConfigs(): ConnectorConfig[] {
    return Array.from(this.configs.values());
  }

  async connect(id: string): Promise<void> {
    const connector = this.connectors.get(id);
    if (!connector) {
      throw new Error(`Connector ${id} not found`);
    }
    await connector.connect();
    
    const config = this.configs.get(id);
    if (config) {
      config.status = 'connected';
      this.configs.set(id, config);
    }
  }

  async disconnect(id: string): Promise<void> {
    const connector = this.connectors.get(id);
    if (!connector) {
      throw new Error(`Connector ${id} not found`);
    }
    await connector.disconnect();
    
    const config = this.configs.get(id);
    if (config) {
      config.status = 'disconnected';
      this.configs.set(id, config);
    }
  }

  async sync(id: string): Promise<SyncResult> {
    const connector = this.connectors.get(id);
    if (!connector) {
      throw new Error(`Connector ${id} not found`);
    }
    
    const config = this.configs.get(id);
    if (config) {
      config.status = 'syncing';
      this.configs.set(id, config);
    }
    
    try {
      const result = await connector.sync();
      
      if (config) {
        config.status = 'connected';
        config.lastSync = new Date();
        this.configs.set(id, config);
      }
      
      return result;
    } catch (error) {
      if (config) {
        config.status = 'error';
        this.configs.set(id, config);
      }
      throw error;
    }
  }

  async healthCheck(id: string): Promise<HealthStatus> {
    const connector = this.connectors.get(id);
    if (!connector) {
      throw new Error(`Connector ${id} not found`);
    }
    return connector.healthCheck();
  }

  async syncAll(): Promise<Map<string, SyncResult>> {
    const results = new Map<string, SyncResult>();
    
    for (const [id] of this.connectors) {
      try {
        const result = await this.sync(id);
        results.set(id, result);
      } catch (error) {
        results.set(id, {
          success: false,
          recordsProcessed: 0,
          errors: [{ code: 'SYNC_ERROR', message: String(error) }],
          duration: 0,
          timestamp: new Date(),
        });
      }
    }
    
    return results;
  }
}

export const connectorRegistry = ConnectorRegistry.getInstance();
