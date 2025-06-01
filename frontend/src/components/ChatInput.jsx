import React from "react";
import { Send } from "lucide-react";

/**
 * ChatInput component provides a text input field for sending messages
 * @param {Object} props - Component props
 * @param {string} props.value - Current input value
 * @param {Function} props.onChange - Handler for input changes
 * @param {Function} props.onSend - Handler for sending messages
 * @param {boolean} props.isTyping - Whether the bot is currently typing
 * @returns {JSX.Element} A styled chat input component
 */
const ChatInput = ({ value, onChange, onSend, isTyping }) => {
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-md border-t border-white/20 p-4">
      <div className="max-w-4xl mx-auto flex gap-2">
        <div className="flex-1 relative">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Tell me what you're looking for..."
            className="w-full p-4 pr-12 rounded-2xl border border-gray-200 focus:border-black focus:ring-0 resize-none"
            rows={1}
            disabled={isTyping}
          />
          <button
            onClick={onSend}
            disabled={!value.trim() || isTyping}
            className="absolute right-3 bottom-3 p-2 bg-black text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-800 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
