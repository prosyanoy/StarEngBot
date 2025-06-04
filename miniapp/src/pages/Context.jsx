import { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import ProgressBar from '@/components/ProgressBar';
import OptionButton from '@/components/OptionButton';

function shuffle(arr) {
  const res = arr.slice();
  for (let i = res.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [res[i], res[j]] = [res[j], res[i]];
  }
  return res;
}

export default function Context({ tasks, onFinish }) {
  const { t } = useTranslation();
  const [idx, setIdx] = useState(0);
  const [options, setOptions] = useState([]);
  const [picked, setPicked] = useState([]);
  const [wrong, setWrong] = useState(null);

  const task = tasks[idx] ?? {};
  const words = useMemo(() => (task.en ? task.en.split(' ') : []), [task]);

  useEffect(() => {
    setOptions(shuffle(words));
    setPicked([]);
    setWrong(null);
  }, [words]);

  const handle = (w, i) => {
    if (w === words[picked.length]) {
      setPicked([...picked, w]);
      setOptions((o) => o.filter((_, j) => j !== i));
      if (picked.length + 1 === words.length) {
        setTimeout(() => {
          if (idx + 1 === tasks.length) onFinish();
          else setIdx((n) => n + 1);
        }, 500);
      }
    } else {
      setWrong(i);
      setTimeout(() => setWrong(null), 500);
    }
  };

  if (!tasks.length) return <p>{t('No tasks')}</p>;

  return (
    <div className="p-4 max-w-xs mx-auto">
      <ProgressBar value={(idx / tasks.length) * 100} className="mb-4" />
      <h2 className="mb-4 text-center">{task.ru}</h2>
      <p className="min-h-6 mb-4 text-center font-semibold">{picked.join(' ')}</p>
      <div className="grid grid-cols-2 gap-2">
        {options.map((w, i) => (
          <OptionButton
            key={i}
            text={w}
            state={wrong === i ? 'wrong' : 'normal'}
            onClick={() => handle(w, i)}
          />
        ))}
      </div>
    </div>
  );
}

