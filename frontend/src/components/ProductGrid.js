// components/ProductGrid.js
import React from "react";

const ProductGrid = ({ products }) => {
  return (
    <div className="product-grid">
      {products.map((product, index) => (
        <div key={index} className="product-card">
          <div className="product-content">
            {product.image && (
              <img src={product.image} alt={product.title} className="product-image" />
            )}
            <h3 className="product-title">{product.title}</h3>
            
            {/* Common details */}
            <p className="product-detail"><span className="label">Category:</span> {product.category}</p>
            <p className="product-detail"><span className="label">Price:</span> {product.price}</p>
            
            {/* Source-specific details */}
            {product.source === "Blinkit" && (
              <>
                <p className="product-detail"><span className="label">Weight:</span> {product.weight}</p>
                {product.old_price && <p className="product-detail"><span className="label">Old Price:</span> {product.old_price}</p>}
              </>
            )}
            
            {product.source === "BigBasket" && (
              <>
                <p className="product-detail"><span className="label">Brand:</span> {product.brand}</p>
                <p className="product-detail"><span className="label">Pack Size:</span> {product.pack_size}</p>
                {product.old_price && <p className="product-detail"><span className="label">Old Price:</span> {product.old_price}</p>}
                {product.rating && <p className="product-detail"><span className="label">Rating:</span> {product.rating}</p>}
                {product.review_count && <p className="product-detail"><span className="label">Reviews:</span> {product.review_count}</p>}
                {product.special_offer && <p className="product-detail"><span className="label">Special Offer:</span> {product.special_offer}</p>}
              </>
            )}
            
            {product.source === "Zepto" && (
              <>
                <p className="product-detail"><span className="label">Quantity:</span> {product.quantity}</p>
                {product.original_price && <p className="product-detail"><span className="label">Original Price:</span> {product.original_price}</p>}
              </>
            )}

            {/* Common optional details */}
            {product.discount && <p className="product-detail discount"><span className="label">Discount:</span> {product.discount}</p>}
            <p className="product-detail stock-status"><span className="label">In Stock:</span> {product.in_stock}</p>
            
            {product.product_url && (
              <p className="product-detail">
                <a href={product.product_url} target="_blank" rel="noopener noreferrer">View Product</a>
              </p>
            )}
            <p className="product-detail source"><span className="label">Source:</span> {product.source}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProductGrid;