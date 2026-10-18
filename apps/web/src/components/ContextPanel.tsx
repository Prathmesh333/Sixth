import {
  ArrowRight,
  BrainCircuit,
  CheckCheck,
  Database,
  X,
} from "lucide-react";
import type { Task } from "../types";
import type { Workspace } from "../useWorkspace";

export function ContextPanel({
  workspace: w,
  evidence,
  onClose,
}: {
  workspace: Workspace;
  evidence: Task | null;
  onClose: () => void;
}) {
  const facts = evidence?.evidence || w.facts.slice(0, 4);
  return (
    <aside
      className={`context-panel ${evidence ? "evidence-open" : ""}`}
      aria-label={evidence ? "Evidence for this decision" : "Personal context"}
    >
      <div className="context-heading">
        <span>{evidence ? "BEHIND THIS DECISION" : "YOUR CONTEXT"}</span>
        <button
          className="icon-button"
          aria-label={evidence ? "Close evidence" : "Close personal context"}
          onClick={onClose}
        >
          <X size={17} />
        </button>
      </div>
      <h2>
        {evidence ? "A reason for every choice." : "The little things matter."}
      </h2>
      <p className="context-intro">
        {evidence
          ? "These are the memories behind this response, with the words they came from."
          : "A few things you share can make the next request feel a lot more familiar."}
      </p>
      <div className="context-divider" />
      <div className="context-section-title">
        <BrainCircuit size={15} />
        <span>{evidence ? "Connected evidence" : "Kept in mind"}</span>
        <span>{facts.length}</span>
      </div>
      {facts.length ? (
        facts.map((fact) => (
          <div className="context-fact" key={fact.id}>
            <div className="fact-person">
              <span className="person-dot">{fact.subject[0]}</span>
              <strong>{fact.subject}</strong>
              <CheckCheck size={13} />
            </div>
            <p>
              {fact.predicate === "avoids" ? "Avoids " : ""}
              {fact.value}
            </p>
            <small>
              {fact.scope_type === "event"
                ? "For this plan only"
                : "Shared by you"}{" "}
              · v{fact.version}
            </small>
            {evidence && <blockquote>{fact.sources[0]?.excerpt}</blockquote>}
          </div>
        ))
      ) : (
        <div className="context-empty">
          <span>✳</span>
          <p>
            Nothing assumed.
            <br />
            Start with something you’d like me to remember.
          </p>
        </div>
      )}
      {evidence && (
        <div className="evidence-path">
          <span>Source</span>
          <ArrowRight size={12} />
          <span>Memory</span>
          <ArrowRight size={12} />
          <span>Decision</span>
        </div>
      )}
      <div className="context-bottom">
        <Database size={17} />
        <div>
          <strong>
            {w.status?.memory.backend === "falkordb"
              ? "Connected through FalkorDB"
              : "Running on fixture memory"}
          </strong>
          <p>
            {w.status?.memory.backend === "falkordb"
              ? "Relationships ground your assistant’s choices."
              : "Connect FalkorDB to enable the real graph backend."}
          </p>
        </div>
      </div>
    </aside>
  );
}
