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

    @Value("${pharmaledger.contract.address:0x5FbDB2315678afecb367f032d93F642f64180aa3}")
    private String contractAddress;

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
     */
    @Scheduled(fixedDelay = 30000) // Chạy mỗi 30 giây
    @Async
    public void indexNewEvents() {
        try {
            log.info("🔍 Starting blockchain event indexing...");

            // Lấy block number cao nhất đã index
            BigInteger lastIndexedBlock = eventRepository.findMaxBlockNumber()
                .orElse(BigInteger.ZERO);

            // Lấy block number hiện tại
            BigInteger currentBlock = web3j.ethBlockNumber().send().getBlockNumber();

            if (currentBlock.compareTo(lastIndexedBlock) <= 0) {
                log.debug("No new blocks to index. Current: {}, Last indexed: {}", 
                    currentBlock, lastIndexedBlock);
                return;
            }

            BigInteger fromBlock = lastIndexedBlock.add(BigInteger.ONE);
            BigInteger toBlock = currentBlock;

            log.info("📊 Indexing events from block {} to {}", fromBlock, toBlock);

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
            
            indexBatchIssuedEvents(fromBlock, currentBlock);
            indexShipmentCreatedEvents(fromBlock, currentBlock);
            indexShipmentReceivedEvents(fromBlock, currentBlock);
            
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
            
            return status;
        } catch (Exception e) {
            log.error("❌ Failed to get indexing status: {}", e.getMessage());
            throw new RuntimeException("Failed to get indexing status", e);
        }
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
