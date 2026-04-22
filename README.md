# Autor: Paulo Nicolas Santos Zuasnabar
# EcommerceEmp - Tienda de Música

Aplicación de ecommerce completa desarrollada con Django REST Framework y React que permite gestionar inventarios de álbumes musicales con carrito de compras funcional.

## Características

- **API REST completa** con Django para gestión de productos y carrito
- **Frontend React** con React Query v5 para gestión de estado
- **Carrito de compras funcional** con procesamiento de compras
- **Gestión de inventario** con control de stock en tiempo real
- **Sistema de categorías** con filtrado por categoría
- **Búsqueda y filtros** avanzados
- **Elementos de marketing** (promociones y descuentos)
- **Sistema de recomendaciones** basado en rating
- **Interfaz responsiva** optimizada para móviles
- **Prefetch de datos** para navegación fluida

## Vistas Implementadas

1. **Home** - Lista productos con búsqueda, filtros y recomendaciones
2. **Categorías** - Lista todas las categorías disponibles
3. **Productos por Categoría** - Productos filtrados por categoría
4. **Detalle Producto** - Información completa del producto
5. **Carrito** - Gestión completa del carrito con checkout funcional
6. **Inventario** - Panel administrativo para gestión de stock

## Tecnologías

### Backend
- Django 5.2.8
- Django REST Framework
- Django CORS Headers
- SQLite (base de datos)

### Frontend
- React 18
- React Query v5 (TanStack Query)
- CSS3 con diseño responsivo

## Instalación

### Backend (Django)
```bash
# Crear ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install django djangorestframework django-cors-headers

# Ejecutar migraciones
cd API
python manage.py makemigrations
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

## API Endpoints

### Productos
- `GET /api/albums/` - Listar todos los productos
- `GET /api/albums/{id}/` - Detalle de producto
- `GET /api/albums/?categoria={id}` - Productos por categoría

### Categorías
- `GET /api/categorias/` - Listar categorías

### Carrito
- `GET /api/carrito/` - Obtener carrito actual
- `POST /api/carrito/` - Agregar producto al carrito
- `PUT /api/carrito/{id}/` - Actualizar cantidad
- `DELETE /api/carrito/{id}/` - Eliminar item del carrito
- `DELETE /api/carrito/` - Procesar compra (checkout)

## Funcionalidades Avanzadas

### React Query v5
- **Optimistic Updates**: Actualizaciones inmediatas en la UI
- **Rollback automático**: Reversión en caso de errores
- **Invalidación de caché**: Sincronización automática
- **Prefetch**: Carga anticipada de datos al hover

### Gestión de Carrito
- Agregar/eliminar productos
- Actualizar cantidades con validación de stock
- Procesamiento de compras con reducción de inventario
- Persistencia por sesión

### Sistema de Inventario
- Control de stock en tiempo real
- Alertas de stock bajo/agotado
- Actualización automática post-compra
- Panel administrativo

## Uso

1. Ejecutar el backend en `http://localhost:8000`
2. Ejecutar el frontend en `http://localhost:3000`
3. Navegar por las categorías y productos
4. Agregar productos al carrito
5. Procesar compras que actualizan el inventario

## Estructura del Proyecto

```
ecommerceEmp/
├── API/                          # Backend Django
│   ├── vinyl/                    # App principal
│   │   ├── models.py            # Modelos (Album, Categoria, CarritoItem)
│   │   ├── views.py             # Vistas de API
│   │   ├── serializers.py       # Serializers DRF
│   │   └── urls.py              # URLs de API
│   └── manage.py
├── frontend/                     # Frontend React
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   ├── hooks/               # Hooks personalizados
│   │   ├── services/            # Servicios API
│   │   └── App.js               # Componente principal
│   └── package.json
└── README.md
```

## Características Técnicas

- **Responsivo**: Adaptable a móviles, tablets y desktop
- **Optimizado**: Prefetch y caché inteligente
- **Robusto**: Manejo de errores y estados de carga
- **Escalable**: Arquitectura modular y reutilizable
