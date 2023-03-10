from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

import market.views as views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main'),
    path('sign_in', views.SiteLoginView.as_view(), name='sign_in'),
    path('sign_out', views.SiteLogoutView.as_view(), name='sign_out'),
    path('sign_up', views.RegisterView.as_view(), name='sign_up'),
    path('password_reset_form', views.UserPasswordResetView.as_view(), name='password_reset_form'),
    re_path(r'^password_reset/done/$', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<slug:uidb64>/<slug:token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', views.UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('catalogue', views.ProductList.as_view(), name='catalogue'),
    path('catalogue/<int:pk>', views.ProductDetail.as_view(), name='product'),
    path('cart', views.CartView.as_view(), name='cart'),
    path('order', views.OrderView.as_view(), name='order'),
    path('order/<int:pk>/payment', views.PaymentView.as_view(), name='payment'),
    path('order/<int:pk>/payment/confirmation', views.PaymentConfirmationView.as_view(), name='confirmation'),
    path('order/<int:pk>/payment/error', views.PaymentErrorView.as_view(), name='error'),
    path('account/<int:pk>', views.AccountDetailView.as_view(), name='account'),
    path('account/<int:pk>/update', views.AccountUpdateView.as_view(), name='profile'),
    path('account/<int:pk>/history/<int:sk>', views.OrderHistoryView.as_view(), name='history'),
    path('password_change', views.PasswordUpdateView.as_view(), name='password_change'),
    path('password_change_done', views.PasswordUpdateDone.as_view(), name='password_change_done'),
    path('moderator', views.ModeratorsView.as_view(), name='moderator'),
    path('moderator_users', views.UsersListView.as_view(), name='moderator_users'),
    path('moderator_orders', views.OrdersListView.as_view(), name='moderator_orders'),
    path('moderator_categories', views.CategoriesListView.as_view(), name='moderator_categories'),
    path('moderator_categories_create', views.CategoryCreateView.as_view(), name='moderator_categories_create'),
    path('moderator_products', views.ProductsListView.as_view(), name='moderator_products'),
    path('moderator_products_create', views.ProductCreateView.as_view(), name='moderator_products_create'),
    path('moderator_users/<int:pk>', views.UsersUpdateView.as_view(), name='moderator_users_edit'),
    path('moderator_orders/<int:pk>', views.OrdersUpdateView.as_view(), name='moderator_order_edit'),
    path('moderator_orders/un_auth/<int:pk>', views.UnAuthOrdersUpdateView.as_view(), name='moderator_unauth_order_edit'),
    path('moderator_products/<int:pk>', views.ProductUpdateView.as_view(), name='moderator_product_edit'),
    path('moderator_categories/<int:pk>', views.CategoriesDetailView.as_view(), name='moderator_categories_edit'),
    path('i18n/', include('django.conf.urls.i18n'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
