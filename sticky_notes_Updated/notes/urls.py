from django.urls import path
from . import views # Import views from the current app

# Define the app name for namespacing URLs
app_name = 'notes'

urlpatterns = [
    # Path for listing all notes (homepage of the app)
    path('', views.NoteListView.as_view(), name='note_list'),
    # Path for viewing a single note's details
    path('<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    # Path for creating a new note
    path('create/', views.NoteCreateView.as_view(), name='note_create'),
    # Path for updating an existing note (requires note's primary key)
    path('<int:pk>/update/', views.NoteUpdateView.as_view(), name='note_update'),
    # Path for deleting an existing note (requires note's primary key)
    path('<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
]
