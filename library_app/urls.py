from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import book_list, add_book, issue_book, return_book, user_issues

# urlpatterns = [   
#     path('', book_list, name='book_list'),
#     path('register/', views.register, name='register'),
#     path('login/', views.custom_login, name='login'),
#     path('add/', add_book, name='add_book'),
#     path('issue/<int:book_id>/', issue_book, name='issue_book'),
#     path('return/<int:issue_id>/', return_book, name='return_book'),
#     path('my-issues/', user_issues, name='user_issues'),
#     path('user_requests/', views.user_requests, name='user_requests'),
#     path('manage_requests/', views.manage_requests, name='manage_requests'),
#     path('approve_request/<int:request_id>/', views.approve_request, name='approve_request'),
#     path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
#     path('upload-cover/<int:book_id>/', views.upload_book_image, name='upload_book_image'),
#     path('all-images/', views.all_images, name='all_images'),
#     # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     # path('logout/', auth_views.LogoutView.as_view(next_page='login', http_method_names=['get', 'post']), name='logout'),
#     path('book/<int:book_id>/request/', views.request_book, name='request_book'),
#     path('logout/', views.custom_logout, name='logout'),
# ]


urlpatterns = [   
    path('', views.book_list, name='book_list'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Regular user actions:
    path('book/<int:book_id>/request/', views.request_book, name='request_book'),
    path('return/<int:issue_id>/', views.return_book, name='return_book'),
    path('my-issues/', views.user_issues, name='user_issues'),
    path('user_requests/', views.user_requests, name='user_requests'),
    path('all-images/', views.all_images, name='all_images'),

    # Admin-only actions:
    path('add/', views.add_book, name='add_book'),
    path('issue/<int:book_id>/', views.issue_book, name='issue_book'),
    path('upload-cover/<int:book_id>/', views.upload_book_image, name='upload_book_image'),
    path('manage_requests/', views.manage_requests, name='manage_requests'),
    path('approve_request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
]


