import { Session, ModelOption } from '../types/chat';
import { Artifact } from '../types/artifact';

export const MODEL_OPTIONS: ModelOption[] = [
  {
    id: 'openai-cloud',
    name: 'OpenAI (GPT-4o mini)',
    provider: 'Cloud',
    note: 'Cloud — high reasoning capacity',
    available: true,
    modelIdentifier: 'OpenAI · Cloud',
  },
  {
    id: 'ollama-local',
    name: 'Ollama (Llama 3.2 3B)',
    provider: 'Local',
    note: 'Local — private inference (Llama 3.2 3B detected)',
    available: true,
    modelIdentifier: 'Ollama · Local',
  },
];

export const MOCK_ARTIFACTS: Record<string, Artifact> = {
  'artifact-1': {
    id: 'artifact-1',
    sessionId: 'session-1',
    title: 'B2B SaaS Retention Playbook: Cohort Flattening and Natural Frequency',
    type: 'markdown',
    wordCount: 1240,
    sourceCount: 3,
    createdAt: '2 hours ago',
    content: `# B2B SaaS Retention Playbook: Cohort Flattening and Natural Frequency

*Synthesized from transcript evidence across Lenny's Podcast episodes with Casey Winters, Elena Verna, and Brian Balfour.*

---

## Executive Summary

True Product-Market Fit (PMF) in B2B SaaS is not measured by acquisition velocity or conversion rates; it is revealed exclusively by the behavior of the retention curve asymptote. If your cohort retention curve does not flatten parallel to the x-axis, no amount of top-of-funnel optimization can preserve enterprise value.

This playbook synthesizes the empirical frameworks articulated by Casey Winters (former Chief Product Officer at Eventbrite, Growth Lead at Pinterest) and Elena Verna (Head of Growth at Lovable, former interim CMO at Miro/Amplitude).

---

## 1. The Asymptote Imperative: Measuring Real PMF

Most early-stage SaaS companies mistake positive customer feedback for Product-Market Fit. In Episode 42, Casey Winters warns against "leaky bucket syndrome":

> "Product-market fit is revealed when a cohort curve stops dropping and runs flat. If you don't have that horizontal floor, nothing else you do matters. You are merely renting users rather than building an enduring business."

### Key Retention Thresholds by Business Model

| Segment | Minimum Acceptable Floor | Good Benchmark | Elite / World Class |
| :--- | :--- | :--- | :--- |
| **SMB (<20 seats)** | 55% - 65% annual floor | 75% - 82% | 100% - 110% net |
| **Mid-Market (20-250 seats)** | 75% - 84% annual floor | 85% - 90% | 115% - 128% net |
| **Enterprise (>250 seats)** | 88% - 92% annual floor | 93% - 96% | 130%+ net |

---

## 2. Natural Problem Frequency: The Core Diagnostic

A fatal error when designing retention mechanics is attempting to manufacture artificial daily habits for problems that occur weekly, monthly, or quarterly.

Elena Verna (Episode 88) breaks down the alignment formula:

1. **Daily Cadence:** Communication tools (Slack, Teams), task dispatchers, IDEs.
2. **Weekly Cadence:** Project management (Linear, Asana), sprint tracking, analytics dashboards.
3. **Monthly / Quarterly Cadence:** Financial reporting, payroll, tax compliance, hiring pipeline reviews.

\`\`\`typescript
// Retention Metric Evaluation Pattern
interface CohortHealth {
  cohortMonth: string;
  month3Retention: number; // Target: >65%
  month6Retention: number; // Target: flat compared to month 3 (<2% delta)
  asymptoteEstablished: boolean;
}

function evaluatePMFHealth(cohort: CohortHealth): 'HEALTHY' | 'CHURN_TRAP' {
  if (cohort.month6Retention >= cohort.month3Retention - 0.02) {
    return 'HEALTHY';
  }
  return 'CHURN_TRAP';
}
\`\`\`

---

## 3. Four Tactical Levers to Bend the Curve Upward

To transition from an unstable curve to a flattened asymptote, growth teams must execute four consecutive interventions:

### Lever 1: Aggressive Qualification & Anti-Targeting
Stop onboarding users outside your core Ideal Customer Profile (ICP). Churn from non-ICP users contaminates product metrics and leads roadmap decisions astray.

### Lever 2: Time-to-Value (TTV) Compression
Elena Verna emphasizes that onboarding should not aim to explain the entire surface area of your tool. Instead, guide the user to their first "aha" moment within the first session.

### Lever 3: Habit Loop Anchoring
Identify existing workflows within the organization and tie notifications directly to real-world team triggers rather than arbitrary marketing emails.

### Lever 4: In-Product Expansion Triggers
Organic expansion should be built directly into the workflow—shared dashboards, multi-player collaboration, and shared artifacts create natural invitations for peers.

---

## 4. Operational Checklist for Growth Leads

- [ ] Audit last 6 cohorts: verify whether retention curves flatten after month 3.
- [ ] Measure natural frequency: survey your best 20 retained accounts on when they naturally encounter the core problem.
- [ ] Remove friction from the single activation workflow responsible for 80% of retained users.
- [ ] Implement event-based warning signals for accounts dropping below baseline frequency.
`,
  },
  'artifact-2': {
    id: 'artifact-2',
    sessionId: 'session-2',
    title: 'Interactive PMF Survey Calculator & Retention Simulator',
    type: 'html',
    wordCount: 420,
    sourceCount: 2,
    createdAt: '1 day ago',
    allowScripts: false,
    content: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 24px;
      color: #14171F;
      background: #FDFCFA;
      line-height: 1.5;
    }
    h2 { font-size: 18px; margin-top: 0; margin-bottom: 8px; font-weight: 600; }
    p { font-size: 14px; color: #3A4050; margin-bottom: 20px; }
    .card {
      background: #F3F1EC;
      border: 1px solid #E4E1D8;
      border-radius: 6px;
      padding: 16px;
      margin-bottom: 16px;
    }
    .metric {
      font-size: 28px;
      font-weight: 700;
      color: #2F5D50;
      font-family: "IBM Plex Mono", monospace;
    }
    .label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #6B7280;
      margin-top: 4px;
    }
    .bar-container {
      background: #EAE7DF;
      height: 12px;
      border-radius: 999px;
      margin-top: 12px;
      overflow: hidden;
    }
    .bar {
      height: 100%;
      background: #2F5D50;
      width: 58%;
      border-radius: 999px;
    }
    .slider-group {
      margin-top: 16px;
    }
    label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 6px;
    }
    input[type="range"] {
      width: 100%;
      accent-color: #2F5D50;
    }
    .footnote {
      font-size: 12px;
      color: #6B7280;
      margin-top: 24px;
      border-top: 1px solid #E4E1D8;
      padding-top: 12px;
    }
  </style>
</head>
<body>
  <h2>Superhuman PMF Benchmark Calculator</h2>
  <p>Based on Rahul Vohra's framework on Lenny's Podcast: What percentage of users would be <em>"very disappointed"</em> if the product disappeared?</p>
  
  <div class="card">
    <div class="metric" id="score-display">58%</div>
    <div class="label">Very Disappointed Ratio (Threshold: 40%)</div>
    <div class="bar-container">
      <div class="bar" id="score-bar" style="width: 58%;"></div>
    </div>
  </div>

  <div class="slider-group">
    <label for="input-range">Adjust "Very Disappointed" Responses (Simulated):</label>
    <input type="range" id="input-range" min="10" max="90" value="58" />
  </div>

  <div class="footnote">
    Status: <strong>Product-Market Fit Indicated</strong> (&gt;40% benchmark established by Sean Ellis and validated by Rahul Vohra).
  </div>

  <script>
    const slider = document.getElementById('input-range');
    const display = document.getElementById('score-display');
    const bar = document.getElementById('score-bar');
    if (slider && display && bar) {
      slider.addEventListener('input', (e) => {
        const val = e.target.value;
        display.textContent = val + '%';
        bar.style.width = val + '%';
        if (val < 40) {
          bar.style.backgroundColor = '#A6620C';
        } else {
          bar.style.backgroundColor = '#2F5D50';
        }
      });
    }
  </script>
</body>
</html>`,
  },
};

export const MOCK_SESSIONS: Session[] = [
  {
    id: 'session-1',
    title: 'B2B SaaS Retention & Cohort Flattening',
    createdAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: ['artifact-1'],
    messages: [
      {
        id: 'm1-1',
        role: 'user',
        content: 'How do top product leaders on Lenny\'s Podcast determine whether their retention curve is healthy or fatally leaky?',
        timestamp: '14:20',
      },
      {
        id: 'm1-2',
        role: 'assistant',
        timestamp: '14:21',
        status: 'complete',
        content: `Based on podcast discussions with Casey Winters, Elena Verna, and Brian Balfour, assessing retention health comes down to one non-negotiable mathematical requirement: **the cohort retention curve must flatten parallel to the x-axis**.

### 1. The Asymptote Rule
Casey Winters emphasizes that if your retention curve continues to decline monotonically toward zero, you do not have Product-Market Fit. Top-of-funnel acquisition, growth hacks, and paid spend only rent users when the asymptote is missing.

### 2. Natural Problem Frequency Alignment
Elena Verna points out that you cannot diagnose retention without first mapping your metric to the product's natural cadence. Measuring daily active usage for a monthly financial close tool creates false alarms, while measuring monthly usage for a developer code review tool masks dangerous churn.

### 3. Actionable Retention Diagnostic
- **Check month 3 to month 6 stability:** For B2B SaaS, the retention floor between Month 3 and Month 6 should not drop by more than 2-3 percentage points.
- **Isolate your high-conviction ICP:** General churn is often just bad acquisition targeting. Filter the cohort to only ideal accounts.`,
        citations: [
          {
            id: 'cit-1',
            episodeNumber: 42,
            episodeTitle: 'Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie',
            guest: 'Casey Winters',
            guestRole: 'Former CPO at Eventbrite, Growth Lead at Pinterest',
            timestamp: '15:20',
            quoteExcerpt: 'Product-market fit is revealed when a cohort curve stops dropping and runs flat. If you don\'t have that horizontal floor, nothing else you do matters. You are merely renting users rather than building an enduring business.',
            episodeUrl: 'https://www.youtube.com/watch?v=WlRfyEpAKxw',
          },
          {
            id: 'cit-2',
            episodeNumber: 88,
            episodeTitle: 'Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops',
            guest: 'Elena Verna',
            guestRole: 'Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude',
            timestamp: '28:44',
            quoteExcerpt: 'B2B growth loops must align with the natural cadence of the organization. Trying to create daily habits for quarterly problems always creates churn.',
            episodeUrl: 'https://www.youtube.com/watch?v=Tlx4fxzuHNw',
          },
        ],
      },
      {
        id: 'm1-3',
        role: 'user',
        content: 'Write an essay summarizing this as an actionable playbook for our product team.',
        timestamp: '14:24',
      },
      {
        id: 'm1-4',
        role: 'assistant',
        timestamp: '14:25',
        status: 'complete',
        artifactId: 'artifact-1',
        content: `I've synthesized a comprehensive Ship 30/30 playbook titled **"B2B SaaS Retention Playbook: Cohort Flattening and Natural Frequency"** grounded in the transcript frameworks of Casey Winters and Elena Verna.

The document includes cohort benchmark tables across SMB, Mid-Market, and Enterprise, mathematical code patterns, and an operational checklist. You can inspect and export the full text in the Artifact Workbench on the right.`,
      },
    ],
  },
  {
    id: 'session-2',
    title: 'Product-Market Fit Engine & Superhuman',
    createdAt: new Date(Date.now() - 3600000 * 26).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 26).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: ['artifact-2'],
    messages: [
      {
        id: 'm2-1',
        role: 'user',
        content: 'How did Rahul Vohra operationalize the 40% PMF survey rule at Superhuman?',
        timestamp: 'Yesterday 11:05',
      },
      {
        id: 'm2-2',
        role: 'assistant',
        timestamp: 'Yesterday 11:06',
        status: 'complete',
        artifactId: 'artifact-2',
        content: `Rahul Vohra discussed this extensively on Lenny's Podcast. Rather than treating Sean Ellis's 40% rule as a passive lagging metric, Superhuman turned it into an active development engine.

### Rahul Vohra's 4-Step Engine:
1. **Segment the respondents:** Filter users by the question: *"How would you feel if you could no longer use Superhuman?"* (Very disappointed, Somewhat disappointed, Not disappointed).
2. **Double down on your advocates:** Analyze the "Very disappointed" cohort to identify the exact archetype and ICP who loves the product today.
3. **Filter the middle group:** Look at the "Somewhat disappointed" users, but *only* those who share the same primary benefit as your "Very disappointed" group.
4. **Allocate roadmap 50/50:** Spend 50% of engineering bandwidth strengthening what your fans love, and 50% removing blockers for the on-the-fence users who share that profile.

I also compiled an interactive PMF Calculator tool in the Artifact Viewer.`,
        citations: [
          {
            id: 'cit-3',
            episodeNumber: 15,
            episodeTitle: 'Rahul Vohra on The Product-Market Fit Engine and Building Superhuman',
            guest: 'Rahul Vohra',
            guestRole: 'Founder & CEO of Superhuman',
            timestamp: '19:12',
            quoteExcerpt: 'We surveyed our users and only 22% said they would be very disappointed. Instead of despairing, we created a systematic method to drive that number up to 58%.',
            episodeUrl: 'https://www.youtube.com/watch?v=ourIThGMpYE',
          },
        ],
      },
    ],
  },
  {
    id: 'session-3',
    title: 'Web3 & Crypto Tokenomics Mechanics',
    createdAt: new Date(Date.now() - 3600000 * 72).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 72).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: [],
    messages: [
      {
        id: 'm3-1',
        role: 'user',
        content: 'What does Lenny\'s Podcast recommend for designing token distribution schedules in web3 games?',
        timestamp: '3 days ago',
      },
      {
        id: 'm3-2',
        role: 'assistant',
        timestamp: '3 days ago',
        status: 'low-evidence',
        content: `I don't have enough grounded material on token distribution mechanics for web3 games in Lenny's Podcast to answer confidently.

While Lenny has occasionally explored broader web3 narratives with guests like Chris Dixon and Packy McCormick, the podcast transcript archive focuses overwhelmingly on traditional software product management, SaaS growth loops, retention metrics, and consumer marketplace mechanics. It does not contain empirical guidance or tactical benchmarks on token distribution schedules or cryptocurrency liquidity mechanics.

I cannot synthesize reliable operational guidance on this topic without fabricating claims beyond Lenny's podcast archives.`,
      },
    ],
  },
  {
    id: 'session-4',
    title: 'Growth Loops vs Funnels & Retention',
    createdAt: new Date(Date.now() - 3600000 * 120).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 120).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: [],
    messages: [
      {
        id: 'm4-1',
        role: 'user',
        content: 'Why does Brian Balfour argue that traditional linear funnels are dead?',
        timestamp: '5 days ago',
      },
      {
        id: 'm4-2',
        role: 'assistant',
        timestamp: '5 days ago',
        status: 'complete',
        content: `Brian Balfour (Reforge Founder, former VP Growth at HubSpot) explained on the podcast that the traditional linear funnel (AARRR: Acquisition, Activation, Retention, Referral, Revenue) creates a fatal structural flaw: **it produces diminishing returns requiring ever-increasing inputs of capital or attention**.

### Why Growth Loops Win:
- **Reinvestment of Output:** In a loop, the output of one cohort serves as the acquisition input for the next cohort (e.g. viral loops, content loops, paid loops).
- **Compounding instead of linear decay:** A linear funnel requires you to pour more leads into the top every month. A loop compounds with each cycle.
- **Defensibility:** Competitors can easily copy a landing page or bid higher on Google keywords; they cannot easily copy a proprietary closed-loop system where product usage inherently generates new distribution.`,
        citations: [
          {
            id: 'cit-4',
            episodeNumber: 112,
            episodeTitle: 'Brian Balfour on Growth Loops, Retention Engines, and The Four Fits',
            guest: 'Brian Balfour',
            guestRole: 'Founder & CEO at Reforge, Former VP Growth at HubSpot',
            timestamp: '11:45',
            quoteExcerpt: 'Funnels create organizational silos and run into diminishing returns. The fastest growing products are powered by 1 to 2 compound loops where users going through the product inherently bring in more users.',
            episodeUrl: 'https://www.youtube.com/watch?v=Mq_T3KVBR9E',
          },
        ],
      },
    ],
  },
  {
    id: 'session-5',
    title: 'Local LLM Connection Troubleshooting',
    createdAt: new Date(Date.now() - 3600000 * 240).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 240).toISOString(),
    activeModelId: 'ollama-mistral',
    artifactIds: [],
    messages: [
      {
        id: 'm5-1',
        role: 'user',
        content: 'Can you summarize Gibson Biddle\'s DHM model using my local Ollama model?',
        timestamp: '10 days ago',
      },
      {
        id: 'm5-2',
        role: 'assistant',
        timestamp: '10 days ago',
        status: 'error',
        content: '',
        errorDetails: {
          message: "Couldn't reach the local model. Check that Ollama is running on localhost:11434, or switch to Cloud.",
          canSwitchToCloud: true,
        },
      },
    ],
  },
];
