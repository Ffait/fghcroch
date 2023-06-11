from django.urls import path, re_path

from .views import *
from croch import views

urlpatterns = [
    path('', CrochHome.as_view(), name='home'),
    path('product/<slug:product_slug>/', ShowProducts.as_view(), name='product'),
    path('category/<slug:cat_slug>/', ProdCategory.as_view(), name='category'),
    path('contacts', about, name="contacts"),
    path('add_prod', AddProd.as_view(), name='add_product'),
    path('product/<slug:product_slug>/update_prod/', UpdateProd.as_view(), name='update'),
    path('product/<slug:product_slug>/delete_prod/', DeleteProd.as_view(), name='delete'),
    path('<str:product_id>/detail/', product_detail, name='product_detail'),
    path('product/<int:product_id>/cart-add/', cart_add, name='cart_add'),
    path('cart/', cart, name='cart'),
    path('<str:item_id>/update/', item_update, name='item_update'),
    path('<str:item_id>/delete/', item_delete, name='item_delete'),
    path('create-order/', create_order, name='create_order'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('cheque/<int:pk>', Cheque.as_view(), name='cheque'),
    path('login/', LoginUser.as_view(), name="login"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('logout/', logout_user, name="logout"),
    path('user/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('user/<slug:profile_detail>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('feedback/', FeedbackCreateView.as_view(), name='feedback'),
    path('product/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view')
]