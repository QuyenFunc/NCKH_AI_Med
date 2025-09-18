import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import ProductManagement from './components/ProductManagement';
import BatchAllocation from './components/BatchAllocation';
import ShipmentManagement from './components/ShipmentManagement';
import Reports from './components/Reports';
import AccountManagement from './components/AccountManagement';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/products" element={<ProductManagement />} />
          <Route path="/batch-allocation" element={<BatchAllocation />} />
          <Route path="/shipments" element={<ShipmentManagement />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/account" element={<AccountManagement />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
