import { useEffect, useRef, useState } from 'react';
import { api } from '../api';

interface GoogleIdentity {
  initialize(options: { client_id: string; nonce: string; callback: (response: { credential: string }) => void; auto_select: boolean }): void;
  renderButton(element: HTMLElement, options: { theme: string; size: string; shape: string; text: string; width: number }): void;
}
declare global { interface Window { google?: { accounts: { id: GoogleIdentity } } } }

let scriptPromise: Promise<void> | null = null;
function loadGoogle() {
  if (window.google?.accounts.id) return Promise.resolve();
  if (!scriptPromise) scriptPromise = new Promise<void>((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client'; script.async = true;
    script.onload = () => resolve();
    script.onerror = () => { script.remove(); scriptPromise = null; reject(new Error('Could not load Google sign-in. Check your connection and reload.')); };
    document.head.append(script);
  });
  return scriptPromise;
}

export function GoogleSignIn({ onCredential, busy }: { onCredential: (credential: string) => Promise<void>; busy: boolean }) {
  const container = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<'loading' | 'unconfigured' | 'ready' | 'error'>('loading');
  const [error, setError] = useState('');
  useEffect(() => {
    let cancelled = false;
    let observer: ResizeObserver | undefined;
    async function setup() {
      try {
        const config = await api<{ google_client_id: string | null }>('/v1/auth/config');
        if (cancelled) return;
        if (!config.google_client_id) { setState('unconfigured'); return; }
        const challenge = await api<{ nonce: string }>('/v1/auth/google/start', 'POST');
        if (cancelled) return;
        await loadGoogle();
        if (cancelled || !container.current || !window.google) return;
        window.google.accounts.id.initialize({ client_id: config.google_client_id, nonce: challenge.nonce,
          auto_select: false, callback: response => { if (!cancelled) void onCredential(response.credential); } });
        let lastWidth = 0;
        const render = () => {
          if (!container.current || !window.google || cancelled) return;
          const width = Math.min(360, container.current.parentElement?.clientWidth || 280);
          if (width === lastWidth) return;
          lastWidth = width;
          container.current.replaceChildren();
          window.google.accounts.id.renderButton(container.current, {
            theme: 'outline', size: 'large', shape: 'pill', text: 'continue_with', width,
          });
        };
        render();
        if (container.current.parentElement) {
          observer = new ResizeObserver(render);
          observer.observe(container.current.parentElement);
        }
        setState('ready');
      } catch (err) {
        if (!cancelled) { setState('error'); setError(err instanceof Error ? err.message : 'Google sign-in is unavailable.'); }
      }
    }
    void setup();
    return () => { cancelled = true; observer?.disconnect(); };
  }, [onCredential]);
  return <div className="google-signin" aria-busy={busy || state === 'loading'}>
    <div ref={container} className="google-button-slot" hidden={state !== 'ready' || busy} />
    {state !== 'ready' && <button type="button" className="google-placeholder" disabled><span aria-hidden="true">G</span>Continue with Google</button>}
    {busy && <p role="status">Opening your Sixth…</p>}
    {state === 'loading' && <p role="status">Preparing secure sign-in…</p>}
    {state === 'unconfigured' && <p role="status">Google sign-in is being connected. Check back shortly.</p>}
    {state === 'error' && <p role="alert">{error}</p>}
  </div>;
}
