import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  Filter,
  CheckCircle,
  XCircle,
  Eye,
  Save,
  X
} from 'lucide-react';
import manufacturerService from '../services/apiService';
import './ProductManagement.css';

const ProductManagement = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fetchingRef, setFetchingRef] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [newProduct, setNewProduct] = useState({
    name: '',
    category: '',
    dosage: '',
    unit: '',
    description: '',
    activeIngredient: '',
    storageConditions: '',
    shelfLife: '',
    status: 'active'
  });

  const categories = [
    'Giảm đau hạ sốt',
    'Kháng sinh',
    'Vitamin & Khoáng chất',
    'Thuốc tim mạch',
    'Thuốc tiêu hóa',
    'Thuốc hô hấp',
    'Thuốc da liễu',
    'Khác'
  ];

  const units = ['viên', 'ml', 'gói', 'lọ', 'ống', 'chai'];

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    // Prevent multiple simultaneous calls
    if (fetchingRef) {
      console.log('ProductManagement: Already fetching, skipping...');
      return;
    }
    
    try {
      setFetchingRef(true);
      setLoading(true);
      setError(null);
      
      console.log('ProductManagement: Starting fetchProducts...');
      
      // Fetch real data from API
      const response = await manufacturerService.getProducts();
      
      if (response.success && response.data) {
        setProducts(response.data);
      } else {
        setProducts([]);
        setError(response.message || 'Không thể tải danh sách sản phẩm');
      }
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Không thể tải danh sách sản phẩm: ' + err.message);
      setProducts([]);
    } finally {
      setLoading(false);
      setFetchingRef(false);
    }
  };

  const filteredProducts = products.filter(product => {
    const matchesSearch = 
      (product.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (product.category || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (product.activeIngredient || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || product.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  // Debug log
  console.log('ProductManagement: Render - products count:', products.length, 'filtered count:', filteredProducts.length);

  const handleAddProduct = async () => {
    try {
      // Call real API
      const response = await manufacturerService.createProduct(newProduct);
      
      if (response.success) {
        // Refresh products list
        await fetchProducts();
        setShowAddModal(false);
        setNewProduct({
          name: '',
          category: '',
          dosage: '',
          unit: '',
          description: '',
          activeIngredient: '',
          storageConditions: '',
          shelfLife: '',
          status: 'active'
        });
      } else {
        setError(response.message || 'Không thể tạo sản phẩm');
      }
    } catch (err) {
      console.error('Error adding product:', err);
      setError('Lỗi khi tạo sản phẩm: ' + err.message);
    }
  };

  const handleEditProduct = async (productId, updatedData) => {
    try {
      // Call real API
      const response = await manufacturerService.updateProduct(productId, updatedData);
      
      if (response.success) {
        // Refresh products list
        await fetchProducts();
        setEditingProduct(null);
      } else {
        setError(response.message || 'Không thể cập nhật sản phẩm');
      }
    } catch (err) {
      console.error('Error updating product:', err);
      setError('Lỗi khi cập nhật sản phẩm: ' + err.message);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa sản phẩm này?')) {
      try {
        // Call real API
        const response = await manufacturerService.deleteProduct(productId);
        
        if (response.success) {
          // Refresh products list
          await fetchProducts();
        } else {
          setError(response.message || 'Không thể xóa sản phẩm');
        }
      } catch (err) {
        console.error('Error deleting product:', err);
        setError('Lỗi khi xóa sản phẩm: ' + err.message);
      }
    }
  };

  const handleToggleStatus = async (productId, newStatus) => {
    try {
      // Find the product and update its status
      const product = products.find(p => p.id === productId);
      if (!product) return;
      
      const updatedProduct = { ...product, status: newStatus };
      const response = await manufacturerService.updateProduct(productId, updatedProduct);
      
      if (response.success) {
        // Refresh products list
        await fetchProducts();
      } else {
        setError(response.message || 'Không thể cập nhật trạng thái sản phẩm');
      }
    } catch (err) {
      console.error('Error updating product status:', err);
      setError('Lỗi khi cập nhật trạng thái: ' + err.message);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN');
  };

  if (loading) {
    return (
      <div className="product-management">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Đang tải danh sách sản phẩm...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="product-management">
      <div className="page-header">
        <h1>
          <Package className="page-icon" />
          Quản lý Dòng sản phẩm
        </h1>
        <p>Thêm, sửa, hoặc vô hiệu hóa thông tin các loại thuốc</p>
      </div>

      <div className="controls">
        <div className="search-filter">
          <div className="search-box">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Tìm kiếm theo tên sản phẩm, danh mục, hoạt chất..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="filter-box">
            <Filter className="filter-icon" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">Tất cả trạng thái</option>
              <option value="active">Đang hoạt động</option>
              <option value="inactive">Ngưng sản xuất</option>
            </select>
          </div>
        </div>

        <button 
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary add-btn"
        >
          <Plus size={16} />
          Thêm sản phẩm mới
        </button>
      </div>

      <div className="products-table">
        <table>
          <thead>
            <tr>
              <th>Mã SP</th>
              <th>Tên sản phẩm</th>
              <th>Danh mục</th>
              <th>Liều lượng</th>
              <th>Hoạt chất</th>
              <th>Trạng thái</th>
              <th>Số lô SX</th>
              <th>Tổng SL</th>
              <th>Ngày tạo</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {filteredProducts.length === 0 ? (
              <tr>
                <td colSpan="10" className="no-data">
                  <Package size={48} className="no-data-icon" />
                  <div>
                    <h4>Không có sản phẩm nào</h4>
                    <p>
                      {searchTerm || statusFilter !== 'all' 
                        ? 'Không tìm thấy sản phẩm nào phù hợp với bộ lọc.'
                        : 'Chưa có sản phẩm nào được tạo.'
                      }
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredProducts.map(product => (
                <tr key={product.id}>
                  <td className="product-id">{product.id}</td>
                  <td className="product-name">
                    <strong>{product.name}</strong>
                  </td>
                  <td className="category">{product.category}</td>
                  <td className="dosage">{product.dosage}</td>
                  <td className="ingredient">{product.activeIngredient}</td>
                  <td className="status">
                    <span className={`status-badge status-${product.status}`}>
                      {product.status === 'active' ? (
                        <>
                          <CheckCircle size={14} />
                          Hoạt động
                        </>
                      ) : (
                        <>
                          <XCircle size={14} />
                          Ngưng SX
                        </>
                      )}
                    </span>
                  </td>
                  <td className="batches">{product.totalBatches || 0}</td>
                  <td className="produced">{(product.totalProduced || 0).toLocaleString()}</td>
                  <td className="date">{product.createdAt ? formatDate(product.createdAt) : 'N/A'}</td>
                  <td className="actions">
                    <button 
                      onClick={() => setEditingProduct(product)}
                      className="action-btn edit-btn"
                      title="Chỉnh sửa"
                    >
                      <Edit size={14} />
                    </button>
                    <button 
                      onClick={() => handleToggleStatus(
                        product.id, 
                        product.status === 'active' ? 'inactive' : 'active'
                      )}
                      className={`action-btn toggle-btn ${product.status === 'active' ? 'deactivate' : 'activate'}`}
                      title={product.status === 'active' ? 'Ngưng sản xuất' : 'Kích hoạt'}
                    >
                      {product.status === 'active' ? <XCircle size={14} /> : <CheckCircle size={14} />}
                    </button>
                    <button 
                      onClick={() => handleDeleteProduct(product.id)}
                      className="action-btn delete-btn"
                      title="Xóa"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Thêm sản phẩm mới</h2>
              <button onClick={() => setShowAddModal(false)} className="close-button">×</button>
            </div>
            <div className="modal-body">
              <div className="form-grid">
                <div className="form-group">
                  <label>Tên sản phẩm *</label>
                  <input
                    type="text"
                    value={newProduct.name}
                    onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                    placeholder="VD: Paracetamol 500mg"
                  />
                </div>
                <div className="form-group">
                  <label>Danh mục *</label>
                  <select
                    value={newProduct.category}
                    onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                  >
                    <option value="">Chọn danh mục</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Liều lượng *</label>
                  <input
                    type="text"
                    value={newProduct.dosage}
                    onChange={(e) => setNewProduct({...newProduct, dosage: e.target.value})}
                    placeholder="VD: 500mg"
                  />
                </div>
                <div className="form-group">
                  <label>Đơn vị *</label>
                  <select
                    value={newProduct.unit}
                    onChange={(e) => setNewProduct({...newProduct, unit: e.target.value})}
                  >
                    <option value="">Chọn đơn vị</option>
                    {units.map(unit => (
                      <option key={unit} value={unit}>{unit}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group full-width">
                  <label>Hoạt chất *</label>
                  <input
                    type="text"
                    value={newProduct.activeIngredient}
                    onChange={(e) => setNewProduct({...newProduct, activeIngredient: e.target.value})}
                    placeholder="VD: Paracetamol"
                  />
                </div>
                <div className="form-group full-width">
                  <label>Mô tả</label>
                  <textarea
                    value={newProduct.description}
                    onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                    placeholder="Mô tả chi tiết về sản phẩm..."
                    rows="3"
                  />
                </div>
                <div className="form-group">
                  <label>Điều kiện bảo quản</label>
                  <input
                    type="text"
                    value={newProduct.storageConditions}
                    onChange={(e) => setNewProduct({...newProduct, storageConditions: e.target.value})}
                    placeholder="VD: Nơi khô ráo, tránh ánh sáng"
                  />
                </div>
                <div className="form-group">
                  <label>Hạn sử dụng</label>
                  <input
                    type="text"
                    value={newProduct.shelfLife}
                    onChange={(e) => setNewProduct({...newProduct, shelfLife: e.target.value})}
                    placeholder="VD: 36 tháng"
                  />
                </div>
              </div>
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowAddModal(false)} className="btn btn-secondary">
                Hủy
              </button>
              <button 
                onClick={handleAddProduct}
                className="btn btn-primary"
                disabled={!newProduct.name || !newProduct.category || !newProduct.dosage || !newProduct.unit || !newProduct.activeIngredient}
              >
                <Save size={16} />
                Thêm sản phẩm
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Product Modal */}
      {editingProduct && (
        <div className="modal-overlay" onClick={() => setEditingProduct(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Chỉnh sửa sản phẩm</h2>
              <button onClick={() => setEditingProduct(null)} className="close-button">×</button>
            </div>
            <div className="modal-body">
              <div className="form-grid">
                <div className="form-group">
                  <label>Tên sản phẩm *</label>
                  <input
                    type="text"
                    value={editingProduct.name}
                    onChange={(e) => setEditingProduct({...editingProduct, name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Danh mục *</label>
                  <select
                    value={editingProduct.category}
                    onChange={(e) => setEditingProduct({...editingProduct, category: e.target.value})}
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Liều lượng *</label>
                  <input
                    type="text"
                    value={editingProduct.dosage}
                    onChange={(e) => setEditingProduct({...editingProduct, dosage: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Đơn vị *</label>
                  <select
                    value={editingProduct.unit}
                    onChange={(e) => setEditingProduct({...editingProduct, unit: e.target.value})}
                  >
                    {units.map(unit => (
                      <option key={unit} value={unit}>{unit}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group full-width">
                  <label>Hoạt chất *</label>
                  <input
                    type="text"
                    value={editingProduct.activeIngredient}
                    onChange={(e) => setEditingProduct({...editingProduct, activeIngredient: e.target.value})}
                  />
                </div>
                <div className="form-group full-width">
                  <label>Mô tả</label>
                  <textarea
                    value={editingProduct.description}
                    onChange={(e) => setEditingProduct({...editingProduct, description: e.target.value})}
                    rows="3"
                  />
                </div>
                <div className="form-group">
                  <label>Điều kiện bảo quản</label>
                  <input
                    type="text"
                    value={editingProduct.storageConditions}
                    onChange={(e) => setEditingProduct({...editingProduct, storageConditions: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Hạn sử dụng</label>
                  <input
                    type="text"
                    value={editingProduct.shelfLife}
                    onChange={(e) => setEditingProduct({...editingProduct, shelfLife: e.target.value})}
                  />
                </div>
              </div>
            </div>
            <div className="modal-actions">
              <button onClick={() => setEditingProduct(null)} className="btn btn-secondary">
                Hủy
              </button>
              <button 
                onClick={() => handleEditProduct(editingProduct.id, editingProduct)}
                className="btn btn-primary"
              >
                <Save size={16} />
                Cập nhật
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductManagement;
