import time

from django.core.management.base import BaseCommand
from django.db.models import Q

from vinyl.models import Album
from vinyl.utils import fetch_album_cover

# Mismas pistas de ejemplo (royalty-free) usadas por seed_demo.py.
_SOUNDHELIX = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-{}.mp3"
_SOUNDHELIX_COUNT = 16

_ITUNES_DELAY_SECONDS = 0.5


class Command(BaseCommand):
    help = 'Rellena cover_image (iTunes) y preview_url (SoundHelix) en los albumes que aun no los tienen'

    def handle(self, *args, **options):
        sin_cover = list(Album.objects.filter(Q(cover_image__isnull=True) | Q(cover_image='')))
        sin_preview = list(Album.objects.filter(Q(preview_url__isnull=True) | Q(preview_url='')))

        covers_asignados = 0
        covers_no_encontrados = []
        for album in sin_cover:
            cover = fetch_album_cover(album.title, album.artist)
            if cover:
                album.cover_image = cover
                album.save(update_fields=['cover_image'])
                covers_asignados += 1
                self.stdout.write(f"[+] cover_image: {album.title} - {album.artist}")
            else:
                covers_no_encontrados.append(f"{album.title} - {album.artist}")
                self.stdout.write(
                    self.style.WARNING(f"[-] no se encontro cover en iTunes: {album.title} - {album.artist}")
                )
            time.sleep(_ITUNES_DELAY_SECONDS)  # evitar rate limiting de la API de iTunes

        previews_asignados = 0
        for i, album in enumerate(sin_preview):
            album.preview_url = _SOUNDHELIX.format((i % _SOUNDHELIX_COUNT) + 1)
            album.save(update_fields=['preview_url'])
            previews_asignados += 1
            self.stdout.write(f"[+] preview_url: {album.title} - {album.artist}")

        self.stdout.write(
            self.style.SUCCESS(
                '\nBackfill completado:\n'
                f'   - {covers_asignados}/{len(sin_cover)} cover_image asignados\n'
                f'   - {previews_asignados}/{len(sin_preview)} preview_url asignados'
            )
        )
        if covers_no_encontrados:
            self.stdout.write(
                self.style.WARNING(
                    '\nAlbumes sin cover en iTunes (revisar titulo/artista):\n'
                    + '\n'.join(f'   - {a}' for a in covers_no_encontrados)
                )
            )
