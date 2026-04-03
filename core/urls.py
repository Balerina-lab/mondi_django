from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Nova putanja koja prima ID magacina (npr. /magacin/1/)
    path('magacin/<int:id>/', views.warehouse_detail, name='warehouse_detail'),
    path('obrisi-artikal/<int:id>/', views.delete_item, name='delete_item'),
    path('update-stock/<int:id>/', views.update_stock, name='update_stock'),
    path('obrisi-artikal/<int:id>/', views.delete_item, name='delete_item'),
    path('izmeni-artikal/<int:id>/', views.edit_item, name='edit_item'),        
]