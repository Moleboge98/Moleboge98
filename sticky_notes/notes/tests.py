from django.test import TestCase
from django.urls import reverse
from .models import Task

class TestStickyNotesApp(TestCase):
    """
    Unit tests for a Django-based Sticky Notes application.

    These tests use Django's test client to simulate user requests and
    interact with a temporary test database, ensuring tests are isolated
    and accurately reflect the application's behavior.
    """

    def setUp(self):
        """
        Set up initial data for tests. This creates a sample task
        that can be used by multiple test methods.
        """
        self.task = Task.objects.create(
            title="Initial Task",
            description="A description for the initial task."
        )

    def test_use_case_view_all_notes(self):
        """
        Tests the use case of viewing all sticky notes on the main page.
        """

        url = reverse('note_list')
        response = self.client.get(url)

        # Check that the page loads successfully (HTTP 200 OK)
        self.assertEqual(response.status_code, 200)

        # Check that the task we created in setUp is visible on the page
        self.assertContains(response, self.task.title)

    def test_use_case_add_note(self):
        """
        Tests the use case of adding a new sticky note via a form submission.
        """
        # Assume the URL for adding a note is named 'add_note'
        url = reverse('add_note')
        note_data = {
            'title': 'New Test Note',
            'description': 'This is a brand new note.',
            'due_date': '2025-12-01'
        }

        # Simulate a POST request, as if a user submitted a form
        response = self.client.post(url, note_data)

        # Check that a new task object has been created in the database
        self.assertEqual(Task.objects.count(), 2) # The initial one + the new one

        # Check that the title of the latest task is correct
        latest_task = Task.objects.last()
        self.assertEqual(latest_task.title, 'New Test Note')

        # Check that after adding, the user is redirected (a common pattern)
        # Typically to the main list page
        self.assertEqual(response.status_code, 302)

    def test_use_case_mark_note_as_complete(self):
        """
        Tests the use case of marking a sticky note as complete.
        """
        # Assume the URL for completing a note is named 'complete_note'
        # and takes the task's ID as an argument
        url = reverse('complete_note', args=[self.task.id])

        # Simulate a POST request to the complete URL
        response = self.client.post(url)

        # Refresh the task object from the database to get its updated state
        self.task.refresh_from_db()

        # Check that the task's 'is_complete' status is now True
        self.assertTrue(self.task.is_complete)

        # Check that the user is redirected after the action
        self.assertEqual(response.status_code, 302)

    def test_use_case_delete_note(self):
        """
        Tests the use case of deleting a sticky note.
        """
        # Assume the URL for deleting a note is named 'delete_note'
        url = reverse('delete_note', args=[self.task.id])

        # Simulate a POST request to delete the note
        response = self.client.post(url)

        # Check that the task no longer exists in the database
        self.assertEqual(Task.objects.count(), 0)

        # Check for a redirect after deletion
        self.assertEqual(response.status_code, 302)

    def test_delete_nonexistent_note_returns_404(self):
        """
        Tests that the app handles trying to access a note that doesn't exist.
        """
        # Use a fake ID (e.g., 999) that doesn't exist in the database
        url = reverse('delete_note', args=[999])

        # Act: Try to access the delete page for this non-existent note
        response = self.client.post(url)

        # Assert: The server should return a 404 Not Found error
        self.assertEqual(response.status_code, 404)
