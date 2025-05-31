import { Heart } from "lucide-react";
import { Product } from "@/types";

interface ProductCardProps {
  product: Product;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product }) => (
  <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
    <div className="relative">
      <button className="absolute top-3 right-3 p-2 bg-white/80 backdrop-blur-sm rounded-full hover:bg-white transition-colors">
        <Heart className="w-4 h-4 text-gray-600 hover:text-red-500 transition-colors" />
      </button>
    </div>
    <div className="p-4">
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
