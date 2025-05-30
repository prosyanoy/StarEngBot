import { useState } from 'react';
import { distanceOne } from '@/lib/stringScore';
import { useTranslation } from 'react-i18next';
import ProgressBar from '@/components/ProgressBar';

export default function Spelling({ tasks, onFinish }) {
  // tasks: array of { id, kind:'spelling', en, ru, mistakes }
  const { t }       = useTranslation();
  const [idx, setIdx]     = useState(0);
  const [feedback, setFB] = useState(null);
  const [input, setInp]   = useState('');
  const [score, setScore] = useState(0);

  console.log("tasks", tasks);
  const task = tasks[idx];

  const handle = () => {
    const dist = distanceOne(task.en.toLowerCase(), input.trim().toLowerCase());
    const add  = dist === 0 ? 3
              : dist === 1 && task.mistakes === 1 ? 1   // 1/3 of 3%
              : 0;
    setScore(s => s + add);
    setInp('');
    setFB(add ? 'correct' : 'wrong');        // ← show banner
    setTimeout(() => {
      setFB(null);
      if (idx + 1 === tasks.length) onFinish(score + add);
      else setIdx(i => i + 1);
    }, 1000);
  };

  return (
    <div className="p-4 max-w-xs mx-auto relative">
        {feedback && (
       <div className="absolute inset-0 flex items-center justify-center text-3xl font-bold
                       text-white bg-black/60 z-10">
         {feedback === 'correct' ? t('Correct') : t('Wrong')}
       </div>
     )}
      <ProgressBar value={(idx / tasks.length) * 100} className="mb-4" />
      <p className="mb-2">{t('Translate')} — <b>{task.ru}</b></p>
      <input
        className="border w-full p-2 rounded mb-3"
        value={input}
        onChange={e => setInp(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && handle()}
        autoFocus
      />
      <button className="w-full bg-blue-600 text-white py-2 rounded" onClick={handle}>
        {t('Submit')}
      </button>
    </div>
  );
}
