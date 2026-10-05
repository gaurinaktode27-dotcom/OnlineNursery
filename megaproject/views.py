import json
from django.shortcuts import render, redirect
from .models import Product, Order, Contact, OldOrder, Blog
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
# from .models import Blog
import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
import random
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import razorpay
from django.shortcuts import get_object_or_404

User=get_user_model()
# Create your views here.

def headerfooter(request):
    products=Product.objects.all()
    context={
        "products":products,
    }
    return render(request,"headerfooter.html",context)

def index(request):
    products=Product.objects.all()
    context={
        "products":products,
    }
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request,"index.html",{'products': products, 'blogs': blogs})

def login(request):
    if request.method=="POST":
        userid=request.POST.get("userid")
        password=request.POST.get("password")
        user = authenticate(request, username=userid,password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            messages.error(request, " Enter Correct ID, Password")
            return redirect("login")
        
    return render(request,"login.html")

@login_required
def profile_update(request):
    if request.method == "POST":
        first_name= request.POST.get("first_name")
        last_name= request.POST.get("last_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        user_id=request.user.id
        
        try:
            user = User.objects.get(id=user_id)
            user.first_name=first_name
            user.last_name=last_name
            user.username=username
            user.email=email
            user.save()
            messages.success(request,"Profile updated successfully")
        
        except User.DoesNotExist:
            messages.error(request,"User does not exist")
            
        return redirect("profile")
    
    return render(request,"profile.html")

# Temporary storage for OTPs
otp_storage = {}

def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        userid = request.POST.get("userid")
        password = request.POST.get("password")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")

        # Check if the username (User ID) already exists
        if User.objects.filter(username=userid).exists():
            messages.error(request, "User ID already taken. Try another one!")
            return redirect("signup")

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken. Try another one!")
            return redirect("signup")
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Store user data and OTP temporarily
        otp_storage[email] = {
            'otp': otp,
            'userid': userid,
            'password': password,
            'firstname': firstname,
            'lastname': lastname,
            'timestamp': datetime.datetime.now()
        }
        
        # Send OTP email
        subject = 'GreenNest - Email Verification OTP'
        message = f'''
        Hello {firstname},

        Thank you for registering with GreenNest!
        
        Your OTP for email verification is: {otp}
        
        This OTP is valid for 5 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        GreenNest Team
        '''
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            messages.success(request, "OTP has been sent to your email. Please check your inbox and verify to complete registration.")
            return redirect('verify_otp', email=email)
        except Exception as e:
            print(f"Email error: {str(e)}")  # This will show in your console
            messages.error(request, f"Failed to send OTP. Please try again. Error: {str(e)}")
            return redirect("signup")
        
    return render(request, "signup.html")

def verify_otp(request, email):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        
        # Check if OTP exists in storage
        if email not in otp_storage:
            messages.error(request, "OTP expired. Please sign up again.")
            return redirect("signup")
            
        stored_data = otp_storage[email]
        
        # Check if OTP is expired (5 minutes)
        if (datetime.datetime.now() - stored_data['timestamp']).total_seconds() > 300:
            del otp_storage[email]
            messages.error(request, "OTP expired. Please sign up again.")
            return redirect("signup")
            
        # Verify OTP
        if entered_otp == stored_data['otp']:
            try:
                # Create user
                user = User.objects.create_user(
                    username=stored_data['userid'],
                    email=email,
                    password=stored_data['password'],
                    first_name=stored_data['firstname'],
                    last_name=stored_data['lastname']
                )
                user.save()
                
                # Clear OTP data
                del otp_storage[email]
                
                messages.success(request, "Account created successfully! Please login.")
                return redirect("login")
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
                return redirect("signup")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_otp', email=email)
            
    return render(request, "verify_otp.html", {'email': email})

def profile(request):
    return render(request,"profile.html")

def logout1(request):
    logout(request)
    return render(request,"index.html")

def manageproduct(request):
    products=Product.objects.all()
    context={
        "products":products,
    }
    return render(request,"manageproduct.html",context)

def add_product(request):
    if request.method == "POST":
        try:
            pname = request.POST.get("pname")
            category = request.POST.get("category")
            description = request.POST.get("description")
            price = request.POST.get("price")
            stockqty = request.POST.get("stockqty")
            pub_date = request.POST.get("pub_date", timezone.now().date())
            care = request.POST.get("caretip", "No care tip is available")
            water = request.POST.get("water", "No water is available")
            fertilizer = request.POST.get("fertilizer", "No fertilizer is available")
            soil = request.POST.get("soil", "No soil is available")
            sun = request.POST.get("sun", "No sun is available")
            img = request.FILES.get("image")

            if not img:
                messages.error(request, "Please upload an image for the product")
                return redirect("manageproduct")

            # Create and save the product
            product = Product(
                pname=pname,
                category=category,
                description=description,
                price=price,
                stockqty=stockqty,
                pub_date=pub_date,
                care=care,
                water=water,
                fertilizer=fertilizer,
                soil=soil,
                sun=sun,
                img=img
            )
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect("manageproduct")
        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect("manageproduct")
    return render(request, "manageproduct.html")

def update_product(request, id):
    product = get_object_or_404(Product, pid=id)
    print(id,"is the id")

    if request.method == "POST":
        # Capture form data
        if request.POST.get("pname"):
            product.pname = request.POST.get("pname")
        if request.POST.get("category"):
            product.category = request.POST.get("category")
        if request.POST.get("description"):
            product.description = request.POST.get("description")
        if request.POST.get("price"):
            product.price = request.POST.get("price")
        if request.POST.get("stockqty"):
         product.stockqty = request.POST.get("stockqty")
        
        # Handle Date (Only update if new date is provided)
        if request.POST.get("pub_date"):
            product.pub_date = request.POST.get("pub_date")
        
        # Handle other fields (Only update if new data is provided)
        if request.POST.get("caretip"):
            product.care = request.POST.get("caretip")
        if request.POST.get("water"):
            product.water = request.POST.get("water")
        if request.POST.get("fertilizer"):
            product.fertilizer = request.POST.get("fertilizer")
        if request.POST.get("soil"):
            product.soil = request.POST.get("soil")
        if request.POST.get("sun"):
            product.sun = request.POST.get("sun")
        
        # Handle Image Update (Only update if image is uploaded)
        if request.FILES.get("image"):
            product.img = request.FILES["image"]

        # Save Product
        try:
            product.save()
            messages.success(request, "✅ Product updated successfully!")
        except Exception as e:
            messages.error(request, f"❌ Error updating product: {e}")

        # Redirect to manage product page
        return redirect('manageproduct')

    return render(request, "manageproduct.html", {"product": product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, pid=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('manageproduct')

@login_required
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        updatedqty = request.POST.get('updatedqty','')
        pid = request.POST.get('pid','')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip', '')
        phone = request.POST.get('phone', '')
        total_amount = request.POST.get('checkoutAmount', '')
        payment_method = request.POST.get('payment_method', 'COD')
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')

        # Create and save the order
        order = Order(
            user=request.user,
            items_json=items_json, 
            amount=total_amount, 
            name=name, 
            email=email,
            address=address, 
            city=city, 
            state=state, 
            zip_code=zip_code, 
            phone=phone,
            date=datetime.datetime.now(),
            payment_method=payment_method,
            razorpay_payment_id=razorpay_payment_id if payment_method == 'Online' else None
        )
        order.save()

        # Update product quantities
        try:
            upqty = [x for x in updatedqty.split(",") if x]  # Filter out empty strings
            upid = [int(x) for x in pid.split(",") if x]  # Convert each element to int and filter out empty strings
            
            # Ensure both lists have the same length
            if len(upqty) != len(upid):
                raise ValueError("Mismatch between quantity and product ID lists")
            
            # Update each product's quantity
            for i in range(len(upqty)):
                try:
                    product = Product.objects.get(pid=upid[i])
                    product.stockqty = upqty[i]
                    product.save()
                except Product.DoesNotExist:
                    print(f"Product with pid {upid[i]} not found")
                    continue
                except Exception as e:
                    print(f"Error updating product {upid[i]}: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error processing quantities: {str(e)}")
            # Continue with the order even if quantity update fails
            pass

        thank = True
        id = order.order_id
        return render(request, "checkout.html", {
            'thank': thank, 
            'id': id,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID
        })
    
    # Handle cart checkout
    elif request.method == "GET":
        cart_data = request.GET.get('cart')
        amount = request.GET.get('amount')
        
        if cart_data and amount:
            try:
                cart_items = json.loads(cart_data)
                context = {
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'is_cart_checkout': True,
                    'cart_items': cart_items,
                    'total_amount': amount
                }
            except json.JSONDecodeError:
                messages.error(request, "Invalid cart data")
                return redirect('viewproduct')
        else:
            context = {
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'is_cart_checkout': True
            }
        
        return render(request, "checkout.html", context)
    
    return render(request, "checkout.html", {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    })

def manageorder(request):
    orders = Order.objects.all().order_by('-date')  # Fetch all orders
    return render(request, "manageorder.html", {'orders': orders})


@login_required
def myorder(request):
    active_orders = Order.objects.filter(user=request.user).order_by('-date')
    old_orders = OldOrder.objects.filter(user=request.user).order_by('-date')
    return render(request, "myorder.html", {'active_orders': active_orders, 'old_orders': old_orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # Move the order to OldOrder database
    OldOrder.objects.create(
        user=order.user,
        items_json=order.items_json,
        amount=order.amount,
        name=order.name,
        email=order.email,
        address=order.address,
        city=order.city,
        state=order.state,
        zip_code=order.zip_code,
        phone=order.phone,
        date=order.date,
        status="Cancelled"
    )

    # Delete the order from active orders
    order.delete()
    return redirect('my_orders')

@login_required
def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, order_id=order_id)
        new_status = request.POST.get("status")

        if new_status in dict(Order.STATUS_CHOICES):
            if new_status in ["Cancelled", "Delivered"]:
                # Move order to OldOrder before deleting
                OldOrder.objects.create(
                    user = request.user,
                    order_id=order.order_id,
                    items_json=order.items_json,
                    amount=order.amount,
                    name=order.name,
                    email=order.email,
                    address=order.address,
                    city=order.city,
                    state=order.state,
                    zip_code=order.zip_code,
                    phone=order.phone,
                    date=order.date,
                    status=new_status
                )
                order.delete()  # Remove from active orders
            else:
                order.status = new_status
                order.save()

    return redirect("manageorder")

def old_orders(request):
    old_orders = OldOrder.objects.all().order_by('-date')
    return render(request, "oldorder.html", {'old_orders': old_orders})


def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.delete()
    return redirect('manageorder')  # Redirect back to the order list

@login_required
def manageuser(request):
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('index')
    
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users
    }
    return render(request, "manageuser.html", context)

def viewproduct(request):
    category_filter = request.GET.get('category', None)
    search_query = request.GET.get('search', None)

    if category_filter:
        products = Product.objects.filter(category__iexact=category_filter)
    elif search_query:
        search_query = search_query.strip()  # Remove extra spaces
        products = Product.objects.filter(
            Q(category__icontains=search_query) |
            Q(pname__icontains=search_query) |
            Q(description__icontains=search_query)|
            Q(price__icontains=search_query) |
            Q(care__icontains=search_query) |
            Q(water__icontains=search_query) |
            Q(fertilizer__icontains=search_query) |
            Q(soil__icontains=search_query) |
            Q(sun__icontains=search_query)
        )
    else:
        products = Product.objects.all()

    categorized_products = {}
    for product in products:
        if product.category not in categorized_products:
            categorized_products[product.category] = []
        categorized_products[product.category].append(product)

    return render(request, "viewproduct.html", {"categorized_products": categorized_products})

from django.shortcuts import get_object_or_404

def product(request, myid):
    product = get_object_or_404(Product, pid=myid)
    return render(request, "product.html", {"product": product})

def contact(request):
    if request.method == "POST":
        name1 = request.POST.get("name")
        email1 = request.POST.get("email")
        contact1 = request.POST.get("contact")
        subject1 = request.POST.get("subject")
        message1 = request.POST.get("message")

        cont = Contact(name=name1, email=email1, contact=contact1, subject=subject1, message=message1)
        cont.save()
        return redirect(contact)
    return render(request,"contact.html")

@login_required
def managefeedback(request):
    if not request.user.is_staff:  # Only allow staff/admin users
        return redirect('home')

    feedbacks = Contact.objects.all().order_by('-id')  # Get all feedbacks
    return render(request, 'managefeedback.html', {'feedbacks': feedbacks})

@login_required
def deletefeedback(request, feedback_id):

    feedback = get_object_or_404(Contact, id=feedback_id)
    feedback.delete()
    return redirect('managefeedback')

def blog(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog.html', {'blogs': blogs})

def create_blog(request):
    if request.method == "POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        if title and author and content:
            blog = Blog(title=title, author=author, content=content, image=image, created_at=timezone.now())
            blog.save()
            return redirect('blog')

    return render(request, 'blog.html')

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Only superuser can delete
    if request.user.is_superuser:
        blog.delete()
        messages.success(request, "Blog deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this blog.")
    
    return redirect('blog')



client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def razorpay_payment(request):
    if request.method == "POST":
        amount = int(float(request.POST.get('amount', 0)) * 100)  # Convert to paise
        if amount <= 0:
            messages.error(request, "Invalid amount")
            return redirect('checkout')
            
        try:
            # Store the form data in session for later use
            request.session['order_data'] = {
                'items_json': request.POST.get('itemsJson', ''),
                'updatedqty': request.POST.get('updatedqty', ''),
                'id': request.POST.get('id', ''),
                'name': request.POST.get('name', ''),
                'email': request.POST.get('email', ''),
                'address': request.POST.get('address', ''),
                'city': request.POST.get('city', ''),
                'state': request.POST.get('state', ''),
                'zip_code': request.POST.get('zip', ''),
                'phone': request.POST.get('phone', ''),
                'amount': amount / 100,  # Convert back to rupees
            }
            
            # Create Razorpay order
            payment = client.order.create({
                'amount': amount,
                'currency': 'INR',
                'payment_capture': '1'
            })
            
            context = {
                'payment': payment,
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            }
            return render(request, 'razorpay_payment.html', context)
        except Exception as e:
            messages.error(request, f"Error creating payment: {str(e)}")
            return redirect('checkout')
    return redirect('checkout')

@login_required
def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        try:
            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            # Get the stored order data
            order_data = request.session.get('order_data', {})
            if not order_data:
                messages.error(request, "Order data not found")
                return redirect('checkout')
            
            # Create the order
            order = Order(
                user=request.user,
                items_json=order_data['items_json'],
                amount=order_data['amount'],
                name=order_data['name'],
                email=order_data['email'],
                address=order_data['address'],
                city=order_data['city'],
                state=order_data['state'],
                zip_code=order_data['zip_code'],
                phone=order_data['phone'],
                date=datetime.datetime.now(),
                payment_method='Online',
                razorpay_payment_id=razorpay_payment_id
            )
            order.save()
            
            # Update product quantities
            upqty = order_data['updatedqty'].split(",")
            upid = order_data['id'].split(",")
            for i in range(len(upqty)):
                product = Product.objects.get(pid=upid[i])
                product.stockqty = upqty[i]
                product.save()
            
            # Clear the session data
            del request.session['order_data']
            
            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect('myorder')
            
        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return redirect('checkout')
    
    return redirect('checkout')

def test_email(request):
    try:
        subject = 'Online Nursery - Test Email'
        message = 'This is a test email from Online Nursery. If you receive this, the email configuration is working correctly.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['test@example.com']  # This will be captured in Mailtrap inbox
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        messages.success(request, "Test email sent successfully! Check your Mailtrap inbox.")
    except Exception as e:
        messages.error(request, f"Failed to send test email: {str(e)}")
        print(f"Email error: {str(e)}")  # This will show in your console
    return redirect('index')