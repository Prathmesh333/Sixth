import { Menu, PanelRight } from "lucide-react";
import type { Status, View } from "../types";

const titles: Record<View, string> = {
  chat: "Conversation",
  plans: "Plans",
  memory: "Memory",
  friends: "Friends",
  availability: "Availability",
  settings: "Settings",
};

export function WorkspaceHeader({
  view,
  status,
  onNavigation,
  onContext,
  contextOpen,
}: {
  view: View;
  status: Status | null;
  onNavigation: () => void;
  onContext: () => void;
  contextOpen: boolean;
}) {
  const graphConfigured = status?.memory.backend === "falkordb";
  const connected = graphConfigured && status.memory.connected;
  const label = graphConfigured
    ? connected
      ? "Graph connected"
      : "Graph unavailable"
    : "Local demo";
  return (
    <header className="topbar">
      <div>
        <button
          className="icon-button mobile-menu"
          aria-label="Open navigation"
          onClick={onNavigation}
        >
          <Menu size={20} />
        </button>
        <span className="breadcrumb">
          Your workspace <span>/</span> <strong>{titles[view]}</strong>
        </span>
      </div>
      <div className="topbar-right">
        <span className="connection-label">
          <span
            className={
              connected ? "connection-dot connected" : "connection-dot"
            }
          />
          {label}
        </span>
        {view === "chat" && (
          <button
            className="icon-button"
            aria-label="Show personal context"
            aria-expanded={contextOpen}
            onClick={onContext}
          >
            <PanelRight size={18} />
          </button>
        )}
      </div>
    </header>
  );
}
