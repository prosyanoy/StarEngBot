import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import ProgressBar from '@/components/ProgressBar';

function shuffle(arr) {
  const res = arr.slice();
  for (let i = res.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [res[i], res[j]] = [res[j], res[i]];
  }
  return res;
}

export default function Matching({ tasks, onFinish }) {
  const { t } = useTranslation();
  const [idx, setIdx] = useState(0);
  const [left, setLeft] = useState([]); // {id,text}
  const [right, setRight] = useState([]);
  const [selLeft, setSelLeft] = useState(null);
  const [selRight, setSelRight] = useState(null);
  const [remaining, setRemaining] = useState(0);

  const task = tasks[idx] ?? {};

  useEffect(() => {
    if (!task.pairs) return;
    const items = task.pairs.map((p, i) => ({ id: i, en: p.en, ru: p.ru }));
    setLeft(shuffle(items.map(({ id, en }) => ({ id, text: en }))));
    setRight(shuffle(items.map(({ id, ru }) => ({ id, text: ru }))));
    setRemaining(items.length);
    setSelLeft(null);
    setSelRight(null);
  }, [task]);

  const tryMatch = (leftId, rightId) => {
    if (leftId === rightId) {
      setLeft((l) => l.filter((o) => o.id !== leftId));
      setRight((r) => r.filter((o) => o.id !== rightId));
      setRemaining((n) => n - 1);
      if (remaining - 1 === 0) {
        setTimeout(() => {
          if (idx + 1 === tasks.length) onFinish();
          else setIdx((n) => n + 1);
        }, 300);
      }
    }
  };

  const handleLeft = (id) => {
    setSelLeft(id);
    if (selRight !== null) {
      tryMatch(id, selRight);
      setSelLeft(null);
      setSelRight(null);
    }
  };

  const handleRight = (id) => {
    setSelRight(id);
    if (selLeft !== null) {
      tryMatch(selLeft, id);
      setSelLeft(null);
      setSelRight(null);
    }
  };

  if (!tasks.length) return <p>{t('No tasks')}</p>;

  return (
    <div className="p-4 max-w-xs mx-auto">
      <ProgressBar value={(idx / tasks.length) * 100} className="mb-4" />
      <div className="grid grid-cols-2 gap-4">
        <div className="grid gap-2">
          {left.map((o) => (
            <button
              key={o.id}
              onClick={() => handleLeft(o.id)}
              className={`px-2 py-1 rounded ${selLeft === o.id ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              {o.text}
            </button>
          ))}
        </div>
        <div className="grid gap-2">
          {right.map((o) => (
            <button
              key={o.id}
              onClick={() => handleRight(o.id)}
              className={`px-2 py-1 rounded ${selRight === o.id ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            >
              {o.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

