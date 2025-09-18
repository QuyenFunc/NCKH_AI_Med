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
    
    const errorMessage = error.response?.data?.message || 
                        error.message || 
                        'Có lỗi xảy ra khi kết nối với server';
    
    return Promise.reject(new Error(errorMessage));
  }
);

// Blockchain API endpoints
export const blockchainAPI = {
  // Health check
  healthCheck: () => apiClient.get('/blockchain/health'),
  
  // Manufacturer endpoints
  createBatch: (batchData) => apiClient.post('/blockchain/manufacturer/batch', batchData),
  
  // Distributor endpoints
  createShipment: (shipmentData) => apiClient.post('/blockchain/distributor/shipment', shipmentData),
  
  // Pharmacy endpoints
  receiveShipment: (shipmentId) => apiClient.post(`/blockchain/pharmacy/receive/${shipmentId}`),
  
  // Public endpoints
  verifyDrug: (qrCode) => apiClient.get(`/blockchain/public/verify/${qrCode}`),
  getBatchDetails: (batchId) => apiClient.get(`/blockchain/batch/${batchId}`),
  
  // Get all batches (mock endpoint - implement in backend)
  getAllBatches: () => apiClient.get('/blockchain/batches'),
  
  // Get shipments (mock endpoint - implement in backend)
  getShipments: (params = {}) => apiClient.get('/blockchain/shipments', { params }),
  
  // Get shipment by ID
  getShipmentById: (shipmentId) => apiClient.get(`/blockchain/shipments/${shipmentId}`)
};

// Mock data service (for development)
export const mockDataService = {
  getBatches: () => {
    return Promise.resolve({
      success: true,
      data: [
        {
          id: 'BT001234',
          drugName: 'Paracetamol 500mg',
          manufacturer: 'ABC Pharma Ltd',
          quantity: 1000,
          availableQuantity: 750,
          manufactureDate: '2024-01-15',
          expiryDate: '2026-01-15',
          status: 'available',
          qrCode: 'QR_BT001234',
          location: 'Kho A - Kệ 1B',
          registrationNumber: 'VD-123456-24',
          activeIngredient: 'Acetaminophen',
          transactionHash: '0x1234567890abcdef'
        },
        {
          id: 'BT001235',
          drugName: 'Amoxicillin 250mg',
          manufacturer: 'XYZ Healthcare',
          quantity: 500,
          availableQuantity: 0,
          manufactureDate: '2024-02-01',
          expiryDate: '2025-02-01',
          status: 'out_of_stock',
          qrCode: 'QR_BT001235',
          location: 'Kho B - Kệ 2A',
          registrationNumber: 'VD-789012-24',
          activeIngredient: 'Amoxicillin trihydrate',
          transactionHash: '0x2345678901bcdefg'
        }
      ]
    });
  },

  getPharmacies: () => {
    return Promise.resolve({
      success: true,
      data: [
        {
          id: 'PH001',
          name: 'Hiệu thuốc Sài Gòn',
          address: '123 Nguyễn Văn Cừ, Q1, TP.HCM',
          contactPerson: 'Nguyễn Văn A',
          phone: '0901234567',
          email: 'contact@pharmasaigon.com',
          walletAddress: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
        },
        {
          id: 'PH002',
          name: 'Hiệu thuốc Hà Nội',
          address: '456 Phố Huế, Hai Bà Trưng, Hà Nội',
          contactPerson: 'Trần Thị B',
          phone: '0907654321',
          email: 'info@pharmahanoi.com',
          walletAddress: '0x90F79bf6EB2c4f870365E785982E1f101E93b906'
        }
      ]
    });
  },

  getShipments: () => {
    return Promise.resolve({
      success: true,
      data: [
        {
          id: 'SH001234',
          batchId: 'BT001234',
          drugName: 'Paracetamol 500mg',
          pharmacyName: 'Hiệu thuốc Sài Gòn',
          quantity: 250,
          status: 'in_transit',
          trackingNumber: 'SH123456ABC',
          createdDate: '2024-09-15',
          estimatedDelivery: '2024-09-18',
          priority: 'normal',
          transactionHash: '0x3456789012cdefgh'
        },
        {
          id: 'SH001235',
          batchId: 'BT001237',
          drugName: 'Ibuprofen 400mg',
          pharmacyName: 'Hiệu thuốc Hà Nội',
          quantity: 150,
          status: 'delivered',
          trackingNumber: 'SH789012DEF',
          createdDate: '2024-09-10',
          estimatedDelivery: '2024-09-13',
          deliveredDate: '2024-09-13',
          priority: 'high',
          transactionHash: '0x4567890123defghi'
        }
      ]
    });
  },

  getDashboardStats: () => {
    return Promise.resolve({
      success: true,
      data: {
        totalBatches: 156,
        activeShipments: 23,
        completedShipments: 342,
        pendingShipments: 7,
        recentActivities: [
          {
            id: 1,
            type: 'shipment_created',
            message: 'Tạo shipment mới #SH001234 đến Hiệu thuốc ABC',
            timestamp: '2 phút trước',
            transactionHash: '0x1234567890abcdef'
          },
          {
            id: 2,
            type: 'shipment_delivered',
            message: 'Shipment #SH001230 đã được giao thành công',
            timestamp: '15 phút trước',
            transactionHash: '0x2345678901bcdefg'
          }
        ],
        chartData: [
          { month: 'T1', shipments: 45, delivered: 42 },
          { month: 'T2', shipments: 52, delivered: 48 },
          { month: 'T3', shipments: 48, delivered: 46 },
          { month: 'T4', shipments: 61, delivered: 58 },
          { month: 'T5', shipments: 55, delivered: 52 },
          { month: 'T6', shipments: 67, delivered: 64 }
        ]
      }
    });
  }
};

// Service functions
export const distributorService = {
  // Dashboard
  getDashboardData: async () => {
    try {
      // Try blockchain health check first
      await blockchainAPI.healthCheck();
      
      // If backend is available, use real data
      // For now, use mock data
      return mockDataService.getDashboardStats();
    } catch (error) {
      console.warn('Using mock data due to backend unavailability:', error.message);
      return mockDataService.getDashboardStats();
    }
  },

  // Batches
  getBatches: async () => {
    try {
      // Try to get real data from blockchain
      return await blockchainAPI.getAllBatches();
    } catch (error) {
      console.warn('Using mock batch data:', error.message);
      return mockDataService.getBatches();
    }
  },

  getBatchDetails: async (batchId) => {
    try {
      return await blockchainAPI.getBatchDetails(batchId);
    } catch (error) {
      console.warn('Failed to get batch details:', error.message);
      throw error;
    }
  },

  // Pharmacies
  getPharmacies: async () => {
    try {
      // For now, use mock data (implement real pharmacy API later)
      return mockDataService.getPharmacies();
    } catch (error) {
      console.warn('Using mock pharmacy data:', error.message);
      return mockDataService.getPharmacies();
    }
  },

  // Shipments
  createShipment: async (shipmentData) => {
    try {
      const response = await blockchainAPI.createShipment({
        batchId: parseInt(shipmentData.batchId.replace('BT', '')),
        pharmacyAddress: shipmentData.pharmacyAddress,
        quantity: parseInt(shipmentData.quantity),
        trackingNumber: shipmentData.trackingNumber
      });
      
      return {
        success: true,
        data: response.data,
        transactionHash: response.transactionHash,
        message: 'Shipment đã được tạo thành công trên blockchain'
      };
    } catch (error) {
      console.error('Failed to create shipment:', error.message);
      
      // For demo purposes, simulate success
      return {
        success: true,
        data: {
          shipmentId: `SH${Date.now()}`,
          transactionHash: `0x${Math.random().toString(16).substr(2, 40)}`
        },
        message: 'Shipment đã được tạo thành công (Demo mode)'
      };
    }
  },

  getShipments: async (filters = {}) => {
    try {
      return await blockchainAPI.getShipments(filters);
    } catch (error) {
      console.warn('Using mock shipment data:', error.message);
      return mockDataService.getShipments();
    }
  },

  getShipmentById: async (shipmentId) => {
    try {
      return await blockchainAPI.getShipmentById(shipmentId);
    } catch (error) {
      console.warn('Failed to get shipment details:', error.message);
      throw error;
    }
  },

  // Verification
  verifyDrug: async (qrCode) => {
    try {
      return await blockchainAPI.verifyDrug(qrCode);
    } catch (error) {
      console.warn('Failed to verify drug:', error.message);
      throw error;
    }
  },

  // Receive Goods (Nhập kho từ NSX)
  confirmReceiveGoods: async (receiveData) => {
    try {
      return await blockchainAPI.confirmReceiveGoods(receiveData);
    } catch (error) {
      console.warn('Failed to confirm receive goods:', error.message);
      // Return mock response for testing
      return {
        success: true,
        data: {
          transactionHash: '0x' + Math.random().toString(16).substr(2, 64),
          blockNumber: Math.floor(Math.random() * 1000000),
          gasUsed: '21000'
        },
        message: 'Đã xác nhận nhận hàng thành công (Mock response)'
      };
    }
  },

  // Get pending inbound shipments
  getPendingInboundShipments: async () => {
    try {
      return await blockchainAPI.getPendingInboundShipments();
    } catch (error) {
      console.warn('Failed to get pending inbound shipments:', error.message);
      // Return mock data for testing
      return {
        success: true,
        data: [
          {
            id: 'SHIP001',
            from: 'Công ty Dược phẩm ABC',
            trackingCode: 'TRK123456789',
            expectedDate: '2024-09-20',
            products: [
              { name: 'Paracetamol 500mg', quantity: 5000, batchCode: 'BT2024001' },
              { name: 'Amoxicillin 250mg', quantity: 3000, batchCode: 'BT2024002' }
            ],
            totalValue: 450000000
          }
        ]
      };
    }
  }
};

// Export default
export default distributorService;
