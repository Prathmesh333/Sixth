import { ArrowUpRight, BrainCircuit, Check, LockKeyhole, MessageCircle, Sparkles, Users } from 'lucide-react';
import type { Workspace } from '../useWorkspace';
import { Mark } from './Brand';
import { GoogleSignIn } from './GoogleSignIn';

export function Welcome({ workspace: w }: { workspace: Workspace }) {
  return <main className="welcome-page sixth-theme">
    <header className="welcome-nav"><a className="brand" href="/" aria-label="Sixth home"><Mark small /><span>sixth<span className="brand-period">.</span></span></a><span className="preview-label"><span />YOUR PERSONAL AI SPACE</span></header>
    <div className="welcome-stage">
      <section className="welcome-copy" aria-labelledby="welcome-title">
        <div className="welcome-kicker"><span />A LITTLE MORE IN SYNC</div>
        <h1 id="welcome-title">Life has a lot<br />of moving parts.<br /><em>Meet your sixth.</em></h1>
        <p className="welcome-intro">A place to think out loud, remember the little things,<br className="desktop-break" /> and turn what’s on your mind into a next step.</p>
        <div className="welcome-auth"><GoogleSignIn onCredential={w.signInGoogle} busy={w.busy} />
          <p className="signin-note"><LockKeyhole size={13} />One Google account. Your own space.</p>
          <p className="consent-note">By continuing, you agree to Sixth storing and processing messages you send to its AI. Hackathon preview — use sample information.</p>
          {w.error && <p className="error-text" role="alert">{w.error}</p>}
        </div>
        <div className="welcome-capabilities"><span><BrainCircuit size={16} />Memory that stays</span><span><Users size={16} />People you choose</span><span><Check size={16} />Actions you approve</span></div>
      </section>
      <aside className="welcome-preview" aria-label="Example of a Sixth conversation">
        <div className="preview-caption"><span className="little-star">✳</span> A SMALL GLIMPSE OF SIXTH <ArrowUpRight size={15} /></div>
        <div className="preview-window"><div className="preview-window-header"><span className="preview-avatar"><Mark small /></span><div><strong>Your everyday, connected.</strong><span>Context grows with you</span></div><Sparkles size={18} /></div>
          <div className="preview-conversation"><div className="preview-user">Maya is vegetarian. Help me plan dinner for four?</div><div className="preview-assistant"><Mark small /><div><p>One less thing to keep in your head.</p><p>I’ll keep Maya’s preference in mind and put together a dinner everyone can share.</p></div></div>
            <div className="preview-memory"><BrainCircuit size={17} /><div><strong>Maya · vegetarian</strong><span>A little context, remembered.</span></div><Check size={16} /></div>
            <div className="preview-plan"><div className="plan-illustration" aria-hidden="true"><span>✳</span><i /><i /><i /></div><div><span className="preview-plan-label">A PLAN TO START WITH</span><h2>Good food.<br />Even better company.</h2><p>Dinner for 4 · Built around your context</p></div></div>
            <div className="preview-review"><LockKeyhole size={13} /><span>You review the next step before it happens.</span></div>
          </div><div className="preview-composer"><MessageCircle size={16} /><span>What’s on your mind?</span><span>↗</span></div>
        </div><div className="preview-footnote"><span />Illustrative conversation · No action taken</div>
      </aside>
    </div><footer className="welcome-footer"><span>A little more context. A little less on your plate.</span><span>Made for your everyday <span aria-hidden="true">✳</span></span></footer>
  </main>;
}
