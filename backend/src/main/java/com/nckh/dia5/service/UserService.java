package com.nckh.dia5.service;

import com.nckh.dia5.dto.user.UserDTO;
import com.nckh.dia5.model.User;
import com.nckh.dia5.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserService implements UserDetailsService {
    
    private final UserRepository userRepository;
    
    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with email: " + email));
    }
    
    public User findByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with email: " + email));
    }
    
    public User findById(String id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with id: " + id));
    }
    
    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }
    
    @Transactional
    public User createUser(String email, String passwordHash, String name) {
        if (existsByEmail(email)) {
            throw new RuntimeException("Email đã được sử dụng");
        }
        
        User user = User.builder()
                .id(UUID.randomUUID().toString())
                .email(email)
                .passwordHash(passwordHash)
                .name(name)
                .isProfileComplete(false)
                .isActive(true)
                .build();
        
        return userRepository.save(user);
    }
    
    @Transactional
    public void updateLastLoginTime(String userId) {
        userRepository.updateLastLoginTime(userId, LocalDateTime.now());
    }
    
    @Transactional
    public void updateProfileCompleteStatus(String userId, boolean isComplete) {
        userRepository.updateProfileCompleteStatus(userId, isComplete);
    }
    
    public UserDTO convertToDTO(User user) {
        return UserDTO.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .lastLoginAt(user.getLastLoginAt())
                .isProfileComplete(user.getIsProfileComplete())
                .isActive(user.getIsActive())
                .createdAt(user.getCreatedAt())
                .build();
    }
}
