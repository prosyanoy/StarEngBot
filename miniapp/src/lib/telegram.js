// src/lib/telegram.js
export const tg = (()=>{
  if (typeof window === 'undefined') return null;
  const real = window.Telegram?.WebApp;
  if (real) return real;

  // --- mock so code keeps working in a normal browser ---
  return {
    initDataUnsafe: { user: { language_code: navigator.language.slice(0,2) }},
    ready(){},
    expand(){},
    close(){},
    // add whatever else you call later
  };
})();
