from django.urls import path

from search import views

urlpatterns = [
    path("recherche/", views.search_view, name="search"),
]
