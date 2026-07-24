/**
 * Tipos para el módulo Connectors
 * Framework preparado para FHIR, HL7, DICOM
 */

export type ConnectorType = 'fhir' | 'hl7_v2' | 'dicom' | 'mqtt' | 'rest' | 'custom';
export type ConnectorStatus = 'connected' | 'disconnected' | 'error' | 'syncing';

export interface ConnectorConfig {
  id: string;
  name: string;
  type: ConnectorType;
  enabled: boolean;
  status: ConnectorStatus;
  config: Record<string, unknown>;
  credentials?: Record<string, unknown>;
  lastSync?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface Connector {
  id: string;
  name: string;
  type: ConnectorType;
  enabled: boolean;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  sync(): Promise<SyncResult>;
  healthCheck(): Promise<HealthStatus>;
}

export interface SyncResult {
  success: boolean;
  recordsProcessed: number;
  errors: SyncError[];
  duration: number;
  timestamp: Date;
}

export interface SyncError {
  code: string;
  message: string;
  recordId?: string;
}

export interface HealthStatus {
  healthy: boolean;
  latency?: number;
  message?: string;
}

// ============== FHIR ==============

export interface FHIRConfig {
  baseUrl: string;
  version: 'r4' | 'stu3';
  auth?: FHIRAuth;
}

export interface FHIRAuth {
  type: 'basic' | 'bearer' | 'oauth2';
  token?: string;
  username?: string;
  password?: string;
  clientId?: string;
  clientSecret?: string;
}

// ============== HL7 ==============

export interface HL7Config {
  host: string;
  port: number;
  application: string;
  facility: string;
  encoding?: string;
}

// ============== DICOM ==============

export interface DICOMConfig {
  aeTitle: string;
  host: string;
  port: number;
  tls: boolean;
  certPath?: string;
  keyPath?: string;
}
