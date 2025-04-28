// src/components/OptionButton.jsx
import { useEffect, useState } from 'react';
import clsx from 'clsx';

/**
 * Props
 * ──
 * text   : string  – label to display
 * state  : "normal" | "correct" | "wrong" | "disabled"
 * onClick: () => void
 *
 * When state === "wrong" the button flashes red for 1 s, then becomes disabled.
 */
export default function OptionButton({ text, state = 'normal', onClick }) {
  const [localState, setLocalState] = useState(state);

  // handle the 1-second red flash for a wrong answer
  useEffect(() => {
    if (state === 'wrong') {
      setLocalState('wrong');
      const t = setTimeout(() => setLocalState('disabled'), 1000);
      return () => clearTimeout(t);
    } else {
      setLocalState(state);
    }
  }, [state]);

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={localState === 'disabled'}
      className={clsx(
        'w-full rounded-lg py-3 text-sm font-medium transition-colors',
        {
          normal:
            'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
          correct: 'bg-green-500 text-white',
          wrong: 'bg-red-600 text-white',
          disabled: 'bg-gray-200 text-gray-400 cursor-not-allowed',
        }[localState]
      )}
    >
      {text}
    </button>
  );
}
