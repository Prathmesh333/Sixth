import { useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { ArrowUpRight, Pause, Play } from "lucide-react";
import { Mark } from "./Brand";
import "./technology-wheel.css";

const technologies = [
  {
    id: "falkordb",
    name: "FalkorDB",
    role: "Graph memory",
    href: "https://www.falkordb.com/",
  },
  { id: "react", name: "React", role: "Interface", href: "https://react.dev/" },
  {
    id: "typescript",
    name: "TypeScript",
    role: "Typed frontend",
    href: "https://www.typescriptlang.org/",
  },
  { id: "vite", name: "Vite", role: "Web build", href: "https://vite.dev/" },
  {
    id: "python",
    name: "Python",
    role: "Agent runtime",
    href: "https://www.python.org/",
  },
  {
    id: "fastapi",
    name: "FastAPI",
    role: "Application API",
    href: "https://fastapi.tiangolo.com/",
  },
  {
    id: "langgraph",
    name: "LangGraph",
    role: "Persistent workflows",
    href: "https://docs.langchain.com/oss/python/langgraph/overview",
  },
  {
    id: "postgresql",
    name: "PostgreSQL",
    role: "Hosted storage option",
    href: "https://www.postgresql.org/",
  },
];

export function TechnologyWheel() {
  const wheel = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.isIntersecting),
      { threshold: 0.1 },
    );
    if (wheel.current) observer.observe(wheel.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      className="lp-technologies lp-section"
      id="made-using"
      aria-labelledby="technology-title"
    >
      <div className="lp-tech-copy">
        <span className="lp-eyebrow">MADE USING</span>
        <h2 id="technology-title">
          Good things.
          <br />
          <span>Built together.</span>
        </h2>
        <p>
          A thoughtful interface. Memory with connections. A little coordination
          behind every next step.
        </p>
        <a
          className="lp-falkor-credit"
          href="https://www.falkordb.com/"
          target="_blank"
          rel="noreferrer"
        >
          <img
            src="/landing/technologies/falkordb.svg"
            width="38"
            height="35"
            alt=""
            loading="lazy"
          />
          <span>
            Built with FalkorDB
            <small>The graph layer behind connected memory.</small>
          </span>
          <ArrowUpRight size={16} />
        </a>
        <p className="lp-tech-detail">
          React & TypeScript for the experience. Python, FastAPI & LangGraph for
          the runtime. PostgreSQL is a hosted storage option; the offline demo
          uses fixture memory.
        </p>
        <button
          className="lp-wheel-toggle"
          onClick={() => setPaused(!paused)}
          aria-pressed={paused}
          aria-controls="technology-orbit"
        >
          {paused ? <Play size={14} /> : <Pause size={14} />}
          {paused ? "Resume logo animation" : "Pause logo animation"}
        </button>
      </div>
      <div
        className="lp-tech-wheel"
        ref={wheel}
        data-running={visible && !paused}
      >
        <div className="lp-tech-wheel-center" aria-hidden="true">
          <Mark />
          <strong>sixth.</strong>
          <span>CONNECTED BY DESIGN</span>
        </div>
        <ul
          className="lp-tech-rotor"
          id="technology-orbit"
          aria-label="Technologies used to build Sixth"
        >
          {technologies.map((tech, i) => (
            <li
              className="lp-tech-spoke"
              key={tech.id}
              style={{ "--angle": `${i * 45}deg` } as CSSProperties}
            >
              <div className="lp-tech-badge">
                <a
                  href={tech.href}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={`${tech.name} — ${tech.role}`}
                  title={`${tech.name} · ${tech.role}`}
                >
                  <img
                    src={`/landing/technologies/${tech.id}.svg`}
                    width="32"
                    height="32"
                    alt=""
                    loading="lazy"
                  />
                  <span>{tech.name}</span>
                </a>
              </div>
            </li>
          ))}
        </ul>
        <span className="lp-tech-wheel-note">
          A FEW GOOD TOOLS. ONE CONNECTED EXPERIENCE.
        </span>
      </div>
    </section>
  );
}
