// src/pages/Results.jsx
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export default function Results() {
  const { id }   = useParams();
  const { state }= useLocation();   // expect { scorePercent: number }
  const { t }    = useTranslation();
  const navigate = useNavigate();

  const pct = state?.scorePercent ?? 0;

  return (
    <div className="p-6 text-center">
      <h1 className="text-4xl font-bold mb-6">{t('Result')}</h1>
      <p className="text-3xl mb-10">{pct.toFixed(1)} %</p>
      <button
        onClick={() => { navigate('/'); window.location.reload(); }}
        className="bg-blue-600 text-white px-6 py-3 rounded"
      >
        {t('Back to collections')}
      </button>
    </div>
  );
}
