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

            {product.source === "Swiggy" ? (
              <>
                <p className="product-detail">
                  <span className="label">Rating:</span> {product.rating}
                </p>
                <p className="product-detail">
                  <span className="label">Cuisine:</span> {product.cuisine}
                </p>
                <p className="product-detail">
                  <span className="label">Location:</span> {product.location}
                </p>
              </>
            ) : (
              <>
                {product.category && (
                  <p className="product-detail">
                    <span className="label">Category:</span> {product.category}
                  </p>
                )}
                {product.weight && (
                  <p className="product-detail">
                    <span className="label">Weight:</span> {product.weight}
                  </p>
                )}
                <p className="product-detail">
                  <span className="label">Price:</span> {product.price}
                </p>
                {product.old_price && (
                  <p className="product-detail">
                    <span className="label">Old Price:</span> {product.old_price}
                  </p>
                )}
                {product.discount && (
                  <p className="product-detail">
                    <span className="label">Discount:</span> {product.discount}
                  </p>
                )}
                <p className="product-detail">
                  <span className="label">In Stock:</span> {product.in_stock}
                </p>
                {product.product_url && (
                  <p className="product-detail">
                    <a href={product.product_url} target="_blank" rel="noopener noreferrer">
                      View Product
                    </a>
                  </p>
                )}
              </>
            )}

            {product.source && (
              <p className="product-detail source">
                <span className="label">Source:</span> {product.source}
              </p>
            )}
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
        file: "/blinkit_products_part_1.json",
        transform: (product) => ({
          title: product.name || "Unknown Product",
          category: product.category || "N/A",
          weight: product.weight || "N/A",
          price: product.new_price || "Not Available",
          old_price: product.old_price || "N/A",
          discount: product.discount || "No discount",
          in_stock: product.in_stock || "Unknown",
          image: product.image_url || "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=90/assets/eta-icons/15-mins.png",
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
        file: "/bigbasket_products.json",
        transform: (product) => ({
          title: product.name || product.Name || "Unknown Product",
          price: product.price || "Not Available",
          discount: product.discount || "No discount",
          image: product.image_url || product['product_url'] || "",
          source: "BigBasket"
        })
      }
    ];

    try {
      setIsLoading(true);
      let results = [];

      for (const source of sources) {
        try {
          const response = await fetch(source.file);
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          const data = await response.json();
          
          const formattedProducts = data
            .map(source.transform)
            .filter(product => product.title && product.title !== "Unknown Product");
          
          results.push(...formattedProducts);
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
    if (isLoading) {
      return <div className="loading">Loading products...</div>;
    }

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