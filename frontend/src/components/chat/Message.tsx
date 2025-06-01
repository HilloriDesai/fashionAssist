import React from "react";
import { Sparkles, ShoppingBag } from "lucide-react";
import { Message as MessageType } from "@/types";
import ProductCard from "./ProductCard";

interface MessageProps {
  message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  return (
    <div
      className={`flex ${
        message.type === "user" ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[80%] ${
          message.type === "user"
            ? "bg-black text-white"
            : "bg-white text-gray-900"
        } rounded-2xl p-4 shadow-lg`}
      >
        {message.type === "bot" && (
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-purple-600">
              Style Assistant
            </span>
          </div>
        )}
        <p className="text-sm leading-relaxed">{message.content}</p>

        {/* Product Recommendations */}
        {message.responseType === "recommendation" &&
          message.recommendations && (
            <div className="mt-6">
              <div className="flex items-center gap-2 mb-4">
                <ShoppingBag className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">
                  {message.recommendations.length > 0
                    ? "Perfect matches for you:"
                    : "Looks like no exact matches found."}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {message.recommendations.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            </div>
          )}

        <div className="text-xs opacity-60 mt-2">
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
};
