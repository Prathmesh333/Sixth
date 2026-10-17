import { ArrowRight } from 'lucide-react';
import { useState } from 'react';
import type { Workspace } from '../useWorkspace';
import { Mark } from './Brand';
import { WhatsAppConnect } from './WhatsAppConnect';

export function Welcome({ workspace: w }: { workspace: Workspace }) {
  const [accessCode, setAccessCode] = useState('');
  return <main className="login-screen sixth-theme"><div className="login-card">
    <div className="brand"><Mark small /><span>sixth.</span></div>
    <div className="eyebrow">YOUR SIXTH SENSE FOR EVERYDAY LIFE</div>
    <h1>Your everyday,<br /><em>connected.</em></h1>
    <p>An assistant that remembers what matters<br />and helps you take the next step.</p>
    <WhatsAppConnect onConnected={w.resumeSession} />
    <details><summary>Private web demo</summary><form onSubmit={event => { event.preventDefault(); void w.login('alex', accessCode); }}>
      <label htmlFor="demo-code">Demo access code</label>
      <input id="demo-code" type="password" autoComplete="off" value={accessCode} onChange={event => setAccessCode(event.target.value)} placeholder="Leave empty for local setup" maxLength={256} />
      <button className="button primary" type="submit" disabled={w.busy}>Enter your local workspace <ArrowRight size={17} /></button>
    </form></details>
    <small>Private demo · Shared sample accounts · Use synthetic data only</small>
    {w.error && <p className="error-text" role="alert">{w.error}</p>}
  </div></main>;
}
