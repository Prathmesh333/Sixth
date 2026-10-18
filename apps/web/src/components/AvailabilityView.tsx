import { useEffect, useState } from "react";
import { api } from "../api";
interface Slot {
  id: string;
  title: string;
  starts_at: string;
  ends_at: string;
  meeting_id?: string;
}
interface Person {
  name: string;
  username: string;
  response?: string;
}
interface Invitation extends Slot {
  kind: "meeting" | "availability_request";
  status: string;
  is_organizer: boolean;
  your_response: string;
  participants: Person[];
  organizer: Person;
}
interface Friend extends Person {
  id: string;
  status: string;
}
interface Presence {
  status: string;
  until: string | null;
}
const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
const time = (value: string) =>
  new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
export function AvailabilityView({ demo = false }: { demo?: boolean }) {
  const [slots, setSlots] = useState<Slot[]>([]);
  const [inbox, setInbox] = useState<Invitation[]>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [presence, setPresence] = useState<Presence>({
    status: "unknown",
    until: null,
  });
  const [flag, setFlag] = useState("unknown");
  const [until, setUntil] = useState("");
  const [title, setTitle] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  async function load(isCurrent: () => boolean = () => true) {
    const [a, b, c, d] = await Promise.all([
      api<{ items: Slot[] }>("/v1/calendar/events"),
      api<{ items: Invitation[] }>("/v1/scheduling/inbox"),
      demo
        ? Promise.resolve({ items: [] as Friend[] })
        : api<{ items: Friend[] }>("/v1/friends"),
      api<Presence>("/v1/availability"),
    ]);
    if (!isCurrent()) return;
    setSlots(a.items);
    setInbox(b.items);
    setFriends(c.items.filter((f) => f.status === "accepted"));
    setPresence(d);
    setFlag(d.status);
    setReady(true);
  }
  useEffect(() => {
    let active = true;
    void load(() => active).catch((err) => {
      if (active) setError(err.message);
    });
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    let cancelled = false;
    async function refreshInbox() {
      if (document.hidden) return;
      try {
        const result = await api<{ items: Invitation[] }>(
          "/v1/scheduling/inbox",
        );
        if (!cancelled) setInbox(result.items);
      } catch {
        /* The manual refresh control reports connection errors. */
      }
    }
    const timer = window.setInterval(() => void refreshInbox(), 20000);
    window.addEventListener("focus", refreshInbox);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
      window.removeEventListener("focus", refreshInbox);
    };
  }, []);
  useEffect(() => {
    if (!presence.until) return;
    const delay = Math.max(0, new Date(presence.until).getTime() - Date.now()) + 250;
    const timer = window.setTimeout(() => {
      void api<Presence>("/v1/availability").then(setPresence).catch(() => {});
    }, Math.min(delay, 2147483647));
    return () => window.clearTimeout(timer);
  }, [presence.until]);

  async function act(path: string, method = "POST", body?: unknown) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api(path, method, body);
      await load();
      setNotice("Updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Please try again.");
    } finally {
      setBusy(false);
    }
  }
  function body() {
    return {
      title: title.trim() || "Busy",
      starts_at: new Date(start).toISOString(),
      ends_at: new Date(end).toISOString(),
      timezone: zone,
    };
  }
  async function check() {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const query = new URLSearchParams({ ...body() });
      const results = await Promise.all(
        friends
          .filter((f) => selected.includes(f.username))
          .map(async (f) => {
            const result = await api<{ status: string }>(
              `/v1/friends/${f.id}/availability?${query}`,
            );
            return `${f.name}: ${result.status.replaceAll("_", " ")}`;
          }),
      );
      setNotice(results.join(" · "));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Check failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="page-view availability-view">
      <div className="eyebrow">A LITTLE ROOM FOR YOUR PEOPLE</div>
      <h1>
        Your time.
        <br />
        <em>Simply shared.</em>
      </h1>
      <p className="page-description">
        Set a status, save a busy slot, or ask a friend. Only friends you allow
        can check your free/busy times. An empty schedule means no recorded
        conflict.
      </p>
      {error && <p role="alert">{error}</p>}
      {notice && <p role="status">{notice}</p>}
      <section className="settings-section">
        <h2>
          Right now · {presence.status}
          {presence.until && ` until ${time(presence.until)}`}
        </h2>
        <form
          className="availability-form"
          onSubmit={(e) => {
            e.preventDefault();
            void act("/v1/availability", "PUT", {
              status: flag,
              until: until ? new Date(until).toISOString() : null,
            });
          }}
        >
          <div>
            <label htmlFor="availability-status">Status</label>
            <select
              id="availability-status"
              disabled={!ready || busy}
              value={flag}
              onChange={(e) => setFlag(e.target.value)}
            >
              <option value="unknown">Not set</option>
              <option value="available">Available</option>
              <option value="busy">Busy</option>
              <option value="away">Away</option>
            </select>
          </div>
          <label>
            Until (optional)
            <input
              type="datetime-local"
              value={until}
              onChange={(e) => setUntil(e.target.value)}
            />
          </label>
          <button className="button primary" disabled={busy}>
            Update status
          </button>
        </form>
      </section>
      <section className="settings-section">
        <h2>Make a little space</h2>
        <p>
          Times shown in {zone}. Invitations stay pending until each person
          accepts and the organizer confirms.
        </p>
        <form
          className="availability-form"
          onSubmit={(e) => {
            e.preventDefault();
            void act("/v1/calendar/events", "POST", body());
          }}
        >
          <label>
            What’s the plan?
            <input
              maxLength={160}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Focus time or coffee"
            />
          </label>
          <label>
            Starts
            <input
              type="datetime-local"
              required
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </label>
          <label>
            Ends
            <input
              type="datetime-local"
              required
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </label>
          <button className="button primary" disabled={busy}>
            Save my busy slot
          </button>
          <fieldset>
            <legend>Include friends</legend>
            {friends.length === 0 && (
              <p>Add an accepted friend in Friends to invite them.</p>
            )}
            {friends.map((f) => (
              <label className="check-row" key={f.id}>
                <input
                  type="checkbox"
                  checked={selected.includes(f.username)}
                  onChange={(e) =>
                    setSelected(
                      e.target.checked
                        ? [...selected, f.username]
                        : selected.filter((name) => name !== f.username),
                    )
                  }
                />
                {f.name} · @{f.username}
              </label>
            ))}
          </fieldset>
          <div className="friend-actions">
            <button
              className="button secondary"
              type="button"
              disabled={busy || !selected.length || !start || !end}
              onClick={() => void check()}
            >
              Check availability
            </button>
            <button
              className="button secondary"
              type="button"
              disabled={busy || !selected.length || !start || !end}
              onClick={() =>
                void act("/v1/scheduling/availability_request", "POST", {
                  ...body(),
                  friend_usernames: selected,
                })
              }
            >
              Ask if available
            </button>
            <button
              className="button primary"
              type="button"
              disabled={busy || !selected.length || !start || !end}
              onClick={() =>
                void act("/v1/scheduling/meeting", "POST", {
                  ...body(),
                  friend_usernames: selected,
                })
              }
            >
              Send invitation
            </button>
          </div>
        </form>
      </section>
      <section className="settings-section">
        <h2>Your busy slots</h2>
        {!slots.length && <p>No busy slots recorded.</p>}
        {slots.map((slot) => (
          <article className="schedule-card" key={slot.id}>
            <strong>{slot.title}</strong>
            <p>
              {time(slot.starts_at)} – {time(slot.ends_at)}
            </p>
            {!slot.meeting_id && (
              <button
                className="button secondary"
                disabled={busy}
                onClick={() =>
                  void act(`/v1/calendar/events/${slot.id}`, "DELETE")
                }
              >
                Remove slot
              </button>
            )}
          </article>
        ))}
      </section>
      <section className="settings-section">
        <div className="friend-actions">
          <h2>Invitations & questions</h2>
          <button
            className="button secondary"
            disabled={busy}
            onClick={() => void act("/v1/scheduling/inbox", "GET")}
          >
            Refresh inbox
          </button>
        </div>
        {!inbox.length && <p>You’re all caught up.</p>}
        {inbox.map((item) => (
          <article className="schedule-card" key={item.id}>
            <strong>{item.title}</strong>
            <p>
              {time(item.starts_at)} – {time(item.ends_at)}
            </p>
            <p>
              {item.kind === "availability_request"
                ? "Availability question"
                : "Invitation"}{" "}
              from {item.organizer.name} · {item.status.replaceAll("_", " ")}
            </p>
            <p>
              {item.participants
                .map((p) => `${p.name}: ${p.response}`)
                .join(" · ")}
            </p>
            <div className="friend-actions">
              {!item.is_organizer &&
                !["booked", "cancelled"].includes(item.status) &&
                new Date(item.ends_at) > new Date() && (
                  <>
                    <button
                      className="button primary"
                      disabled={busy || item.your_response === "accepted"}
                      onClick={() =>
                        void act(
                          `/v1/scheduling/${item.kind}/${item.id}/respond`,
                          "POST",
                          { accepted: true },
                        )
                      }
                    >
                      {item.kind === "meeting" ? "Accept" : "I’m available"}
                    </button>
                    <button
                      className="button secondary"
                      disabled={busy || item.your_response === "declined"}
                      onClick={() =>
                        void act(
                          `/v1/scheduling/${item.kind}/${item.id}/respond`,
                          "POST",
                          { accepted: false },
                        )
                      }
                    >
                      {item.kind === "meeting" ? "Decline" : "Unavailable"}
                    </button>
                  </>
                )}
              {item.is_organizer &&
                item.kind === "meeting" &&
                item.status === "ready_to_book" && (
                  <button
                    className="button primary"
                    disabled={busy}
                    onClick={() =>
                      void act(`/v1/scheduling/meeting/${item.id}/confirm`)
                    }
                  >
                    Confirm booking
                  </button>
                )}
              {item.is_organizer &&
                item.kind === "meeting" &&
                item.status !== "cancelled" && (
                  <button
                    className="button secondary"
                    disabled={busy}
                    onClick={() =>
                      void act(`/v1/scheduling/meeting/${item.id}/cancel`)
                    }
                  >
                    Cancel for everyone
                  </button>
                )}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
