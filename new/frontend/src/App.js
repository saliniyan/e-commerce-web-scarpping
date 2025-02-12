// App.js
import React, { useState, useEffect } from "react";
import "./App.css";
import Blinkit from "./components/Blinkit";
import BigBasket from "./components/BigBasket";
import Zepto from "./components/Zepto";
import Swiggy from "./components/Swiggy";
import Search from "./components/Search";

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
          category: product.category || "N/A",
          price: product.price || "Not Available",
          quantity: product.quantity || "N/A",
          original_price: product.original_price || "N/A",
          discount: product.discount || "No discount",
          in_stock: product.in_stock || "Unknown",
          image: product.image_url || "",
          product_url: product.product_link || "",
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
          product_url: product.product_url || "",
          source: "Blinkit"
        }),
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
          special_offer: product.special_offer || null,
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

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
    if (activeTab !== "search") {
      setActiveTab("search");
    }
  };

  const renderActiveComponent = () => {
    if (isLoading) return <div className="loading">Loading products...</div>;

    switch (activeTab) {
      case "zepto":
        return <Zepto products={productData} />;
      case "blinkit":
        return <Blinkit products={productData} />;
      case "bigbasket":
        return <BigBasket products={productData} />;
      case "swiggy":
        return <Swiggy products={productData} />;
      case "search":
        return <Search products={productData} searchQuery={searchQuery} />;
      default:
        return null;
    }
  };

  return (
    <div className="container">
      <h1 className="main-title">Price Comparison</h1>
      <div className="search-box">
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={handleSearch}
          className="search-input"
        />
      </div>
      <div className="layout">
        <div className="tabs-container">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="content-area">
          {renderActiveComponent()}
        </div>
      </div>
    </div>
  );
};

export default App;