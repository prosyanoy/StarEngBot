import {useState, useMemo, useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import CollectionCard from '@/components/CollectionCard';
import SortSheet from '@/components/SortSheet';
import {fetchCollections, useAuth} from "@/lib/api";

export default function Home() {
  const { loading: authLoading, isAuthed } = useAuth();
  const { t, i18n } = useTranslation();
  const navigate    = useNavigate();

  const [sortBy, setSortBy] = useState('alphabet');
  const [data, setData]   = useState([]);
  const [err, setErr]    = useState(null);

  /* ─── fetch once we’re authenticated ───────────────────────────── */
  useEffect(() => {
  // console.log('Auth state:', authLoading, isAuthed);
  if (authLoading || !isAuthed) return;

  fetchCollections()
    .then((res) => {
      // console.log('Fetched collections:', res);
      setData(res);
      // console.log('🗄️ cols after setCols:', data);
    })
    .catch(e => {
      // console.error('Fetch error:', e);
      setErr(e);
    });
}, [authLoading, isAuthed]);

  const sorted = useMemo(() => {
    const list = [...data];

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
  }, [data, sortBy]);

  /* ───────── click handler ───────── */
  const handleAction = (collection, mode) => {
    if (mode === 'repeat') {
      navigate(`/learnflow/${collection.id}?mode=repeat`);
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
          emoji={col.icon}
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
