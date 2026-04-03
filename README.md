# Bookstore Inventory API

API REST para sistema de gestión de inventario de librerías, diseñada de la manera más específica y sencilla sin utilizar base de datos real (opera en memoria sobre una lista preestablecida que simula el JSON).

## Requisitos Previos

- Python 3.12 (o superior)
- Docker y Docker Compose (Opcional, para ejecución dockerizada)

## Instalación y Ejecución Local (Usando entorno virtual)

1. Clonar este repositorio.
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   ```
3. Activar el entorno virtual:
   - En Windows: `venv\Scripts\activate`
   - En Linux/Mac: `source venv/bin/activate`
4. Instalar las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```
5. Renombrar `.env.example` a `.env` o asegurarse de que las variables de entorno están cargadas.
6. Ejecutar el servidor usando Uvicorn:
   ```bash
   uvicorn bookstore.asgi:application --reload
   ```
La API estará disponible en `http://127.0.0.1:8000/`

## Instalación y Ejecución (Usando Docker)


1. Ejecutar el contenedor mediante Docker Compose:
   ```bash
   docker-compose up --build
   ```
La API estará disponible en `http://localhost:8000/`.

## Colección de Postman

Se incluye el archivo `Bookstore.postman_collection.json` en la raíz del proyecto.

## Ejemplos de uso de los Endpoints

# 1. Listar todos los libros / Crear un libro
**GET** `/books` o **GET** `/books?page=1&limit=10`
Devuelve la lista de libros precargados en memoria. Si se envían `page` y `limit`, la respuesta tendrá el formato `{"page": 1, "limit": 10, "total": 3, "data": [...]}`.

**POST** `/books`
Crea un nuevo libro.
{
    "title": "Don Quijote de la Mancha",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": 15.99,
    "stock_quantity": 25,
    "category": "Literatura Clásica",
    "supplier_country": "ES"
}

# 2. Obtener / Actualizar / Eliminar por ID
**GET** `/books/{id}` -> Retorna el detalle del libro.
**PUT** `/books/{id}` -> Actualiza la información del libro, pasando en el body los datos en JSON.
**DELETE** `/books/{id}` -> Elimina un libro.

# 3. Buscar por categoría
**GET** `/books/search?category=clásica`
Devuelve la lista de libros cuya categoría coincida con la búsqueda.

# 4. Consultar libros con bajo stock
**GET** `/books/low-stock?threshold=10`
Devuelve los libros cuya cantidad en stock sea menor o igual a 10.

# 5. Calcular Precio
**POST** `/books/{id}/calculate-price`
Se conecta con la API de tasas de cambio para calcular el precio aplicando el 40% de margen. Siempre realiza el cálculo convirtiendo (si aplicara) o simplemente basándose en la tasa de USD.
No requiere cuerpo en la petición (Body vacío).

Respuesta Esperada:
{
    "book_id": 1,
    "cost_usd": 15.99,
    "exchange_rate": 1.0,
    "cost_local": 15.99,
    "margin_percentage": 40,
    "selling_price_local": 22.39,
    "currency": "USD",
    "calculation_timestamp": "2025-01-15T10:30:00+00:00"
}
