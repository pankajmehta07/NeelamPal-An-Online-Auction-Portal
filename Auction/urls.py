from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("",views.home, name="home"),
    path("search",views.search, name="search"),
    path("bid",views.bid, name="bid"),
    path("login",views.login_user, name="login_user"),
    path("logout",views.logout_user, name="logut"),
    path("register",views.register_user, name="regist"),
    path("createTables",views.createTables, name="createTables"),
    path("addItem",views.addItem, name="addItem"),
    path("saveItem",views.saveItem, name="saveItem"),
    path("category",views.category, name="category"),
    path("item/<int:itemID>",views.item, name="item"),
    path("items",views.showItems, name="showItems"),
    path("edit",views.edit, name="edit"),
    path("updateItem",views.updateItem, name="updateItem"),
    path("deleteItem",views.deleteItem, name="deleteItem"),
    re_path(r"^profile/(?P<profile_type>bidder|organization)/(?P<id>\d+)",views.profile, name="profile"),
    path("editProfile",views.editProfile, name="editProfile"),
    path("updateProfile", views.updateProfile, name="updateProfile"),
    path("myBids", views.showBids, name="showBids")
]