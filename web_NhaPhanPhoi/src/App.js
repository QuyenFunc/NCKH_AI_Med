import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import BatchManagement from './components/BatchManagement';
import CreateShipment from './components/CreateShipment';
import ShipmentTracking from './components/ShipmentTracking';
import Reports from './components/Reports';
import ReceiveGoods from './components/ReceiveGoods';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/receive-goods" element={<ReceiveGoods />} />
          <Route path="/batches" element={<BatchManagement />} />
          <Route path="/create-shipment" element={<CreateShipment />} />
          <Route path="/shipments" element={<ShipmentTracking />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
