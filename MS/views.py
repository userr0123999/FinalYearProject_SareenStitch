from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.http import require_POST

from .forms import CustomUserRegistrationForm, LoginForm, ProductForm, ThriftProductForm, ThriftExtraForm, \
    VendorProductForm
from .models import Product, CartItem, WishlistItem, Notification, CustomUser
from django.contrib.auth import get_user_model
User = get_user_model()  # ✅ this ensures CustomUser is used


# ---------- PUBLIC ----------
def home(request):
    latest_products = Product.objects.filter(user__is_superuser=True).order_by('-created_at')[:6]
    return render(request, 'mytemplates/home.html', {
        'products': latest_products
    })



def start(request):
    return render(request, 'mytemplates/start.html')

def aboutus(request):
    return render(request, 'mytemplates/aboutus.html')

from django.db.models import Q, Max
from .models import Product

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Product, Vendor, ThriftProduct, BiddingProduct


from django.db.models import Q
from .models import Product, Vendor, BiddingProduct, ThriftProduct

def search_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(user__is_superuser=True)  # Only admin products

    vendors = Vendor.objects.all()
    bidding_products = BiddingProduct.objects.all()
    thrift_products = ThriftProduct.objects.all()

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

        vendors = vendors.filter(
            Q(store_name__icontains=query) |
            Q(store_description__icontains=query)
        )

        bidding_products = bidding_products.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query)
        )

        thrift_products = thrift_products.filter(
            Q(product__product_name__icontains=query) |  # ✅ Fix here
            Q(product__description__icontains=query) |
            Q(product__category__icontains=query)
        )

    return render(request, 'mytemplates/search_results.html', {
        'products': products,
        'vendors': vendors,
        'bidding_products': bidding_products,
        'thrift_products': thrift_products,
        'query': query
    })



from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Profile updated successfully!")
        return render(request, 'mytemplates/profile.html', {'user': user})

    return render(request, 'mytemplates/profile.html', {'user': user})




def thrift(request):
    return render(request, 'mytemplates/thrift.html')


from django.contrib.auth.decorators import login_required

@login_required
def chat_page(request, thrift_id):
    thrift = get_object_or_404(ThriftProduct, id=thrift_id)
    seller = thrift.user

    # Fetch messages only between current user and seller
    chat_messages = Chat.objects.filter(
        thrift=thrift
    ).filter(
        Q(sender=request.user) | Q(sender=seller)
    ).order_by('timestamp')

    if request.method == 'POST':
        msg = request.POST.get('message')
        if msg:
            Chat.objects.create(
                thrift=thrift,
                sender=request.user,
                vendor=seller.vendor if hasattr(seller, 'vendor') else None,
                message=msg
            )

            Notification.objects.create(
                user=seller,
                message=f"New message from {request.user.username} on {thrift.product.product_name}",
                type='chat'
            )
            Notification.objects.create(
                user=request.user,
                message=f"You messaged {seller.username} regarding {thrift.product.product_name}",
                type='chat'
            )

        # No toast messages — just reload to update chat
        return redirect('thrift_chat', thrift_id=thrift_id)

    return render(request, 'mytemplates/thrift_chat.html', {
        'thrift': thrift,
        'seller': seller,
        'messages': chat_messages
    })

# def thrift_list_view(request):
#     thrift_products = ThriftProduct.objects.filter(
#         approval_status='approved',
#         product__is_thrift=True
#     ).select_related('product').order_by('is_sold', '-id')  # ✅ removed is_sold=False
#
#     # Filters
#     category = request.GET.get('category')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#
#     if category:
#         thrift_products = thrift_products.filter(product__category__iexact=category)
#
#     try:
#         if min_price:
#             thrift_products = thrift_products.filter(product__price__gte=float(min_price))
#         if max_price:
#             thrift_products = thrift_products.filter(product__price__lte=float(max_price))
#     except ValueError:
#         pass
#
#     context = {
#         'thrift_products': thrift_products,
#     }
#     return render(request, 'mytemplates/thrift.html', context)

def thrift_list_view(request):
    thrift_products = ThriftProduct.objects.filter(
        approval_status='approved'
    ).select_related('product').order_by('is_sold', '-id')

    # Filters
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category:
        thrift_products = thrift_products.filter(product__category__iexact=category)

    try:
        if min_price:
            thrift_products = thrift_products.filter(product__price__gte=float(min_price))
        if max_price:
            thrift_products = thrift_products.filter(product__price__lte=float(max_price))
    except ValueError:
        pass

    context = {
        'thrift_products': thrift_products,
    }
    return render(request, 'mytemplates/thrift.html', context)



@login_required
def post_thrift(request):
    if request.method == 'POST':
        product_form = ThriftProductForm(request.POST, request.FILES)
        extra_form = ThriftExtraForm(request.POST)

        if product_form.is_valid() and extra_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            product.is_thrift = True
            product.save()

            thrift = extra_form.save(commit=False)
            thrift.product = product
            thrift.user = request.user
            thrift.approval_status = 'pending'  # 🚨 Important
            thrift.save()

            messages.success(request, 'Your thrift item has been submitted for approval.')
            return redirect('thrift')

    else:
        product_form = ThriftProductForm()
        extra_form = ThriftExtraForm()

    return render(request, 'mytemplates/post_thrift.html', {
        'product_form': product_form,
        'thrift_form': extra_form,
    })

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_manage_thrift(request):
    query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    thrift_items = ThriftProduct.objects.select_related('product', 'user')

    if query:
        thrift_items = thrift_items.filter(product__product_name__icontains=query)

    if status_filter:
        thrift_items = thrift_items.filter(approval_status=status_filter)

    # Add average rating to each product
    for thrift in thrift_items:
        thrift.avg_rating = thrift.product.rating_set.aggregate(avg=Avg('rating'))['avg']

    context = {
        'thrift_items': thrift_items,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'mytemplates/admin_thrift.html', context)




@staff_member_required
def approve_thrift(request, thrift_id):
    thrift = get_object_or_404(ThriftProduct, id=thrift_id)
    thrift.approval_status = 'approved'
    thrift.save()

    # ✅ Important: Set product.is_thrift = True
    product = thrift.product
    product.is_thrift = True
    product.save()

    messages.success(request, "Thrift item approved and now visible on the site.")
    return redirect('admin_thrift')


@staff_member_required
def reject_thrift(request, thrift_id):
    thrift = get_object_or_404(ThriftProduct, id=thrift_id)
    thrift.approval_status = 'rejected'
    thrift.save()
    return redirect('admin_thrift')

@staff_member_required
def mark_thrift_sold(request, thrift_id):
    thrift = get_object_or_404(ThriftProduct, id=thrift_id)
    thrift.is_sold = not thrift.is_sold
    thrift.save()
    return redirect('admin_thrift')

@staff_member_required
def delete_thrift(request, thrift_id):
    thrift = get_object_or_404(ThriftProduct, id=thrift_id)
    product_name = thrift.product.product_name
    thrift.product.delete()  # Deletes both thrift and linked product
    thrift.delete()
    messages.error(request, f"'{product_name}' has been deleted.")
    return redirect('admin_thrift')

from .forms import ThriftRatingForm
from .models import ThriftComment, Rating
from django.db.models import Avg, Sum


def thrift_detail_view(request, thrift_id):
    thrift = get_object_or_404(ThriftProduct, id=thrift_id, approval_status='approved')
    comments = ThriftComment.objects.filter(thrift=thrift).order_by('-created_at')
    reviews = Rating.objects.filter(thrift=thrift).order_by('-timestamp')
    rating_form = ThriftRatingForm()

    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'comment' in request.POST:
                msg = request.POST.get('comment')
                if msg:
                    ThriftComment.objects.create(thrift=thrift, user=request.user, message=msg)
            elif 'rating' in request.POST:
                rating_form = ThriftRatingForm(request.POST)
                if rating_form.is_valid():
                    rating_instance = rating_form.save(commit=False)
                    rating_instance.user = request.user
                    rating_instance.thrift = thrift
                    rating_instance.save()
                    messages.success(request, "Review submitted successfully!")

    # Avg rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_count = reviews.count()

    return render(request, 'mytemplates/thrift_detail.html', {
        'thrift': thrift,
        'comments': comments,
        'reviews': reviews,
        'rating_form': rating_form,
        'average_rating': avg_rating,
        'review_count': review_count,
    })


from .models import ThriftProduct, CartItem
from django.contrib.auth.decorators import login_required


@login_required
def add_thrift_to_cart(request, product_id):
    """Add thrift product to cart with size validation."""
    if request.method == 'POST':
        size = request.POST.get('size', 'Free Size') or 'Free Size'

        thrift = get_object_or_404(
            ThriftProduct,
            product__id=product_id,
            approval_status='approved',
            is_sold=False
        )

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=thrift.product,
            size=size
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, "Thrift item added to your cart.")
        return redirect('thrift_detail', thrift.id)

    return redirect('thrift')


def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact')
        message = request.POST.get('message')

        if full_name and email and contact_number and message:
            ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                contact=contact_number,
                message=message
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "Please fill out all the fields.")

    return render(request, 'mytemplates/contact.html')


# def forgotpassword(request):
#     return render(request, 'mytemplates/forgotpassword.html')
def forgotpassword(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    subject = "Password Reset - SareenStitch"
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_url = request.build_absolute_uri(
                        reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                    )
                    message = f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_url}"
                    send_mail(subject, message, 'noreply@sareenstitch.com', [user.email])
                messages.success(request, "Password reset link sent! Please check your email.")
            else:
                messages.error(request, "No user found with that email.")
    else:
        form = PasswordResetForm()
    return render(request, 'mytemplates/forgotpassword.html', {'form': form})


def custom_reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = DjangoUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, DjangoUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'mytemplates/password_reset_form.html', {'form': form})
    else:
        messages.error(request, 'The reset link is invalid or has expired.')
        return redirect('forgotpassword')


#--------biddding------------------------------------------------
from django.shortcuts import render
from django.utils import timezone
from .models import BiddingProduct, Bid

def bidding_list_view(request):
    now = timezone.now()

    # Get all products for display
    products = BiddingProduct.objects.all().order_by('-end_time')

    # Prepare a dict of product.id → winner.username (for ended bids)
    product_winners = {}
    for product in products:
        if product.end_time < now:
            highest_bid = Bid.objects.filter(product=product).order_by('-amount').first()
            if highest_bid:
                product_winners[product.id] = highest_bid.user.username

    return render(request, 'mytemplates/bidding_list.html', {
        'products': products,
        'now': now,
        'product_winners': product_winners,
    })



@login_required
def bidding_detail(request, product_id):
    product = get_object_or_404(BiddingProduct, id=product_id)

    product = get_object_or_404(BiddingProduct, id=product_id)
    highest = product.highest_bid()  # ← Fix is here
    min_bid = product.starting_price if not highest else highest.amount + 1

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))

            if amount < min_bid:
                messages.error(request, f"⚠️ Minimum bid must be Rs {min_bid}")
                return redirect('bidding_detail', product_id=product.id)

            # ✅ Place bid
            Bid.objects.create(product=product, user=request.user, amount=amount)

            # ✅ Success message
            messages.success(request, f"✅ You successfully placed a bid of Rs {amount} on '{product.product_name}'")

            # ✅ Notify user
            Notification.objects.create(
                user=request.user,
                message=f"✅ You successfully placed a bid of Rs {amount} on '{product.product_name}'",
                type='bid'
            )

            return redirect('bidding_detail', product_id=product.id)

        except ValueError:
            messages.error(request, "Invalid bid amount.")
            return redirect('bidding_detail', product_id=product.id)

    return render(request, 'mytemplates/bidding_detail.html', {'product': product, 'highest_bid': highest})


from django.contrib.auth.decorators import login_required
@login_required
def place_bid_view(request, product_id):
    product = get_object_or_404(BiddingProduct, id=product_id)

    #  Check if bidding is still open
    if not product.is_active():
        messages.error(request, "❌ Bidding for this product is closed.")
        return redirect('bidding_list')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except ValueError:
            messages.error(request, "❗ Invalid bid amount.")
            return redirect('bidding_list')

        highest_bid = product.highest_bid()
        min_bid = float(product.starting_price) if not highest_bid else float(highest_bid.amount) + 1

        if amount < min_bid:
            messages.error(request, f"⚠️ Your bid must be at least Rs {min_bid}.")
            return redirect('bidding_list')

        #  Notify previous highest bidder
        if highest_bid and highest_bid.user != request.user:
            Notification.objects.create(
                user=highest_bid.user,
                message=f"You have been outbid on '{product.product_name}'. Place a new bid before time runs out!",
                type='bid'
            )

        #  Save new bid
        Bid.objects.create(product=product, user=request.user, amount=amount)

        #  Notify current bidder
        Notification.objects.create(
            user=request.user,
            message=f"✅ You placed a bid of Rs {amount} on '{product.product_name}'",
            type='bid'
        )

        messages.success(request, "🎉 Bid placed successfully!")
        return redirect('bidding_list')

    return render(request, 'mytemplates/place_bid.html', {'product': product})



def close_bidding_and_notify():
    ended_products = BiddingProduct.objects.filter(end_time__lt=timezone.now(), notified=False)

    for product in ended_products:
        winner_bid = product.highest_bid()

        if winner_bid:
            # Notify winner
            Notification.objects.create(
                user=winner_bid.user,
                message=f"🎉 Congratulations! You won the bid for '{product.product_name}' at Rs {winner_bid.amount}.",
                type='bid'
            )

            # Notify losers
            losing_bids = Bid.objects.filter(product=product).exclude(user=winner_bid.user).distinct('user')
            for bid in losing_bids:
                Notification.objects.create(
                    user=bid.user,
                    message=f"❌ You lost the bid for '{product.product_name}'. Better luck next time!",
                    type='bid'
                )

        product.notified = True  # ✅ Add 'notified' boolean to BiddingProduct model
        product.save()




from django.contrib.admin.views.decorators import staff_member_required
from .models import BiddingProduct, Bid

@staff_member_required
def admin_manage_bidding(request):
    form = BiddingProductForm()

    if request.method == 'POST':
        if 'edit_id' in request.POST:
            instance = get_object_or_404(BiddingProduct, id=request.POST['edit_id'])
            form = BiddingProductForm(request.POST, request.FILES, instance=instance)
        else:
            form = BiddingProductForm(request.POST, request.FILES)

        if form.is_valid():
            new_product = form.save()

            # ✅ Notify all non-staff users
            from .models import Notification, CustomUser
            for user in CustomUser.objects.filter(is_superuser=False, is_active=True):
                Notification.objects.create(
                    user=user,
                    message=f"📢 New bidding started for {new_product.product_name}. Place your bid now!",
                    type='bid'
                )

            messages.success(request, "Bidding product saved successfully!")
            return redirect('admin_bidding')

    status_filter = request.GET.get('status')
    bidding_items = BiddingProduct.objects.all()

    # Filter logic
    if status_filter == 'active':
        bidding_items = [item for item in bidding_items if item.is_active()]
    elif status_filter == 'closed':
        bidding_items = [item for item in bidding_items if not item.is_active()]

    context = {
        'form': form,
        'bidding_items': bidding_items,
    }
    return render(request, 'mytemplates/admin_bidding.html', context)


# Admin - Delete Bidding Product
@staff_member_required
def delete_bidding_product(request, product_id):
    product = get_object_or_404(BiddingProduct, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('admin_bidding')


@staff_member_required
def edit_bidding_product(request, product_id):
    product = get_object_or_404(BiddingProduct, id=product_id)

    if request.method == 'POST':
        form = BiddingProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('admin_bidding')
    else:
        form = BiddingProductForm(instance=product)

    return render(request, 'mytemplates/edit_bidding_product.html', {'form': form, 'product': product})


# Admin - Add/Edit Bidding Products
@login_required
def admin_bidding_view(request):
    if request.method == 'POST':
        form = BiddingProductForm(request.POST, request.FILES)
        if form.is_valid():
            # If editing an existing product
            if 'id' in request.POST:
                bidding_product = get_object_or_404(BiddingProduct, id=request.POST['id'])
                form = BiddingProductForm(request.POST, request.FILES, instance=bidding_product)
            # Save the product
            form.save()
            messages.success(request, "Bidding product saved successfully!")
            return redirect('admin_bidding')
    else:
        form = BiddingProductForm()
    return render(request, 'mytemplates/admin_bidding.html', {'form': form})


from .models import Bid, BiddingProduct
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def view_bidders(request, product_id):
    product = get_object_or_404(BiddingProduct, id=product_id)
    bids = Bid.objects.filter(product=product).order_by('-amount')  # Highest bid first
    return render(request, 'mytemplates/view_bidders.html', {
        'product': product,
        'bids': bids
    })


from django.contrib.admin.views.decorators import staff_member_required

from .forms import BiddingProductForm
from .models import BiddingProduct

@staff_member_required
def add_bidding_product(request):
    if request.method == 'POST':
        form = BiddingProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)

            if timezone.is_naive(product.start_time):
                product.start_time = timezone.make_aware(product.start_time)
            if timezone.is_naive(product.end_time):
                product.end_time = timezone.make_aware(product.end_time)

            product.save()
            messages.success(request, "Bidding product added!")
        else:
            messages.error(request, "Please correct the form errors.")
    return redirect('admin_bidding')




def admin_bidding_view(request):
    status = request.GET.get('status', '')
    items = BiddingProduct.objects.all()

    if status == 'active':
        items = [item for item in items if item.is_active()]
    elif status == 'closed':
        items = [item for item in items if not item.is_active()]

    form = BiddingProductForm()

    context = {
        'bidding_items': items,
        'form': form,
        'product_names': [item.product_name for item in items],
        'bid_counts': [item.bid_count() for item in items],
    }
    return render(request, 'mytemplates/admin_bidding.html', context)


def product(request):
    admin_products = Product.objects.filter(user__is_superuser=True)
    return render(request, 'mytemplates/product.html', {'products': admin_products})


# ---------- AUTH ----------
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import authenticate, login as auth_login


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # ✅ Add welcome toast here
            messages.success(request, f"Welcome {user.first_name}!")

            # Redirect based on role
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'is_vendor') and user.is_vendor:
                return redirect('vendor_dashboard')
            else:
                return redirect('home')  # ✅ Your customer home page

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'mytemplates/login.html', {'form': form})



def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('start')

from django.contrib.auth import login

from django.contrib.auth import get_user_model
User = get_user_model()

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_vendor = request.POST.get('is_vendor') == 'on'
        store_name = request.POST.get('store_name')
        store_description = request.POST.get('store_description')

        errors = {}

        if User.objects.filter(username=username).exists():
            errors['username_error'] = "Username already exists."

        if User.objects.filter(email=email).exists():
            errors['email_error'] = "Email already registered."

        if password != confirm_password:
            errors['password_error'] = "Passwords do not match."

        if errors:
            return render(request, 'mytemplates/register.html', {
                'errors': errors,
                'values': request.POST
            })

        #  Create user first without custom fields
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
        )

        #  Then assign custom fields manually
        if hasattr(user, 'is_vendor'):
            user.is_vendor = is_vendor
        if hasattr(user, 'role'):
            user.role = 'vendor' if is_vendor else 'customer'
        user.save()

        #  Create Vendor profile if vendor
        if is_vendor:
            Vendor.objects.create(
                user=user,
                store_name=store_name or f"{username}'s Store",
                store_description=store_description or "This is a vendor store."
            )

        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('login')

    return render(request, 'mytemplates/register.html', {'values': {}})


# ---------- ADMIN ----------
def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    user_counts = {
        'admin': User.objects.filter(is_staff=True).count(),
        'customer': User.objects.filter(is_staff=False).count()
    }
    order_status_counts = Order.objects.values('status').annotate(count=Count('status'))
    category_counts = Product.objects.values('category').annotate(count=Count('category'))

    context = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'user_counts': user_counts,
        'order_status_counts': order_status_counts,
        'category_counts': category_counts
    }
    return render(request, 'mytemplates/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all()
    return render(request, 'mytemplates/admin_users.html', {'users': users})

@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.filter(user__is_staff=True)
    return render(request, 'mytemplates/admin_products.html', {'products': products})

@user_passes_test(is_admin)
def admin_all_orders(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'mytemplates/admin_orders.html', {'orders': orders})

@user_passes_test(is_admin)
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get("status")

    if new_status in ['pending', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        order.save()
        messages.success(request, "Order status updated successfully.")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect('admin_all_orders')

@user_passes_test(is_admin)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('admin_products')  # ✅ Redirect after adding product
    else:
        form = ProductForm()

    return render(request, 'mytemplates/create_product.html', {'form': form})




@user_passes_test(is_admin)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_products')
    return render(request, 'mytemplates/update_product.html', {'form': form})

@user_passes_test(is_admin)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_products')
    return render(request, 'mytemplates/delete_product.html', {'product': product})

# ---------- CART ----------
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    size_choices = ['S', 'M', 'L', 'XL', 'Free']

    return render(request, 'mytemplates/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'size_choices': size_choices,
    })


@login_required
def update_cart(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                item_id = key.split('_')[1]
                item = get_object_or_404(CartItem, id=item_id, user=request.user)
                item.quantity = int(value)
                item.save()
            elif key.startswith('size_'):
                item_id = key.split('_')[1]
                item = get_object_or_404(CartItem, id=item_id, user=request.user)
                item.size = value
                item.save()
        messages.success(request, "Cart updated successfully.")
    return redirect('cart')

from django.contrib.auth.decorators import login_required
from .models import CartItem

@login_required
def remove_cart_item(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id, user=request.user)
        item.delete()
        messages.success(request, "Item removed from cart.")
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found or already removed.")
    return redirect('cart')


from .models import Coupon, Order, CartItem
from django.utils import timezone
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def checkout(request):
    if request.method == "POST":
        coupon_code = request.POST.get('coupon', '').strip()
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)

        discount = Decimal(0.00)
        final_total = total
        coupon_obj = None

        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(
                    coupon_code__iexact=coupon_code,
                    is_used=False,
                    expiry_date__gte=timezone.now()
                )
                discount = (coupon_obj.discount_percentage / 100) * total
                final_total = total - discount
            except Coupon.DoesNotExist:
                messages.warning(request, "Invalid or expired coupon.")

        # ✅ Create orders for each cart item and decrease stock
        for item in cart_items:
            if item.product.quantity >= item.quantity:
                # Decrease stock
                item.product.quantity -= item.quantity
                item.product.save()

                # Create order for each product
                Order.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.product.price * item.quantity,
                    status='pending',
                    payment_method=payment_method,
                )
            else:
                messages.error(request, f"Not enough stock for {item.product.product_name}.")
                return redirect('cart')

        # If coupon applied, mark it used
        if coupon_obj:
            coupon_obj.is_used = True
            coupon_obj.save()

        # Clear cart after successful order
        cart_items.delete()

        messages.success(request, f"Order placed successfully! Final amount: Rs. {final_total:.2f}")
        return redirect('user_orders')

    return redirect('cart')




# ---------- WISHLIST ----------
@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'mytemplates/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    exists = WishlistItem.objects.filter(user=request.user, product=product).exists()
    if exists:
        messages.warning(request, f"{product.product_name} is already in your wishlist.")
    else:
        WishlistItem.objects.create(user=request.user, product=product)
        messages.success(request, f"{product.product_name} added to your wishlist!")
    return redirect('product')

@login_required
def remove_wishlist_item(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    item.delete()
    return redirect('wishlist')


#
# @login_required
# def buy_now_checkout(request):
#     if request.method == 'POST':
#         try:
#             product_id = request.POST.get('product_id')
#             quantity = int(request.POST.get('quantity'))
#             size = request.POST.get('size')
#             name = request.POST.get('name')
#             phone = request.POST.get('phone')
#             address = request.POST.get('address')
#             payment_method = request.POST.get('payment_method')
#
#             # Limit quantity to 5
#             if quantity > 5:
#                 messages.error(request, "You cannot order more than 5 units of a product.")
#                 return redirect('product')
#
#             product = get_object_or_404(Product, id=product_id)
#
#             if quantity < 1:
#                 messages.error(request, "Quantity must be at least 1.")
#                 return redirect('product')
#
#             # Ensure there's enough stock
#             if product.quantity >= quantity:
#                 product.quantity -= quantity  # Decrease the quantity
#                 product.save()  # Save the updated product quantity
#             else:
#                 messages.error(request, f"Not enough stock for {product.product_name}.")
#                 return redirect('product')
#
#             total_price = product.price * quantity
#
#             # Create the order
#             Order.objects.create(
#                 user=request.user,              # ✅ FK to authenticated user
#                 product=product,
#                 quantity=quantity,
#                 total_price=total_price,
#                 status='pending',
#             )
#
#             messages.success(request, "Order placed successfully!")
#             return redirect('user_orders')
#
#         except Exception as e:
#             messages.error(request, f"Something went wrong: {str(e)}")
#             return redirect('product')
#
#     return redirect('product')


@login_required
def buy_now_checkout(request):
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity'))
            size = request.POST.get('size')
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')

            # Limit quantity
            if quantity > 5:
                messages.error(request, "You cannot order more than 5 units of a product.")
                return redirect('product')

            product = get_object_or_404(Product, id=product_id)

            if quantity < 1:
                messages.error(request, "Quantity must be at least 1.")
                return redirect('product')

            # ✅ Check and Decrease stock
            if product.quantity >= quantity:
                product.quantity -= quantity
                product.save()
            else:
                messages.error(request, f"Not enough stock for {product.product_name}.")
                return redirect('product')

            total_price = product.price * quantity

            # ✅ Create Order
            Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=total_price,
                status='pending',
                payment_method=payment_method,  # ✅
            )

            messages.success(request, "Order placed successfully!")
            return redirect('user_orders')

        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('product')

    return redirect('product')


@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'mytemplates/orders.html', {'orders': orders})



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size', 'M')
    quantity = int(request.POST.get('quantity', 1))

    # ✅ Match item by user, product, and size
    item = CartItem.objects.filter(user=request.user, product=product, size=size).first()

    if item:
        item.quantity += quantity
        item.save()
    else:
        CartItem.objects.create(user=request.user, product=product, size=size, quantity=quantity)

    messages.success(request, f"{product.product_name} added to cart.")
    return redirect('cart')



@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status.lower() == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Order has been cancelled.")
    else:
        messages.warning(request, "Only pending orders can be cancelled.")
    return redirect('user_orders')


def contact_us_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            message=message
        )
        messages.success(request, "Your message has been sent!")
        return redirect('contact')  # or wherever your contact page URL name is

    return render(request, 'mytemplates/contact.html')


from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ContactMessage

@login_required
def admin_messages_view(request):
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    paginator = Paginator(messages_list, 10)  # Show 5 messages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mytemplates/admin_messages.html', {'page_obj': page_obj})


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import ProductForm

# Helper to check if user is a vendor
def is_vendor(user):
    return hasattr(user, 'is_vendor') and user.is_vendor

# Vendor Dashboard
from collections import defaultdict
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import Order
@login_required(login_url='login')
def vendor_dashboard(request):
    orders = Order.objects.filter(product__user=request.user)

    # Order Status Count
    status_counts = defaultdict(int)
    for status in ['pending', 'shipped', 'delivered', 'cancelled']:
        status_counts[status] = orders.filter(status=status).count()

    # Monthly Orders
    monthly_orders_qs = orders.annotate(month=TruncMonth('order_date')).values('month').annotate(count=Count('order_id')).order_by('month')
    monthly_orders = {o['month'].strftime('%b %Y'): o['count'] for o in monthly_orders_qs}

    # Top Products
    top_products = orders.values('product__product_name').annotate(total=Count('order_id')).order_by('-total')[:5]

    context = {
        'total_products': request.user.product_set.count(),
        'total_orders': orders.count(),
        'status_counts': status_counts,
        'monthly_orders': monthly_orders,
        'top_products': top_products,
    }
    return render(request, 'mytemplates/vendor_dashboard.html', context)


# Vendor Product List
@login_required
@user_passes_test(is_vendor)
def vendor_products(request):
    products = Product.objects.filter(user=request.user)
    return render(request, 'mytemplates/vendor_products.html', {'products': products})


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import VendorProductForm

@login_required
def vendor_product_form(request, pk=None):
    product = get_object_or_404(Product, pk=pk, user=request.user) if pk else None
    form = VendorProductForm(request.POST or None, request.FILES or None, instance=product)
    title = "Edit Product" if pk else "Add Product"

    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.user = request.user  # ✅ assign the logged-in vendor
        product.save()
        form.save_m2m()  # ✅ required for saving ManyToMany fields like size and age_group
        messages.success(request, f"Product {'updated' if pk else 'added'} successfully!")
        return redirect('vendor_products')

    return render(request, 'mytemplates/vendor_product_form.html', {
        'form': form,
        'title': title
    })

# from django.shortcuts import get_object_or_404
#
# def vendor_product_detail(request, product_id):
#     product = get_object_or_404(Product.objects.prefetch_related('age_groups', 'sizes'), id=product_id)
#     vendor_id = product.user.id if product.user.is_vendor else None
#
#     return render(request, 'mytemplates/vendor_product_details.html', {
#         'product': product,
#         'vendor_id': vendor_id,
#     })
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from .models import Product

from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from .models import Product


def vendor_product_detail(request, product_id):
    product = get_object_or_404(Product.objects.prefetch_related('age_groups', 'sizes'), id=product_id)
    vendor_id = product.user.id if product.user.is_vendor else None

    # Handle the form submission to check the age group
    if request.method == 'POST':
        selected_age_group = request.POST.get('age_group')

        print(f"Selected Age Group: {selected_age_group}")

        # Check if the selected age group is valid for the product
        if selected_age_group not in [age_group.name for age_group in product.age_groups.all()]:
            print("Invalid Age Group Selected!")
            messages.error(request, "Sorry, this product is not available for the selected Age Group.")
        else:
            print("Valid Age Group Selected!")

    return render(request, 'mytemplates/vendor_product_details.html', {
        'product': product,
        'vendor_id': vendor_id,
    })


# Vendor Delete Product
@login_required
@user_passes_test(is_vendor)
def vendor_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('vendor_products')
    return render(request, 'mytemplates/vendor_delete_products.html', {'product': product})

# Vendor Orders
@login_required
@user_passes_test(is_vendor)
def vendor_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.filter(id=order_id, product__user=request.user).first()

        if order:
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order_id} status updated to {new_status.title()}.")

    orders = Order.objects.filter(product__user=request.user).select_related('product', 'user')
    return render(request, 'mytemplates/vendor_orders.html', {'orders': orders})



# @login_required
# def vendor_add_product(request):
#     form = ProductForm(request.POST or None, request.FILES or None)
#     if request.method == 'POST' and form.is_valid():
#         product = form.save(commit=False)
#         product.user = request.user
#         product.save()
#         messages.success(request, "Product added successfully!")
#         return redirect('vendor_products')
#     return render(request, 'mytemplates/vendor_product_form.html', {'form': form, 'title': 'Add Product'})

from .forms import VendorProductForm

@login_required
def vendor_add_product(request):
    form = VendorProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        form.save_m2m()  # VERY IMPORTANT because of ManyToManyField
        messages.success(request, "Product added successfully!")
        return redirect('vendor_products')
    return render(request, 'mytemplates/vendor_product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def vendor_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        form = VendorProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('vendor_products')
    else:
        form = VendorProductForm(instance=product)
    return render(request, 'mytemplates/vendor_product_form.html', {'form': form, 'title': 'Edit Product'})

# from .models import AgeGroup
#
# def vendor_store(request, vendor_id):
#     vendor = get_object_or_404(CustomUser, id=vendor_id, is_vendor=True)
#     products = Product.objects.filter(user=vendor)
#
#     # Filters
#     category = request.GET.get('category')
#     age_group = request.GET.get('age_group')
#
#     if category:
#         products = products.filter(category__iexact=category)
#
#     if age_group:
#         try:
#             age_group_obj = AgeGroup.objects.get(label=age_group)
#             products = products.filter(age_group__label=age_group)
#         except AgeGroup.DoesNotExist:
#             products = Product.objects.none()
#
#     # Ratings
#     for product in products:
#         product.avg_rating = product.rating_set.aggregate(avg=Avg('rating'))['avg']
#         product.latest_review = product.rating_set.last().review if product.rating_set.exists() else None
#
#     all_ratings = []
#     for product in products:
#         ratings = product.rating_set.values_list('rating', flat=True)
#         all_ratings.extend(ratings)
#
#     vendor_avg_rating = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else None
#
#     context = {
#         'vendor': vendor,
#         'products': products,
#         'vendor_avg_rating': vendor_avg_rating,
#     }
#     return render(request, 'mytemplates/vendor_store.html', context)
from django.db.models import Avg
from .models import AgeGroup, Product

def vendor_store(request, vendor_id):
    vendor = get_object_or_404(CustomUser, id=vendor_id, is_vendor=True)
    products = Product.objects.filter(user=vendor)

    # Filters
    category = request.GET.get('category')
    age_group = request.GET.get('age_group')

    if category:
        products = products.filter(category__iexact=category)

    if age_group:
        try:
            # Filter by Age Group
            age_group_obj = AgeGroup.objects.get(label=age_group)
            products = products.filter(age_groups__label=age_group_obj.label)
        except AgeGroup.DoesNotExist:
            products = Product.objects.none()

    # Ratings: Efficient calculation of avg_rating and latest review for all products
    products = products.annotate(
        avg_rating=Avg('rating__rating'),
        latest_review=Max('rating__timestamp')  # Latest review date (optional)
    )

    # Calculate vendor's average rating
    all_ratings = [rating for product in products for rating in product.rating_set.values_list('rating', flat=True)]
    vendor_avg_rating = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else None

    context = {
        'vendor': vendor,
        'products': products,
        'vendor_avg_rating': vendor_avg_rating,
    }
    return render(request, 'mytemplates/vendor_store.html', context)



@login_required
def vendor_profile(request):
    vendor = Vendor.objects.filter(user=request.user).first()

    if request.method == 'POST':
        store_name = request.POST.get('store_name')
        store_description = request.POST.get('store_description')
        logo = request.FILES.get('logo')

        if vendor:
            vendor.store_name = store_name
            vendor.store_description = store_description
            if logo:
                vendor.logo = logo
            vendor.save()
            messages.success(request, "Profile updated successfully.")
        else:
            Vendor.objects.create(
                user=request.user,
                store_name=store_name,
                store_description=store_description,
                logo=logo
            )
            messages.success(request, "Vendor profile created successfully.")

        return redirect('vendor_profile')

    return render(request, 'mytemplates/vendor_profile.html', {'vendor': vendor})

from django.utils.dateparse import parse_date

from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.dateparse import parse_date
import csv
from .models import Order

@login_required
def vendor_payment_report(request):
    method_filter = request.GET.get('method')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    orders = Order.objects.filter(product__user=request.user)

    if method_filter in ['eSewa', 'COD']:
        orders = orders.filter(payment_method=method_filter)

    if start_date:
        orders = orders.filter(order_date__date__gte=parse_date(start_date))
    if end_date:
        orders = orders.filter(order_date__date__lte=parse_date(end_date))

    orders = orders.order_by('-order_date')

    esewa_total = orders.filter(payment_method='eSewa', status='delivered').aggregate(Sum('total_price'))['total_price__sum'] or 0
    cod_total = orders.filter(payment_method='COD', status='delivered').aggregate(Sum('total_price'))['total_price__sum'] or 0

    return render(request, 'mytemplates/vendor_payment_report.html', {
        'orders': orders,
        'esewa_total': esewa_total,
        'cod_total': cod_total,
        'selected_method': method_filter,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def export_payment_report_excel(request):
    orders = Order.objects.filter(product__user=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vendor_payment_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product', 'Customer', 'Amount', 'Payment Method', 'Status', 'Date'])

    for order in orders:
        writer.writerow([
            order.id,
            order.product.product_name,
            order.user.username,
            order.total_price,
            order.payment_method,
            order.status,
            order.order_date.strftime("%Y-%m-%d")
        ])

    return response


# views.py
from django.shortcuts import render, redirect
from .models import Chat
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required(login_url='login')
def vendor_chat_page(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Chat.objects.create(user=request.user.username, message=message, timestamp=timezone.now())
            return redirect('vendor_messages')

    chats = Chat.objects.all().order_by('timestamp')
    return render(request, 'mytemplates/vendor_chat.html', {'chats': chats})

from .models import Vendor

from MS.models import CustomUser

def all_vendors(request):
    vendors = CustomUser.objects.filter(is_vendor=True)
    return render(request, 'mytemplates/all_vendors.html', {'vendors': vendors})


from django.http import JsonResponse
from .models import Vendor, Chat

@login_required
def get_chat_messages(request, vendor_id):
    messages = Chat.objects.filter(vendor_id=vendor_id).order_by('timestamp')
    data = [{"sender": msg.sender.username, "message": msg.message} for msg in messages]
    return JsonResponse({"messages": data})

@login_required
@require_POST
def send_chat_message(request):
    vendor_id = request.POST.get('vendor_id')
    message = request.POST.get('message')
    vendor = get_object_or_404(Vendor, id=vendor_id)

    Chat.objects.create(
        sender=request.user,
        vendor=vendor,
        message=message
    )
    return JsonResponse({'status': 'success'})

@login_required
def customer_chat_with_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    messages = Chat.objects.filter(vendor=vendor, sender=request.user).order_by('timestamp')

    if request.method == 'POST':
        msg = request.POST.get('message')
        Chat.objects.create(sender=request.user, vendor=vendor, message=msg)
        return redirect('customer_chat_with_vendor', vendor_id=vendor.id)

    return render(request, 'mytemplates/customer_chat.html', {
        'vendor': vendor,
        'messages': messages
    })


from .models import Notification, Chat, ThriftProduct


from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Notification, Chat

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Notification, Chat

@login_required
def notifications_view(request):
    user = request.user

    # ✅ Mark all notifications as read when visited
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    bid_notifications = Notification.objects.filter(user=user, type='bid').order_by('-timestamp')
    general_notifications = Notification.objects.filter(user=user, type='general').order_by('-timestamp')
    thrift_notifications = Notification.objects.filter(user=user, type='thrift').order_by('-timestamp')

    chat_messages = Chat.objects.filter(Q(sender=user) | Q(thrift__user=user)).order_by('-timestamp')

    context = {
        'bid_notifications': bid_notifications,
        'general_notifications': general_notifications,
        'thrift_notifications': thrift_notifications,
        'chats': chat_messages,
        'unread_notifications': 0,  # ✅ Set to 0 since they are now read
        'unread_messages': chat_messages.exclude(sender=user).count(),
    }
    return render(request, 'mytemplates/notifications.html', context)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})



@login_required
def delete_notification(request, note_id):
    notif = get_object_or_404(Notification, id=note_id, user=request.user)
    notif.delete()
    return redirect('notifications')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')


def product(request):
    products = Product.objects.filter(user__is_superuser=True)

    # Filters
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category:
        products = products.filter(category__iexact=category)

    try:
        if min_price:
            products = products.filter(price__gte=float(min_price))
        if max_price:
            products = products.filter(price__lte=float(max_price))
    except ValueError:
        pass

    return render(request, 'mytemplates/product.html', {'products': products})


from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'mytemplates/product_details.html', {'product': product})

from django.utils import timezone
from .models import Bid, BiddingProduct

from collections import defaultdict

@login_required
def bidding_history(request):
    user_bids = Bid.objects.filter(user=request.user).order_by('-bid_time')
    now = timezone.now()

    # Group bids by product
    bid_groups = defaultdict(list)
    for bid in user_bids:
        bid_groups[bid.product].append(bid)
    for product in bid_groups.keys():
        highest_bid = Bid.objects.filter(product=product).order_by('-amount').first()
        product.highest_bid = highest_bid

    return render(request, 'mytemplates/bidding_history.html', {
        'bid_groups': bid_groups.items(),
        'now': now,
    })



from django.http import JsonResponse
from .models import Coupon
from datetime import datetime
from django.utils import timezone

def apply_coupon(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')

        try:
            coupon = Coupon.objects.get(coupon_code__iexact=coupon_code, is_used=False)
            if coupon.expiry_date < timezone.now():
                return JsonResponse({'success': False, 'message': 'Coupon expired.'})

            total_price = 0
            cart_items = CartItem.objects.filter(user=request.user)
            for item in cart_items:
                total_price += item.product.price * item.quantity

            discount_amount = total_price * (coupon.discount_percentage / 100)
            new_total = total_price - discount_amount

            return JsonResponse({
                'success': True,
                'discount': coupon.discount_percentage,
                'new_total': round(new_total, 2)
            })
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or used coupon.'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})
from .models import Coupon



from .models import Coupon


from django.utils import timezone

@login_required
def admin_coupons(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')
    coupons = Coupon.objects.all().order_by('-expiry_date')
    now = timezone.now()
    return render(request, 'mytemplates/admin_coupons.html', {'coupons': coupons, 'now': now})


def add_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount_percentage = request.POST.get('discount_percentage')
        expiry_date = request.POST.get('expiry_date')

        # Check if coupon code already exists
        if Coupon.objects.filter(coupon_code__iexact=coupon_code).exists():
            messages.error(request, 'Coupon code already exists! Please use a different one.')
            return redirect('add_coupon')

        # Create new coupon
        coupon = Coupon(
            coupon_code=coupon_code,
            discount_percentage=discount_percentage,
            expiry_date=expiry_date
        )
        coupon.save()

        messages.success(request, 'Coupon added successfully!')
        return redirect('admin_coupons')

    return render(request, 'mytemplates/add_coupon.html')

def edit_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, coupon_id=coupon_id)
    if request.method == 'POST':
        coupon.coupon_code = request.POST['coupon_code']
        coupon.discount_percentage = request.POST['discount_percentage']
        coupon.expiry_date = request.POST['expiry_date']
        coupon.save()
        messages.success(request, 'Coupon updated successfully!')
        return redirect('admin_coupons')

    return render(request, 'mytemplates/edit_coupon.html', {'coupon': coupon})


def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, coupon_id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully!')
    return redirect('admin_coupons')

from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse
import csv

@login_required
def admin_payment_report(request):
    if not request.user.is_superuser:
        return redirect('home')

    orders = Order.objects.all()

    # Filtering
    selected_method = request.GET.get('method')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if selected_method:
        orders = orders.filter(payment_method=selected_method)
    if start_date:
        orders = orders.filter(order_date__date__gte=start_date)
    if end_date:
        orders = orders.filter(order_date__date__lte=end_date)

    esewa_total = orders.filter(payment_method='eSewa').aggregate(Sum('total_price'))['total_price__sum'] or 0
    cod_total = orders.filter(payment_method='COD').aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_amount = esewa_total + cod_total

    return render(request, 'mytemplates/admin_payment_report.html', {
        'orders': orders,
        'esewa_total': esewa_total,
        'cod_total': cod_total,
        'total_amount': total_amount,
        'selected_method': selected_method,
        'start_date': start_date,
        'end_date': end_date,
    })


# @login_required
# def export_admin_payment_report(request):
#     if not request.user.is_superuser:
#         return redirect('home')
#
#     orders = Order.objects.all()
#
#     # Apply same filtering here too
#     selected_method = request.GET.get('method')
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#
#     if selected_method:
#         orders = orders.filter(payment_method=selected_method)
#     if start_date:
#         orders = orders.filter(order_date__date__gte=start_date)
#     if end_date:
#         orders = orders.filter(order_date__date__lte=end_date)
#
#     # Create CSV
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="admin_payment_report.csv"'
#
#     writer = csv.writer(response)
#     writer.writerow(['Order ID', 'Product', 'Customer', 'Amount (Rs)', 'Payment Method', 'Status', 'Order Date'])
#
#     for order in orders:
#         writer.writerow([
#             order.id,
#             order.product.product_name,
#             order.user.username,
#             order.total_price,
#             order.payment_method,
#             order.status,
#             order.order_date.strftime('%Y-%m-%d'),
#         ])
#
#     return response

import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def export_admin_payment_report(request):
    if not request.user.is_superuser:
        return redirect('home')

    orders = Order.objects.all()

    # Apply same filtering
    selected_method = request.GET.get('method')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if selected_method:
        orders = orders.filter(payment_method=selected_method)
    if start_date:
        orders = orders.filter(order_date__date__gte=start_date)
    if end_date:
        orders = orders.filter(order_date__date__lte=end_date)

    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admin_payment_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['SN', 'Product', 'Customer', 'Amount (Rs)', 'Payment Method', 'Status', 'Order Date'])

    # Serial number counter
    for idx, order in enumerate(orders, start=1):
        writer.writerow([
            idx,  # << ✅ Here serial number
            order.product.product_name,
            order.user.username,
            order.total_price,
            order.payment_method,
            order.status,
            order.order_date.strftime('%Y-%m-%d'),
        ])

    return response
