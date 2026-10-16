import { useState } from 'react';
import { ArrowUpRight, BrainCircuit, Check, Pencil, Search, Trash2, X } from 'lucide-react';
import type { Workspace } from '../useWorkspace';

export function MemoryView({ workspace: w, onChat }: { workspace: Workspace; onChat: () => void }) {
  const [query, setQuery] = useState('');
  const [editing, setEditing] = useState<string | null>(null);
  const [value, setValue] = useState('');
  const [forgetting, setForgetting] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  async function saveCorrection(fact: Workspace['facts'][number]) {
    setSaving(true);
    try { if (await w.correct(fact, value)) setEditing(null); }
    finally { setSaving(false); }
  }
  const filtered = w.facts.filter(f => `${f.subject} ${f.predicate} ${f.value}`.toLowerCase().includes(query.toLowerCase()));
  return <div className="page-view memory-view">
    <div className="eyebrow">PERSONAL, NOT ASSUMED</div><div className="page-title-row"><h1>A little context<br /><em>goes a long way.</em></h1><button className="button secondary" onClick={onChat}>Share something <ArrowUpRight size={16} /></button></div>
    <p className="page-description">The things you’ve shared, in your control. See where a memory came from, change it, or let it go.</p>
    <div className="search-field"><Search size={16} /><input aria-label="Search memories" placeholder="Find a person, preference, or detail…" value={query} onChange={event => setQuery(event.target.value)} /><span>{filtered.length} memories</span></div>
    {filtered.length ? <div className="memory-list">{filtered.map(fact => <article className="memory-card" key={fact.id}>
      <div className="memory-card-heading"><span className="person-dot">{fact.subject[0]}</span><strong>{fact.subject}</strong><span className="memory-kind">{fact.scope_type === 'event' ? 'This plan only' : fact.predicate}</span>
        <div className="memory-controls"><button className="icon-button" aria-label={`Edit ${fact.subject}'s ${fact.predicate}`} onClick={() => { setEditing(fact.id); setValue(fact.value); setForgetting(null); }}><Pencil size={15} /></button><button className="icon-button" aria-label={`Forget ${fact.subject}'s ${fact.predicate}`} onClick={() => { setForgetting(fact.id); setEditing(null); }}><Trash2 size={15} /></button></div>
      </div>
      {editing === fact.id ? <form className="memory-edit" onSubmit={event => { event.preventDefault(); void saveCorrection(fact); }}>
        <label htmlFor={`edit-${fact.id}`}>Updated preference</label><input id={`edit-${fact.id}`} value={value} onChange={event => setValue(event.target.value)} autoFocus required maxLength={1000} />
        <div><button type="submit" className="button primary" disabled={saving || !value.trim()}><Check size={14} /> Save correction</button><button type="button" className="button ghost" onClick={() => setEditing(null)}>Cancel</button></div>
      </form> : <p className="memory-value">{fact.value}</p>}
      <blockquote><span>YOU SHARED</span>“{fact.sources[0]?.excerpt}”</blockquote>
      {forgetting === fact.id ? <div className="forget-confirm"><p>Remove this memory and its related conversation context? Plans using it will need a fresh review.</p><button className="button danger" onClick={async () => { await w.forget(fact); setForgetting(null); }}>Forget this memory</button><button className="icon-button" aria-label="Cancel forgetting" onClick={() => setForgetting(null)}><X size={16} /></button></div> :
        <div className="memory-footer"><span><Check size={12} /> Confirmed by you</span><span>Version {fact.version} · {new Date(fact.recorded_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</span></div>}
    </article>)}</div> : <div className="empty-state"><BrainCircuit size={30} /><h2>{query ? 'No matching memories' : 'Start with a small detail.'}</h2><p>{query ? 'Try another name or preference.' : 'Tell Sixth a preference in conversation. It will be here the next time you need it.'}</p><button className="button secondary" onClick={onChat}>Open conversation <ArrowUpRight size={15} /></button></div>}
  </div>;
}
