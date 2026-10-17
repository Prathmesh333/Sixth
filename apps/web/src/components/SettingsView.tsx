import { useState } from 'react';
import { Check, Database, Download, Globe2, MessageSquare, ShoppingBag, Sparkles } from 'lucide-react';
import { api } from '../api';
import type { Theme } from '../types';
import type { Workspace } from '../useWorkspace';

export function SettingsView({ workspace: w, theme, onTheme }: { workspace: Workspace; theme: Theme; onTheme: (theme: Theme) => void }) {
  const [exportError, setExportError] = useState('');
  async function download() {
    try {
      const data = await api('/v1/export');
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
      const link = document.createElement('a'); link.href = url; link.download = 'sixth-personal-context.json'; link.click();
      URL.revokeObjectURL(url);
    } catch { setExportError('Could not export your context. Please retry.'); }
  }
  const connections = [
    { icon: Database, title: 'Personal memory', detail: w.status?.memory.detail, state: w.status?.memory.backend === 'falkordb' && w.status.memory.connected ? 'Connected' : 'Fixture mode' },
    { icon: Sparkles, title: 'Intelligence', detail: w.status?.planner.mode === 'model' ? w.status.planner.model : 'A deterministic local planner. No model API calls.', state: w.status?.planner.mode === 'model' ? 'Model configured' : 'Local planner' },
    { icon: Globe2, title: 'Calendar', detail: 'Sample events for the demo. A live calendar is not connected.', state: 'Sample data' },
    { icon: ShoppingBag, title: 'Shopping', detail: 'Prepare and verify a local test cart. No checkout or real purchases.', state: 'Sandbox' },
    { icon: MessageSquare, title: 'Sixth chat', detail: 'Chat directly in your own account. Conversations and memories follow you when you sign in.', state: 'Available' },
  ];
  return <div className="page-view settings-view"><div className="eyebrow">MAKE IT YOURS</div><h1>Comfortably<br /><em>in your control.</em></h1><p className="page-description">Choose how Sixth feels, and see exactly what’s connected.</p>
    <section className="settings-section"><h2>Appearance</h2><p>A quieter space for the way you think.</p><div className="theme-options">{(['dusk', 'paper', 'grove'] as const).map(option => <button className={`theme-option ${option} ${theme === option ? 'selected' : ''}`} aria-pressed={theme === option} onClick={() => onTheme(option)} key={option}>
      <span className="theme-preview"><span /><span /><span /></span><span>{option[0].toUpperCase() + option.slice(1)} {theme === option && <Check size={14} />}</span></button>)}</div></section>
    <section className="settings-section"><h2>Connections & capabilities</h2><p>Available features are labeled honestly. Nothing runs behind your back.</p><div className="connections">{connections.map(({ icon: Icon, title, detail, state }) => <div className="connection" key={title}><Icon size={19} /><div><strong>{title}</strong><p>{detail}</p></div><span className="mode-tag">{state}</span></div>)}</div>
      <details className="setup-details"><summary>Configure the model and FalkorDB</summary><p>Set the server environment variables in the root .env file and restart the API. Credentials stay on the server.</p><pre>SIXTH_MEMORY_BACKEND=falkordb{'\n'}SIXTH_FALKORDB_HOST=127.0.0.1{'\n'}SIXTH_MODEL_NAME=your-model{'\n'}SIXTH_MODEL_API_KEY=your-key</pre><p>See the repository README for local startup. Fixture mode is not the hackathon graph integration.</p></details>
    </section>
    <section className="settings-section"><h2>Your context belongs to you</h2><p>Download your saved memories, plans and test carts. Credentials are excluded.</p><button className="button secondary" onClick={() => void download()}><Download size={15} /> Export your context</button>{exportError && <p role="alert">{exportError}</p>}</section>
    {w.session?.demo && <section className="settings-section"><h2>Local demo accounts</h2><p>Switch accounts to check that memories and conversations stay separate.</p><div className="account-switch">{['alex', 'jordan'].map(account => <button className="button secondary" key={account} disabled={w.session?.account === account || w.busy} onClick={() => void w.login(account)}>{account[0].toUpperCase() + account.slice(1)} {w.session?.account === account && <Check size={14} />}</button>)}</div></section>}
    <section className="settings-section"><h2>Your account</h2><p>Signed in as {w.session?.name}. Signing out removes this browser’s session.</p><button className="button secondary" disabled={w.busy} onClick={() => void w.logout()}>Sign out</button></section>
  </div>;
}
