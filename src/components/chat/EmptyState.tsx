import React from 'react';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string, isEssay?: boolean) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const examplePrompts = [
    {
      text: "How do top product leaders determine whether their cohort retention curve has flattened?",
      isEssay: false,
    },
    {
      text: "Why does Brian Balfour argue that traditional acquisition funnels are dead?",
      isEssay: false,
    },
    {
      text: "What was Rahul Vohra's 4-step framework for Superhuman's PMF engine?",
      isEssay: false,
    },
    {
      text: "Write a Ship 30/30 playbook on pricing tier design based on Madhavan Ramanujam's interview.",
      isEssay: true,
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-[620px] mx-auto text-center px-4 py-12">
      <div className="w-9 h-9 rounded-full bg-evidence-100 flex items-center justify-center mb-5 text-evidence-600">
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
          <path d="M6 6h10" />
          <path d="M6 10h10" />
        </svg>
      </div>

      <h1 className="font-serif text-xl sm:text-2xl text-ink-950 font-semibold mb-3 tracking-normal">
        Ask about product and growth, grounded in Lenny's Podcast
      </h1>

      <p className="font-sans text-sm text-ink-700 max-w-[480px] mb-8 leading-relaxed">
        Every claim is traced directly to transcript evidence with timestamps, guest citations, and verifiable quotes.
      </p>

      <div className="w-full text-left border-t border-line-200 pt-5">
        <div className="text-xs font-sans text-ink-500 mb-3 uppercase tracking-wider">
          Suggested inquiries
        </div>
        <div className="flex flex-col divide-y divide-line-200">
          {examplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onSelectPrompt(p.text, p.isEssay)}
              className="py-3 px-1 text-left font-sans text-sm text-ink-950 hover:text-evidence-600 hover:bg-paper-100/60 rounded transition-colors duration-fast flex items-center justify-between group focus-visible:outline-evidence-600"
            >
              <span>{p.text}</span>
              {p.isEssay && (
                <span className="text-[11px] font-mono text-evidence-600 bg-evidence-100 px-2 py-0.5 rounded-pill ml-2 flex-shrink-0">
                  Essay
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
