import { useState } from 'react';
import { distanceOne } from '@/lib/stringScore';
import { useTranslation } from 'react-i18next';
import ProgressBar from '@/components/ProgressBar';

export default function Spelling({ tasks, onFinish }) {
  // tasks: array of { id, kind:'spelling', en, ru, mistakes }
  const { t } = useTranslation();
  const [idx, setIdx] = useState(0);
  const [feedback, setFB] = useState(null);
  const [input, setInp] = useState('');
  const [score, setScore] = useState(0);
  const [reveal, setReveal] = useState(false);

  console.log("tasks", tasks);
  const task = tasks[idx];

  const handle = () => {
    const dist = distanceOne(task.en.toLowerCase(), input.trim().toLowerCase());
    const add =
      dist === 0
        ? 3
        : dist === 1 && task.mistakes === 1
        ? 1 // 1/3 of 3%
        : 0;
    const newScore = score + add;
    setScore(newScore);
    setInp('');
    setFB(add ? 'correct' : 'wrong');
    setReveal(true);
    setTimeout(() => {
      setFB(null);
      setReveal(false);
      if (idx + 1 === tasks.length) onFinish(newScore);
      else setIdx((i) => i + 1);
    }, 1000);
  };

  return (
    <div className="p-4 max-w-xs mx-auto relative flex flex-col min-h-screen">
      {feedback && (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-3xl font-bold text-white bg-black/60 z-10">
          <p>{feedback === 'correct' ? t('Correct') : t('Wrong')}</p>
          {reveal && <p className="text-base mt-2">{task.en}</p>}
        </div>
      )}
      <ProgressBar value={(idx / tasks.length) * 100} className="mb-4" />
      <p className="mb-2">{t('Translate')} — <b>{task.ru}</b></p>
      <input
        className="border w-full p-2 rounded mb-3"
        value={input}
        onChange={(e) => setInp(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handle()}
        autoFocus
      />
      <div className="mt-auto">
        <button className="w-full bg-blue-600 text-white py-2 rounded" onClick={handle}>
          {t('Submit')}
        </button>
      </div>
    </div>
  );
}
