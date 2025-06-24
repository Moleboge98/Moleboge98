from django.db import models
from django.urls import reverse # Used to generate URLs for objects

# Define the Note model for sticky notes
class Note(models.Model):
    """
    Represents a single sticky note in the application.
    Each note has a title, content, and timestamps for creation and last update.
    """
    title = models.CharField(max_length=200, help_text="Enter the title of your sticky note.")
    content = models.TextField(help_text="Write the content of your sticky note.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time the note was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time the note was last updated.")

    class Meta:
        """
        Meta options for the Note model.
        Orders notes by creation date in descending order by default.
        """
        ordering = ['-created_at'] # Order notes by creation date, newest first

    def __str__(self):
        """
        String representation of the Note object.
        Returns the title of the note.
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the URL to access a particular instance of the Note model.
        This is useful for redirecting after creating/updating a note.
        """
        # 'note_detail' is the name of the URL pattern for a single note
        return reverse('note_detail', args=[str(self.id)])

