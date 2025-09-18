import React, { useState } from 'react';
import { Truck, Plus, Edit, Eye, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import './ShipmentManagement.css';

const ShipmentManagement = () => {
  const [shipments] = useState([
    {
      id: 'SH001',
      batchId: 'BT2024001',
      productName: 'Paracetamol 500mg',
      recipient: 'Nhà phân phối ABC',
      recipientType: 'distributor',
      quantity: 5000,
      status: 'delivered',
      createdDate: '2024-09-15',
      deliveredDate: '2024-09-17'
    },
    {
      id: 'SH002', 
      batchId: 'BT2024002',
      productName: 'Amoxicillin 250mg',
      recipient: 'Hiệu thuốc XYZ',
      recipientType: 'pharmacy',
      quantity: 2000,
      status: 'in_transit',
      createdDate: '2024-09-16',
      estimatedDelivery: '2024-09-19'
    }
  ]);

  return (
    <div className="shipment-management">
      <div className="page-header">
        <h1>
          <Truck className="page-icon" />
          Quản lý Xuất hàng
        </h1>
        <p>Tạo và quản lý các lệnh vận chuyển đến nhà phân phối hoặc hiệu thuốc</p>
      </div>

      <div className="shipments-table">
        <table>
          <thead>
            <tr>
              <th>Mã lô hàng</th>
              <th>Sản phẩm</th>
              <th>Người nhận</th>
              <th>Số lượng</th>
              <th>Trạng thái</th>
              <th>Ngày tạo</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {shipments.map(shipment => (
              <tr key={shipment.id}>
                <td>{shipment.id}</td>
                <td>{shipment.productName}</td>
                <td>{shipment.recipient}</td>
                <td>{shipment.quantity.toLocaleString()}</td>
                <td>
                  <span className={`status-badge status-${shipment.status}`}>
                    {shipment.status === 'delivered' ? <CheckCircle size={14} /> : <Clock size={14} />}
                    {shipment.status === 'delivered' ? 'Đã giao' : 'Đang giao'}
                  </span>
                </td>
                <td>{new Date(shipment.createdDate).toLocaleDateString('vi-VN')}</td>
                <td>
                  <button className="btn btn-outline">
                    <Eye size={14} />
                    Chi tiết
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ShipmentManagement;
