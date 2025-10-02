package com.nckh.dia5.controller;

import com.nckh.dia5.dto.common.ApiResponse;
import com.nckh.dia5.model.DrugProduct;
import com.nckh.dia5.model.ManufacturerUser;
import com.nckh.dia5.model.PharmaCompany;
import com.nckh.dia5.repository.DrugProductRepository;
import com.nckh.dia5.repository.PharmaCompanyRepository;
import com.nckh.dia5.service.ManufacturerAuthService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class DrugProductController {

    private final DrugProductRepository drugProductRepository;
    private final PharmaCompanyRepository pharmaCompanyRepository;
    private final ManufacturerAuthService manufacturerAuthService;

    @GetMapping
    public ResponseEntity<ApiResponse<List<DrugProduct>>> getAll() {
        ManufacturerUser current = manufacturerAuthService.getCurrentUser();
        if (current == null) {
            return ResponseEntity.status(401).body(ApiResponse.error("Chưa đăng nhập", 401));
        }
        
        log.info("Current user: {} (Company: {}, ID: {})", current.getName(), current.getCompanyName(), current.getId());
        
        // First try to find PharmaCompany by manufacturerUserId
        PharmaCompany pharmaCompany = pharmaCompanyRepository.findByManufacturerUserId(current.getId()).orElse(null);
        Long manufacturerId = null;
        
        if (pharmaCompany != null) {
            manufacturerId = pharmaCompany.getId();
            log.info("Found PharmaCompany by userId: {} with ID: {}", pharmaCompany.getName(), manufacturerId);
        } else {
            // Fallback: try to find by company name match
            List<PharmaCompany> companies = pharmaCompanyRepository.findAll();
            for (PharmaCompany company : companies) {
                // Match by company name (case-insensitive, partial match)
                if (current.getCompanyName() != null && 
                    (company.getName().toLowerCase().contains(current.getCompanyName().toLowerCase()) ||
                     current.getCompanyName().toLowerCase().contains(company.getName().toLowerCase()))) {
                    manufacturerId = company.getId();
                    log.info("Matched by name: '{}' matches '{}' with ID: {}", 
                             current.getCompanyName(), company.getName(), manufacturerId);
                    
                    // Update the PharmaCompany to link with this user
                    company.setManufacturerUserId(current.getId());
                    pharmaCompanyRepository.save(company);
                    log.info("Linked PharmaCompany {} to user {}", company.getName(), current.getId());
                    break;
                }
            }
        }
        
        List<DrugProduct> products;
        if (manufacturerId != null) {
            products = drugProductRepository.findAllByManufacturerId(manufacturerId);
            log.info("Found {} products for manufacturer ID: {}", products.size(), manufacturerId);
        } else {
            // If no match found, show all products as fallback
            products = drugProductRepository.findAll();
            log.info("No manufacturer match found for '{}', showing all {} products", 
                     current.getCompanyName(), products.size());
        }
        
        return ResponseEntity.ok(ApiResponse.success(products, "Lấy danh sách sản phẩm thành công"));
    }

    @PostMapping
    public ResponseEntity<ApiResponse<DrugProduct>> create(@RequestBody DrugProduct product) {
        try {
            log.info("Creating product: {}", product.getName());
            
            ManufacturerUser current = manufacturerAuthService.getCurrentUser();
            if (current == null) {
                log.warn("Unauthorized product creation attempt");
                return ResponseEntity.status(401).body(ApiResponse.error("Chưa đăng nhập", 401));
            }
            
            log.info("Current manufacturer: {} ({})", current.getName(), current.getId());
            
            // Validate required fields
            if (product.getName() == null || product.getName().trim().isEmpty()) {
                return ResponseEntity.badRequest().body(ApiResponse.error("Tên sản phẩm là bắt buộc", 400));
            }
            
            // Ensure PharmaCompany exists for this manufacturer
            Long manufacturerId = ensurePharmaCompanyExists(current);
            product.setManufacturerId(manufacturerId);
            DrugProduct saved = drugProductRepository.save(product);
            
            log.info("Product created successfully: {} with ID: {}", saved.getName(), saved.getId());
            return ResponseEntity.ok(ApiResponse.success(saved, "Tạo sản phẩm thành công"));
            
        } catch (Exception e) {
            log.error("Error creating product: ", e);
            return ResponseEntity.status(500).body(ApiResponse.error("Lỗi server: " + e.getMessage(), 500));
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<DrugProduct>> update(@PathVariable Long id, @RequestBody DrugProduct product) {
        ManufacturerUser current = manufacturerAuthService.getCurrentUser();
        if (current == null) {
            return ResponseEntity.status(401).body(ApiResponse.error("Chưa đăng nhập", 401));
        }
        return drugProductRepository.findByIdAndManufacturerId(id, convertUserIdToManufacturerId(current.getId()))
                .map(existing -> {
                    existing.setName(product.getName());
                    existing.setActiveIngredient(product.getActiveIngredient());
                    existing.setDosage(product.getDosage());
                    existing.setUnit(product.getUnit());
                    existing.setCategory(product.getCategory());
                    existing.setDescription(product.getDescription());
                    existing.setStorageConditions(product.getStorageConditions());
                    existing.setShelfLife(product.getShelfLife());
                    existing.setStatus(product.getStatus());
                    DrugProduct updated = drugProductRepository.save(existing);
                    return ResponseEntity.ok(ApiResponse.success(updated, "Cập nhật sản phẩm thành công"));
                })
                .orElseGet(() -> ResponseEntity.status(404).body(ApiResponse.error("Không tìm thấy sản phẩm", 404)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<String>> delete(@PathVariable Long id) {
        ManufacturerUser current = manufacturerAuthService.getCurrentUser();
        if (current == null) {
            return ResponseEntity.status(401).body(ApiResponse.error("Chưa đăng nhập", 401));
        }
        return drugProductRepository.findByIdAndManufacturerId(id, convertUserIdToManufacturerId(current.getId()))
                .map(existing -> {
                    drugProductRepository.delete(existing);
                    return ResponseEntity.ok(ApiResponse.success("", "Xóa sản phẩm thành công"));
                })
                .orElseGet(() -> ResponseEntity.status(404).body(ApiResponse.error("Không tìm thấy sản phẩm", 404)));
    }

    @GetMapping("/debug/all")
    public ResponseEntity<ApiResponse<Object>> debugAll() {
        java.util.Map<String, Object> debugInfo = new java.util.HashMap<>();
        
        // Check all companies
        List<PharmaCompany> allCompanies = pharmaCompanyRepository.findAll();
        debugInfo.put("allCompanies", allCompanies);
        
        // Check all products
        List<DrugProduct> allProducts = drugProductRepository.findAll();
        debugInfo.put("allProducts", allProducts);
        
        return ResponseEntity.ok(ApiResponse.success(debugInfo, "Debug info"));
    }
    
    /**
     * Convert ManufacturerUser.id (String UUID) to Long manufacturerId
     * Uses hashCode to generate a consistent Long value
     */
    private Long convertUserIdToManufacturerId(String userId) {
        if (userId == null) return null;
        // Use hashCode to convert UUID string to Long
        // This ensures same UUID always maps to same Long
        return Math.abs((long) userId.hashCode());
    }

    /**
     * Ensure PharmaCompany record exists for the manufacturer user
     * Creates one if it doesn't exist
     */
    private Long ensurePharmaCompanyExists(ManufacturerUser user) {
        Long manufacturerId = convertUserIdToManufacturerId(user.getId());
        
        // Check if PharmaCompany already exists
        if (!pharmaCompanyRepository.existsById(manufacturerId)) {
            // Create new PharmaCompany record
            PharmaCompany pharmaCompany = new PharmaCompany();
            pharmaCompany.setId(manufacturerId);
            pharmaCompany.setName(user.getCompanyName() != null ? user.getCompanyName() : user.getName());
            pharmaCompany.setCompanyType(PharmaCompany.CompanyType.MANUFACTURER); // Required field
            pharmaCompany.setAddress(user.getCompanyAddress());
            pharmaCompany.setEmail(user.getEmail());
            pharmaCompany.setLicenseNumber(user.getLicenseNumber());
            pharmaCompany.setWalletAddress(user.getWalletAddress());
            pharmaCompany.setManufacturerUserId(user.getId());
            pharmaCompany.setStatus("ACTIVE");
            
            pharmaCompanyRepository.save(pharmaCompany);
            log.info("Created PharmaCompany record for manufacturer: {} with ID: {}", user.getName(), manufacturerId);
        }
        
        return manufacturerId;
    }
}


