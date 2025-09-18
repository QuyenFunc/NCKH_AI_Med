import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import ReceiveGoods from './components/ReceiveGoods';
import InventoryManagement from './components/InventoryManagement';
import CounterVerification from './components/CounterVerification';
import Reports from './components/Reports';
import AccountManagement from './components/AccountManagement';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/receive-goods" element={<ReceiveGoods />} />
          <Route path="/inventory" element={<InventoryManagement />} />
          <Route path="/verification" element={<CounterVerification />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/account" element={<AccountManagement />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;