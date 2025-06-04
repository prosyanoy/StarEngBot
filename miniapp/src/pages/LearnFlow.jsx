import {useEffect, useMemo, useState} from 'react';
import Translation     from './Translation';
import Spelling        from './Spelling';
import Pronunciation   from './Pronunciation';
import Context         from './Context';
import Matching        from './Matching';
import {useLocation, useNavigate, useParams, useSearchParams} from 'react-router-dom';
import {fetchRepeat, fetchTasks, useAuth} from "@/lib/api";
import {t} from "i18next";

export default function LearnFlow() {
  const { loading: authLoading, isAuthed } = useAuth();
  const { id }          = useParams();      // collection id
  const { state } = useLocation();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams]  = useSearchParams();
  const mode = searchParams.get('mode');
  const navigate        = useNavigate();

  const [scores, setScores] = useState({
    translation: 0,
    spelling: 0,
    pronunciation: 0,
    context: 0,
  });

  const wordIds = useMemo(
    () =>
      Array.isArray(state?.wordIds)
        ? state.wordIds.slice(0, 5)
        : [],
    [state?.wordIds]
  );


  useEffect(() => {
    let alive = true;
    async function load() {
      setLoading(true);

      try {
        let data;
        if (mode === 'repeat') {
          data = await fetchRepeat(id);
        } else if (wordIds.length > 0) {
          data = await fetchTasks(id, wordIds);
          console.log("data", data);
        } else {
          data = [];
        }

        if (alive) {
          setTasks(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (alive) setLoading(false);
      }
    }

    load();

    return () => {
      alive = false;
    };
  }, [id, mode, wordIds]); // now wordIds is memoized, so this won't loop

  // split once
  const translationTasks   = tasks.filter(t => t.kind === 'translation');
  const spellingTasks      = tasks.filter(t => t.kind === 'spelling');
  const pronunciationTasks = tasks.filter(t => t.kind === 'pronunciation');
  const contextTasks       = tasks.filter(t => t.kind === 'context');
  const matchingTasks      = tasks.filter(t => t.kind === 'matching');

  const words = useMemo(() => {
    const set = new Set();
    spellingTasks.forEach(t => set.add(t.en));
    pronunciationTasks.forEach(t => set.add(t.en));
    contextTasks.forEach(t => set.add(t.en));
    return Array.from(set);
  }, [spellingTasks, pronunciationTasks, contextTasks]);

  // stage index:
  // 0 - translation
  // 1 - spelling
  // 2 - pronunciation
  // 3 - context
  // 4 - matching
  const [stage, setStage] = useState(0);
  const next = () => setStage(s => s + 1);

  // Skip empty stages
  useEffect(() => {
    if (loading) return;
    if (stage === 0 && translationTasks.length === 0) {
      setStage(1);
    } else if (stage === 1 && spellingTasks.length === 0) {
      setStage(2);
    } else if (stage === 2 && pronunciationTasks.length === 0) {
      setStage(3);
    } else if (stage === 3 && contextTasks.length === 0) {
      setStage(4);
    } else if (stage === 4 && matchingTasks.length === 0) {
      const breakdown = {
        translation: scores.translation,
        spellingPron: scores.spelling + scores.pronunciation,
        context: scores.context,
        matching: 0,
      };
      const scorePercent =
        breakdown.translation +
        breakdown.spellingPron +
        breakdown.context +
        breakdown.matching;
      navigate(`/results/${id}`, { state: { scorePercent, breakdown, words } });
    }
  }, [stage, loading, translationTasks.length, spellingTasks.length, pronunciationTasks.length, contextTasks.length, matchingTasks.length, navigate, id, scores, words]);

  if (authLoading)        return <p>{t('Authorising...')}</p>;
  if (!isAuthed)          return <p>{t('Auth failed')}</p>;
  if (loading)              return <p>{t('Loading collections...')}</p>;

  if (stage === 0) {
    return (
      <Translation
        tasks={translationTasks}
        onFinish={(scr) => {
          setScores(s => ({ ...s, translation: scr }));
          next();
        }}
      />
    );
  }

  if (stage === 1) {
    return (
      <Spelling
        tasks={spellingTasks}
        onFinish={(scr) => {
          const norm = spellingTasks.length
            ? (scr / (spellingTasks.length * 3)) * 15
            : 0;
          setScores(s => ({ ...s, spelling: norm }));
          next();
        }}
      />
    );
  }

  if (stage === 2) {
    return (
      <Pronunciation
        tasks={pronunciationTasks}
        onFinish={(scr) => {
          const norm = pronunciationTasks.length
            ? (scr / (pronunciationTasks.length * 3)) * 15
            : 0;
          setScores(s => ({ ...s, pronunciation: norm }));
          next();
        }}
      />
    );
  }

  if (stage === 3) {
    return (
      <Context
        tasks={contextTasks}
        onFinish={() => {
          const val = contextTasks.length ? 30 : 0;
          setScores(s => ({ ...s, context: val }));
          next();
        }}
      />
    );
  }

  if (stage === 4) {
    return (
      <Matching
        tasks={matchingTasks}
        onFinish={() => {
          const breakdown = {
            translation: scores.translation,
            spellingPron: scores.spelling + scores.pronunciation,
            context: scores.context,
            matching: 10,
          };
          const scorePercent =
            breakdown.translation +
            breakdown.spellingPron +
            breakdown.context +
            breakdown.matching;
          navigate(`/results/${id}`, { state: { scorePercent, breakdown, words } });
        }}
      />
    );
  }

  return null;
}
