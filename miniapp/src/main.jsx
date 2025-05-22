import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './i18n.js';
import './index.css';
import {AuthProvider, useAuth} from "@/lib/api.tsx";
/*
function Gate() {
  const { jwt } = useAuth();
  if (!jwt) return <p>…authorising…</p>;
  return <App />;
}

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
    <AuthProvider>
      <Gate />
    </AuthProvider>
  </React.StrictMode>
);
 */

ReactDOM.createRoot(document.getElementById('root')).render(<App />);