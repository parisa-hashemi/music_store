# vinyl/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.db import transaction
from django.db.models import Q


from .models import Album, Categoria, CarritoItem, Compra, CompraItem
from .serializers import *

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Album, Comment
from .serializers import CommentSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import models
from .models import Rating



@api_view(['GET'])
def user_stats(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=401)
    
    compras = Compra.objects.filter(usuario=request.user)
    total_orders = compras.count()
    total_spent = sum(compra.total for compra in compras)
    avg_order = total_spent / total_orders if total_orders > 0 else 0
    
    return Response({
        'total_orders': total_orders,
        'total_spent': float(total_spent),
        'avg_order': round(avg_order, 2)
    })

@api_view(['GET', 'PUT'])
def user_profile(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=401)
    
    if request.method == 'GET':
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'es_vip': getattr(request.user, 'vip', False)
        })
    
    elif request.method == 'PUT':
        data = request.data
        if 'username' in data:
            request.user.username = data['username']
        if 'email' in data:
            request.user.email = data['email']
        request.user.save()
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'es_vip': getattr(request.user, 'vip', False)
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_album(request, album_id):
    try:
        album = Album.objects.get(id=album_id)
        score = request.data.get('score')

        try:
            score = int(score)
        except (TypeError, ValueError):
            return Response({'error': 'The score must be an integer between 1 and 5'}, status=400)

        if score < 1 or score > 5:
            return Response({'error': 'The score must be between 1 and 5'}, status=400)

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            album=album,
            defaults={'score': score}
        )


        avg = album.ratings.aggregate(models.Avg('score'))['score__avg']
        album.average_rating = avg or 0
        album.save()

        return Response({
            'status': 'ok',
            'average_rating': album.average_rating,
            'user_rating': score
        })
    except Album.DoesNotExist:
        return Response({'error': 'Album not found'}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def album_rating(request, album_id):
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return Response({'error': 'Album not found'}, status=404)

    user_rating = None
    if request.user.is_authenticated:
        existing = Rating.objects.filter(user=request.user, album=album).first()
        if existing:
            user_rating = existing.score

    return Response({
        'average_rating': album.average_rating,
        'user_rating': user_rating
    })
@api_view(['GET'])
def check_auth(request):
    if request.user.is_authenticated:
        return Response({'authenticated': True, 'user': request.user.username})
    return Response({'authenticated': False}, status=401)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def album_comments(request, album_id):
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return Response({'error': 'Album not found'}, status=404)
    
    if request.method == 'GET':
        comments = album.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'error': 'You must be logged in'}, status=401)
        
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, album=album)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class IndexView(APIView):
    def get(self, request):
        context = {'mensaje': 'Active API for Vinyl Albums'}
        return Response(context)

class CategoriaView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

class AlbumView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        queryset = Album.objects.all()
        
        # ========== فیلتر بر اساس دسته‌بندی (قبلاً داشت) ==========
        categoria_id = request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        # ========== جستجوی پیشرفته (جدید) ==========
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(artist__icontains=search)
            )
        
        # ========== فیلتر بر اساس ژانر (جدید) ==========
        genre = request.query_params.get('genre')
        if genre and genre != '':
            queryset = queryset.filter(genre__iexact=genre)
        
        # ========== فیلتر بر اساس قیمت (جدید) ==========
        min_price = request.query_params.get('min_price')
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(precio__gte=min_price)
            except ValueError:
                pass
        
        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                max_price = float(max_price)
                queryset = queryset.filter(precio__lte=max_price)
            except ValueError:
                pass
        # ==============================================

        serializer = AlbumSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data

        if isinstance(data, list):
            serializer = AlbumSerializer(data=data, many=True)
        else:
            serializer = AlbumSerializer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)
    

    
class AlbumDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        try:
            return Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return None

    def get(self, request, pk):
        album = self.get_object(pk)
        if album is None:
            return Response({'error': 'Album not found'}, status=404)
        serializer = AlbumSerializer(album)
        return Response(serializer.data)

    def put(self, request, pk):
        album = self.get_object(pk)
        if album is None:
            return Response({'error': 'Album not found'}, status=404)
        serializer = AlbumSerializer(album, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        album = self.get_object(pk)
        if album is None:
            return Response({'error': 'Album not found'}, status=404)
        album.delete()
        return Response(status=204)

class CarritoView(APIView):
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
        serializer = CarritoItemSerializer(items, many=True, context={'request': request})
        
        es_vip = False
        if request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(username=request.user.username)
                es_vip = usuario.VIP
            except Usuario.DoesNotExist:
                pass
        
        total = 0
        for item in items:
            precio = item.album.precio
            if es_vip:
                precio = precio * 0.7
            elif item.album.genre == 'Rock':
                precio = precio * 0.8
            total += item.cantidad * precio
        
        return Response({
            'items': serializer.data,
            'total': float(total),
            'cantidad_total': sum(item.cantidad for item in items)
        })

    def post(self, request):
        session_id = self.get_session_id(request)
        album_id = request.data.get('album_id')
        cantidad = request.data.get('cantidad', 1)

        try:
            album = Album.objects.get(id=album_id)
        except Album.DoesNotExist:
            return Response({'error': 'Album not found'}, status=404)

        if cantidad > album.stock:
            return Response({'error': f'Insufficient stock. Available: {album.stock}'}, status=400)

        with transaction.atomic():
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

        serializer = CarritoItemSerializer(item)
        return Response(serializer.data, status=201)

    def delete(self, request):
        """Vaciar todo el carrito (checkout)"""
        session_id = self.get_session_id(request)
        items = CarritoItem.objects.filter(session_id=session_id)
        
        es_vip = False
        if request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(username=request.user.username)
                es_vip = usuario.VIP
            except Usuario.DoesNotExist:
                pass
        
        with transaction.atomic():
            total = 0
            for item in items:
                album = item.album
                if album.stock >= item.cantidad:
                    album.stock -= item.cantidad
                    album.save()
                    
                    precio = album.precio
                    if es_vip:
                        precio = precio * 0.7
                    elif album.genre == 'Rock':
                        precio = precio * 0.8
                    total += item.cantidad * precio
                else:
                    return Response(
                        {'error': f'Insufficient stock for {album.title}'},
                        status=400
                    )

            items.delete()

        return Response({
            'message': 'Purchase processed successfully',
            'total': float(total)
        }, status=200)

class CarritoItemView(APIView):
    permission_classes = [AllowAny]
    
    def get_session_id(self, request):
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        return session_id

    def put(self, request, pk):
        session_id = self.get_session_id(request)
        try:
            item = CarritoItem.objects.get(id=pk, session_id=session_id)
        except CarritoItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)

        nueva_cantidad = request.data.get('cantidad')
        if nueva_cantidad <= 0:
            return Response({'error': 'Quantity must be greater than 0'}, status=400)

        if nueva_cantidad > item.album.stock:
            return Response({'error': f'Insufficient stock. Available: {item.album.stock}'}, status=400)

        item.cantidad = nueva_cantidad
        item.save()
        
        serializer = CarritoItemSerializer(item)
        return Response(serializer.data)

    def delete(self, request, pk):
        session_id = self.get_session_id(request)
        try:
            item = CarritoItem.objects.get(id=pk, session_id=session_id)
            item.delete()
            return Response(status=204)
        except CarritoItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)