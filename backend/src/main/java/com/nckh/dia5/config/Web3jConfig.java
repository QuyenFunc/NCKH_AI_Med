package com.nckh.dia5.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.web3j.crypto.Credentials;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.http.HttpService;
import org.web3j.tx.gas.DefaultGasProvider;
import org.web3j.tx.gas.StaticGasProvider;

import java.math.BigInteger;

/**
 * Configuration class cho Web3j blockchain integration
 */
@Slf4j
@Configuration
public class Web3jConfig {

    @Value("${blockchain.network.url}")
    private String networkUrl;

    @Value("${blockchain.wallet.private-key}")
    private String privateKey;

    @Value("${blockchain.gas.price}")
    private long gasPrice;

    @Value("${blockchain.gas.limit}")
    private long gasLimit;

    /**
     * Web3j instance để kết nối blockchain
     */
    @Bean
    public Web3j web3j() {
        log.info("🔗 Connecting to blockchain network: {}", networkUrl);
        
        Web3j web3j = Web3j.build(new HttpService(networkUrl));
        
        try {
            String clientVersion = web3j.web3ClientVersion().send().getWeb3ClientVersion();
            log.info("✅ Connected to blockchain client: {}", clientVersion);
        } catch (Exception e) {
            log.error("❌ Failed to connect to blockchain: {}", e.getMessage());
            throw new RuntimeException("Cannot connect to blockchain network", e);
        }
        
        return web3j;
    }

    /**
     * Credentials để ký transaction
     */
    @Bean
    public Credentials credentials() {
        if (privateKey == null || privateKey.trim().isEmpty() || 
            privateKey.equals("0x0000000000000000000000000000000000000000000000000000000000000000")) {
            log.warn("⚠️ No private key configured. Using default hardhat account.");
            // Default Hardhat private key (KHÔNG dùng trong production)
            privateKey = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
        }
        
        log.info("🔐 Loading wallet credentials...");
        return Credentials.create(privateKey);
    }

    /**
     * Gas provider cho transaction
     */
    @Bean
    public StaticGasProvider gasProvider() {
        log.info("⛽ Setting up gas provider - Price: {} wei, Limit: {}", gasPrice, gasLimit);
        return new StaticGasProvider(
            BigInteger.valueOf(gasPrice), 
            BigInteger.valueOf(gasLimit)
        );
    }
}
