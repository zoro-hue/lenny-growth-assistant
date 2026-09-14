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
    id: 'demo-balfour-channel-model',
    title: 'Brian Balfour — Channel Model Fit',
    createdAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 2).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: [],
    messages: [
      {
        id: 'm-balfour-1',
        role: 'user',
        content: 'Why does Brian Balfour argue that traditional acquisition funnels are dead, and how does Channel-Model Fit work?',
        timestamp: '14:20',
      },
      {
        id: 'm-balfour-2',
        role: 'assistant',
        timestamp: '14:21',
        status: 'complete',
        evidenceStrength: 'high',
        evidenceLabel: '2 transcript sources · 1 speaker',
        followUpSuggestions: [
          'Compare Brian Balfour and Elena Verna on growth loops',
          'What metric should I track for Channel-Model Fit?',
          'Turn this into a playbook',
          'Write a Ship 30/30 essay',
        ],
        content: `Based on Brian Balfour's Four Fits Framework on Lenny's Podcast (Episode #112), distribution channels do not bend to your product—your product must bend to the channel.

### 1. Products Are Built to Fit Channels
Distribution channels (Google SEO, Meta ads, Virality, App Stores) are external platforms with their own rules. You cannot build a product and then 'find a channel'; the product characteristics must be engineered specifically to exploit the natural dynamics of the channel.

### 2. Channel-Model Fit & The Growth Danger Zone
Your pricing model determines what Customer Acquisition Cost (CAC) you can afford:
- **Low ARPU ($10/mo):** Requires low CAC channels such as virality, UGC, or organic search.
- **High ARPU ($100k+/yr):** Can support enterprise sales, high-touch onboarding, and multi-month sales cycles.
- **The Danger Zone:** Companies with ARPU too high for frictionless self-serve but too low to support direct sales reps get trapped without a viable channel.`,
        citations: [
          {
            id: 'cit-balfour-1',
            episodeNumber: 112,
            episodeTitle: 'Brian Balfour on the Four Fits Framework and Why Growth Is a System',
            guest: 'Brian Balfour',
            guestRole: 'Founder & CEO of Reforge, Former VP Growth at HubSpot',
            timestamp: '00:01:28',
            quoteExcerpt: 'Distribution channels—whether it is Google SEO, Facebook ads, Apple App Store, or Virality—do not care about your product. You do not control the rules of Google or Meta; they control their algorithms.',
            episodeUrl: 'https://www.youtube.com/watch?v=BrianBalfourGrowth',
            whyThisSource: 'Direct evidence from Brian Balfour supporting the Channel-Model Fit argument.',
          },
          {
            id: 'cit-balfour-2',
            episodeNumber: 112,
            episodeTitle: 'Brian Balfour on the Four Fits Framework and Why Growth Is a System',
            guest: 'Brian Balfour',
            guestRole: 'Founder & CEO of Reforge, Former VP Growth at HubSpot',
            timestamp: '00:02:20',
            quoteExcerpt: 'Your pricing model determines what CAC you can afford. If your Average Revenue Per User (ARPU) is $10 a month, you cannot use an outbound sales team or expensive enterprise marketing—the math simply will not work.',
            episodeUrl: 'https://www.youtube.com/watch?v=BrianBalfourGrowth',
            whyThisSource: 'Direct evidence from Brian Balfour on CAC alignment with pricing model.',
          },
        ],
      },
    ],
  },
  {
    id: 'demo-winters-retention',
    title: 'Retention Curves — What Actually Matters',
    createdAt: new Date(Date.now() - 3600000 * 3).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 3).toISOString(),
    activeModelId: 'ollama-local',
    artifactIds: [],
    messages: [
      {
        id: 'm-winters-1',
        role: 'user',
        content: 'How does Casey Winters recommend measuring true product-market fit using cohort retention curves?',
        timestamp: '13:10',
      },
      {
        id: 'm-winters-2',
        role: 'assistant',
        timestamp: '13:11',
        status: 'complete',
        evidenceStrength: 'high',
        evidenceLabel: '2 transcript sources · 1 speaker',
        followUpSuggestions: [
          'Compare Casey Winters and Brian Balfour on retention',
          'How does this apply to PLG?',
          'Turn this into a playbook',
          'Write a Ship 30/30 essay',
        ],
        content: `On Episode 42 of Lenny's Podcast, Casey Winters articulates the single quantitative indicator of real Product-Market Fit:

### The Asymptote Floor
Product-market fit is revealed exclusively when a cohort retention curve stops declining and runs completely flat, parallel to the horizontal x-axis by Month 3 or Month 6. If the curve continues dropping monotonically toward zero, you do not have PMF, regardless of top-of-funnel conversion or user signups.

### Benchmarks by Business Model
- **Consumer Subscription / Social:** A retention floor of **20% to 30%** can build a massive business if organic acquisition is massive.
- **B2B SaaS:** Requires a logo retention floor of **70% to 80%**, and Net Revenue Retention (NRR) above **110% to 120%** via seat and usage expansion.`,
        citations: [
          {
            id: 'cit-winters-1',
            episodeNumber: 42,
            episodeTitle: 'Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie',
            guest: 'Casey Winters',
            guestRole: 'Former CPO at Eventbrite, Growth Lead at Pinterest',
            timestamp: '00:00:44',
            quoteExcerpt: 'Product-market fit is revealed when a cohort retention curve stops dropping and runs completely flat parallel to the horizontal axis. If you don\'t have that horizontal floor by Month 3 or Month 6, nothing else you do matters.',
            episodeUrl: 'https://www.youtube.com/watch?v=WlRfyEpAKxw',
            whyThisSource: 'Empirical methodology from Casey Winters on cohort retention flattening.',
          },
          {
            id: 'cit-winters-2',
            episodeNumber: 42,
            episodeTitle: 'Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie',
            guest: 'Casey Winters',
            guestRole: 'Former CPO at Eventbrite, Growth Lead at Pinterest',
            timestamp: '00:01:25',
            quoteExcerpt: 'In consumer subscription or social, a flat retention curve at 20% to 30% can build a massive business... In B2B SaaS, your logo retention floor needs to be 70% or 80%, and your Net Revenue Retention (NRR) should be over 110% to 120%.',
            episodeUrl: 'https://www.youtube.com/watch?v=WlRfyEpAKxw',
            whyThisSource: 'Benchmark criteria for cohort asymptotes across consumer and B2B SaaS.',
          },
        ],
      },
    ],
  },
  {
    id: 'demo-ship30-pricing',
    title: 'Ship 30/30 — Pricing Strategy',
    createdAt: new Date(Date.now() - 3600000 * 4).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 4).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: ['artifact-1'],
    messages: [
      {
        id: 'm-ship30-1',
        role: 'user',
        content: 'Write a Ship 30/30 essay on pricing strategy and channel-model fit.',
        timestamp: '12:00',
      },
      {
        id: 'm-ship30-2',
        role: 'assistant',
        timestamp: '12:01',
        status: 'complete',
        artifactId: 'artifact-1',
        evidenceStrength: 'limited',
        evidenceLabel: '1 relevant transcript source',
        followUpSuggestions: [
          'How do I implement this framework step-by-step?',
          'What metric should I track?',
          'Compare this with Elena Verna\'s view',
          'Write a Ship 30/30 essay',
        ],
        content: `I've synthesized a comprehensive Ship 30 for 30 playbook titled **"The Channel-Model Pricing Law: Why Your Business Model Dictates Acquisition"** grounded in transcript frameworks from Brian Balfour.

The complete ~1,180-word playbook with a 1-3-1 hook, Danger Zone diagnostic matrix, and tactical 5-step audit is open in the Artifact Workbench to your right.`,
        citations: [
          {
            id: 'cit-balfour-pricing-1',
            episodeNumber: 112,
            episodeTitle: 'Brian Balfour on the Four Fits Framework and Why Growth Is a System',
            guest: 'Brian Balfour',
            guestRole: 'Founder & CEO of Reforge, Former VP Growth at HubSpot',
            timestamp: '00:02:20',
            quoteExcerpt: 'Low ARPU products require low CAC distribution channels like virality, user-generated content, or organic search. Conversely, high ARPU products ($100k+ annual contracts) can afford direct sales...',
            episodeUrl: 'https://www.youtube.com/watch?v=BrianBalfourGrowth',
            whyThisSource: 'Direct evidence from Brian Balfour on channel-model pricing laws.',
          },
        ],
      },
    ],
  },
  {
    id: 'demo-b2b-saas-playbook',
    title: 'B2B SaaS Retention Playbook',
    createdAt: new Date(Date.now() - 3600000 * 5).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 5).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: ['artifact-1'],
    messages: [
      {
        id: 'm-b2b-1',
        role: 'user',
        content: 'Generate a comprehensive tactical playbook for B2B SaaS retention benchmarks and monetization loops.',
        timestamp: '11:15',
      },
      {
        id: 'm-b2b-2',
        role: 'assistant',
        timestamp: '11:16',
        status: 'complete',
        artifactId: 'artifact-1',
        evidenceStrength: 'high',
        evidenceLabel: '2 transcript sources · 2 speakers',
        followUpSuggestions: [
          'Compare Casey Winters and Brian Balfour on retention',
          'How does this apply to PLG?',
          'Turn this into a playbook',
          'Write a Ship 30/30 essay',
        ],
        content: `I've generated a comprehensive Markdown playbook titled **"B2B SaaS Retention Playbook: Cohort Flattening & Natural Frequency"** grounded in transcript evidence from Casey Winters and Elena Verna.

The operational framework, cohort benchmark tables, and 7-step checklist are open in the Artifact Workbench to your right.`,
        citations: [
          {
            id: 'cit-b2b-playbook-1',
            episodeNumber: 42,
            episodeTitle: 'Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie',
            guest: 'Casey Winters',
            guestRole: 'Former CPO at Eventbrite, Growth Lead at Pinterest',
            timestamp: '00:01:25',
            quoteExcerpt: 'In B2B SaaS, your logo retention floor needs to be 70% or 80%, and your Net Revenue Retention (NRR) should be over 110% to 120% because existing accounts expand over time.',
            episodeUrl: 'https://www.youtube.com/watch?v=WlRfyEpAKxw',
            whyThisSource: 'Benchmark criteria for B2B SaaS logo retention and NRR.',
          },
          {
            id: 'cit-b2b-playbook-2',
            episodeNumber: 88,
            episodeTitle: 'Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops',
            guest: 'Elena Verna',
            guestRole: 'Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude',
            timestamp: '00:01:38',
            quoteExcerpt: 'B2B growth loops must strictly align with the natural cadence of the organization. Trying to create daily habits for quarterly problems always creates churn.',
            episodeUrl: 'https://www.youtube.com/watch?v=ElenaVernaPLG',
            whyThisSource: 'Direct operational guidance on problem frequency alignment.',
          },
        ],
      },
    ],
  },
  {
    id: 'demo-verna-plg',
    title: 'Elena Verna — Product-Led Growth',
    createdAt: new Date(Date.now() - 3600000 * 26).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 26).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: [],
    messages: [
      {
        id: 'm-verna-1',
        role: 'user',
        content: 'What is the single biggest misconception about PLG according to Elena Verna?',
        timestamp: 'Yesterday 14:00',
      },
      {
        id: 'm-verna-2',
        role: 'assistant',
        timestamp: 'Yesterday 14:01',
        status: 'complete',
        evidenceStrength: 'high',
        evidenceLabel: '2 transcript sources · 1 speaker',
        followUpSuggestions: [
          'Compare Elena Verna and Brian Balfour on PLG',
          'What is the Time-to-Aha threshold for B2B activation?',
          'Turn this into a playbook',
          'Write a Ship 30/30 essay',
        ],
        content: `In Episode 88 of Lenny's Podcast, Elena Verna explains that the most destructive misconception is assuming Product-Led Growth is just a self-serve pricing page and a free trial.

### 1. True PLG is an Organizational Distribution Model
PLG means the product itself performs the heavy lifting of acquisition, retention, and expansion. If your product requires a human sales rep to explain why it is valuable before the user feels the value, you do not have a PLG motion.

### 2. The 8-Minute Time-to-Aha Rule
Elena highlights that in a true PLG motion, your **Time-to-Aha must be under 8 minutes**. If users cannot experience the core value proposition in their very first session without reading documentation, onboarding drop-off will routinely exceed 80%.

### 3. Monetize Governance, Not Activation
Never place a paywall before the user has formed a habit. Charge for organizational collaboration, security (SSO/SCIM), and administrative controls when multiple teams adopt the tool.`,
        citations: [
          {
            id: 'cit-verna-plg-1',
            episodeNumber: 88,
            episodeTitle: 'Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops',
            guest: 'Elena Verna',
            guestRole: 'Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude',
            timestamp: '00:00:45',
            quoteExcerpt: 'The biggest mistake is assuming PLG is just a self-serve pricing page and a free trial. PLG is an organizational distribution model where the product itself does the heavy lifting of acquisition, retention, and expansion.',
            episodeUrl: 'https://www.youtube.com/watch?v=ElenaVernaPLG',
            whyThisSource: 'Direct statement on PLG organizational definition and Time-to-Aha.',
          },
          {
            id: 'cit-verna-plg-2',
            episodeNumber: 88,
            episodeTitle: 'Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops',
            guest: 'Elena Verna',
            guestRole: 'Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude',
            timestamp: '00:02:40',
            quoteExcerpt: 'Never paywall activation. If you put a credit card wall or hard paywall before the user has validated that the product solves their problem, you destroy your conversion loop. You should monetize on scale and organizational governance...',
            episodeUrl: 'https://www.youtube.com/watch?v=ElenaVernaPLG',
            whyThisSource: 'Tactical guidance on monetization placement and paywall timing.',
          },
        ],
      },
    ],
  },
  {
    id: 'demo-vohra-pmf',
    title: 'Rahul Vohra — PMF Framework',
    createdAt: new Date(Date.now() - 3600000 * 28).toISOString(),
    updatedAt: new Date(Date.now() - 3600000 * 28).toISOString(),
    activeModelId: 'openai-cloud',
    artifactIds: [],
    messages: [
      {
        id: 'm-vohra-1',
        role: 'user',
        content: 'How did Rahul Vohra operationalize the 40% PMF survey rule at Superhuman?',
        timestamp: 'Yesterday 11:05',
      },
      {
        id: 'm-vohra-2',
        role: 'assistant',
        timestamp: 'Yesterday 11:06',
        status: 'complete',
        evidenceStrength: 'high',
        evidenceLabel: '2 transcript sources · 1 speaker',
        followUpSuggestions: [
          'Compare Rahul Vohra and Casey Winters on PMF signals',
          'How do I filter the 40% PMF survey respondents?',
          'Turn this into a playbook',
          'Write a Ship 30/30 essay',
        ],
        content: `On Episode 15 of Lenny's Podcast, Rahul Vohra shared how Superhuman turned Sean Ellis's 40% survey question into an active product engine that systematically drove their PMF score from 22% to 58%:

### The 4-Step PMF Engine
1. **Survey and Segment:** Ask: *'How would you feel if you could no longer use the product?'* (Very disappointed, Somewhat disappointed, Not disappointed).
2. **Analyze Your High-Expectation Advocates:** Isolate the 'Very disappointed' group to identify the exact customer archetype who finds undeniable value.
3. **Filter the Middle Cohort:** Look at the 'Somewhat disappointed' group, but **ONLY** those who share the same primary benefit as the 'Very disappointed' lovers. Politely ignore everyone else so you don't build a Frankenstein product.
4. **The 50/50 Roadmap Allocation:** Dedicate half of your engineering roadmap to doubling down on what fans love, and the other half to systematically removing blockers for that specific target middle cohort.`,
        citations: [
          {
            id: 'cit-vohra-pmf-1',
            episodeNumber: 15,
            episodeTitle: 'Rahul Vohra on The Product-Market Fit Engine and Building Superhuman',
            guest: 'Rahul Vohra',
            guestRole: 'Founder & CEO of Superhuman',
            timestamp: '00:00:52',
            quoteExcerpt: 'We surveyed our users and only 22% said they would be very disappointed if Superhuman disappeared. Instead of despairing, we created a systematic method to drive that number up to 58%.',
            episodeUrl: 'https://www.youtube.com/watch?v=ourIThGMpYE',
            whyThisSource: 'Operational breakdown of the Superhuman 40% PMF engine.',
          },
          {
            id: 'cit-vohra-pmf-2',
            episodeNumber: 15,
            episodeTitle: 'Rahul Vohra on The Product-Market Fit Engine and Building Superhuman',
            guest: 'Rahul Vohra',
            guestRole: 'Founder & CEO of Superhuman',
            timestamp: '00:02:24',
            quoteExcerpt: 'Because if you listen to everyone, you will build a Frankenstein product. Users who want completely different value propositions will pull your product in directions that dilute what makes it magical...',
            episodeUrl: 'https://www.youtube.com/watch?v=ourIThGMpYE',
            whyThisSource: 'Guidance on why feedback from non-ICP users must be filtered.',
          },
        ],
      },
    ],
  },
];
