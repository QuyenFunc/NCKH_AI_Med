export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  metadata?: ChatMetadata;
}

// Chat Streaming Types
export interface ChatChunkData {
  chunk: string;
  word_index?: number;  // Optional vì Python không gửi
  session_id?: string;
  [key: string]: any;
}

export interface ChatFinalData {
  type: 'final';
  confidence: number;
  sources: ChatSource[];
  processing_time?: number;
  search_time?: number;
  session_id?: string;
  intent?: string;
  [key: string]: any;
}

export interface ChatSource {
  title: string;
  url?: string;
  content?: string;  // Optional vì Python không có
  confidence?: number;
}

export interface ChatMetadata {
  confidence?: number;
  sources?: ChatSource[];
  processingTime?: number;
}

export interface ChatStreamCallbacks {
  onChunk: (chunkData: ChatChunkData) => void;
  onComplete: (finalData: ChatFinalData) => void;
  onError: (error: Error) => void;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  createdAt: Date;
}

// Profile Form Data
export interface ProfileFormData {
  name?: string;
  birthYear?: number;
  birthMonth?: number;
  gender?: 'male' | 'female' | 'other';
  heightCm?: number;
  weightKg?: number;
  bloodType?: string;
  provinceId?: number;
  occupation?: string;
  educationLevel?: string;
  medicalHistory?: string;
  allergies?: string;
  currentMedications?: string;
  smokingStatus?: 'never' | 'former' | 'current';
  drinkingStatus?: 'never' | 'occasional' | 'frequent';
}

export interface ApiErrorData {
  message: string;
  code?: string;
  details?: any;
}


// Auth Types cho backend Spring Boot
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
  name?: string;
}

export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
  user: UserInfo;
}

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  isProfileComplete: boolean;
  isActive: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
  statusCode: number;
  timestamp: string;
}