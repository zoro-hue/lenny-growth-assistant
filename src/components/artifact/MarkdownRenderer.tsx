import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="font-serif text-[16px] leading-relaxed text-ink-950 max-w-full">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="font-sans font-bold text-xl sm:text-2xl text-ink-950 mt-7 mb-3.5 tracking-tight border-b border-line-200 pb-2">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="font-sans font-semibold text-lg text-ink-950 mt-6 mb-2.5">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="font-sans font-medium text-base text-ink-950 mt-4 mb-2">
              {children}
            </h3>
          ),
          p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
          ul: ({ children }) => (
            <ul className="list-disc pl-5 mb-4 space-y-1.5">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-5 mb-4 space-y-1.5">{children}</ol>
          ),
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          hr: () => <hr className="border-line-200 my-6" />,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-evidence-600 pl-4 py-1 my-4 italic text-ink-700 bg-paper-100/40 rounded-r">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-5 border border-line-200 rounded-sm">
              <table className="min-w-full divide-y divide-line-200 text-left font-sans text-sm">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-paper-100 text-ink-700 text-xs font-semibold uppercase tracking-wider">
              {children}
            </thead>
          ),
          th: ({ children }) => <th className="px-3 py-2.5">{children}</th>,
          td: ({ children }) => (
            <td className="px-3 py-2 border-t border-line-200 text-ink-950">
              {children}
            </td>
          ),
          code: ({ children, className }) => {
            const isBlock = className && className.includes('language-');
            if (isBlock) {
              return (
                <code className="block font-mono text-xs bg-paper-100 p-3.5 rounded-sm border border-line-200 overflow-x-auto text-ink-950 my-3">
                  {children}
                </code>
              );
            }
            return (
              <code className="font-mono text-xs bg-paper-100 px-1.5 py-0.5 rounded-sm text-ink-950 border border-line-200">
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
