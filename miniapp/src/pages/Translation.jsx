import {useEffect, useMemo, useRef, useState} from 'react';
import {useSearchParams, useLocation, useNavigate, useParams} from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import OptionButton   from '@/components/OptionButton';
import ProgressBar    from '@/components/ProgressBar';

export default function Translation({tasks, onFinish}) {
  const nav      = useNavigate();
  const { t }    = useTranslation();

  const [score, setScore] = useState(0);          // 0-30 %

  /* ───── local state ───── */
  const [idx, setIdx]           = useState(0);           // which task
  const [attempts, setAtt]      = useState(0);
  const [reveal, setReveal]     = useState(false);       // show correct = true
  const [wrongIdx, setWrong]    = useState(null);        // index flashing red
  const [disabled, setDis]      = useState([]);          // wrong options so far
  const [progress, setProg]     = useState(0);

  // ─── ensure attempts sync with the current task ────────────────────
  useEffect(() => {
    if (tasks.length) {
      setAtt(tasks[0].attempts ?? 1);
    }
  }, [tasks]);

  console.log("tasks", tasks);
  // ─── current task (safe even if tasks is empty) ────────────────────
  const task = tasks[idx] ?? {};

  // ─── audio player ref & effect (always run) ────────────────────────
  const playerRef = useRef(null);

  useEffect(() => {
    if (
      task.kind !== 'translation' ||
      task.type  !== 'audio-ru'   ||
      !task.audio
    ) {
      return;
    }

    playerRef.current?.pause();
    const player = new Audio(task.audio);
    playerRef.current = player;
    player.play().catch(()=>{});

    return () => {
      playerRef.current?.pause();
      playerRef.current = null;
    };
  }, [task]);

  if (tasks.length === 0) return <p>No tasks</p>;

  const replayAudio = () => playerRef.current?.play();

  /* ───── move to next task ───── */
  const nextTask = () => {
    const next = idx + 1;
    if (next >= tasks.length) return onFinish();

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
      const perTask = 3 * (10 / tasks.length);      // 3% scaled
      setScore(s => s + perTask);
    }
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
        <button
          onClick={replayAudio}
          className="mb-6 px-6 py-3 rounded-full bg-blue-600 text-white font-medium active:bg-blue-700"
        >
          🔊 {t('Play')}
        </button>
      ) : (
        <h1 className="text-3xl font-bold mb-6">{task.word}</h1>
      )}

      <p className="text-xs text-gray-500 mb-2">
        {t('Score')}: {score.toFixed(1)} %
      </p>

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