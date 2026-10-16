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

  const load = useCallback(async (conversationId?: string) => {
    const version = generation.current;
    const nextStatus = await api<Status>('/v1/status');
    const [nextConversations, nextFacts, nextPlans, nextConversation] = await Promise.all([
      api<Conversation[]>('/v1/conversations'),
      nextStatus.memory.connected ? api<{ items: Fact[] }>('/v1/memory') : Promise.resolve({ items: [] }),
      api<Plan[]>('/v1/plans'),
      conversationId ? api<ConversationDetail>(`/v1/conversations/${conversationId}`) : Promise.resolve(null),
    ]);
    if (version !== generation.current) return;
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
    return () => { cancelled = true; stream.current?.close(); };
  }, [load]);

  const report = (err: unknown) => setError(err instanceof Error ? err.message : 'Something went wrong. Please retry.');

  async function login(account = 'alex') {
    setError(''); setBusy(true); stream.current?.close(); generation.current++;
    try {
      const current = await api<Session>('/v1/session/demo', 'POST', { account });
      setCsrf(current.csrf_token); setSession(current); setConversation(null); await load();
    } catch (err) { report(err); } finally { setBusy(false); }
  }

  function watch(taskId: string, conversationId: string) {
    stream.current?.close();
    const version = generation.current;
    const events = new EventSource(`/v1/tasks/${taskId}/events`);
    stream.current = events;
    events.onmessage = (message: MessageEvent<string>) => {
      const event = JSON.parse(message.data) as TaskEvent;
      if (generation.current !== version) { events.close(); return; }
      const labels: Record<string, string> = {
        'task.started': 'Understanding your request…', 'context.retrieved': 'Connecting the relevant context…',
        'plan.updated': 'Putting your plan together…', 'tool.started': 'Preparing your test cart…',
        'memory.updated': 'Saving what matters…',
      };
      setProgress(labels[event.type] || '');
      if (['input.required', 'task.completed', 'task.failed', 'task.cancelled'].includes(event.type)) {
        events.close(); setBusy(false); setProgress('');
        void load(conversationId).catch(report);
      }
    };
    events.onerror = () => {
      events.close(); setBusy(false); setProgress('');
      void load(conversationId).catch(report);
    };
  }

  async function send(text: string) {
    if (busy || !text.trim()) return;
    const version = generation.current;
    setError(''); setBusy(true); setProgress('Understanding your request…');
    try {
      let identifier = conversation?.id;
      if (!identifier) identifier = (await api<Conversation>('/v1/conversations', 'POST')).id;
      const accepted = await api<{ task_id: string }>(`/v1/conversations/${identifier}/messages`, 'POST', { text, timezone: 'Asia/Calcutta' });
      if (version !== generation.current) return;
      await load(identifier); watch(accepted.task_id, identifier);
    } catch (err) { report(err); setBusy(false); setProgress(''); }
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
    const current = conversation?.tasks.findLast(task => ['queued', 'running', 'awaiting_input'].includes(task.status));
    if (!current) return;
    try { await api(`/v1/tasks/${current.id}/cancel`, 'POST'); await load(conversation?.id); }
    catch (err) { report(err); }
    stream.current?.close(); setBusy(false); setProgress('');
  }

  function newConversation() {
    stream.current?.close(); generation.current++; setConversation(null); setBusy(false); setProgress(''); setError('');
  }

  async function selectConversation(id: string) {
    stream.current?.close(); generation.current++; setBusy(false); setProgress(''); setError('');
    try { await load(id); } catch (err) { report(err); }
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
    login, send, decide, stop, newConversation, selectConversation, forget, correct, clearError: () => setError('') };
}
export type Workspace = ReturnType<typeof useWorkspace>;
