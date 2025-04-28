import {useState, useMemo, useEffect} from 'react';
import collectionsData from '@/data/collections';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import SortSheet from '@/components/SortSheet.jsx';

export default function Home() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const [sortBy, setSortBy] = useState('alphabet');
  const [collections, setCollections] = useState([]);

  // Detect Telegram user language on mount
  useEffect(() => {
    // fetch or load dummy
    setCollections(collectionsData);
  }, []);

  const sortedCollections = useMemo(() => {
    const list = [...collections];
    switch (sortBy) {
      case 'total':
        return list.sort((a, b) => b.total - a.total);
      case 'learnLeft':
        return list.sort((a, b) => b.wordsToLearn - a.wordsToLearn);
      default:
        return list.sort((a, b) =>
          a.title.localeCompare(b.title, 'ru')
        );
    }
  }, [collections, sortBy]);

  return (
    <div className="p-4 space-y-4 max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-2">{t('Collections')}</h1>

      {sortedCollections.map((c) => (
        <Card key={c.id} className="flex items-center gap-4 p-3">
          <img src={c.icon} alt="icon" className="w-14 h-14 rounded-xl bg-gray-100" />
          <CardContent className="flex-1">
            <h2 className="text-lg font-semibold">{c.title}</h2>
            <p className="text-gray-400 text-sm">
              {c.wordsToLearn}/{c.total} {t('to be learned')}
            </p>
          </CardContent>
          <Button
            disabled={c.wordsToLearn === 0}
            onClick={() => nav(`/learn/${c.id}`)}
          >
            {t('Learn')}
          </Button>
        </Card>
      ))}

      <SortSheet selected={sortBy} onSelect={setSortBy} />
    </div>
  );
}