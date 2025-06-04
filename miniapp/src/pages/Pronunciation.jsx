import {useState, useRef, useMemo} from 'react';
import { useTranslation } from 'react-i18next';
import ProgressBar from '@/components/ProgressBar';
import { postPronunciation } from '@/lib/api';


export default function Pronunciation({ tasks, onFinish }) {
  const { t } = useTranslation();
  const decorated = useMemo(
     () => tasks.map(t => ({ ...t, showRu: Math.random() < 0.5 })),
     [tasks]
  );
  const [idx, setIdx]   = useState(0);
  const [score, setScore]= useState(0);
  const [recording,setRec]=useState(false);
  const [fb, setFb]      = useState(null);   // banner
  const mediaRef = useRef(null);

  const task = decorated[idx] ?? {};

  const startRec = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio:true });
    const rec = new MediaRecorder(stream);
    mediaRef.current = rec;
    const chunks = [];
    rec.ondataavailable = e => chunks.push(e.data);
    rec.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/webm' });
      try {
        const { ok, points } = await postPronunciation(task.id, task.en, blob);
        nextTask(ok ? points : 0);
      } catch (e) {
        nextTask(0);
      }
    };

    rec.start();
    setRec(true);
  };

  const stopRec = () => {
    mediaRef.current?.stop();
    setRec(false);
  };

  const nextTask = (points) => {
    const newScore = score + points;
    setScore(newScore);
    setFb(points ? 'correct' : 'wrong');
    setTimeout(() => {
      setFb(null);
      if (idx + 1 === decorated.length) onFinish(newScore);
      else setIdx((i) => i + 1);
    }, 1000);
  };


  return (
  <div className="p-4 max-w-xs mx-auto relative">
    {fb && (
      <div className="absolute inset-0 flex items-center justify-center text-3xl font-bold
                      text-white bg-black/60 z-10">
        {fb === 'correct' ? t('Correct') : t('Wrong')}
      </div>
    )}

    <ProgressBar value={(idx / decorated.length) * 100} className="mb-4" />

    {/* random language per task */}
    {Math.round(Math.random()) ? (
      <>
        <h2 className="text-xl font-semibold mb-2">{task.ru}</h2>
        <p className="text-gray-500 mb-6">{task.en}</p>
      </>
    ) : (
      <>
        <h2 className="text-xl font-semibold mb-2">{task.en}</h2>
        <p className="text-gray-500 mb-6">{task.ru}</p>
      </>
    )}
      {!recording ? (
        <button className="w-full bg-blue-600 text-white py-2 rounded" onClick={startRec}>
          🎙️ {t('Record')}
        </button>
      ) : (
        <button className="w-full bg-red-600 text-white py-2 rounded" onClick={stopRec}>
          ⏹️ {t('Stop')}
        </button>
      )}
    </div>
  );
}
