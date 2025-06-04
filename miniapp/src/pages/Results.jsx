// src/pages/Results.jsx
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useEffect } from 'react';
import { postSpacedRepeat } from '@/lib/api';

export default function Results() {
  const { id }   = useParams();
  const { state }= useLocation();   // expect { scorePercent, breakdown, words }
  const { t }    = useTranslation();
  const navigate = useNavigate();

  const pct = state?.scorePercent ?? 0;
  const breakdown = state?.breakdown ?? {};
  const words = state?.words ?? [];

  useEffect(() => {
    if (!words.length) return;
    const results = words.map((w) => ({ word: w, score: pct }));
    postSpacedRepeat(id, results).catch(() => {});
  }, [words, pct, id]);

  return (
    <div className="p-6 text-center">
      <h1 className="text-4xl font-bold mb-6">{t('Result')}</h1>
      <p className="text-3xl mb-6">{pct.toFixed(1)} %</p>

      <ul className="text-left mb-8 inline-block">
        <li>Translation: {(breakdown.translation ?? 0).toFixed(1)} %</li>
        <li>Spelling + Pronunciation: {(breakdown.spellingPron ?? 0).toFixed(1)} %</li>
        <li>Context: {(breakdown.context ?? 0).toFixed(1)} %</li>
        <li>Matching: {(breakdown.matching ?? 0).toFixed(1)} %</li>
      </ul>

      {words.map((w) => (
        <div key={w} className="mb-4">
          <h3 className="font-semibold">{w}</h3>
          <ul className="text-left inline-block">
            <li>Translation: {(breakdown.translation ?? 0).toFixed(1)} %</li>
            <li>Spelling + Pronunciation: {(breakdown.spellingPron ?? 0).toFixed(1)} %</li>
            <li>Context: {(breakdown.context ?? 0).toFixed(1)} %</li>
            <li>Matching: {(breakdown.matching ?? 0).toFixed(1)} %</li>
          </ul>
        </div>
      ))}

      <button
        onClick={() => {
          navigate('//');
          window.location.reload();
        }}
        className="bg-blue-600 text-white px-6 py-3 rounded"
      >
        {t('Back to collections')}
      </button>
    </div>
  );
}
