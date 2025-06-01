import React from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isTyping: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  isTyping,
}) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-white/20 p-4">
      <div className="flex gap-3 items-end">
        <div className="flex-1">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your style vibe... (e.g., 'casual summer brunch outfit')"
            className="w-full resize-none border-0 bg-transparent focus:ring-0 focus:outline-none text-gray-900 placeholder-gray-500"
            rows={1}
            style={{ maxHeight: "120px" }}
          />
        </div>
        <button
          onClick={onSend}
          disabled={!value.trim() || isTyping}
          className="bg-gradient-to-r from-pink-500 to-purple-600 text-white p-3 rounded-xl hover:from-pink-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
      <div className="mt-2 flex gap-2">
        {["casual brunch", "date night", "work meeting", "weekend vibes"].map(
          (suggestion) => (
            <button
              key={suggestion}
              onClick={() => onChange(suggestion)}
              className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs rounded-full transition-colors"
            >
              {suggestion}
            </button>
          )
        )}
      </div>
    </div>
  );
};
