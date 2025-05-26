from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.models import Group
import base64
from app import constants as const
from django.contrib.auth.models import User
from django.shortcuts import render
from app import models as md
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.

@login_required
def index(request):
    ledger = md.Ledger.objects.filter(user=request.user)
    return render(request, 'student/ledger.html', {'ledger': ledger})


def books(request):
    return render(request, 'student/ledger.html')

def student_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='student').exists():
            return redirect('/index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def ledger(request):
    ledger = md.Ledger.objects.filter(user=request.user)
    return render(request, 'student/ledger.html', {'ledger': ledger})

@login_required
def library(request, lb=None, dept=None, rack=None, book=None):
    if lb:
        if dept:
            if rack:
                if book:
                    book = md.Book.objects.get(id=book)
                    if book.image:
                        book.base64_image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
                    else:
                        book.base64_image = None
                    return render(request, 'student/book-detail.html', {'book': book, 'library_name': lb, 'department_name': dept, 'rack_name': rack})
                books = md.Book.objects.filter(rack__department__library__name=lb, rack__department__name=dept, rack__name=rack)
                for book in books:
                    if book.image:
                        book.base64_image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
                    else:
                        book.base64_image = None
                return render(request, 'student/book.html', {'books': books, 'library_name': lb, 'department_name': dept, 'rack_name': rack})
            racks = md.Rack.objects.filter(department__library__name=lb, department__name=dept)
            return_data = render(request, 'student/rack.html', {'racks': racks, 'library_name': lb, 'department_name': dept})
            return return_data
        departments = md.Department.objects.filter(library__name=lb)
        return render(request, 'student/department.html', {'departments': departments, 'library_name': lb})
    libraries = md.Library.objects.all()
    return render(request, 'student/library.html', {'libraries': libraries})

# functional units
@login_required
def search_books(request):
    query_string = str(request.GET.get('query')).strip()
    books = md.Book.objects.filter(
        Q(name__icontains=query_string) |
        Q(author__icontains=query_string) |
        Q(publication__icontains=query_string) |
        Q(release__icontains=query_string) |
        Q(rack__name__icontains=query_string) |
        Q(rack__department__name__icontains=query_string) |
        Q(rack__department__library__name__icontains=query_string)
    )
    books_list = []
    for book in books:
        if book.image:
            image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
        else:
            image = None
        books_list.append({
            'id': book.id,
            'image': image,
            'name': book.name,
            'author': book.author,
            'publication': book.publication,
            'release': str(book.release),
            'library': book.rack.department.library.name,
            'department': book.rack.department.name,
            'rack': book.rack.name
        })
    return JsonResponse({'status': 200, 'books': books_list})

def library_meta(request):
    # Build a list of libraries, each with id, name, and departments
    libraries = []
    for library in md.Library.objects.all():
        library_data = {
            'id': library.id,
            'name': library.name,
            # add more library fields if needed
            'departments': []
        }
        departments = md.Department.objects.filter(library=library)
        for department in departments:
            department_data = {
                'id': department.id,
                'name': department.name,
                # add more department fields if needed
                'racks': []
            }
            racks = md.Rack.objects.filter(department=department)
            for rack in racks:
                rack_data = {
                    'id': rack.id,
                    'name': rack.name,
                    # add more rack fields if needed
                }
                department_data['racks'].append(rack_data)
            library_data['departments'].append(department_data)
        libraries.append(library_data)
    library_dict = {'libraries': libraries}
    return JsonResponse(library_dict)

def view_book(request, book_id):
    try:
        book = md.Book.objects.get(pk=book_id)
        if book.image:
            book.base64_image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
        else:
            book.base64_image = None
        return render(request, 'student/book-detail.html', {'book': book})
    except md.Book.DoesNotExist:
        raise Http404("Book not found")

def racks(request):
    racks = md.Rack.objects.all()
    depts = md.Department.objects.all()
    return_data = render(request, 'student/racks.html', {'racks': racks, 'departments': depts})
    if request.method == const.POST:
        rack_name = str(request.POST.get('rack-name')).strip()
        if not rack_name.isalpha():
            messages.error(request, 'Rack name must contain only alphabetic characters')
            return return_data
        rack_name = "RK-" + rack_name.upper().replace(' ', '-')
        if md.Rack.objects.filter(name=rack_name).exists():
            messages.error(request, 'Rack already exists!')
            return return_data
        if rack_name:
            department = md.Department.objects.get(id=request.POST.get('department'))
            md.Rack.objects.create(name=rack_name, department=department)
            return return_data
        else:
            messages.error(request, 'Unable to create rack!')
            return return_data
    return return_data

@login_required
def download_file(request, file_id):
    try:
        file_obj = md.File.objects.get(pk=file_id)
        response = HttpResponse(file_obj.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
        return response
    except md.File.DoesNotExist:
        raise Http404("File not found")

def books(request):
    if request.method == const.POST:
        book_name = str(request.POST.get('book-name')).strip()
        author_name = str(request.POST.get('author-name')).strip()
        publication_name = str(request.POST.get('publication-name')).strip()
        release_date = str(request.POST.get('release-date')).strip()
        rack = md.Rack.objects.get(name=request.POST.get('rack'))
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
        book_obj = dict()
        book_obj['name'] = book_name
        book_obj['author'] = author_name
        book_obj['publication'] = publication_name
        book_obj['release'] = release_date
        book_obj['rack'] = rack
        book_obj['file'] = book_file
        book_obj['image'] = book_image
        md.Book.objects.create(**book_obj)
    books = md.Book.objects.all()
    for book in books:
        if book.image:
            book.base64_image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
        else:
            book.base64_image = None
    lbs = md.Library.objects.all()
    depts = md.Department.objects.all()
    racks = md.Rack.objects.all()
    return render(request, 'student/books.html', {'books': books, 'libraries': lbs, 'departments': depts, 'racks': racks})


def request_book(request):
    isbn = request.POST.get('isbn')
    checkout_date = request.POST.get('checkout-date')
    checkin_date = request.POST.get('checkin-date')
    book_obj = md.Stock.objects.filter(isbn=isbn)
    book = dict()
    profile = md.Profile.objects.get(user=request.user)
    book['user'] = request.user
    book['isbn'] = isbn
    book['roll_no'] = profile.roll
    book['checkout_date'] = checkout_date
    book['checkin_date'] = checkin_date
    book['is_pending'] = True
    if book_obj:
        book['book'] = book_obj
    md.Ledger.objects.create(
        **book
    )
    return redirect('/student/ledger')