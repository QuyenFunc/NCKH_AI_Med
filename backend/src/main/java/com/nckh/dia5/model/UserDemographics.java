package com.nckh.dia5.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "user_demographics")
public class UserDemographics extends BaseEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @OneToOne
    @JoinColumn(name = "user_id", referencedColumnName = "id", unique = true)
    private User user;
    
    @Column(name = "birth_year", nullable = false)
    private Integer birthYear;
    
    @Column(name = "birth_month")
    private Integer birthMonth;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "gender", nullable = false)
    private Gender gender;
    
    @Column(name = "height_cm")
    private Integer heightCm;
    
    @Column(name = "weight_kg", precision = 5, scale = 2)
    private BigDecimal weightKg;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "blood_type")
    private BloodType bloodType;
    
    @ManyToOne
    @JoinColumn(name = "province_id")
    private Province province;
    
    @Column(name = "occupation")
    private String occupation;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "education_level")
    private EducationLevel educationLevel;
    
    public enum Gender {
        MALE, FEMALE, OTHER
    }
    
    public enum BloodType {
        A_POSITIVE("A+"), A_NEGATIVE("A-"),
        B_POSITIVE("B+"), B_NEGATIVE("B-"),
        AB_POSITIVE("AB+"), AB_NEGATIVE("AB-"),
        O_POSITIVE("O+"), O_NEGATIVE("O-"),
        UNKNOWN("unknown");
        
        private final String value;
        
        BloodType(String value) {
            this.value = value;
        }
        
        public String getValue() {
            return value;
        }
    }
    
    public enum EducationLevel {
        PRIMARY, SECONDARY, HIGH_SCHOOL, BACHELOR, MASTER, PHD, OTHER
    }
}
