from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    pid = models.AutoField(primary_key=True)
    pname = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=1000,)
    price = models.IntegerField()
    stockqty = models.IntegerField()
    pub_date = models.DateField(default=timezone.now)
    care = models.CharField(max_length=1000,default="No care tip is available")
    water = models.CharField(max_length=50,default="No water is available")
    fertilizer = models.CharField(max_length=50,default="No fertilizer is available")
    soil = models.CharField(max_length=50,default="No soil is available")
    sun = models.CharField(max_length=50,default="No sun is available")
    img = models.ImageField(upload_to="shop/images",blank=False, null=False,default="")

    def __str__(self):
        return self.pname

class Order(models.Model):  # Link order to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow existing orders
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=90)
    email = models.EmailField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=6)
    phone = models.CharField(max_length=10,default="")
    date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=10, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')], default='COD')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    contact = models.IntegerField(default=0)
    subject = models.CharField(max_length=150)
    message = models.CharField(max_length=10000)
    
    def __str__(self):
        return (self.name)

class OldOrder(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.IntegerField()
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField()
    name = models.CharField(max_length=90)
    email = models.EmailField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=6)
    phone = models.CharField(max_length=10)
    date = models.DateField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return (self.name)

class Blog(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title