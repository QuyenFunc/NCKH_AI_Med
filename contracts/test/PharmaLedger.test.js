const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time, loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

describe("PharmaLedger", function () {
  // Fixture để deploy contract và setup initial state
  async function deployPharmaLedgerFixture() {
    const [owner, manufacturer, pharmacy, distributor, user] = await ethers.getSigners();

    const PharmaLedger = await ethers.getContractFactory("PharmaLedger");
    const pharmaLedger = await PharmaLedger.deploy();

    // Grant roles
    const MANUFACTURER_ROLE = await pharmaLedger.MANUFACTURER_ROLE();
    const PHARMACY_ROLE = await pharmaLedger.PHARMACY_ROLE();
    const DISTRIBUTOR_ROLE = await pharmaLedger.DISTRIBUTOR_ROLE();

    await pharmaLedger.grantRole(MANUFACTURER_ROLE, manufacturer.address);
    await pharmaLedger.grantRole(PHARMACY_ROLE, pharmacy.address);
    await pharmaLedger.grantRole(DISTRIBUTOR_ROLE, distributor.address);

    return {
      pharmaLedger,
      owner,
      manufacturer,
      pharmacy,
      distributor,
      user,
      MANUFACTURER_ROLE,
      PHARMACY_ROLE,
      DISTRIBUTOR_ROLE
    };
  }

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      const { pharmaLedger, owner } = await loadFixture(deployPharmaLedgerFixture);
      
      const DEFAULT_ADMIN_ROLE = await pharmaLedger.DEFAULT_ADMIN_ROLE();
      expect(await pharmaLedger.hasRole(DEFAULT_ADMIN_ROLE, owner.address)).to.be.true;
    });

    it("Should have correct name and symbol", async function () {
      const { pharmaLedger } = await loadFixture(deployPharmaLedgerFixture);
      
      expect(await pharmaLedger.name()).to.equal("PharmaLedger");
      expect(await pharmaLedger.symbol()).to.equal("PHARMA");
    });
  });

  describe("Role Management", function () {
    it("Should allow admin to grant manufacturer role", async function () {
      const { pharmaLedger, manufacturer, MANUFACTURER_ROLE } = await loadFixture(deployPharmaLedgerFixture);
      
      expect(await pharmaLedger.hasRole(MANUFACTURER_ROLE, manufacturer.address)).to.be.true;
    });

    it("Should allow admin to add new manufacturer", async function () {
      const { pharmaLedger, user } = await loadFixture(deployPharmaLedgerFixture);
      
      await pharmaLedger.addManufacturer(user.address);
      const MANUFACTURER_ROLE = await pharmaLedger.MANUFACTURER_ROLE();
      expect(await pharmaLedger.hasRole(MANUFACTURER_ROLE, user.address)).to.be.true;
    });

    it("Should not allow non-admin to grant roles", async function () {
      const { pharmaLedger, user, manufacturer } = await loadFixture(deployPharmaLedgerFixture);
      
      await expect(
        pharmaLedger.connect(user).addManufacturer(manufacturer.address)
      ).to.be.reverted;
    });
  });

  describe("Batch Issuance", function () {
    it("Should allow manufacturer to issue new batch", async function () {
      const { pharmaLedger, manufacturer } = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (365 * 24 * 60 * 60); // 1 year later
      const qrCode = "QR123456789";

      await expect(
        pharmaLedger.connect(manufacturer).issueBatch(
          drugInfo,
          quantity,
          manufactureDate,
          expiryDate,
          qrCode
        )
      ).to.emit(pharmaLedger, "BatchIssued")
        .withArgs(1, manufacturer.address, drugInfo.name, quantity, qrCode);

      // Verify batch details
      const batch = await pharmaLedger.batches(1);
      expect(batch.batchId).to.equal(1);
      expect(batch.quantity).to.equal(quantity);
      expect(batch.manufacturer).to.equal(manufacturer.address);
      expect(batch.currentOwner).to.equal(manufacturer.address);
      expect(batch.qrCode).to.equal(qrCode);
      expect(batch.isActive).to.be.true;
    });

    it("Should not allow non-manufacturer to issue batch", async function () {
      const { pharmaLedger, user } = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (365 * 24 * 60 * 60);
      const qrCode = "QR123456789";

      await expect(
        pharmaLedger.connect(user).issueBatch(
          drugInfo,
          quantity,
          manufactureDate,
          expiryDate,
          qrCode
        )
      ).to.be.reverted;
    });

    it("Should not allow duplicate QR codes", async function () {
      const { pharmaLedger, manufacturer } = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (365 * 24 * 60 * 60);
      const qrCode = "QR123456789";

      // First batch
      await pharmaLedger.connect(manufacturer).issueBatch(
        drugInfo,
        quantity,
        manufactureDate,
        expiryDate,
        qrCode
      );

      // Try to create second batch with same QR code
      await expect(
        pharmaLedger.connect(manufacturer).issueBatch(
          drugInfo,
          quantity,
          manufactureDate,
          expiryDate,
          qrCode
        )
      ).to.be.revertedWith("QR code already exists");
    });

    it("Should validate expiry date", async function () {
      const { pharmaLedger, manufacturer } = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate - (30 * 24 * 60 * 60); // 30 days ago
      const qrCode = "QR123456789";

      await expect(
        pharmaLedger.connect(manufacturer).issueBatch(
          drugInfo,
          quantity,
          manufactureDate,
          expiryDate,
          qrCode
        )
      ).to.be.revertedWith("Invalid expiry date");
    });
  });

  describe("Shipment Creation and Reception", function () {
    async function createBatchFixture() {
      const base = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (365 * 24 * 60 * 60);
      const qrCode = "QR123456789";

      await base.pharmaLedger.connect(base.manufacturer).issueBatch(
        drugInfo,
        quantity,
        manufactureDate,
        expiryDate,
        qrCode
      );

      return { ...base, batchId: 1 };
    }

    it("Should allow batch owner to create shipment", async function () {
      const { pharmaLedger, manufacturer, pharmacy, batchId } = await loadFixture(createBatchFixture);
      
      const shipmentQuantity = 500;
      const trackingNumber = "TRACK123456";

      await expect(
        pharmaLedger.connect(manufacturer).createShipment(
          batchId,
          pharmacy.address,
          shipmentQuantity,
          trackingNumber
        )
      ).to.emit(pharmaLedger, "ShipmentCreated")
        .withArgs(1, batchId, manufacturer.address, pharmacy.address, shipmentQuantity);

      // Verify shipment details
      const shipment = await pharmaLedger.shipments(1);
      expect(shipment.batchId).to.equal(batchId);
      expect(shipment.from).to.equal(manufacturer.address);
      expect(shipment.to).to.equal(pharmacy.address);
      expect(shipment.quantity).to.equal(shipmentQuantity);
      expect(shipment.trackingNumber).to.equal(trackingNumber);
    });

    it("Should allow recipient to receive shipment", async function () {
      const { pharmaLedger, manufacturer, pharmacy, batchId } = await loadFixture(createBatchFixture);
      
      const shipmentQuantity = 500;
      const trackingNumber = "TRACK123456";

      // Create shipment
      await pharmaLedger.connect(manufacturer).createShipment(
        batchId,
        pharmacy.address,
        shipmentQuantity,
        trackingNumber
      );

      // Receive shipment
      await expect(
        pharmaLedger.connect(pharmacy).receiveShipment(1)
      ).to.emit(pharmaLedger, "ShipmentReceived")
        .withArgs(1, batchId, pharmacy.address, await time.latest() + 1);

      // Verify ownership transfer
      const batch = await pharmaLedger.batches(batchId);
      expect(batch.currentOwner).to.equal(pharmacy.address);
    });

    it("Should not allow unauthorized user to receive shipment", async function () {
      const { pharmaLedger, manufacturer, pharmacy, user, batchId } = await loadFixture(createBatchFixture);
      
      const shipmentQuantity = 500;
      const trackingNumber = "TRACK123456";

      // Create shipment
      await pharmaLedger.connect(manufacturer).createShipment(
        batchId,
        pharmacy.address,
        shipmentQuantity,
        trackingNumber
      );

      // Try to receive shipment with unauthorized user
      await expect(
        pharmaLedger.connect(user).receiveShipment(1)
      ).to.be.revertedWith("Not authorized to receive");
    });
  });

  describe("QR Code Verification", function () {
    async function createBatchFixture() {
      const base = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (365 * 24 * 60 * 60);
      const qrCode = "QR123456789";

      await base.pharmaLedger.connect(base.manufacturer).issueBatch(
        drugInfo,
        quantity,
        manufactureDate,
        expiryDate,
        qrCode
      );

      return { ...base, qrCode };
    }

    it("Should verify valid QR code", async function () {
      const { pharmaLedger, qrCode } = await loadFixture(createBatchFixture);
      
      const result = await pharmaLedger.verifyByQRCode(qrCode);
      expect(result.isValid).to.be.true;
      expect(result.batchInfo.drugInfo.name).to.equal("Paracetamol");
      expect(result.message).to.equal("Valid drug batch");
    });

    it("Should reject invalid QR code", async function () {
      const { pharmaLedger } = await loadFixture(createBatchFixture);
      
      const result = await pharmaLedger.verifyByQRCode("INVALID_QR");
      expect(result.isValid).to.be.false;
      expect(result.message).to.equal("QR code not found");
    });

    it("Should reject expired batch", async function () {
      const { pharmaLedger, manufacturer } = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Expired Drug",
        activeIngredient: "Something",
        dosage: "100mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG789"
      };
      
      const quantity = 100;
      const now = Math.floor(Date.now() / 1000);
      const manufactureDate = now - (400 * 24 * 60 * 60); // 400 days ago
      const expiryDate = now - (30 * 24 * 60 * 60); // 30 days ago (expired)
      const qrCode = "EXPIRED_QR";

      await expect(
        pharmaLedger.connect(manufacturer).issueBatch(
          drugInfo,
          quantity,
          manufactureDate,
          expiryDate,
          qrCode
        )
      ).to.be.revertedWith("Expiry date in the past");
    });
  });

  describe("Ownership Verification", function () {
    async function createAndTransferBatchFixture() {
      const base = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (365 * 24 * 60 * 60);
      const qrCode = "QR123456789";

      await base.pharmaLedger.connect(base.manufacturer).issueBatch(
        drugInfo,
        quantity,
        manufactureDate,
        expiryDate,
        qrCode
      );

      // Create and receive shipment
      await base.pharmaLedger.connect(base.manufacturer).createShipment(
        1,
        base.pharmacy.address,
        500,
        "TRACK123"
      );

      await base.pharmaLedger.connect(base.pharmacy).receiveShipment(1);

      return { ...base, batchId: 1 };
    }

    it("Should verify correct ownership", async function () {
      const { pharmaLedger, pharmacy, batchId } = await loadFixture(createAndTransferBatchFixture);
      
      const isOwner = await pharmaLedger.verifyOwnership(batchId, pharmacy.address);
      expect(isOwner).to.be.true;
    });

    it("Should reject incorrect ownership", async function () {
      const { pharmaLedger, manufacturer, batchId } = await loadFixture(createAndTransferBatchFixture);
      
      const isOwner = await pharmaLedger.verifyOwnership(batchId, manufacturer.address);
      expect(isOwner).to.be.false;
    });
  });

  describe("Soul-Bound Token (SBT) Restrictions", function () {
    async function createBatchFixture() {
      const base = await loadFixture(deployPharmaLedgerFixture);
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      const quantity = 1000;
      const manufactureDate = Math.floor(Date.now() / 1000);
      const expiryDate = manufactureDate + (365 * 24 * 60 * 60);
      const qrCode = "QR123456789";

      await base.pharmaLedger.connect(base.manufacturer).issueBatch(
        drugInfo,
        quantity,
        manufactureDate,
        expiryDate,
        qrCode
      );

      return { ...base, batchId: 1 };
    }

    it("Should prevent direct token transfer", async function () {
      const { pharmaLedger, manufacturer, pharmacy, batchId } = await loadFixture(createBatchFixture);
      
      await expect(
        pharmaLedger.connect(manufacturer).transferFrom(
          manufacturer.address,
          pharmacy.address,
          batchId
        )
      ).to.be.revertedWith("Soul-bound token cannot be transferred");
    });

    it("Should prevent approval and transfer", async function () {
      const { pharmaLedger, manufacturer, pharmacy, batchId } = await loadFixture(createBatchFixture);
      
      await expect(
        pharmaLedger.connect(manufacturer).approve(pharmacy.address, batchId)
      ).to.be.revertedWith("Soul-bound token cannot be approved");
    });
  });

  describe("Pause Functionality", function () {
    it("Should allow admin to pause contract", async function () {
      const { pharmaLedger, owner } = await loadFixture(deployPharmaLedgerFixture);
      
      await pharmaLedger.connect(owner).pause();
      expect(await pharmaLedger.paused()).to.be.true;
    });

    it("Should prevent actions when paused", async function () {
      const { pharmaLedger, manufacturer, owner } = await loadFixture(deployPharmaLedgerFixture);
      
      await pharmaLedger.connect(owner).pause();
      
      const drugInfo = {
        name: "Paracetamol",
        activeIngredient: "Acetaminophen",
        dosage: "500mg",
        manufacturer: "ABC Pharma",
        registrationNumber: "REG123456"
      };
      
      // OpenZeppelin 5.x uses custom errors instead of string messages for Pausable
      await expect(
        pharmaLedger.connect(manufacturer).issueBatch(
          drugInfo,
          1000,
          Math.floor(Date.now() / 1000),
          Math.floor(Date.now() / 1000) + (365 * 24 * 60 * 60),
          "QR123"
        )
      ).to.be.revertedWithCustomError(pharmaLedger, "EnforcedPause");
    });
  });
});
