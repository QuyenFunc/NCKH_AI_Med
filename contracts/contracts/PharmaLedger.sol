// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title PharmaLedger
 * @dev Smart Contract cho hệ thống truy xuất nguồn gốc thuốc dựa trên Soul-Bound Token (SBT)
 * @author NCKH AI Medical Team
 */
contract PharmaLedger is ERC721, ERC721URIStorage, AccessControl, Pausable {
    
    // Roles
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    bytes32 public constant PHARMACY_ROLE = keccak256("PHARMACY_ROLE");
    bytes32 public constant DISTRIBUTOR_ROLE = keccak256("DISTRIBUTOR_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    // Counters
    uint256 private _batchIdCounter;
    uint256 private _shipmentIdCounter;
    
    // Enums
    enum BatchStatus {
        MANUFACTURED,  // Vừa sản xuất
        IN_TRANSIT,    // Đang vận chuyển
        DELIVERED,     // Đã giao
        DISPENSED,     // Đã phát thuốc
        EXPIRED        // Hết hạn
    }
    
    enum ShipmentStatus {
        CREATED,       // Tạo lô hàng
        IN_PROGRESS,   // Đang giao
        COMPLETED,     // Hoàn thành
        CANCELLED      // Hủy bỏ
    }
    
    // Structs
    struct DrugInfo {
        string name;           // Tên thuốc
        string activeIngredient; // Hoạt chất
        string dosage;         // Liều lượng
        string manufacturer;   // Nhà sản xuất
        string registrationNumber; // Số đăng ký
    }
    
    struct BatchInfo {
        uint256 batchId;       // ID lô hàng
        DrugInfo drugInfo;     // Thông tin thuốc
        uint256 quantity;      // Số lượng
        uint256 manufactureDate; // Ngày sản xuất
        uint256 expiryDate;    // Ngày hết hạn
        address manufacturer;   // Địa chỉ nhà sản xuất
        address currentOwner;   // Chủ sở hữu hiện tại
        BatchStatus status;     // Trạng thái lô hàng
        string qrCode;         // Mã QR
        bool isActive;         // Còn hoạt động
        uint256 registeredSerials; // Số serial đã đăng ký
        uint256 redeemedSerials;   // Số serial đã bán
    }

    struct SerialInfo {
        bool exists;           // Serial đã được đăng ký hay chưa
        bool redeemed;         // Serial đã được bán hay chưa
        uint256 redeemedAt;    // Thời gian bán
        address redeemedBy;    // Địa chỉ người bán
    }

    struct ShipmentInfo {
        uint256 shipmentId;    // ID lô giao hàng
        uint256 batchId;       // ID lô hàng
        address from;          // Người gửi
        address to;            // Người nhận
        uint256 quantity;      // Số lượng giao
        uint256 shipDate;      // Ngày giao
        uint256 receiveDate;   // Ngày nhận
        ShipmentStatus status; // Trạng thái giao hàng
        string trackingNumber; // Số theo dõi
    }
    
    // Mappings
    mapping(uint256 => BatchInfo) public batches;
    mapping(uint256 => ShipmentInfo) public shipments;
    mapping(string => uint256) public qrCodeToBatchId;
    mapping(address => uint256[]) public manufacturerBatches;
    mapping(address => uint256[]) public ownerBatches;
    mapping(uint256 => uint256[]) public batchShipments;
    mapping(uint256 => mapping(string => SerialInfo)) private batchSerialNumbers;

    // Events
    event BatchIssued(
        uint256 indexed batchId,
        address indexed manufacturer,
        string drugName,
        uint256 quantity,
        string qrCode
    );

    event SerialNumbersRegistered(
        uint256 indexed batchId,
        uint256 count
    );

    event SerialNumberRedeemed(
        uint256 indexed batchId,
        string serialNumber,
        address indexed redeemedBy,
        uint256 timestamp
    );
    
    event ShipmentCreated(
        uint256 indexed shipmentId,
        uint256 indexed batchId,
        address indexed from,
        address to,
        uint256 quantity
    );
    
    event ShipmentReceived(
        uint256 indexed shipmentId,
        uint256 indexed batchId,
        address indexed receiver,
        uint256 receiveDate
    );
    
    event BatchStatusUpdated(
        uint256 indexed batchId,
        BatchStatus oldStatus,
        BatchStatus newStatus
    );
    
    event OwnershipTransferred(
        uint256 indexed batchId,
        address indexed previousOwner,
        address indexed newOwner
    );
    
    constructor() ERC721("PharmaLedger", "PHARMA") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }
    
    /**
     * @dev Modifier để kiểm tra quyền sở hữu lô hàng
     */
    modifier onlyBatchOwner(uint256 batchId) {
        require(batches[batchId].currentOwner == msg.sender, "Not batch owner");
        _;
    }
    
    /**
     * @dev Modifier để kiểm tra lô hàng tồn tại
     */
    modifier batchExists(uint256 batchId) {
        require(batches[batchId].isActive, "Batch does not exist");
        _;
    }
    
    /**
     * @dev Cấp phát lô thuốc mới (chỉ nhà sản xuất)
     */
    function issueBatch(
        DrugInfo memory _drugInfo,
        uint256 _quantity,
        uint256 _manufactureDate,
        uint256 _expiryDate,
        string memory _qrCode
    ) external onlyRole(MANUFACTURER_ROLE) whenNotPaused returns (uint256) {
        require(_quantity > 0, "Quantity must be greater than 0");
        require(_expiryDate > _manufactureDate, "Invalid expiry date");
        require(_expiryDate > block.timestamp, "Expiry date in the past");
        require(qrCodeToBatchId[_qrCode] == 0, "QR code already exists");
        
        _batchIdCounter++;
        uint256 newBatchId = _batchIdCounter;
        
        BatchInfo storage newBatch = batches[newBatchId];
        newBatch.batchId = newBatchId;
        newBatch.drugInfo = _drugInfo;
        newBatch.quantity = _quantity;
        newBatch.manufactureDate = _manufactureDate;
        newBatch.expiryDate = _expiryDate;
        newBatch.manufacturer = msg.sender;
        newBatch.currentOwner = msg.sender;
        newBatch.status = BatchStatus.MANUFACTURED;
        newBatch.qrCode = _qrCode;
        newBatch.isActive = true;
        newBatch.registeredSerials = 0;
        newBatch.redeemedSerials = 0;

        // Map QR code to batch ID
        qrCodeToBatchId[_qrCode] = newBatchId;

        // Track manufacturer batches
        manufacturerBatches[msg.sender].push(newBatchId);
        ownerBatches[msg.sender].push(newBatchId);
        
        // Mint SBT (Soul-Bound Token)
        _safeMint(msg.sender, newBatchId);
        
        emit BatchIssued(newBatchId, msg.sender, _drugInfo.name, _quantity, _qrCode);
        
        return newBatchId;
    }
    
    /**
     * @dev Tạo lô giao hàng
     */
    function createShipment(
        uint256 _batchId,
        address _to,
        uint256 _quantity,
        string memory _trackingNumber
    ) external onlyBatchOwner(_batchId) batchExists(_batchId) whenNotPaused returns (uint256) {
        require(_to != address(0), "Invalid recipient address");
        require(_quantity > 0 && _quantity <= batches[_batchId].quantity, "Invalid quantity");
        require(batches[_batchId].status == BatchStatus.MANUFACTURED || 
                batches[_batchId].status == BatchStatus.DELIVERED, "Invalid batch status");
        
        _shipmentIdCounter++;
        uint256 newShipmentId = _shipmentIdCounter;
        
        ShipmentInfo storage newShipment = shipments[newShipmentId];
        newShipment.shipmentId = newShipmentId;
        newShipment.batchId = _batchId;
        newShipment.from = msg.sender;
        newShipment.to = _to;
        newShipment.quantity = _quantity;
        newShipment.shipDate = block.timestamp;
        newShipment.status = ShipmentStatus.CREATED;
        newShipment.trackingNumber = _trackingNumber;
        
        // Update batch status
        _updateBatchStatus(_batchId, BatchStatus.IN_TRANSIT);
        
        // Track shipments for batch
        batchShipments[_batchId].push(newShipmentId);
        
        emit ShipmentCreated(newShipmentId, _batchId, msg.sender, _to, _quantity);
        
        return newShipmentId;
    }

    /**
     * @dev Đăng ký danh sách serial cho lô hàng
     */
    function registerSerialNumbers(
        uint256 _batchId,
        string[] calldata _serialNumbers
    ) external batchExists(_batchId) whenNotPaused {
        require(_serialNumbers.length > 0, "Serial list empty");

        BatchInfo storage batch = batches[_batchId];

        bool isAdmin = hasRole(ADMIN_ROLE, msg.sender);
        require(
            isAdmin || (hasRole(MANUFACTURER_ROLE, msg.sender) && batch.manufacturer == msg.sender),
            "Not authorized"
        );

        require(
            batch.registeredSerials + _serialNumbers.length <= batch.quantity,
            "Exceeds batch quantity"
        );

        uint256 newlyRegistered = 0;

        for (uint256 i = 0; i < _serialNumbers.length; i++) {
            string calldata serial = _serialNumbers[i];
            SerialInfo storage info = batchSerialNumbers[_batchId][serial];
            require(!info.exists, "Serial already registered");

            info.exists = true;
            info.redeemed = false;
            info.redeemedAt = 0;
            info.redeemedBy = address(0);

            newlyRegistered++;
        }

        if (newlyRegistered > 0) {
            batch.registeredSerials += newlyRegistered;
            emit SerialNumbersRegistered(_batchId, newlyRegistered);
        }
    }

    /**
     * @dev Nhận lô hàng
     */
    function receiveShipment(
        uint256 _shipmentId
    ) external whenNotPaused {
        ShipmentInfo storage shipment = shipments[_shipmentId];
        require(shipment.to == msg.sender, "Not authorized to receive");
        require(shipment.status == ShipmentStatus.CREATED, "Invalid shipment status");
        
        uint256 batchId = shipment.batchId;
        BatchInfo storage batch = batches[batchId];
        
        // Update shipment
        shipment.status = ShipmentStatus.COMPLETED;
        shipment.receiveDate = block.timestamp;
        
        // Transfer ownership
        address previousOwner = batch.currentOwner;
        batch.currentOwner = msg.sender;
        
        // Update batch status
        _updateBatchStatus(batchId, BatchStatus.DELIVERED);
        
        // Update owner tracking
        _removeFromOwnerBatches(previousOwner, batchId);
        ownerBatches[msg.sender].push(batchId);
        
        emit ShipmentReceived(_shipmentId, batchId, msg.sender, block.timestamp);
        emit OwnershipTransferred(batchId, previousOwner, msg.sender);
    }

    /**
     * @dev Đánh dấu serial đã bán
     */
    function redeemSerialNumber(
        uint256 _batchId,
        string calldata _serialNumber
    ) external batchExists(_batchId) whenNotPaused {
        BatchInfo storage batch = batches[_batchId];
        require(batch.registeredSerials > 0, "No serials registered");

        SerialInfo storage info = batchSerialNumbers[_batchId][_serialNumber];
        require(info.exists, "Serial not registered");
        require(!info.redeemed, "Serial already redeemed");

        bool isAdmin = hasRole(ADMIN_ROLE, msg.sender);
        if (!isAdmin) {
            require(hasRole(PHARMACY_ROLE, msg.sender), "Caller must be pharmacy");
            require(batch.currentOwner == msg.sender, "Not batch owner");
        }

        info.redeemed = true;
        info.redeemedAt = block.timestamp;
        info.redeemedBy = msg.sender;

        batch.redeemedSerials += 1;

        emit SerialNumberRedeemed(_batchId, _serialNumber, msg.sender, block.timestamp);
    }

    /**
     * @dev Xác thực lô hàng bằng QR code (public view function)
     */
    function verifyByQRCode(string memory _qrCode) external view returns (
        bool isValid,
        BatchInfo memory batchInfo,
        string memory message
    ) {
        uint256 batchId = qrCodeToBatchId[_qrCode];
        
        if (batchId == 0) {
            return (false, BatchInfo({
                batchId: 0,
                drugInfo: DrugInfo("", "", "", "", ""),
                quantity: 0,
                manufactureDate: 0,
                expiryDate: 0,
                manufacturer: address(0),
                currentOwner: address(0),
                status: BatchStatus.EXPIRED,
                qrCode: "",
                isActive: false
            }), "QR code not found");
        }
        
        BatchInfo memory batch = batches[batchId];
        
        if (!batch.isActive) {
            return (false, batch, "Batch is inactive");
        }
        
        if (block.timestamp > batch.expiryDate) {
            return (false, batch, "Drug has expired");
        }
        
        return (true, batch, "Valid drug batch");
    }

    /**
     * @dev Lấy trạng thái serial
     */
    function getSerialNumberStatus(
        uint256 _batchId,
        string calldata _serialNumber
    ) external view returns (
        bool exists,
        bool redeemed,
        uint256 redeemedAt,
        address redeemedBy
    ) {
        SerialInfo storage info = batchSerialNumbers[_batchId][_serialNumber];
        return (info.exists, info.redeemed, info.redeemedAt, info.redeemedBy);
    }
    
    /**
     * @dev Xác thực quyền sở hữu
     */
    function verifyOwnership(uint256 _batchId, address _owner) external view returns (bool) {
        return batches[_batchId].currentOwner == _owner && batches[_batchId].isActive;
    }
    
    /**
     * @dev Lấy lịch sử giao dịch của lô hàng
     */
    function getBatchHistory(uint256 _batchId) external view returns (uint256[] memory) {
        return batchShipments[_batchId];
    }
    
    /**
     * @dev Lấy danh sách lô hàng của owner
     */
    function getOwnerBatches(address _owner) external view returns (uint256[] memory) {
        return ownerBatches[_owner];
    }
    
    /**
     * @dev Cập nhật trạng thái lô hàng (internal)
     */
    function _updateBatchStatus(uint256 _batchId, BatchStatus _newStatus) internal {
        BatchStatus oldStatus = batches[_batchId].status;
        batches[_batchId].status = _newStatus;
        emit BatchStatusUpdated(_batchId, oldStatus, _newStatus);
    }
    
    /**
     * @dev Xóa lô hàng khỏi danh sách owner (internal)
     */
    function _removeFromOwnerBatches(address _owner, uint256 _batchId) internal {
        uint256[] storage ownerBatchList = ownerBatches[_owner];
        for (uint i = 0; i < ownerBatchList.length; i++) {
            if (ownerBatchList[i] == _batchId) {
                ownerBatchList[i] = ownerBatchList[ownerBatchList.length - 1];
                ownerBatchList.pop();
                break;
            }
        }
    }
    
    /**
     * @dev Override transfer functions để implement Soul-Bound Token
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal override returns (address) {
        address from = _ownerOf(tokenId);
        require(from == address(0) || to == address(0), "Soul-bound token cannot be transferred");
        return super._update(to, tokenId, auth);
    }

    /**
     * @dev Override approve to prevent Soul-bound token approval
     */
    function approve(address, uint256) public pure override(ERC721, IERC721) {
        revert("Soul-bound token cannot be approved");
    }

    /**
     * @dev Override setApprovalForAll to prevent Soul-bound token approval
     */
    function setApprovalForAll(address, bool) public pure override(ERC721, IERC721) {
        revert("Soul-bound token cannot be approved");
    }
    
    /**
     * @dev Admin functions
     */
    function addManufacturer(address _manufacturer) external onlyRole(ADMIN_ROLE) {
        _grantRole(MANUFACTURER_ROLE, _manufacturer);
    }
    
    function addPharmacy(address _pharmacy) external onlyRole(ADMIN_ROLE) {
        _grantRole(PHARMACY_ROLE, _pharmacy);
    }
    
    function addDistributor(address _distributor) external onlyRole(ADMIN_ROLE) {
        _grantRole(DISTRIBUTOR_ROLE, _distributor);
    }
    
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
    
           /**
            * @dev Required overrides
            */
           function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
               return super.tokenURI(tokenId);
           }
    
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
