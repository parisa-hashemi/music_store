from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.db import transaction
from django.db import models
from django.contrib.auth.models import User

from .models import CarritoItem, Compra, CompraItem, Usuario
from .serializers import UserRegistrationSerializer, UserLoginSerializer, CompraSerializer, UserProfileSerializer

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Also create the custom Usuario
            from .models import Usuario
            Usuario.objects.create(
                username=user.username,
                email=user.email,
                password=user.password
            )
            return Response({'message': 'User created successfully', 'user_id': user.id}, status=201)
        return Response(serializer.errors, status=400)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=400)

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

class UserLogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            # Clear cart before logout
            session_id = request.session.session_key
            if session_id:
                CarritoItem.objects.filter(session_id=session_id).delete()
            logout(request)
        return Response({'message': 'Logout successful'})

class HistorialComprasView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.is_staff:
            compras = Compra.objects.all().order_by('-fecha')
        else:
            compras = Compra.objects.filter(usuario=request.user).order_by('-fecha')
        serializer = CompraSerializer(compras, many=True)
        return Response(serializer.data)

from decimal import Decimal

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        stripe_payment_id = request.data.get('stripe_payment_id')
        
        session_id = request.session.session_key
        if not session_id:
            return Response({'error': 'No active cart'}, status=400)

        items = CarritoItem.objects.filter(session_id=session_id)
        if not items.exists():
            return Response({'error': 'Cart is empty'}, status=400)
        
        es_vip = False
        try:
            usuario = Usuario.objects.get(username=request.user.username)
            es_vip = usuario.VIP
        except Usuario.DoesNotExist:
            pass
        
        total = Decimal("0")
        
        for item in items:
            precio = item.album.precio

            if es_vip:
                precio = precio * Decimal("0.7")
            elif item.album.genre == 'Rock':
                precio = precio * Decimal("0.8")

            total += item.cantidad * precio
        
        with transaction.atomic():
            compra = Compra.objects.create(
                usuario=request.user,
                total=total,
                stripe_payment_id=stripe_payment_id
            )
            
            for item in items:
                album = item.album
                if album.stock >= item.cantidad:
                    precio = album.precio

                    if es_vip:
                        precio = precio * Decimal("0.7")
                    elif album.genre == 'Rock':
                        precio = precio * Decimal("0.8")
                    
                    CompraItem.objects.create(
                        compra=compra,
                        album=album,
                        cantidad=item.cantidad,
                        precio_unitario=precio
                    )
                    album.stock -= item.cantidad
                    album.save()
                else:
                    return Response(
                        {'error': f'Insufficient stock for {album.title}'},
                        status=400
                    )

            items.delete()

        return Response({
            'message': 'Purchase processed successfully',
            'compra_id': compra.id
        }, status=201)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

class UsuariosVIPView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Not authorized'}, status=403)
        
        usuarios_vip = Usuario.objects.filter(VIP=True)
        data = []
        for usuario in usuarios_vip:
            try:
                user = User.objects.get(username=usuario.username)
                total_albums = CompraItem.objects.filter(compra__usuario=user).aggregate(
                    total=models.Sum('cantidad')
                )['total'] or 0
                data.append({
                    'id': usuario.id,
                    'username': usuario.username,
                    'email': usuario.email,
                    'total_albums': total_albums,
                    'VIP': usuario.VIP
                })
            except User.DoesNotExist:
                pass
        return Response(data)