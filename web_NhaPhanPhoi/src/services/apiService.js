import axios from 'axios';

// Base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('distributor_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('distributor_token');
      localStorage.removeItem('distributor_user');
      localStorage.removeItem('walletAddress');
      // Redirect to login if needed
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    const errorMessage = error.response?.data?.message || 
                        error.message || 
                        'Có lỗi xảy ra khi kết nối với server';
    
    return Promise.reject(new Error(errorMessage));
  }
);

// Helpers
const toDateTimeString = (input) => {
  const d = new Date(input);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
};

// Blockchain API endpoints (aligned with backend controllers)
export const blockchainAPI = {
  // Health check -> GET /api/blockchain/status
  healthCheck: () => apiClient.get('/blockchain/status'),
  
  // Manufacturer: create batch -> POST /api/blockchain/drugs/batches
  createBatch: (batchData) => apiClient.post('/blockchain/drugs/batches', {
    drugName: batchData.drugName,
    manufacturer: batchData.manufacturer,
    batchNumber: batchData.batchNumber,
    quantity: Number(batchData.quantity),
    expiryDate: toDateTimeString(batchData.expiryDate),
    storageConditions: batchData.storageConditions || ''
  }),
  
  // Distributor: create shipment -> POST /api/blockchain/drugs/shipments
  createShipment: (shipmentData) => apiClient.post('/blockchain/drugs/shipments', {
    batchId: shipmentData.batchId.toString(), // Ensure string for BigInteger
    toAddress: shipmentData.pharmacyAddress,
    quantity: Number(shipmentData.quantity),
    trackingInfo: shipmentData.trackingInfo || shipmentData.trackingNumber
  }),
  
  // Pharmacy: receive shipment -> POST /api/blockchain/drugs/shipments/{id}/receive
  receiveShipment: (shipmentId) => apiClient.post(`/blockchain/drugs/shipments/${shipmentId}/receive`),
  
  // Public: verify drug by QR -> POST /api/blockchain/drugs/verify
  verifyDrug: (qrCode) => apiClient.post('/blockchain/drugs/verify', { qrCode }),
  
  // Batch details -> GET /api/blockchain/drugs/batches/{batchId}
  getBatchDetails: (batchId) => apiClient.get(`/blockchain/drugs/batches/${batchId}`),
  // Shipments by batch -> GET /api/blockchain/drugs/batches/{batchId}/shipments
  getShipmentsByBatch: (batchId) => apiClient.get(`/blockchain/drugs/batches/${batchId}/shipments`),
  
  // All batches
  getAllBatches: () => apiClient.get('/blockchain/drugs/batches'),
  // Batches by current owner -> GET /api/blockchain/drugs/batches/owner/{ownerAddress}
  getBatchesByOwner: (ownerAddress) => apiClient.get(`/blockchain/drugs/batches/owner/${ownerAddress}`),
  
  // Shipments list
  getShipments: (params = {}) => apiClient.get('/blockchain/drugs/shipments', { params }),
  
  // Shipment by ID
  getShipmentById: (shipmentId) => apiClient.get(`/blockchain/drugs/shipments/${shipmentId}`),

  // Shipments by recipient (inbound for distributor) -> GET /api/blockchain/drugs/shipments/recipient/{recipientAddress}
  getShipmentsByRecipient: (recipientAddress) => apiClient.get(`/blockchain/drugs/shipments/recipient/${recipientAddress}`)
};

// Service functions
export const distributorService = {
  // Dashboard
  getDashboardData: async () => {
    try {
      return await apiClient.get('/blockchain/drugs/stats');
    } catch (error) {
      console.error('Failed to get dashboard data:', error.message);
      throw error;
    }
  },

  // Batches
  getBatches: async () => {
    try {
      return await apiClient.get('/blockchain/drugs/batches');
    } catch (error) {
      console.error('Failed to get batches:', error.message);
      throw error;
    }
  },

  // Batches owned by distributor
  getBatchesByOwner: async (ownerAddress) => {
    if (!ownerAddress) {
      throw new Error('Owner address is required');
    }
    try {
      return await blockchainAPI.getBatchesByOwner(ownerAddress);
    } catch (error) {
      console.error('Failed to get batches by owner:', error.message);
      throw error;
    }
  },

  // Get distributor inventory with REAL available quantities
  getInventoryByWallet: async (walletAddress) => {
    if (!walletAddress) {
      throw new Error('Wallet address is required');
    }
    try {
      return await apiClient.get(`/distributor/inventory/wallet/${walletAddress}`);
    } catch (error) {
      console.error('Failed to get inventory by wallet:', error.message);
      throw error;
    }
  },

  getBatchDetails: async (batchId) => {
    try {
      return await blockchainAPI.getBatchDetails(batchId);
    } catch (error) {
      console.error('Failed to get batch details:', error.message);
      throw error;
    }
  },

  // Pharmacies
  getPharmacies: async () => {
    try {
      return await apiClient.get('/pharmacies');
    } catch (error) {
      console.error('Failed to get pharmacies:', error.message);
      throw error;
    }
  },

  // Shipments
  createShipment: async (shipmentData) => {
    try {
      // Normalize batchId - remove any prefix and convert to BigInteger compatible string
      let batchId = shipmentData.batchId;
      if (typeof batchId === 'string' && batchId.startsWith('BT')) {
        batchId = batchId.replace('BT', '');
      }
      
      // Use the distributor-specific endpoint with pharmacyId
      return await apiClient.post('/distributor/shipments', {
        batchId: batchId.toString(), // Ensure string for BigInteger parsing
        pharmacyId: parseInt(shipmentData.pharmacyId),
        quantity: parseInt(shipmentData.quantity),
        trackingNumber: shipmentData.trackingNumber,
        notes: shipmentData.notes || '',
        driverName: shipmentData.driverName || '',
        driverPhone: shipmentData.driverPhone || '',
        transportMethod: shipmentData.transportMethod || 'Xe tải'
      });
    } catch (error) {
      console.error('Failed to create shipment:', error.message);
      throw error;
    }
  },

  getShipments: async (filters = {}) => {
    try {
      return await blockchainAPI.getShipments(filters);
    } catch (error) {
      console.error('Failed to get shipments:', error.message);
      throw error;
    }
  },

  getShipmentById: async (shipmentId) => {
    try {
      return await blockchainAPI.getShipmentById(shipmentId);
    } catch (error) {
      console.error('Failed to get shipment details:', error.message);
      throw error;
    }
  },

  // Shipments by batch
  getShipmentsByBatch: async (batchId) => {
    try {
      return await blockchainAPI.getShipmentsByBatch(batchId);
    } catch (error) {
      console.error('Failed to get shipments by batch:', error.message);
      throw error;
    }
  },

  // Shipments by recipient
  getShipmentsByRecipient: async (recipientAddress) => {
    try {
      return await blockchainAPI.getShipmentsByRecipient(recipientAddress);
    } catch (error) {
      console.error('Failed to get shipments by recipient:', error.message);
      throw error;
    }
  },

  // Verification
  verifyDrug: async (qrCode) => {
    try {
      return await blockchainAPI.verifyDrug(qrCode);
    } catch (error) {
      console.error('Failed to verify drug:', error.message);
      throw error;
    }
  },

  // Verify shipment ownership on blockchain - Anti-counterfeit check
  verifyShipmentOwnership: async (shipmentId, expectedOwner) => {
    try {
      return await apiClient.get(`/blockchain/drugs/shipments/${shipmentId}/verify-ownership`, {
        params: { expectedOwner }
      });
    } catch (error) {
      console.error('Failed to verify shipment ownership:', error.message);
      throw error;
    }
  },

  // Receive Goods (Nhập kho từ NSX)
  receiveShipment: async (shipmentId) => {
    try {
      return await blockchainAPI.receiveShipment(shipmentId);
    } catch (error) {
      console.error('Failed to receive shipment:', error.message);
      throw error;
    }
  },

  // Get pending inbound shipments for a recipient
  getInboundShipments: async (recipientAddress) => {
    try {
      const response = await distributorService.getShipmentsByRecipient(recipientAddress);
      if (response.success && response.data) {
        // Filter for shipments that are 'in_transit' and not yet received
        return {
          ...response,
          data: response.data.filter(shipment => shipment.status === 'in_transit')
        };
      }
      return { success: true, data: [] };
    } catch (error) {
      console.error('Failed to get inbound shipments:', error.message);
      throw error;
    }
  },

  // ==================== DISTRIBUTOR INVENTORY APIs ====================

  // Get distributor inventory by wallet address
  getDistributorInventory: async (walletAddress) => {
    try {
      return await apiClient.get(`/distributor/inventory/wallet/${walletAddress}`);
    } catch (error) {
      console.error('Failed to get distributor inventory:', error.message);
      throw error;
    }
  },

  // Get low stock items
  getDistributorLowStock: async (distributorId) => {
    try {
      return await apiClient.get(`/distributor/inventory/company/${distributorId}/low-stock`);
    } catch (error) {
      console.error('Failed to get low stock items:', error.message);
      throw error;
    }
  },

  // Get expiring soon items
  getDistributorExpiringSoon: async (distributorId) => {
    try {
      return await apiClient.get(`/distributor/inventory/company/${distributorId}/expiring-soon`);
    } catch (error) {
      console.error('Failed to get expiring soon items:', error.message);
      throw error;
    }
  },

  // Search distributor inventory
  searchDistributorInventory: async (distributorId, searchTerm) => {
    try {
      return await apiClient.get(`/distributor/inventory/company/${distributorId}/search`, {
        params: { searchTerm }
      });
    } catch (error) {
      console.error('Failed to search inventory:', error.message);
      throw error;
    }
  },

  // Get total inventory value
  getDistributorInventoryValue: async (distributorId) => {
    try {
      return await apiClient.get(`/distributor/inventory/company/${distributorId}/total-value`);
    } catch (error) {
      console.error('Failed to get inventory value:', error.message);
      throw error;
    }
  }
};

// Export API client for auth service
export { apiClient };

// Export default
export default distributorService;