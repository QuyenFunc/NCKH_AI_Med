package com.nckh.dia5.controller;

import com.nckh.dia5.dto.common.ApiResponse;
import com.nckh.dia5.dto.pharmacy.PharmacyInventoryDto;
import com.nckh.dia5.model.PharmacyInventory;
import com.nckh.dia5.service.PharmacyInventoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/pharmacy/inventory")
@RequiredArgsConstructor
@Tag(name = "Pharmacy Inventory", description = "APIs quản lý kho hiệu thuốc")
public class PharmacyInventoryController {

    private final PharmacyInventoryService inventoryService;

    @GetMapping("/company/{pharmacyId}")
    @Operation(summary = "Lấy kho hàng theo ID công ty", description = "Lấy tất cả sản phẩm trong kho của hiệu thuốc")
    public ResponseEntity<ApiResponse<List<PharmacyInventory>>> getInventoryByCompanyId(
            @PathVariable Long pharmacyId) {
        log.info("Getting inventory for pharmacy: {}", pharmacyId);
        List<PharmacyInventory> inventory = inventoryService.getInventoryByPharmacyId(pharmacyId);
        return ResponseEntity.ok(ApiResponse.success(inventory, "Lấy danh sách kho thành công"));
    }

    @GetMapping("/wallet/{walletAddress}")
    @Operation(summary = "Lấy kho hàng theo wallet address", description = "Lấy tất cả sản phẩm trong kho theo địa chỉ ví blockchain")
    public ResponseEntity<ApiResponse<List<PharmacyInventoryDto>>> getInventoryByWalletAddress(
            @PathVariable String walletAddress) {
        log.info("Getting inventory for wallet: {}", walletAddress);
        List<PharmacyInventoryDto> inventory = inventoryService.getInventoryDtoByWalletAddress(walletAddress);
        return ResponseEntity.ok(ApiResponse.success(inventory, "Lấy danh sách kho thành công"));
    }

    @GetMapping("/company/{pharmacyId}/low-stock")
    @Operation(summary = "Lấy sản phẩm sắp hết hàng", description = "Lấy danh sách sản phẩm có số lượng <= ngưỡng tối thiểu")
    public ResponseEntity<ApiResponse<List<PharmacyInventory>>> getLowStockItems(
            @PathVariable Long pharmacyId) {
        log.info("Getting low stock items for pharmacy: {}", pharmacyId);
        List<PharmacyInventory> items = inventoryService.getLowStockItems(pharmacyId);
        return ResponseEntity.ok(ApiResponse.success(items, "Lấy danh sách sản phẩm sắp hết hàng thành công"));
    }

    @GetMapping("/company/{pharmacyId}/need-reorder")
    @Operation(summary = "Lấy sản phẩm cần đặt hàng lại", description = "Lấy danh sách sản phẩm cần đặt hàng lại")
    public ResponseEntity<ApiResponse<List<PharmacyInventory>>> getItemsNeedReorder(
            @PathVariable Long pharmacyId) {
        log.info("Getting items need reorder for pharmacy: {}", pharmacyId);
        List<PharmacyInventory> items = inventoryService.getItemsNeedReorder(pharmacyId);
        return ResponseEntity.ok(ApiResponse.success(items, "Lấy danh sách sản phẩm cần đặt hàng thành công"));
    }

    @GetMapping("/company/{pharmacyId}/expiring-soon")
    @Operation(summary = "Lấy sản phẩm sắp hết hạn", description = "Lấy danh sách sản phẩm sắp hết hạn trong 30 ngày")
    public ResponseEntity<ApiResponse<List<PharmacyInventory>>> getExpiringSoonItems(
            @PathVariable Long pharmacyId) {
        log.info("Getting expiring soon items for pharmacy: {}", pharmacyId);
        List<PharmacyInventory> items = inventoryService.getExpiringSoonItems(pharmacyId);
        return ResponseEntity.ok(ApiResponse.success(items, "Lấy danh sách sản phẩm sắp hết hạn thành công"));
    }

    @GetMapping("/company/{pharmacyId}/search")
    @Operation(summary = "Tìm kiếm sản phẩm trong kho", description = "Tìm kiếm sản phẩm theo tên thuốc")
    public ResponseEntity<ApiResponse<List<PharmacyInventory>>> searchByDrugName(
            @PathVariable Long pharmacyId,
            @RequestParam String searchTerm) {
        log.info("Searching inventory for pharmacy: {}, term: {}", pharmacyId, searchTerm);
        List<PharmacyInventory> items = inventoryService.searchByDrugName(pharmacyId, searchTerm);
        return ResponseEntity.ok(ApiResponse.success(items, "Tìm kiếm thành công"));
    }

    @GetMapping("/company/{pharmacyId}/featured")
    @Operation(summary = "Lấy sản phẩm nổi bật", description = "Lấy danh sách sản phẩm được đánh dấu nổi bật")
    public ResponseEntity<ApiResponse<List<PharmacyInventory>>> getFeaturedProducts(
            @PathVariable Long pharmacyId) {
        log.info("Getting featured products for pharmacy: {}", pharmacyId);
        List<PharmacyInventory> items = inventoryService.getFeaturedProducts(pharmacyId);
        return ResponseEntity.ok(ApiResponse.success(items, "Lấy sản phẩm nổi bật thành công"));
    }

    @GetMapping("/company/{pharmacyId}/on-sale")
    @Operation(summary = "Lấy sản phẩm đang khuyến mãi", description = "Lấy danh sách sản phẩm đang khuyến mãi")
    public ResponseEntity<ApiResponse<List<PharmacyInventory>>> getProductsOnSale(
            @PathVariable Long pharmacyId) {
        log.info("Getting products on sale for pharmacy: {}", pharmacyId);
        List<PharmacyInventory> items = inventoryService.getProductsOnSale(pharmacyId);
        return ResponseEntity.ok(ApiResponse.success(items, "Lấy sản phẩm khuyến mãi thành công"));
    }

    @GetMapping("/company/{pharmacyId}/values")
    @Operation(summary = "Lấy thống kê giá trị kho", description = "Lấy tổng giá trị kho (giá vốn và giá bán)")
    public ResponseEntity<ApiResponse<Map<String, Double>>> getInventoryValues(
            @PathVariable Long pharmacyId) {
        log.info("Getting inventory values for pharmacy: {}", pharmacyId);
        Double costValue = inventoryService.getTotalInventoryValue(pharmacyId);
        Double retailValue = inventoryService.getTotalRetailValue(pharmacyId);
        
        Map<String, Double> values = Map.of(
            "costValue", costValue,
            "retailValue", retailValue,
            "potentialProfit", retailValue - costValue
        );
        
        return ResponseEntity.ok(ApiResponse.success(values, "Lấy thống kê giá trị kho thành công"));
    }

    @PostMapping("/company/{pharmacyId}/batch/{batchId}/sale")
    @Operation(summary = "Ghi nhận bán hàng", description = "Ghi nhận việc bán sản phẩm và cập nhật kho")
    public ResponseEntity<ApiResponse<PharmacyInventory>> recordSale(
            @PathVariable Long pharmacyId,
            @PathVariable Long batchId,
            @RequestParam Integer quantity) {
        log.info("Recording sale for pharmacy: {}, batch: {}, quantity: {}", pharmacyId, batchId, quantity);
        PharmacyInventory inventory = inventoryService.recordSale(pharmacyId, batchId, quantity);
        return ResponseEntity.ok(ApiResponse.success(inventory, "Ghi nhận bán hàng thành công"));
    }
}
