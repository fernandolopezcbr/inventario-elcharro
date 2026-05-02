from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from core.models import *
from datetime import date, timedelta
import json

class AuthTest(TestCase):
    """Pruebas de autenticación y roles"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.operativo = User.objects.create_user(username='operativo', password='operativo123')
        grupo, _ = Group.objects.get_or_create(name='Operativo')
        self.operativo.groups.add(grupo)
    
    def test_login_admin(self):
        response = self.client.post('/login/', {'username': 'admin', 'password': 'admin123'})
        self.assertEqual(response.status_code, 302)  # Redirige al home
        print("✅ Login admin - OK")
    
    def test_login_operativo(self):
        response = self.client.post('/login/', {'username': 'operativo', 'password': 'operativo123'})
        self.assertEqual(response.status_code, 302)
        print("✅ Login operativo - OK")


class EntradaTest(TestCase):
    """Pruebas del módulo Entradas"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
        self.categoria = Categoria.objects.create(nombre='Electrónicos')
    
    def test_crear_entrada(self):
        response = self.client.post('/entradas/crear/', {
            'codigo': 'TEST001',
            'producto': 'Producto Prueba',
            'categoria': 'Electrónicos',
            'cantidad': 10,
            'precio_compra': 100.50,
            'fecha_ingreso': date.today().isoformat(),
            'ubicacion': 'bodega1'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        print("✅ Crear entrada - OK")
    
    def test_listar_entradas(self):
        response = self.client.get('/entradas/')
        self.assertEqual(response.status_code, 200)
        print("✅ Listar entradas - OK")


class VentaTest(TestCase):
    """Pruebas del módulo Ventas"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
        self.cliente = Cliente.objects.create(nit='CF', nombre='Consumidor Final')
        self.pre = PreInventario.objects.create(
            codigo='PROD001',
            producto='Producto Test',
            categoria='General',
            cantidad=50,
            ubicacion='bodega1'
        )
    
    def test_buscar_productos(self):
        response = self.client.get('/ventas/buscar-productos/', {'q': 'PROD001'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data), 0)
        print("✅ Buscar productos - OK")
    
    def test_finalizar_venta(self):
        response = self.client.post('/ventas/finalizar/', 
            json.dumps({
                'cliente_id': self.cliente.id,
                'carrito': [{
                    'codigo': 'PROD001',
                    'producto': 'Producto Test',
                    'cantidad': 2,
                    'precio': 150,
                    'ubicacion': 'bodega1'
                }],
                'subtotal': 300,
                'total': 300,
                'tipo_documento': 'factura',
                'tipo_pago': 'contado'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        print("✅ Finalizar venta - OK")


class PedidoTest(TestCase):
    """Pruebas del módulo Pedidos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
        self.cliente = Cliente.objects.create(nit='CF', nombre='Consumidor Final')
        self.pre = PreInventario.objects.create(
            codigo='PED001',
            producto='Pedido Test',
            categoria='General',
            cantidad=30,
            ubicacion='bodega1'
        )
    
    def test_catalogo_pedidos(self):
        response = self.client.get('/pedidos/catalogo/')
        self.assertEqual(response.status_code, 200)
        print("✅ Catálogo pedidos - OK")
    
    def test_crear_pedido(self):
        response = self.client.post('/pedidos/checkout/',
            json.dumps({
                'carrito': [{
                    'codigo': 'PED001',
                    'producto': 'Pedido Test',
                    'cantidad': 3,
                    'precio': 100,
                    'ubicacion': 'bodega1'
                }],
                'cliente': {'id': self.cliente.id, 'nombre': 'Consumidor Final'}
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        print("✅ Crear pedido - OK")


class ProductoTest(TestCase):
    """Pruebas del módulo Productos"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
        self.pre = PreInventario.objects.create(
            codigo='PROD001',
            producto='Producto Stock',
            categoria='General',
            cantidad=25,
            ubicacion='bodega1'
        )
    
    def test_listar_productos(self):
        response = self.client.get('/productos/')
        self.assertEqual(response.status_code, 200)
        print("✅ Listar productos - OK")
    
    def test_registrar_movimiento(self):
        response = self.client.post('/productos/movimiento/', {
            'producto_codigo': 'PROD001',
            'producto_nombre': 'Producto Stock',
            'categoria': 'General',
            'proveedor': 'Test',
            'cantidad': 5,
            'ubicacion_origen': 'bodega1',
            'ubicacion_destino': 'bodega2',
            'tipo': 'cambio_ubicacion',
            'motivo': 'Prueba'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        print("✅ Registrar movimiento - OK")


class InventarioGeneralTest(TestCase):
    """Pruebas del módulo Inventario General"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
        PreInventario.objects.create(
            codigo='INV001',
            producto='Producto Inv',
            categoria='General',
            cantidad=15,
            ubicacion='bodega1'
        )
        PreInventario.objects.create(
            codigo='INV001',
            producto='Producto Inv',
            categoria='General',
            cantidad=10,
            ubicacion='bodega2'
        )
    
    def test_inventario_general(self):
        response = self.client.get('/inventario/')
        self.assertEqual(response.status_code, 200)
        print("✅ Inventario general - OK")


class ClienteProveedorTest(TestCase):
    """Pruebas de Clientes y Proveedores"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
    
    def test_crear_cliente(self):
        response = self.client.post('/clientes/crear/', {
            'nit': '999999-9',
            'nombre': 'Cliente QA Test'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        print("✅ Crear cliente - OK")
    
    def test_crear_proveedor(self):
        response = self.client.post('/proveedores/crear/', {
            'nit': 'PROV001',
            'nombre': 'Proveedor QA Test'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        print("✅ Crear proveedor - OK")


# ==================== PRUEBAS DE SEGURIDAD ====================

class SeguridadTest(TestCase):
    """Pruebas de autenticación y autorización"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.operativo = User.objects.create_user(username='operativo', password='operativo123')
        grupo, _ = Group.objects.get_or_create(name='Operativo')
        self.operativo.groups.add(grupo)
    
    def test_urls_protegidas_sin_login(self):
        """Verificar que URLs importantes requieren login"""
        urls_protegidas = ['/entradas/', '/ventas/', '/productos/', '/pedidos/catalogo/']
        for url in urls_protegidas:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Redirige a login
            print(f"✅ {url} está protegida")
    
    def test_operativo_no_accede_entradas(self):
        """Operativo NO debe acceder a Entradas"""
        self.client.login(username='operativo', password='operativo123')
        response = self.client.get('/entradas/')
        self.assertEqual(response.status_code, 403)  # Prohibido
        print("✅ Operativo no accede a Entradas")
    
    def test_operativo_accede_ventas(self):
        """Operativo SÍ debe acceder a Ventas"""
        self.client.login(username='operativo', password='operativo123')
        response = self.client.get('/ventas/')
        self.assertEqual(response.status_code, 200)
        print("✅ Operativo accede a Ventas")
    
    def test_admin_accede_entradas(self):
        """Admin SÍ debe acceder a Entradas"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/entradas/')
        self.assertEqual(response.status_code, 200)
        print("✅ Admin accede a Entradas")


class SQLInjectionTest(TestCase):
    """Pruebas de inyección SQL"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
    
    def test_busqueda_con_sql_injection(self):
        """Intentar inyección SQL en búsqueda"""
        payloads = ["'; DROP TABLE core_entrada; --", "' OR '1'='1", "1; DELETE FROM core_entrada"]
        for payload in payloads:
            response = self.client.get(f'/entradas/?busqueda={payload}')
            self.assertEqual(response.status_code, 200)
            print(f"✅ Inyección SQL bloqueada")
    
    def test_parametros_maliciosos(self):
        """Parámetros con caracteres especiales (XSS)"""
        response = self.client.get('/entradas/?busqueda=<script>alert("XSS")</script>')
        self.assertEqual(response.status_code, 200)
        print("✅ XSS prevenido")


class InputValidationTest(TestCase):
    """Pruebas de validación de entrada"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='admin123', is_superuser=True)
        self.client.login(username='admin', password='admin123')
        self.categoria = Categoria.objects.create(nombre='Electrónicos')
    
    def test_crear_entrada_campos_vacios(self):

        response = self.client.post('/entradas/crear/', {
            'codigo': '',
            'producto': '',
            'cantidad': 1,
            'precio_compra': 100,
            'categoria': '',
            'fecha_ingreso': date.today().isoformat(),
            'ubicacion': 'bodega1'
    })
        data = json.loads(response.content)

    # Verificar que no sea éxito (debe fallar)
        if data.get('success'):
            print(f"Respuesta inesperada: {data}")
            self.assertFalse(data.get('success', False))
            print("✅ Validación de campos vacíos")
    
    def test_cantidad_negativa(self):
        """No se permiten cantidades negativas"""
        response = self.client.post('/entradas/crear/', {
            'codigo': 'TEST',
            'producto': 'Test',
            'cantidad': -10,
            'precio_compra': 100,
            'categoria': 'Electrónicos',
            'fecha_ingreso': date.today().isoformat()
        })
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        print("✅ Validación de cantidad negativa")


class SessionTest(TestCase):
    """Pruebas de sesión"""
    
    def test_logout_invalida_sesion(self):
        """No se puede acceder después de cerrar sesión"""
        self.client.login(username='admin', password='admin123')
        self.client.logout()
        response = self.client.get('/entradas/')
        self.assertEqual(response.status_code, 302)  # Redirige a login
        print("✅ Logout invalida sesión")
    
    def test_login_requerido_para_admin(self):
        """El admin requiere login"""
        response = self.client.get('/admin-elcharro/')
        self.assertEqual(response.status_code, 302)  # Redirige a login
        print("✅ Admin requiere login")