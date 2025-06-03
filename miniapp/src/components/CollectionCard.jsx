import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';

export default function CollectionCard({
  title,
  emoji,
  learnLeft,
  repeatLeft,
  total,
  onAction,     // receives "learn" | "repeat"
}) {
  const { t } = useTranslation();
  const isRepeat = repeatLeft > 0;

  const renderEmoji = () => {
    if (!emoji) return '📚'; // default book emoji
    const match = emoji.match(/^&#(\d+);$/);
    if (match) {
      return String.fromCodePoint(Number(match[1]));
    }
    return emoji;
  };

  return (
    <div className="flex items-center gap-4 py-3">
      <div className="w-16 h-16 flex items-center justify-center text-4xl">
        {renderEmoji()}
      </div>

      <div className="flex-1">
        <h3 className="text-lg font-medium">{title}</h3>
        <p className="text-gray-500 text-sm">
          {isRepeat
            ? `${repeatLeft}/${total} ${t('to be repeated')}`
            : `${learnLeft}/${total} ${t('to be learned')}`}
        </p>
      </div>

      <Button
        onClick={() => onAction(isRepeat ? 'repeat' : 'learn')}
        disabled={!isRepeat && learnLeft === 0}
      >
        {isRepeat ? t('Repeat') : t('Learn')}
      </Button>
    </div>
  );
}
