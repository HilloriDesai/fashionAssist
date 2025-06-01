import React, { useState, useRef, useEffect } from "react";
import Header from "./components/Header";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";

/**
 * Main App component that manages the chat interface and state
 * @returns {JSX.Element} The main application component
 */
const App = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      content:
        "Hi! I'm your personal style assistant ✨ Tell me what vibe you're going for and I'll help you find the perfect pieces!",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [conversation, setConversation] = useState({
    followupCount: 0,
    attributes: {},
    stage: "initial",
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const processMessage = async (userMessage) => {
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          current_attributes: conversation.attributes,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to process message");
      }

      const data = await response.json();
      return {
        type: data.type,
        message: data.message,
        recommendations: data.recommendations,
        justification: data.justification,
        stage: data.type === "followup" ? "followup" : "recommendation",
      };
    } catch (error) {
      console.error("Error processing message:", error);
      throw error;
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      const response = await processMessage(inputValue);

      setConversation((prev) => ({
        ...prev,
        followupCount:
          response.type === "followup"
            ? prev.followupCount + 1
            : prev.followupCount,
        attributes: { ...prev.attributes, ...response.attributes },
        stage: response.stage,
      }));

      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: response.message,
        timestamp: new Date(),
        recommendations: response.recommendations,
        justification: response.justification,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error processing message:", error);
      const errorMessage = {
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
      <Header />

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white/50 backdrop-blur-sm rounded-3xl shadow-lg p-6 min-h-[60vh] flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto mb-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <ChatInput
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSendMessage}
            isTyping={isTyping}
          />
        </div>
      </div>
    </div>
  );
};

export default App;
