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

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('manufacturer_token') || localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response?.status === 401) {
      localStorage.removeItem('manufacturer_token');
      localStorage.removeItem('manufacturer_user');
      localStorage.removeItem('walletAddress');
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// Helpers
const toDateTimeString = (input) => {
  const d = new Date(input);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
};

// Blockchain API calls
const blockchainAPI = {
  // Create new batch (core function) -> POST /api/blockchain/drugs/batches
  createBatch: async (batchData) => {
    // Ensure proper date formatting for LocalDateTime
    const formatExpiryDate = (dateString) => {
      if (!dateString) return null;
      // If already has time component, use as is
      if (dateString.includes('T')) {
        return dateString;
      }
      // Otherwise add time component for end of day
      return `${dateString}T23:59:59`;
    };
    
    const payload = {
      drugName: batchData.productName,
      manufacturer: batchData.manufacturer,
      batchNumber: batchData.id,
      quantity: parseInt(batchData.quantity),
      expiryDate: formatExpiryDate(batchData.expiryDate),
      storageConditions: batchData.storageConditions || 'Bảo quản ở nhiệt độ phòng'
    };
    
    console.log('Creating batch with payload:', payload);
    return await apiClient.post('/blockchain/drugs/batches', payload);
  },

  // Create shipment -> POST /api/blockchain/drugs/shipments
  createShipment: async (shipmentData) => {
    console.log('API Service - Creating shipment with data:', shipmentData);
    const payload = {
      batchId: String(shipmentData.batchId), // Ensure it's a string for BigInteger parsing
      toAddress: String(shipmentData.toAddress || shipmentData.pharmacyAddress),
      quantity: Number(shipmentData.quantity),
      trackingInfo: shipmentData.trackingInfo || undefined
    };
    console.log('API Service - Sending payload:', payload);
    return await apiClient.post('/blockchain/drugs/shipments', payload);
  },

  // Get batch details -> GET /api/blockchain/drugs/batches/{batchId}
  getBatchById: async (batchId) => {
    return await apiClient.get(`/blockchain/drugs/batches/${batchId}`);
  },

  // Get manufacturer statistics
  getManufacturerStats: async () => {
    try {
      return await apiClient.get('/blockchain/manufacturer/stats');
    } catch (error) {
      console.error('Failed to get manufacturer stats:', error.message);
      throw error;
    }
  }
};

  // Manufacturer Service
const manufacturerService = {
  // Dashboard
  getDashboardData: async () => {
    try {
      // Try to get real stats from API
      const response = await blockchainAPI.getManufacturerStats();
      if (response.success) {
        return response;
      }
      throw new Error('Failed to get manufacturer stats');
    } catch (error) {
      console.error('Failed to get dashboard data:', error.message);
      throw error;
    }
  },

  // Product Management
  getProducts: async () => {
    try {
      // Use real manufacturer products
      const response = await apiClient.get('/products');
      if (response.success && response.data) {
        // Backend already returns drug_products; no transform/duplication
        return { success: true, data: response.data };
      }
      throw new Error('Invalid response format');
    } catch (error) {
      console.error('Failed to get products from API:', error.message);
      throw error;
    }
  },

  createProduct: async (productData) => {
    try {
      return await apiClient.post('/products', productData);
    } catch (error) {
      console.error('Failed to create product:', error.message);
      throw error;
    }
  },

  updateProduct: async (productId, productData) => {
    try {
      return await apiClient.put(`/products/${productId}`, productData);
    } catch (error) {
      console.error('Failed to update product:', error.message);
      throw error;
    }
  },

  deleteProduct: async (productId) => {
    try {
      return await apiClient.delete(`/products/${productId}`);
    } catch (error) {
      console.error('Failed to delete product:', error.message);
      throw error;
    }
  },

  // Batch Allocation - Core function
  createBatch: async (batchData) => {
    try {
      return await blockchainAPI.createBatch(batchData);
    } catch (error) {
      console.error('Failed to create batch:', error.message);
      throw error;
    }
  },

  getBatches: async () => {
    try {
      return await apiClient.get('/blockchain/drugs/batches');
    } catch (error) {
      console.error('Failed to get batches:', error.message);
      throw error;
    }
  },

  getBatchesReadyForShipment: async () => {
    try {
      return await apiClient.get('/blockchain/drugs/batches/ready-for-shipment');
    } catch (error) {
      console.error('Failed to get batches ready for shipment:', error.message);
      throw error;
    }
  },

  getDistributors: async () => {
    try {
      return await apiClient.get('/blockchain/drugs/distributors');
    } catch (error) {
      console.error('Failed to get distributors:', error.message);
      throw error;
    }
  },

  // Shipment Management
  createShipment: async (shipmentData) => {
    try {
      return await blockchainAPI.createShipment(shipmentData);
    } catch (error) {
      console.error('Failed to create shipment:', error.message);
      throw error;
    }
  },

  getShipments: async () => {
    try {
      return await apiClient.get('/blockchain/drugs/shipments');
    } catch (error) {
      console.error('Failed to get shipments:', error.message);
      throw error;
    }
  },

  updateShipmentStatus: async (shipmentId, status) => {
    try {
      return await apiClient.patch(`/blockchain/drugs/shipments/${shipmentId}/status`, { status });
    } catch (error) {
      console.error('Failed to update shipment status:', error.message);
      throw error;
    }
  },

  // Reports
  getProductionReport: async (dateRange) => {
    try {
      return await apiClient.get('/reports/production', { params: dateRange });
    } catch (error) {
      console.error('Failed to get production report:', error.message);
      throw error;
    }
  },

  getShipmentReport: async (dateRange) => {
    try {
      return await apiClient.get('/reports/shipments', { params: dateRange });
    } catch (error) {
      console.error('Failed to get shipment report:', error.message);
      throw error;
    }
  },

  // Account Management
  getCompanyInfo: async () => {
    try {
      return await apiClient.get('/account/company');
    } catch (error) {
      console.error('Failed to get company info:', error.message);
      throw error;
    }
  },

  updateCompanyInfo: async (companyData) => {
    try {
      return await apiClient.put('/account/company', companyData);
    } catch (error) {
      console.error('Failed to update company info:', error.message);
      throw error;
    }
  },

  getEmployees: async () => {
    try {
      return await apiClient.get('/account/employees');
    } catch (error) {
      console.error('Failed to get employees:', error.message);
      throw error;
    }
  },

  // Verification
  verifyBatch: async (batchId) => {
    try {
      return await blockchainAPI.getBatchById(batchId);
    } catch (error) {
      console.error('Failed to verify batch:', error.message);
      throw error;
    }
  }
};

// Export default
export default manufacturerService;
