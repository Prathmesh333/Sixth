import { useRef, useState } from 'react';
import { ArrowUp, BrainCircuit, CalendarDays, CornerDownLeft, Plus, ShoppingBag, Square } from 'lucide-react';
import type { Workspace } from '../useWorkspace';
import type { Task } from '../types';
import { ActionCard } from './ActionCard';
import { Mark } from './Brand';

const suggestions = [
  { icon: BrainCircuit, title: 'Keep something in mind', text: 'Remember that Maya is vegetarian.' },
  { icon: ShoppingBag, title: 'Make a plan happen', text: 'Plan Maya’s birthday dinner for four.' },
  { icon: CalendarDays, title: 'Find a little clarity', text: 'What’s on my calendar on Saturday?' },
];

export function Chat({ workspace: w, onEvidence }: { workspace: Workspace; onEvidence: (task: Task) => void }) {
  const [text, setText] = useState('');
  const input = useRef<HTMLTextAreaElement>(null);
  const detail = w.conversation;
  const welcome = !detail?.messages.length;
  const pending = detail?.tasks.filter(task => !detail.messages.some(m => m.task_id === task.id) && task.reply) || [];
  function submit() { if (text.trim() && !w.busy) { void w.send(text.trim()); setText(''); input.current?.focus(); } }

  return <div className={`chat-view ${welcome ? 'is-welcome' : ''}`}>
    <div className="chat-scroll" aria-label="Conversation">
      {welcome ? <div className="welcome">
        <div className="welcome-mark"><Mark /></div>
        <div className="eyebrow">A LITTLE MORE IN SYNC</div>
        <h1>Your everyday,<br /><em>connected.</em></h1>
        <p className="welcome-description">The things you tell me become the context<br className="desktop-break" /> that helps me take something off your plate.</p>
        <div className="suggestions">{suggestions.map(({ icon: Icon, title, text: prompt }) => <button key={title} onClick={() => void w.send(prompt)} disabled={w.busy}>
          <Icon size={18} /><span>{title}<small>{prompt}</small></span><span className="suggestion-arrow">↗</span>
        </button>)}</div>
      </div> : <div className="transcript" role="log" aria-label="Messages">
        {detail.messages.map(message => {
          const task = detail.tasks.find(t => t.id === message.task_id);
          return <article className={`message ${message.role}`} key={message.id}>
            {message.role === 'assistant' && <Mark small />}
            <div className="message-content"><span className="message-author">{message.role === 'user' ? 'You' : 'Sixth'}</span><p>{message.text}</p>
              {task?.plan && <ActionCard task={task} busy={w.busy} onDecision={decision => void w.decide(task, decision)} onEvidence={() => onEvidence(task)} />}
              {task?.evidence?.length && !task.plan ? <button className="evidence-link" onClick={() => onEvidence(task)}>Based on {task.evidence.length} sourced {task.evidence.length === 1 ? 'memory' : 'memories'} ↗</button> : null}
            </div>
          </article>;
        })}
        {pending.map(task => <article className="message assistant" key={task.id}><Mark small /><div className="message-content"><span className="message-author">Sixth</span><p>{task.reply}</p>
          <ActionCard task={task} busy={w.busy} onDecision={decision => void w.decide(task, decision)} onEvidence={() => onEvidence(task)} />
        </div></article>)}
      </div>}
    </div>
    <div className="composer-wrap">
      <div className="progress" role="status" aria-live="polite">{w.busy && <><span className="progress-dot" />{w.progress || 'Working on it…'}</>}</div>
      <form className="composer" onSubmit={event => { event.preventDefault(); submit(); }}>
        <label htmlFor="message" className="sr-only">Message Sixth</label>
        <textarea ref={input} id="message" value={text} onChange={event => setText(event.target.value)} placeholder="Tell me what’s on your mind…" rows={2}
          onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit(); } }} />
        <div className="composer-tools"><span className="composer-context"><Plus size={15} /> Context grows with you</span><div><span className="enter-hint"><CornerDownLeft size={12} /> to send</span>
          {w.busy ? <button type="button" className="send-button" aria-label="Stop current task" onClick={() => void w.stop()}><Square size={14} /></button> :
            <button type="submit" className="send-button" disabled={!text.trim()} aria-label="Send message"><ArrowUp size={19} /></button>}</div></div>
      </form>
      <p className="composer-caption">{w.status?.planner.mode === 'model' ? 'Model-assisted' : 'Local planner'} · {w.status?.memory.backend === 'falkordb' ? 'FalkorDB memory' : 'Fixture memory'} · You review actions before they happen.</p>
    </div>
  </div>;
}
