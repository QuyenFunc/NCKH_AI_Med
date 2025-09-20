package com.nckh.dia5.service;

import com.nckh.dia5.config.BlockchainConfig;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.web3j.abi.EventEncoder;
import org.web3j.abi.FunctionEncoder;
import org.web3j.abi.FunctionReturnDecoder;
import org.web3j.abi.TypeReference;
import org.web3j.abi.datatypes.*;
import org.web3j.abi.datatypes.generated.Uint256;
import org.web3j.crypto.Credentials;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.DefaultBlockParameterName;
import org.web3j.protocol.core.methods.request.EthFilter;
import org.web3j.protocol.core.methods.request.Transaction;
import org.web3j.protocol.core.methods.response.*;
import org.web3j.tx.gas.ContractGasProvider;
import org.web3j.tx.RawTransactionManager;
import org.web3j.tx.TransactionManager;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

@Slf4j
@Service
@RequiredArgsConstructor
public class BlockchainService {

    private final Web3j web3j;
    private final Credentials credentials;
    private final ContractGasProvider gasProvider;
    private final BlockchainConfig blockchainConfig;

    // Smart contract function signatures
    private static final String ISSUE_BATCH_FUNCTION = "issueBatch";
    private static final String CREATE_SHIPMENT_FUNCTION = "createShipment";
    private static final String RECEIVE_SHIPMENT_FUNCTION = "receiveShipment";
    private static final String UPDATE_BATCH_STATUS_FUNCTION = "updateBatchStatus";
    private static final String VERIFY_OWNERSHIP_FUNCTION = "verifyOwnership";

    // Event signatures
    private static final String BATCH_ISSUED_EVENT = "BatchIssued(uint256,address,string,uint256,string)";
    private static final String SHIPMENT_CREATED_EVENT = "ShipmentCreated(uint256,uint256,address,address,uint256)";
    private static final String SHIPMENT_RECEIVED_EVENT = "ShipmentReceived(uint256,uint256,address)";
    private static final String BATCH_STATUS_UPDATED_EVENT = "BatchStatusUpdated(uint256,uint8)";

    /**
     * Issue a new drug batch on the blockchain
     */
    public CompletableFuture<TransactionReceipt> issueBatch(
            String drugName,
            String manufacturer,
            String batchNumber,
            BigInteger quantity,
            BigInteger expiryTimestamp,
            String storageConditions) {

        return CompletableFuture.supplyAsync(() -> {
            try {
                if (credentials == null) {
                    throw new IllegalStateException("Blockchain credentials not available");
                }

                log.info("Issuing batch on blockchain: drugName={}, manufacturer={}, batchNumber={}, quantity={}", 
                         drugName, manufacturer, batchNumber, quantity);

                // Prepare function parameters
                List<Type> inputParameters = Arrays.asList(
                    new Utf8String(drugName),
                    new Utf8String(manufacturer),
                    new Utf8String(batchNumber),
                    new Uint256(quantity),
                    new Uint256(expiryTimestamp),
                    new Utf8String(storageConditions)
                );

                Function function = new Function(
                    ISSUE_BATCH_FUNCTION,
                    inputParameters,
                    Arrays.asList(new TypeReference<Uint256>() {})
                );

                TransactionReceipt receipt = executeTransaction(function);
                log.info("Batch issued successfully. Transaction hash: {}", receipt.getTransactionHash());
                return receipt;

            } catch (Exception e) {
                log.error("Failed to issue batch on blockchain", e);
                throw new RuntimeException("Failed to issue batch on blockchain", e);
            }
        });
    }

    /**
     * Create a shipment on the blockchain
     */
    public CompletableFuture<TransactionReceipt> createShipment(
            BigInteger batchId,
            String toAddress,
            BigInteger quantity) {

        return CompletableFuture.supplyAsync(() -> {
            try {
                if (credentials == null) {
                    throw new IllegalStateException("Blockchain credentials not available");
                }

                log.info("Creating shipment on blockchain: batchId={}, toAddress={}, quantity={}", 
                         batchId, toAddress, quantity);

                List<Type> inputParameters = Arrays.asList(
                    new Uint256(batchId),
                    new Address(toAddress),
                    new Uint256(quantity)
                );

                Function function = new Function(
                    CREATE_SHIPMENT_FUNCTION,
                    inputParameters,
                    Arrays.asList(new TypeReference<Uint256>() {})
                );

                TransactionReceipt receipt = executeTransaction(function);
                log.info("Shipment created successfully. Transaction hash: {}", receipt.getTransactionHash());
                return receipt;

            } catch (Exception e) {
                log.error("Failed to create shipment on blockchain", e);
                throw new RuntimeException("Failed to create shipment on blockchain", e);
            }
        });
    }

    /**
     * Receive a shipment on the blockchain
     */
    public CompletableFuture<TransactionReceipt> receiveShipment(BigInteger shipmentId) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                if (credentials == null) {
                    throw new IllegalStateException("Blockchain credentials not available");
                }

                log.info("Receiving shipment on blockchain: shipmentId={}", shipmentId);

                List<Type> inputParameters = Arrays.asList(new Uint256(shipmentId));

                Function function = new Function(
                    RECEIVE_SHIPMENT_FUNCTION,
                    inputParameters,
                    Arrays.asList()
                );

                TransactionReceipt receipt = executeTransaction(function);
                log.info("Shipment received successfully. Transaction hash: {}", receipt.getTransactionHash());
                return receipt;

            } catch (Exception e) {
                log.error("Failed to receive shipment on blockchain", e);
                throw new RuntimeException("Failed to receive shipment on blockchain", e);
            }
        });
    }

    /**
     * Update batch status on the blockchain
     */
    public CompletableFuture<TransactionReceipt> updateBatchStatus(BigInteger batchId, BigInteger newStatus) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                if (credentials == null) {
                    throw new IllegalStateException("Blockchain credentials not available");
                }

                log.info("Updating batch status on blockchain: batchId={}, newStatus={}", batchId, newStatus);

                List<Type> inputParameters = Arrays.asList(
                    new Uint256(batchId),
                    new Uint256(newStatus)
                );

                Function function = new Function(
                    UPDATE_BATCH_STATUS_FUNCTION,
                    inputParameters,
                    Arrays.asList()
                );

                TransactionReceipt receipt = executeTransaction(function);
                log.info("Batch status updated successfully. Transaction hash: {}", receipt.getTransactionHash());
                return receipt;

            } catch (Exception e) {
                log.error("Failed to update batch status on blockchain", e);
                throw new RuntimeException("Failed to update batch status on blockchain", e);
            }
        });
    }

    /**
     * Verify ownership of a batch
     */
    public CompletableFuture<Boolean> verifyOwnership(BigInteger batchId, String ownerAddress) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                log.info("Verifying ownership on blockchain: batchId={}, ownerAddress={}", batchId, ownerAddress);

                List<Type> inputParameters = Arrays.asList(
                    new Uint256(batchId),
                    new Address(ownerAddress)
                );

                Function function = new Function(
                    VERIFY_OWNERSHIP_FUNCTION,
                    inputParameters,
                    Arrays.asList(new TypeReference<Bool>() {})
                );

                List<Type> result = executeCall(function);
                boolean isOwner = (Boolean) result.get(0).getValue();
                
                log.info("Ownership verification result: batchId={}, ownerAddress={}, isOwner={}", 
                         batchId, ownerAddress, isOwner);
                return isOwner;

            } catch (Exception e) {
                log.error("Failed to verify ownership on blockchain", e);
                throw new RuntimeException("Failed to verify ownership on blockchain", e);
            }
        });
    }

    /**
     * Get transaction receipt by hash
     */
    public Optional<TransactionReceipt> getTransactionReceipt(String transactionHash) {
        try {
            EthGetTransactionReceipt response = web3j.ethGetTransactionReceipt(transactionHash).send();
            return response.getTransactionReceipt();
        } catch (Exception e) {
            log.error("Failed to get transaction receipt for hash: {}", transactionHash, e);
            return Optional.empty();
        }
    }

    /**
     * Get the latest block number
     */
    public BigInteger getLatestBlockNumber() {
        try {
            EthBlockNumber response = web3j.ethBlockNumber().send();
            return response.getBlockNumber();
        } catch (Exception e) {
            log.error("Failed to get latest block number", e);
            throw new RuntimeException("Failed to get latest block number", e);
        }
    }

    /**
     * Check if a transaction is successful
     */
    public boolean isTransactionSuccessful(String transactionHash) {
        return getTransactionReceipt(transactionHash)
                .map(receipt -> "0x1".equals(receipt.getStatus()))
                .orElse(false);
    }

    /**
     * Execute a transaction on the blockchain
     */
    private TransactionReceipt executeTransaction(Function function) throws Exception {
        String contractAddress = blockchainConfig.getContractAddress();
        if (contractAddress == null || contractAddress.isEmpty()) {
            throw new IllegalStateException("Contract address not configured");
        }

        String encodedFunction = FunctionEncoder.encode(function);
        TransactionManager transactionManager = new RawTransactionManager(web3j, credentials, blockchainConfig.getChainId());
        
        EthSendTransaction transactionResponse = transactionManager.sendTransaction(
                gasProvider.getGasPrice(),
                gasProvider.getGasLimit(),
                contractAddress,
                encodedFunction,
                BigInteger.ZERO
        );

        if (transactionResponse.hasError()) {
            throw new RuntimeException("Transaction failed: " + transactionResponse.getError().getMessage());
        }

        String transactionHash = transactionResponse.getTransactionHash();
        
        // Wait for transaction receipt
        return web3j.ethGetTransactionReceipt(transactionHash).send().getTransactionReceipt().orElse(null);
    }

    /**
     * Execute a call (read-only) on the blockchain
     */
    private List<Type> executeCall(Function function) throws Exception {
        String contractAddress = blockchainConfig.getContractAddress();
        if (contractAddress == null || contractAddress.isEmpty()) {
            throw new IllegalStateException("Contract address not configured");
        }

        String encodedFunction = FunctionEncoder.encode(function);
        EthCall response = web3j.ethCall(
                Transaction.createEthCallTransaction(credentials.getAddress(), contractAddress, encodedFunction),
                DefaultBlockParameterName.LATEST
        ).send();

        return FunctionReturnDecoder.decode(response.getValue(), function.getOutputParameters());
    }

    /**
     * Get events from the blockchain
     */
    public List<EthLog.LogResult> getContractEvents(String eventSignature, BigInteger fromBlock, BigInteger toBlock) {
        try {
            String contractAddress = blockchainConfig.getContractAddress();
            if (contractAddress == null || contractAddress.isEmpty()) {
                throw new IllegalStateException("Contract address not configured");
            }

            EthFilter filter = new EthFilter(
                    org.web3j.protocol.core.DefaultBlockParameter.valueOf(fromBlock),
                    org.web3j.protocol.core.DefaultBlockParameter.valueOf(toBlock),
                    contractAddress
            );

            // Simplified event filtering - just use the basic filter for now
            EthLog response = web3j.ethGetLogs(filter).send();
            return response.getLogs();

        } catch (Exception e) {
            log.error("Failed to get contract events", e);
            throw new RuntimeException("Failed to get contract events", e);
        }
    }
}