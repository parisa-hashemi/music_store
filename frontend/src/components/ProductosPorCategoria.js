import React from 'react';
import { useProductos, usePrefetch } from '../hooks/useProductos';
import { useAgregarAlCarrito } from '../hooks/useCarrito';
import './ProductosPorCategoria.css';

const PLACEHOLDER_COVER = `data:image/svg+xml,${encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120"><rect width="120" height="120" fill="#e2e8f0"/><text x="60" y="70" font-size="44" text-anchor="middle" fill="#94a3b8">🎵</text></svg>'
)}`;

const ProductosPorCategoria = ({ categoriaId, categoriaNombre, onVerDetalle, onVolver }) => {
  const { data: productos, isLoading, error } = useProductos(categoriaId);
  const { prefetchProducto } = usePrefetch();
  const agregarAlCarritoMutation = useAgregarAlCarrito();

  const handleMouseEnter = (productoId) => {
    prefetchProducto(productoId);
  };

  const handleAgregarCarrito = (producto) => {
    agregarAlCarritoMutation.mutate({
      album_id: producto.id,
      cantidad: 1
    });
  };

  if (isLoading) return <div className="loading">Loading products...</div>;
  if (error) return <div className="error">Error: {error.message}</div>;

  return (
    <div className="productos-categoria">
      <button onClick={onVolver} className="btn-volver">
        ← Back to Categories
      </button>

      <h1>🎵 {categoriaNombre}</h1>
      <p className="categoria-info">{productos?.length || 0} products found</p>

      {productos?.length === 0 ? (
        <div className="sin-productos">
          <p>There are no products in this category</p>
        </div>
      ) : (
        <div className="productos-grid">
          {productos?.map(producto => (
            <div
              key={producto.id}
              className="producto-card"
              onMouseEnter={() => handleMouseEnter(producto.id)}
            >
              <img
                src={producto.cover_image || PLACEHOLDER_COVER}
                alt={producto.title}
                className="producto-cover"
                onError={(e) => { e.target.onerror = null; e.target.src = PLACEHOLDER_COVER; }}
              />
              <h3>{producto.title}</h3>
              <p><strong>Artist:</strong> {producto.artist}</p>
              <p><strong>Genre:</strong> {producto.genre}</p>
              <p><strong>Rating:</strong> {producto.rating}/5</p>
              <p className="precio">${producto.precio}</p>
              <p className="stock">Stock: {producto.stock}</p>

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
      )}
    </div>
  );
};

export default ProductosPorCategoria;