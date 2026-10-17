import { useEffect, useState } from 'react';
import { api, ApiError } from '../api';

export function WhatsAppConnect({ onConnected }: { onConnected: () => Promise<void> }) {
  const [enabled, setEnabled] = useState(false);
  const [phone, setPhone] = useState('');
  const [consent, setConsent] = useState(false);
  const [url, setUrl] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    let cancelled = false;
    void api<{ enabled: boolean }>('/v1/whatsapp/config').then(config => {
      if (!cancelled) setEnabled(config.enabled);
    }).catch(() => { if (!cancelled) setError('Could not check the WhatsApp connection.'); });
    return () => { cancelled = true; };
  }, []);
  useEffect(() => {
    if (!url) return;
    let cancelled = false;
    const timer = setInterval(() => {
      void api<{ connected: boolean }>('/v1/whatsapp/link').then(async result => {
        if (!cancelled && result.connected) {
          clearInterval(timer);
          await onConnected();
        }
      }).catch(err => {
        if (!cancelled && err instanceof ApiError && err.status === 410) {
          setUrl(''); setError('The connection expired. Start again.');
        }
      });
    }, 3000);
    return () => { cancelled = true; clearInterval(timer); };
  }, [url, onConnected]);
  async function connect() {
    setBusy(true); setError('');
    try {
      const result = await api<{ url: string }>('/v1/whatsapp/link', 'POST', { phone: phone.trim(), consent });
      setUrl(result.url);
    } catch (err) { setError(err instanceof Error ? err.message : 'Connection failed.'); }
    finally { setBusy(false); }
  }
  return <section className="whatsapp-connect" aria-labelledby="whatsapp-heading">
    <h2 id="whatsapp-heading">Connect your WhatsApp</h2>
    <p>Verify your number by sending a connection message to Sixth. Messages you send to Sixth are stored and processed by our AI to answer you and remember preferences.</p>
    <form onSubmit={event => { event.preventDefault(); void connect(); }}>
      <label htmlFor="whatsapp-phone">WhatsApp number with country code</label>
      <input id="whatsapp-phone" type="tel" autoComplete="tel" placeholder="+919876543210" pattern="\+[1-9][0-9]{7,14}" maxLength={16} required value={phone} onChange={event => setPhone(event.target.value)} disabled={!enabled || busy || !!url} />
      <label className="whatsapp-consent"><input type="checkbox" checked={consent} onChange={event => setConsent(event.target.checked)} disabled={!enabled || busy || !!url} required />I agree to Sixth storing and processing messages I send to its WhatsApp number.</label>
      <button className="button primary" disabled={!enabled || !consent || busy || !!url} type="submit">{busy ? 'Preparing connection…' : 'Connect WhatsApp'}</button>
    </form>
    {!enabled && <p role="status">WhatsApp setup is in progress. The private web demo is available below.</p>}
    {url && <div><a className="button primary" href={url} target="_blank" rel="noopener noreferrer">Open WhatsApp and send verification</a><p role="status">Waiting for your message. This link expires in 10 minutes. Keep this page open.</p><button className="button secondary" onClick={() => setUrl('')}>Use another number</button></div>}
    {error && <p role="alert">{error}</p>}
  </section>;
}
