package com.nckh.dia5.service;

import com.nckh.dia5.dto.auth.AuthResponse;
import com.nckh.dia5.dto.auth.LoginRequest;
import com.nckh.dia5.dto.auth.RegisterRequest;
import com.nckh.dia5.model.User;
import com.nckh.dia5.security.JwtUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {
    
    private final AuthenticationManager authenticationManager;
    private final UserService userService;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;
    
    @Transactional
    public AuthResponse login(LoginRequest request) {
        try {
            // Authenticate user
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
            );
            
            UserDetails userDetails = (UserDetails) authentication.getPrincipal();
            User user = userService.findByEmail(userDetails.getUsername());
            
            // Generate JWT token
            String token = jwtUtils.generateToken(userDetails);
            
            // Update last login time
            userService.updateLastLoginTime(user.getId());
            
            // Return response
            return AuthResponse.builder()
                    .token(token)
                    .user(userService.convertToDTO(user))
                    .build();
                    
        } catch (Exception e) {
            log.error("Login failed for email: {}", request.getEmail(), e);
            throw new BadCredentialsException("Email hoặc mật khẩu không chính xác");
        }
    }
    
    @Transactional
    public AuthResponse register(RegisterRequest request) {
        // Check if email already exists
        if (userService.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email đã được sử dụng");
        }
        
        // Create new user
        String passwordHash = passwordEncoder.encode(request.getPassword());
        User user = userService.createUser(request.getEmail(), passwordHash, request.getName());
        
        // Generate JWT token
        String token = jwtUtils.generateToken(user);
        
        log.info("New user registered with email: {}", request.getEmail());
        
        return AuthResponse.builder()
                .token(token)
                .user(userService.convertToDTO(user))
                .build();
    }
}
