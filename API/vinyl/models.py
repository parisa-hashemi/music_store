# vinyl/models.py
from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    VIP = models.BooleanField(default=False) # Becomes VIP after purchasing 5+ albums

    def actualizar_estado_vip(self):
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=self.username)
            total_albums = CompraItem.objects.filter(compra__usuario=user).aggregate(
                total=models.Sum('cantidad')
            )['total'] or 0
            
            nuevo_vip = total_albums >= 5
            if self.VIP != nuevo_vip:
                self.VIP = nuevo_vip
                self.save()
        except User.DoesNotExist:
            pass

    def __str__(self):
        return self.username

class Album(models.Model):
    NN = 'NN'
    # --- Rock y derivados ---
    ROCK = 'Rock'
    INDIE_ROCK = 'Indie Rock'
    INDIE_POP = 'Indie Pop'
    ALTERNATIVE_ROCK = 'Alternative Rock'
    METAL = 'Metal'
    PUNK = 'Punk'

    # --- Pop y derivados ---
    POP = 'Pop'
    JPOP = 'J-pop'
    KPOP = 'K-pop'

    # --- Jazz / Blues / Soul ---
    JAZZ = 'Jazz'
    BLUES = 'Blues'
    DISCO = 'Disco'

    # --- Latin Music ---
    SALSA = 'Salsa'
    BACHATA = 'Bachata'
    REGGAETON = 'Reggaeton'
    CUMBIA = 'Cumbia'
    DEMBOW = 'Dembow'
    BOLERO = 'Bolero'

    # --- Electronic ---
    ELECTRONICA = 'Electronic'
    TECHNO = 'Techno'

    # --- Hip Hop / Reggae ---
    HIP_HOP = 'Hip Hop'
    REGGAE = 'Reggae'
    TRAP = 'Trap'

    GENRE_CHOICES = [
        (NN, 'No definido'),
        # --- Rock y derivados ---
        (ROCK, 'Rock'),
        (INDIE_ROCK, 'Indie Rock'),
        (INDIE_POP, 'Indie Pop'),
        (ALTERNATIVE_ROCK, 'Alternative Rock'),
        (METAL, 'Metal'),
        (PUNK, 'Punk'),

        # --- Pop y derivados ---
        (POP, 'Pop'),
        (KPOP, 'K-pop'),
        (JPOP, 'J-pop'),

        # --- Jazz / Blues / Soul ---
        (JAZZ, 'Jazz'),
        (BLUES, 'Blues'),
        (DISCO, 'Disco'),

        # --- Latin Music ---
        (SALSA, 'Salsa'),
        (BACHATA, 'Bachata'),
        (REGGAETON, 'Reggaeton'),
        (CUMBIA, 'Cumbia'),
        (DEMBOW, 'Dembow'),
        (BOLERO, 'Bolero'),

        # --- Electronic ---
        (ELECTRONICA, 'Electronic'),
        (TECHNO, 'Techno'),

        # --- Hip Hop / Reggae ---
        (HIP_HOP, 'Hip Hop'),
        (REGGAE, 'Reggae'),
        (TRAP, 'Trap'),

    
    ]
    
    BESTSELLER = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    rating = models.IntegerField(default=0)
    release_date = models.DateField()
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, default=NN)
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='album_images/', null=True, blank=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)

    
  
    tracks = models.JSONField(default=list, blank=True, verbose_name="لیست ترک‌ها")
    average_rating = models.FloatField(default=0, verbose_name="میانگین امتیاز")
    preview_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="پیش‌پخش صوتی")
    cover_image = models.URLField(max_length=500, blank=True, null=True, verbose_name="عکس کاور")


    def __str__(self):
        return f"{self.title} by {self.artist}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class CarritoItem(models.Model):
    session_id = models.CharField(max_length=100)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session_id', 'album']
    
    def __str__(self):
        return f"{self.cantidad}x {self.album.title}"

class Comment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="کاربر")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='comments', verbose_name="آلبوم")
    body = models.TextField(verbose_name="متن نظر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        ordering = ['-created_at']  # آخرین نظرات اول نمایش داده شوند
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
    
    def __str__(self):
        return f"{self.user.username} - {self.album.title}"

class Compra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"Compra {self.id} - {self.usuario.username}"

class CompraItem(models.Model):
    compra = models.ForeignKey(Compra, related_name='items', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.cantidad}x {self.album.title}"
class Rating(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="امتیاز")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'album')  # هر کاربر فقط یک بار امتیاز بده
    
    def __str__(self):
        return f"{self.user.username} - {self.album.title}: {self.score}"
# Signal to automatically update VIP status
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Compra)
def actualizar_vip_usuario(sender, instance, created, **kwargs):
    if created:
        try:
            usuario = Usuario.objects.get(username=instance.usuario.username)
            usuario.actualizar_estado_vip()
        except Usuario.DoesNotExist:
            pass
