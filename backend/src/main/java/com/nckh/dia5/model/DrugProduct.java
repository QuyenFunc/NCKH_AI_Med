package com.nckh.dia5.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "drug_products")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
public class DrugProduct {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @NotNull
    @Size(max = 255)
    @Column(name = "name", nullable = false)
    private String name;

    @Size(max = 255)
    @Column(name = "active_ingredient")
    private String activeIngredient;

    @Size(max = 100)
    @Column(name = "dosage")
    private String dosage;

    @Size(max = 50)
    @Column(name = "unit")
    private String unit;

    @Size(max = 100)
    @Column(name = "category")
    private String category;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Size(max = 500)
    @Column(name = "storage_conditions")
    private String storageConditions;

    @Size(max = 100)
    @Column(name = "shelf_life")
    private String shelfLife;

    @Size(max = 50)
    @Column(name = "status")
    private String status = "active";

    // Ownership: which manufacturer owns this product
    @Column(name = "manufacturer_id")
    private Long manufacturerId;

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}


