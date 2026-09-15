import React from 'react';
import { ArrowDown, CheckCircle2, Split, Lightbulb } from 'lucide-react';

interface ComparePerspectivesViewProps {
  content: string;
}

interface SpeakerPerspective {
  name: string;
  coreIdea?: string;
  growthMechanism?: string;
  evidence?: string;
  otherPoints: { label: string; text: string }[];
}

export const ComparePerspectivesView: React.FC<ComparePerspectivesViewProps> = ({ content }) => {
  // Parse speaker sections and synthesis from markdown
  const parseComparison = () => {
    const lines = content.split('\n');
    let currentSection: 'header' | 'speaker_a' | 'speaker_b' | 'synthesis' = 'header';
    let speakerAName = 'Speaker A';
    let speakerBName = 'Speaker B';
    const speakerALines: string[] = [];
    const speakerBLines: string[] = [];
    const synthesisLines: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('### ')) {
        const title = line.replace('### ', '').trim();
        if (title.toLowerCase().includes('synthesis')) {
          currentSection = 'synthesis';
        } else if (currentSection === 'header') {
          currentSection = 'speaker_a';
          speakerAName = title;
        } else if (currentSection === 'speaker_a') {
          currentSection = 'speaker_b';
          speakerBName = title;
        }
        continue;
      }

      if (currentSection === 'speaker_a') {
        speakerALines.push(line);
      } else if (currentSection === 'speaker_b') {
        speakerBLines.push(line);
      } else if (currentSection === 'synthesis') {
        synthesisLines.push(line);
      }
    }

    const parseSpeaker = (name: string, rawLines: string[]): SpeakerPerspective => {
      let coreIdea: string | undefined;
      let growthMechanism: string | undefined;
      let evidence: string | undefined;
      const otherPoints: { label: string; text: string }[] = [];

      for (const line of rawLines) {
        const trimmed = line.trim().replace(/^-\s*\*\*/, '').replace(/^\*\*/, '');
        if (!trimmed) continue;

        if (trimmed.toLowerCase().startsWith('core idea**:') || trimmed.toLowerCase().startsWith('core idea:')) {
          coreIdea = trimmed.replace(/^core idea\*?\*?:\s*/i, '');
        } else if (trimmed.toLowerCase().startsWith('growth mechanism**:') || trimmed.toLowerCase().startsWith('growth mechanism:')) {
          growthMechanism = trimmed.replace(/^growth mechanism\*?\*?:\s*/i, '');
        } else if (trimmed.toLowerCase().startsWith('relevant evidence**:') || trimmed.toLowerCase().startsWith('relevant evidence:')) {
          evidence = trimmed.replace(/^relevant evidence\*?\*?:\s*/i, '');
        } else {
          const match = trimmed.match(/^([^:]+)\*?\*?:\s*(.+)$/);
          if (match) {
            otherPoints.push({ label: match[1], text: match[2] });
          }
        }
      }

      return { name, coreIdea, growthMechanism, evidence, otherPoints };
    };

    const parseSynthesis = (rawLines: string[]) => {
      let agreements: string | undefined;
      let differences: string | undefined;
      let practicalImplication: string | undefined;

      for (const line of rawLines) {
        const trimmed = line.trim().replace(/^-\s*\*\*/, '').replace(/^\*\*/, '');
        if (!trimmed) continue;

        if (trimmed.toLowerCase().startsWith('agreements**:') || trimmed.toLowerCase().startsWith('agreements:')) {
          agreements = trimmed.replace(/^agreements\*?\*?:\s*/i, '');
        } else if (trimmed.toLowerCase().startsWith('differences**:') || trimmed.toLowerCase().startsWith('differences:')) {
          differences = trimmed.replace(/^differences\*?\*?:\s*/i, '');
        } else if (trimmed.toLowerCase().startsWith('practical implication**:') || trimmed.toLowerCase().startsWith('practical implication:')) {
          practicalImplication = trimmed.replace(/^practical implication\*?\*?:\s*/i, '');
        }
      }

      return { agreements, differences, practicalImplication };
    };

    return {
      speakerA: parseSpeaker(speakerAName, speakerALines),
      speakerB: parseSpeaker(speakerBName, speakerBLines),
      synthesis: parseSynthesis(synthesisLines),
    };
  };

  const parsed = parseComparison();

  return (
    <div className="editorial-comparison my-4 space-y-6">
      {/* Editorial Header */}
      <div className="border-b border-line-200 pb-3">
        <span className="text-[10px] font-mono uppercase tracking-widest text-evidence-700 font-bold bg-evidence-100/90 px-2 py-0.5 rounded">
          PERSPECTIVE COMPARISON
        </span>
        <h3 className="font-serif text-lg font-semibold text-ink-950 mt-1.5">
          {parsed.speakerA.name} vs. {parsed.speakerB.name}
        </h3>
      </div>

      {/* Side-by-Side Perspectives Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 relative">
        {/* Subtle center vertical divider for desktop */}
        <div className="hidden md:block absolute top-0 bottom-0 left-1/2 w-[1px] bg-line-200 -translate-x-1/2" />

        {/* Speaker A Column */}
        <div className="bg-paper-100/60 p-4 sm:p-5 rounded-md border border-line-200 space-y-4">
          <div className="border-b border-line-200 pb-2">
            <span className="text-[10px] font-mono uppercase tracking-wider text-ink-500 font-semibold">
              PERSPECTIVE A
            </span>
            <h4 className="font-sans font-bold text-ink-950 text-base">
              {parsed.speakerA.name}
            </h4>
          </div>

          {parsed.speakerA.coreIdea && (
            <div>
              <div className="text-[11px] font-mono uppercase tracking-wider text-evidence-700 font-semibold mb-1">
                Core Idea
              </div>
              <p className="font-sans text-sm text-ink-900 leading-relaxed">
                {parsed.speakerA.coreIdea}
              </p>
            </div>
          )}

          {parsed.speakerA.growthMechanism && (
            <div>
              <div className="text-[11px] font-mono uppercase tracking-wider text-ink-500 font-semibold mb-1">
                Growth Mechanism
              </div>
              <p className="font-sans text-sm text-ink-800 leading-relaxed">
                {parsed.speakerA.growthMechanism}
              </p>
            </div>
          )}

          {parsed.speakerA.evidence && (
            <div className="p-3 bg-paper-0/80 rounded border-l-2 border-evidence-600">
              <div className="text-[10px] font-mono uppercase tracking-wider text-ink-400 mb-1">
                Relevant Evidence
              </div>
              <p className="font-serif italic text-xs text-ink-800 leading-relaxed">
                {parsed.speakerA.evidence}
              </p>
            </div>
          )}
        </div>

        {/* Speaker B Column */}
        <div className="bg-paper-100/60 p-4 sm:p-5 rounded-md border border-line-200 space-y-4">
          <div className="border-b border-line-200 pb-2">
            <span className="text-[10px] font-mono uppercase tracking-wider text-ink-500 font-semibold">
              PERSPECTIVE B
            </span>
            <h4 className="font-sans font-bold text-ink-950 text-base">
              {parsed.speakerB.name}
            </h4>
          </div>

          {parsed.speakerB.coreIdea && (
            <div>
              <div className="text-[11px] font-mono uppercase tracking-wider text-evidence-700 font-semibold mb-1">
                Core Idea
              </div>
              <p className="font-sans text-sm text-ink-900 leading-relaxed">
                {parsed.speakerB.coreIdea}
              </p>
            </div>
          )}

          {parsed.speakerB.growthMechanism && (
            <div>
              <div className="text-[11px] font-mono uppercase tracking-wider text-ink-500 font-semibold mb-1">
                Growth Mechanism
              </div>
              <p className="font-sans text-sm text-ink-800 leading-relaxed">
                {parsed.speakerB.growthMechanism}
              </p>
            </div>
          )}

          {parsed.speakerB.evidence && (
            <div className="p-3 bg-paper-0/80 rounded border-l-2 border-evidence-600">
              <div className="text-[10px] font-mono uppercase tracking-wider text-ink-400 mb-1">
                Relevant Evidence
              </div>
              <p className="font-serif italic text-xs text-ink-800 leading-relaxed">
                {parsed.speakerB.evidence}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Synthesis Connector Graphic */}
      <div className="flex flex-col items-center justify-center my-2">
        <div className="h-4 w-[1px] bg-line-300" />
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-pill bg-paper-100 border border-line-200 text-[10px] font-mono text-ink-600 uppercase tracking-wider">
          <ArrowDown className="w-3 h-3 text-evidence-600" />
          <span>Synthesis & Differences</span>
        </div>
        <div className="h-4 w-[1px] bg-line-300" />
      </div>

      {/* Synthesis Section: Agreements, Differences, Practical Implication */}
      <div className="bg-paper-0 p-4 sm:p-5 rounded-md border border-line-200 space-y-4 shadow-xs">
        {parsed.synthesis.agreements && (
          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-evidence-600 flex-shrink-0 mt-0.5" />
            <div>
              <h5 className="font-mono text-[11px] uppercase tracking-wider font-semibold text-ink-950 mb-0.5">
                Agreements
              </h5>
              <p className="font-sans text-sm text-ink-800 leading-relaxed">
                {parsed.synthesis.agreements}
              </p>
            </div>
          </div>
        )}

        {parsed.synthesis.differences && (
          <div className="flex items-start gap-2.5 border-t border-line-200/70 pt-3">
            <Split className="w-4 h-4 text-ink-500 flex-shrink-0 mt-0.5" />
            <div>
              <h5 className="font-mono text-[11px] uppercase tracking-wider font-semibold text-ink-950 mb-0.5">
                Key Differences
              </h5>
              <p className="font-sans text-sm text-ink-800 leading-relaxed">
                {parsed.synthesis.differences}
              </p>
            </div>
          </div>
        )}

        {parsed.synthesis.practicalImplication && (
          <div className="flex items-start gap-2.5 border-t border-line-200/70 pt-3 bg-evidence-100/40 p-3 rounded">
            <Lightbulb className="w-4 h-4 text-evidence-700 flex-shrink-0 mt-0.5" />
            <div>
              <h5 className="font-mono text-[11px] uppercase tracking-wider font-semibold text-evidence-800 mb-0.5">
                Practical Implication
              </h5>
              <p className="font-serif text-[13.5px] text-ink-900 leading-relaxed">
                {parsed.synthesis.practicalImplication}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
