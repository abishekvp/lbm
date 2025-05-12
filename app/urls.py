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
    
    # functional
    path('library', views.library, name="library"),
    path('library/<str:lb>', views.library, name="library"),
    path('library/<str:lb>/<str:dept>', views.library, name="library"),
    path('library/<str:lb>/<str:dept>/<str:rack>', views.library, name="library"),
    path('library/<str:lb>/<str:dept>/<str:rack>/<int:book>', views.library, name="library"),

    path('download/<int:file_id>/', views.download_file, name='download-file'),

    # path('edit-library', views.edit_library, name="edit-library"),
    # path('edit-library/<str:lb>', views.edit_library, name="edit-library"),
    # path('edit-library/<str:lb>/<str:dept>', views.edit_library, name="edit-library"),
    # path('edit-library/<str:lb>/<str:dept>/<str:rack>', views.edit_library, name="edit-library"),
    # path('edit-library/<str:lb>/<str:dept>/<str:rack>/<int:book>', views.edit_library, name="edit-library"),


    path('delete/<str:lb>', views.delete),
    path('delete/<str:lb>/<str:dept>', views.delete),
    path('delete/<str:lb>/<str:dept>/<str:rack>', views.delete),
    path('delete/<str:lb>/<str:dept>/<str:rack>/<int:book>', views.delete),
    
    # pages
    path('index', views.index, name='index'),
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
]