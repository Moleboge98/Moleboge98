from django import forms
from .models import Note

# Define the form for creating and updating Note objects
class NoteForm(forms.ModelForm):
    """
    A ModelForm for the Note model.
    It automatically generates form fields based on the Note model's fields.
    """
    class Meta:
        """
        Meta options for the NoteForm.
        Specifies the model to use and the fields to include in the form.
        """
        model = Note
        fields = ['title', 'content'] # Fields to be included in the form
        # You can add custom widgets for styling or specific input types
        widgets = {
            'title': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline', 'placeholder': 'Enter note title'}),
            'content': forms.Textarea(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32', 'placeholder': 'Write your note content here'}),
        }