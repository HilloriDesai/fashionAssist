import React, { useState, useRef, useEffect } from "react";
import { Send, ShoppingBag, Sparkles, Heart, Star } from "lucide-react";

const FashionChatbot = () => {
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
    stage: "initial", // initial, followup, recommendation
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Sample product data (replace with your actual API)
  const sampleProducts = [
    {
      id: 1,
      name: "Linen Summer Dress",
      price: 85,
      image:
        "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=400&fit=crop",
      category: "dress",
      brand: "Everlane",
      rating: 4.8,
      match_reason: "Perfect casual summer vibe with breathable linen",
    },
    {
      id: 2,
      name: "Relaxed Cotton Top",
      price: 45,
      image:
        "https://images.unsplash.com/photo-1564257591-5c8d1e7e5b4b?w=300&h=400&fit=crop",
      category: "top",
      brand: "COS",
      rating: 4.6,
      match_reason: "Great for brunch with relaxed fit",
    },
    {
      id: 3,
      name: "Flowy Midi Skirt",
      price: 65,
      image:
        "https://images.unsplash.com/photo-1583496661160-fb5886a13d27?w=300&h=400&fit=crop",
      category: "skirt",
      brand: "& Other Stories",
      rating: 4.7,
      match_reason: "Feminine and perfect for summer occasions",
    },
  ];

  // Mock AI processing function (replace with your actual API call)
  const processMessage = async (userMessage) => {
    // Simulate AI processing
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const lowerMessage = userMessage.toLowerCase();

    // Simple rule-based logic for demo (replace with your actual AI)
    if (conversation.followupCount === 0) {
      // First interaction - ask follow-up
      const needsCategory =
        !lowerMessage.includes("dress") &&
        !lowerMessage.includes("top") &&
        !lowerMessage.includes("skirt");
      const needsBudget =
        !lowerMessage.includes("$") &&
        !lowerMessage.includes("budget") &&
        !lowerMessage.includes("under");

      if (needsCategory || needsBudget) {
        return {
          type: "followup",
          message: needsCategory
            ? "Love that vibe! Are you thinking dresses, tops & skirts, or something else? And any budget in mind? 💕"
            : "Perfect! What's your budget range? And any size preferences? ✨",
          attributes: extractAttributes(userMessage),
          stage: "followup",
        };
      }
    } else if (conversation.followupCount === 1) {
      // Second follow-up if needed
      const stillNeedsInfo =
        !lowerMessage.includes("size") && !lowerMessage.includes("$");
      if (stillNeedsInfo) {
        return {
          type: "followup",
          message:
            "Almost there! What size should I look for? And any must-haves like sleeveless, specific colors? 🎯",
          attributes: extractAttributes(userMessage),
          stage: "followup",
        };
      }
    }

    // Provide recommendations
    return {
      type: "recommendation",
      message:
        "Perfect! Based on your casual summer brunch vibe, I found some amazing pieces that match your style ✨",
      recommendations: sampleProducts,
      justification:
        "I selected breathable fabrics and relaxed fits that are perfect for summer brunching!",
      stage: "recommendation",
    };
  };

  const extractAttributes = (message) => {
    const attributes = {};
    const lowerMessage = message.toLowerCase();

    // Simple extraction (replace with your sophisticated logic)
    if (lowerMessage.includes("dress")) attributes.category = "dress";
    if (lowerMessage.includes("casual")) attributes.style = "casual";
    if (lowerMessage.includes("summer")) attributes.season = "summer";

    return attributes;
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

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const ProductCard = ({ product }) => (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
      <div className="relative">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-48 object-cover"
        />
        <button className="absolute top-3 right-3 p-2 bg-white/80 backdrop-blur-sm rounded-full hover:bg-white transition-colors">
          <Heart className="w-4 h-4 text-gray-600 hover:text-red-500 transition-colors" />
        </button>
      </div>
      <div className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm text-gray-500">{product.brand}</span>
          <div className="flex items-center gap-1">
            <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
            <span className="text-xs text-gray-600">{product.rating}</span>
          </div>
        </div>
        <h3 className="font-semibold text-gray-900 mb-2">{product.name}</h3>
        <p className="text-xs text-gray-600 mb-3">{product.match_reason}</p>
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-gray-900">
            ${product.price}
          </span>
          <button className="bg-black text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors">
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );

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
                {message.recommendations && (
                  <div className="mt-6">
                    <div className="flex items-center gap-2 mb-4">
                      <ShoppingBag className="w-4 h-4 text-gray-600" />
                      <span className="text-sm font-medium text-gray-700">
                        Perfect matches for you:
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {message.recommendations.map((product) => (
                        <ProductCard key={product.id} product={product} />
                      ))}
                    </div>
                    {message.justification && (
                      <div className="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-100">
                        <p className="text-xs text-purple-700">
                          <strong>Why these work:</strong>{" "}
                          {message.justification}
                        </p>
                      </div>
                    )}
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
                rows="1"
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

export default FashionChatbot;
