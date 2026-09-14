import React from 'react';

interface HtmlSandboxFrameProps {
  htmlContent: string;
  title: string;
  allowScripts: boolean;
}

export const HtmlSandboxFrame: React.FC<HtmlSandboxFrameProps> = ({
  htmlContent,
  title,
  allowScripts,
}) => {
  // SECURITY MODEL:
  // 1. When allowScripts is false: sandbox="" enforces maximum isolation:
  //    - No scripts, no forms, no popups, opaque origin, zero access to parent window/cookies/storage.
  // 2. When allowScripts is true: sandbox="allow-scripts" (STRICTLY WITHOUT allow-same-origin):
  //    - Scripts can run within the iframe's isolated scope, but the origin remains opaque ("null"),
  //      completely blocking access to parent.document, parent window, cookies, localStorage, and session tokens.
  const sandboxFlags = allowScripts ? 'allow-scripts' : '';

  // Sanitize any attempt to hijack parent window or navigate top frame
  const safeContent = React.useMemo(() => {
    if (!htmlContent) return '';
    return htmlContent
      .replace(/<base[^>]*target\s*=\s*['"]?_(?:top|parent)['"]?[^>]*>/gi, '')
      .replace(/<meta[^>]*http-equiv\s*=\s*['"]?refresh['"]?[^>]*>/gi, '');
  }, [htmlContent]);

  return (
    <iframe
      srcDoc={safeContent}
      title={`Sandboxed view of ${title}`}
      sandbox={sandboxFlags}
      className="w-full h-full min-h-[520px] bg-paper-0 border-none rounded"
    />
  );
};
