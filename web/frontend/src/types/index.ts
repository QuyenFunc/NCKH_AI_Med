export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  createdAt: Date;
}

export interface ApiErrorData {
  message: string;
  code?: string;
  details?: any;
}

export interface ProfileFormData {
  medicalHistory: string;
  allergies: string;
  currentMedications: string;
  smokingStatus: 'never' | 'former' | 'current';
  drinkingStatus: 'never' | 'occasional' | 'frequent';
}