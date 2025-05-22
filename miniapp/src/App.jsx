import { useState, useEffect } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/i18n';
import { tg } from '@/lib/telegram';
import Home from '@/pages/Home';
import Learn from '@/pages/Learn';
import Translation from '@/pages/Translation';
import Results from '@/pages/Results.jsx';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

export default function App() {
  const [lang, setLang] = useState('en');

  useEffect(() => {
    const userLang = tg?.initDataUnsafe?.user?.language_code ?? navigator.language;
    const short = userLang.slice(0, 2);
    const chosen = short === 'ru' ? 'ru' : 'en';
    i18n.changeLanguage(chosen);
    setLang(chosen);
  }, []);

  return (
    <I18nextProvider i18n={i18n}>
      <BrowserRouter>
        <Routes>
          <Route index element={<Home lang={lang} />} />
          <Route path="/learn/:collectionId" element={<Learn />} />
          <Route path="/translate/:id" element={<Translation />} />
          <Route path="/results/:id"   element={<Results />} />
        </Routes>
      </BrowserRouter>
    </I18nextProvider>
  );
}