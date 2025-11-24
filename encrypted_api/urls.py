from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # AUTH ROUTES
    path('api/auth/', include('accounts.urls')),

    # MESSAGES ROUTES
    path('api/', include('api.urls')),
]
