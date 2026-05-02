from django.contrib import admin
from .models import Entrada, Proveedor, Cliente, Venta, DetalleVenta, MovimientoInventario, MovimientoProducto, PreInventario, Pedido, DetallePedido
from .models import Categoria


# Personalización del admin
admin.site.site_header = "El Charro - Inventario"
admin.site.site_title = "Panel de Control"
admin.site.index_title = "Bienvenido al Sistema de Inventario"

# Registrar modelos (sin usar @admin.register para evitar duplicados)
admin.site.register(Entrada)
admin.site.register(Proveedor)
admin.site.register(Cliente)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(MovimientoInventario)
admin.site.register(MovimientoProducto)

# Registrar PreInventario con configuración personalizada
class PreInventarioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'producto', 'categoria', 'proveedor', 'cantidad', 'ubicacion']
    list_filter = ['categoria', 'ubicacion', 'proveedor']
    search_fields = ['codigo', 'producto', 'categoria', 'proveedor', 'ubicacion']
    list_per_page = 50

admin.site.register(PreInventario, PreInventarioAdmin)

admin.site.register(Pedido)
admin.site.register(DetallePedido)



# Registrar Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'fecha_creacion']
    search_fields = ['nombre']
    list_filter = ['fecha_creacion']