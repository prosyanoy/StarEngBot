// src/pages/Translation.jsx
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import translationData from '@/data/translation';      // ← the object you pasted
import OptionButton   from '@/components/OptionButton';
import ProgressBar    from '@/components/ProgressBar';

export default function Translation() {
  const { id }   = useParams();          // "1"
  const nav      = useNavigate();
  const { t }    = useTranslation();

  /* ───── tasks for this collection ───── */
  const tasks = translationData[id] ?? [];
  if (tasks.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="mb-4">{t('No translation tasks')}</p>
        <button className="text-blue-600 underline" onClick={()=>nav('/')}>
          {t('Back')}
        </button>
      </div>
    );
  }

  /* ───── local state ───── */
  const [idx, setIdx]           = useState(0);           // which task
  const [attempts, setAtt]      = useState(tasks[0].attempts);
  const [reveal, setReveal]     = useState(false);       // show correct = true
  const [wrongIdx, setWrong]    = useState(null);        // index flashing red
  const [disabled, setDis]      = useState([]);          // wrong options so far
  const [progress, setProg]     = useState(0);

  const task = tasks[idx];

  /* ───── move to next task ───── */
  const nextTask = () => {
    const next = idx + 1;
    if (next >= tasks.length) return nav(`/results/${id}`);

    setIdx(next);
    setProg(p => p + 3);
    setAtt(tasks[next].attempts);
    setReveal(false);
    setWrong(null);
    setDis([]);
  };

  /* ───── click handler ───── */
  const onPick = (i) => {
    if (reveal || wrongIdx !== null) return;             // ignore during flash / reveal

    const isCorrect = i === task.correct;

    if (isCorrect) {
      setReveal(true);
      setTimeout(nextTask, 1000);
    } else {
      setWrong(i);                                       // turn red
      if (attempts > 1) {
        setTimeout(() => {
          setDis(d => [...d, i]);                        // permanently mute wrong btn
          setWrong(null);
          setAtt(a => a - 1);
        }, 1000);
      } else {
        // no attempts left → show correct then advance
        setTimeout(() => {
          setReveal(true);
          setWrong(null);
          setTimeout(nextTask, 1000);
        }, 1000);
      }
    }
  };

  /* ───── option button state helper ───── */
  const stateFor = (i) => {
    if (reveal)             return i === task.correct ? 'correct' : 'disabled';
    if (i === wrongIdx)     return 'wrong';
    if (disabled.includes(i)) return 'disabled';
    return 'normal';
  };

  /* ───── UI ───── */
  return (
    <div className="p-4 flex flex-col items-center max-w-xs mx-auto">

      <button className="self-end text-2xl" onClick={()=>nav('/')}>×</button>

      <ProgressBar value={progress} className="w-full mb-4" />
      <h2 className="text-sm text-center mb-6 font-medium">
        {t('Choose correct translation')}
      </h2>

      {/* prompt */}
      {task.type === 'audio-ru' ? (
        <audio key={task.id} src={task.audio} autoPlay controls className="mb-6" />
      ) : (
        <h1 className="text-3xl font-bold mb-6">{task.word}</h1>
      )}

      {/* variants */}
      <div className="grid gap-3 w-full">
        {task.variants.map((v, i) => (
          <OptionButton
            key={i}
            text={
              reveal && i === task.correct
                ? t('Correct')
                : v
            }
            state={stateFor(i)}
            onClick={() => onPick(i)}
          />
        ))}
      </div>

      {/* Skip appears after at least one wrong click & attempts remain */}
      {attempts < task.attempts && !reveal && (
        <button
          className="text-blue-600 mt-5 text-sm"
          onClick={nextTask}
        >
          {t('Skip')}
        </button>
      )}
    </div>
  );
}