import React from 'react';

/**
 * KnowledgeNetworkGraphic
 * A subtle, lightweight editorial SVG visualization representing:
 * Lenny's Podcast → Transcript → Evidence → Insight → Action
 *
 * Designed with restrained ink/paper/evidence tones, minimal node connections,
 * and quiet ambient motion.
 */
export const KnowledgeNetworkGraphic: React.FC = () => {
  const nodes = [
    { id: 'podcast', label: "Lenny's Podcast", cx: 60, cy: 38, radius: 4, type: 'origin' },
    { id: 'transcript', label: 'Transcript', cx: 170, cy: 62, radius: 4.5, type: 'core' },
    { id: 'evidence', label: 'Evidence', cx: 280, cy: 30, radius: 5, type: 'evidence' },
    { id: 'insight', label: 'Insight', cx: 390, cy: 60, radius: 4.5, type: 'core' },
    { id: 'action', label: 'Action', cx: 490, cy: 36, radius: 4, type: 'action' },
  ];

  return (
    <div
      className="w-full max-w-[560px] mx-auto mb-6 px-4 select-none pointer-events-none animate-network-float"
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 550 90"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-auto overflow-visible opacity-85"
      >
        <defs>
          {/* Subtle line gradient using evidence tones */}
          <linearGradient id="networkGradient" x1="50" y1="40" x2="500" y2="40" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#D5D1C5" stopOpacity="0.4" />
            <stop offset="50%" stopColor="#2F5D50" stopOpacity="0.65" />
            <stop offset="100%" stopColor="#D5D1C5" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {/* Connecting backbone curves */}
        <path
          d="M 60 38 C 110 38, 120 62, 170 62 C 220 62, 230 30, 280 30 C 330 30, 340 60, 390 60 C 440 60, 450 36, 490 36"
          stroke="url(#networkGradient)"
          strokeWidth="1.25"
          strokeDasharray="3 3"
          strokeLinecap="round"
          className="opacity-70"
        />

        {/* Connecting secondary branches */}
        <path
          d="M 170 62 Q 225 76 280 30"
          stroke="#D5D1C5"
          strokeWidth="0.75"
          strokeDasharray="2 4"
          strokeOpacity="0.4"
        />
        <path
          d="M 280 30 Q 335 16 390 60"
          stroke="#D5D1C5"
          strokeWidth="0.75"
          strokeDasharray="2 4"
          strokeOpacity="0.4"
        />

        {/* Nodes & Labels */}
        {nodes.map((node) => {
          const isEvidence = node.type === 'evidence';
          const isAction = node.type === 'action';
          const isOrigin = node.type === 'origin';

          return (
            <g key={node.id} className="transition-all duration-base">
              {/* Outer halo for Evidence node */}
              {isEvidence && (
                <circle
                  cx={node.cx}
                  cy={node.cy}
                  r={node.radius + 5}
                  fill="#2F5D50"
                  fillOpacity="0.12"
                  className="animate-network-pulse"
                />
              )}

              {/* Node base circle */}
              <circle
                cx={node.cx}
                cy={node.cy}
                r={node.radius}
                fill={isEvidence ? '#2F5D50' : '#FDFCFA'}
                stroke={isEvidence ? '#2F5D50' : isAction ? '#3A4050' : '#B3ADA0'}
                strokeWidth={isEvidence ? '2' : '1.5'}
              />

              {/* Center inner pin */}
              {!isEvidence && (
                <circle
                  cx={node.cx}
                  cy={node.cy}
                  r={1.5}
                  fill={isOrigin ? '#8C857B' : '#3A4050'}
                />
              )}

              {/* Label */}
              <text
                x={node.cx}
                y={node.cy + (node.cy > 50 ? 18 : -12)}
                textAnchor="middle"
                className={`font-sans text-[10px] tracking-wider uppercase font-medium fill-current ${
                  isEvidence
                    ? 'text-evidence-700 font-semibold'
                    : isOrigin || isAction
                    ? 'text-ink-700'
                    : 'text-ink-500'
                }`}
                style={{ fontSize: '9.5px', letterSpacing: '0.06em' }}
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
