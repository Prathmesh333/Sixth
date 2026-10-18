import type { Task } from "../types";
export function SchedulingCard({
  task,
  busy,
  onDecision,
}: {
  task: Task;
  busy: boolean;
  onDecision: (decision: "approve" | "reject") => void;
}) {
  const data = task.scheduling;
  if (!data) return null;
  return (
    <section className="schedule-card" aria-label="Scheduling review">
      <strong>{data.title}</strong>
      {data.starts_at && (
        <p>
          {new Date(data.starts_at).toLocaleString()} –{" "}
          {data.ends_at && new Date(data.ends_at).toLocaleString()}
        </p>
      )}
      {data.friends?.length ? (
        <p>People: {data.friends.map((name) => `@${name}`).join(", ")}</p>
      ) : null}
      {data.starts_at && (
        <small>
          Shown in {Intl.DateTimeFormat().resolvedOptions().timeZone}
        </small>
      )}
      {data.results?.map((item) => (
        <p key={item.friend.name}>
          {item.friend.name}: {item.status.replaceAll("_", " ")}
        </p>
      ))}
      {task.status === "awaiting_input" && task.action && (
        <div className="friend-actions">
          <button
            className="button primary"
            disabled={busy}
            onClick={() => onDecision("approve")}
          >
            {data.action_label || "Confirm"}
          </button>
          <button
            className="button secondary"
            disabled={busy}
            onClick={() => onDecision("reject")}
          >
            Not now
          </button>
        </div>
      )}
      {task.result && <p role="status">Saved and verified.</p>}
    </section>
  );
}
