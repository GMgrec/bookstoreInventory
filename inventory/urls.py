from django.urls import path
from . import views

# Se definen las rutas de la API
urlpatterns = [
    path('books', views.book_list_create, name='book-list-create'),
    path('books/search', views.book_search, name='book-search'),
    path('books/low-stock', views.book_low_stock, name='book-low-stock'),
    path('books/<int:book_id>', views.book_detail, name='book-detail'),
    path('books/<int:book_id>/calculate-price', views.calculate_price, name='calculate-price'),
]
