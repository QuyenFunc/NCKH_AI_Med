require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-verify");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      },
      // Add metadata for better verification
      metadata: {
        bytecodeHash: "none"
      }
    }
  },
  networks: {
    hardhat: {
      chainId: 31337,
      mining: {
        auto: true,
        interval: 0
      }
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
      accounts: ["0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"],
      timeout: 60000
    },
    'pharmaledger-network': {
      url: 'http://127.0.0.1:8545',
      chainId: 31337,
      accounts: ["0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"]
    }
  },
  // Enable direct verification against local Blockscout
  etherscan: {
    apiKey: {
      'localhost': 'blockscout',
      'pharmaledger-network': 'blockscout'
    },
    customChains: [
      {
        network: "localhost",
        chainId: 31337,
        urls: {
          apiURL: "http://localhost:3000/api",
          browserURL: "http://localhost:3000"
        }
      },
      {
        network: "pharmaledger-network",
        chainId: 31337,
        urls: {
          apiURL: "http://localhost:3000/api",
          browserURL: "http://localhost:3000"
        }
      }
    ]
  },
  sourcify: { 
    enabled: false
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};
