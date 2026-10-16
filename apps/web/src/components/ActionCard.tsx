import { ArrowUpRight, Check, Clock3, ShoppingBag, Users } from 'lucide-react';
import type { Task } from '../types';

const currency = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' });

export function ActionCard({ task, busy, onDecision, onEvidence }: {
  task: Task; busy: boolean; onDecision: (decision: 'approve' | 'reject') => void; onEvidence: () => void;
}) {
  const plan = task.plan;
  if (!plan) return null;
  const ready = task.result?.status === 'succeeded';
  const review = task.status === 'awaiting_input';
  const total = plan.items.reduce((sum, item) => sum + item.amount_minor, 0);
  return <section className="action-card" aria-label="Dinner plan">
    <div className="action-eyebrow"><span><ShoppingBag size={14} /> DINNER, SORTED</span><span className="mode-tag">Test store</span></div>
    <h3>{plan.recipe.name}</h3><p>{plan.recipe.description}</p>
    <div className="recipe-meta"><span><Users size={14} /> {plan.guests} people</span><span><Clock3 size={14} /> {plan.recipe.minutes} min</span><span>{plan.recipe.dairy_free ? 'Plant-based' : 'Vegetarian'}</span></div>
    <div className="ingredient-list"><div className="ingredient-head"><span>Shopping list</span><span>Quantity</span></div>
      {plan.items.map(item => <div className="ingredient" key={item.id}><span>{item.name}{item.pantry > 0 && <small>{item.pantry} {item.unit} already in the sample pantry</small>}</span><strong>{item.quantity} {item.unit}</strong></div>)}
    </div>
    <div className="cart-total"><span>Sample estimate</span><strong>{currency.format(total / 100)}</strong></div>
    <button className="evidence-link" onClick={onEvidence}>Why this plan? <span>{task.evidence?.length || 0} memories</span><ArrowUpRight size={14} /></button>
    {review ? <div className="action-footer"><button className="button primary" disabled={busy} onClick={() => onDecision('approve')}><ShoppingBag size={15} /> Prepare test cart</button><button className="button ghost" disabled={busy} onClick={() => onDecision('reject')}>Not now</button></div> :
      <div className={`action-outcome ${ready ? 'success' : ''}`}><Check size={16} /><span>{ready ? 'Cart contents verified. No purchase made.' : task.stale ? 'This plan changed. Ask me to replan.' : 'Plan saved. Your cart has not changed.'}</span></div>}
    <div className="card-caption">Revision {plan.revision} · Sandbox only · Prices are sample estimates</div>
  </section>;
}
