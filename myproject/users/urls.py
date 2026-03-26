from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', LogoutView.as_view(next_page='/'), name="logout"),
    path("admin/", admin.site.urls),
    path('feedback/', views.feedback, name="feedback"),
    path('support/', views.support, name="support"),
]
