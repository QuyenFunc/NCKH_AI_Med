package com.nckh.dia5.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.nckh.dia5.model.BlockchainEvent;
import com.nckh.dia5.repository.BlockchainEventRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.web3j.abi.EventEncoder;
import org.web3j.abi.TypeReference;
import org.web3j.abi.datatypes.Address;
import org.web3j.abi.datatypes.Event;
import org.web3j.abi.datatypes.Utf8String;
import org.web3j.abi.datatypes.generated.Uint256;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.DefaultBlockParameterNumber;
import org.web3j.protocol.core.methods.request.EthFilter;
import org.web3j.protocol.core.methods.response.EthLog;
import org.web3j.protocol.core.methods.response.Log;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Service để index blockchain events
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class BlockchainIndexerService {

    private final Web3j web3j;
    private final BlockchainEventRepository eventRepository;
    private final ObjectMapper objectMapper;

    @Value("${pharmaledger.contract.address:0xc6e7DF5E7b4f2A278906862b61205850344D4e7d}")
    private String contractAddress;

    @Value("${pharmaledger.blockchain.safety-buffer:2}")
    private int safetyBuffer;

    @Value("${blockscout.api.url:http://localhost:3000/api}")
    private String blockscoutApiUrl;

    // Event signatures
    private static final Event BATCH_ISSUED_EVENT = new Event("BatchIssued",
        Arrays.asList(
            new TypeReference<Uint256>(true) {}, // batchId (indexed)
            new TypeReference<Address>(true) {}, // manufacturer (indexed) 
            new TypeReference<Utf8String>() {}, // drugName
            new TypeReference<Uint256>() {}, // quantity
            new TypeReference<Utf8String>() {} // qrCode
        )
    );

    private static final Event SHIPMENT_CREATED_EVENT = new Event("ShipmentCreated",
        Arrays.asList(
            new TypeReference<Uint256>(true) {}, // shipmentId (indexed)
            new TypeReference<Uint256>(true) {}, // batchId (indexed)
            new TypeReference<Address>(true) {}, // from (indexed)
            new TypeReference<Address>() {}, // to
            new TypeReference<Uint256>() {} // quantity
        )
    );

    private static final Event SHIPMENT_RECEIVED_EVENT = new Event("ShipmentReceived",
        Arrays.asList(
            new TypeReference<Uint256>(true) {}, // shipmentId (indexed)
            new TypeReference<Uint256>(true) {}, // batchId (indexed)
            new TypeReference<Address>(true) {} // receiver (indexed)
        )
    );

    /**
     * Index blockchain events từ block cũ nhất chưa được index
     * With Blockscout sync validation
     */
    @Scheduled(fixedDelay = 30000) // Chạy mỗi 30 giây
    @Async
    public void indexNewEvents() {
        try {
            log.info("🔍 Starting blockchain event indexing...");

            // Lấy block number cao nhất đã index
            BigInteger lastIndexedBlock = eventRepository.findMaxBlockNumber()
                .orElse(BigInteger.ZERO);

            // Lấy block number hiện tại từ blockchain
            BigInteger currentBlock = web3j.ethBlockNumber().send().getBlockNumber();
            BigInteger configuredBuffer = getConfiguredBuffer();
            BigInteger safeCurrentBlock = applySafetyBuffer(currentBlock, configuredBuffer);

            // Validate block exists before indexing
            if (!validateBlockExists(safeCurrentBlock)) {
                log.warn("⚠️ Target block {} not yet available on blockchain, skipping indexing", safeCurrentBlock);
                return;
            }

            if (safeCurrentBlock.compareTo(lastIndexedBlock) <= 0) {
                log.debug("No new blocks to index. Safe current: {}, last indexed: {}, buffer: {}",
                    safeCurrentBlock, lastIndexedBlock, configuredBuffer);
                return;
            }

            BigInteger fromBlock = lastIndexedBlock.add(BigInteger.ONE);
            BigInteger toBlock = safeCurrentBlock;

            if (toBlock.compareTo(fromBlock) < 0) {
                log.debug("Safety buffer leaves no range to index (from: {}, to: {}, buffer: {})",
                    fromBlock, toBlock, configuredBuffer);
                return;
            }

            log.info("📊 Indexing events from block {} to {} (current: {}, buffer: {})",
                fromBlock, toBlock, currentBlock, configuredBuffer);
            log.info("   Blockscout should have indexed these blocks by now");

            // Index từng loại event
            indexBatchIssuedEvents(fromBlock, toBlock);
            indexShipmentCreatedEvents(fromBlock, toBlock);
            indexShipmentReceivedEvents(fromBlock, toBlock);

            log.info("✅ Blockchain indexing completed. Processed blocks: {} - {}", 
                fromBlock, toBlock);

        } catch (Exception e) {
            log.error("❌ Failed to index blockchain events: {}", e.getMessage(), e);
        }
    }

    /**
     * Validate that a block exists on the blockchain
     */
    private boolean validateBlockExists(BigInteger blockNumber) {
        try {
            if (blockNumber.compareTo(BigInteger.ZERO) < 0) {
                return false;
            }
            
            org.web3j.protocol.core.methods.response.EthBlock ethBlock = web3j.ethGetBlockByNumber(
                new DefaultBlockParameterNumber(blockNumber), false).send();
            
            boolean exists = ethBlock.getBlock() != null;
            if (!exists) {
                log.warn("Block {} does not exist yet", blockNumber);
            }
            return exists;
            
        } catch (Exception e) {
            log.error("Failed to validate block existence: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Index BatchIssued events
     */
    private void indexBatchIssuedEvents(BigInteger fromBlock, BigInteger toBlock) {
        try {
            String eventSignature = EventEncoder.encode(BATCH_ISSUED_EVENT);
            
            EthFilter filter = new EthFilter(
                new DefaultBlockParameterNumber(fromBlock),
                new DefaultBlockParameterNumber(toBlock),
                contractAddress
            ).addSingleTopic(eventSignature);

            EthLog ethLog = web3j.ethGetLogs(filter).send();
            List<EthLog.LogResult> logs = ethLog.getLogs();

            log.info("📦 Found {} BatchIssued events", logs.size());

            for (EthLog.LogResult logResult : logs) {
                Log eventLog = (Log) logResult.get();
                
                if (!eventRepository.existsByTransactionHashAndLogIndex(
                    eventLog.getTransactionHash(), eventLog.getLogIndex())) {
                    
                    Map<String, Object> eventData = new HashMap<>();
                    eventData.put("drugName", ""); // Parse từ log data
                    eventData.put("quantity", "");
                    eventData.put("qrCode", "");
                    
                    BlockchainEvent event = BlockchainEvent.builder()
                        .eventType("BatchIssued")
                        .contractAddress(contractAddress)
                        .transactionHash(eventLog.getTransactionHash())
                        .blockNumber(eventLog.getBlockNumber())
                        .logIndex(eventLog.getLogIndex())
                        .eventData(objectMapper.writeValueAsString(eventData))
                        .batchId(extractBatchIdFromLog(eventLog))
                        .fromAddress(extractManufacturerFromLog(eventLog))
                        .processed(false)
                        .build();
                    
                    eventRepository.save(event);
                    log.info("💾 Saved BatchIssued event: TX {}", eventLog.getTransactionHash());
                }
            }
        } catch (Exception e) {
            log.error("❌ Failed to index BatchIssued events: {}", e.getMessage());
        }
    }

    /**
     * Index ShipmentCreated events
     */
    private void indexShipmentCreatedEvents(BigInteger fromBlock, BigInteger toBlock) {
        try {
            String eventSignature = EventEncoder.encode(SHIPMENT_CREATED_EVENT);
            
            EthFilter filter = new EthFilter(
                new DefaultBlockParameterNumber(fromBlock),
                new DefaultBlockParameterNumber(toBlock),
                contractAddress
            ).addSingleTopic(eventSignature);

            EthLog ethLog = web3j.ethGetLogs(filter).send();
            List<EthLog.LogResult> logs = ethLog.getLogs();

            log.info("🚚 Found {} ShipmentCreated events", logs.size());

            for (EthLog.LogResult logResult : logs) {
                Log eventLog = (Log) logResult.get();
                
                if (!eventRepository.existsByTransactionHashAndLogIndex(
                    eventLog.getTransactionHash(), eventLog.getLogIndex())) {
                    
                    Map<String, Object> eventData = new HashMap<>();
                    eventData.put("quantity", "");
                    
                    BlockchainEvent event = BlockchainEvent.builder()
                        .eventType("ShipmentCreated")
                        .contractAddress(contractAddress)
                        .transactionHash(eventLog.getTransactionHash())
                        .blockNumber(eventLog.getBlockNumber())
                        .logIndex(eventLog.getLogIndex())
                        .eventData(objectMapper.writeValueAsString(eventData))
                        .batchId(extractBatchIdFromLog(eventLog))
                        .shipmentId(extractShipmentIdFromLog(eventLog))
                        .fromAddress(extractFromAddressFromLog(eventLog))
                        .toAddress(extractToAddressFromLog(eventLog))
                        .processed(false)
                        .build();
                    
                    eventRepository.save(event);
                    log.info("💾 Saved ShipmentCreated event: TX {}", eventLog.getTransactionHash());
                }
            }
        } catch (Exception e) {
            log.error("❌ Failed to index ShipmentCreated events: {}", e.getMessage());
        }
    }

    /**
     * Index ShipmentReceived events
     */
    private void indexShipmentReceivedEvents(BigInteger fromBlock, BigInteger toBlock) {
        try {
            String eventSignature = EventEncoder.encode(SHIPMENT_RECEIVED_EVENT);
            
            EthFilter filter = new EthFilter(
                new DefaultBlockParameterNumber(fromBlock),
                new DefaultBlockParameterNumber(toBlock),
                contractAddress
            ).addSingleTopic(eventSignature);

            EthLog ethLog = web3j.ethGetLogs(filter).send();
            List<EthLog.LogResult> logs = ethLog.getLogs();

            log.info("📦 Found {} ShipmentReceived events", logs.size());

            for (EthLog.LogResult logResult : logs) {
                Log eventLog = (Log) logResult.get();
                
                if (!eventRepository.existsByTransactionHashAndLogIndex(
                    eventLog.getTransactionHash(), eventLog.getLogIndex())) {
                    
                    BlockchainEvent event = BlockchainEvent.builder()
                        .eventType("ShipmentReceived")
                        .contractAddress(contractAddress)
                        .transactionHash(eventLog.getTransactionHash())
                        .blockNumber(eventLog.getBlockNumber())
                        .logIndex(eventLog.getLogIndex())
                        .eventData("{}")
                        .batchId(extractBatchIdFromLog(eventLog))
                        .shipmentId(extractShipmentIdFromLog(eventLog))
                        .toAddress(extractReceiverFromLog(eventLog))
                        .processed(false)
                        .build();
                    
                    eventRepository.save(event);
                    log.info("💾 Saved ShipmentReceived event: TX {}", eventLog.getTransactionHash());
                }
            }
        } catch (Exception e) {
            log.error("❌ Failed to index ShipmentReceived events: {}", e.getMessage());
        }
    }

    /**
     * Manual indexing từ block cụ thể
     */
    public void indexFromBlock(BigInteger fromBlock) {
        try {
            log.info("🔄 Manual indexing from block: {}", fromBlock);
            
            BigInteger currentBlock = web3j.ethBlockNumber().send().getBlockNumber();
            BigInteger configuredBuffer = getConfiguredBuffer();
            BigInteger safeCurrentBlock = applySafetyBuffer(currentBlock, configuredBuffer);
            
            if (safeCurrentBlock.compareTo(fromBlock) < 0) {
                log.warn("Current safe block {} is less than from block {} (buffer: {}). Skipping indexing.",
                    safeCurrentBlock, fromBlock, configuredBuffer);
                return;
            }
            
            log.info("📊 Manual indexing from {} to {} (current: {}, buffer: {})", 
                fromBlock, safeCurrentBlock, currentBlock, configuredBuffer);
            
            indexBatchIssuedEvents(fromBlock, safeCurrentBlock);
            indexShipmentCreatedEvents(fromBlock, safeCurrentBlock);
            indexShipmentReceivedEvents(fromBlock, safeCurrentBlock);
            
            log.info("✅ Manual indexing completed");
        } catch (Exception e) {
            log.error("❌ Manual indexing failed: {}", e.getMessage());
            throw new RuntimeException("Manual indexing failed", e);
        }
    }

    /**
     * Get indexing status
     */
    public Map<String, Object> getIndexingStatus() {
        try {
            BigInteger currentBlock = web3j.ethBlockNumber().send().getBlockNumber();
            BigInteger lastIndexedBlock = eventRepository.findMaxBlockNumber()
                .orElse(BigInteger.ZERO);
            long unprocessedEvents = eventRepository.countByProcessedFalse();
            
            Map<String, Object> status = new HashMap<>();
            status.put("currentBlock", currentBlock);
            status.put("lastIndexedBlock", lastIndexedBlock);
            status.put("blocksBehind", currentBlock.subtract(lastIndexedBlock));
            status.put("unprocessedEvents", unprocessedEvents);
            status.put("isUpToDate", currentBlock.equals(lastIndexedBlock));
            status.put("safetyBuffer", getConfiguredBuffer());
            
            return status;
        } catch (Exception e) {
            log.error("❌ Failed to get indexing status: {}", e.getMessage());
            throw new RuntimeException("Failed to get indexing status", e);
        }
    }

    private BigInteger getConfiguredBuffer() {
        return BigInteger.valueOf(Math.max(0, safetyBuffer));
    }

    private BigInteger applySafetyBuffer(BigInteger currentBlock, BigInteger buffer) {
        BigInteger safeCurrentBlock = currentBlock.subtract(buffer);
        if (safeCurrentBlock.compareTo(BigInteger.ZERO) < 0) {
            return BigInteger.ZERO;
        }
        return safeCurrentBlock;
    }

    // Helper methods để parse log data
    private BigInteger extractBatchIdFromLog(Log log) {
        // TODO: Implement proper log parsing
        return BigInteger.ZERO;
    }

    private BigInteger extractShipmentIdFromLog(Log log) {
        // TODO: Implement proper log parsing
        return BigInteger.ZERO;
    }

    private String extractManufacturerFromLog(Log log) {
        // TODO: Implement proper log parsing
        return "";
    }

    private String extractFromAddressFromLog(Log log) {
        // TODO: Implement proper log parsing
        return "";
    }

    private String extractToAddressFromLog(Log log) {
        // TODO: Implement proper log parsing
        return "";
    }

    private String extractReceiverFromLog(Log log) {
        // TODO: Implement proper log parsing
        return "";
    }
}
