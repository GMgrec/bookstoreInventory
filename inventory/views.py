import json
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

from .services import ExchangeRateService

# Array de objetos para simular registros de BD de libros.
books_db = [
    {
        "id": 1,
        "title": "El Quijote",
        "author": "Miguel de Cervantes",
        "isbn": "978-84-376-0494-7",
        "cost_usd": 15.99,
        "selling_price_local": None,
        "stock_quantity": 25,
        "category": "Literatura Clásica",
        "supplier_country": "ES",
        "created_at": "2025-01-15T10:30:00Z",
        "updated_at": "2025-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "title": "Cien Años de Soledad",
        "author": "Gabriel García Márquez",
        "isbn": "978-03-074-7472-8",
        "cost_usd": 18.50,
        "selling_price_local": None,
        "stock_quantity": 10,
        "category": "Realismo Mágico",
        "supplier_country": "CO",
        "created_at": "2025-01-15T11:00:00Z",
        "updated_at": "2025-01-15T11:00:00Z"
    },
    {
        "id": 3,
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-04-515-2493-5",
        "cost_usd": 12.99,
        "selling_price_local": None,
        "stock_quantity": 5,
        "category": "Ciencia Ficción",
        "supplier_country": "UK",
        "created_at": "2025-01-15T12:00:00Z",
        "updated_at": "2025-01-15T12:00:00Z"
    }
]

# Función para obtener la fecha y hora actual en formato ISO
def current_time_iso():
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Función para limpiar el ISBN
def clean_isbn(isbn):
    return "".join(c for c in isbn if c.isdigit() or c.upper() == 'X')

# Función para validar los datos del libro
def validate_book_data(data, book_id=None):
    cost_usd = data.get("cost_usd")
    if cost_usd is None or float(cost_usd) <= 0:
        return {"error": "cost_usd debe ser mayor a 0"}

    stock_quantity = data.get("stock_quantity")
    if stock_quantity is None or int(stock_quantity) < 0:
        return {"error": "stock_quantity no puede ser negativo"}

    isbn = str(data.get("isbn", ""))
    cleaned = clean_isbn(isbn)
    if len(cleaned) not in [10, 13]:
        return {"error": "isbn debe tener formato válido (10 o 13 dígitos)."}

    # Duplicate check
    for b in books_db:
        if b["isbn"] == data.get("isbn") and b["id"] != book_id:
            return {"error": "No se permiten libros duplicados (mismo ISBN)."}

    return None

@csrf_exempt
# Función para listar y crear libros, diferencia por los metodos del request
def book_list_create(request):
    if request.method == 'GET':
        # Obtiene los parámetros de paginación
        page = request.GET.get('page')
        limit = request.GET.get('limit', 10)
        
        if page:
            try:
                page = int(page)
                limit = int(limit)
                start_index = (page - 1) * limit
                end_index = start_index + limit
                paginated_books = books_db[start_index:end_index]
                return JsonResponse({"page": page, "limit": limit, "total": len(books_db), "data": paginated_books}, status=200)
            except ValueError:
                return JsonResponse({"error": "Parámetros de paginación inválidos"}, status=400)
                
        return JsonResponse(books_db, safe=False, status=200)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "JSON inválido"}, status=400)
        
        # Valida los datos del libro
        error = validate_book_data(data)
        if error:
            return JsonResponse(error, status=400)
        
        # Genera un nuevo ID para el libro
        new_id = max((b["id"] for b in books_db), default=0) + 1
        
        # Crea el nuevo libro
        new_book = {
            "id": new_id,
            "title": data.get("title", ""),
            "author": data.get("author", ""),
            "isbn": data.get("isbn", ""),
            "cost_usd": float(data.get("cost_usd", 0)),
            "selling_price_local": None,
            "stock_quantity": int(data.get("stock_quantity", 0)),
            "category": data.get("category", ""),
            "supplier_country": data.get("supplier_country", ""),
            "created_at": current_time_iso(),
            "updated_at": current_time_iso()
        }
        books_db.append(new_book)
        return JsonResponse(new_book, status=201)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
# Función para obtener, actualizar y eliminar libros por ID
def book_detail(request, book_id):
    book = next((b for b in books_db if b["id"] == book_id), None)
    if not book:
        return JsonResponse({"error": "Libro no encontrado"}, status=404)

    if request.method == 'GET':
        return JsonResponse(book, status=200)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "JSON inválido"}, status=400)
            
        error = validate_book_data(data, book_id=book_id)
        if error:
            return JsonResponse(error, status=400)

        book["title"] = data.get("title", book["title"])
        book["author"] = data.get("author", book["author"])
        book["isbn"] = data.get("isbn", book["isbn"])
        book["cost_usd"] = float(data.get("cost_usd", book["cost_usd"]))
        book["stock_quantity"] = int(data.get("stock_quantity", book["stock_quantity"]))
        book["category"] = data.get("category", book["category"])
        book["supplier_country"] = data.get("supplier_country", book["supplier_country"])
        book["updated_at"] = current_time_iso()
        
        return JsonResponse(book, status=200)

    elif request.method == 'DELETE':
        books_db.remove(book)
        return JsonResponse({}, status=204)

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
# Función para buscar libros por categoría
def book_search(request):
    if request.method == 'GET':
        category = request.GET.get('category', '').lower()
        if not category:
            return JsonResponse({"error": "El parámetro category es requerido"}, status=400)
        
        results = [b for b in books_db if category in b.get("category", "").lower()]
        return JsonResponse(results, safe=False, status=200)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
# Función para buscar libros con bajo stock
def book_low_stock(request):
    if request.method == 'GET':
        try:
            threshold = int(request.GET.get('threshold', 10))
        except ValueError:
            return JsonResponse({"error": "El threshold debe ser un número entero"}, status=400)
            
        results = [b for b in books_db if b.get("stock_quantity", 0) <= threshold]
        return JsonResponse(results, safe=False, status=200)
        
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
# Función para calcular el precio de venta del libro
def calculate_price(request, book_id):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    book = next((b for b in books_db if b["id"] == book_id), None)
    if not book:
        return JsonResponse({"error": "Libro no encontrado"}, status=404)
    # Se usa USD como moneda por defecto
    currency = "USD"

    # Se crea una instancia del servicio de tasas de cambio
    service = ExchangeRateService()
    try:
        # Se calcula el precio de venta del libro
        result = service.calculate_selling_price(book, currency)
        
        # Actualiza el precio de venta en la base de datos
        book["selling_price_local"] = result["selling_price_local"]
        book["updated_at"] = current_time_iso()
        
        return JsonResponse(result, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
