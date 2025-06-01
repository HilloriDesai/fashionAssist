import React from "react";
import { Sparkles } from "lucide-react";
import ProductCard from "./ProductCard";

/**
 * ChatMessage component displays a single chat message with optional product recommendations
 * @param {Object} message - The message object containing content and metadata
 * @returns {JSX.Element} A styled chat message component
 */
const ChatMessage = ({ message }) => {
  const isBot = message.type === "bot";

  return (
    <div className={`flex ${isBot ? "justify-start" : "justify-end"} mb-4`}>
      <div
        className={`max-w-[80%] ${
          isBot ? "bg-white" : "bg-black text-white"
        } rounded-2xl p-4 shadow-sm`}
      >
        <div className="flex items-start gap-2">
          {isBot && (
            <div className="bg-gradient-to-r from-pink-500 to-purple-600 p-2 rounded-xl">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
          )}
          <div className="flex-1">
            <p className="text-sm">{message.content}</p>
            {message.justification && (
              <p className="text-xs text-gray-500 mt-2">
                {message.justification}
              </p>
            )}
          </div>
        </div>

        {message.recommendations && message.recommendations.length > 0 && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {message.recommendations.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
