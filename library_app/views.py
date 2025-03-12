# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth.models import User
# from datetime import date
# from django.contrib.auth import login, authenticate, logout
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Book, BookIssue, BookRequest
# import requests

# def is_admin(user):
#     return user.is_superuser and user.username == "admin"

# def register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email    = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')
#         if password != confirm_password:
#             return render(request, 'register.html', {'error': 'Passwords do not match'})
#         if User.objects.filter(username=username).exists():
#             return render(request, 'register.html', {'error': 'Username already exists'})
#         user = User.objects.create_user(username=username, email=email, password=password)
#         login(request, user)
#         return redirect('book_list')
#     return render(request, 'register.html')

# # Custom login view
# def custom_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             # Redirect to the library homepage (book list) after login
#             return redirect('book_list')
#         else:
#             return render(request, 'login.html', {'error': 'Invalid username or password.'})
            
#     return render(request, 'login.html')


# def book_list(request):
#     books = Book.objects.all()
#     return render(request, 'book_list.html', {'books': books})

# @login_required
# def request_book(request, book_id):
#     book = get_object_or_404(Book, id=book_id)
#     if request.method == 'POST':
#         # Check if there's already a pending request for this book by the user
#         if BookRequest.objects.filter(book=book, user=request.user, status='pending').exists():
#             return render(request, 'request_book.html', {
#                 'book': book,
#                 'error': 'You have already requested this book.'
#             })
#         BookRequest.objects.create(book=book, user=request.user)
#         return redirect('user_requests')
#     return render(request, 'request_book.html', {'book': book})

# @login_required
# def user_requests(request):
#     """Display the logged-in user’s book requests."""
#     requests_list = BookRequest.objects.filter(user=request.user)
#     return render(request, 'user_requests.html', {'requests': requests_list})


# @user_passes_test(is_admin, login_url='login')
# def add_book(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         author = request.POST.get('author')
#         quantity = request.POST.get('quantity')
#         try:
#             quantity = int(quantity)
#         except ValueError:
#             return render(request, 'add_book.html', {'error': 'Quantity must be a number.'})
#         Book.objects.create(title=title, author=author, quantity=quantity)
#         return redirect('book_list')
#     return render(request, 'add_book.html')

# # @login_required
# # def issue_book(request, book_id):
# #     book = get_object_or_404(Book, id=book_id)
# #     if book.quantity > 0:
# #         BookIssue.objects.create(book=book, user=request.user)
# #         book.quantity -= 1
# #         book.save()
# #     return redirect('book_list')


# @staff_member_required
# def issue_book(request, book_id):
#     book = get_object_or_404(Book, id=book_id)
    
#     if request.method == 'POST':
#         selected_user_id = request.POST.get('user_id')
#         selected_user = get_object_or_404(User, id=selected_user_id)

#         if book.quantity > 0:
#             BookIssue.objects.create(book=book, user=selected_user)
#             book.quantity -= 1
#             book.save()

#         return redirect('book_list')
    
#     else:
#         # GET request -> Show the form with a list of users (can be filtered as needed)
#         all_users = User.objects.all()
#         return render(request, 'issue_form.html', {
#             'book': book,
#             'all_users': all_users,
#         })


# @login_required
# def return_book(request, issue_id):
#     issue_record = get_object_or_404(BookIssue, id=issue_id)
#     if issue_record.user != request.user:
#         # Optionally, display an error or redirect if the user is not authorized
#         return redirect('user_issues')
#     issue_record.status = 'returned'
#     issue_record.return_date = date.today()
#     issue_record.save()

#     # Increase the book quantity
#     issue_record.book.quantity += 1
#     issue_record.book.save()

#     return redirect('user_issues')



# # @login_required
# # def return_book(request, issue_id):
# #     issue_record = get_object_or_404(BookIssue, id=issue_id)
# #     issue_record.status = 'returned'
# #     issue_record.return_date = date.today()
# #     issue_record.save()

# #     # Increase the book quantity
# #     issue_record.book.quantity += 1
# #     issue_record.book.save()

# #     return redirect('user_issues')

# @login_required
# def user_issues(request):
#     issues = BookIssue.objects.filter(user=request.user, status='issued')
#     return render(request, 'user_issues.html', {'issues': issues})

# @user_passes_test(is_admin, login_url='login')
# def upload_book_image(request, book_id):
#     """
#     Handle uploading a book cover image to the external Azure-based image API.
#     """
#     book = get_object_or_404(Book, pk=book_id)

#     if request.method == 'POST':
#         # 1. Get the uploaded file from request.FILES
#         uploaded_file = request.FILES.get('cover_image')
#         if not uploaded_file:
#             # No file uploaded
#             return render(request, 'upload_cover.html', {
#                 'book': book,
#                 'error': 'No file selected!'
#             })

#         try:
#             # 2. Send to external API using multipart/form-data
#             #    Example POST URL (adjust to your folder or desired path):
#             base_url = "https://scalablecloudapimgm.azure-api.net/scalablecloud/x23293080"
#             endpoint = f"{base_url}/image/upload?virtualFolderName=book_covers"

#             files = {
#                 'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
#             }
#             response = requests.post(endpoint, files=files)
#             response.raise_for_status()

#             # 3. Extract SAS URL from success response
#             #    (Assuming response JSON: { "sas_url": "https://..." } or similar)
#             # data = response.json()
#             # sas_url = data.get('sas_url')  # Adjust key to match the actual API response

#             raw_text = response.text.strip()
#             # print("DEBUG: Raw response text:", raw_text)
#             # print(raw_text.strip())
#             sas_url = raw_text

#             if not sas_url:
#                 return render(request, 'upload_cover.html', {
#                     'book': book,
#                     'error': 'Unable to retrieve SAS URL from API response.'
#                 })

#             # 4. Save the SAS URL to the Book model
#             book.cover_url = sas_url
#             print(book.cover_url)
#             book.save()

#             return redirect('book_list')

#         except requests.exceptions.RequestException as e:
#             # Handle errors from the external API
#             return render(request, 'upload_cover.html', {
#                 'book': book,
#                 'error': f'Error uploading image: {e}'
#             })

#     # GET request -> Render upload form
#     return render(request, 'upload_cover.html', {'book': book})


# def all_images(request):
#     """
#     Displays a page showing all books that have a 'cover_url'.
#     """
#     books = Book.objects.exclude(cover_url__exact='')
#     return render(request, 'all_images.html', {'books': books})


# @user_passes_test(is_admin, login_url='login')
# def manage_requests(request):
#     """View all pending book requests for admin review."""
#     pending_requests = BookRequest.objects.filter(status='pending')
#     return render(request, 'manage_requests.html', {'requests': pending_requests})

# @user_passes_test(is_admin, login_url='login')
# def approve_request(request, request_id):
#     """Approve a book request, issue the book, and reduce the available quantity."""
#     book_request = get_object_or_404(BookRequest, id=request_id)
#     book = book_request.book
#     if book.quantity > 0:
#         book_request.status = 'approved'
#         book_request.response_date = date.today()
#         book_request.save()
#         # Issue the book to the user
#         BookIssue.objects.create(book=book, user=book_request.user)
#         book.quantity -= 1
#         book.save()
#     else:
#         # Optionally, mark the request as rejected if no copies are available
#         book_request.status = 'rejected'
#         book_request.response_date = date.today()
#         book_request.save()
#     return redirect('manage_requests')

# @user_passes_test(is_admin, login_url='login')
# def reject_request(request, request_id):
#     """Reject a book request."""
#     book_request = get_object_or_404(BookRequest, id=request_id)
#     book_request.status = 'rejected'
#     book_request.response_date = date.today()
#     book_request.save()
#     return redirect('manage_requests')

# def custom_logout(request):
#     logout(request)
#     # Redirect to a page that offers both login and registration options.
#     # For instance, if your login page includes a link to registration, use its URL name:
#     return redirect('login')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from datetime import date
from django.contrib.auth import login, authenticate, logout
from .models import Book, BookIssue, BookRequest
import requests

# Custom test: Only allow access if user is superuser and username is "admin"


def is_admin(user):
    return user.is_superuser or user.username == "admin"


# -------------------------
# Views for All Registered Users
# -------------------------

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('book_list')
    return render(request, 'register.html')


# Custom login view for all users
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('book_list')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')


def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})





@login_required
def request_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        # Prevent duplicate pending requests for the same book
        if BookRequest.objects.filter(book=book, user=request.user, status='pending').exists():
            return render(request, 'request_book.html', {
                'book': book,
                'error': 'You have already requested this book.'
            })
        BookRequest.objects.create(book=book, user=request.user, status='pending')
        return redirect('book_list')
    return render(request, 'request_book.html', {'book': book})


@login_required
def user_requests(request):
    requests_list = BookRequest.objects.filter(user=request.user)
    return render(request, 'user_requests.html', {'requests': requests_list})


@login_required
def return_book(request, issue_id):
    issue_record = get_object_or_404(BookIssue, id=issue_id)
    if issue_record.user != request.user:
        return redirect('user_issues')
    issue_record.status = 'returned'
    issue_record.return_date = date.today()
    issue_record.save()
    # Increase available quantity of the book
    issue_record.book.quantity += 1
    issue_record.book.save()
    return redirect('user_issues')


@login_required
def user_issues(request):
    issues = BookIssue.objects.filter(user=request.user, status='issued')
    return render(request, 'user_issues.html', {'issues': issues})


def custom_logout(request):
    logout(request)
    return redirect('login')


def all_images(request):
    """
    Displays a page showing all books that have a cover image.
    """
    books = Book.objects.exclude(cover_url__exact='')
    return render(request, 'all_images.html', {'books': books})


# -------------------------
# Admin-only Views (Accessible only by superuser "admin")
# -------------------------

@user_passes_test(is_admin, login_url='login')
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
        except ValueError:
            return render(request, 'add_book.html', {'error': 'Quantity must be a number.'})
        Book.objects.create(title=title, author=author, quantity=quantity)
        return redirect('book_list')
    return render(request, 'add_book.html')


@user_passes_test(is_admin, login_url='login')
def issue_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        selected_user_id = request.POST.get('user_id')
        selected_user = get_object_or_404(User, id=selected_user_id)
        if book.quantity > 0:
            BookIssue.objects.create(book=book, user=selected_user)
            book.quantity -= 1
            book.save()
        return redirect('book_list')
    else:
        # Display a form for admin to select a user to issue the book
        all_users = User.objects.all()
        return render(request, 'issue_form.html', {
            'book': book,
            'all_users': all_users,
        })


@user_passes_test(is_admin, login_url='login')
def upload_book_image(request, book_id):
    """
    Allows the admin to upload a book cover image via an external API.
    """
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        uploaded_file = request.FILES.get('cover_image')
        if not uploaded_file:
            return render(request, 'upload_cover.html', {
                'book': book,
                'error': 'No file selected!'
            })
        try:
            base_url = "https://scalablecloudapimgm.azure-api.net/scalablecloud/x23293080"
            endpoint = f"{base_url}/image/upload?virtualFolderName=book_covers"
            files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}
            response = requests.post(endpoint, files=files)
            response.raise_for_status()
            sas_url = response.text.strip()
            if not sas_url:
                return render(request, 'upload_cover.html', {
                    'book': book,
                    'error': 'Unable to retrieve SAS URL from API response.'
                })
            book.cover_url = sas_url
            book.save()
            return redirect('book_list')
        except requests.exceptions.RequestException as e:
            return render(request, 'upload_cover.html', {
                'book': book,
                'error': f'Error uploading image: {e}'
            })
    return render(request, 'upload_cover.html', {'book': book})


@user_passes_test(is_admin, login_url='login')
def manage_requests(request):
    pending_requests = BookRequest.objects.filter(status='pending')
    context = {'requests': pending_requests}
    # If there are any pending requests, add a flag to show a popup message
    if pending_requests.exists():
        context['new_request'] = True
    return render(request, 'manage_requests.html', context)

@user_passes_test(is_admin, login_url='login')
def approve_request(request, request_id):
    book_request = get_object_or_404(BookRequest, id=request_id)
    book = book_request.book
    if book.quantity > 0:
        book_request.status = 'approved'
        book_request.response_date = date.today()
        book_request.save()
        # Optionally issue the book to the user (if your logic does that)
        BookIssue.objects.create(book=book, user=book_request.user)
        book.quantity -= 1
        book.save()
    else:
        book_request.status = 'rejected'
        book_request.response_date = date.today()
        book_request.save()
    return redirect('manage_requests')


@user_passes_test(is_admin, login_url='login')
def reject_request(request, request_id):
    book_request = get_object_or_404(BookRequest, id=request_id)
    book_request.status = 'rejected'
    book_request.response_date = date.today()
    book_request.save()
    return redirect('manage_requests')
