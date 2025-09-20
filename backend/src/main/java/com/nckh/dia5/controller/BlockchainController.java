package com.nckh.dia5.controller;

import com.nckh.dia5.dto.common.ApiResponse;
import com.nckh.dia5.service.BlockchainService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.web3j.protocol.core.methods.response.TransactionReceipt;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Slf4j
@RestController
@RequestMapping("/api/blockchain")
@RequiredArgsConstructor
public class BlockchainController {

    private final BlockchainService blockchainService;

    @GetMapping("/status")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getBlockchainStatus() {
        try {
            BigInteger latestBlock = blockchainService.getLatestBlockNumber();
            
            Map<String, Object> status = new HashMap<>();
            status.put("connected", true);
            status.put("latestBlock", latestBlock);
            status.put("timestamp", System.currentTimeMillis());
            
            return ResponseEntity.ok(ApiResponse.success(status, "Kết nối blockchain thành công"));
        } catch (Exception e) {
            log.error("Failed to get blockchain status", e);
            Map<String, Object> status = new HashMap<>();
            status.put("connected", false);
            status.put("error", e.getMessage());
            status.put("timestamp", System.currentTimeMillis());
            
            return ResponseEntity.ok(ApiResponse.success(status, "Lỗi kết nối blockchain"));
        }
    }

    @GetMapping("/transactions/{transactionHash}")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getTransactionReceipt(
            @PathVariable String transactionHash) {
        try {
            Optional<TransactionReceipt> receiptOpt = blockchainService.getTransactionReceipt(transactionHash);
            
            if (receiptOpt.isPresent()) {
                TransactionReceipt receipt = receiptOpt.get();
                Map<String, Object> result = new HashMap<>();
                result.put("transactionHash", receipt.getTransactionHash());
                result.put("blockNumber", receipt.getBlockNumber());
                result.put("from", receipt.getFrom());
                result.put("to", receipt.getTo());
                result.put("gasUsed", receipt.getGasUsed());
                result.put("status", receipt.getStatus());
                result.put("successful", "0x1".equals(receipt.getStatus()));
                
                return ResponseEntity.ok(ApiResponse.success(result, "Lấy thông tin giao dịch thành công"));
            } else {
                return ResponseEntity.ok(ApiResponse.success(null, "Không tìm thấy giao dịch"));
            }
        } catch (Exception e) {
            log.error("Failed to get transaction receipt", e);
            return ResponseEntity.ok(ApiResponse.error("Lỗi khi lấy thông tin giao dịch: " + e.getMessage()));
        }
    }

    @GetMapping("/transactions/{transactionHash}/status")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getTransactionStatus(
            @PathVariable String transactionHash) {
        try {
            boolean isSuccessful = blockchainService.isTransactionSuccessful(transactionHash);
            
            Map<String, Object> result = new HashMap<>();
            result.put("transactionHash", transactionHash);
            result.put("successful", isSuccessful);
            result.put("status", isSuccessful ? "SUCCESS" : "FAILED");
            
            return ResponseEntity.ok(ApiResponse.success(result, "Lấy trạng thái giao dịch thành công"));
        } catch (Exception e) {
            log.error("Failed to get transaction status", e);
            return ResponseEntity.ok(ApiResponse.error("Lỗi khi lấy trạng thái giao dịch: " + e.getMessage()));
        }
    }

    @PostMapping("/verify-ownership")
    public ResponseEntity<ApiResponse<Map<String, Object>>> verifyOwnership(
            @RequestParam BigInteger batchId,
            @RequestParam String ownerAddress) {
        try {
            boolean isOwner = blockchainService.verifyOwnership(batchId, ownerAddress).get();
            
            Map<String, Object> result = new HashMap<>();
            result.put("batchId", batchId);
            result.put("ownerAddress", ownerAddress);
            result.put("isOwner", isOwner);
            result.put("verified", isOwner);
            
            return ResponseEntity.ok(ApiResponse.success(result, "Xác minh quyền sở hữu thành công"));
        } catch (Exception e) {
            log.error("Failed to verify ownership", e);
            return ResponseEntity.ok(ApiResponse.error("Lỗi khi xác minh quyền sở hữu: " + e.getMessage()));
        }
    }

    @GetMapping("/blocks/latest")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getLatestBlock() {
        try {
            BigInteger latestBlock = blockchainService.getLatestBlockNumber();
            
            Map<String, Object> result = new HashMap<>();
            result.put("blockNumber", latestBlock);
            result.put("timestamp", System.currentTimeMillis());
            
            return ResponseEntity.ok(ApiResponse.success(result, "Lấy thông tin block mới nhất thành công"));
        } catch (Exception e) {
            log.error("Failed to get latest block", e);
            return ResponseEntity.ok(ApiResponse.error("Lỗi khi lấy thông tin block: " + e.getMessage()));
        }
    }
}