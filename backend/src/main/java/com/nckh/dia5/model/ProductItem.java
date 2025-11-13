package com.nckh.dia5.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "product_items")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ProductItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "drug_batch_id", nullable = false)
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private DrugBatch drugBatch;

    @Column(name = "serial_number", nullable = false, unique = true, length = 255)
    private String serialNumber;

    @Column(name = "qr_code", length = 1000)
    private String qrCode;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 50)
    private ProductItemStatus status = ProductItemStatus.CREATED;

    @Column(name = "blockchain_registered", nullable = false)
    private Boolean blockchainRegistered = false;

    @Column(name = "blockchain_redeemed", nullable = false)
    private Boolean blockchainRedeemed = false;

    @Column(name = "redeemed_by_address", length = 42)
    private String redeemedByAddress;

    @Column(name = "redeemed_at")
    private LocalDateTime redeemedAt;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public enum ProductItemStatus {
        CREATED,
        REGISTERED,
        REDEEMED,
        DECOMMISSIONED
    }
}
