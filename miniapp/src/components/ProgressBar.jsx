// src/components/ProgressBar.jsx
import clsx from 'clsx';

/**
 * ProgressBar
 * ----------
 * props:
 *   value  : number  // 0-100
 *   className? : string // extra classes for the outer wrapper
 */
export default function ProgressBar({ value = 0, className = '' }) {
  const pct = Math.min(Math.max(value, 0), 100); // clamp

  return (
    <div
      className={clsx(
        'h-2 w-full rounded-full bg-gray-200 overflow-hidden',
        className
      )}
    >
      <div
        style={{ width: `${pct}%` }}
        className="h-full bg-blue-600 transition-all duration-300"
      />
    </div>
  );
}
