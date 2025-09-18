import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  Heart, 
  Lock, 
  Plus 
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import type { ProfileFormData } from '../../types';
import { UserService } from '../../services/user.service';
import { MEDICAL_CONDITIONS, SMOKING_OPTIONS, DRINKING_OPTIONS, ROUTES } from '../../constants';
import './styles/ProfileSetupScreen.css';

const ProfileSetupScreen: React.FC = () => {
  const navigate = useNavigate();
  const { setHasCompletedProfile } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { }
  } = useForm<ProfileFormData>({
    defaultValues: {
      medicalHistory: '',
      allergies: '',
      currentMedications: '',
      smokingStatus: 'never' as const,
      drinkingStatus: 'never' as const
    }
  });

  // Watch the current value of medicalHistory to add suggestions
  const medicalHistoryValue = watch('medicalHistory');

  // Use predefined medical conditions from constants

  const handleMedicalConditionClick = (condition: string) => {
    const currentValue = medicalHistoryValue || '';
    const newValue = currentValue 
      ? `${currentValue}, ${condition}`
      : condition;
    setValue('medicalHistory', newValue);
  };

  const onSubmit = async (data: ProfileFormData) => {
    setIsLoading(true);
    
    try {
      await UserService.updateHealthProfile(data);
      
      toast.success('Hồ sơ đã được lưu thành công!', {
        duration: 3000,
        position: 'top-center',
      });
      
      // Mark profile as completed and navigate to dashboard
      setHasCompletedProfile(true);
      setTimeout(() => {
        navigate(ROUTES.DASHBOARD);
      }, 1000);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Có lỗi xảy ra khi lưu hồ sơ.';
      toast.error(errorMessage, {
        duration: 4000,
        position: 'top-center',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkip = () => {
    navigate(ROUTES.DASHBOARD);
  };


  return (
    <div className="profile-setup-screen">
      {/* Header */}
      <div className="profile-setup-header">
        <div className="profile-setup-header-content">
          <h1 className="profile-setup-title">
            Thiết lập hồ sơ y tế
          </h1>
          <button
            onClick={handleSkip}
            className="profile-skip-btn"
          >
            Bỏ qua
          </button>
        </div>
      </div>

      <div className="profile-setup-container">
        {/* Information Header */}
        <div className="profile-info-header">
          <div className="profile-info-content">
            <div className="profile-info-icon">
              <Heart size={24} />
            </div>
            <div className="profile-info-text">
              <h2>Thông tin sức khỏe của bạn</h2>
              <p>
                Cung cấp thông tin này sẽ giúp AI đưa ra các gợi ý chính xác và an toàn hơn cho riêng bạn.
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Medical History Section */}
          <div className="profile-form-section">
            <h3 className="profile-section-title">
              Tiền sử y tế
            </h3>
            
            {/* Medical Conditions */}
            <div className="profile-field">
              <label className="profile-field-label">
                Bệnh nền/Bệnh mãn tính
              </label>
              <textarea
                {...register('medicalHistory')}
                rows={4}
                className="profile-textarea"
                placeholder="Ví dụ: Tăng huyết áp, tiểu đường type 2..."
              />
              
              {/* Suggestion Chips */}
              <div className="profile-suggestions">
                <span className="profile-suggestions-label">Gợi ý:</span>
                <div className="profile-suggestions-list">
                  {MEDICAL_CONDITIONS.map((condition) => (
                    <button
                      key={condition}
                      type="button"
                      onClick={() => handleMedicalConditionClick(condition)}
                      className="profile-suggestion-chip"
                    >
                      <Plus size={14} />
                      {condition}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Allergies */}
            <div className="profile-field">
              <label className="profile-field-label">
                Dị ứng
              </label>
              <textarea
                {...register('allergies')}
                rows={3}
                className="profile-textarea"
                placeholder="Ví dụ: Dị ứng penicillin, đậu phộng..."
              />
            </div>

            {/* Current Medications */}
            <div className="profile-field">
              <label className="profile-field-label">
                Thuốc đang sử dụng
              </label>
              <textarea
                {...register('currentMedications')}
                rows={3}
                className="profile-textarea"
                placeholder="Ví dụ: Metformin 500mg, Lisinopril 10mg..."
              />
            </div>
          </div>

          {/* Lifestyle Section */}
          <div className="profile-form-section">
            <h3 className="profile-section-title">
              Lối sống & Thói quen
            </h3>
            
            {/* Smoking Status */}
            <div className="profile-field">
              <label className="profile-field-label">
                Hút thuốc lá
              </label>
              <div className="profile-choices">
                {SMOKING_OPTIONS.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setValue('smokingStatus', value)}
                    className={`profile-choice-chip ${watch('smokingStatus') === value ? 'selected' : ''}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Drinking Status */}
            <div className="profile-field">
              <label className="profile-field-label">
                Uống rượu bia
              </label>
              <div className="profile-choices">
                {DRINKING_OPTIONS.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setValue('drinkingStatus', value)}
                    className={`profile-choice-chip ${watch('drinkingStatus') === value ? 'selected' : ''}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Security Notice */}
          <div className="profile-security-notice">
            <div className="profile-security-content">
              <Lock className="profile-security-icon" size={24} />
              <p className="profile-security-text">
                Thông tin y tế của bạn được mã hóa và bảo mật tuyệt đối. 
                Chúng tôi cam kết không chia sẻ với bên thứ ba.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="profile-actions" >
            <button
              type="submit"
              disabled={isLoading}
              className="profile-primary-btn"
            >
              {isLoading ? (
                <>
                  <div className="profile-spinner" />
                  Đang lưu...
                </>
              ) : (
                'Lưu hồ sơ và tiếp tục'
              )}
            </button>
            
            <button
              type="button"
              onClick={handleSkip}
              className="profile-secondary-btn"
            >
              Tôi sẽ cập nhật sau
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileSetupScreen;
