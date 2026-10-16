import { ArrowRight } from 'lucide-react';
import type { Workspace } from '../useWorkspace';
import { Mark } from './Brand';

export function Welcome({ workspace: w }: { workspace: Workspace }) {
  return <main className="login-screen sixth-theme"><div className="login-card">
    <div className="brand"><Mark small /><span>sixth.</span></div>
    <div className="eyebrow">YOUR SIXTH SENSE FOR EVERYDAY LIFE</div>
    <h1>Your everyday,<br /><em>connected.</em></h1>
    <p>An assistant that remembers what matters<br />and helps you take the next step.</p>
    <button className="button primary" disabled={w.busy} onClick={() => void w.login()}>Enter your local workspace <ArrowRight size={17} /></button>
    <small>Private local demo · No signup or external accounts</small>
    {w.error && <p className="error-text" role="alert">{w.error}</p>}
  </div></main>;
}
