import React, { useState, useRef, useEffect } from "react";
import { Send, ShoppingBag, Sparkles } from "lucide-react";
import { Message } from "@/types";
import { chatService } from "@/services/api";
import ProductCard from "./ProductCard";

const initialMessage: Message = {
  id: 1,
  type: "bot",
  content:
    "Hi! I'm your personal style assistant ✨ Tell me what vibe you're going for and I'll help you find the perfect pieces!",
  timestamp: new Date(),
};

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([initialMessage]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history if session exists
  useEffect(() => {
    const savedSessionId = localStorage.getItem("chatSessionId");
    if (savedSessionId) {
      setSessionId(savedSessionId);
      loadChatHistory(savedSessionId);
    }
  }, []);

  const loadChatHistory = async (sid: string) => {
    try {
      const history = await chatService.getChatHistory(sid);
      if (!history.messages) {
        setMessages([initialMessage]);
        return;
      }
      const formattedMessages: Message[] = history.messages.map((msg: any) => ({
        id: Date.now() + Math.random(),
        type: msg.role === "user" ? "user" : "bot",
        content: msg.content,
        timestamp: new Date(msg.timestamp),
        recommendations: msg.response_data?.recommendations,
        responseType: msg.response_data?.type,
      }));
      setMessages(formattedMessages);
    } catch (error: any) {
      console.error("Error loading chat history:", error);
      // If session not found (404), clear the stored session ID and start fresh
      if (error.response?.status === 404) {
        localStorage.removeItem("chatSessionId");
        setSessionId(null);
        setMessages([initialMessage]);
      }
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    console.log("User Query:", inputValue);
    console.log("Current Message History:", messages);

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      const response = await chatService.processMessage(
        inputValue,
        sessionId || undefined
      );

      console.log("API Response:", {
        type: response.type,
        message: response.message,
        recommendations: response.recommendations,
        followup: response.followup_question,
      });

      // Save session ID if this is a new session
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
        localStorage.setItem("chatSessionId", response.session_id);
      }

      const botMessage: Message = {
        id: Date.now() + 1,
        type: "bot",
        content:
          response.message +
          (response.followup_question
            ? `\n\n${response.followup_question}`
            : ""),
        timestamp: new Date(),
        recommendations: response.recommendations,
        responseType: response.type,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error processing message:", error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: "bot",
        content:
          "Sorry, I had a little hiccup! Can you tell me again what you're looking for? 😊",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md shadow-sm border-b border-white/20">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-pink-500 to-purple-600 p-2 rounded-xl">
              <ShoppingBag className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-xl text-gray-900">
                Style Assistant
              </h1>
              <p className="text-sm text-gray-600">
                Your personal fashion curator
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto p-4 h-[calc(100vh-140px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
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
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl p-4 shadow-lg">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-500" />
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-white/20 p-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your style vibe... (e.g., 'casual summer brunch outfit')"
                className="w-full resize-none border-0 bg-transparent focus:ring-0 focus:outline-none text-gray-900 placeholder-gray-500"
                rows={1}
                style={{ maxHeight: "120px" }}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="bg-gradient-to-r from-pink-500 to-purple-600 text-white p-3 rounded-xl hover:from-pink-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="mt-2 flex gap-2">
            {[
              "casual brunch",
              "date night",
              "work meeting",
              "weekend vibes",
            ].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setInputValue(suggestion)}
                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
