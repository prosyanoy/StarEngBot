// src/pages/Home.jsx
import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import collections from '@/data/collections';      // array of { id, icon, title, total, wordsToLearn, wordsToRepeat }
import CollectionCard from '@/components/CollectionCard';
import SortSheet from '@/components/SortSheet';

export default function Home() {
  const { i18n } = useTranslation();
  const navigate = useNavigate();

  /* ───────── sorting state ───────── */
  const [sortBy, setSortBy] = useState('alphabet'); // "alphabet" | "total" | "learnLeft"

  const sorted = useMemo(() => {
    const list = [...collections];

    switch (sortBy) {
      case 'total':
        return list.sort((a, b) => b.total - a.total);

      case 'learnLeft':
        // combine learn+repeat to decide “words left” for a fair ranking
        return list.sort(
          (a, b) =>
            (b.wordsToLearn + b.wordsToRepeat) -
            (a.wordsToLearn + a.wordsToRepeat)
        );

      case 'alphabet':
      default:
        return list.sort((a, b) =>
          (a.title).localeCompare(b.title, undefined, { sensitivity: 'base' })
        );
    }
  }, [sortBy]);

  /* ───────── click handler ───────── */
  const handleAction = (collection, mode) => {
    if (mode === 'repeat') {
      navigate(`/translate/${collection.id}?mode=repeat`);
    } else {
      navigate(`/learn/${collection.id}`);
    }
  };

  /* ───────── render ───────── */
  return (
    <div className="px-4 pt-6 max-w-lg mx-auto relative">
      <h1 className="text-4xl font-extrabold mb-6">
        {i18n.t('Collections')}
      </h1>

      {sorted.map(col => (
        <CollectionCard
          key={col.id}
          title={col.title}
          icon={col.icon}
          learnLeft={col.wordsToLearn}
          repeatLeft={col.wordsToRepeat}
          total={col.total}
          onAction={mode => handleAction(col, mode)}
        />
      ))}

      {/* floating bottom-sheet with 3 sort options */}
      <SortSheet selected={sortBy} onSelect={setSortBy} />
    </div>
  );
}
