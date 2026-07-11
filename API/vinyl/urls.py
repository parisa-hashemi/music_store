# vinyl/urls.py
from django.urls import path
from . import views 
from .views import album_comments 
from . import auth_views
from . import test_views
from . import simple_views
from . import carrito_views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('albums/', views.AlbumView.as_view(), name='albums'),
    path('albums/<int:pk>/', views.AlbumDetailView.as_view(), name='album-detail'),
    path('categorias/', views.CategoriaView.as_view(), name='categorias'),
    path('carrito/', simple_views.SimpleCarritoView.as_view(), name='carrito'),
    path('carrito/checkout/', views.CarritoView.as_view(), name='carrito-checkout'),
    path('carrito/<int:pk>/', views.CarritoItemView.as_view(), name='carrito-item'),
    path('carrito/album/<int:album_id>/', carrito_views.CarritoAlbumView.as_view(), name='carrito-album'),
    
    # Auth endpoints
    path('auth/register/', auth_views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', auth_views.UserLoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.UserLogoutView.as_view(), name='logout'),
    path('historial/', auth_views.HistorialComprasView.as_view(), name='historial'),
    path('user/profile/', auth_views.UserProfileView.as_view(), name='user-profile'),
    path('usuarios-vip/', auth_views.UsuariosVIPView.as_view(), name='usuarios-vip'),
    path('checkout/', auth_views.CheckoutView.as_view(), name='checkout'),
    path('test/', test_views.TestView.as_view(), name='test'),
    path('albums/<int:album_id>/comments/', album_comments, name='album-comments'),
    path('auth/check/', views.check_auth, name='check-auth'),
    path('albums/<int:album_id>/rate/', views.rate_album, name='rate-album'),
    path('albums/<int:album_id>/rating/', views.album_rating, name='album-rating'),
    path('user/stats/', views.user_stats, name='user-stats'),
    path('user/profile/', views.user_profile, name='user-profile'),

] 