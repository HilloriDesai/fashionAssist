import React from "react";
import { Heart, Star } from "lucide-react";

interface Product {
  id: string | number;
  brand: string;
  name: string;
  price: number;
  rating: number;
  match_reason: string;
  image_url?: string;
}

interface ProductCardProps {
  product: Product;
}

/**
 * ProductCard component displays a single product with its details
 * @param {ProductCardProps} props - The props containing the product object
 * @returns {JSX.Element} A styled product card component
 */
const ProductCard: React.FC<ProductCardProps> = ({ product }) => (
  <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
    <div className="relative">
      <button
        className="absolute top-3 right-3 p-2 bg-white/80 backdrop-blur-sm rounded-full hover:bg-white transition-colors"
        aria-label="Add to favorites"
      >
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
          ${product.price.toFixed(2)}
        </span>
        <button
          className="bg-black text-white px-2 py-2 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
          aria-label={`Add ${product.name} to cart`}
        >
          Add to Cart
        </button>
      </div>
    </div>
  </div>
);

export default ProductCard;
