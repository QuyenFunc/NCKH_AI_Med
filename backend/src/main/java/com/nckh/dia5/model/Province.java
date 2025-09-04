package com.nckh.dia5.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "provinces")
public class Province extends BaseEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "name", nullable = false, unique = true, length = 100)
    private String name;
    
    @Column(name = "code", length = 10)
    private String code;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "region")
    private Region region;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "climate")
    private Climate climate;
    
    @Column(name = "endemic_diseases", columnDefinition = "TEXT")
    private String endemicDiseases; // JSON array
    
    public enum Region {
        NORTH, CENTRAL, SOUTH
    }
    
    public enum Climate {
        TROPICAL, SUBTROPICAL, TEMPERATE
    }
}
