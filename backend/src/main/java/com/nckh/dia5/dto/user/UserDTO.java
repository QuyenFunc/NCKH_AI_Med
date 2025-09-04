package com.nckh.dia5.dto.user;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {
    private String id;
    private String email;
    private String name;
    private LocalDateTime lastLoginAt;
    private Boolean isProfileComplete;
    private Boolean isActive;
    private LocalDateTime createdAt;
}
