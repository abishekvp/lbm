from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from app import models as md
from app import constants as const
from django.utils import timezone

def index(request):
    if request.user.is_authenticated:return redirect("dashboard")
    else:return redirect('signin')

def dashboard(request):
    if request.user.is_authenticated:
        data = dict()
        data['total_books'] = md.Book.objects.count()
        data['total_racks'] = md.Rack.objects.count()
        data['total_department'] = md.Department.objects.count()
        data['total_library'] = md.Library.objects.count()
        today = timezone.now().date()
        data['today_updated_books'] = md.Book.objects.filter(updated__date=today)
        data['last_updated_books'] = md.Book.objects.order_by('-updated')[:3]
        return render(request,'dashboard.html', data)
    else:
        return redirect('signin')

# functional units
def library(request, lb=None, dept=None, rack=None, book=None):
    import base64
    if lb:
        if dept:
            if rack:
                if book:
                    book = md.Book.objects.get(id=book)
                    if book.image:
                        book.base64_image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
                    else:
                        book.base64_image = None
                    return render(request, 'book-detail.html', {'book': book, 'library_name': lb, 'department_name': dept, 'rack_name': rack})

                if request.method == const.POST:
                    book_name = str(request.POST.get('book-name')).strip()
                    author_name = str(request.POST.get('author-name')).strip()
                    publication_name = str(request.POST.get('publication-name')).strip()
                    release_date = str(request.POST.get('release-date')).strip()
                    book_file = request.FILES.get('book-file')
                    if book_file:
                        book_file = md.File.objects.create(
                            name=book_file.name,
                            file=book_file.read(),
                        )
                    book_image = request.FILES.get('book-image')
                    if book_image:
                        book_image = md.Image.objects.create(
                            name=book_image.name,
                            image=book_image.read(),
                            extension=book_image.name.split('.')[-1]
                        )
                    rack_obj = md.Rack.objects.get(department__library__name=lb, department__name=dept, name=rack)
                    book_obj = dict()
                    book_obj['name'] = book_name
                    book_obj['author'] = author_name
                    book_obj['publication'] = publication_name
                    book_obj['release'] = release_date
                    book_obj['file'] = book_file
                    book_obj['image'] = book_image
                    book_obj['rack'] = rack_obj
                    md.Book.objects.create(**book_obj)
                books = md.Book.objects.filter(rack__department__library__name=lb, rack__department__name=dept, rack__name=rack)
                for book in books:
                    if book.image:
                        book.base64_image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
                    else:
                        book.base64_image = None
                return render(request, 'book.html', {'books': books, 'library_name': lb, 'department_name': dept, 'rack_name': rack})

            if request.method == const.POST:
                rack_name = str(request.POST.get('rack-name')).strip()
                if not rack_name.isalpha():
                    return JsonResponse({'status': 403, 'message': 'Rack name must contain only alphabetic characters'})
                rack_name = "RK-" + rack_name.upper().replace(' ', '-')
                if md.Rack.objects.filter(department__library__name=lb, department__name=dept, name=rack_name).exists():
                    return JsonResponse({'status': 403, 'message': 'Rack already exists!'})
                if rack_name:
                    department = md.Department.objects.get(name=dept, library__name=lb)
                    md.Rack.objects.create(name=rack_name, department=department)
                else:
                    return JsonResponse({'status': 403, 'message': 'Unable to create rack!'})
            racks = md.Rack.objects.filter(department__library__name=lb, department__name=dept)
            return render(request, 'rack.html', {'racks': racks, 'library_name': lb, 'department_name': dept})
        
        if request.method == const.POST:
            department_name = str(request.POST.get('department-name')).strip()
            if not department_name.isalpha():
                return JsonResponse({'status': 403, 'message': 'Department name must contain only alphabetic characters'})
            department_name = "DEPT-" + department_name.upper().replace(' ', '-')
            if md.Department.objects.filter(name=department_name, library__name=lb).exists():
                return JsonResponse({'status': 403, 'message': 'Department already exists!'})
            if department_name:
                library = md.Library.objects.get(name=lb)
                md.Department.objects.create(name=department_name, library=library)
            else:
                return JsonResponse({'status': 403, 'message': 'Unable to create department!'})
        departments = md.Department.objects.filter(library__name=lb)
        return render(request, 'department.html', {'departments': departments, 'library_name': lb})
    
    if request.method == const.POST:
        library_name = str(request.POST.get('library-name')).strip()
        if not library_name.isalpha():
            return JsonResponse({'status': 403, 'message': 'Library name must contain only alphabetic characters'})
        library_name = "LB-" + library_name.upper().replace(' ', '-')
        if md.Library.objects.filter(name=library_name).exists():
            libraries = md.Library.objects.all()
            return render(request, 'library.html', {'libraries': libraries, 'message': 'Library already exists!'})
        if library_name:
            md.Library.objects.create(name=library_name)
        else:
            return JsonResponse({'status': 403, 'message': 'Unable to create library!'})
    libraries = md.Library.objects.all()
    return render(request, 'library.html', {'libraries': libraries})

def download_file(request, file_id):
    try:
        file_obj = md.File.objects.get(pk=file_id)
        response = HttpResponse(file_obj.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
        return response
    except md.File.DoesNotExist:
        raise Http404("File not found")

def delete(request, lb=None, dept=None, rack=None, book=None):
    if lb:
        if dept:
            if rack:
                if book:
                    md.Book.objects.filter(id=book).delete()
                    return redirect(f'/library/{lb}/{dept}/{rack}')
                else:
                    md.Rack.objects.filter(name=rack).delete()
                    return redirect(f'/library/{lb}/{dept}')
            else:
                md.Department.objects.filter(name=dept).delete()
                return redirect(f'/library/{lb}')
        else:
            md.Library.objects.filter(name=lb).delete()
            return redirect(f'/library')
    return redirect('library')

# auth units
def signup(request):
    if request.method == 'POST':
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        if username and email and password:
            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                user = User.objects.create_user(username, email, password)
                user.save()
                messages.success(request, 'Account created successfully')
                return redirect('signin')
            else:
                messages.error(request, 'Username or Email already exists')
                return redirect('signin')
        else:
            messages.error(request, 'Please fill all the fields to create an account')
    return render(request,'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials Please try again')
    return render(request,'signin.html')

def signout(request):
    if request.user.is_authenticated: logout(request)
    return redirect('signin')

def ui_typography(request):
    return render(request, 'ui_typography.html')

def ui_colors(request):
    return render(request, 'ui_colors.html')

def ui_fontawesome(request):
    return render(request, 'ui_fontawesome.html')

def ui_themify(request):
    return render(request, 'ui_themify.html')

def ui_buttons(request):
    return render(request, 'ui_buttons.html')

def ui_cards(request):
    return render(request, 'ui_cards.html')

def ui_modals(request):
    return render(request, 'ui_modals.html')

def ui_toastr(request):
    return render(request, 'ui_toastr.html')

def tb_basic(request):
    return render(request, 'tb_basic.html')

def tb_datatables(request):
    return render(request, 'tb_datatables.html')

def fm_control(request):
    return render(request, 'fm_control.html')

def fm_ckeditor_classic(request):
    return render(request, 'fm_ckeditor_classic.html')

def fm_ckeditor_balloon(request):
    return render(request, 'fm_ckeditor_balloon.html')

def fm_ckeditor_block(request):
    return render(request, 'fm_ckeditor_block.html')

def fm_ckeditor_inline(request):
    return render(request, 'fm_ckeditor_inline.html')

def fm_ckeditor_document(request):
    return render(request, 'fm_ckeditor_document.html')

def ch_apexcharts(request):
    return render(request, 'ch_apexcharts.html')

def pg_login(request):
    return render(request, 'pg_login.html')
