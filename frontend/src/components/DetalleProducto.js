import React,{useState} from 'react';
import { useProducto } from '../hooks/useProductos';
import { useAgregarAlCarrito } from '../hooks/useCarrito';
import { useUserProfile } from '../hooks/useAuth';
import './DetalleProducto.css';
import Comments from './Comments';
import Rating from './Rating';

const PLACEHOLDER_COVER = `data:image/svg+xml,${encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120"><rect width="120" height="120" fill="#e2e8f0"/><text x="60" y="70" font-size="44" text-anchor="middle" fill="#94a3b8">🎵</text></svg>'
)}`;

const DetalleProducto = ({ productoId, onVolver }) => {
  // console.log(",ugtfktdjrsshsh",productoId)
  const { data: producto, isLoading, error } = useProducto(productoId);
  const agregarAlCarritoMutation = useAgregarAlCarrito();
  const { data: userProfile } = useUserProfile();
  const [avgRating, setAvgRating] = useState(producto?.average_rating || 0);

  const handleAgregarCarrito = () => {
    agregarAlCarritoMutation.mutate({
      album_id: producto.id,
      cantidad: 1
    });
  };

  if (isLoading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error.message}</div>;
  if (!producto) return <div className="error">Product not found</div>;

  const esVIP = userProfile?.es_vip;
  const descuentoRock = producto.genre === 'Rock' ? 0.2 : 0;
  const descuentoVIP = esVIP ? 0.3 : 0;
  const descuentoTotal = Math.max(descuentoRock, descuentoVIP);
  const precioFinal = (producto.precio * (1 - descuentoTotal)).toFixed(2);

  return (
    <div className="detalle-producto">
      <button onClick={onVolver} className="btn-volver">
        ← Back
      </button>

      <div className="producto-detalle">
        <img
          src={producto.cover_image || PLACEHOLDER_COVER}
          alt={producto.title}
          className="producto-cover-detalle"
          onError={(e) => { e.target.onerror = null; e.target.src = PLACEHOLDER_COVER; }}
        />
        <h1>{producto.title}</h1>
        <div className="producto-info">
          <p><strong>Artist:</strong> {producto.artist}</p>
          <p><strong>Genre:</strong> {producto.genre}</p>
          <p><strong>Rating:</strong> {producto.rating}/10</p>
          <p><strong>Release Date:</strong> {producto.release_date}</p>
          <p><strong>Stock available:</strong> {producto.stock}</p>
          <p className="precio-detalle">
            <strong>Price:</strong>
            {descuentoTotal > 0 && (
              <span className="precio-original">${producto.precio}</span>
            )}
            ${precioFinal}
            {esVIP && (
              <span className="descuento-detalle vip">✨ 30% OFF VIP</span>
            )}
            {!esVIP && producto.genre === 'Rock' && (
              <span className="descuento-detalle">20% OFF</span>
            )}
          </p>
        </div>

        <div className="producto-acciones">
          <button
            onClick={handleAgregarCarrito}
            className="btn-agregar-carrito"
            disabled={producto.stock === 0 || agregarAlCarritoMutation.isPending}
          >
            {agregarAlCarritoMutation.isPending
              ? 'Adding to Cart...'
              : producto.stock === 0
                ? 'Out of Stock'
                : 'Add to Cart'
            }
          </button>
        </div>

        {agregarAlCarritoMutation.error && (
          <div className="error-message">
            {agregarAlCarritoMutation.error.message}
          </div>
        )}


        {agregarAlCarritoMutation.isSuccess && (
          <div className="success-message">
            Product added to cart successfully!
          </div>
        )}
      </div>

       <div className="rating-wrapper">
      <Rating 
       albumId={producto.id} 
        initialRating={producto.average_rating || 0}
       onRatingChange={(newRating) => {
      setAvgRating(newRating);
       }}
      />
       </div>
      {/* {console.log("Rendering Comments with albumId:", producto.id)}
      <Comments albumId={producto.id} /> */}
      <Comments albumId={producto.id} />
    </div>
  );
};

export default DetalleProducto;