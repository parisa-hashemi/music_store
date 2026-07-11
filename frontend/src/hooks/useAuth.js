import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { registrarUsuario, loginUsuario, logoutUsuario, fetchHistorialCompras } from '../services/api';

export const useRegistro = () => {
  return useMutation({
    mutationFn: registrarUsuario,
  });
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: loginUsuario,
    onSuccess: (data) => {
      // Guardar usuario en localStorage
      localStorage.setItem('user', JSON.stringify(data.user));
      // Invalidar queries para actualizar estado
      queryClient.invalidateQueries({ queryKey: ['carrito'] });
      queryClient.invalidateQueries({ queryKey: ['historial'] });
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async () => {
      // Intentar logout en backend, pero no fallar si hay error
      try {
        await logoutUsuario();
      } catch (error) {
        console.log('Error en logout backend:', error);
      }
      return true;
    },
    onSuccess: () => {
      // Limpiar localStorage
      localStorage.removeItem('user');
      // Clear the cart specifically
      queryClient.setQueryData(['carrito'], {
        items: [],
        total: 0,
        cantidad_total: 0
      });
      // Limpiar todas las queries
      queryClient.clear();
      // Reload the page to reset state
      window.location.reload();
    },
  });
};

export const useHistorialCompras = () => {
  return useQuery({
    queryKey: ['historial'],
    queryFn: fetchHistorialCompras,
    enabled: !!getCurrentUser(),
  });
};

export const getCurrentUser = () => {
  try {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
};

export const useUserProfile = () => {
  return useQuery({
    queryKey: ['userProfile'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/user/profile/', {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Error fetching profile');
      return response.json();
    },
    enabled: !!getCurrentUser(),
  });
};

export const isAuthenticated = () => {
  return !!getCurrentUser();
};