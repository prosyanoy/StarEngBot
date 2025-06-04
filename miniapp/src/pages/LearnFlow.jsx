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
      navigate(`/results/${id}`, { state: { scorePercent: 0 } });
    }
  }, [stage, loading, translationTasks.length, spellingTasks.length, pronunciationTasks.length, contextTasks.length, matchingTasks.length, navigate, id]);

  if (authLoading)        return <p>{t('Authorising...')}</p>;
  if (!isAuthed)          return <p>{t('Auth failed')}</p>;
  if (loading)              return <p>{t('Loading collections...')}</p>;

  if (stage === 0) {
    return (
      <Translation
        tasks={translationTasks}
        onFinish={next}
      />
    );
  }

  if (stage === 1) {
    return (
      <Spelling
        tasks={spellingTasks}
        onFinish={next}
      />
    );
  }

  if (stage === 2) {
    return (
      <Pronunciation
        tasks={pronunciationTasks}
        onFinish={next}
      />
    );
  }

  if (stage === 3) {
    return (
      <Context
        tasks={contextTasks}
        onFinish={next}
      />
    );
  }

  if (stage === 4) {
    return (
      <Matching
        tasks={matchingTasks}
        onFinish={(score) =>
          navigate(`/results/${id}`, { state: { scorePercent: score ?? 0 } })
        }
      />
    );
  }

  return null;
}
