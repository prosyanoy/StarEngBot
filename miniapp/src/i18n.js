import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

export const resources = {
  en: {
    translation: {
      Collections: 'Collections',
      Learn: 'Learn',
      Known: 'Known',
      Alphabetically: 'Alphabetically',
      'Number of words': 'Number of words',
      'Number of words to learn': 'Number of words to learn',
      'All words in this collection are learned!':
        'All words in this collection are learned!',
      Results: 'Results',
      'No cards left': 'No cards left',
      'Choose correct translation': 'Choose correct translation',
      'Correct!': 'Correct!',
      Skip: 'Skip',
      'to be learned': 'to be learned',
      Sort: 'Sort'
    },
  },
  ru: {
    translation: {
      Collections: 'Коллекции',
      Learn: 'Учить',
      Known: 'Знаю',
      Alphabetically: 'По алфавиту',
      'Number of words': 'По количеству слов',
      'Number of words to learn': 'По количеству слов к изучению',
      'All words in this collection are learned!':
        'Все слова в этой коллекции выучены!',
      Results: 'Результаты',
      'No cards left': 'Слова закончились',
      'Choose correct translation': 'Выберите правильный перевод',
      'Correct!': 'Верно!',
      Skip: 'Пропустить',
      'to be learned': 'к изучению',
      Sort: 'Сортировать'
    },
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: 'en',
  interpolation: { escapeValue: false },
});
export default i18n;