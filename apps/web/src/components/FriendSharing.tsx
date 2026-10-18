import { useEffect, useState } from "react";
import { api } from "../api";
import type { Fact } from "../types";
interface Context {
  availability_shared: boolean;
  your_sharing: { availability: boolean; memory_ids: string[] };
  memories: Pick<Fact, "id" | "subject" | "predicate" | "value">[];
}
export function FriendSharing({ id }: { id: string }) {
  const [context, setContext] = useState<Context | null>(null);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [availability, setAvailability] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);
  useEffect(() => {
    let cancelled = false;
    void Promise.all([
      api<Context>(`/v1/friends/${id}/context`),
      api<{ items: Fact[] }>("/v1/memory?limit=100"),
    ])
      .then(([c, m]) => {
        if (cancelled) return;
        setContext(c);
        setAvailability(c.your_sharing.availability);
        setSelected(c.your_sharing.memory_ids);
        setFacts(m.items.filter((f) => f.scope_type === "person"));
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);
  async function save() {
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await api(`/v1/friends/${id}/sharing`, "PUT", {
        availability,
        memory_ids: selected,
      });
      setContext(await api<Context>(`/v1/friends/${id}/context`));
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save sharing.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="friend-sharing">
      {error && <p role="alert">{error}</p>}
      {!context ? (
        <p>Loading sharing…</p>
      ) : (
        <>
          <p>
            They {context.availability_shared ? "share" : "do not share"}{" "}
            free/busy access with you.
          </p>
          <label className="check-row">
            <input
              type="checkbox"
              checked={availability}
              onChange={(e) => {
                setAvailability(e.target.checked);
                setSaved(false);
              }}
            />
            Let this friend check my status and busy times
          </label>
          <details>
            <summary>Choose memories to share</summary>
            <p>
              Only selected facts are shared. Chats and source excerpts stay
              private.
            </p>
            {facts.length === 0 && <p>No personal memories to share.</p>}
            {facts.map((f) => (
              <label className="check-row" key={f.id}>
                <input
                  type="checkbox"
                  checked={selected.includes(f.id)}
                  onChange={(e) => {
                    setSelected(
                      e.target.checked
                        ? [...selected, f.id]
                        : selected.filter((id) => id !== f.id),
                    );
                    setSaved(false);
                  }}
                />
                {f.subject} · {f.predicate}: {f.value}
              </label>
            ))}
          </details>
          <button
            className="button secondary"
            disabled={busy}
            onClick={() => void save()}
          >
            Save sharing
          </button>
          {saved && <p role="status">Sharing saved.</p>}
          <h3>Shared with you</h3>
          {context.memories.length ? (
            context.memories.map((f) => (
              <p key={f.id}>
                {f.subject} · {f.predicate}: {f.value}
              </p>
            ))
          ) : (
            <p>No memories shared with you.</p>
          )}
        </>
      )}
    </div>
  );
}

export function FriendSharingPanel({ id }: { id: string }) {
  const [open, setOpen] = useState(false);
  return (
    <details onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary>Manage sharing</summary>
      {open && <FriendSharing id={id} />}
    </details>
  );
}
