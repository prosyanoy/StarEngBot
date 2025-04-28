import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';

export default function CollectionCard({ collection, onLearn }) {
  const { i18n, t } = useTranslation();

  return (
    <div className="flex items-center justify-between bg-slate-50 rounded-card p-3 shadow mb-3">
      <div className="flex items-center gap-3">
        <img src={collection.icon} alt={collection.title} className="w-12 h-12 rounded-lg" />
        <div>
          <h3 className="font-semibold text-lg leading-tight">{collection.title}</h3>
          <p className="text-sm text-gray-500">
            {collection.wordsToLearn}/{collection.total} {t('toLearn')}
          </p>
        </div>
      </div>
      <Button onClick={() => onLearn(collection)} className="px-4 py-2">
        {t('learn')}
      </Button>
    </div>
  );
}