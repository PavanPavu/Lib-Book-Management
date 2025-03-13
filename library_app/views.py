# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth.models import User
# from datetime import date
# from django.contrib.auth import login, authenticate, logout
# from django.contrib.admin.views.decorators import staff_member_required
# from .models import Book, BookIssue, BookRequest
# import requests


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from datetime import date
from django.contrib.auth import login, authenticate, logout
from .models import Book, BookIssue, BookRequest
import requests
import os, boto3

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


@user_passes_test(is_admin, login_url='login')
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        # Optionally, remove the key-value mapping from the external API.
        key = f"book:{book.id}"
        delete_key_value(key)
        
        # Delete the book from the database.
        book.delete()
        return redirect('book_list')
    
    # For GET requests, render a confirmation page.
    return render(request, 'delete_book_confirm.html', {'book': book})


# @login_required
# def return_book(request, issue_id):
#     issue_record = get_object_or_404(BookIssue, id=issue_id)
#     if issue_record.user != request.user:
#         return redirect('user_issues')
#     issue_record.status = 'returned'
#     issue_record.return_date = date.today()
#     issue_record.save()
#     # Increase available quantity of the book
#     issue_record.book.quantity += 1
#     issue_record.book.save()
#     return redirect('user_issues')


API_URL = "https://uvbvgn4d1l.execute-api.us-east-1.amazonaws.com/x23304987api"

def delete_key_value(key):
    """
    Deletes a key–value pair from the external API.
    This example uses a GET request with an additional query parameter 'action=delete'.
    Adjust according to your API's requirements.
    """
    params = {
        "key": key,
        "action": "delete"
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        print("Delete API Request URL:", response.url)
        print("Delete API Status Code:", response.status_code)
        print("Delete API Response:", response.text)
    except Exception as e:
        print("Error deleting key value via API:", e)


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

    # Delete the key-value mapping for this book from the external API.
    # Assuming the key was stored as "book:{book.id}"
    key = f"book:{issue_record.book.id}"
    delete_key_value(key)

    return redirect('user_issues')

@user_passes_test(is_admin, login_url='login')
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        # Optionally, remove the key-value mapping from the external API.
        key = f"book:{book.id}"
        delete_key_value(key)
        
        # Delete the book from the database.
        book.delete()
        return redirect('book_list')
    
    # For GET requests, render a confirmation page.
    return render(request, 'delete_book_confirm.html', {'book': book})
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



# @user_passes_test(is_admin, login_url='login')
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
#         # Display a form for admin to select a user to issue the book
#         all_users = User.objects.all()
#         return render(request, 'issue_form.html', {
#             'book': book,
#             'all_users': all_users,
#         })

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

            # Use GET request with query parameters
            api_url = "https://uvbvgn4d1l.execute-api.us-east-1.amazonaws.com/x23304987api"
            params = {
                "key": f"book:{book.id}",
                "value": selected_user.username
            }
            try:
                response = requests.get(api_url, params=params)

                # Debug output:
                print("API Request URL:", response.url)
                print("Status Code:", response.status_code)
                print("Response Headers:", response.headers)
                print("Response Content:", response.text)


                response.raise_for_status()
            except requests.RequestException as e:
                # Log or handle the error as needed.
                print("Error updating external API:", e)

        return redirect('book_list')
    
    else:
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
