import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet.jsx';
import { ListFilter } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function SortSheet({ selected, onSelect }) {
  const { t } = useTranslation();
  const options = [
    { id: 'alphabet', label: t('alphabetically') },
    { id: 'total', label: t('totalWords') },
    { id: 'learnLeft', label: t('wordsToLearn') },
  ];

  return (
    <Sheet>
      <SheetTrigger className="absolute top-4 right-4 p-2">
        <ListFilter size={24} />
      </SheetTrigger>
      <SheetContent side="bottom" className="pb-8">
        <h2 className="font-semibold text-center mb-4">{t('sort')}</h2>
        <div className="flex flex-col gap-3">
          {options.map((o) => (
            <button
              key={o.id}
              onClick={() => onSelect(o.id)}
              className={`rounded-card px-4 py-3 font-medium border text-center ${
                selected === o.id ? 'bg-telegram-primary text-white' : 'bg-slate-200 text-gray-700'
              }`}
            >
              {o.label}
            </button>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}