"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from stats import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ranking/", views.ranking, name="ranking"),
    path("ranking_table/", views.ranking_table, name="ranking_table"),
    path("graph/", views.graph, name="graph"),
    path("graph_positions/", views.graph_positions, name="graph_positions"),
    path("fixtures/", views.fixtures, name="fixtures"),
    path("fixtures_list/", views.fixtures_list, name="fixtures_list"),
    path("fixtures/<int:pk>/", views.fixture_details, name="fixture_details"),
    path("fixtures/add/", views.fixture_add, name="fixture_add"),
]
