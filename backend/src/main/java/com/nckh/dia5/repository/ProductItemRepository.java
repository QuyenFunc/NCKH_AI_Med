package com.nckh.dia5.repository;

import com.nckh.dia5.model.DrugBatch;
import com.nckh.dia5.model.ProductItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProductItemRepository extends JpaRepository<ProductItem, Long> {

    Optional<ProductItem> findBySerialNumber(String serialNumber);

    Optional<ProductItem> findByDrugBatchAndSerialNumber(DrugBatch drugBatch, String serialNumber);

    List<ProductItem> findByDrugBatch(DrugBatch drugBatch);

    long countByBlockchainRegisteredTrue();

    long countByStatus(ProductItem.ProductItemStatus status);
}
