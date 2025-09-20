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

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "shipments")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
public class Shipment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @NotNull
    @Column(name = "shipment_id", nullable = false, unique = true)
    private BigInteger shipmentId;

    @NotNull
    @Size(max = 42)
    @Column(name = "from_address", nullable = false, length = 42)
    private String fromAddress;

    @NotNull
    @Size(max = 42)
    @Column(name = "to_address", nullable = false, length = 42)
    private String toAddress;

    @NotNull
    @Column(name = "quantity", nullable = false)
    private Long quantity;

    @NotNull
    @Column(name = "shipment_timestamp", nullable = false)
    private LocalDateTime shipmentTimestamp;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    private ShipmentStatus status = ShipmentStatus.PENDING;

    @Size(max = 1000)
    @Column(name = "tracking_info")
    private String trackingInfo;

    @Size(max = 66)
    @Column(name = "transaction_hash", length = 66)
    private String transactionHash;

    @Column(name = "block_number")
    private BigInteger blockNumber;

    @Column(name = "is_synced", nullable = false)
    private Boolean isSynced = false;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // Many-to-one relationship with drug batch
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "batch_id", referencedColumnName = "id")
    private DrugBatch drugBatch;

    // One-to-many relationship with blockchain transactions
    @OneToMany(mappedBy = "shipment", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<BlockchainTransaction> transactions;

    public enum ShipmentStatus {
        PENDING,
        IN_TRANSIT,
        DELIVERED,
        CANCELED
    }
}
