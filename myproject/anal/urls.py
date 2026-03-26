from django.urls import path
from . import views

app_name = 'anal'

urlpatterns = [
    path('anal/<int:dataset_id>/', views.anal, name='anal'),
    path('upload/', views.upload_dataset_view, name='upload_dataset'),
    path('demo/', views.demo, name='demo'),
    path('demo2/', views.demo2, name='demo2'),
    path('category/', views.category, name='category'),
    path('price/', views.price, name='price'),
    path('price-2/', views.price2, name='price-2'),
    path('age/', views.age, name='age'),
    path('age-2/', views.age2, name='age-2'),
    path('age-select/', views.ageselect, name='age-select'),
    path('gender/', views.gender, name='gender'), 
    path('month/', views.month, name='month'),    
    path('home/', views.home_view, name='homepage'),
    path('1-2/', views.onetwo, name='1-2'),
    path('1-3/', views.onethree, name='1-3'),
    path('1-4/', views.onefour, name='1-4'),
    path('1-5/', views.onefive, name='1-5'),
    path('2-3/', views.twothree, name='2-3'),
    path('2-4/', views.twofour, name='2-4'),
    path('2-5/', views.twofive, name='2-5'),
    path('3-4/', views.threefour, name='3-4'),
    path('3-5/', views.threefive, name='3-5'),
]
