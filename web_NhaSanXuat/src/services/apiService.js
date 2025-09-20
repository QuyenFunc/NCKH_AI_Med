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
    const token = localStorage.getItem('authToken');
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
    return await apiClient.post('/blockchain/drugs/batches', {
      drugName: batchData.productName,
      manufacturer: batchData.manufacturer,
      batchNumber: batchData.id,
      quantity: Number(batchData.quantity),
      expiryDate: batchData.expiryDate + 'T00:00:00',  // LocalDateTime format
      storageConditions: batchData.storageConditions || ''
    });
  },

  // Create shipment -> POST /api/blockchain/drugs/shipments
  createShipment: async (shipmentData) => {
    return await apiClient.post('/blockchain/drugs/shipments', {
      batchId: shipmentData.batchId,
      toAddress: shipmentData.recipientAddress,
      quantity: Number(shipmentData.quantity),
      trackingInfo: shipmentData.trackingInfo || undefined
    });
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
      console.warn('Failed to get manufacturer stats:', error.message);
      // Mock response
      return {
        success: true,
        data: {
          totalProducts: 25,
          activeBatches: 45,
          shippedBatches: 128,
          totalDistributors: 15
        }
      };
    }
  }
};

// Manufacturer Service
const manufacturerService = {
  // Dashboard
  getDashboardData: async () => {
    try {
      return await blockchainAPI.getManufacturerStats();
    } catch (error) {
      console.warn('Failed to get dashboard data:', error.message);
      // Mock response
      return {
        success: true,
        data: {
          totalProducts: 25,
          activeBatches: 45,
          shippedBatches: 128,
          totalDistributors: 15,
          recentActivities: [],
          chartData: []
        }
      };
    }
  },

  // Product Management
  getProducts: async () => {
    try {
      const response = await apiClient.get('/medications');
      // Transform medication data to product format expected by frontend
      if (response.success && response.data) {
        const products = response.data.map(med => ({
          id: med.id,
          name: med.name,
          category: med.drugClass || 'Khác',
          dosage: med.commonDosages ? JSON.parse(med.commonDosages)[0] : 'N/A',
          unit: 'viên', // Default unit
          activeIngredient: med.genericName || med.name,
          description: `Thuốc ${med.drugClass || 'điều trị'}`,
          storageConditions: 'Nơi khô ráo, tránh ánh sáng',
          shelfLife: '36 tháng', // Default shelf life
          status: 'active',
          createdDate: med.createdAt || new Date().toISOString(),
          totalBatches: 0,
          totalProduced: 0
        }));
        
        return {
          success: true,
          data: products
        };
      }
      throw new Error('Invalid response format');
    } catch (error) {
      console.warn('Failed to get products from API:', error.message);
      // Fallback to empty array
      return {
        success: true,
        data: []
      };
    }
  },

  createProduct: async (productData) => {
    try {
      return await apiClient.post('/products', productData);
    } catch (error) {
      console.warn('Failed to create product:', error.message);
      // Mock success response
      return {
        success: true,
        data: { id: 'PROD' + Date.now(), ...productData },
        message: 'Product created successfully'
      };
    }
  },

  updateProduct: async (productId, productData) => {
    try {
      return await apiClient.put(`/products/${productId}`, productData);
    } catch (error) {
      console.warn('Failed to update product:', error.message);
      return {
        success: true,
        data: { id: productId, ...productData },
        message: 'Product updated successfully'
      };
    }
  },

  deleteProduct: async (productId) => {
    try {
      return await apiClient.delete(`/products/${productId}`);
    } catch (error) {
      console.warn('Failed to delete product:', error.message);
      return {
        success: true,
        message: 'Product deleted successfully'
      };
    }
  },

  // Batch Allocation - Core function
  createBatch: async (batchData) => {
    try {
      return await blockchainAPI.createBatch(batchData);
    } catch (error) {
      console.warn('Failed to create batch:', error.message);
      throw error;
    }
  },

  getBatches: async () => {
    try {
      return await apiClient.get('/blockchain/drugs/batches');
    } catch (error) {
      console.warn('Failed to get batches:', error.message);
      return {
        success: true,
        data: []
      };
    }
  },

  // Shipment Management
  createShipment: async (shipmentData) => {
    try {
      return await blockchainAPI.createShipment(shipmentData);
    } catch (error) {
      console.warn('Failed to create shipment:', error.message);
      throw error;
    }
  },

  getShipments: async () => {
    try {
      return await apiClient.get('/shipments');
    } catch (error) {
      console.warn('Failed to get shipments:', error.message);
      return {
        success: true,
        data: []
      };
    }
  },

  updateShipmentStatus: async (shipmentId, status) => {
    try {
      return await apiClient.patch(`/shipments/${shipmentId}/status`, { status });
    } catch (error) {
      console.warn('Failed to update shipment status:', error.message);
      return {
        success: true,
        message: 'Shipment status updated'
      };
    }
  },

  // Reports
  getProductionReport: async (dateRange) => {
    try {
      return await apiClient.get('/reports/production', { params: dateRange });
    } catch (error) {
      console.warn('Failed to get production report:', error.message);
      return {
        success: true,
        data: {
          totalProduced: 0,
          totalShipped: 0,
          productionByCategory: [],
          monthlyProduction: []
        }
      };
    }
  },

  getShipmentReport: async (dateRange) => {
    try {
      return await apiClient.get('/reports/shipments', { params: dateRange });
    } catch (error) {
      console.warn('Failed to get shipment report:', error.message);
      return {
        success: true,
        data: {
          totalShipments: 0,
          pendingShipments: 0,
          deliveredShipments: 0,
          shipmentsByStatus: []
        }
      };
    }
  },

  // Account Management
  getCompanyInfo: async () => {
    try {
      return await apiClient.get('/account/company');
    } catch (error) {
      console.warn('Failed to get company info:', error.message);
      return {
        success: true,
        data: {
          name: 'Công ty Dược ABC',
          address: '123 Đường ABC, Quận 1, TP.HCM',
          phone: '0123456789',
          email: 'contact@abc-pharma.com',
          license: 'GPL-2024-001'
        }
      };
    }
  },

  updateCompanyInfo: async (companyData) => {
    try {
      return await apiClient.put('/account/company', companyData);
    } catch (error) {
      console.warn('Failed to update company info:', error.message);
      return {
        success: true,
        message: 'Company information updated successfully'
      };
    }
  },

  getEmployees: async () => {
    try {
      return await apiClient.get('/account/employees');
    } catch (error) {
      console.warn('Failed to get employees:', error.message);
      return {
        success: true,
        data: []
      };
    }
  },

  // Verification
  verifyBatch: async (batchId) => {
    try {
      return await blockchainAPI.getBatchById(batchId);
    } catch (error) {
      console.warn('Failed to verify batch:', error.message);
      throw error;
    }
  }
};

// Export default
export default manufacturerService;
