import React, { useState, useEffect, useRef } from 'react';
import { useProductos, usePrefetch } from '../hooks/useProductos';
import { useAgregarAlCarrito } from '../hooks/useCarrito';
import { useUserProfile } from '../hooks/useAuth';
import './Home.css';

const DURACION_PREVIEW_MS = 28000; // ~28s: most preview_urls are full songs

const PLACEHOLDER_COVER = `data:image/svg+xml,${encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120"><rect width="120" height="120" fill="#e2e8f0"/><text x="60" y="70" font-size="44" text-anchor="middle" fill="#94a3b8">🎵</text></svg>'
)}`;

const Home = ({ onVerDetalle }) => {
  const [busqueda, setBusqueda] = useState('');
  const [filtroGenero, setFiltroGenero] = useState('');
  const [precioMin, setPrecioMin] = useState('');
  const [precioMax, setPrecioMax] = useState('');
  const [reproduciendo, setReproduciendo] = useState(null);
  const audioRef = useRef(null);
  const previewTimeoutRef = useRef(null);

  const { data: productos, isLoading, error } = useProductos();
  const { prefetchProducto } = usePrefetch();
  const agregarAlCarritoMutation = useAgregarAlCarrito();
  const { data: userProfile } = useUserProfile();

  const detenerPreview = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (previewTimeoutRef.current) {
      clearTimeout(previewTimeoutRef.current);
      previewTimeoutRef.current = null;
    }
    setReproduciendo(null);
  };

  const togglePreview = (producto, cardKey) => {
    if (!producto.preview_url) return;

    if (reproduciendo === cardKey) {
      detenerPreview();
      return;
    }

    detenerPreview();

    const audio = new Audio(producto.preview_url);
    audio.addEventListener('ended', detenerPreview);
    audio.play().catch(detenerPreview);

    audioRef.current = audio;
    previewTimeoutRef.current = setTimeout(detenerPreview, DURACION_PREVIEW_MS);
    setReproduciendo(cardKey);
  };

  useEffect(() => {
    return () => detenerPreview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // تابع اعمال فیلترها (جستجو)
  const aplicarFiltros = () => {
    // این تابع از فیلترهای موجود استفاده می‌کند
    // فعلاً نیازی به پیاده‌سازی جداگانه نیست چون filtrarProductos کار می‌کند
    console.log('Filtros aplicados');
  };

  const limpiarFiltros = () => {
    setBusqueda('');
    setFiltroGenero('');
    setPrecioMin('');
    setPrecioMax('');
  };

  const handleMouseEnter = (productoId) => {
    prefetchProducto(productoId);
  };

  const handleAgregarCarrito = (producto) => {
    agregarAlCarritoMutation.mutate({
      album_id: producto.id,
      cantidad: 1
    });
  };

  const filtrarProductos = () => {
    if (!productos) return [];
    
    let filtrados = productos;

    
    

    // فیلتر بر اساس جستجو
    if (busqueda) {
      filtrados = filtrados.filter(p => 
        p.title.toLowerCase().includes(busqueda.toLowerCase()) ||
        p.artist.toLowerCase().includes(busqueda.toLowerCase())
      );
    }

    // فیلتر بر اساس ژانر
    if (filtroGenero) {
      filtrados = filtrados.filter(p => p.genre === filtroGenero);
    }

    // فیلتر بر اساس حداقل قیمت
    if (precioMin) {
      filtrados = filtrados.filter(p => p.precio >= parseFloat(precioMin));
    }

    // فیلتر بر اساس حداکثر قیمت
    if (precioMax) {
      filtrados = filtrados.filter(p => p.precio <= parseFloat(precioMax));
    }

    return filtrados;
  };

  const obtenerPrecio = (producto) => {
    const esVIP = userProfile?.es_vip;
    const descuentoRock = producto.genre === 'Rock' ? 0.2 : 0;
    const descuentoVIP = esVIP ? 0.3 : 0;
    const descuentoTotal = Math.max(descuentoRock, descuentoVIP);
    return (producto.precio * (1 - descuentoTotal)).toFixed(2);
  };

  const obtenerDescuento = (producto) => {
    const esVIP = userProfile?.es_vip;
    if (esVIP) return { texto: '✨ 30% OFF VIP', clase: 'vip' };
    if (producto.genre === 'Rock') return { texto: '20% OFF', clase: '' };
    return null;
  };

  const obtenerRecomendados = (productos) => {
    return productos
      .filter(p => p.rating >= 8)
      .slice(0, 3);
  };

  if (isLoading) return <div className="loading">Loading products...</div>;
  if (error) return <div className="error">Error: {error.message}</div>;

  const productosFiltrados = filtrarProductos();
  const recomendados = obtenerRecomendados(productosFiltrados);
  const generos = [...new Set(productos?.map(p => p.genre) || [])];

  const esVIP = userProfile?.es_vip;
  const promociones = [
    { id: 1, texto: '🎵 20% OFF on Rock albums!', activa: !esVIP },
    { id: 2, texto: '✨ 30% OFF on EVERYTHING for VIP members!', activa: esVIP },
    { id: 3, texto: '🔥 Free shipping on orders over $50', activa: true }
  ];

  return (
    <div className="home">
      {/* Banner de promociones */}
      <div className="promociones-banner">
        {promociones.filter(p => p.activa).map(promo => (
          <div key={promo.id} className="promocion">{promo.texto}</div>
        ))}
      </div>

      <h1>Music Store</h1>

      {/* Advanced search and filter controls */}
      <div className="advanced-search">
        <div className="search-row">
          <input
            type="text"
            placeholder="🔍 Search by title or artist..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filters-row">
          <select
            value={filtroGenero}
            onChange={(e) => setFiltroGenero(e.target.value)}
            className="filter-select"
          >
            <option value="">🎵 All genres</option>
            {generos.map(genero => (
              <option key={genero} value={genero}>{genero}</option>
            ))}
          </select>

          <div className="price-filters">
            <input
              type="number"
              placeholder="💰 Minimum price"
              value={precioMin}
              onChange={(e) => setPrecioMin(e.target.value)}
              className="price-input"
            />
            <span className="price-separator">-</span>
            <input
              type="number"
              placeholder="💰 Maximum price"
              value={precioMax}
              onChange={(e) => setPrecioMax(e.target.value)}
              className="price-input"
            />
          </div>
        </div>

        <div className="search-buttons">
          <button onClick={aplicarFiltros} className="search-btn">
            🔍 Search
          </button>
          <button onClick={limpiarFiltros} className="reset-btn">
            🗑️ Clear filters
          </button>
        </div>
      </div>

      {/* Recommended products */}
      {recomendados.length > 0 && (
        <div className="recomendados">
          <h2>🌟 Recommended for you</h2>
          <div className="productos-grid">
            {recomendados.map(producto => (
              <div 
                key={`rec-${producto.id}`} 
                className="producto-card recomendado"
                onMouseEnter={() => handleMouseEnter(producto.id)}
              >
                <div className="badge-recomendado">⭐ TOP</div>
                {producto.preview_url && (
                  <button
                    onClick={() => togglePreview(producto, `rec-${producto.id}`)}
                    className="btn-preview"
                    aria-label={reproduciendo === `rec-${producto.id}` ? 'Pausar preview' : 'Reproducir preview'}
                  >
                    {reproduciendo === `rec-${producto.id}` ? '⏸️' : '▶️'}
                  </button>
                )}
                <img
                  src={producto.cover_image || PLACEHOLDER_COVER}
                  alt={producto.title}
                  className="producto-cover"
                  onError={(e) => { e.target.onerror = null; e.target.src = PLACEHOLDER_COVER; }}
                />
                <h3>{producto.title}</h3>
                <p><strong>Artist:</strong> {producto.artist}</p>
                <p><strong>Genre:</strong> {producto.genre}</p>
                <p><strong>Rating:</strong> {producto.rating}/10</p>
                <p className="precio">${obtenerPrecio(producto)}</p>
                {obtenerDescuento(producto) && (
                  <span className={`descuento ${obtenerDescuento(producto).clase}`}>
                    {obtenerDescuento(producto).texto}
                  </span>
                )}
                <div className="producto-actions">
                  <button
                    onClick={() => onVerDetalle(producto.id)}
                    className="btn-detalle"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => handleAgregarCarrito(producto)}
                    className="btn-carrito"
                    disabled={producto.stock === 0 || agregarAlCarritoMutation.isPending}
                  >
                    {agregarAlCarritoMutation.isPending ? 'Adding...' : 'Add to Cart'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Todos los productos */}
      <div className="todos-productos">
        <h2>All Products ({productosFiltrados.length})</h2>
        <div className="productos-grid">
          {productosFiltrados.map(producto => (
            <div
              key={producto.id}
              className="producto-card"
              onMouseEnter={() => handleMouseEnter(producto.id)}
            >
              {producto.preview_url && (
                <button
                  onClick={() => togglePreview(producto, producto.id)}
                  className="btn-preview"
                  aria-label={reproduciendo === producto.id ? 'Pausar preview' : 'Reproducir preview'}
                >
                  {reproduciendo === producto.id ? '⏸️' : '▶️'}
                </button>
              )}
              <img
                src={producto.cover_image || PLACEHOLDER_COVER}
                alt={producto.title}
                className="producto-cover"
                onError={(e) => { e.target.onerror = null; e.target.src = PLACEHOLDER_COVER; }}
              />
              <h3>{producto.title}</h3>
              <p><strong>Artist:</strong> {producto.artist}</p>
              <p><strong>Genre:</strong> {producto.genre}</p>
              <p><strong>Rating:</strong> {producto.rating}/10</p>
              <p className="precio">${obtenerPrecio(producto)}</p>
              {obtenerDescuento(producto) && (
                <span className={`descuento ${obtenerDescuento(producto).clase}`}>
                  {obtenerDescuento(producto).texto}
                </span>
              )}
              <div className="producto-actions">
                <button 
                  onClick={() => onVerDetalle(producto.id)} 
                  className="btn-detalle"
                >
                  View Details
                </button>
                <button
                  onClick={() => handleAgregarCarrito(producto)}
                  className="btn-carrito"
                  disabled={producto.stock === 0 || agregarAlCarritoMutation.isPending}
                >
                  {agregarAlCarritoMutation.isPending ? 'Adding...' : 'Add to Cart'}
                </button>
              </div>
              {producto.stock === 0 && (
                <div className="sin-stock">Out of Stock</div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {agregarAlCarritoMutation.error && (
        <div className="error-message">
          {agregarAlCarritoMutation.error.message}
        </div>
      )}
    </div>
  );
};

export default Home;