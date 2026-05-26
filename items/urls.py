from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='account_login'),
    path('logout/', views.logout_view, name='account_logout'),
    path('register/', views.register_view, name='account_signup'),
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('verification-sent/', views.verification_sent_view, name='verification_sent'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('forgot-password/', views.forgot_password_view, name='account_reset_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='verify_reset_password'),
    path('reset-password-sent/', views.reset_password_sent_view, name='password_reset_sent'),
    path('resend-reset-email/', views.resend_reset_email_view, name='resend_reset_email'),
    path('items/', views.item_list_view, name='item_list'),
    path('items/post/', views.post_item_view, name='post_item'),
    path('items/<int:pk>/', views.item_detail_view, name='item_detail'),
    path('items/<int:pk>/claim/', views.claim_item_view, name='claim_item'),
    path('claims/<int:pk>/approve/', views.approve_claim_view, name='approve_claim'),
    path('claims/<int:pk>/reject/', views.reject_claim_view, name='reject_claim'),
    path('claims/<int:pk>/approved/', views.claim_approved_view, name='claim_approved'),
    path('my-claims/', views.my_claims_view, name='my_claims'),
    path('items/<int:pk>/edit/', views.edit_item_view, name='edit_item'),
    path('items/<int:pk>/delete/', views.delete_item_view, name='delete_item'),
    path('my-items/', views.user_items_view, name='user_items'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.account_change_password_view, name='account_change_password'),
    path('profile/delete-account/', views.delete_account_view, name='delete_account'),
    
    # Admin Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/users/', views.admin_users_view, name='admin_users'),
    path('admin-dashboard/users/<int:pk>/toggle/', views.admin_toggle_user_status, name='admin_toggle_user'),
    path('admin-dashboard/items/', views.admin_items_view, name='admin_items'),
    path('admin-dashboard/items/<int:pk>/delete/', views.admin_delete_item, name='admin_delete_item'),
]


