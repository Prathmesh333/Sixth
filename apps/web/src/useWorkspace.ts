import { useCallback, useEffect, useRef, useState } from 'react';
import { api, ApiError, setCsrf } from './api';
import type { Conversation, ConversationDetail, Fact, Plan, Session, Status, Task, TaskEvent } from './types';

export function useWorkspace() {
  const [session, setSession] = useState<Session | null>(null);
  const [starting, setStarting] = useState(true);
  const [status, setStatus] = useState<Status | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState('');
  const stream = useRef<EventSource | null>(null);
  const generation = useRef(0);
  const watchRevision = useRef(0);
  const demoCode = useRef('');
  const statusCache = useRef<Status | null>(null);
  const sending = useRef(false);
  const activeTask = useRef<string | null>(null);
  const poll = useRef<ReturnType<typeof setInterval> | null>(null);

  function closeStream(invalidate = true) {
    if (invalidate) watchRevision.current++;
    stream.current?.close();
    stream.current = null;
    if (poll.current) clearInterval(poll.current);
    poll.current = null;
  }

  const refreshConversation = useCallback(async (id: string, version: number) => {
    const detail = await api<ConversationDetail>(`/v1/conversations/${id}`);
    if (version !== generation.current) return null;
    setConversation(previous => previous?.id === id ? {
      ...detail,
      messages: detail.messages.map(message => ({ ...message,
        client_id: previous.messages.find(old => old.id === message.id)?.client_id,
      })),
    } : previous);
    return detail;
  }, []);

  const load = useCallback(async (conversationId?: string) => {
    const version = generation.current;
    const nextStatus = statusCache.current || await api<Status>('/v1/status');
    const [nextConversations, nextFacts, nextPlans, nextConversation] = await Promise.all([
      api<Conversation[]>('/v1/conversations'),
      nextStatus.memory.connected ? api<{ items: Fact[] }>('/v1/memory') : Promise.resolve({ items: [] }),
      api<Plan[]>('/v1/plans'),
      conversationId ? api<ConversationDetail>(`/v1/conversations/${conversationId}`) : Promise.resolve(null),
    ]);
    if (version !== generation.current) return;
    statusCache.current = nextStatus;
    setStatus(nextStatus); setConversations(nextConversations); setFacts(nextFacts.items); setPlans(nextPlans);
    if (!nextStatus.memory.connected) setError(nextStatus.memory.detail);
    if (nextConversation) setConversation(nextConversation);
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function start() {
      try {
        const current = await api<Session>('/v1/session');
        if (cancelled) return;
        setCsrf(current.csrf_token); setSession(current); await load();
      } catch (err) {
        if (!cancelled && (!(err instanceof ApiError) || err.status !== 401)) setError('The Sixth API is unavailable. Start the API and retry.');
      } finally { if (!cancelled) setStarting(false); }
    }
    void start();
    return () => { cancelled = true; watchRevision.current++; stream.current?.close(); if (poll.current) clearInterval(poll.current); };
  }, [load]);

  const report = (err: unknown) => setError(err instanceof Error ? err.message : 'Something went wrong. Please retry.');

  const resumeSession = useCallback(async () => {
    const current = await api<Session>('/v1/session');
    setCsrf(current.csrf_token); setSession(current); setConversation(null); await load();
  }, [load]);

  async function login(account = 'alex', accessCode?: string) {
    if (accessCode !== undefined) demoCode.current = accessCode;
    setError(''); setBusy(true); stream.current?.close(); generation.current++;
    try {
      const current = await api<Session>('/v1/session/demo', 'POST', { account, access_code: demoCode.current });
      setCsrf(current.csrf_token); setSession(current); setConversation(null); await load();
    } catch (err) { report(err); } finally { setBusy(false); }
  }

  const signInGoogle = useCallback(async (credential: string) => {
    setError(''); setBusy(true); stream.current?.close(); generation.current++;
    try {
      const current = await api<Session>('/v1/auth/google', 'POST', { credential, consent: true });
      setCsrf(current.csrf_token); setConversation(null); setFacts([]); setPlans([]); setConversations([]);
      await load(); setSession(current);
    } catch (err) { setError(err instanceof Error ? err.message : 'Google sign-in failed. Please retry.'); }
    finally { setBusy(false); }
  }, [load]);

  async function logout() {
    setBusy(true); setError('');
    try {
      await api('/v1/session/logout', 'POST');
      closeStream(); generation.current++; setCsrf(''); demoCode.current = ''; statusCache.current = null;
      sending.current = false; activeTask.current = null;
      setSession(null); setStatus(null); setConversation(null); setConversations([]); setFacts([]); setPlans([]); setProgress('');
    } catch (err) { report(err); } finally { setBusy(false); }
  }

  function watch(taskId: string, conversationId: string) {
    closeStream();
    activeTask.current = taskId;
    const version = generation.current;
    const revision = watchRevision.current;
    const current = () => version === generation.current && revision === watchRevision.current;
    let finishing = false;
    let checking = false;
    async function finish() {
      if (finishing || !current()) return;
      finishing = true;
      closeStream(false);
      try {
        const detail = await refreshConversation(conversationId, version);
        if (!current() || !detail) return;
        const task = detail.tasks.find(task => task.id === taskId);
        if (task?.evidence?.length || task?.plan) {
          const [memory, nextPlans] = await Promise.all([
            api<{ items: Fact[] }>('/v1/memory'), api<Plan[]>('/v1/plans'),
          ]);
          if (current()) { setFacts(memory.items); setPlans(nextPlans); }
        }
      } catch (err) { if (current()) report(err); }
      finally {
        if (current()) {
          activeTask.current = null; sending.current = false; setBusy(false); setProgress('');
        }
      }
    }
    async function checkTask() {
      if (!current() || finishing || checking) return;
      checking = true;
      try {
        const task = await api<Task>(`/v1/tasks/${taskId}`);
        if (!current() || finishing) return;
        if (['awaiting_input', 'completed', 'failed', 'cancelled'].includes(task.status)) {
          await finish(); return;
        }
        setProgress('Still working on your reply…');
      } catch (err) {
        if (!current()) return;
        if (err instanceof ApiError && [401, 404].includes(err.status)) {
          finishing = true;
          report(err); closeStream(false); sending.current = false; setBusy(false); return;
        }
        setProgress('Reconnecting to your reply…');
      } finally { checking = false; }
    }
    const events = new EventSource(`/v1/tasks/${taskId}/events`);
    stream.current = events;
    events.onmessage = (message: MessageEvent<string>) => {
      if (!current() || finishing) { events.close(); return; }
      const event = JSON.parse(message.data) as TaskEvent;
      const labels: Record<string, string> = {
        'task.started': 'Thinking about your request…', 'context.retrieved': 'Connecting the relevant context…',
        'context.started': 'Checking saved context…', 'planner.started': 'Checking your request…',
        'plan.updated': 'Putting your plan together…', 'tool.started': 'Applying your approved action…',
        'memory.updated': 'Saving what matters…',
      };
      if (labels[event.type]) setProgress(labels[event.type]);
      if (['input.required', 'task.completed', 'task.failed', 'task.cancelled'].includes(event.type)) {
        // A replayed review event cannot settle a resumed action: check its state.
        void checkTask();
      }
    };
    events.onerror = () => {
      events.close();
      if (current() && !finishing) void checkTask();
    };
    // Poll independently of SSE callbacks. A stale stream or a replayed event
    // must never clear the next task's fallback timer in this conversation.
    poll.current = setInterval(() => void checkTask(), 3000);
    void checkTask();
  }

  async function send(text: string) {
    if (sending.current || busy || !text.trim()) return;
    sending.current = true;
    const version = generation.current;
    const clientId = crypto.randomUUID();
    const optimistic = { id: clientId, client_id: clientId, role: 'user' as const, text };
    const previous = conversation;
    setConversation(current => current ? { ...current, messages: [...current.messages, optimistic] } : {
      id: `pending-${clientId}`, title: text.slice(0, 48), created_at: new Date().toISOString(), messages: [optimistic], tasks: [],
    });
    setError(''); setBusy(true); setProgress('Thinking about your request…');
    try {
      let identifier = previous?.id;
      if (!identifier) {
        const created = await api<Conversation>('/v1/conversations', 'POST');
        if (version !== generation.current) return;
        identifier = created.id;
        setConversation(current => current ? { ...current, ...created, title: text.slice(0, 48) } : current);
        setConversations(current => [...current, { ...created, title: text.slice(0, 48) }]);
      }
      const accepted = await api<{ task_id: string; message_id: string }>(`/v1/conversations/${identifier}/messages`, 'POST', { text, timezone: 'Asia/Calcutta' });
      if (version !== generation.current) return;
      setConversation(current => current ? { ...current,
        messages: current.messages.map(message => message.client_id === clientId ? { ...message, id: accepted.message_id } : message),
      } : current);
      watch(accepted.task_id, identifier);
      return true;
    } catch (err) {
      if (version !== generation.current) return;
      report(err); sending.current = false; setBusy(false); setProgress('');
      setConversation(previous);
      return false;
    }
  }

  async function decide(task: Task, decision: 'approve' | 'reject') {
    if (!task.action || busy) return;
    setBusy(true); setError('');
    try {
      await api(`/v1/tasks/${task.id}/decisions`, 'POST', { decision_id: task.action.decision_id,
        decision, fingerprint: task.action.fingerprint, plan_revision: task.action.plan_revision });
      watch(task.id, task.conversation_id);
    } catch (err) { report(err); setBusy(false); await load(task.conversation_id); }
  }

  async function stop() {
    const id = activeTask.current || conversation?.tasks.findLast(task => ['queued', 'running', 'awaiting_input'].includes(task.status))?.id;
    if (!id) return;
    try { await api(`/v1/tasks/${id}/cancel`, 'POST'); if (conversation) await refreshConversation(conversation.id, generation.current); }
    catch (err) { report(err); }
    closeStream(); activeTask.current = null; sending.current = false; setBusy(false); setProgress('');
  }

  function newConversation() {
    closeStream(); activeTask.current = null; sending.current = false; generation.current++; setConversation(null); setBusy(false); setProgress(''); setError('');
  }

  async function selectConversation(id: string) {
    closeStream(); activeTask.current = null; sending.current = false; generation.current++; setBusy(false); setProgress(''); setError('');
    const version = generation.current;
    try {
      const detail = await api<ConversationDetail>(`/v1/conversations/${id}`);
      if (version === generation.current) setConversation(detail);
    } catch (err) { if (version === generation.current) report(err); }
  }

  async function forget(fact: Fact) {
    setError('');
    try { await api(`/v1/memory/${fact.id}`, 'DELETE'); await load(conversation?.id); }
    catch (err) { report(err); }
  }

  async function correct(fact: Fact, value: string) {
    setError('');
    try {
      await api(`/v1/memory/${fact.id}`, 'PATCH', { expected_version: fact.version, value, reason: `Updated by you: ${value}` });
      await load(conversation?.id); return true;
    } catch (err) { report(err); return false; }
  }

  return { session, starting, status, conversations, conversation, facts, plans, error, busy, progress,
    login, signInGoogle, logout, resumeSession, send, decide, stop, newConversation, selectConversation, forget, correct, clearError: () => setError('') };
}
export type Workspace = ReturnType<typeof useWorkspace>;
