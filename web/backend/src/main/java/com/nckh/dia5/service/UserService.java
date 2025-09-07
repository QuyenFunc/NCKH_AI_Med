package com.nckh.dia5.service;

import com.nckh.dia5.dto.user.UpdateProfileRequest;
import com.nckh.dia5.dto.user.UserProfileResponse;
import com.nckh.dia5.dto.user.UserResponse;
import com.nckh.dia5.handler.ResourceNotFoundException;
import com.nckh.dia5.model.Province;
import com.nckh.dia5.model.User;
import com.nckh.dia5.model.UserDemographic;
import com.nckh.dia5.repository.ProvinceRepository;
import com.nckh.dia5.repository.UserChronicDiseaseRepository;
import com.nckh.dia5.repository.UserDemographicRepository;
import com.nckh.dia5.repository.UserRepository;
import com.nckh.dia5.repository.UserMedicationRepository;
import com.nckh.dia5.repository.UserAllergyRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final UserDemographicRepository userDemographicRepository;
    private final ProvinceRepository provinceRepository;
    private final UserChronicDiseaseRepository userChronicDiseaseRepository;
    private final UserMedicationRepository userMedicationRepository;
    private final UserAllergyRepository userAllergyRepository;
    private final AuthService authService;

    public UserResponse getCurrentUserInfo() {
        User user = authService.getCurrentUser();
        return mapToUserResponse(user);
    }

    public UserProfileResponse getCurrentUserProfile() {
        User user = authService.getCurrentUser();
        UserDemographic demographic = userDemographicRepository.findByUserId(user.getId()).orElse(null);

        UserProfileResponse.UserProfileResponseBuilder builder = UserProfileResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .isProfileComplete(user.getIsProfileComplete());

        if (demographic != null) {
            builder.birthYear(demographic.getBirthYear())
                    .birthMonth(demographic.getBirthMonth())
                    .gender(demographic.getGender())
                    .heightCm(demographic.getHeightCm())
                    .weightKg(demographic.getWeightKg())
                    .bloodType(demographic.getBloodType())
                    .occupation(demographic.getOccupation())
                    .educationLevel(demographic.getEducationLevel());

            if (demographic.getProvince() != null) {
                builder.provinceName(demographic.getProvince().getName());
            }
        }

        // Get health summary
        Long chronicDiseaseCount = userChronicDiseaseRepository.countActiveByUserId(user.getId());
        Long activeMedicationCount = userMedicationRepository.countActiveByUserId(user.getId());
        Long allergyCount = userAllergyRepository.countActiveByUserId(user.getId());

        builder.chronicDiseaseCount(chronicDiseaseCount.intValue())
                .activeMedicationCount(activeMedicationCount.intValue())
                .allergyCount(allergyCount.intValue());

        return builder.build();
    }

    @Transactional
    public UserProfileResponse updateProfile(UpdateProfileRequest request) {
        User user = authService.getCurrentUser();

        // Update user basic info
        if (request.getName() != null) {
            user.setName(request.getName());
        }

        // Get or create user demographic
        UserDemographic demographic = userDemographicRepository.findByUserId(user.getId())
                .orElse(new UserDemographic());

        if (demographic.getId() == null) {
            demographic.setUser(user);
        }

        // Update demographic info
        if (request.getBirthYear() != null) {
            demographic.setBirthYear(request.getBirthYear());
        }
        if (request.getBirthMonth() != null) {
            demographic.setBirthMonth(request.getBirthMonth());
        }
        if (request.getGender() != null) {
            demographic.setGender(request.getGender());
        }
        if (request.getHeightCm() != null) {
            demographic.setHeightCm(request.getHeightCm());
        }
        if (request.getWeightKg() != null) {
            demographic.setWeightKg(request.getWeightKg());
        }
        if (request.getBloodType() != null) {
            demographic.setBloodType(request.getBloodType());
        }
        if (request.getOccupation() != null) {
            demographic.setOccupation(request.getOccupation());
        }
        if (request.getEducationLevel() != null) {
            demographic.setEducationLevel(request.getEducationLevel());
        }
        if (request.getProvinceId() != null) {
            Province province = provinceRepository.findById(request.getProvinceId())
                    .orElseThrow(() -> new ResourceNotFoundException("Province", "id", request.getProvinceId()));
            demographic.setProvince(province);
        }

        // Check if profile is complete
        boolean isProfileComplete = demographic.getBirthYear() != null &&
                demographic.getGender() != null &&
                user.getName() != null && !user.getName().trim().isEmpty();

        user.setIsProfileComplete(isProfileComplete);

        userRepository.save(user);
        userDemographicRepository.save(demographic);

        log.info("User profile updated: {}", user.getId());
        return getCurrentUserProfile();
    }

    public UserResponse getUserById(String userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", userId));
        return mapToUserResponse(user);
    }

    private UserResponse mapToUserResponse(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .isProfileComplete(user.getIsProfileComplete())
                .isActive(user.getIsActive())
                .createdAt(user.getCreatedAt())
                .lastLoginAt(user.getLastLoginAt())
                .build();
    }
}
