from django.db import models
from django.contrib.auth.models import User

class Entrada(models.Model):
    producto = models.CharField(max_length=100, verbose_name="Producto")
    codigo = models.CharField(max_length=100, verbose_name="Código de Producto")
    no_duca = models.CharField(max_length=100   , verbose_name="No. de DUCA", blank=True, null=True)
    categoria = models.CharField(max_length=50, verbose_name="Categoría")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Compra")
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor", blank=True, null=True)  # Volver a texto
    ubicacion = models.CharField(max_length=100, verbose_name="Ubicación", blank=True, null=True)
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    comentario = models.TextField(verbose_name="Comentario", blank=True, null=True)
    imagen = models.ImageField(upload_to='entradas/', verbose_name="Imagen", blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='entradas')
    
    def __str__(self):
        return f"{self.codigo} - {self.producto} - {self.cantidad} und"
    
    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-fecha_registro']


class Cliente(models.Model):
    nit = models.CharField(max_length=20, blank=True, null=True, verbose_name="NIT")  # No unique
    nombre = models.CharField(max_length=100, verbose_name="Nombre/Razón Social")
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    telefono2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre}"
    
    def get_nit_display(self):
        return self.nit if self.nit else "Consumidor Final"
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']


class Venta(models.Model):
    TIPO_DOCUMENTO = [('factura', 'Factura'), ('envio', 'Envío')]
    TIPO_PAGO = [('contado', 'Contado'), ('credito', 'Crédito')]
    
    numero_factura = models.CharField(max_length=20, unique=True, verbose_name="N° Factura")
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Sin IVA
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO, default='factura')
    tipo_pago = models.CharField(max_length=10, choices=TIPO_PAGO, default='contado')
    comentario = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ventas')


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.CharField(max_length=100, verbose_name="Producto")
    codigo = models.CharField(max_length=50, verbose_name="Código")
    proveedor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Proveedor")
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.venta.numero_factura} - {self.producto} x{self.cantidad}"


class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    
    producto = models.CharField(max_length=100, verbose_name="Producto")
    codigo = models.CharField(max_length=50, verbose_name="Código")
    proveedor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Proveedor")
    cantidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    referencia = models.CharField(max_length=50, verbose_name="Referencia (ID Venta/Entrada)")
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movimientos')
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto} - {self.cantidad}"
    
    class Meta:
        verbose_name = "Movimiento Inventario"
        verbose_name_plural = "Movimientos Inventario"
        ordering = ['-fecha']


class MovimientoProducto(models.Model):
    TIPO_MOVIMIENTO = [
        ('cambio_ubicacion', 'Cambio de Ubicación'),
        ('ajuste', 'Ajuste de Stock'),
        ('revision', 'Revisión'),
    ]
    
    producto_codigo = models.CharField(max_length=50, verbose_name="Código")
    producto_nombre = models.CharField(max_length=100, verbose_name="Producto")
    categoria = models.CharField(max_length=50, verbose_name="Categoría")
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor", blank=True, null=True)
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    ubicacion_origen = models.CharField(max_length=100, verbose_name="Ubicación Origen", blank=True, null=True)
    ubicacion_destino = models.CharField(max_length=100, verbose_name="Ubicación Destino", blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO, verbose_name="Tipo")
    motivo = models.TextField(verbose_name="Motivo")
    imagen = models.ImageField(upload_to='movimientos/', blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='movimientos_producto')
    
    def __str__(self):
        return f"{self.producto_codigo} - {self.get_tipo_display()} - {self.cantidad} und"
    
    class Meta:
        verbose_name = "Movimiento de Producto"
        verbose_name_plural = "Movimientos de Productos"
        ordering = ['-fecha']


class PreInventario(models.Model):
    codigo = models.CharField(max_length=100, verbose_name="Código")
    producto = models.CharField(max_length=100, verbose_name="Producto")
    categoria = models.CharField(max_length=50, verbose_name="Categoría")
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor", blank=True, null=True)
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    ubicacion = models.CharField(max_length=100, verbose_name="Ubicación")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    imagen_catalogo = models.ImageField(upload_to='catalogo/', blank=True, null=True, verbose_name="Imagen para Catálogo")
    
    class Meta:
        unique_together = ('codigo', 'producto', 'categoria', 'proveedor', 'ubicacion')
        verbose_name = "Pre-Inventario"
        verbose_name_plural = "Pre-Inventario"
    
    def __str__(self):
        return f"{self.codigo} - {self.producto} - {self.proveedor} - {self.ubicacion}"

class Abono(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='abonos')
    fecha = models.DateField(verbose_name="Fecha de Abono")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='abonos')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Abono {self.fecha.strftime('%d/%m/%Y')} - Q{self.cantidad}"
    

class Proveedor(models.Model):
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT/ID")
    nombre = models.CharField(max_length=100, verbose_name="Nombre/Razón Social")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    persona_contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Persona de Contacto")
    direccion_fiscal = models.TextField(blank=True, null=True, verbose_name="Dirección Fiscal")
    ciudad = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ciudad")
    pais = models.CharField(max_length=50, blank=True, null=True, default="Guatemala", verbose_name="País")
    codigo_postal = models.CharField(max_length=10, blank=True, null=True, verbose_name="Código Postal")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.nit}"
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']


class Pedido(models.Model):
    ESTADO_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('anulado', 'Anulado'), 
    ]
    TIPO_DOCUMENTO = [
        ('factura', 'Factura'),
        ('envio', 'Envío'),
    ]
    TIPO_PAGO = [
        ('contado', 'Contado'),
        ('credito', 'Crédito'),
    ]
    
    numero_pedido = models.CharField(max_length=20, unique=True, verbose_name="N° Pedido")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente")
    direccion_envio = models.TextField(blank=True, null=True, verbose_name="Dirección de Envío")
    estado = models.CharField(max_length=20, choices=ESTADO_PEDIDO, default='pendiente', verbose_name="Estado")
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO, blank=True, null=True, verbose_name="Tipo Documento")
    tipo_pago = models.CharField(max_length=10, choices=TIPO_PAGO, blank=True, null=True, verbose_name="Tipo Pago")
    numero_factura = models.CharField(max_length=20, blank=True, null=True, verbose_name="N° Factura/Envío")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pedidos', verbose_name="Usuario")
    
    def __str__(self):
        return f"{self.numero_pedido} - {self.cliente.nombre if self.cliente else 'Sin cliente'} - {self.get_estado_display()}"
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha']


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles', verbose_name="Pedido")
    producto = models.CharField(max_length=100, verbose_name="Producto")
    codigo = models.CharField(max_length=50, verbose_name="Código")
    proveedor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Proveedor")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    ubicacion = models.CharField(max_length=100, verbose_name="Ubicación")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.pedido.numero_pedido} - {self.producto} x{self.cantidad}"
    
    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Permitir null temporalmente
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']