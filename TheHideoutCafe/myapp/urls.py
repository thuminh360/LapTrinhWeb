from django.urls import path
from . import views
app_name = 'myapp'
urlpatterns = [
    # Quản lý
    path('menu/quanly/', views.menu_management, name='menu_management'),
    path('menu/quanly/add/', views.add_menu_item, name='add_menu_item'),
    path('menu/quanly/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/quanly/toggle-visibility/', views.toggle_menu_item_visibility, name='toggle_menu_item_visibility'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/update_status/', views.update_order_status, name='update_order_status'),
    path('orders/chi-tiet/<int:ma_don_hang>/', views.order_detail, name='order_detail'),
    path('orders/update_payment_status/', views.update_payment_status, name='update_payment_status'),
    path('quanlyban/', views.table_management, name='table_management'),
    path('quanlyban/cap-nhat-trang-thai/', views.update_table_status, name='update_table_status'),
    path('quanlyban/them-ban/', views.create_table, name='create_table'),
    path('quanlyban/sua-ban/', views.edit_table, name='edit_table'),
    path('quanlyban/chi-tiet/<int:ma_ban>/', views.table_detail, name='table_detail'),
    path('quanlydatban/', views.booking_management, name='booking_management'),
    path('quanlydatban/them-dat-ban/', views.create_booking, name='create_booking'),
    path('quanlydatban/cap-nhat-trang-thai-dat-ban/', views.update_booking_status, name='update_booking_status'),
    path('quanlydatban/huy-dat-ban/', views.cancel_booking, name='cancel_booking'),
    path('revenue/', views.revenue_management, name='revenue_management'),
    path('reviews/', views.manage_reviews, name='manage_reviews'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),

    path('message/', views.message_view, name='message'),
    path('message/<int:phien_id>/', views.message_view, name='message'),
    # Nhân viên
    path('menu/nhanvien/', views.menu_nhanvien, name='menu_nhanvien'),


    # Khách hàng
    path('menu/khachhang/', views.menu_khachhang, name='menu_khachhang'),
    path('menu/khachhang/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('place-order/', views.place_order_mon, name='place_order_mon'),
    path('order/<int:ma_don_hang>/', views.order_detail_khach, name='order_detail'),
    path('orders/khachhang/', views.order_history, name='order_history'),
    path('order/<int:ma_don_hang>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:ma_don_hang>/reorder/', views.reorder, name='reorder'),
    path('order/<int:ma_don_hang>/rate/', views.rate_order, name='rate_order'),  # Thêm route cho đánh giá
    path('reviews/khachhang', views.public_reviews, name='public_reviews'),

    path('book-table/', views.book_table, name='book_table'),
    path('book-table/form/<int:ma_ban>/', views.book_table_form, name='book_table_form'),

    # Chuyển hướng
    path('menu/', views.redirect_based_on_role, name='redirect_based_on_role'),
]