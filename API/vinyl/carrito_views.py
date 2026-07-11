from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from .models import Album, CarritoItem
from .serializers import CarritoItemSerializer

class CarritoAlbumView(APIView):
    permission_classes = [AllowAny]
    
    def get_session_id(self, request):
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        return session_id

    def put(self, request, album_id):
        session_id = self.get_session_id(request)
        nueva_cantidad = request.data.get('cantidad')
        
        try:
            album = Album.objects.get(id=album_id)
            item, created = CarritoItem.objects.get_or_create(
                session_id=session_id,
                album=album,
                defaults={'cantidad': nueva_cantidad}
            )
            
            if not created:
                item.cantidad = nueva_cantidad
                item.save()
            
            serializer = CarritoItemSerializer(item)
            return Response(serializer.data)
        except Album.DoesNotExist:
            return Response({'error': 'Album not found'}, status=404)

    def delete(self, request, album_id):
        session_id = self.get_session_id(request)
        
        deleted_count = CarritoItem.objects.filter(
            session_id=session_id, 
            album__id=album_id
        ).delete()[0]
        
        return Response({'message': f'{deleted_count} items removed'}, status=200)