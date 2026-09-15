import React from 'react';
import { TrendingUp, Repeat, Target, Feather, ArrowRight, BookOpen } from 'lucide-react';
import { KnowledgeNetworkGraphic } from './KnowledgeNetworkGraphic';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string, isEssay?: boolean) => void;
}

interface SuggestedCard {
  category: string;
  icon: React.ComponentType<{ className?: string }>;
  text: string;
  badge?: string;
  isEssay: boolean;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const suggestedCards: SuggestedCard[] = [
    {
      category: 'RETENTION',
      icon: TrendingUp,
      text: 'How do top product leaders determine whether their cohort retention curve has flattened?',
      badge: 'Benchmark',
      isEssay: false,
    },
    {
      category: 'GROWTH',
      icon: Repeat,
      text: 'Why does Brian Balfour argue that traditional acquisition funnels are dead?',
      badge: 'Loops',
      isEssay: false,
    },
    {
      category: 'PMF',
      icon: Target,
      text: "What was Rahul Vohra's 4-step framework for Superhuman's PMF engine?",
      badge: 'Framework',
      isEssay: false,
    },
    {
      category: 'ESSAY',
      icon: Feather,
      text: 'Write a Ship 30/30 playbook on pricing tiers based on Madhavan Ramanujam.',
      badge: 'Ship 30/30',
      isEssay: true,
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[64vh] max-w-[680px] mx-auto text-center px-4 py-8 sm:py-12">
      {/* Knowledge Network Graphic */}
      <KnowledgeNetworkGraphic />

      {/* Hero Icon with subtle entrance & idle float */}
      <div className="w-10 h-10 rounded-full bg-evidence-100 flex items-center justify-center mb-4 text-evidence-600 shadow-xs border border-evidence-600/15 animate-hero-icon">
        <BookOpen className="w-5 h-5" />
      </div>

      {/* Main Headline */}
      <h1 className="font-serif text-xl sm:text-2xl text-ink-950 font-semibold mb-2.5 tracking-tight max-w-[580px]">
        Ask about product and growth, grounded in Lenny's Podcast
      </h1>

      {/* Editorial Subtitle */}
      <p className="font-sans text-sm text-ink-700 max-w-[500px] mb-8 leading-relaxed">
        Every claim is traced directly to transcript evidence with timestamps, guest citations, and verifiable quotes.
      </p>

      {/* Suggested Inquiries Section */}
      <div className="w-full text-left pt-2">
        <div className="flex items-center justify-between mb-3 px-0.5">
          <span className="text-[11px] font-mono uppercase tracking-wider text-ink-500 font-semibold">
            Suggested Inquiries
          </span>
          <span className="text-[11px] font-sans text-ink-400">
            Click to research
          </span>
        </div>

        {/* 2x2 Grid of Refined Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {suggestedCards.map((card, idx) => {
            const IconComponent = card.icon;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectPrompt(card.text, card.isEssay)}
                className="group relative flex flex-col justify-between p-3.5 rounded-md bg-paper-0/70 hover:bg-paper-0 border border-line-200 hover:border-line-300 text-left transition-all duration-150 hover:-translate-y-0.5 shadow-xs focus-visible:outline-evidence-600"
              >
                {/* Top: Category Pill + Action Badge */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-1.5 text-[10px] font-mono uppercase tracking-wider text-ink-500 font-semibold">
                    <IconComponent className="w-3 h-3 text-evidence-600 group-hover:scale-105 transition-transform duration-150" />
                    <span>{card.category}</span>
                  </div>
                  {card.badge && (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-pill bg-paper-100 text-ink-700 border border-line-200 group-hover:border-evidence-600/30 group-hover:text-evidence-700 transition-colors">
                      {card.badge}
                    </span>
                  )}
                </div>

                {/* Question */}
                <p className="font-sans text-xs sm:text-[13px] font-medium text-ink-950 leading-snug mb-3 group-hover:text-ink-950">
                  {card.text}
                </p>

                {/* Bottom: subtle arrow appearing/sliding on hover */}
                <div className="flex items-center justify-end text-xs text-ink-400 group-hover:text-evidence-600 font-sans mt-auto pt-1">
                  <span className="text-[11px] opacity-0 group-hover:opacity-100 transition-opacity duration-150 mr-1">
                    Explore
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform duration-150" />
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

