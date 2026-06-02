import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  // Website Core States
  const [catalog, setCatalog] = useState([]);
  const [filteredCategory, setFilteredCategory] = useState('All');
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Customization Configuration States for Active View
  const [activeFabric, setActiveFabric] = useState(null);
  const [activeLining, setActiveLining] = useState(null);

  // Advanced Cart State Engine
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [backendError, setBackendError] = useState(null);

  // Chatbot Connection States
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Welcome back to the showroom floor. I am Marco, your personal stylist. Let's begin systematically. What category of attire or look are we designing today?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => 'session_' + Math.random().toString(36).substring(2, 11));

  const chatEndRef = useRef(null);

  // Fetch all 160 items from your Postgres database server with safety wrappers
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/products')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP Error Status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data)) {
          setCatalog(data);
          setBackendError(null);
        } else {
          setBackendError("Database returned an invalid layout map structure.");
        }
      })
      .catch(err => {
        console.error("Database sync disruption:", err);
        setBackendError("Cannot connect to your FastAPI server. Make sure 'uvicorn main:app --reload' is running on port 8000.");
      });
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sync default options when a customer swaps active product cards
  const handleProductSelect = (productId) => {
    const product = catalog.find(p => p.base_product_id === productId);
    if (product) {
      const matrix = parseMatrix(product.customization_matrix);
      setSelectedProductId(productId);
      setActiveFabric(matrix.fabrics?.[0] || null);
      setActiveLining(matrix.lining_options?.[0] || "Standard Unlined Layout");
    }
  };

  // SMART ROUTE INTERCEPTOR: Automatically maps bot commands to active UI actions
  const handleBotNavigation = (textLabel, linkTarget) => {
    if (!Array.isArray(catalog)) return;
    const cleanTarget = linkTarget.toLowerCase();
    const cleanLabel = textLabel.toLowerCase();

    // Context Action A: Fixed lining selection intercept link router mapping rule match loop!
    if (cleanTarget.includes('lining') || cleanTarget.includes('apply lining')) {
      if (selectedProductId) {
        const product = catalog.find(p => p.base_product_id === selectedProductId);
        const matrix = parseMatrix(product?.customization_matrix);

        // Use loose text checks to map the conversational label onto the exact technical database option
        const targetOptionMatch = matrix.lining_options?.find(opt =>
          textLabel.toLowerCase().includes(opt.toLowerCase()) ||
          opt.toLowerCase().includes(cleanLabel.replace('apply ', ''))
        );
        if (targetOptionMatch) {
          setActiveLining(targetOptionMatch);
          return;
        }
      }
      // Fallback fallback string clean mechanism
      setActiveLining(textLabel.replace(/Apply\s+/i, ''));
      return;
    }

    // Context Action B: Intercept fabric configuration change commands
    if (cleanTarget.includes('fabric')) {
      if (selectedProductId) {
        const product = catalog.find(p => p.base_product_id === selectedProductId);
        const matrix = parseMatrix(product?.customization_matrix);
        const match = matrix.fabrics?.find(f => textLabel.includes(f.name) || f.name.toLowerCase().includes(cleanLabel));
        if (match) setActiveFabric(match);
      } else {
        setFilteredCategory('Bespoke Fabrics');
      }
      return;
    }

    // Context Action C: Intercept standard garment navigation paths
    const matchedItem = catalog.find(item =>
      cleanTarget.includes((item.base_product_id || '').toLowerCase()) ||
      cleanTarget.includes((item.name || '').toLowerCase()) ||
      (item.name || '').toLowerCase().includes(cleanLabel)
    );

    if (matchedItem) {
      handleProductSelect(matchedItem.base_product_id);
    }
  };

  // TEXT SCRUBBER CLEANER: Completely strips raw asterisks out of text nodes while drawing clean link inputs
  const formatAndParseChatText = (text) => {
    let scrubbedText = text.replace(/\*\*/g, '').replace(/\*/g, '•');

    const regex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(scrubbedText)) !== null) {
      if (match.index > lastIndex) {
        parts.push(scrubbedText.substring(lastIndex, match.index));
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
    if (lastIndex < scrubbedText.length) {
      parts.push(scrubbedText.substring(lastIndex));
    }
    return parts.length > 0 ? parts : scrubbedText;
  };

  // --- RESTORED UNBROKEN MESSAGING ACTION HANDLER ---
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
      setMessages((prev) => [...prev, { role: 'assistant', content: "Server interaction break. Re-verify Python pipeline is active!" }]);
    } finally {
      setIsLoading(false);
    }
  };

  // DYNAMIC TRANSACTION ENGINE: Handles nested garment configurations vs standalone fabric lengths
  const handleAddToCart = (type, fabricData = null, customLength = 3) => {
    if (type === 'apparel') {
      const product = catalog.find(p => p.base_product_id === selectedProductId);
      if (!product) return;

      setCart(prevCart => {
        const existingIndex = prevCart.findIndex(item =>
          item.id === product.base_product_id &&
          item.fabric?.name === activeFabric?.name &&
          item.lining === activeLining
        );

        if (existingIndex > -1) {
          const updated = [...prevCart];
          updated[existingIndex].quantity += 1;
          return updated;
        } else {
          return [...prevCart, {
            type: 'apparel',
            id: product.base_product_id,
            name: product.name,
            category: product.category,
            fabric: activeFabric,
            lining: activeLining,
            quantity: 1,
            price: "$1,499"
          }];
        }
      });
    } else if (type === 'fabric_only' && fabricData) {
      setCart(prevCart => {
        const existingIndex = prevCart.findIndex(item => item.type === 'fabric_only' && item.name === fabricData.name && item.length === customLength);
        if (existingIndex > -1) {
          const updated = [...prevCart];
          updated[existingIndex].quantity += 1;
          return updated;
        } else {
          return [...prevCart, {
            type: 'fabric_only',
            name: fabricData.name,
            length: customLength,
            parentCategory: fabricData.parentCategory,
            quantity: 1,
            price: `$${(customLength * 45).toFixed(2)}`
          }];
        }
      });
    }
    setIsCartOpen(true);
  };

  // POSTS STATED LAYOUT DIRECTLY INTO POSTGRES REPOSITORY ORDER TABLE
  const handleConfirmOrderSubmit = async () => {
    if (cart.length === 0) return;

    try {
      const response = await fetch('http://127.0.0.1:8000/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          items: cart
        })
      });

      if (!response.ok) throw new Error("Database transaction rejected.");

      const resData = await response.json();

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Splendid! I have officially processed your custom layouts. Your custom profile configurations are logged under Confirmation Token Reference: #ORDER-00${resData.order_id}. Our tailors have been notified!`
      }]);

      setCart([]);
      setIsCartOpen(false);
      alert(`🎉 Order Allocation Confirmed Successfully!\nSaved in PostgreSQL order table index token: #00${resData.order_id}`);
    } catch (err) {
      alert("Fulfillment Network Interruption: Could not save order payload sequence.");
    }
  };

  const handleRemoveFromCart = (index) => {
    setCart(prev => prev.filter((_, i) => i !== index));
  };

  const parseMatrix = (matrixData) => {
    if (!matrixData) return { fabrics: [], buttons: [], lining_options: [] };
    try {
      return typeof matrixData === 'string' ? JSON.parse(matrixData) : matrixData;
    } catch (e) {
      return { fabrics: [], buttons: [], lining_options: [] };
    }
  };

  // GLOBAL DYNAMIC APPAREL CRAWLER: Extracts and maps fabrics under EVERY single applicable style variant page
  const getGlobalFabricLibrary = () => {
    const uniqueFabrics = new Map();
    catalog.forEach(product => {
      const matrix = parseMatrix(product.customization_matrix);
      if (matrix && Array.isArray(matrix.fabrics)) {
        matrix.fabrics.forEach(fab => {
          if (!uniqueFabrics.has(fab.name)) {
            let contextLabel = "Premium Fabric Swatch Outfits";
            if (product.category.includes("Suits")) contextLabel = "Premium Suiting Options";
            if (product.category.includes("Gowns")) contextLabel = "Bridal & Evening Gown Outfits";
            if (product.category.includes("Sarees")) contextLabel = "Traditional Wedding & Festive Sarees";
            uniqueFabrics.set(fab.name, { ...fab, parentCategory: contextLabel, sampleProduct: product.name });
          }
        });
      }
    });
    return Array.from(uniqueFabrics.values());
  };

  // Filter Utilities logic pipelines
  const menuCategories = ['All', 'Bespoke Fabrics', 'Suits - Men', 'Suits - Women', 'Gowns', 'Sarees', 'Coats - Men', 'Coats - Women', 'Scarfs - Men', 'Scarfs - Women'];
  const visibleProducts = catalog.filter(p => {
    const matchesSearch = (p.name || '').toLowerCase().includes(searchQuery.toLowerCase()) || (p.category || '').toLowerCase().includes(searchQuery.toLowerCase());
    if (filteredCategory === 'All' || filteredCategory === 'Bespoke Fabrics') return matchesSearch;
    return p.category === filteredCategory && matchesSearch;
  });

  const selectedProduct = catalog.find(p => p.base_product_id === selectedProductId);
  const activeMatrix = selectedProduct ? parseMatrix(selectedProduct.customization_matrix) : null;

  const getImagePlaceholder = (name, category) => {
    const title = (name || '').toLowerCase();
    const cat = (category || '').toLowerCase();
    if (cat.includes('suit')) {
      return title.includes('women') || cat.includes('women')
        ? "https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&q=80&w=500"
        : "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&q=80&w=500";
    }
    if (cat.includes('gown')) return "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&q=80&w=500";
    if (cat.includes('saree')) return "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&q=80&w=500";
    return "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=500";
  };

  const totalCartItemsCount = cart.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <div className="showroom-workspace">

      {/* GLOBAL VIEWPORT: INDEPENDENT DIGITAL RETAIL WEBSITE STORE */}
      <div className="showroom-display-pane">
        <header className="showroom-navbar">
          <div className="logo" onClick={() => { setSelectedProductId(null); setFilteredCategory('All'); }}>
            ✨ MARCO BESPOKE CORE
          </div>

          <div className="search-bar-shell">
            <input
              type="text"
              placeholder="🔍 Search across 160 varieties of suits, traditional sarees, bridal gowns..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="cart-widget-trigger" onClick={() => setIsCartOpen(true)}>
            🛒 Open Order Bag ({totalCartItemsCount})
          </div>
        </header>

        <div className="showroom-filter-bar architecture-nav">
          {menuCategories.map(cat => (
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
            <div style={{ padding: '30px', background: '#2a1414', border: '1px solid #ef4444', borderRadius: '8px', color: '#fca5a5', textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '1.1rem' }}>⚠️ Showroom Connection Error</h4>
              <p style={{ fontSize: '0.9rem', lineHeight: '1.5', color: '#cbd5e1' }}>{backendError}</p>
              <button onClick={() => window.location.reload()} style={{ marginTop: '15px', background: '#ef4444', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', fontWeight: '700', cursor: 'pointer' }}>
                Retry Network Sync
              </button>
            </div>
          ) : selectedProduct ? (

            /* VIEW TIER A: LIVE CUSTOMIZABLE PRODUCT RUNTIME BLOCK */
            <div className="product-detail-page">
              <button className="back-btn" onClick={() => setSelectedProductId(null)}>← Return to Catalog Grid Floor</button>

              <div className="detail-layout">
                <img src={getImagePlaceholder(selectedProduct.name, selectedProduct.category)} alt={selectedProduct.name} className="detail-img" />
                <div className="detail-info">
                  <span className="cat-badge">{selectedProduct.category}</span>
                  <h2>{selectedProduct.name}</h2>
                  <p className="description-text">{selectedProduct.description}</p>

                  <div className="customization-status-card-box">
                    <h4>Current Order Profile Specifications:</h4>
                    <p>🧵 Foundation Fabric Selection: <strong style={{ color: '#3b82f6' }}>{activeFabric ? activeFabric.name : 'Unassigned foundation'}</strong></p>
                    <p>🛡️ Selected Inner Lining Shell: <strong style={{ color: '#10b981' }}>{activeLining || 'Standard Lining default'}</strong></p>
                  </div>

                  <div className="price-tag">Bespoke Design Fitting Tier Price</div>
                  <button className="add-to-cart-btn" onClick={() => handleAddToCart('apparel')}>
                    Add This Configured Cut To Bag
                  </button>
                </div>
              </div>

              <div className="fabric-catalog-showcase">
                <h3>🧵 Available Compatible Foundations for {selectedProduct.name}</h3>
                <p className="section-sub-intro">Select a material swatch below to dynamically alter this garment structure prior to ordering:</p>
                <div className="fabric-swatch-grid">
                  {activeMatrix && Array.isArray(activeMatrix.fabrics) && activeMatrix.fabrics.map((fabric, idx) => (
                    <div key={idx} className={`fabric-swatch-card ${activeFabric?.name === fabric.name ? 'selected-border' : ''}`}>
                      <div className="fabric-card-header">
                        <h4>{fabric.name}</h4>
                        <span className="weight-pill">{fabric.weight}</span>
                      </div>
                      <p className="fabric-stat"><strong>Texture profile:</strong> {fabric.texture}</p>
                      <button className="select-fabric-indicator-btn" onClick={() => setActiveFabric(fabric)}>
                        {activeFabric?.name === fabric.name ? '✓ Selected as Base' : 'Apply to This Silhouette'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="fabric-catalog-showcase" style={{ marginTop: '30px' }}>
                <h3>🛡️ Inner Haberdashery Lining Structural Options</h3>
                <div className="lining-selection-flex-row">
                  {activeMatrix && Array.isArray(activeMatrix.lining_options) && activeMatrix.lining_options.map((lining, idx) => (
                    <button
                      key={idx}
                      className={`lining-selection-pill-btn ${activeLining === lining ? 'active-lining' : ''}`}
                      onClick={() => setActiveLining(lining)}
                    >
                      {lining}
                    </button>
                  ))}
                </div>
              </div>

            </div>
          ) : filteredCategory === 'Bespoke Fabrics' ? (

            <div className="fabric-catalog-showcase" style={{ marginTop: 0 }}>
              <h3>🧵 Global Raw Bespoke Material Vault</h3>
              <p className="section-sub-intro">Order raw premium materials independently sorted by custom cut length requirements (Meters):</p>
              <div className="fabric-swatch-grid">
                {getGlobalFabricLibrary().map((fabric, idx) => (
                  <FabricLengthCard key={idx} fabric={fabric} onAddToBag={(length) => handleAddToCart('fabric_only', fabric, length)} />
                ))}
              </div>
            </div>

          ) : (

            <div className="catalog-grid-layout">
              {visibleProducts.map(product => (
                <div key={product.base_product_id} className="catalog-card" onClick={() => handleProductSelect(product.base_product_id)}>
                  <div className="img-wrapper"><img src={getImagePlaceholder(product.name, product.category)} alt={product.name} /></div>
                  <div className="card-meta">
                    <h3>{product.name}</h3>
                    <span className="category-subtext">{product.category}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT VIEWPORT: PERSISTENT COMPANION AI ADVISOR INTERFACE */}
      <div className="assistant-sidebar-pane">
        <div className="assistant-header">
          <div><h3>Marco</h3><small style={{ color: '#10b981', fontWeight: 700 }}>Personal Stylist Connoisseur</small></div>
          <span className="live-pulse">🟢 Online</span>
        </div>
        <div className="chat-message-stream">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              <div className="message-bubble"><p>{formatAndParseChatText(msg.content)}</p></div>
            </div>
          ))}
          {isLoading && <div className="message-row assistant"><div className="message-bubble typing-glow">Marco is syncing customization vectors...</div></div>}
          <div ref={chatEndRef} />
        </div>
        <form onSubmit={handleSendMessage} className="assistant-input-tray">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type a message to map designs systematically..." disabled={isLoading} />
          <button type="submit" disabled={isLoading}>Send</button>
        </form>
      </div>

      {/* TRANSACTION OVERLAY SLIDE OUT DRAWER MODAL CONTAINER */}
      {isCartOpen && (
        <div className="cart-slide-out-overlay-modal">
          <div className="cart-content-drawer">
            <div className="cart-drawer-header">
              <h3>Bespoke Order Bag Checkout Review</h3>
              <button className="close-cart-btn" onClick={() => setIsCartOpen(false)}>✕ Close</button>
            </div>

            <div className="cart-items-wrapper-list">
              {cart.length === 0 ? (
                <p style={{ color: '#666', padding: '40px 0', textAlign: 'center' }}>Your bespoke order container bag is completely empty.</p>
              ) : (
                <>
                  {cart.map((item, idx) => (
                    <div key={idx} className="cart-transaction-row-card">
                      <div style={{ textAlign: 'left' }}>
                        {item.type === 'apparel' ? (
                          <>
                            <h4>{item.name} <span className="qty-tag">x{item.quantity}</span></h4>
                            <span className="category-subtext" style={{ fontSize: '0.75rem' }}>{item.category}</span>
                            <p className="cart-spec-note">🧵 Base Thread: <span>{item.fabric?.name}</span></p>
                            <p className="cart-spec-note">🛡️ Inner Lining Shell: <span>{item.lining}</span></p>
                          </>
                        ) : (
                          <>
                            <h4>{item.name} <span className="qty-tag">x{item.quantity}</span></h4>
                            <span className="category-subtext" style={{ fontSize: '0.75rem', color: '#10b981' }}>Independent Material Cut</span>
                            <p className="cart-spec-note">📏 Linear Length: <span>{item.length} Meters</span></p>
                          </>
                        )}
                      </div>
                      <div className="cart-card-right-actions">
                        <div className="cart-item-price">{item.price}</div>
                        <button className="cart-remove-item-action-btn" onClick={() => handleRemoveFromCart(idx)}>Delete Cut</button>
                      </div>
                    </div>
                  ))}

                  <div style={{ marginTop: '30px', borderTop: '1px solid #262626', paddingTop: '20px' }}>
                    <button
                      className="add-to-cart-btn"
                      style={{ maxWidth: '100%', width: '100%', background: '#10b981' }}
                      onClick={handleConfirmOrderSubmit}
                    >
                      Confirm Order Allocation & Archive to DB
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

// Sub-component card configuration layout helper to isolate independent numeric input state changes
function FabricLengthCard({ fabric, onAddToBag }) {
  const [length, setLength] = useState(3);
  return (
    <div className="fabric-swatch-card" style={{ minHeight: '230px' }}>
      <div className="fabric-card-header">
        <div>
          <h4>{fabric.name}</h4>
          <small style={{ color: '#3b82f6', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginTop: '4px' }}>{fabric.parentCategory}</small>
        </div>
        <span className="weight-pill">{fabric.weight}</span>
      </div>
      <p className="fabric-stat" style={{ marginTop: '10px' }}><strong>Weave Texture:</strong> {fabric.texture}</p>

      <div className="fabric-purchase-length-input-control-row">
        <label>Required Cut Length:</label>
        <div className="input-stepper-flex">
          <input type="number" min="1" max="50" value={length} onChange={(e) => setLength(Math.max(1, parseInt(e.target.value) || 1))} />
          <span>Meters</span>
        </div>
      </div>

      <button className="select-fabric-indicator-btn active-buy-btn" onClick={() => onAddToBag(length)}>
        Purchase Fabric Segment (${(length * 45).toFixed(2)})
      </button>
    </div>
  );
}

export default App;