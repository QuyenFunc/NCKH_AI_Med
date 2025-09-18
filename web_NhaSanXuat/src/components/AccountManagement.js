import React, { useState } from 'react';
import { Users, Building, Edit, Save } from 'lucide-react';
import './AccountManagement.css';

const AccountManagement = () => {
  const [companyInfo, setCompanyInfo] = useState({
    name: 'Công ty Dược phẩm ABC',
    address: '123 Đường ABC, Quận 1, TP.HCM',
    phone: '0123456789',
    email: 'contact@abc-pharma.com',
    license: 'GPL-2024-001',
    website: 'https://abc-pharma.com'
  });

  const [employees] = useState([
    {
      id: 1,
      name: 'Nguyễn Văn A',
      position: 'Giám đốc Sản xuất',
      email: 'a.nguyen@abc-pharma.com',
      role: 'admin',
      status: 'active'
    },
    {
      id: 2,
      name: 'Trần Thị B',
      position: 'Quản lý Chất lượng',
      email: 'b.tran@abc-pharma.com',
      role: 'manager',
      status: 'active'
    }
  ]);

  const [isEditingCompany, setIsEditingCompany] = useState(false);

  const handleSaveCompany = () => {
    setIsEditingCompany(false);
    // API call to update company info
  };

  return (
    <div className="account-management">
      <div className="page-header">
        <h1>
          <Users className="page-icon" />
          Quản lý Tài khoản
        </h1>
        <p>Cập nhật thông tin công ty và quản lý tài khoản nhân viên</p>
      </div>

      {/* Company Information */}
      <div className="section-card">
        <div className="section-header">
          <h3>
            <Building size={24} />
            Thông tin Công ty
          </h3>
          <button 
            onClick={() => isEditingCompany ? handleSaveCompany() : setIsEditingCompany(true)}
            className="btn btn-primary"
          >
            {isEditingCompany ? <Save size={16} /> : <Edit size={16} />}
            {isEditingCompany ? 'Lưu' : 'Chỉnh sửa'}
          </button>
        </div>

        <div className="company-form">
          <div className="form-row">
            <div className="form-group">
              <label>Tên công ty</label>
              <input
                type="text"
                value={companyInfo.name}
                onChange={(e) => setCompanyInfo({...companyInfo, name: e.target.value})}
                disabled={!isEditingCompany}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Số giấy phép</label>
              <input
                type="text"
                value={companyInfo.license}
                onChange={(e) => setCompanyInfo({...companyInfo, license: e.target.value})}
                disabled={!isEditingCompany}
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Địa chỉ</label>
            <input
              type="text"
              value={companyInfo.address}
              onChange={(e) => setCompanyInfo({...companyInfo, address: e.target.value})}
              disabled={!isEditingCompany}
              className="form-input"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Số điện thoại</label>
              <input
                type="tel"
                value={companyInfo.phone}
                onChange={(e) => setCompanyInfo({...companyInfo, phone: e.target.value})}
                disabled={!isEditingCompany}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={companyInfo.email}
                onChange={(e) => setCompanyInfo({...companyInfo, email: e.target.value})}
                disabled={!isEditingCompany}
                className="form-input"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Employees */}
      <div className="section-card">
        <div className="section-header">
          <h3>
            <Users size={24} />
            Nhân viên ({employees.length})
          </h3>
        </div>

        <div className="employees-table">
          <table>
            <thead>
              <tr>
                <th>Họ tên</th>
                <th>Chức vụ</th>
                <th>Email</th>
                <th>Vai trò</th>
                <th>Trạng thái</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(employee => (
                <tr key={employee.id}>
                  <td className="employee-name">{employee.name}</td>
                  <td>{employee.position}</td>
                  <td>{employee.email}</td>
                  <td>
                    <span className={`role-badge role-${employee.role}`}>
                      {employee.role === 'admin' ? 'Quản trị' : 'Nhân viên'}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge status-${employee.status}`}>
                      {employee.status === 'active' ? 'Hoạt động' : 'Tạm khóa'}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-outline">
                      <Edit size={14} />
                      Sửa
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AccountManagement;
