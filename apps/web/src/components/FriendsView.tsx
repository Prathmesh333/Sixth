import { useEffect, useState } from 'react';
import { api } from '../api';

interface Friend { id: string; name: string; username: string; status: 'pending' | 'accepted'; incoming: boolean }
interface Friends { username: string; items: Friend[] }

export function FriendsView() {
  const [data, setData] = useState<Friends | null>(null);
  const [username, setUsername] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  useEffect(() => {
    let cancelled = false;
    void api<Friends>('/v1/friends').then(result => { if (!cancelled) setData(result); })
      .catch(err => { if (!cancelled) setError(err instanceof Error ? err.message : 'Could not load friends.'); });
    return () => { cancelled = true; };
  }, []);
  async function act(path: string, method: string, body?: unknown) {
    setBusy(true); setError(''); setNotice('');
    try {
      await api(path, method, body); setData(await api<Friends>('/v1/friends'));
      setUsername(''); setNotice('Friends updated.');
    } catch (err) { setError(err instanceof Error ? err.message : 'Please try again.'); }
    finally { setBusy(false); }
  }
  return <div className="page-view friends-view"><div className="eyebrow">THE PEOPLE IN YOUR WORLD</div>
    <h1>A little more<br /><em>connected.</em></h1>
    <p className="page-description">Add someone by their Sixth username. They choose whether to accept. Your conversations and memories stay private.</p>
    {data && <p>Your username: <strong>@{data.username}</strong></p>}
    <form className="friend-form" onSubmit={event => { event.preventDefault(); void act('/v1/friends', 'POST', { username }); }}>
      <label htmlFor="friend-username">Friend’s username</label>
      <input id="friend-username" autoCapitalize="none" autoComplete="off" spellCheck={false} pattern="[A-Za-z0-9_]{3,32}" minLength={3} maxLength={32} required value={username} onChange={event => setUsername(event.target.value)} placeholder="e.g. avery" />
      <button className="button primary" disabled={busy || !data}>Send friend request</button>
    </form>
    {error && <p role="alert">{error}</p>}{notice && <p role="status">{notice}</p>}
    <section className="settings-section"><h2>Your people</h2>
      {!data && !error && <p role="status">Loading friends…</p>}
      {data?.items.length === 0 && <p>No connections yet. Invite a friend to create a Sixth account, then enter their username above.</p>}
      {data?.items.map(friend => <article className="friend-card" key={friend.id}><div><strong>{friend.name}</strong><p>@{friend.username} · {friend.status === 'accepted' ? 'Friends' : friend.incoming ? 'Wants to connect' : 'Request sent'}</p><small>Memories are private. No access to your chats.</small></div>
        <div className="friend-actions">{friend.status === 'pending' && friend.incoming && <button className="button primary" disabled={busy} onClick={() => void act(`/v1/friends/${friend.id}/accept`, 'POST')}>Accept</button>}
          <button className="button secondary" disabled={busy} onClick={() => void act(`/v1/friends/${friend.id}`, 'DELETE')}>{friend.status === 'accepted' ? 'Remove' : friend.incoming ? 'Decline' : 'Cancel request'}</button></div>
      </article>)}
    </section><p className="page-description">Shared memories and direct messages between friends are coming later. Friendship currently connects your profiles only.</p>
  </div>;
}
