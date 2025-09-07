import { AuthService } from './auth.service';
import type { ProfileFormData } from '../types';

const API_BASE = 'http://localhost:8080/api';

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  isProfileComplete: boolean;
  demographics?: {
    birthYear?: number;
    birthMonth?: number;
    gender?: 'male' | 'female' | 'other';
    heightCm?: number;
    weightKg?: number;
    bloodType?: string;
    province?: string;
    occupation?: string;
    educationLevel?: string;
  };
  medicalHistory?: string;
  allergies?: string;
  currentMedications?: string;
  smokingStatus?: string;
  drinkingStatus?: string;
}

export class UserService {
  
  /**
   * Cập nhật thông tin hồ sơ sức khỏe
   */
  static async updateHealthProfile(data: ProfileFormData): Promise<UserProfile> {
    try {
      const response = await fetch(`${API_BASE}/users/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
        body: JSON.stringify({
          // Map ProfileFormData to backend format
          name: data.name,
          birthYear: data.birthYear,
          birthMonth: data.birthMonth,
          gender: data.gender,
          heightCm: data.heightCm,
          weightKg: data.weightKg,
          bloodType: data.bloodType,
          provinceId: data.provinceId,
          occupation: data.occupation,
          educationLevel: data.educationLevel,
          // Lifestyle data - sẽ cần mapping phù hợp với backend
          medicalHistory: data.medicalHistory,
          allergies: data.allergies,
          currentMedications: data.currentMedications,
          smokingStatus: data.smokingStatus,
          drinkingStatus: data.drinkingStatus,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Cập nhật profile thất bại');
      }

      return result.data;
    } catch (error) {
      console.error('Error updating health profile:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Không thể cập nhật thông tin. Vui lòng thử lại.');
    }
  }

  /**
   * Lấy thông tin profile hiện tại
   */
  static async getCurrentProfile(): Promise<UserProfile> {
    try {
      const response = await fetch(`${API_BASE}/users/profile`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể lấy thông tin profile');
      }

      return result.data;
    } catch (error) {
      console.error('Error fetching current profile:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Không thể lấy thông tin profile. Vui lòng thử lại.');
    }
  }

  /**
   * Lấy thông tin user cơ bản
   */
  static async getCurrentUser(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE}/users/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...AuthService.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.message || 'Không thể lấy thông tin user');
      }

      return result.data;
    } catch (error) {
      console.error('Error fetching current user:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Không thể lấy thông tin user. Vui lòng thử lại.');
    }
  }
}
