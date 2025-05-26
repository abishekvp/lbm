from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from app import models as md
from app import constants as const
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import base64
from django.contrib.auth.models import Group

def index(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='student').exists():
            return redirect('/student')
        return redirect("/dashboard")
    else: return redirect('/signin')

def student_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='student').exists():
            return redirect('/index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='admin').exists():
            return redirect('/student')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@admin_required
def dashboard(request):
    data = dict()
    data['total_books'] = md.Book.objects.count()
    data['total_racks'] = md.Rack.objects.count()
    data['total_department'] = md.Department.objects.count()
    data['total_library'] = md.Library.objects.count()
    today = timezone.now().date()
    data['today_updated_books'] = md.Book.objects.filter(updated__date=today)
    data['last_updated_books'] = md.Book.objects.order_by('-updated')[:3]
    return render(request,'dashboard.html', data)

@login_required
@admin_required
def stocks(request):
    data = dict()
    data['total_books'] = md.Book.objects.count()
    data['total_racks'] = md.Rack.objects.count()
    data['total_department'] = md.Department.objects.count()
    data['total_library'] = md.Library.objects.count()
    today = timezone.now().date()
    data['today_updated_books'] = md.Book.objects.filter(updated__date=today)
    data['last_updated_books'] = md.Book.objects.order_by('-updated')[:3]
    return render(request,'stocks.html', data)

# functional units
@login_required
@admin_required
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

@login_required
@admin_required
def library(request, lb=None, dept=None, rack=None, book=None):
    if lb:
        if dept:
            if rack:
                if book:
                    if request.method == const.POST:
                        book_name = str(request.POST.get('book-name')).strip()
                        author_name = str(request.POST.get('author-name')).strip()
                        publication_name = str(request.POST.get('publication-name')).strip()
                        release_date = str(request.POST.get('release-date')).strip()
                        try:
                            library = md.Library.objects.get(id=request.POST.get('library_name'))
                            department = md.Department.objects.get(id=request.POST.get('department_name'))
                            rack = md.Rack.objects.get(id=request.POST.get('rack_name'))
                        except md.Library.DoesNotExist:
                            rack = None
                            pass

                        book_image = request.FILES.get('book-image')
                        book = md.Book.objects.get(id=book)
                        if book_image:
                            book.image.name = book_image.name
                            book.image.image = book_image.read()
                            book.image.extension = book_image.name.split('.')[-1]
                            book.image.save()
                        if book_name:
                            book.name = book_name
                        if author_name:
                            book.author = author_name
                        if publication_name:
                            book.publication = publication_name
                        if release_date:
                            book.release = release_date
                        if rack:
                            book.rack = rack
                        book.save()
                        return redirect(f'/library/{book.rack.department.library.name}/{book.rack.department.name}/{book.rack.name}/{book.id}')
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
                    messages.warning(request, 'Rack name must contain only alphabetic characters')
                rack_name = "RK-" + rack_name.upper().replace(' ', '-')
                if md.Rack.objects.filter(department__library__name=lb, department__name=dept, name=rack_name).exists():
                    messages.warning(request, 'Rack already exists!')
                elif rack_name:
                    department = md.Department.objects.get(name=dept, library__name=lb)
                    md.Rack.objects.create(name=rack_name, department=department)
                else:
                    messages.error(request, 'Unable to create rack!')
            racks = md.Rack.objects.filter(department__library__name=lb, department__name=dept)
            return_data = render(request, 'rack.html', {'racks': racks, 'library_name': lb, 'department_name': dept})
            return return_data
        
        if request.method == const.POST:
            department_name = str(request.POST.get('department-name')).strip()
            if not department_name.isalpha():
                messages.warning(request, 'Department name must contain only alphabetic characters')
            department_name = "DEPT-" + department_name.upper().replace(' ', '-')
            if md.Department.objects.filter(name=department_name, library__name=lb).exists():
                messages.warning(request, 'Department already exists!')
            elif department_name:
                library = md.Library.objects.get(name=lb)
                md.Department.objects.create(name=department_name, library=library)
            else:
                messages.error(request, 'Unable to create department!')
        departments = md.Department.objects.filter(library__name=lb)
        return render(request, 'department.html', {'departments': departments, 'library_name': lb})
    
    if request.method == const.POST:
        library_name = str(request.POST.get('library-name')).strip()
        if not library_name.isalpha():
            messages.warning(request, 'Library name must contain only alphabetic characters')
        library_name = "LB-" + library_name.upper().replace(' ', '-')
        if md.Library.objects.filter(name=library_name).exists():
            libraries = md.Library.objects.all()
            messages.warning('Library already exists!')
            return render(request, 'library.html', {'libraries': libraries})
        elif library_name:
            md.Library.objects.create(name=library_name)
        else:
            messages.error(request, 'Unable to create library!')
    libraries = md.Library.objects.all()
    return render(request, 'library.html', {'libraries': libraries})

# book
@admin_required
def reject_book_request(request, request_id):
    book_req = md.Ledger.objects.get(id=request_id)
    book_req.is_rejected = True
    book_req.is_approved = False
    book_req.is_pending = False
    book_req.is_checked_in = False
    book_req.is_checked_out = False
    date_now = timezone.now().date()
    book_req.rejected_date = date_now
    book_req.save()
    return redirect('/ledger')

@admin_required
def approve_book_request(request, request_id):
    book_req = md.Ledger.objects.get(id=request_id)
    book_req.is_rejected = False
    book_req.is_approved = True
    book_req.is_pending = False
    book_req.is_checked_in = False
    book_req.is_checked_out = False
    date_now = timezone.now().date()
    book_req.approved_date = date_now
    book_req.save()
    return redirect('/ledger')

def check_out_book(request, request_id):
    book_req = md.Ledger.objects.get(id=request_id)
    book_req.is_checked_in = False
    book_req.is_checked_out = True
    date_now = timezone.now().date()
    book_req.checkout_date = date_now
    book_req.save()
    return redirect('/ledger')

def check_in_book(request, request_id):
    book_req = md.Ledger.objects.get(id=request_id)
    book_req.is_checked_in = True
    book_req.is_checked_out = True
    date_now = timezone.now().date()
    book_req.checkin_date = date_now
    book_req.save()
    return redirect('/ledger')

@admin_required
def edit_library(request, lb=None, dept=None, rack=None, book=None):
    if lb:
        if dept:
            if rack:
                if book:
                    if request.method == const.POST:
                        book_name = str(request.POST.get('book-name')).strip()
                        author_name = str(request.POST.get('author-name')).strip()
                        publication_name = str(request.POST.get('publication-name')).strip()
                        release_date = str(request.POST.get('release-date')).strip()
                        library = md.Library.objects.get(id=request.POST.get('library_name'))
                        department = md.Department.objects.get(id=request.POST.get('department_name'))
                        rack = md.Rack.objects.get(id=request.POST.get('rack_name'))
                        book_image = request.POST.get('book-image')
                        book = md.Book.objects.get(id=book)
                        if book_image:
                            book.image.name = book_image.name
                            book.image.image = book_image.read()
                            book.image.extension = book_image.name.split('.')[-1]
                            book.image.save()
                        book.name = book_name
                        book.author = author_name
                        book.publication = publication_name
                        book.release = release_date
                        book.rack.department.library = library
                        book.rack.department = department
                        book.rack = rack
                        book.rack.department.library.save()
                        book.rack.department.save()
                        book.rack.save()
                        book.save()
                        return redirect(f'/library/{library.name}/{department.name}/{rack.name}/{book.id}')
                    return render(request, 'book-detail.html', {'book': book, 'library_name': lb, 'department_name': dept, 'rack_name': rack})
                if request.method == const.POST:
                    library = md.Library.objects.get(name=request.POST.get('library_name'))
                    department = md.Department.objects.get(name=request.POST.get('department_name'), library=library)
                    rack = md.Rack.objects.get(department__library__name=lb, department__name=dept, name=rack)
                    rack.department = department
                    rack_name = str(request.POST.get('rack-name')).strip()
                    if not rack_name.isalpha():
                        messages.warning(request, 'Rack name must contain only alphabetic characters')
                    else:
                        rack_name = "RK-" + rack_name.upper().replace(' ', '-')
                    if md.Rack.objects.filter(department__library__name=lb, department__name=dept, name=rack_name).exists():
                        messages.warning(request, 'Rack already exists!')
                    elif rack_name:
                        rack.name = rack_name
                        rack.save()
                        return redirect(f'/library/{library.name}/{department.name}/{rack.name}')
                    else:
                        messages.error(request, 'Unable to create rack!')
                return render(request, 'edit-rack.html')
            return render(request, 'edit-department.html')
        return render(request, 'edit-library.html')
    return redirect('/')

@admin_required
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

@admin_required
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
    return render(request, 'books.html', {'books': books, 'libraries': lbs, 'departments': depts, 'racks': racks})

def view_book(request, book_id):
    try:
        book = md.Book.objects.get(pk=book_id)
        if book.image:
            book.base64_image = f"data:image/{book.image.extension};base64," + base64.b64encode(book.image.image).decode('utf-8')
        else:
            book.base64_image = None
        return render(request, 'book-detail.html', {'book': book})
    except md.Book.DoesNotExist:
        raise Http404("Book not found")

def racks(request):
    racks = md.Rack.objects.all()
    depts = md.Department.objects.all()
    return_data = render(request, 'racks.html', {'racks': racks, 'departments': depts})
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

@login_required
@admin_required
def delete(request, lb=None, dept=None, rack=None, book=None):
    if lb:
        if dept:
            if rack:
                if book:
                    md.Book.objects.filter(id=book).delete()
                    messages.info(request, "Book successfully deleted")
                    return redirect(f'/library/{lb}/{dept}/{rack}')
                else:
                    md.Rack.objects.filter(name=rack).delete()
                    messages.info(request, "Rack successfully deleted")
                    return redirect(f'/library/{lb}/{dept}')
            else:
                md.Department.objects.filter(name=dept).delete()
                messages.info(request, "Department successfully deleted")
                return redirect(f'/library/{lb}')
        else:
            md.Library.objects.filter(name=lb).delete()
            messages.info(request, "Library successfully deleted")
            return redirect(f'/library')
    return redirect('library')

# Students

def student_detail(request, student_id):
    student = dict()
    student_data = md.User.objects.get(id=student_id)
    profile = md.Profile.objects.get(user=student_data)
    student['username'] = student_data.username
    student['first_name'] = student_data.first_name
    student['last_name'] = student_data.last_name
    student['email'] = student_data.email
    student['mobile_no'] = profile.phone
    student['roll_no'] = profile.roll
    return render(request, 'student.html', {**student})

@admin_required
def students(request):
    students = md.User.objects.filter(groups__name='student')
    return render(request, 'students.html', {'students': students})

@login_required
@admin_required
def approve_student(request, stu_id):
    user = md.User.objects.get(id=stu_id)
    if user:
        user.is_staff = True
        user.save()
        messages.success(request, f'Student {user.username} approved')
        return redirect('/students')
    else:
        messages.error(request, 'Student not found!')
        return redirect('/students')

@login_required
@admin_required
def disable_student(request, stu_id):
    user = md.User.objects.get(id=stu_id)
    if user:
        user.is_staff = False
        user.save()
        messages.success(request, f'Student {user.username} disabled')
        return redirect('/students')
    else:
        messages.error(request, 'Student not found!')
        return redirect('/students')

@login_required
@admin_required
def delete_student(request, stu_id):
    user = md.User.objects.get(id=stu_id)
    if user:
        name = user.username.capitalize()
        user.delete()
        messages.success(request, f"Student {name} deleted Successfully")
        return redirect('/students')
    else:
        messages.warning(request, 'Student not found!')
        return redirect('/students')

# ledger
def ledger(request):
    ledger = md.Ledger.objects.filter()
    students = md.User.objects.filter(groups__name='student')
    return render(request, 'ledger.html', {'ledger': ledger, 'students': students})

def add_book_ledger_entry(request):
    student = request.POST.get('student')
    isbn = request.POST.get('isbn')
    roll = request.POST.get('roll-no')
    checkout_date = request.POST.get('checkout-date')
    checkin_date = request.POST.get('checkin-date')
    md.Ledger.objects.create(
        user_id=student,
        isbn=isbn,
        roll_no=roll,
        checkout_date=checkout_date,
        checkin_date=checkin_date,
        is_pending=True,
    )
    return redirect('/ledger')

def overdue(request):
    today = timezone.now().date()
    logs = md.Ledger.objects.filter(checkin_date__lt=today, is_checked_in=False)
    return render(request, 'overdue.html', {'logs': logs})

def approved(request):
    logs = md.Ledger.objects.filter(is_approved=True, is_pending=False, is_checked_in=False, is_checked_out=False)
    return render(request, 'approved.html', {'logs': logs})

def checked_out(request):
    logs = md.Ledger.objects.filter(is_checked_out=True, is_checked_in=False)
    return render(request, 'checked-out.html', {'logs': logs})

# auth units
@login_required
def update_profile(request):
    if request.method == const.POST:
        first_name = str(request.POST.get('first_name')).strip()
        last_name = str(request.POST.get('last_name')).strip()
        email = str(request.POST.get('email')).strip()
        password = str(request.POST.get('password')).strip()
        url = str(request.POST.get('form-current-url')).strip()
        user_data = dict()
        if first_name:
            user_data['first_name'] = first_name
        if last_name:
            user_data['last_name'] = last_name
        if email:
            user_data['email'] = email
        md.User.objects.filter(username=request.user.username).update(**user_data)
        if password:
            user = request.user
            user.set_password(password)
            user.save()
            del password
        return redirect(url)
    return redirect('/')

def signup(request):
    if request.method == 'POST':
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        mobile_no = request.POST["mobile-no"]
        roll_no = request.POST["roll-no"]
        password = request.POST["password"]
        if username and email and password:
            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
                user.is_staff = False
                student_group = Group.objects.get(name='student')
                user.groups.add(student_group)
                user.save()
                profile = md.Profile.objects.create(
                    user=user,
                    email=email,
                    phone=mobile_no,
                    roll=roll_no,
                )
                messages.success(request, 'User created successfully')
                return redirect('signin')
            else:
                messages.error(request, 'Username or Email already exists')
                return redirect('signin')
        else:
            messages.error(request, 'Please fill all the fields to create an account')
    return render(request,'signup.html')

def signin(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='student').exists():
            return redirect('/student')
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        if "@" in username:
            user_obj = User.objects.get(email=username)
            if user_obj:
                username = user_obj.username
            else:
                messages.error(request, 'User not found!')
                return redirect('/signin')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.warning(request, 'Student needs to be approved')
                return redirect('/signin')
        else:
            messages.error(request, 'Invalid credentials Please try again')
    return render(request,'signin.html')

def circulation_log(request):
    logs = md.Ledger.objects.filter(is_pending=False)
    return render(request, 'circulation-log.html', {'logs': logs})

def signout(request):
    if request.user.is_authenticated: logout(request)
    return redirect('signin')

@login_required
def ui_typography(request):
    return render(request, 'ui_typography.html')

@login_required
def ui_colors(request):
    return render(request, 'ui_colors.html')

@login_required
def ui_fontawesome(request):
    return render(request, 'ui_fontawesome.html')

@login_required
def ui_themify(request):
    return render(request, 'ui_themify.html')

@login_required
def ui_buttons(request):
    return render(request, 'ui_buttons.html')

@login_required
def ui_cards(request):
    return render(request, 'ui_cards.html')

@login_required
def ui_modals(request):
    return render(request, 'ui_modals.html')

@login_required
def ui_toastr(request):
    return render(request, 'ui_toastr.html')

@login_required
def tb_basic(request):
    return render(request, 'tb_basic.html')

@login_required
def tb_datatables(request):
    return render(request, 'tb_datatables.html')

@login_required
def fm_control(request):
    return render(request, 'fm_control.html')

@login_required
def fm_ckeditor_classic(request):
    return render(request, 'fm_ckeditor_classic.html')

@login_required
def fm_ckeditor_balloon(request):
    return render(request, 'fm_ckeditor_balloon.html')

@login_required
def fm_ckeditor_block(request):
    return render(request, 'fm_ckeditor_block.html')

@login_required
def fm_ckeditor_inline(request):
    return render(request, 'fm_ckeditor_inline.html')

@login_required
def fm_ckeditor_document(request):
    return render(request, 'fm_ckeditor_document.html')

@login_required
def ch_apexcharts(request):
    return render(request, 'ch_apexcharts.html')

@login_required
def pg_login(request):
    return render(request, 'pg_login.html')

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)