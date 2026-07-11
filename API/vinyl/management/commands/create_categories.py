from django.core.management.base import BaseCommand
from vinyl.models import Categoria, Album

class Command(BaseCommand):
    help = 'Creates categories and assigns albums'

    def handle(self, *args, **options):
        # Create categories
        categorias_data = [
            {'nombre': 'Rock & Metal', 'descripcion': 'Rock, Metal, Punk and related genres'},
            {'nombre': 'International Pop', 'descripcion': 'Pop, K-pop, J-pop'},
            {'nombre': 'Jazz & Blues', 'descripcion': 'Jazz, Blues and classical music'},
            {'nombre': 'Latin Music', 'descripcion': 'Salsa, Bachata, Reggaeton, Cumbia'},
            {'nombre': 'Electronic', 'descripcion': 'Disco, Electronic, Techno'},
            {'nombre': 'Hip Hop & Reggae', 'descripcion': 'Hip Hop, Reggae, Trap'},
        ]
        
        created_categories = 0
        for cat_data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={'descripcion': cat_data['descripcion']}
            )
            if created:
                created_categories += 1
                self.stdout.write(f"[+] Categoria creada: {categoria.nombre}")
        
        # Assign albums to categories
        asignaciones = {
            'Rock & Metal': ['Rock', 'Indie Rock', 'Alternative Rock', 'Metal', 'Punk'],
            'International Pop': ['Pop', 'K-pop', 'J-pop', 'Indie Pop'],
            'Jazz & Blues': ['Jazz', 'Blues'],
            'Latin Music': ['Salsa', 'Bachata', 'Reggaeton', 'Cumbia', 'Dembow', 'Bolero'],
            'Electronic': ['Disco', 'Electronic', 'Techno'],
            'Hip Hop & Reggae': ['Hip Hop', 'Reggae', 'Trap'],
        }
        
        albums_assigned = 0
        for categoria_nombre, generos in asignaciones.items():
            try:
                categoria = Categoria.objects.get(nombre=categoria_nombre)
                albums = Album.objects.filter(genre__in=generos, categoria__isnull=True)
                
                for album in albums:
                    album.categoria = categoria
                    album.save()
                    albums_assigned += 1
                    self.stdout.write(f"[*] {album.title} -> {categoria_nombre}")
                    
            except Categoria.DoesNotExist:
                self.stdout.write(f"Error: Categoria {categoria_nombre} no encontrada")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nProceso completado:\n'
                f'   - {created_categories} categorias creadas\n'
                f'   - {albums_assigned} albumes asignados a categorias'
            )
        )