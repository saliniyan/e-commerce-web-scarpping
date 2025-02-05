import React, { useState } from "react";
import "./App.css";

// ProductGrid component for displaying products
const ProductGrid = ({ products }) => {
  return (
    <div className="product-grid">
      {products.map((product, index) => (
        <div key={index} className="product-card">
          <div className="product-content">
            {product.image && (
              <img
                src={product.image}
                alt={product.title}
                className="product-image"
              />
            )}
            <h3 className="product-title">{product.title}</h3>
            <p className="product-detail">
              <span className="label">Price:</span> {product.price}
            </p>
            <p className="product-detail">
              <span className="label">Discount:</span> {product.discount}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

// Main App component
const App = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [productData, setProductData] = useState([]);
  const [activeTab, setActiveTab] = useState("zepto");

  const tabs = [
    { id: "zepto", label: "Zepto" },
    { id: "blinkit", label: "Blinkit" },
    { id: "bigbasket", label: "BigBasket" },
    { id: "swiggy", label: "Swiggy" },
    { id: "search", label: "Search All" },
  ];

  const fetchData = async () => {
    const sources = [
      { name: "Blinkit", file: "/blinkit_multi_category_products.json" },
      { name: "BigBasket", file: "/bigbasket_products.json" },
      { name: "Swiggy", file: "/swiggy_restaurants.json" },
      { name: "Zepto", file: "/zepto_products.json" },
    ];

    let results = [];
    for (const source of sources) {
      try {
        const response = await fetch(source.file);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const text = await response.text();
        const data = JSON.parse(text);
        
        const formattedProducts = data.map((product) => ({
          title: product.name || product.Name || "Unknown Product",
          price: product.price || "Not Available",
          discount: product.discount || "No discount",
          image: product.image_url || product["Image URL"] || "",
          source: source.name,
        })).filter(Boolean);
        
        results.push(...formattedProducts);
      } catch (error) {
        console.error(`Error fetching ${source.name} data:`, error);
      }
    }
    setProductData(results);
  };

  // Filter products based on source and search query
  const getFilteredProducts = (source) => {
    return productData.filter((product) => product.source === source);
  };

  const getSearchResults = () => {
    return productData.filter((product) =>
      product.title.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  // Load data when component mounts
  React.useEffect(() => {
    fetchData();
  }, []);

  const renderTabContent = () => {
    if (activeTab === "search") {
      return (
        <div>
          <div className="search-container">
            <input
              type="text"
              placeholder="Search for any product..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
          <ProductGrid products={getSearchResults()} />
        </div>
      );
    }
    
    const source = tabs.find(tab => tab.id === activeTab)?.label;
    return <ProductGrid products={getFilteredProducts(source)} />;
  };

  return (
    <div className="container">
      <h1 className="main-title">Price Comparison</h1>
      
      <div className="layout">
        {/* Vertical Tabs */}
        <div className="tabs-container">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="content-area">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default App;