import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './i18n.js';
import './index.css';
import { AuthProvider } from '@/lib/api';
import {BrowserRouter} from "react-router-dom";

ReactDOM.createRoot(document.getElementById('root')).render(
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
);