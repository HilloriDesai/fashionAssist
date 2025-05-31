import axios from "axios";
import { ChatResponse } from "@/types";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const chatService = {
  async processMessage(
    message: string,
    sessionId?: string,
    currentAttributes?: Record<string, any>
  ): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>("/chat", {
        message,
        session_id: sessionId,
        current_attributes: currentAttributes,
      });
      console.log("chat response: processMessage", response.data);
      return response.data;
    } catch (error) {
      console.error("Error processing message:", error);
      throw error;
    }
  },

  async getChatHistory(sessionId: string): Promise<ChatResponse> {
    try {
      const response = await api.get<ChatResponse>(`/chat/${sessionId}`);
      console.log(response.data);
      return response.data;
    } catch (error) {
      console.error("Error fetching chat history:", error);
      throw error;
    }
  },
};
