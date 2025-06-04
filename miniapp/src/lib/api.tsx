// src/lib/api.tsx
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react';
import axios, { AxiosInstance } from 'axios';

/* ------------------------------------------------------------------ */
/* 1. Axios instance + JWT plumbing                                   */
/* ------------------------------------------------------------------ */
const API_ROOT = "https://stdio.bot/stareng/api";
// const API_ROOT = "http://localhost:8000";

const api: AxiosInstance = axios.create({ baseURL: API_ROOT });
let jwt: string | null = null;

const setJWT = (token: string | null) => {
  jwt = token;
};

api.interceptors.request.use((cfg) => {
  if (jwt) cfg.headers.Authorization = `Bearer ${jwt}`;
  return cfg;
});

/* ------------------------------------------------------------------ */
/* 2. Auth context                                                    */
/* ------------------------------------------------------------------ */
interface AuthCtxShape {
  jwt: string | null;
  loading: boolean;
  isAuthed: boolean;
  signIn(initData: string): Promise<void>;
}

const AuthCtx = createContext<AuthCtxShape>({
  jwt: null,
  loading: true,
  isAuthed: false,
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  signIn: async () => {},
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [jwtState, setJwtState] = useState<string | null>(null);
  const [loading, setLoading]   = useState(true);

  const signIn = async (initData: string) => {
    try {
      const res = await api.post<{ access_token: string }>('/auth/', { initData });
      setJwtState(res.data.access_token);
      setJWT(res.data.access_token);
    } finally {
      setLoading(false);
    }
  };

  /* automatic login on mount */
  useEffect(() => {
    //const initData = (window as any).Telegram?.WebApp?.initData;
    if (window.Telegram && window.Telegram.WebApp) {
         // Инициализируем Telegram Web App
         window.Telegram.WebApp.ready();

         // Получаем initData
         const initData = window.Telegram.WebApp.initData;
         // const initData = "user=%7B%22id%22%3A334089475%2C%22first_name%22%3A%22%D0%98%D0%BB%D1%8C%D1%8F%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22prosyanoy%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2F1Mdp9HYM70uySxrLRRBt_q48YPbcvraZhaQu-vb-sH8.svg%22%7D&chat_instance=7526889782112480440&chat_type=private&auth_date=1748969173&signature=VSdIrZbPCWSjUTYUIaFBXaBuxmkwyGyMP3LomArYhvTu7bh-XCa9L01WWeR_4YS-s3OHAptgOGjks9CRuH8VDw&hash=a99a3b79f24194372526e40e64a158bbba20d64ffac5b3103392db3285d5ca2d"
         // console.log("initData", initData);

         if (initData) {
             console.log("initData", initData);
             signIn(initData)
         } else {
            console.error("initData", 'initData not found');
            setLoading(false);
         }
    } else {
      console.error('Telegram Web App is not available');
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value: AuthCtxShape = {
    jwt: jwtState,
    loading,
    isAuthed: !!jwtState,
    signIn,
  };

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
};

export const useAuth = () => useContext(AuthCtx);

/* ------------------------------------------------------------------ */
/* 3. DTO types (optional if you’re on JS — keep for IntelliSense)    */
/* ------------------------------------------------------------------ */
export interface CollectionDTO {
  id: number;
  icon: string;
  title: { en: string; ru: string };
  total: number;
  wordsToLearn: number;
  wordsToRepeat: number;
}

export interface WordDTO {
  id: number | string;
  en: string;
  ru: string;
  transcription?: string;
  context?: { en: string; ru: string }[];
}

/**  IntelliSense only – include if you use JS with JSDoc
 * @typedef {import('./api').TaskDTO} TaskDTO
 */
export type TaskDTO =
  | {
      id: string;
      kind: 'translation';
      type: 'eng-ru' | 'ru-eng' | 'audio-ru';
      audio: string | null;
      variants: string[];
      word: string;
      correct: number;
      attempts: number;
    }
  | {
      id: string;
      kind: 'spelling';
      en: string;
      ru: string;
      mistakes: number;
    }
  | {
      id: string;
      kind: 'pronunciation';
      en: string;
      ru: string;
    }
  | { id: string; kind: 'context'; en: string; ru: string }
  | {
      id: string;
      kind: 'matching';
      pairs: { en: string; ru: string }[];
    };

export interface PronunciationResponse {
  ok: boolean;
  points: number;
  dtw: number;
}

/* ------------------------------------------------------------------ */
/* 4. Data fetch helpers                                              */
/* ------------------------------------------------------------------ */
export const fetchCollections = async (): Promise<CollectionDTO[]> => {
  const { data } = await api.get<CollectionDTO[]>('/collections/');
  return data;
};

export const fetchLearning = async (collectionId: number | string): Promise<WordDTO[]> => {
  const { data } = await api.get<WordDTO[]>(`/learning/${collectionId}`);
  return data;
};

export const fetchRepeat = async (collectionId: number | string): Promise<WordDTO[]> => {
  const { data } = await api.get<WordDTO[]>(`/repeat/${collectionId}`);
  return data;
};

export const fetchTasks = async (collectionId: string | number, wordIds: (number | string)[]): Promise<TaskDTO[]> => {
  const params = new URLSearchParams();
  wordIds.slice(0, 5).forEach((id) => params.append('word_ids', id.toString()));
  const { data } = await api.get<TaskDTO[]>(`/tasks/${collectionId}`, { params });
  return data;
};

export const postPronunciation = async (
  taskId: string | number,
  word: string,
  audioBlob: Blob
): Promise<PronunciationResponse> => {
  const form = new FormData();
  form.append('word', word);
  form.append('audio', audioBlob, 'voice.webm');

  const { data } = await api.post<PronunciationResponse>(
    `/pronunciation/${taskId}`,
    form
  );
  return data;
};

export interface RepeatPayload {
  word: string;
  score: number;
}

export const postSpacedRepeat = async (
  collectionId: string | number,
  results: RepeatPayload[]
): Promise<void> => {
  await api.post(`/spaced_repeat/${collectionId}`, results);
};
