import React, { useState } from 'react';
import { useCarrito } from '../hooks/useCarrito';
import { procesarPago } from '../services/api';
import { useQueryClient } from '@tanstack/react-query';
import './Checkout.css';

const Checkout = ({ onVolver, onExito }) => {
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('card');
  const queryClient = useQueryClient();
  
  const { data: carrito } = useCarrito();

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    setProcessing(true);
    setError(null);

    try {
      // Simular procesamiento de pago
      const mockPaymentId = `payment_${Date.now()}`;
      
      // Procesar pago en el backend
      await procesarPago(mockPaymentId);
      
      // Limpiar carrito y actualizar queries
      queryClient.setQueryData(['carrito'], {
        items: [],
        total: 0,
        cantidad_total: 0
      });
      queryClient.invalidateQueries({ queryKey: ['carrito'] });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      queryClient.invalidateQueries({ queryKey: ['historial'] });
      
      onExito();
      
    } catch (err) {
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="checkout-container">
      <button onClick={onVolver} className="btn-volver">
        ← Back to Cart
      </button>

      <div className="checkout-form">
        <h1>💳 Process Payment</h1>

        <div className="order-summary">
          <h3>Order Summary</h3>
          {carrito?.items?.map(item => (
            <div key={item.id} className="order-item">
              <span>{item.cantidad}x {item.album.title}</span>
              <span>${item.subtotal}</span>
            </div>
          ))}
          <div className="order-total">
            <strong>Total: ${carrito?.total || 0}</strong>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="payment-section">
            <h3>Payment Method</h3>

            <div className="payment-options">
              <label className="payment-option">
                <input
                  type="radio"
                  name="payment"
                  value="card"
                  checked={paymentMethod === 'card'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                />
                💳 Credit/Debit Card
              </label>

              <label className="payment-option">
                <input
                  type="radio"
                  name="payment"
                  value="paypal"
                  checked={paymentMethod === 'paypal'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                />
                🅿️ PayPal
              </label>

              <label className="payment-option">
                <input
                  type="radio"
                  name="payment"
                  value="google"
                  checked={paymentMethod === 'google'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                />
                🔵 Google Pay
              </label>
            </div>

            {paymentMethod === 'card' && (
              <div className="card-form">
                <input type="text" placeholder="Card number" required />
                <div className="card-row">
                  <input type="text" placeholder="MM/YY" required />
                  <input type="text" placeholder="CVV" required />
                </div>
                <input type="text" placeholder="Cardholder name" required />
              </div>
            )}
          </div>

          <button
            type="submit"
            className="btn-pay"
            disabled={processing || !carrito?.items?.length}
          >
            {processing ? 'Processing...' : `Pay $${carrito?.total || 0}`}
          </button>
        </form>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="payment-methods">
          <p>Accepted payment methods:</p>
          <div className="payment-icons">
            💳 Card • 🅿️ PayPal • 🔵 Google Pay
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;