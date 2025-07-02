from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy 
from .models import Note
from .forms import NoteForm 

# List all notes (Read operation)
class NoteListView(generic.ListView):
    """
    Displays a list of all sticky notes.
    Inherits from Django's generic ListView.
    """
    model = Note # Specify the model to use
    template_name = 'notes/note_list.html' # Template to render
    context_object_name = 'note_list' # Name of the variable in the template context

# Display a single note's details (Read operation)
class NoteDetailView(generic.DetailView):
    """
    Displays the details of a single sticky note.
    Inherits from Django's generic DetailView.
    """
    model = Note #  Specify the model to use
    template_name = 'notes/note_detail.html' #  Template to render
    context_object_name = 'note' #  Name of the variable in the template context

# Create a new note (Create operation)
class NoteCreateView(generic.CreateView):
    """
    Handles the creation of a new sticky note.
    Inherits from Django's generic CreateView.
    """
    model = Note # Specify the model to create
    form_class = NoteForm # Specify the form to use for input
    template_name = 'notes/note_form.html' # Template to render the form
    # Redirect to the note list after successful creation
    success_url = reverse_lazy('notes:note_list')
    def form_valid(self, form):
        print("Form is valid, saving...")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid:", form.errors)
        return super().form_invalid(form)
# Update an existing note (Update operation)
class NoteUpdateView(generic.UpdateView):
    """
    Handles the updating of an existing sticky note.
    Inherits from Django's generic UpdateView.
    """
    model = Note # Specify the model to update
    form_class = NoteForm # Specify the form to use for input
    template_name = 'notes/note_form.html' # Template to render the form
    # Redirect to the updated note's detail page after successful update
    success_url = reverse_lazy('notes:note_list') # Or reverse_lazy('note_detail', args=[self.object.pk]) if you want to go to detail

# Delete a note (Delete operation)
class NoteDeleteView(generic.DeleteView):
    """
    Handles the deletion of a sticky note.
    Inherits from Django's generic DeleteView.
    """
    model = Note #  Specify the model to delete
    template_name = 'notes/note_confirm_delete.html' #  Template for confirmation
    # Redirect to the note list after successful deletion
    success_url = reverse_lazy('notes:note_list')

