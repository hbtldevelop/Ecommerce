from home import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("signup1/",views.signup1, name="signup1"),  
    path("signup/",views.signup, name="signup"),  
    path("login/",views.login, name= 'login'), 
    path("product/<str:pi>/",views.viewProduct, name='ViewProducts'),
    path("product/",views.viewProducts, name="allProducts"),
    path("cart/<str:username>/",views.cart,name="Cart"),
    path('updateCart/<str:opr>/',views.updateCart,name= "UpdateCart"),
    path("order/address/<str:username>/",views.address,name="view address"), 
    path("order/placeorder/",views.placeOrder,name="Order"), 
    path("user/<str:username>/",views.viewUser,name = "User Data"),
    path('search/', views.ProductsSearchView.as_view(), name='products-search'),
]  

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
