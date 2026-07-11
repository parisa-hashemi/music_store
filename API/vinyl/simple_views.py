from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from decimal import Decimal
from .models import Album, Categoria, CarritoItem, Usuario

class SimpleCarritoView(APIView):
    permission_classes = [AllowAny]
    
    def get_session_id(self, request):
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        return session_id
    
    def get(self, request):
        session_id = self.get_session_id(request)
        items = CarritoItem.objects.filter(session_id=session_id)
        
        es_vip = False
        if request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(username=request.user.username)
                es_vip = usuario.VIP
            except Usuario.DoesNotExist:
                pass
        
        items_data = []
        total = Decimal('0')
        
        for item in items:
            precio = item.album.precio  # Decimal
            
            if es_vip:
                precio = precio * Decimal('0.7')
            elif item.album.genre == 'Rock':
                precio = precio * Decimal('0.8')
            
            subtotal = precio * item.cantidad  # int × Decimal → OK
            
            items_data.append({
                'id': item.id,
                'album': {
                    'id': item.album.id,
                    'title': item.album.title,
                    'artist': item.album.artist,
                    'precio': float(precio),
                    'precio_original': float(item.album.precio)
                },
                'cantidad': item.cantidad,
                'subtotal': float(subtotal)
            })
            
            total += subtotal
        
        return Response({
            'items': items_data,
            'total': float(total),
            'cantidad_total': sum(i.cantidad for i in items)
        })
    
    def post(self, request):
        session_id = self.get_session_id(request)
        album_id = request.data.get('album_id')
        cantidad = int(request.data.get('cantidad', 1))  # ← IMPORTANTE
        
        try:
            album = Album.objects.get(id=album_id)
        except Album.DoesNotExist:
            return Response({'error': 'Album not found'}, status=404)

        if cantidad > album.stock:
            return Response({'error': f'Insufficient stock. Available: {album.stock}'}, status=400)

        item, created = CarritoItem.objects.get_or_create(
            session_id=session_id,
            album=album,
            defaults={'cantidad': cantidad}
        )

        if not created:
            nueva_cantidad = item.cantidad + cantidad
            if nueva_cantidad > album.stock:
                return Response({'error': f'Insufficient stock. Available: {album.stock}'}, status=400)
            item.cantidad = nueva_cantidad
            item.save()

        return Response({'message': 'Product added to cart'}, status=201)