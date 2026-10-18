import { useEffect, useState } from "react";
import { X } from "lucide-react";
import type { Task, Theme, View } from "./types";
import { useWorkspace } from "./useWorkspace";
import { Mark } from "./components/Brand";
import { Sidebar } from "./components/Sidebar";
import { Chat } from "./components/Chat";
import { ContextPanel } from "./components/ContextPanel";
import { MemoryView } from "./components/MemoryView";
import { PlansView } from "./components/PlansView";
import { SettingsView } from "./components/SettingsView";
import { WorkspaceHeader } from "./components/WorkspaceHeader";
import { Welcome } from "./components/Welcome";
import { FriendsView } from "./components/FriendsView";

function initialTheme(): Theme {
  try {
    const value = localStorage.getItem("sixth-theme");
    return value === "dusk" || value === "grove" ? value : "paper";
  } catch {
    return "paper";
  }
}

export function App() {
  const workspace = useWorkspace();
  const [view, setView] = useState<View>("chat");
  const [theme, setTheme] = useState<Theme>(initialTheme);
  const [navOpen, setNavOpen] = useState(false);
  const [evidence, setEvidence] = useState<Task | null>(null);
  const [contextOpen, setContextOpen] = useState(false);
  const [showLanding, setShowLanding] = useState(false);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("sixth-theme", theme);
    } catch {
      /* Private browsing may disable storage. */
    }
  }, [theme]);
  useEffect(() => {
    function escape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setNavOpen(false);
        setEvidence(null);
        setContextOpen(false);
      }
    }
    window.addEventListener("keydown", escape);
    return () => window.removeEventListener("keydown", escape);
  }, []);

  function navigate(next: View) {
    setView(next);
    setEvidence(null);
    setContextOpen(false);
  }
  if (workspace.starting)
    return (
      <main className="login-screen sixth-theme">
        <Mark />
        <p role="status">Finding your place…</p>
      </main>
    );
  if (!workspace.session || showLanding)
    return (
      <Welcome workspace={workspace} onEnter={() => setShowLanding(false)} />
    );
  return (
    <div className="app-shell sixth-theme">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <Sidebar
        workspace={workspace}
        view={view}
        onView={navigate}
        open={navOpen}
        onClose={() => setNavOpen(false)}
        onHome={() => {
          setNavOpen(false);
          setShowLanding(true);
          window.scrollTo(0, 0);
        }}
      />
      <div className="main-shell" inert={navOpen}>
        <WorkspaceHeader
          view={view}
          status={workspace.status}
          contextOpen={contextOpen}
          onNavigation={() => setNavOpen(true)}
          onContext={() => setContextOpen(!contextOpen)}
        />
        {workspace.error && (
          <div className="error-banner" role="alert">
            <span>{workspace.error}</span>
            <button
              className="icon-button"
              aria-label="Dismiss error"
              onClick={workspace.clearError}
            >
              <X size={16} />
            </button>
          </div>
        )}
        <main id="main" className="main-content">
          {view === "chat" && (
            <Chat
              workspace={workspace}
              onEvidence={(task) => {
                setEvidence(task);
                setContextOpen(true);
              }}
            />
          )}
          {view === "memory" && (
            <MemoryView workspace={workspace} onChat={() => navigate("chat")} />
          )}
          {view === "friends" && (
            <FriendsView key={workspace.session.account} />
          )}
          {view === "plans" && (
            <PlansView
              workspace={workspace}
              onOpen={(id) => {
                if (id) void workspace.selectConversation(id);
                else workspace.newConversation();
                navigate("chat");
              }}
            />
          )}
          {view === "settings" && (
            <SettingsView
              workspace={workspace}
              theme={theme}
              onTheme={setTheme}
            />
          )}
        </main>
      </div>
      {view === "chat" && (
        <div
          className={`context-shell ${contextOpen ? "expanded" : ""}`}
          inert={navOpen}
        >
          <ContextPanel
            workspace={workspace}
            evidence={evidence}
            onClose={() => {
              setEvidence(null);
              setContextOpen(false);
            }}
          />
        </div>
      )}
    </div>
  );
}
