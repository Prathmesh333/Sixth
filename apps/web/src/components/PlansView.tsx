import { ArrowUpRight, CalendarDays, Check, Clock3, Users } from 'lucide-react';
import type { Workspace } from '../useWorkspace';

export function PlansView({ workspace: w, onOpen }: { workspace: Workspace; onOpen: (id?: string) => void }) {
  return <div className="page-view">
    <div className="eyebrow">LESS TO KEEP TRACK OF</div><h1>Good intentions,<br /><em>taking shape.</em></h1><p className="page-description">Your plans and the next steps that bring them together.</p>
    {w.plans.length ? <div className="plans-list">{[...w.plans].reverse().map(plan => <article className="plan-card" key={plan.id}>
      <div className="plan-date"><span>OCT</span><strong>17</strong><span>SATURDAY</span></div><div className="plan-summary"><div className="plan-kicker">DINNER AT HOME <span>Revision {plan.revision}</span></div><h2>{plan.title}</h2><p>{plan.recipe.name}</p><div className="recipe-meta"><span><Users size={14} /> {plan.guests} people</span><span><Clock3 size={14} /> 7:00 pm</span></div></div>
      <div className="plan-card-end"><span className={`status-pill ${plan.status === 'cart_ready' ? 'success' : ''}`}>{plan.status === 'cart_ready' ? <><Check size={13} /> Test cart ready</> : plan.status === 'stale' ? 'Needs a fresh plan' : 'Awaiting your review'}</span><button className="button ghost" onClick={() => onOpen(plan.conversation_id)}>Open conversation <ArrowUpRight size={15} /></button></div>
    </article>)}</div> : <div className="empty-state"><CalendarDays size={30} /><h2>Make room for something good.</h2><p>Start with a dinner plan. Sixth can put together a menu and a shopping list for your review.</p><button className="button secondary" onClick={() => onOpen()}>Start a conversation <ArrowUpRight size={15} /></button></div>}
    <div className="quiet-note"><span>✳</span><p>Plans remember their context. When something changes, ask Sixth to replan.</p></div>
  </div>;
}
