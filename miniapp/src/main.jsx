import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import App from './App.jsx';
import './i18n.js';
import './index.css';
import { AuthProvider } from '@/lib/api';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter basename="/stareng">
    <AuthProvider>
      <App />
    </AuthProvider>
  </BrowserRouter>
);
