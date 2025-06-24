from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView # Import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redirect the root URL '/' to your notes list
    path('', RedirectView.as_view(url='notes/', permanent=True)), # Added this line
    # Include the URLs from your 'notes' app.
    # All URLs starting with 'notes/' will be handled by the 'notes' app.
    path('notes/', include('notes.urls')),
]