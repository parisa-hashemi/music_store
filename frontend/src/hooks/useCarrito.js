import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchCarrito, agregarAlCarrito, actualizarCantidadCarrito, eliminarDelCarrito, procesarCompra } from '../services/api';

export const useCarrito = () => {
  return useQuery({
    queryKey: ['carrito'],
    queryFn: fetchCarrito,
    staleTime: 0,
  });
};

export const useAgregarAlCarrito = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: agregarAlCarrito,
    // به جای optimistic update، فقط بعد از موفقیت invalidate کن
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['carrito'] });
    },
    onError: (error) => {
      console.error('Error adding to cart:', error);
    },
  });
};

export const useActualizarCantidad = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: actualizarCantidadCarrito,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['carrito'] });
    },
  });
};

export const useEliminarDelCarrito = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: eliminarDelCarrito,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['carrito'] });
    },
  });
};

export const useProcesarCompra = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: procesarCompra,
    onSuccess: () => {
      queryClient.setQueryData(['carrito'], {
        items: [],
        total: 0,
        cantidad_total: 0
      });
      queryClient.invalidateQueries({ queryKey: ['productos'] });
      queryClient.invalidateQueries({ queryKey: ['carrito'] });
    },
  });
};