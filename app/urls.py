from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="index"),
    path('index', views.dashboard, name="dashboard"),
    path('dashboard', views.dashboard, name="dashboard"),
    
    # auth
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    
    path('update-profile', views.update_profile, name="update-profile"),

    # functional
    path('library', views.library, name="library"),
    path('library/<str:lb>', views.library, name="library"),
    path('library/<str:lb>/<str:dept>', views.library, name="library"),
    path('library/<str:lb>/<str:dept>/<str:rack>', views.library, name="library"),
    path('library/<str:lb>/<str:dept>/<str:rack>/<int:book>', views.library, name="library"),

    path('library-meta', views.library_meta, name="library-meta"),

    path('search-books', views.search_books, name='search-books'),
    path('download/<int:file_id>', views.download_file, name='download-file'),

    path('books', views.books, name='books'),
    path('view-book/<int:book_id>', views.view_book),

    path('racks', views.racks, name='racks'),

    path('stocks', views.stocks, name='stocks'),

    path('edit-library', views.edit_library, name="edit-library"),
    path('edit-library/<str:lb>', views.edit_library, name="edit-library"),
    path('edit-library/<str:lb>/<str:dept>', views.edit_library, name="edit-library"),
    path('edit-library/<str:lb>/<str:dept>/<str:rack>', views.edit_library, name="edit-library"),
    path('edit-library/<str:lb>/<str:dept>/<str:rack>/<int:book>', views.edit_library, name="edit-library"),

    path('delete/<str:lb>', views.delete),
    path('delete/<str:lb>/<str:dept>', views.delete),
    path('delete/<str:lb>/<str:dept>/<str:rack>', views.delete),
    path('delete/<str:lb>/<str:dept>/<str:rack>/<int:book>', views.delete),

    # students
    path('students', views.students),
    path('student-detail/<int:student_id>', views.student_detail),
    path('approve-student/<int:stu_id>', views.approve_student),
    path('disable-student/<int:stu_id>', views.disable_student),
    path('delete-student/<int:stu_id>', views.delete_student),

    # book
    path('reject-book-request/<int:request_id>', views.reject_book_request),
    path('approve-book-request/<int:request_id>', views.approve_book_request),
    path('check-out-book/<int:request_id>', views.check_out_book),
    path('check-in-book/<int:request_id>', views.check_in_book),

    # ledger
    path('ledger', views.ledger),
    path('circulation-log', views.circulation_log),
    path('add-book-ledger-entry', views.add_book_ledger_entry),
    path('overdue', views.overdue),
    path('approved', views.approved),
    path('checked-out', views.checked_out),
    
    # pages
    path('ui_typography', views.ui_typography, name='ui_typography'),
    path('ui_colors', views.ui_colors, name='ui_colors'),
    path('ui_fontawesome', views.ui_fontawesome, name='ui_fontawesome'),
    path('ui_themify', views.ui_themify, name='ui_themify'),
    path('ui_buttons', views.ui_buttons, name='ui_buttons'),
    path('ui_cards', views.ui_cards, name='ui_cards'),
    path('ui_modals', views.ui_modals, name='ui_modals'),
    path('ui_toastr', views.ui_toastr, name='ui_toastr'),
    path('tb_basic', views.tb_basic, name='tb_basic'),
    path('tb_datatables', views.tb_datatables, name='tb_datatables'),
    path('fm_control', views.fm_control, name='fm_control'),
    path('fm_ckeditor_classic', views.fm_ckeditor_classic, name='fm_ckeditor_classic'),
    path('fm_ckeditor_balloon', views.fm_ckeditor_balloon, name='fm_ckeditor_balloon'),
    path('fm_ckeditor_block', views.fm_ckeditor_block, name='fm_ckeditor_block'),
    path('fm_ckeditor_inline', views.fm_ckeditor_inline, name='fm_ckeditor_inline'),
    path('fm_ckeditor_document', views.fm_ckeditor_document, name='fm_ckeditor_document'),
    path('ch_apexcharts', views.ch_apexcharts, name='ch_apexcharts'),
    path('pg_login', views.pg_login, name='pg_login'),

    # error pages
    path('404', views.error_404, name='error_404'),
    path('500', views.error_500, name='error_500'),
]