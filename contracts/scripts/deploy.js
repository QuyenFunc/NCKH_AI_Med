const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Starting PharmaLedger deployment...\n");

  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📋 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", (await ethers.provider.getBalance(deployer.address)).toString(), "wei\n");

  // Deploy PharmaLedger contract
  console.log("⏳ Deploying PharmaLedger contract...");
  const PharmaLedger = await ethers.getContractFactory("PharmaLedger");
  const pharmaLedger = await PharmaLedger.deploy();
  
  await pharmaLedger.waitForDeployment();
  
  const contractAddress = await pharmaLedger.getAddress();
  console.log("✅ PharmaLedger deployed to:", contractAddress);
  console.log("🔗 Transaction hash:", pharmaLedger.deploymentTransaction().hash);
  console.log("⛽ Gas used:", pharmaLedger.deploymentTransaction().gasLimit.toString());

  // Setup initial roles and test accounts
  console.log("\n🔐 Setting up initial roles...");
  
  // Test accounts (you can replace these with real addresses)
  const testManufacturer = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"; // Hardhat account #1
  const testPharmacy = "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC";     // Hardhat account #2
  const testDistributor = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"; // Hardhat account #3

  try {
    // Add manufacturer role
    await pharmaLedger.addManufacturer(testManufacturer);
    console.log("✅ Added manufacturer role to:", testManufacturer);

    // Add pharmacy role
    await pharmaLedger.addPharmacy(testPharmacy);
    console.log("✅ Added pharmacy role to:", testPharmacy);

    // Add distributor role
    await pharmaLedger.addDistributor(testDistributor);
    console.log("✅ Added distributor role to:", testDistributor);

  } catch (error) {
    console.log("⚠️  Role setup skipped (accounts may not exist in this network)");
  }

  // Verify contract structure
  console.log("\n🔍 Verifying contract deployment...");
  
  const contractName = await pharmaLedger.name();
  const contractSymbol = await pharmaLedger.symbol();
  const adminRole = await pharmaLedger.DEFAULT_ADMIN_ROLE();
  const hasAdminRole = await pharmaLedger.hasRole(adminRole, deployer.address);

  console.log("📄 Contract name:", contractName);
  console.log("🔤 Contract symbol:", contractSymbol);
  console.log("👑 Deployer has admin role:", hasAdminRole);

  // Create sample batch for testing (optional)
  if (process.env.CREATE_SAMPLE_DATA === "true") {
    console.log("\n📦 Creating sample batch for testing...");
    
    try {
      // Grant deployer manufacturer role temporarily
      const manufacturerRole = await pharmaLedger.MANUFACTURER_ROLE();
      await pharmaLedger.grantRole(manufacturerRole, deployer.address);

      const sampleDrugInfo = {
        name: "Paracetamol 500mg",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "Sample Pharma Ltd",
        registrationNumber: "VD-123456-25"
      };

      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (2 * 365 * 24 * 60 * 60); // 2 years
      const qrCode = "SAMPLE_QR_" + Date.now();

      const tx = await pharmaLedger.issueBatch(
        sampleDrugInfo,
        quantity,
        manufactureDate,
        expiryDate,
        qrCode
      );

      const receipt = await tx.wait();
      console.log("✅ Sample batch created successfully!");
      console.log("📊 Batch ID: 1");
      console.log("🔗 QR Code:", qrCode);
      console.log("📝 Transaction hash:", receipt.transactionHash);

    } catch (error) {
      console.log("⚠️  Failed to create sample batch:", error.message);
    }
  }

  // Save deployment info
  const deploymentInfo = {
    contractAddress: contractAddress,
    deployerAddress: deployer.address,
    transactionHash: pharmaLedger.deploymentTransaction().hash,
    blockNumber: pharmaLedger.deploymentTransaction().blockNumber,
    gasUsed: pharmaLedger.deploymentTransaction().gasLimit.toString(),
    timestamp: new Date().toISOString(),
    network: process.env.HARDHAT_NETWORK || "hardhat",
    contractABI: PharmaLedger.interface.format('json')
  };

  // Write deployment info to file
  const fs = require('fs');
  const path = require('path');
  
  const deploymentsDir = path.join(__dirname, '..', 'deployments');
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const deploymentFile = path.join(deploymentsDir, 'PharmaLedger.json');
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

  console.log("\n💾 Deployment info saved to:", deploymentFile);

  // Print final summary
  console.log("\n" + "=".repeat(60));
  console.log("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!");
  console.log("=".repeat(60));
  console.log("📍 Contract Address:", contractAddress);
  console.log("🌐 Network:", process.env.HARDHAT_NETWORK || "hardhat");
  console.log("👨‍💻 Deployer:", deployer.address);
  console.log("📊 Gas Used:", pharmaLedger.deploymentTransaction().gasLimit.toString());
  console.log("⏰ Timestamp:", new Date().toLocaleString());
  console.log("=".repeat(60));

  console.log("\n📋 Next steps:");
  console.log("1. Save the contract address for your backend integration");
  console.log("2. Update your environment variables with the contract address");
  console.log("3. Grant appropriate roles to real accounts");
  console.log("4. Test the contract functionality with your frontend");

  return contractAddress;
}

// Handle script execution
main()
  .then((contractAddress) => {
    console.log("\n✅ Script completed successfully!");
    console.log("📍 Contract deployed at:", contractAddress);
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });

