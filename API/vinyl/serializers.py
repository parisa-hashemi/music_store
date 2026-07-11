# vynyl/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import *
from .models import Rating

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class AlbumSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'rating', 'release_date', 'genre', 'stock', 'precio', 'categoria', 'categoria_nombre', 'tracks', 'average_rating', 'preview_url', 'cover_image']

    def create(self, validated_data):
        if not validated_data.get('cover_image'):
            from .utils import fetch_album_cover
            cover = fetch_album_cover(validated_data.get('title', ''), validated_data.get('artist', ''))
            if cover:
                validated_data['cover_image'] = cover
        return super().create(validated_data)

class CarritoItemSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    album_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    precio_con_descuento = serializers.SerializerMethodField()
    
    class Meta:
        model = CarritoItem
        fields = ['id', 'album', 'album_id', 'cantidad', 'subtotal', 'precio_con_descuento', 'fecha_agregado']
    
    def get_precio_con_descuento(self, obj):
        request = self.context.get('request')
        precio_base = obj.album.precio
        
        if request and request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(username=request.user.username)
                if usuario.VIP:
                    return float(precio_base * 0.7)
            except Usuario.DoesNotExist:
                pass
        
        if obj.album.genre == 'Rock':
            return float(precio_base * 0.8)
        
        return float(precio_base)
    
    def get_subtotal(self, obj):
        precio_con_descuento = self.get_precio_con_descuento(obj)
        return obj.cantidad * precio_con_descuento
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    def validate(self, data):
        album_id = data.get('album_id')
        cantidad = data.get('cantidad', 1)

        try:
            album = Album.objects.get(id=album_id)
            if cantidad > album.stock:
                raise serializers.ValidationError(f"Insufficient stock. Available: {album.stock}")
        except Album.DoesNotExist:
            raise serializers.ValidationError("The album does not exist")
        
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("Inactive user")
            
        data['user'] = user
        return data

class CompraItemSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    
    class Meta:
        model = CompraItem
        fields = ['album', 'cantidad', 'precio_unitario']

class CompraSerializer(serializers.ModelSerializer):
    items = CompraItemSerializer(many=True, read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = Compra
        fields = ['id', 'fecha', 'total', 'usuario_username', 'items']

class UserProfileSerializer(serializers.ModelSerializer):
    total_albums_comprados = serializers.SerializerMethodField()
    es_vip = serializers.SerializerMethodField()
    es_staff = serializers.BooleanField(source='is_staff', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'total_albums_comprados', 'es_vip', 'es_staff']
    
    def get_total_albums_comprados(self, obj):
        from django.db import models
        return CompraItem.objects.filter(compra__usuario=obj).aggregate(
            total=models.Sum('cantidad')
        )['total'] or 0
    
    def get_es_vip(self, obj):
        try:
            usuario = Usuario.objects.get(username=obj.username)
            return usuario.VIP
        except Usuario.DoesNotExist:
            return False
    
class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'album', 'user_name', 'body', 'created_at']
        read_only_fields = ['id', 'user_name', 'created_at', 'album']



class RatingSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Rating
        fields = ['id', 'album', 'user_name', 'score', 'created_at']
        read_only_fields = ['id', 'user_name', 'created_at', 'album']