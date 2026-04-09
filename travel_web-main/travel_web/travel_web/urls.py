from django.contrib import admin
from django.urls import path
from tweb import views
from tweb import admin_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('login_v2/', views.login_v2),
    path('sign/', views.sign),
    path('signup/', views.signup),
    path('search/', views.search),
    path('sz/', views.sz),
    path('scenic/', views.scenic, name='scenic'),
    path('add_comment/', views.add_comment),
    path('toggle_favorite/', views.toggle_favorite),
    path('profile/', views.profile),
    path('logout/', views.logout),
    path('send_reset_code/', views.send_reset_code),
    path('reset_password/', views.reset_password),
    path('update_profile/', views.update_profile),
    # 酒店相关路由
    path('hotel/', views.hotel_index, name='hotel_index'),
    path('hotel/search/', views.hotel_search, name='hotel_search'),
    path('hotel/detail/', views.hotel_detail, name='hotel_detail'),
    path('hotel/add_comment/', views.hotel_add_comment, name='hotel_add_comment'),
    path('hotel/toggle_favorite/', views.hotel_toggle_favorite, name='hotel_toggle_favorite'),
    path('hotel/pay/', views.hotel_pay, name='hotel_pay'),
    path('hotel/create_order/', views.hotel_create_order, name='hotel_create_order'),
    path('hotel/cancel_order/', views.hotel_cancel_order, name='hotel_cancel_order'),
    path('hotel/orders/', views.get_user_orders, name='get_user_orders'),
    # 交通票务路由
    path('ticket/', views.ticket_index, name='ticket_index'),
    path('ticket/train/search/', views.train_search, name='train_search'),
    path('ticket/flight/search/', views.flight_search, name='flight_search'),

    # 智能行程规划路由
    path('trip/', views.trip_index, name='trip_index'),
    path('api/trip/plan/', views.generate_itinerary, name='generate_itinerary'),
    path('api/trip/save/', views.save_itinerary, name='save_itinerary'),

    # ============ 智能AI对话模块 ============
    path('ai/', views.ai_chat_page, name='ai_chat'),
    path('ai/chat/', views.travel_chat, name='travel_chat'),
    path('ai/chat/reset/', views.reset_chat, name='reset_chat'),
    path('ai/chat/history/', views.get_conversation_history, name='get_conversation_history'),
    path('ai/scenic/intro/', views.generate_scenic_intro, name='generate_scenic_intro'),

    # ============ 后台管理系统 ============
    path('admin/', admin_views.admin_login, name='admin_login'),
    path('admin/login/', admin_views.admin_login_check, name='admin_login_check'),
    path('admin/logout/', admin_views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/stats/', admin_views.admin_get_stats, name='admin_get_stats'),
    # 用户管理
    path('admin/users/', admin_views.admin_user_list, name='admin_user_list'),
    path('admin/users/data/', admin_views.admin_get_users, name='admin_get_users'),
    path('admin/users/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
    # 评论管理
    path('admin/comments/', admin_views.admin_comment_list, name='admin_comment_list'),
    path('admin/comments/data/', admin_views.admin_get_comments, name='admin_get_comments'),
    path('admin/comments/delete/', admin_views.admin_delete_comment, name='admin_delete_comment'),
    # 订单管理
    path('admin/orders/', admin_views.admin_order_list, name='admin_order_list'),
    path('admin/orders/data/', admin_views.admin_get_orders, name='admin_get_orders'),
    path('admin/orders/update/', admin_views.admin_update_order_status, name='admin_update_order_status'),
    # 酒店管理
    path('admin/hotels/', admin_views.admin_hotel_list, name='admin_hotel_list'),
    path('admin/hotels/data/', admin_views.admin_get_hotels, name='admin_get_hotels'),
    # 景点管理
    path('admin/scenics/', admin_views.admin_scenic_list, name='admin_scenic_list'),
    path('admin/scenics/data/', admin_views.admin_get_scenics, name='admin_get_scenics'),
    path('admin/scenics/add/', admin_views.admin_add_scenic, name='admin_add_scenic'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
