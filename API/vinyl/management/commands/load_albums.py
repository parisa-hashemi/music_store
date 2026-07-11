import json
import os
from django.core.management.base import BaseCommand
from vinyl.models import Album

class Command(BaseCommand):
    help = 'Loads albums from albums.json'

    def handle(self, *args, **options):
        # Ruta al archivo JSON
        json_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'albums.json')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                albums_data = json.load(file)
            
            created_count = 0
            updated_count = 0
            
            for album_data in albums_data:
                # Check whether the album already exists
                album, created = Album.objects.get_or_create(
                    title=album_data['title'],
                    artist=album_data['artist'],
                    defaults={
                        'BESTSELLER': album_data.get('BESTSELLER', False),
                        'rating': album_data.get('rating', 0),
                        'release_date': album_data.get('release_date'),
                        'genre': album_data.get('genre', 'NN'),
                        'stock': album_data.get('stock', 0),
                        'precio': album_data.get('precio', 0.00),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"[+] Creado: {album.title} - {album.artist}")
                else:
                    # Actualizar datos existentes
                    album.BESTSELLER = album_data.get('BESTSELLER', False)
                    album.rating = album_data.get('rating', 0)
                    album.release_date = album_data.get('release_date')
                    album.genre = album_data.get('genre', 'NN')
                    album.stock = album_data.get('stock', 0)
                    album.precio = album_data.get('precio', 0.00)
                    album.save()
                    updated_count += 1
                    self.stdout.write(f"[*] Actualizado: {album.title} - {album.artist}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nProceso completado:\n'
                    f'   - {created_count} albumes creados\n'
                    f'   - {updated_count} albumes actualizados\n'
                    f'   - Total: {created_count + updated_count} albumes procesados'
                )
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('Error: No se encontro el archivo albums.json')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Error: El archivo albums.json no es valido')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error inesperado: {str(e)}')
            )