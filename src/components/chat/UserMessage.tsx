import React from 'react';
import { Message } from '../../types/chat';

interface UserMessageProps {
  message: Message;
}

export const UserMessage: React.FC<UserMessageProps> = ({ message }) => {
  return (
    <div className="flex flex-col items-end my-5 animate-user-message-in">
      <div className="max-w-[85%] sm:max-w-[75%] bg-paper-100 border border-line-200 rounded-md px-4 py-3 text-ink-950 font-sans text-[15px] leading-normal shadow-xs">
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
      <div className="text-[11px] font-mono text-ink-500 mt-1 px-1">
        {message.timestamp}
      </div>
    </div>
  );
};
