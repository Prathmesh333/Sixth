import { useEffect, useRef } from 'react';
import { ArrowUpRight, BrainCircuit, CalendarDays, MessageSquare, Plus, Settings2, X } from 'lucide-react';
import type { View } from '../types';
import type { Workspace } from '../useWorkspace';
import { Mark } from './Brand';

interface Props { workspace: Workspace; view: View; onView: (view: View) => void; open: boolean; onClose: () => void }
export function Sidebar({ workspace: w, view, onView, open, onClose }: Props) {
  const closeButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!open) return;
    const previous = document.activeElement as HTMLElement | null;
    closeButton.current?.focus();
    return () => previous?.focus();
  }, [open]);
  function navigate(next: View) { onView(next); onClose(); }
  return <>
    {open && <button className="sidebar-scrim" onClick={onClose} aria-label="Close navigation" />}
    <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Workspace navigation">
      <div className="brand"><Mark small /><span>sixth<span className="brand-period">.</span></span>
        <button ref={closeButton} className="icon-button mobile-close" onClick={onClose} aria-label="Close navigation"><X size={18} /></button>
      </div>
      <button className="new-chat" aria-label="Start a new conversation" onClick={() => { w.newConversation(); navigate('chat'); }}><Plus size={17} /> New conversation <span>↗</span></button>
      <nav className="primary-nav" aria-label="Main">
        <button className={view === 'chat' ? 'active' : ''} onClick={() => navigate('chat')}><MessageSquare size={17} /> Conversation</button>
        <button className={view === 'plans' ? 'active' : ''} onClick={() => navigate('plans')}><CalendarDays size={17} /> Your plans <span className="nav-count">{w.plans.length}</span></button>
        <button className={view === 'memory' ? 'active' : ''} onClick={() => navigate('memory')}><BrainCircuit size={17} /> Memory <span className="nav-count">{w.facts.length}</span></button>
      </nav>
      <div className="recent-heading">RECENT CONVERSATIONS</div>
      <div className="recent-list">
        {w.conversations.length === 0 ? <p>Your next conversation<br />starts something useful.</p> : [...w.conversations].reverse().map(c =>
          <button key={c.id} className={w.conversation?.id === c.id && view === 'chat' ? 'selected' : ''}
            onClick={() => { void w.selectConversation(c.id); navigate('chat'); }}><span>{c.title}</span></button>)}
      </div>
      <div className="sidebar-bottom">
        <div className="workspace-note"><span className="little-star">✳</span><p>A little more context.<br /><strong>A little less on your plate.</strong></p></div>
        <button className={view === 'settings' ? 'profile active' : 'profile'} onClick={() => navigate('settings')}>
          <span className="avatar">{w.session?.name[0]}</span><span><strong>{w.session?.name}’s workspace</strong><small>Local demo · private to this account</small></span><Settings2 size={16} />
        </button>
        <a className="source-link" href="https://github.com/Prathmesh333/Sixth" target="_blank" rel="noreferrer">Built with context <ArrowUpRight size={12} /></a>
      </div>
    </aside>
  </>;
}
