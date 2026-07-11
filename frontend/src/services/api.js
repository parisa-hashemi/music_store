const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api`;

// Productos
export const fetchProductos = async (categoriaId = null) => {
  const url = categoriaId
    ? `${API_BASE}/albums/?categoria=${categoriaId}`
    : `${API_BASE}/albums/`;
  const response = await fetch(url);
  if (!response.ok) throw new Error('Error loading products');
  return response.json();
};

export const fetchProducto = async (id) => {
  const response = await fetch(`${API_BASE}/albums/${id}/`);
  if (!response.ok) throw new Error('Error loading product');
  return response.json();
};

// Categories
export const fetchCategorias = async () => {
  const response = await fetch(`${API_BASE}/categorias/`);
  if (!response.ok) throw new Error('Error loading categories');
  return response.json();
};

// Cart
export const fetchCarrito = async () => {
  const response = await fetch(`${API_BASE}/carrito/`, {
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Error loading cart');
  return response.json();
};

export const agregarAlCarrito = async ({ album_id, cantidad = 1 }) => {
  const response = await fetch(`${API_BASE}/carrito/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ album_id, cantidad }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Error adding to cart');
  }
  return response.json();
};

export const actualizarCantidadCarrito = async ({ id, cantidad }) => {
  const response = await fetch(`${API_BASE}/carrito/${id}/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ cantidad }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Error updating quantity');
  }
  return response.json();
};

export const eliminarDelCarrito = async (id) => {
  const response = await fetch(`${API_BASE}/carrito/${id}/`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Error removing from cart');
  return true;
};

export const procesarCompra = async () => {
  const response = await fetch(`${API_BASE}/carrito/`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Error processing purchase');
  }
  return response.json();
};

// Authentication
export const registrarUsuario = async (userData) => {
  const response = await fetch(`${API_BASE}/auth/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(userData),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(Object.values(error).flat().join(', '));
  }
  return response.json();
};

export const loginUsuario = async (credentials) => {
  const response = await fetch(`${API_BASE}/auth/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(credentials),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(Object.values(error).flat().join(', '));
  }
  return response.json();
};

export const logoutUsuario = async () => {
  const response = await fetch(`${API_BASE}/auth/logout/`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Error logging out');
  return response.json();
};

export const fetchHistorialCompras = async () => {
  const response = await fetch(`${API_BASE}/historial/`, {
    credentials: 'include'
  });
  if (!response.ok) throw new Error('Error loading history');
  return response.json();
};

export const procesarPago = async (stripePaymentId) => {
  const response = await fetch(`${API_BASE}/checkout/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ stripe_payment_id: stripePaymentId }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Error processing payment');
  }
  return response.json();
};