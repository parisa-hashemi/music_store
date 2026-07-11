import React from 'react';
import { useCarrito, useActualizarCantidad, useEliminarDelCarrito, useProcesarCompra } from '../hooks/useCarrito';
import './Carrito.css';

const Carrito = ({ onVolver, onCheckout }) => {
  const { data: carrito, isLoading, error } = useCarrito();
  const actualizarCantidadMutation = useActualizarCantidad();
  const eliminarDelCarritoMutation = useEliminarDelCarrito();
  const procesarCompraMutation = useProcesarCompra();

  const handleActualizarCantidad = (item, nuevaCantidad) => {
    if (nuevaCantidad <= 0) return;
    
    actualizarCantidadMutation.mutate({
      id: item.id,
      cantidad: nuevaCantidad
    });
  };

  const handleEliminar = (item) => {
    eliminarDelCarritoMutation.mutate(item.id);
  };

  const handleProcesarCompra = () => {
    if (window.confirm('Confirm purchase? This will reduce the stock of the products.')) {
      procesarCompraMutation.mutate();
    }
  };

  if (isLoading) return <div className="loading">Loading cart...</div>;
  if (error) return <div className="error">Error: {error.message}</div>;

  const items = carrito?.items || [];
  const total = carrito?.total || 0;

  return (
    <div className="carrito">
      <button type="button" onClick={onVolver} className="btn-volver">
        ← Back
      </button>
      
      <h1>🛒 Shopping Cart</h1>

      {items.length === 0 ? (
        <div className="carrito-vacio">
          <p>Your cart is empty</p>
          <button type="button" onClick={onVolver} className="btn-seguir-comprando">
            Keep Shopping
          </button>
        </div>
      ) : (
        <div>
          <div className="carrito-items">
            {items.map(item => (
              <div key={item.id} className="carrito-item">
                <div className="item-info">
                  <h3>{item.album.title}</h3>
                  <p>{item.album.artist}</p>
                  <p className="precio">
                    {item.album.precio_original && item.album.precio !== item.album.precio_original && (
                      <span className="precio-original">${item.album.precio_original}</span>
                    )}
                    ${item.album.precio}
                  </p>
                </div>
                
                <div className="item-controles">
                  <button 
                    type="button"
                    onClick={() => handleActualizarCantidad(item, item.cantidad - 1)}
                    disabled={item.cantidad <= 1 || actualizarCantidadMutation.isPending}
                    className="btn-cantidad"
                  >
                    -
                  </button>
                  <span className="cantidad">{item.cantidad}</span>
                  <button 
                    type="button"
                    onClick={() => handleActualizarCantidad(item, item.cantidad + 1)}
                    disabled={actualizarCantidadMutation.isPending}
                    className="btn-cantidad"
                  >
                    +
                  </button>
                  <button 
                    type="button"
                    onClick={() => handleEliminar(item)}
                    disabled={eliminarDelCarritoMutation.isPending}
                    className="btn-eliminar"
                  >
                    {eliminarDelCarritoMutation.isPending ? 'Removing...' : 'Remove'}
                  </button>
                </div>
                
                <div className="item-subtotal">
                  <strong>${item.subtotal}</strong>
                </div>
              </div>
            ))}
          </div>
          
          {(actualizarCantidadMutation.error || eliminarDelCarritoMutation.error || procesarCompraMutation.error) && (
            <div className="error-message">
              {actualizarCantidadMutation.error?.message || eliminarDelCarritoMutation.error?.message || procesarCompraMutation.error?.message}
            </div>
          )}
          
          {procesarCompraMutation.isSuccess && (
            <div className="success-message">
              Purchase processed successfully! Stock has been updated.
            </div>
          )}

          <div className="carrito-total">
            <h2>Total: ${total}</h2>
            <button
              type="button"
              className="btn-comprar"
              onClick={onCheckout}
              disabled={items.length === 0}
            >
              Proceed to Payment
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Carrito;