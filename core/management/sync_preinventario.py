from django.core.management.base import BaseCommand
from core.models import Entrada, PreInventario
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Sincroniza Entradas con Pre-Inventario'

    def handle(self, *args, **options):
        # Limpiar PreInventario
        PreInventario.objects.all().delete()
        
        # Agrupar entradas por combinación
        entradas = Entrada.objects.values(
            'codigo', 'producto', 'categoria', 'proveedor', 'ubicacion'
        ).annotate(total=Sum('cantidad'))
        
        for e in entradas:
            PreInventario.objects.create(
                codigo=e['codigo'],
                producto=e['producto'],
                categoria=e['categoria'],
                proveedor=e['proveedor'] or '',
                cantidad=e['total'],
                ubicacion=e['ubicacion'] or 'Sin ubicación'
            )
            self.stdout.write(f"Creado: {e['codigo']} | {e['ubicacion']} | {e['total']}")
        
        self.stdout.write(self.style.SUCCESS('Sincronización completada'))