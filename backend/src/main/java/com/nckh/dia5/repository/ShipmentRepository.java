package com.nckh.dia5.repository;

import com.nckh.dia5.model.Shipment;
import com.nckh.dia5.model.DrugBatch;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigInteger;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface ShipmentRepository extends JpaRepository<Shipment, Long> {

    Optional<Shipment> findByShipmentId(BigInteger shipmentId);

    List<Shipment> findByDrugBatch(DrugBatch drugBatch);

    List<Shipment> findByFromAddress(String fromAddress);

    List<Shipment> findByToAddress(String toAddress);

    List<Shipment> findByStatus(Shipment.ShipmentStatus status);

    List<Shipment> findByIsSynced(Boolean isSynced);

    @Query("SELECT s FROM Shipment s WHERE s.fromAddress = :address OR s.toAddress = :address")
    List<Shipment> findByInvolvedAddress(@Param("address") String address);

    @Query("SELECT s FROM Shipment s WHERE s.drugBatch.batchId = :batchId")
    List<Shipment> findByBatchId(@Param("batchId") BigInteger batchId);

    @Query("SELECT s FROM Shipment s WHERE s.shipmentTimestamp BETWEEN :startDate AND :endDate")
    List<Shipment> findByShipmentTimestampBetween(@Param("startDate") LocalDateTime startDate, 
                                                  @Param("endDate") LocalDateTime endDate);

    @Query("SELECT s FROM Shipment s WHERE s.fromAddress = :from AND s.toAddress = :to")
    Page<Shipment> findByFromAddressAndToAddress(@Param("from") String fromAddress, 
                                                 @Param("to") String toAddress, 
                                                 Pageable pageable);

    @Query("SELECT COUNT(s) FROM Shipment s WHERE s.fromAddress = :address")
    Long countByFromAddress(@Param("address") String address);

    @Query("SELECT COUNT(s) FROM Shipment s WHERE s.toAddress = :address")
    Long countByToAddress(@Param("address") String address);

    @Query("SELECT s FROM Shipment s WHERE s.status = :status AND s.shipmentTimestamp < :threshold")
    List<Shipment> findStaleShipments(@Param("status") Shipment.ShipmentStatus status, 
                                     @Param("threshold") LocalDateTime threshold);

    @Query("SELECT s FROM Shipment s WHERE s.transactionHash = :hash")
    Optional<Shipment> findByTransactionHash(@Param("hash") String transactionHash);

    @Query("SELECT s FROM Shipment s JOIN s.drugBatch db WHERE db.drugName LIKE %:drugName%")
    List<Shipment> findByDrugName(@Param("drugName") String drugName);
}
