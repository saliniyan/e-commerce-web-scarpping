import React, { useState, useEffect } from "react";
import "./App.css";

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
            {product.source === "Blinkit" ? (
              <>
                <p className="product-detail"><span className="label">Category:</span> {product.category}</p>
                <p className="product-detail"><span className="label">Weight:</span> {product.weight}</p>
              </>
            ) : product.source === "BigBasket" ? (
              <>
                <p className="product-detail"><span className="label">Category:</span> {product.category}</p>
                <p className="product-detail"><span className="label">Brand:</span> {product.brand}</p>
                <p className="product-detail"><span className="label">Pack Size:</span> {product.pack_size}</p>
              </>
            ) : product.source === "Swiggy" ? (
              <>
                <p className="product-detail"><span className="label">Rating:</span> {product.rating}</p>
                <p className="product-detail"><span className="label">Cuisine:</span> {product.cuisine}</p>
                <p className="product-detail"><span className="label">Location:</span> {product.location}</p>
              </>
            ) : null}
            <p className="product-detail"><span className="label">Price:</span> {product.price}</p>
            {product.old_price && <p className="product-detail"><span className="label">Old Price:</span> {product.old_price}</p>}
            {product.discount && <p className="product-detail"><span className="label">Discount:</span> {product.discount}</p>}
            <p className="product-detail"><span className="label">In Stock:</span> {product.in_stock}</p>
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

const App = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [productData, setProductData] = useState([]);
  const [activeTab, setActiveTab] = useState("zepto");
  const [isLoading, setIsLoading] = useState(true);

  const tabs = [
    { id: "zepto", label: "Zepto" },
    { id: "blinkit", label: "Blinkit" },
    { id: "bigbasket", label: "BigBasket" },
    { id: "swiggy", label: "Swiggy" },
    { id: "search", label: "Search All" },
  ];

  const fetchData = async () => {
    const sources = [
      { 
        name: "Zepto", 
        file: "/zepto_products.json",
        transform: (product) => ({
          title: product.name || "Unknown Product",
          price: product.price || "Not Available",
          discount: product.discount || "No discount",
          image: product.image_url || "",
          source: "Zepto"
        })
      },
      {
        name: "Blinkit",
        file: "/blinkit_products.json", 
        transform: (product) => ({
          title: product.name || "Unknown Product",
          category: product.category || "N/A",
          weight: product.weight || "N/A",
          price: product.new_price || "Not Available",
          old_price: product.old_price || "N/A",
          discount: product.discount || "No discount",
          in_stock: product.in_stock || "Unknown",
          image: product.image_url || "",
          source: "Blinkit",
          product_url: product.product_url || "",
        }),
      },
      { 
        name: "Swiggy", 
        file: "/swiggy_restaurants.json",
        transform: (product) => ({
          title: product.Name || product.title || "Unknown Restaurant",
          rating: product.Rating || "",
          cuisine: product.Cuisine || "",
          location: product.Location || "",
          image: product['Image URL'] || "",
          source: "Swiggy"
        })
      },
      { 
        name: "BigBasket", 
        file: "/big_products.json",
        transform: (product) => ({
          title: product.name || "Unknown Product",
          category: product.category || "N/A",
          brand: product.brand || "Unknown Brand",
          pack_size: product.pack_size || "N/A",
          price: product.new_price || "Not Available",
          old_price: product.old_price || "N/A",
          discount: product.discount || "No discount",
          in_stock: product.in_stock || "Unknown",
          rating: product.rating || "No rating",
          review_count: product.review_count || "No reviews",
          image: product.image_url || "",
          source: "BigBasket",
          product_url: product.product_url || "",
        })
      }
    ];

    try {
      setIsLoading(true);
      let results = [];
      for (const source of sources) {
        try {
          const response = await fetch(source.file);
          if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
          const data = await response.json();
          results.push(...data.map(source.transform).filter(product => product.title !== "Unknown Product"));
        } catch (error) {
          console.error(`Error fetching ${source.name} data:`, error);
        }
      }
      setProductData(results);
      setIsLoading(false);
    } catch (error) {
      console.error("Data fetching error:", error);
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const getFilteredProducts = (source) => productData.filter(product => product.source === source);
  const getSearchResults = () => productData.filter(product => product.title.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="container">
      <h1 className="main-title">Price Comparison</h1>
      <div className="layout">
        <div className="tabs-container">
          {tabs.map(tab => <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`tab ${activeTab === tab.id ? 'active' : ''}`}>{tab.label}</button>)}
        </div>
        <div className="content-area">
          {isLoading ? <div className="loading">Loading products...</div> : activeTab === "search" ? <ProductGrid products={getSearchResults()} /> : <ProductGrid products={getFilteredProducts(tabs.find(tab => tab.id === activeTab)?.label)} />}
        </div>
      </div>
    </div>
  );
};

export default App;
