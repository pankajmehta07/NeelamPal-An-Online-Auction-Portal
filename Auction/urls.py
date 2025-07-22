from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("",views.home, name="home"),
    path("search",views.search, name="search"),
    path("login",views.login_user, name="login_user"),
    path("logout",views.logout_user, name="logut"),
    path("register",views.register_user, name="regist"),
    path("createTables",views.createTables, name="createTables"),
    path("users",views.get_users, name="getusers"),
    path("addItem",views.addItem, name="addItem"),
    path("saveItem",views.saveItem, name="saveItem"),
    path("category",views.category, name="category")
]