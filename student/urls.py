from django.urls import path
from student import views

urlpatterns = [
    path('', views.ledger),
    path('student', views.ledger),

    # ledger
    path('ledger', views.ledger),

    # functional
    path('library', views.library),
    path('library/<str:lb>', views.library),
    path('library/<str:lb>/<str:dept>', views.library),
    path('library/<str:lb>/<str:dept>/<str:rack>', views.library),
    path('library/<str:lb>/<str:dept>/<str:rack>/<int:book>', views.library),

    path('library-meta', views.library_meta),

    path('search-books', views.search_books),
    path('download/<int:file_id>', views.download_file),

    path('books', views.books),
    path('view-book/<int:book_id>', views.view_book),

    path('racks', views.racks),
]