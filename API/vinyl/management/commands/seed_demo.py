import urllib.request
import urllib.error

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from vinyl.models import Album, Categoria, Comment, Rating, Usuario
from vinyl.utils import fetch_album_cover
from django.contrib.auth.models import User

# Same category mapping used by create_categories.py
CATEGORIAS = {
    'Rock & Metal': 'Rock, Metal, Punk and related genres',
    'International Pop': 'Pop, K-pop, J-pop',
    'Jazz & Blues': 'Jazz, Blues and classical music',
    'Latin Music': 'Salsa, Bachata, Reggaeton, Cumbia',
    'Electronic': 'Disco, Electronic, Techno',
    'Hip Hop & Reggae': 'Hip Hop, Reggae, Trap',
}

# Sample tracks from SoundHelix (royalty-free, meant for demos/testing of
# audio players). They are not real excerpts from the album, just an
# example preview, same as the picsum.photos cover images.
_SOUNDHELIX = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{}.mp3"

ALBUMS = [
    {'title': 'Abbey Road', 'artist': 'The Beatles', 'genre': 'Rock',
     'release_date': '1969-09-26', 'precio': '92.99', 'stock': 10, 'categoria': 'Rock & Metal',
     'preview_url': _SOUNDHELIX.format(1)},
    {'title': 'The Dark Side of the Moon', 'artist': 'Pink Floyd', 'genre': 'Rock',
     'release_date': '1973-03-01', 'precio': '99.99', 'stock': 8, 'categoria': 'Rock & Metal',
     'preview_url': _SOUNDHELIX.format(2)},
    {'title': 'Nevermind', 'artist': 'Nirvana', 'genre': 'Alternative Rock',
     'release_date': '1991-09-24', 'precio': '84.99', 'stock': 12, 'categoria': 'Rock & Metal',
     'preview_url': _SOUNDHELIX.format(3)},
    {'title': 'Purple Rain', 'artist': 'Prince', 'genre': 'Pop',
     'release_date': '1984-06-25', 'precio': '89.99', 'stock': 15, 'categoria': 'International Pop',
     'preview_url': _SOUNDHELIX.format(4)},
    {'title': 'The Chronic', 'artist': 'Dr. Dre', 'genre': 'Hip Hop',
     'release_date': '1992-12-15', 'precio': '79.99', 'stock': 9, 'categoria': 'Hip Hop & Reggae',
     'preview_url': _SOUNDHELIX.format(5)},
    {'title': 'Exodus', 'artist': 'Bob Marley & The Wailers', 'genre': 'Reggae',
     'release_date': '1977-06-03', 'precio': '74.99', 'stock': 11, 'categoria': 'Hip Hop & Reggae',
     'preview_url': _SOUNDHELIX.format(6)},
    {'title': 'Time Out', 'artist': 'The Dave Brubeck Quartet', 'genre': 'Jazz',
     'release_date': '1959-12-14', 'precio': '94.99', 'stock': 6, 'categoria': 'Jazz & Blues',
     'preview_url': _SOUNDHELIX.format(7)},
    {'title': 'Live at the Regal', 'artist': 'B.B. King', 'genre': 'Blues',
     'release_date': '1965-11-21', 'precio': '69.99', 'stock': 5, 'categoria': 'Jazz & Blues',
     'preview_url': _SOUNDHELIX.format(8)},
    {'title': 'Buena Vista Social Club', 'artist': 'Buena Vista Social Club', 'genre': 'Salsa',
     'release_date': '1997-06-17', 'precio': '79.99', 'stock': 7, 'categoria': 'Latin Music',
     'preview_url': _SOUNDHELIX.format(9)},
    {'title': 'Homework', 'artist': 'Daft Punk', 'genre': 'Electronic',
     'release_date': '1997-01-20', 'precio': '84.99', 'stock': 10, 'categoria': 'Electronic',
     'preview_url': _SOUNDHELIX.format(10)},
]

DEMO_USERS = [
    {'username': 'demo1', 'email': 'demo1@example.com'},
    {'username': 'demo2', 'email': 'demo2@example.com'},
    {'username': 'demo3', 'email': 'demo3@example.com'},
]
DEMO_PASSWORD = 'Demo12345!'

# (album title, username, comment text)
COMENTARIOS = [
    ('Abbey Road', 'demo1', 'One of the best albums ever made, the B-side is pure art.'),
    ('Abbey Road', 'demo2', 'The vinyl quality is excellent, it arrived well packaged.'),
    ('Nevermind', 'demo2', 'It changed the history of rock, a must-have in any collection.'),
    ('The Chronic', 'demo3', 'A classic of 90s hip hop, the vinyl sound is incredible.'),
    ('Time Out', 'demo1', 'Jazz never sounded this good, "Take Five" on vinyl is a whole different experience.'),
    ('Buena Vista Social Club', 'demo3', 'It transports me straight to Havana, great audio quality.'),
]

# (album title, username, score 1-5)
RATINGS = [
    ('Abbey Road', 'demo1', 5),
    ('Abbey Road', 'demo2', 5),
    ('Abbey Road', 'demo3', 4),
    ('Nevermind', 'demo1', 5),
    ('Nevermind', 'demo2', 4),
    ('The Chronic', 'demo3', 5),
    ('Time Out', 'demo1', 4),
    ('Buena Vista Social Club', 'demo2', 5),
    ('Homework', 'demo1', 5),
    ('Homework', 'demo2', 4),
    ('Homework', 'demo3', 5),
]


class Command(BaseCommand):
    help = 'Creates demo data: albums with cover art, test users, comments and ratings'

    def handle(self, *args, **options):
        categorias_creadas = self._crear_categorias()
        albumes_creados = self._crear_albumes(categorias_creadas)
        usuarios_creados = self._crear_usuarios()
        comentarios_creados = self._crear_comentarios(usuarios_creados)
        ratings_creados = self._crear_ratings(usuarios_creados)

        self.stdout.write(
            self.style.SUCCESS(
                '\nSeed completado:\n'
                f'   - {len(categorias_creadas)} categorias disponibles\n'
                f'   - {albumes_creados} albumes nuevos\n'
                f'   - {len(usuarios_creados)} usuarios de demo disponibles\n'
                f'   - {comentarios_creados} comentarios nuevos\n'
                f'   - {ratings_creados} ratings nuevos'
            )
        )

    def _crear_categorias(self):
        categorias = {}
        for nombre, descripcion in CATEGORIAS.items():
            categoria, created = Categoria.objects.get_or_create(
                nombre=nombre, defaults={'descripcion': descripcion}
            )
            if created:
                self.stdout.write(f"[+] Categoria creada: {categoria.nombre}")
            categorias[nombre] = categoria
        return categorias

    def _descargar_portada(self, album, seed):
        if album.image:
            return
        url = f"https://picsum.photos/seed/{seed}/500/500"
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=10) as response:
                contenido = response.read()
            album.image.save(f"{seed}.jpg", ContentFile(contenido), save=True)
            self.stdout.write(f"    -> portada descargada para {album.title}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            self.stdout.write(
                self.style.WARNING(f"    -> no se pudo descargar la portada de {album.title}: {e}")
            )

    def _asignar_cover_image(self, album):
        if album.cover_image:
            return
        cover = fetch_album_cover(album.title, album.artist)
        if cover:
            album.cover_image = cover
            album.save()
            self.stdout.write(f"    -> cover_image (iTunes) asignado para {album.title}")
        else:
            self.stdout.write(
                self.style.WARNING(f"    -> no se encontro cover en iTunes para {album.title}")
            )

    def _crear_albumes(self, categorias):
        creados = 0
        for data in ALBUMS:
            album, created = Album.objects.get_or_create(
                title=data['title'],
                artist=data['artist'],
                defaults={
                    'genre': data['genre'],
                    'release_date': data['release_date'],
                    'precio': data['precio'],
                    'stock': data['stock'],
                    'categoria': categorias.get(data['categoria']),
                    'preview_url': data['preview_url'],
                }
            )
            if created:
                creados += 1
                self.stdout.write(f"[+] Album creado: {album.title} - {album.artist}")
            elif album.preview_url != data['preview_url']:
                album.preview_url = data['preview_url']
                album.save()
                self.stdout.write(f"    -> preview_url actualizado para {album.title}")
            self._descargar_portada(album, slugify(f"{data['title']}-{data['artist']}"))
            self._asignar_cover_image(album)
        return creados

    def _crear_usuarios(self):
        usuarios = {}
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'], defaults={'email': data['email']}
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
                Usuario.objects.get_or_create(
                    username=user.username,
                    defaults={'email': user.email, 'password': user.password}
                )
                self.stdout.write(f"[+] Usuario de demo creado: {user.username} / {DEMO_PASSWORD}")
            usuarios[data['username']] = user
        return usuarios

    def _crear_comentarios(self, usuarios):
        creados = 0
        for titulo, username, texto in COMENTARIOS:
            try:
                album = Album.objects.get(title=titulo)
            except Album.DoesNotExist:
                continue
            user = usuarios.get(username)
            if not user:
                continue
            comment, created = Comment.objects.get_or_create(
                user=user, album=album, body=texto
            )
            if created:
                creados += 1
        return creados

    def _crear_ratings(self, usuarios):
        creados = 0
        albumes_afectados = set()
        for titulo, username, score in RATINGS:
            try:
                album = Album.objects.get(title=titulo)
            except Album.DoesNotExist:
                continue
            user = usuarios.get(username)
            if not user:
                continue
            rating, created = Rating.objects.get_or_create(
                user=user, album=album, defaults={'score': score}
            )
            if created:
                creados += 1
                albumes_afectados.add(album.id)

        # Recalculate the average for affected albums
        from django.db.models import Avg
        for album_id in albumes_afectados:
            album = Album.objects.get(id=album_id)
            avg = album.ratings.aggregate(Avg('score'))['score__avg']
            album.average_rating = avg or 0
            album.save()

        return creados
