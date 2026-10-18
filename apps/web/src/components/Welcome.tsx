import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  BrainCircuit,
  Check,
  CircleCheck,
  Coffee,
  Leaf,
  LockKeyhole,
  MessageCircle,
  Minus,
  Plus,
  RotateCcw,
  ShieldCheck,
  ShoppingBag,
  Users,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { CSSProperties, RefObject } from "react";
import type { Workspace } from "../useWorkspace";
import { Mark } from "./Brand";
import { GoogleSignIn } from "./GoogleSignIn";
import "./landing.css";
import { TechnologyWheel } from "./TechnologyWheel";

const steps = [
  {
    label: "A small detail",
    title: "It starts with you.",
    description:
      "A preference. A person. Something you don’t want to explain all over again.",
    message: "I like my coffee with oat milk.",
    reply:
      "Oat milk for your coffee. I’ll keep that little preference in your context.",
  },
  {
    label: "A dinner together",
    title: "Make room at the table.",
    description:
      "A vegetarian dinner for Maya and three friends. One remembered preference, a meal everyone can share.",
    message: "Plan Maya’s birthday dinner for four.",
    reply:
      "I remember Maya is vegetarian. Let’s make a dinner everyone can share.",
  },
  {
    label: "Room for change",
    title: "People change. Context can too.",
    description:
      "A small correction keeps the picture up to date. You can see what changed and where it came from.",
    message: "Sam prefers green tea now, rather than black tea.",
    reply:
      "I’ve updated Sam’s tea preference. The new detail replaces the old one, with your correction as its source.",
  },
  {
    label: "Your next move",
    title: "You have the final say.",
    description:
      "A simple pantry top-up. Check the items and quantities before preparing a sample cart.",
    message: "Let’s review a pantry top-up: oats, apples, and tea.",
    reply:
      "Here’s your sample list. You review the items first. No checkout, payment, or purchase.",
  },
];
const faq = [
  [
    "What can I try right now?",
    "The working preview supports conversation, sourced memory, dinner planning, and a reviewed sandbox shopping cart. The walkthrough on this page uses sample data and runs entirely in your browser.",
  ],
  [
    "What does Sixth remember?",
    "Details you share, such as someone’s food preferences. In the app, memories include their source and scope. You can correct or forget them. A restriction for one dinner stays specific to that plan.",
  ],
  [
    "Will Sixth buy anything for me?",
    "No. This preview prepares a local test cart after review. It does not make a real purchase, booking, or payment.",
  ],
  [
    "Can I use it on my phone?",
    "Yes. The web app adapts to your phone. Conversation stays central, while memory and plan details open when you need them.",
  ],
  [
    "What’s coming next?",
    "Travel, gifts, voice, and more connections are planned extensions. They are not part of the current meal-planning demo.",
  ],
];

const pantryItems = [
  { name: "Rolled oats", quantity: "500 g" },
  { name: "Apples", quantity: "6" },
  { name: "Green tea", quantity: "1 box" },
];
function PantryItems() {
  return (
    <ul>
      {pantryItems.map((item) => (
        <li key={item.name}>
          <span>{item.name}</span>
          <strong>{item.quantity}</strong>
        </li>
      ))}
    </ul>
  );
}

function RecipeCard({ guests = 4 }: { guests?: number }) {
  return (
    <div className="lp-recipe">
      <img
        src="/landing/vegetable-pasta.webp"
        alt="Illustrative roasted vegetable pasta with tomatoes and basil"
        width="640"
        height="640"
        loading="lazy"
      />
      <div>
        <span className="lp-eyebrow">A LITTLE PLAN, COMING TOGETHER</span>
        <h3>Maya’s birthday dinner</h3>
        <p>
          <Users size={14} /> {guests} guests <span>·</span> <Leaf size={14} />{" "}
          {guests === 6 ? "Dairy-free" : "Vegetarian"}
        </p>
        <div className="lp-recipe-menu">
          Roasted vegetable pasta
          <br />
          <span>Citrus salad · Something everyone can share</span>
        </div>
      </div>
    </div>
  );
}
function HeroArt() {
  const chips = [
    { icon: Leaf, text: "Maya is vegetarian" },
    { icon: Users, text: "A few more friends" },
    { icon: BrainCircuit, text: "The details, remembered" },
  ];
  return (
    <div
      className="lp-hero-art"
      aria-label="Illustration of personal details gathering around Sixth"
    >
      <div className="lp-orbit lp-orbit-one" />
      <div className="lp-orbit lp-orbit-two" />
      <div className="lp-orbit lp-orbit-three" />
      <div className="lp-petal-cluster" aria-hidden="true">
        {Array.from({ length: 6 }, (_, i) => (
          <span key={i} style={{ "--i": i } as CSSProperties} />
        ))}
        <span className="lp-core" />
      </div>
      {chips.map(({ icon: Icon, text }, i) => (
        <div className={`lp-floating-chip lp-chip-${i}`} key={text}>
          <Icon size={17} />
          {text}
        </div>
      ))}
      <div className="lp-art-caption">
        <span className="lp-status-dot" /> A little more in sync.
      </div>
    </div>
  );
}
function Demo({ step, onReview }: { step: number; onReview: () => void }) {
  return (
    <div className="lp-demo-window" data-step={step}>
      <div className="lp-window-bar">
        <span className="lp-window-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span>YOUR EVERYDAY, CONNECTED</span>
        <span className="lp-sample">Sample data</span>
      </div>
      <div className="lp-demo-body">
        <aside className="lp-demo-sidebar" aria-hidden="true">
          <div className="lp-mini-brand">
            <Mark small />
            sixth.
          </div>
          <span className="lp-demo-active">
            <MessageCircle size={16} /> Conversation
          </span>
          <span>
            <BrainCircuit size={16} /> Memory
          </span>
          <span>
            <Users size={16} /> Friends
          </span>
          <span>
            <CircleCheck size={16} /> Plans
          </span>
          <div className="lp-sidebar-bottom">A little less on your plate.</div>
        </aside>
        <div className="lp-demo-chat">
          <div className="lp-demo-chat-heading">
            <span>
              <span className="lp-avatar">A</span> Your space
            </span>
            <span>Just now</span>
          </div>
          <div className="lp-demo-messages" key={step}>
            <div className="lp-user-message">{steps[step].message}</div>
            <div className="lp-assistant-message">
              <Mark small />
              <p>{steps[step].reply}</p>
            </div>
            {step === 0 ? (
              <div className="lp-saved-memory">
                <span className="lp-leaf-icon">
                  <Coffee size={22} />
                </span>
                <div>
                  <strong>You · Coffee with oat milk</strong>
                  <span>Source: what you just shared</span>
                </div>
                <Check size={17} />
              </div>
            ) : step === 1 ? (
              <RecipeCard />
            ) : step === 2 ? (
              <div className="lp-preference-update">
                <span className="lp-eyebrow">SAM’S PREFERENCE · UPDATED</span>
                <div>
                  <span className="lp-old-preference">Black tea</span>
                  <ArrowRight size={17} />
                  <strong>Green tea</strong>
                </div>
                <p>
                  <Check size={14} /> Source: your latest correction
                </p>
              </div>
            ) : (
              <div className="lp-pantry-preview">
                <span className="lp-eyebrow">PANTRY TOP-UP · SAMPLE ITEMS</span>
                <PantryItems />
              </div>
            )}
            {step === 3 && (
              <div className="lp-scope-note">
                <ShieldCheck size={15} /> Test cart only. Nothing purchased.
              </div>
            )}
            {step === 3 && (
              <button
                className="lp-button lp-button-dark lp-demo-review"
                onClick={onReview}
              >
                Review sample cart <ArrowRight size={16} />
              </button>
            )}
          </div>
          <div className="lp-demo-composer" aria-hidden="true">
            <Plus size={18} />
            <span>What’s on your mind?</span>
            <span className="lp-send">
              <ArrowRight size={17} />
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
function MemoryGraph() {
  const [sourceOpen, setSourceOpen] = useState(false);
  return (
    <div className="lp-memory-visual lp-reveal">
      <div className="lp-graph" aria-hidden="true">
        <svg viewBox="0 0 600 380" fill="none">
          <path d="M300 190 C300 60 100 60 100 100 M300 190 C400 190 420 70 490 80 M300 190 C280 310 130 310 100 290 M300 190 C380 190 410 300 490 290" />
        </svg>
        <div className="lp-graph-center">
          <span>M</span>
          <strong>Maya</strong>
          <small>A person, not a prompt.</small>
        </div>
        <div className="lp-graph-node lp-node-a">
          <Leaf size={19} />
          <span>
            Vegetarian<small>Saved preference</small>
          </span>
        </div>
        <div className="lp-graph-node lp-node-b">
          <Users size={19} />
          <span>
            Six guests<small>This plan</small>
          </span>
        </div>
        <div className="lp-graph-node lp-node-c">
          <CircleCheck size={19} />
          <span>
            Birthday dinner<small>A plan together</small>
          </span>
        </div>
        <div className="lp-graph-node lp-node-d">
          <ShieldCheck size={19} />
          <span>
            Dairy-free<small>This dinner only</small>
          </span>
        </div>
      </div>
      <ul className="lp-sr-only">
        <li>Maya’s saved preference: vegetarian.</li>
        <li>Birthday dinner: six guests.</li>
        <li>Dairy-free is scoped to this dinner only.</li>
      </ul>
      <button
        className="lp-source-toggle"
        onClick={() => setSourceOpen(!sourceOpen)}
        aria-expanded={sourceOpen}
      >
        <BrainCircuit size={16} /> Every connection has a little context{" "}
        <Plus size={16} />
      </button>
      {sourceOpen && (
        <blockquote className="lp-source-excerpt">
          “Maya is vegetarian.”
          <span>
            Shared in your sample conversation. The guest count and dairy
            restriction come from the dinner plan update.
          </span>
        </blockquote>
      )}
    </div>
  );
}
function PlanPlayground() {
  const [guests, setGuests] = useState(4);
  return (
    <div className="lp-plan-playground">
      <div className="lp-plan-controls">
        <span>GOOD COMPANY, LESS GUESSWORK</span>
        <div>
          <button
            aria-label="Plan for four guests"
            disabled={guests === 4}
            onClick={() => setGuests(4)}
          >
            <Minus size={18} />
          </button>
          <strong>{guests} guests</strong>
          <button
            aria-label="Plan for six guests"
            disabled={guests === 6}
            onClick={() => setGuests(6)}
          >
            <Plus size={18} />
          </button>
        </div>
      </div>
      <div className="lp-guest-grid">
        {Array.from({ length: guests }, (_, i) => (
          <span key={i} style={{ "--i": i } as CSSProperties}>
            <Users size={25} />
            <small>{i === 0 ? "Maya" : `Guest ${i + 1}`}</small>
          </span>
        ))}
      </div>
      <div className="lp-quantity-row">
        <span>
          Dry pasta <strong>{guests * 100} g</strong>
        </span>
        <span>
          Seasonal vegetables <strong>{guests * 150} g</strong>
        </span>
      </div>
      <p className="lp-plan-footnote" aria-live="polite">
        Illustrative portions for {guests} · Vegetarian · Adjust to your
        appetite
      </p>
    </div>
  );
}
function AppearancePreview() {
  const [theme, setTheme] = useState("paper");
  return (
    <div className="lp-appearance" data-appearance={theme}>
      <div className="lp-appearance-bar">
        <div className="lp-mini-brand">
          <Mark small />
          sixth.
        </div>
        <span>Your own kind of calm.</span>
      </div>
      <div className="lp-appearance-content">
        <Mark />
        <h3>Good morning, Alex.</h3>
        <p>A little more room for what matters.</p>
        <div className="lp-fake-input">
          What’s on your mind? <ArrowRight size={18} />
        </div>
      </div>
      <div
        className="lp-theme-picker"
        role="group"
        aria-label="Preview app appearance"
      >
        {["paper", "dusk", "grove"].map((t) => (
          <button
            key={t}
            aria-pressed={theme === t}
            onClick={() => setTheme(t)}
          >
            <span className={`lp-swatch lp-swatch-${t}`} />
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}
function LandingIntro({ onEnter }: { onEnter?: () => void }) {
  return (
    <>
      <header className="lp-nav">
        <a href="#top" className="lp-brand" aria-label="Sixth home">
          <Mark small />
          sixth.
        </a>
        <nav aria-label="Main navigation">
          <a href="#experience">The experience</a>
          <a href="#memory">Memory</a>
          <a href="#control">Your control</a>
        </nav>
        {onEnter ? (
          <button className="lp-nav-cta" onClick={onEnter}>
            Open workspace <ArrowUpRight size={14} />
          </button>
        ) : (
          <a className="lp-nav-cta" href="#start">
            Meet your Sixth <ArrowUpRight size={14} />
          </a>
        )}
      </header>
      <section className="lp-hero" id="top">
        <div className="lp-hero-copy">
          <span className="lp-eyebrow">
            <span className="lp-status-dot" /> YOUR SIXTH SENSE FOR EVERYDAY
            LIFE
          </span>
          <h1>
            Less on your mind.
            <br />
            <span>More room for life.</span>
          </h1>
          <p>
            The little things, remembered.
            <br />
            The next steps, a little easier.
          </p>
          <a className="lp-button lp-button-dark" href="#experience">
            See Sixth in action <ArrowRight size={17} />
          </a>
          <span className="lp-hero-note">
            A personal assistant that keeps the context.
          </span>
        </div>
        <HeroArt />
        <a className="lp-scroll-cue" href="#intro">
          <ArrowDown size={15} /> A little scroll. A bigger picture.
        </a>
        <span className="lp-hero-index">01 — A LITTLE MORE IN SYNC</span>
      </section>
      <section className="lp-intro lp-section" id="intro">
        <span className="lp-eyebrow lp-reveal">
          LIFE HAS A LOT OF MOVING PARTS.
        </span>
        <h2 className="lp-reveal">
          The people. The plans.
          <br />
          The <span>“don’t let me forget.”</span>
        </h2>
        <div className="lp-intro-bottom lp-reveal">
          <Mark />
          <p>
            Sixth connects the details you share, so the next conversation
            starts a little further along. Less repeating yourself. More getting
            somewhere.
          </p>
        </div>
      </section>
    </>
  );
}

function ContextSections() {
  return (
    <>
      <section className="lp-memory lp-section" id="memory">
        <div className="lp-memory-copy lp-reveal">
          <span className="lp-eyebrow">
            REMEMBER THE PERSON. NOT JUST THE PROMPT.
          </span>
          <h2>
            Little details.
            <br />
            <span>Meaningful connections.</span>
          </h2>
          <p>
            Maya’s vegetarian. Dinner’s now for six. No dairy, just for tonight.
            Sixth keeps the details connected—and keeps their meaning intact.
          </p>
          <a className="lp-text-link" href="#control">
            And you decide what stays <ArrowRight size={16} />
          </a>
        </div>
        <MemoryGraph />
      </section>
      <section className="lp-adapt lp-section">
        <div className="lp-adapt-heading lp-reveal">
          <span className="lp-eyebrow">
            FOR WHEN THE GROUP CHAT GETS BIGGER
          </span>
          <h2>
            A plan that
            <br />
            <span>moves with you.</span>
          </h2>
          <p>
            Life rarely sticks to the first draft.
            <br />
            Your assistant shouldn’t have to.
          </p>
        </div>
        <PlanPlayground />
        <div className="lp-adapt-bottom">
          <span>
            TRY ADDING TWO MORE PEOPLE <ArrowUpRight size={15} />
          </span>
          <p>Change the guest count. Watch the portions follow.</p>
        </div>
      </section>
    </>
  );
}

function ControlSection({ onReview }: { onReview: () => void }) {
  return (
    <>
      <section className="lp-control lp-section" id="control">
        <div className="lp-control-heading lp-reveal">
          <span className="lp-eyebrow">HELPFUL. WITH YOU IN CONTROL.</span>
          <h2>
            A sixth sense.
            <br />
            <span>Not a second decision-maker.</span>
          </h2>
          <p>
            You can see the reasons, change the memories,
            <br />
            and review what happens next.
          </p>
        </div>
        <div className="lp-control-grid">
          <article className="lp-control-card lp-reveal">
            <BrainCircuit />
            <span>01 / UNDERSTAND</span>
            <h3>
              No mysterious
              <br />
              “because AI said so.”
            </h3>
            <p>See the context behind a plan, with the source a click away.</p>
            <div className="lp-evidence-mini">
              <Leaf size={18} />
              <div>
                Maya is vegetarian<small>From your conversation</small>
              </div>
              <Check size={15} />
            </div>
          </article>
          <article className="lp-control-card lp-reveal">
            <ShieldCheck />
            <span>02 / REMEMBER</span>
            <h3>
              Your context.
              <br />
              Your call.
            </h3>
            <p>Correct what changed. Forget what you don’t want to keep.</p>
            <div className="lp-memory-mini">
              <span>Vegetarian</span>
              <span>This dinner only</span>
              <span>Editable by you</span>
            </div>
          </article>
          <article className="lp-control-card lp-reveal">
            <ShoppingBag />
            <span>03 / REVIEW</span>
            <h3>
              A next step.
              <br />
              Never a leap.
            </h3>
            <p>Review the sample items before preparing a local test cart.</p>
            <button className="lp-text-link" onClick={onReview}>
              Try the review <ArrowRight size={16} />
            </button>
          </article>
        </div>
      </section>
    </>
  );
}

function MoreSections() {
  return (
    <>
      <section className="lp-your-space lp-section">
        <div className="lp-space-copy lp-reveal">
          <span className="lp-eyebrow">A SPACE THAT FEELS LIKE YOURS</span>
          <h2>
            Make yourself
            <br />
            <span>a little room.</span>
          </h2>
          <p>
            One calm place for your conversations, memories, people, and plans.
            Choose the appearance that feels right for your day.
          </p>
          <span className="lp-space-note">THREE MOODS. THE SAME SIXTH.</span>
        </div>
        <AppearancePreview />
      </section>
      <section className="lp-current lp-section lp-reveal">
        <span className="lp-eyebrow">SMALL BEGINNINGS. REAL CONNECTIONS.</span>
        <h2>
          Start with dinner.
          <br />
          <span>See where context takes you.</span>
        </h2>
        <div className="lp-current-grid">
          <div>
            <span className="lp-pill">IN THE WORKING PREVIEW</span>
            <h3>One complete everyday loop.</h3>
            <p>
              Conversation. Sourced memory. Meal planning.
              <br />A test cart you review. All connected.
            </p>
          </div>
          <div>
            <span className="lp-pill lp-pill-muted">ON THE HORIZON</span>
            <h3>More of your everyday.</h3>
            <p>
              Travel, gifts, voice, and more connections.
              <br />
              Planned extensions, one step at a time.
            </p>
          </div>
        </div>
      </section>
      <TechnologyWheel />
      <section className="lp-faq lp-section">
        <div>
          <span className="lp-eyebrow">A LITTLE MORE TO KNOW</span>
          <h2>Good questions.</h2>
        </div>
        <div>
          {faq.map(([q, a]) => (
            <details key={q}>
              <summary>
                {q}
                <Plus size={18} />
              </summary>
              <p>{a}</p>
            </details>
          ))}
        </div>
      </section>
    </>
  );
}

function ReviewDialog({
  review,
  prepared,
  onPrepare,
}: {
  review: RefObject<HTMLDialogElement | null>;
  prepared: boolean;
  onPrepare: () => void;
}) {
  return (
    <dialog
      className="lp-review-dialog"
      ref={review}
      aria-labelledby="lp-review-title"
    >
      <div className="lp-dialog-heading">
        <span className="lp-eyebrow">SAMPLE ACTION REVIEW</span>
        <button
          aria-label="Close review"
          onClick={() => review.current?.close()}
        >
          <X size={21} />
        </button>
      </div>
      <h2 id="lp-review-title">
        A little look
        <br />
        before the next step.
      </h2>
      <p>Pantry top-up · Illustrative sample items</p>
      <PantryItems />
      <div className="lp-dialog-safety">
        <ShieldCheck size={20} />
        <span>
          This walkthrough only changes this preview. No account, purchase, or
          external action.
        </span>
      </div>
      {prepared ? (
        <p className="lp-cart-prepared" role="status">
          <CircleCheck size={20} /> Sample cart prepared. Nothing purchased.
        </p>
      ) : (
        <button className="lp-button lp-button-dark" onClick={onPrepare}>
          Prepare sample cart <ArrowRight size={17} />
        </button>
      )}
      <button
        className="lp-dialog-cancel"
        onClick={() => review.current?.close()}
      >
        Back to the page
      </button>
    </dialog>
  );
}

export function Welcome({
  workspace: w,
  onEnter,
}: {
  workspace: Workspace;
  onEnter?: () => void;
}) {
  const root = useRef<HTMLElement>(null);
  const story = useRef<HTMLElement>(null);
  const review = useRef<HTMLDialogElement>(null);
  const [step, setStep] = useState(0);
  const [followScroll, setFollowScroll] = useState(true);
  const [prepared, setPrepared] = useState(false);
  useEffect(() => {
    const element = root.current;
    if (!element) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    const observer = new IntersectionObserver(
      (entries) =>
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("lp-visible");
            observer.unobserve(entry.target);
          }
        }),
      { threshold: 0.12 },
    );
    element
      .querySelectorAll(".lp-reveal")
      .forEach((node) => observer.observe(node));
    let frame = 0;
    function update() {
      frame = 0;
      element?.style.setProperty(
        "--hero-progress",
        String(
          reduced.matches
            ? 0
            : Math.min(1, Math.max(0, window.scrollY / window.innerHeight)),
        ),
      );
      const bounds = story.current?.getBoundingClientRect();
      if (
        bounds &&
        followScroll &&
        !reduced.matches &&
        window.innerHeight >= 600
      ) {
        const progress = Math.max(
          0,
          Math.min(
            0.999,
            -bounds.top / Math.max(1, bounds.height - window.innerHeight),
          ),
        );
        setStep(Math.floor(progress * steps.length));
      }
    }
    function schedule() {
      if (!frame) frame = window.requestAnimationFrame(update);
    }
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    reduced.addEventListener("change", schedule);
    update();
    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", schedule);
      window.removeEventListener("resize", schedule);
      reduced.removeEventListener("change", schedule);
      window.cancelAnimationFrame(frame);
    };
  }, [followScroll]);
  function openReview() {
    setPrepared(false);
    review.current?.showModal();
  }
  return (
    <main className="landing" ref={root}>
      <a className="lp-skip" href="#experience">
        Skip to the demo
      </a>
      <LandingIntro onEnter={w.session ? onEnter : undefined} />
      <section className="lp-story" id="experience" ref={story}>
        <div className="lp-story-sticky">
          <div className="lp-section-heading">
            <div>
              <span className="lp-eyebrow">A SMALL GLIMPSE OF SIXTH</span>
              <h2>
                One detail.
                <br />
                <span>A different kind of help.</span>
              </h2>
            </div>
            <p>
              Different moments. The same little bit of help.
              <br className="lp-desktop-break" /> Explore four illustrative
              everyday examples.
            </p>
          </div>
          <div
            className="lp-story-tabs"
            role="group"
            aria-label="Demo chapters"
          >
            {steps.map((s, i) => (
              <button
                key={s.label}
                aria-pressed={step === i}
                onClick={() => {
                  setFollowScroll(false);
                  setStep(i);
                }}
              >
                <span>0{i + 1}</span>
                {s.label}
                <i />
              </button>
            ))}
          </div>
          <div className="lp-story-stage">
            <div className="lp-story-caption-shell">
              <div className="lp-caption-viewport">
                <div
                  className="lp-caption-track"
                  style={{ transform: `translateX(-${step * 100}%)` }}
                >
                  {steps.map((chapter, index) => (
                    <div
                      className="lp-story-caption"
                      key={chapter.label}
                      aria-hidden={index !== step}
                      inert={index !== step}
                    >
                      <span className="lp-eyebrow">0{index + 1} / 04</span>
                      <h3>{chapter.title}</h3>
                      <p>{chapter.description}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="lp-demo-navigation">
                <button
                  aria-label="Previous demo chapter"
                  onClick={() => {
                    setFollowScroll(false);
                    setStep(Math.max(0, step - 1));
                  }}
                  disabled={step === 0}
                >
                  <ArrowRight size={18} className="lp-reverse" />
                </button>
                <button
                  aria-label="Next demo chapter"
                  onClick={() => {
                    setFollowScroll(false);
                    setStep(Math.min(3, step + 1));
                  }}
                  disabled={step === 3}
                >
                  <ArrowRight size={18} />
                </button>
              </div>
            </div>
            <Demo step={step} onReview={openReview} />
          </div>
          <div className="lp-story-bottom">
            <span>
              <ShieldCheck size={13} /> Interactive walkthrough · Sample data ·
              No purchase
            </span>
            <button
              aria-pressed={followScroll}
              onClick={() => setFollowScroll(!followScroll)}
            >
              <RotateCcw size={13} />
              {followScroll
                ? "Pause scroll progression"
                : "Follow scroll again"}
            </button>
          </div>
        </div>
      </section>
      <ContextSections />
      <ControlSection onReview={openReview} />
      <MoreSections />
      <section className="lp-start lp-section" id="start">
        <div className="lp-start-symbol" aria-hidden="true">
          <Mark />
        </div>
        <span className="lp-eyebrow">ONE LESS THING TO KEEP IN YOUR HEAD.</span>
        <h2>
          What’s on
          <br />
          <span>your mind?</span>
        </h2>
        <p>Meet your sixth sense for everyday life.</p>
        <div className="lp-auth">
          {w.session ? (
            <button className="lp-button lp-button-dark" onClick={onEnter}>
              Return to your workspace <ArrowRight size={17} />
            </button>
          ) : (
            <GoogleSignIn onCredential={w.signInGoogle} busy={w.busy} />
          )}
          <p className="lp-auth-note">
            <LockKeyhole size={12} />{" "}
            {w.session
              ? `Signed in as ${w.session.name}. Your context is waiting.`
              : "One Google account. Your own space."}
          </p>
          {!w.session && (
            <p className="lp-consent">
              By continuing, you agree to Sixth storing and processing messages
              you send to its AI. Hackathon preview—use sample information.
            </p>
          )}
          {w.error && (
            <p role="alert" className="lp-auth-error">
              {w.error}
            </p>
          )}
        </div>
        <a className="lp-text-link" href="#experience">
          Or explore the sample walkthrough <ArrowRight size={15} />
        </a>
      </section>
      <footer className="lp-footer">
        <a className="lp-brand" href="#top">
          <Mark small />
          sixth.
        </a>
        <span>A little more context. A little less on your plate.</span>
        <a
          href="https://github.com/Prathmesh333/Sixth"
          target="_blank"
          rel="noreferrer"
        >
          Built for the everyday <ArrowUpRight size={13} />
        </a>
        <small>Hackathon preview · Sample data</small>
      </footer>
      <ReviewDialog
        review={review}
        prepared={prepared}
        onPrepare={() => setPrepared(true)}
      />
    </main>
  );
}
