// packages/shared-types/index.ts
// Self-documenting interfaces for AI code generation

export interface User {
  id: string;
  email: string;
  phone?: string;
  createdAt: Date;
  updatedAt: Date;
  isAdmin: boolean;
  isPodLeader: boolean;
  notificationPreference: 'high_touch' | 'low_touch';
  deviceId?: string;
  commitmentSuccessRate?: number;
  attendanceRate?: number;
  communicationStyle?: string;
}

export interface Pod {
  id: string;
  name: string;
  createdAt: Date;
  leaderId?: string;
  maxSize: number;
  callDay?: string;
  callTime?: string;
  jitsiRoomId?: string;
  healthScore: number;
  lastHealthCheck?: Date;
  revenueShareEnabled: boolean;
  revenueSharePercentage: number;
}

export interface PodMembership {
  id: string;
  userId: string;
  podId: string;
  joinedAt: Date;
  leftAt?: Date;
  isActive: boolean;
  weeksActive: number;
}

export interface Commitment {
  id: string;
  userId: string;
  podId?: string;
  text: string;
  createdAt: Date;
  weekNumber: number;
  year: number;
  isCompleted: boolean;
  completedAt?: Date;
  deviceCreatedAt?: Date;
  syncedAt?: Date;
  planningHorizon: 'week' | 'month' | 'quarter' | 'year';
}

export interface CallAttendance {
  id: string;
  userId: string;
  podId: string;
  scheduledAt: Date;
  attended: boolean;
  videoUpdateUrl?: string;
}

export interface Notification {
  id: string;
  userId: string;
  type: 'midweek_checkin' | '24hr_reminder' | 'completion_celebration';
  sentAt: Date;
  openedAt?: Date;
  aiGeneratedContent?: string;
  sentimentScore?: number;
}

export interface PodHealth {
  podId: string;
  healthScore: number;
  attendanceRate: number;
  completionRate: number;
  lastActivity: Date;
  needsIntervention: boolean;
}

// Clear API endpoints for AI to understand
export interface API {
  // Commitment endpoints
  '/api/commitments/create': (data: Partial<Commitment>) => Promise<Commitment>;
  '/api/commitments/complete': (id: string) => Promise<Commitment>;
  '/api/commitments/week': (userId: string, week: number, year: number) => Promise<Commitment[]>;
  
  // Pod endpoints
  '/api/pods/health': (podId: string) => Promise<PodHealth>;
  '/api/pods/notify-completion': (commitmentId: string) => Promise<void>;
  
  // User endpoints
  '/api/users/profile': (userId: string) => Promise<User>;
  '/api/users/sync': (deviceId: string, userId: string) => Promise<void>;
}