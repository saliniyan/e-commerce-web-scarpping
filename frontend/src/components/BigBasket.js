// components/BigBasket.js
import React from "react";
import ProductGrid from "./ProductGrid";

const BigBasket = ({ products }) => {
  const bigBasketProducts = products.filter(product => product.source === "BigBasket");
  
  return (
    <div className="bigbasket-container">
      <ProductGrid products={bigBasketProducts} />
    </div>
  );
};

export default BigBasket;