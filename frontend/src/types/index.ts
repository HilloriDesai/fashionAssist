export interface Message {
  id: number;
  type: "user" | "bot";
  content: string;
  timestamp: Date;
  recommendations?: Product[];
  responseType?: string;
}

export interface Product {
  id: number;
  name: string;
  price: number;
  image: string;
  category: string;
  brand: string;
  rating: number;
  match_reason: string;
}

export interface ConversationState {
  followupCount: number;
  attributes: {
    category?: string;
    style?: string;
    season?: string;
    budget?: number;
    size?: string;
  };
  stage: "initial" | "followup" | "recommendation";
}

export interface ChatResponse {
  session_id: string;
  type: "followup" | "recommendation";
  message: string;
  recommendations?: Product[];
  attributes_used?: Record<string, any>;
  followup_question?: string;
  attributes_so_far?: Record<string, any>;
  final_attributes?: Record<string, any>;
  justification?: string;
  is_fallback?: boolean;
  current_state?: {
    attributes: Record<string, any>;
    followup_count: number;
  };
  messages?: Array<{
    role: string;
    content: string;
    timestamp: string;
    response_data?: any;
  }>;
}
