from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    cover_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    

class BookRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateField(auto_now_add=True)
    response_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} requested by {self.user.username}"


class BookIssue(models.Model):
    STATUS_CHOICES = (
        ('issued', 'Issued'),
        ('returned', 'Returned'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='issued')

    def __str__(self):
        return f"{self.book.title} - {self.user.username} ({self.status})"


