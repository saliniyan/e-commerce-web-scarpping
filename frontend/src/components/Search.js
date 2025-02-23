// components/Search.js
import React from "react";
import ProductGrid from "./ProductGrid";

const Search = ({ products, searchQuery }) => {
  const searchResults = products.filter(product => 
    product.title.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div className="search-container">
      <ProductGrid products={searchResults} />
    </div>
  );
};

export default Search;