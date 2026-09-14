import { useState, useCallback, useRef } from 'react';
import { Message, Citation } from '../types/chat';
import { Artifact } from '../types/artifact';
import { api } from '../services/api';

interface UseChatStreamOptions {
  sessionId: string;
  activeModelId: string;
  addMessage: (sessionId: string, message: Message) => void;
  updateMessage: (sessionId: string, messageId: string, updates: Partial<Message>) => void;
  addArtifact: (artifact: Artifact) => void;
  addArtifactToSession: (sessionId: string, artifactId: string) => void;
  openArtifactViewer: (artifactId: string) => void;
}

export function useChatStream({
  sessionId,
  activeModelId,
  addMessage,
  updateMessage,
  addArtifact,
  addArtifactToSession,
  openArtifactViewer,
}: UseChatStreamOptions) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string | null>(null);
  const abortControllerRef = useRef<boolean>(false);

  const sendMessage = useCallback(
    async (content: string, isEssayRequest: boolean = false) => {
      if (!content.trim() || isStreaming) return;
      abortControllerRef.current = false;

      // 1. Add user message
      const userMsgId = 'msg-' + Date.now();
      const userMsg: Message = {
        id: userMsgId,
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      addMessage(sessionId, userMsg);

      setIsStreaming(true);

      // Try calling backend RAG API first
      setLoadingStage(isEssayRequest ? 'Structuring essay…' : 'Retrieving transcripts…');
      try {
        const backendRes = await api.sendChat(sessionId, content, activeModelId, isEssayRequest);
        if (backendRes && backendRes.assistantMessage) {
          const ast = backendRes.assistantMessage;
          const assistantMsgId = ast.id || ('msg-' + (Date.now() + 2));

          if (backendRes.artifact) {
            addArtifact(backendRes.artifact);
            addArtifactToSession(sessionId, backendRes.artifact.id);
            openArtifactViewer(backendRes.artifact.id);
          }

          if (ast.status === 'error' || ast.status === 'low-evidence') {
            setLoadingStage(null);
            addMessage(sessionId, {
              id: assistantMsgId,
              role: 'assistant',
              timestamp: ast.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              status: ast.status,
              content: ast.content,
              citations: ast.citations || [],
              errorDetails: ast.errorDetails,
            });
            setIsStreaming(false);
            return;
          }

          // Stream tokens for grounded response
          addMessage(sessionId, {
            id: assistantMsgId,
            role: 'assistant',
            timestamp: ast.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: 'streaming',
            content: '',
          });
          setLoadingStage(null);

          const words = (ast.content || '').split(' ');
          let currentText = '';
          for (let i = 0; i < words.length; i++) {
            if (abortControllerRef.current) break;
            currentText += (i === 0 ? '' : ' ') + words[i];
            updateMessage(sessionId, assistantMsgId, { content: currentText });
            await new Promise(r => setTimeout(r, 16));
          }

          updateMessage(sessionId, assistantMsgId, {
            status: 'complete',
            citations: ast.citations || [],
          });

          setIsStreaming(false);
          return;
        }
      } catch (err) {
        console.warn('Backend chat API call failed, falling back to local simulation:', err);
      }

      // Check if current model is unavailable local model
      if (activeModelId === 'ollama-mistral') {
        setLoadingStage('Connecting to local model…');
        await new Promise(r => setTimeout(r, 700));
        const errorMsgId = 'msg-' + (Date.now() + 1);
        addMessage(sessionId, {
          id: errorMsgId,
          role: 'assistant',
          content: '',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          status: 'error',
          errorDetails: {
            message: "Couldn't reach the local model. Check that Ollama is running on localhost:11434, or switch to Cloud.",
            canSwitchToCloud: true,
          },
        });
        setLoadingStage(null);
        setIsStreaming(false);
        return;
      }

      const lowerContent = content.toLowerCase().trim();
      const isGreetingOrCasual =
        ['hi', 'hello', 'hey', 'yo', 'test', 'help', 'who are you', 'how are you'].includes(lowerContent) ||
        lowerContent.length <= 3;

      const isGrowthQuery =
        lowerContent.includes('growth') ||
        lowerContent.includes('retention') ||
        lowerContent.includes('pmf') ||
        lowerContent.includes('product') ||
        lowerContent.includes('metric') ||
        lowerContent.includes('loop') ||
        lowerContent.includes('b2b') ||
        lowerContent.includes('cohort') ||
        lowerContent.includes('funnel') ||
        lowerContent.includes('churn') ||
        lowerContent.includes('activation') ||
        lowerContent.includes('monetization') ||
        lowerContent.includes('pricing') ||
        lowerContent.includes('playbook') ||
        lowerContent.includes('essay') ||
        lowerContent.includes('balfour') ||
        lowerContent.includes('winters') ||
        lowerContent.includes('verna') ||
        lowerContent.includes('dhm') ||
        lowerContent.includes('vohra') ||
        lowerContent.includes('lenny');

      const isLowEvidenceQuery =
        isGreetingOrCasual ||
        !isGrowthQuery ||
        lowerContent.includes('web3') ||
        lowerContent.includes('token') ||
        lowerContent.includes('crypto') ||
        lowerContent.includes('nft') ||
        lowerContent.includes('solana') ||
        lowerContent.includes('blockchain');

      const isEssay = isEssayRequest || lowerContent.includes('essay') || lowerContent.includes('playbook');

      if (isEssay) {
        // Staged status text per Spec E.3:
        // 'Structuring essay…' -> 'Grounding claims…' -> 'Finalizing draft…'
        setLoadingStage('Structuring essay…');
        await new Promise(r => setTimeout(r, 650));
        if (abortControllerRef.current) return;

        setLoadingStage('Grounding claims in podcast transcripts…');
        await new Promise(r => setTimeout(r, 800));
        if (abortControllerRef.current) return;

        setLoadingStage('Finalizing draft…');
        await new Promise(r => setTimeout(r, 700));
        if (abortControllerRef.current) return;

        // Create new generated artifact
        const newArtifactId = 'artifact-' + Date.now();
        const generatedArtifact: Artifact = {
          id: newArtifactId,
          sessionId,
          title: `Playbook: ${content.trim().slice(0, 48)}`,
          type: 'markdown',
          wordCount: 1280,
          sourceCount: 3,
          createdAt: 'Just now',
          content: `# Playbook: ${content.trim()}

*Synthesized from transcript evidence across Lenny's Podcast episodes with top product and growth operators.*

---

## Executive Summary

When scaling B2B and product-led businesses, growth is not an accumulation of disparate hacks; it is the compounding output of tightly coupled feedback loops. This document operationalizes the direct transcript guidance from Lenny's Podcast discussions.

---

## 1. Core Framework & Mathematical Foundations

As highlighted across conversations with **Casey Winters** and **Elena Verna**, sustainable expansion requires three preconditions:

1. **Qualitative Product-Market Fit:** Users experience genuine distress if the product is deprecated.
2. **Quantitative PMF:** The cohort retention curve flattens parallel to the horizontal axis by Month 3 to Month 6.
3. **Natural Frequency Alignment:** Measurement intervals mirror the genuine real-world problem frequency rather than an artificial vanity metric.

> "The biggest failure in growth teams is attempting to optimize conversion before understanding where your users naturally find ongoing habit value."
> — Casey Winters, Episode 42

---

## 2. Tactical Execution Protocols

| Stage | Key Metric | Target Benchmark | Transcript Source |
| :--- | :--- | :--- | :--- |
| **Activation** | Time-to-Aha | < 8 minutes | Elena Verna (Ep 88) |
| **Habit Formation** | WAU / MAU | > 40% (team tools) | Brian Balfour (Ep 112) |
| **Monetization** | NRR Floor | > 115% | Madhavan Ramanujam (Ep 74) |

---

## 3. Implementation Checklist

- [ ] Validate cohort retention stabilization across three successive 90-day cohorts.
- [ ] Implement event-based activation triggers rather than arbitrary calendar check-ins.
- [ ] Ensure pricing tiers map directly to customer value realization milestones.
- [ ] Align notification cadences strictly to natural organizational problem frequency.
`,
        };

        addArtifact(generatedArtifact);
        addArtifactToSession(sessionId, newArtifactId);

        // Assistant message with ArtifactGeneratedCard
        const assistantMsgId = 'msg-' + (Date.now() + 2);
        addMessage(sessionId, {
          id: assistantMsgId,
          role: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          status: 'complete',
          artifactId: newArtifactId,
          content: `I've synthesized a complete Ship 30/30 playbook on **${content.trim()}** grounded in transcripts from Casey Winters, Elena Verna, and Brian Balfour.

The essay provides an executive overview, quantitative benchmarks, and a tactical implementation checklist. I have opened it in the Artifact Workbench to your right.`,
        });

        openArtifactViewer(newArtifactId);
        setLoadingStage(null);
        setIsStreaming(false);
        return;
      }

      if (isLowEvidenceQuery) {
        // Spec F.4: "Not enough evidence" state
        setLoadingStage('Retrieving transcripts…');
        await new Promise(r => setTimeout(r, 600));
        setLoadingStage('Verifying evidence threshold…');
        await new Promise(r => setTimeout(r, 600));

        const assistantMsgId = 'msg-' + (Date.now() + 2);
        addMessage(sessionId, {
          id: assistantMsgId,
          role: 'assistant',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          status: 'low-evidence',
          content: lowerContent.includes('web3') || lowerContent.includes('crypto') || lowerContent.includes('token') || lowerContent.includes('solana')
            ? `I don't have enough grounded material on **${content.trim()}** in Lenny's Podcast to answer confidently.

While Lenny has occasionally touched on emerging decentralized architectures with guests like Chris Dixon and Packy McCormick, the podcast transcript archive does not contain tactical or empirical evidence on specific token distribution mechanics or tokenomic CAC offsets.

I cannot synthesize reliable operational guidance without fabricating claims beyond Lenny's podcast archives.`
            : `I don't have enough grounded material on **${content.trim()}** in Lenny's Podcast to answer confidently.

The available podcast transcript archives focus on traditional product management, SaaS growth loops, retention metrics, marketplace mechanics, and startup leadership. They do not contain empirical evidence or tactical guidance on this topic.

I cannot synthesize reliable operational guidance without fabricating claims beyond Lenny's podcast archives.`,
        });

        setLoadingStage(null);
        setIsStreaming(false);
        return;
      }

      // Normal Grounded Q&A Flow (Spec E.2):
      setLoadingStage('Retrieving transcripts…');
      await new Promise(r => setTimeout(r, 550));
      if (abortControllerRef.current) return;

      setLoadingStage('Drafting answer…');
      await new Promise(r => setTimeout(r, 450));
      if (abortControllerRef.current) return;

      const assistantMsgId = 'msg-' + (Date.now() + 2);
      const fullResponse = `Based on Lenny's Podcast discussions with leading operators, addressing this requires understanding the structural drivers rather than surface tactics.

### 1. The Core Growth Mechanics
When operators discuss this on the podcast, they emphasize focusing on compounding loops rather than one-off acquisition channels. The foundation rests on **aligning product usage directly with user value realization**.

### 2. What Top Practitioners Recommend
- **Measure real retention first:** Never scale top-of-funnel marketing until your 90-day cohort retention curve demonstrates an unmistakable plateau.
- **Identify your high-conviction users:** Look closely at the small percentage of users who refuse to churn—what specific workflow creates their dependency?
- **Build feedback loops into the core UX:** Every active user should generate surface area that either retains them or draws in adjacent team members.`;

      const citations: Citation[] = [
        {
          id: 'cit-' + Date.now() + '-1',
          episodeNumber: 42,
          episodeTitle: 'Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie',
          guest: 'Casey Winters',
          guestRole: 'Former CPO at Eventbrite, Growth Lead at Pinterest',
          timestamp: '15:20',
          quoteExcerpt: "Product-market fit is revealed when a cohort curve stops dropping and runs flat. If you don't have that horizontal floor, nothing else you do matters.",
          episodeUrl: 'https://www.lennyspodcast.com/casey-winters',
        },
        {
          id: 'cit-' + Date.now() + '-2',
          episodeNumber: 88,
          episodeTitle: 'Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops',
          guest: 'Elena Verna',
          guestRole: 'Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude',
          timestamp: '28:44',
          quoteExcerpt: 'B2B growth loops must align with the natural cadence of the organization. Trying to create daily habits for quarterly problems always creates churn.',
          episodeUrl: 'https://www.lennyspodcast.com/elena-verna',
        },
      ];

      // Add message in streaming mode
      addMessage(sessionId, {
        id: assistantMsgId,
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        status: 'streaming',
        content: '',
      });
      setLoadingStage(null);

      // Stream tokens
      const words = fullResponse.split(' ');
      let currentText = '';
      for (let i = 0; i < words.length; i++) {
        if (abortControllerRef.current) break;
        currentText += (i === 0 ? '' : ' ') + words[i];
        updateMessage(sessionId, assistantMsgId, {
          content: currentText,
        });
        await new Promise(r => setTimeout(r, 22));
      }

      // Complete message and attach citations (citations animate in post-stream as a distinct beat)
      updateMessage(sessionId, assistantMsgId, {
        status: 'complete',
        citations,
      });

      setIsStreaming(false);
    },
    [
      isStreaming,
      sessionId,
      activeModelId,
      addMessage,
      updateMessage,
      addArtifact,
      addArtifactToSession,
      openArtifactViewer,
    ]
  );

  return {
    isStreaming,
    loadingStage,
    sendMessage,
  };
}
