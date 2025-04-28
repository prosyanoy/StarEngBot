import { useParams, useNavigate } from 'react-router-dom';
import learning from '@/data/learning';
import { useState } from 'react';
import WordCard from '@/components/WordCard';

export default function Learn() {
  const { collectionId } = useParams();
  const queue = learning[collectionId] ?? [];
  const nav = useNavigate();

  const [index, setIndex] = useState(0);
  const [learnClicks, setLearnClicks] = useState(0);
  const [answered, setAnswered] = useState(0);

  const learnWords = [];
  const knownWords = [];

  if (!queue.length) return <p className="text-center mt-20">No cards</p>;

  const handleAnswer = (type) => {
    if (type === 'learn') setLearnClicks((c) => c + 1);
    const next = index + 1;
    const totalAnswered = answered + 1;
    setAnswered(totalAnswered);

    if (next >= queue.length) {
      const totalLearns = learnClicks + (type==='learn'?1:0);
      if (totalLearns === 0) nav(`/results/${collectionId}`);
      else nav(`/translate/${collectionId}`);
      return;
    }

    if (learnClicks + (type === 'learn' ? 1 : 0) >= 5) {
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
