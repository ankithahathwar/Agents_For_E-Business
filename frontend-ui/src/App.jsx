import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  // Website States
  const [catalog, setCatalog] = useState([]);
  const [filteredCategory, setFilteredCategory] = useState('All');
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [cartCount, setCartCount] = useState(0);
  const [backendError, setBackendError] = useState(null);

  // Chatbot States
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hello! I am Marco, your personal tailoring consultant. Browse our collection on the left, or tell me what look you want to design today!" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => 'session_' + Math.random().toString(36).substring(2, 11));

  const chatEndRef = useRef(null);

  // 1. DYNAMIC DATA FETCH: Safe error checking wrapper
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/products')
      .then(res => {
        if (!res.ok) throw new Error(`Server returned status code ${res.status}`);
        return res.json();
      })
      .then(data => {
        // Double check that the backend actually sent an array, not an error dictionary
        if (Array.isArray(data)) {
          setCatalog(data);
          setBackendError(null);
        } else {
          console.error("Backend sent unexpected non-array data:", data);
          setBackendError("Database returned an error structure instead of a product list.");
        }
      })
      .catch(err => {
        console.error("Could not load dynamic database catalog:", err);
        setBackendError("Backend API server offline. Ensure 'uvicorn main:app --reload' is actively running on port 8000.");
      });
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleBotNavigation = (textLabel, linkTarget) => {
    if (!Array.isArray(catalog)) return;
    const searchString = (linkTarget + " " + textLabel).toLowerCase();

    const matchedItem = catalog.find(item =>
      searchString.includes((item.base_product_id || '').toLowerCase()) ||
      searchString.includes((item.name || '').toLowerCase())
    );

    if (matchedItem) {
      setSelectedProductId(matchedItem.base_product_id);
    } else {
      if (searchString.includes('suit')) setFilteredCategory('Suits');
      if (searchString.includes('saree')) setFilteredCategory('Sarees');
      if (searchString.includes('gown')) setFilteredCategory('Gowns');
      setSelectedProductId(null);
    }
  };

  const parseMarkdownLinks = (text) => {
    const regex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      const label = match[1];
      const link = match[2];
      parts.push(
        <button key={match.index} onClick={() => handleBotNavigation(label, link)} className="showroom-inline-link">
          {label}
        </button>
      );
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }
    return parts.length > 0 ? parts : text;
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userText }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_message: userText, session_id: sessionId })
      });
      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: "Connection error. Make sure your Python server is running!" }]);
    } finally {
      setIsLoading(false);
    }
  };

  const availableCategories = ['All', 'Suits', 'Sarees', 'Gowns'];

  // Safe string handler mapping logic to prevent crashes if categories are null
  const getDisplayCategory = (dbCategory) => {
    const cat = (dbCategory || '').toLowerCase();
    if (cat.includes('suit') || cat.includes('menswear')) return 'Suits';
    if (cat.includes('saree')) return 'Sarees';
    if (cat.includes('gown') || cat.includes('bridal')) return 'Gowns';
    return 'Other';
  };

  // Safe checks to guarantee execution arrays are initialized before array methods call
  const safeCatalog = Array.isArray(catalog) ? catalog : [];

  const visibleProducts = safeCatalog.filter(p => {
    if (filteredCategory === 'All') return true;
    return getDisplayCategory(p.category) === filteredCategory;
  });

  const selectedProduct = safeCatalog.find(p => p.base_product_id === selectedProductId);

  const getImagePlaceholder = (name) => {
    const title = (name || '').toLowerCase();
    if (title.includes('wall street') || title.includes('power')) return "https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?auto=format&fit=crop&q=80&w=500";
    if (title.includes('sartorial') || title.includes('bespoke')) return "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&q=80&w=500";
    if (title.includes('riviera') || title.includes('linen')) return "https://images.unsplash.com/photo-1534126511673-b6899657816a?auto=format&fit=crop&q=80&w=500";
    if (title.includes('saree') || title.includes('heritage')) return "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=500";
    return "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&q=80&w=500";
  };

  return (
    <div className="showroom-workspace">

      {/* LEFT SIDE: STANDALONE INDEPENDENT WEBSITE LAYER */}
      <div className="showroom-display-pane">
        <header className="showroom-navbar">
          <div className="logo" onClick={() => { setSelectedProductId(null); setFilteredCategory('All'); }}>
            ✨ MARCO LUXE SHOWROOM
          </div>
          <div className="cart-widget">🛒 Order Bag ({cartCount})</div>
        </header>

        <div className="showroom-filter-bar">
          {availableCategories.map(cat => (
            <button
              key={cat}
              className={`filter-tab ${filteredCategory === cat && !selectedProductId ? 'active' : ''}`}
              onClick={() => { setFilteredCategory(cat); setSelectedProductId(null); }}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="product-view-container">
          {backendError ? (
            /* CRASH SHEILD WARNING SCREEN */
            <div style={{ padding: '30px', background: '#2d1a1a', border: '1px solid #ff4444', borderRadius: '8px', color: '#ff8888', textAlign: 'left' }}>
              <h4>⚠️ Connection Disruption Detected</h4>
              <p>{backendError}</p>
              <button onClick={() => window.location.reload()} style={{ background: '#ff4444', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', marginTop: '10px', fontWeight: 'bold' }}>
                Retry Network Sync
              </button>
            </div>
          ) : selectedProduct ? (
            /* LAYER A: INDIVIDUAL PRODUCT VIEW PAGE */
            <div className="product-detail-page">
              <button className="back-btn" onClick={() => setSelectedProductId(null)}>← Back to Catalog</button>
              <div className="detail-layout">
                <img src={getImagePlaceholder(selectedProduct.name)} alt={selectedProduct.name} className="detail-img" />
                <div className="detail-info">
                  <span className="cat-badge">{selectedProduct.category}</span>
                  <h2>{selectedProduct.name}</h2>
                  <p className="description-text">{selectedProduct.description}</p>
                  <div className="price-tag">Bespoke Configuration Pricing</div>
                  <button className="add-to-cart-btn" onClick={() => setCartCount(c => c + 1)}>
                    Secure This Tailoring Canvas
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* LAYER B: STANDALONE INDEPENDENT SYSTEM CATALOG GRID */
            <div className="catalog-grid-layout">
              {visibleProducts.length === 0 ? (
                <p style={{ color: '#666', gridColumn: '1/-1' }}>No products found in this category slot.</p>
              ) : (
                visibleProducts.map(product => (
                  <div
                    key={product.base_product_id}
                    className="catalog-card"
                    onClick={() => setSelectedProductId(product.base_product_id)}
                  >
                    <div className="img-wrapper">
                      <img src={getImagePlaceholder(product.name)} alt={product.name} />
                    </div>
                    <div className="card-meta">
                      <h3>{product.name}</h3>
                      <span className="category-subtext">{product.category}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT SIDE: FLOATING COMPANION SALESMAN (Marco) */}
      <div className="assistant-sidebar-pane">
        <div className="assistant-header">
          <div>
            <h3>Marco</h3>
            <small style={{ color: '#888' }}>Bespoke Sales Advisor</small>
          </div>
          <span className="live-pulse">🟢 Online</span>
        </div>

        <div className="chat-message-stream">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              <div className="message-bubble">
                <p>{parseMarkdownLinks(msg.content)}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-row assistant">
              <div className="message-bubble typing-glow">
                Marco is searching the vault...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="assistant-input-tray">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Marco about fabric options, styles, combinations..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>Send</button>
        </form>
      </div>

    </div>
  );
}

export default App;