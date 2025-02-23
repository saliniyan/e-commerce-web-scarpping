// components/Blinkit.js
import React from "react";
import ProductGrid from "./ProductGrid";

const Blinkit = ({ products }) => {
  const blinkitProducts = products.filter(product => product.source === "Blinkit");
  
  return (
    <div className="blinkit-container">
      <ProductGrid products={blinkitProducts} />
    </div>
  );
};

export default Blinkit;