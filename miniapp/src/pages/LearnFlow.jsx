import {useEffect, useMemo, useState} from 'react';
import Translation     from './Translation';
import Spelling        from './Spelling';
import Pronunciation   from './Pronunciation';
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
  const translationTasks  = tasks.filter(t => t.kind === 'translation');
  const spellingTasks     = tasks.filter(t => t.kind === 'spelling');
  const pronunciationTasks= tasks.filter(t => t.kind === 'pronunciation');

  // stage index: 0-trans, 1-spell, 2-pronounce, 3-results
  const [stage, setStage] = useState(0);
  const next = () => setStage(s => s + 1);

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
        onFinish={(totalScore) =>
          navigate(`/results/${id}`, { state: { scorePercent: totalScore } })
        }
      />
    );
  }

  return null;
}
