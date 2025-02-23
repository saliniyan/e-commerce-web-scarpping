// components/Zepto.js
import React from "react";
import ProductGrid from "./ProductGrid";

const Zepto = ({ products }) => {
  const zeptoProducts = products.filter(product => product.source === "Zepto");
  
  return (
    <div className="zepto-container">
      <ProductGrid products={zeptoProducts} />
    </div>
  );
};

export default Zepto;