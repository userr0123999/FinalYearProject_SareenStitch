from django.urls import path
from . import views


urlpatterns = [
# --- AUTH ---
path('', views.start, name='start'),
path('home/', views.home, name='home'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('register/', views.register, name='register'),
path('forgotpassword/', views.forgotpassword, name='forgotpassword'),

    # required for reset to work after email
path('reset/<uidb64>/<token>/', views.custom_reset_password_confirm, name='password_reset_confirm'),


path('profile/', views.profile_view, name='profile'),
path('search/', views.search_products, name='search_products'),
path('your-bidding/', views.bidding_history, name='bidding_history'),





# --- PUBLIC PAGES ---
path('product/', views.product, name='product'),
path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),



#-------------------------------BIDDINGGGG--------------------------------------------------
# path('bidding/', views.bidding, name='bidding'),
    path('bidding/', views.bidding_list_view, name='bidding_list'),
    path('place-bid/<int:product_id>/', views.place_bid_view, name='place_bid'),
    path('dashboard/bidding/', views.admin_manage_bidding, name='admin_bidding'),
    path('dashboard/bidding/delete/<int:product_id>/', views.delete_bidding_product, name='delete_bidding_product'),
    path('dashboard/bidding/edit/<int:product_id>/', views.edit_bidding_product, name='edit_bidding_product'),
    path('dashboard/bidding/bids/<int:product_id>/', views.view_bidders, name='view_bidders'),
    path('dashboard/bidding/add/', views.add_bidding_product, name='add_bidding_product'),
    path('bidding-detail/<int:product_id>/', views.bidding_detail, name='bidding_detail'),






#-----Thrift------
# path('thrift/', views.thrift, name='thrift'),
path('thrift/', views.thrift_list_view, name='thrift'),
path('thrift/post/', views.post_thrift, name='post_thrift'),
path('dashboard/thrift/', views.admin_manage_thrift, name='admin_thrift'),
path('dashboard/thrift/approve/<int:thrift_id>/', views.approve_thrift, name='approve_thrift'),
path('dashboard/thrift/reject/<int:thrift_id>/', views.reject_thrift, name='reject_thrift'),
path('dashboard/thrift/sold/<int:thrift_id>/', views.mark_thrift_sold, name='mark_thrift_sold'),
path('dashboard/thrift/delete/<int:thrift_id>/', views.delete_thrift, name='delete_thrift'),
path('thrift/add-to-cart/<int:product_id>/', views.add_thrift_to_cart, name='add_thrift_to_cart'),
path('thrift/chat/<int:thrift_id>/', views.chat_page, name='thrift_chat'),
path('thrift/<int:thrift_id>/', views.thrift_detail_view, name='thrift_detail'),




path('aboutus/', views.aboutus, name='aboutus'),
path('contact/', views.contact, name='contact'),

# --- CART ---

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),



path('cart/checkout/', views.checkout, name='checkout'),

# --- WISHLIST ---
path('wishlist/', views.wishlist_view, name='wishlist'),
path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
path('remove-wishlist/<int:item_id>/', views.remove_wishlist_item, name='remove_wishlist_item'),

# --- BUY NOW / ORDERS ---
path('buy-now-checkout/', views.buy_now_checkout, name='buy_now_checkout'),
path('orders/', views.user_orders, name='user_orders'),
path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # --- ADMIN DASHBOARD ---
path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('dashboard/users/', views.admin_users, name='admin_users'),
path('dashboard/orders/', views.admin_all_orders, name='admin_all_orders'),
path('dashboard/orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
path('dashboard/messages/', views.admin_messages_view, name='admin_messages'),

    # --- ADMIN PRODUCTS ---
path('dashboard/products/', views.admin_products, name='admin_products'),
path('dashboard/products/create/', views.create_product, name='create_product'),
path('dashboard/products/update/<int:pk>/', views.update_product, name='update_product'),
path('dashboard/products/delete/<int:pk>/', views.delete_product, name='delete_product'),




path('vendordashboard/', views.vendor_dashboard, name='vendor_dashboard'),
# Vendor Product CRUD
path('vendor/products/', views.vendor_products, name='vendor_products'),
path('vendor/products/add/', views.vendor_add_product, name='vendor_add_product'),
path('vendor/products/edit/<int:pk>/', views.vendor_edit_product, name='vendor_edit_product'),
path('vendor/products/delete/<int:pk>/', views.vendor_delete_product, name='vendor_delete_product'),

# --- VENDOR ORDERS ---
path('vendor/orders/', views.vendor_orders, name='vendor_orders'),

path('vendor/store/<int:vendor_id>/', views.vendor_store, name='vendor_store'),
path('vendor/product/<int:product_id>/', views.vendor_product_detail, name='vendor_product_details'),
path('vendor/profile/', views.vendor_profile, name='vendor_profile'),
# path('vendor/messages/', views.vendor_messages, name='vendor_messages'),
path('vendor/messages/', views.vendor_chat_page, name='vendor_chat_page'),
path('vendors/', views.all_vendors, name='all_vendors'),
path('chat/messages/<int:vendor_id>/', views.get_chat_messages, name='get_chat_messages'),
path('chat/send/', views.send_chat_message, name='send_chat_message'),
path('vendor/chat/<int:vendor_id>/', views.customer_chat_with_vendor, name='customer_chat_with_vendor'),
path('vendor/payment-report/', views.vendor_payment_report, name='vendor_payment_report'),
path('vendor/payment-report/export/', views.export_payment_report_excel, name='export_vendor_report'),



path('notifications/', views.notifications_view, name='notifications'),
path('notifications/delete/<int:note_id>/', views.delete_notification, name='delete_notification'),
path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),



path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
path('dashboard/coupons/', views.admin_coupons, name='admin_coupons'),
path('dashboard/coupons/add/', views.add_coupon, name='add_coupon'),
path('dashboard/coupons/edit/<int:coupon_id>/', views.edit_coupon, name='edit_coupon'),
path('dashboard/coupons/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),


path('dashboard/payment-report/', views.admin_payment_report, name='admin_payment_report'),
path('dashboard/payment-report/export/', views.export_admin_payment_report, name='export_admin_payment_report'),











    ]