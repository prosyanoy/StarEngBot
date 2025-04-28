import { motion } from 'framer-motion';
import {useEffect, useState} from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import clsx from 'clsx';

export default function WordCard({ card, onAnswer }) {
  const { t } = useTranslation();
  const [flipped, setFlipped] = useState(false);

  useEffect(()=> setFlipped(false), [card.id]);

  // helper to shorten markup
  const faceCls =
    'absolute inset-0 flex flex-col items-center justify-start overflow-y-auto p-6 [backface-visibility:hidden]';

  return (
    <motion.div
      className="relative w-full h-full [transform-style:preserve-3d] cursor-pointer select-none"
      initial={false}
      animate={{ rotateY: flipped ? 180 : 0 }}
      transition={{ duration: flipped ? 0.6 : 0, ease: 'easeInOut' }}
      onClick={() => setFlipped(!flipped)}
    >
      {/* ─── FRONT – EN word + IPA ───────────────────────────── */}
      <div className={clsx(faceCls, 'bg-white rounded-2xl')}>
        <h2 className="text-4xl font-extrabold mb-2">{card.en}</h2>
        {card.transcription && (
          <p className="text-xl text-gray-500">{card.transcription}</p>
        )}
      </div>

      {/* ─── BACK – RU word + contexts + buttons ─────────────── */}
      <div
        className={clsx(
          faceCls,
          'rotate-y-180 bg-white rounded-2xl'
        )}
        // clicking inside back shouldn’t flip again; parent handles click
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-3xl font-semibold mb-4">{card.ru}</h2>

        {(card.contexts ?? []).map((c, i) => (
          <p key={i} className="mb-3 leading-snug text-left w-full">
            <span className="font-medium">{c.en}</span>
            <br />
            {c.ru}
          </p>
        ))}

        <div className="grid grid-cols-2 gap-3 w-full mt-auto pt-6">
          <Button
            variant="ghost"
            className="w-full"
            onClick={() => onAnswer('known')}
          >
            {t('Known')}
          </Button>
          <Button className="w-full" onClick={() => onAnswer('learn')}>
            {t('Learn')}
          </Button>
        </div>
      </div>
    </motion.div>
  );
}