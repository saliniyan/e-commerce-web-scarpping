// components/Swiggy.js
import React from "react";
import ProductGrid from "./ProductGrid";

const Swiggy = ({ products }) => {
  const swiggyProducts = products.filter(product => product.source === "Swiggy");
  
  return (
    <div className="swiggy-container">
      <ProductGrid products={swiggyProducts} />
    </div>
  );
};

export default Swiggy;