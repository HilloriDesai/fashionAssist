import React, { useState, useRef, useEffect } from "react";
import { Message } from "@/types";
import { chatService } from "@/services/api";
import { ChatHeader } from "./chat/ChatHeader";
import { Message as MessageComponent } from "./chat/Message";
import { TypingIndicator } from "./chat/TypingIndicator";
import { ChatInput } from "./chat/ChatInput";

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

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      const response = await chatService.processMessage(
        inputValue,
        sessionId || undefined
      );

      // Save session ID if this is a new session
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
        localStorage.setItem("chatSessionId", response.session_id);
      }

      // Update messages with full history from response
      if (response.messages) {
        const formattedMessages: Message[] = response.messages.map(
          (msg: any) => ({
            id: msg.id || Date.now() + Math.random(),
            type: msg.role === "user" ? "user" : "bot",
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            recommendations: msg.response_data?.recommendations,
            responseType: msg.response_data?.type,
          })
        );
        setMessages(formattedMessages);
      } else {
        // Fallback to just adding the bot message if no history is provided
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
      }
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-100">
      <ChatHeader />

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto p-4 h-[calc(100vh-140px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <MessageComponent key={message.id} message={message} />
          ))}

          {/* Typing Indicator */}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSendMessage}
          isTyping={isTyping}
        />
      </div>
    </div>
  );
};
