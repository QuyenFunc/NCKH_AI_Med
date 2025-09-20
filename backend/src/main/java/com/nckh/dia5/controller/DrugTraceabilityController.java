package com.nckh.dia5.controller;

import com.nckh.dia5.dto.blockchain.*;
import com.nckh.dia5.dto.common.ApiResponse;
import com.nckh.dia5.service.DrugTraceabilityService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigInteger;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/blockchain/drugs")
@RequiredArgsConstructor
public class DrugTraceabilityController {

    private final DrugTraceabilityService drugTraceabilityService;

    @PostMapping("/batches")
    public ResponseEntity<ApiResponse<DrugBatchDto>> createBatch(
            @Valid @RequestBody CreateBatchRequest request) {
        log.info("Creating new drug batch: {}", request.getDrugName());
        DrugBatchDto batch = drugTraceabilityService.createBatch(request);
        return ResponseEntity.ok(ApiResponse.success(batch, "Tạo lô thuốc thành công"));
    }

    @PostMapping("/shipments")
    public ResponseEntity<ApiResponse<ShipmentDto>> createShipment(
            @Valid @RequestBody CreateShipmentRequest request) {
        log.info("Creating new shipment for batch: {}", request.getBatchId());
        ShipmentDto shipment = drugTraceabilityService.createShipment(request);
        return ResponseEntity.ok(ApiResponse.success(shipment, "Tạo shipment thành công"));
    }

    @PostMapping("/shipments/{shipmentId}/receive")
    public ResponseEntity<ApiResponse<ShipmentDto>> receiveShipment(
            @PathVariable BigInteger shipmentId) {
        log.info("Receiving shipment: {}", shipmentId);
        ShipmentDto shipment = drugTraceabilityService.receiveShipment(shipmentId);
        return ResponseEntity.ok(ApiResponse.success(shipment, "Nhận shipment thành công"));
    }

    @PutMapping("/shipments/status")
    public ResponseEntity<ApiResponse<ShipmentDto>> updateShipmentStatus(
            @Valid @RequestBody UpdateShipmentStatusRequest request) {
        log.info("Updating shipment status: {} -> {}", request.getShipmentId(), request.getNewStatus());
        ShipmentDto shipment = drugTraceabilityService.updateShipmentStatus(request);
        return ResponseEntity.ok(ApiResponse.success(shipment, "Cập nhật trạng thái shipment thành công"));
    }

    @PostMapping("/verify")
    public ResponseEntity<ApiResponse<DrugBatchDto>> verifyDrug(
            @Valid @RequestBody VerifyDrugRequest request) {
        log.info("Verifying drug with QR code: {}", request.getQrCode());
        DrugBatchDto batch = drugTraceabilityService.verifyDrug(request);
        return ResponseEntity.ok(ApiResponse.success(batch, "Xác minh thuốc thành công"));
    }

    @GetMapping("/batches/{batchId}")
    public ResponseEntity<ApiResponse<DrugBatchDto>> getBatch(@PathVariable BigInteger batchId) {
        log.info("Getting batch: {}", batchId);
        DrugBatchDto batch = drugTraceabilityService.getBatch(batchId);
        return ResponseEntity.ok(ApiResponse.success(batch, "Lấy thông tin lô thuốc thành công"));
    }

    @GetMapping("/batches/manufacturer/{manufacturerAddress}")
    public ResponseEntity<ApiResponse<List<DrugBatchDto>>> getBatchesByManufacturer(
            @PathVariable String manufacturerAddress) {
        log.info("Getting batches by manufacturer: {}", manufacturerAddress);
        List<DrugBatchDto> batches = drugTraceabilityService.getBatchesByManufacturer(manufacturerAddress);
        return ResponseEntity.ok(ApiResponse.success(batches, "Lấy danh sách lô thuốc theo nhà sản xuất thành công"));
    }

    @GetMapping("/batches/owner/{ownerAddress}")
    public ResponseEntity<ApiResponse<List<DrugBatchDto>>> getBatchesByOwner(
            @PathVariable String ownerAddress) {
        log.info("Getting batches by owner: {}", ownerAddress);
        List<DrugBatchDto> batches = drugTraceabilityService.getBatchesByOwner(ownerAddress);
        return ResponseEntity.ok(ApiResponse.success(batches, "Lấy danh sách lô thuốc theo chủ sở hữu thành công"));
    }

    @GetMapping("/batches/{batchId}/shipments")
    public ResponseEntity<ApiResponse<List<ShipmentDto>>> getShipmentsByBatch(
            @PathVariable BigInteger batchId) {
        log.info("Getting shipments for batch: {}", batchId);
        List<ShipmentDto> shipments = drugTraceabilityService.getShipmentsByBatch(batchId);
        return ResponseEntity.ok(ApiResponse.success(shipments, "Lấy danh sách shipment theo lô thuốc thành công"));
    }

    @GetMapping("/batches/{batchId}/transactions")
    public ResponseEntity<ApiResponse<List<BlockchainTransactionDto>>> getBatchTransactionHistory(
            @PathVariable BigInteger batchId) {
        log.info("Getting transaction history for batch: {}", batchId);
        List<BlockchainTransactionDto> transactions = drugTraceabilityService.getBatchTransactionHistory(batchId);
        return ResponseEntity.ok(ApiResponse.success(transactions, "Lấy lịch sử giao dịch blockchain thành công"));
    }
}
