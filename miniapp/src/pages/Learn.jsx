import { useParams, useNavigate } from 'react-router-dom';
import {useEffect, useRef, useState} from 'react';
import WordCard from '@/components/WordCard';
import {fetchLearning} from "@/lib/api.tsx";

export default function Learn() {
  const { collectionId } = useParams();
  const nav = useNavigate();

  const [index, setIndex] = useState(0);
  const [learnClicks, setLearnClicks] = useState(0);
  const [answered, setAnswered] = useState(0);
  const [queue, setWords] = useState([]);
  const learnIDsRef    = useRef([]);
  const knownIDsRef    = useRef([]);

  useEffect(() => {
    (async () => {
      const res = await fetchLearning(Number(collectionId));
      setWords(res);
    })();
  }, [collectionId]);

  if (!queue.length) return <p className="text-center mt-20">No cards</p>;

  const handleAnswer = (type) => {
    if (type === 'learn') {
      setLearnClicks((c) => c + 1);
      learnIDsRef.current.push(String(queue[index].id));
    } else {
      knownIDsRef.current.push(String(queue[index].id));
    }
    const next = index + 1;
    const totalAnswered = answered + 1;
    setAnswered(totalAnswered);

    if (next >= queue.length) {
      const totalLearns = learnClicks + (type==='learn' ? 1 : 0);
      if (totalLearns === 0) nav(`/results/${collectionId}`);
      else nav(`/learnflow/${collectionId}`, {
        state: { wordIds: learnIDsRef.current }
      });
      return;
    }

    if (learnClicks >= 5) {
      nav(`/translate/${id}`);
      return;
    }

    setIndex(next);
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <WordCard card={queue[index]} onAnswer={handleAnswer} />
    </div>
  );
}
