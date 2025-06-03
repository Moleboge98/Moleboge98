import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.js';
import ErrorBoundary from './components/ErrorBoundary.js';
import { initializeFirebase, auth, db } from './utils/firebase.js';

// Initialize Firebase and make sure it's ready before rendering the app.
// This also handles potential Firebase initialization errors.
try {
    initializeFirebase();
    
    // Get the root element from the HTML
    const container = document.getElementById('root');
    
    // Create a React root
    const root = createRoot(container);

    // Render the App component wrapped in StrictMode and ErrorBoundary
    root.render(
        <StrictMode>
            <ErrorBoundary>
                <App />
            </ErrorBoundary>
        </StrictMode>
    );
} catch (error) {
    console.error("Failed to initialize Firebase or render React app:", error);
    // Display a user-friendly error message if Firebase initialization fails
    const rootElement = document.getElementById('root');
    if (rootElement) {
        rootElement.innerHTML = `
            <div class="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col items-center justify-center p-6 text-center">
                <div class="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-300 px-6 py-4 rounded-lg shadow-lg max-w-md w-full">
                    <strong class="font-bold block mb-2">Initialization Error:</strong>
                    <p>Could not connect to essential services. Please check your internet connection and try refreshing the page.</p>
                </div>
                <button onclick="window.location.reload()" class="mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-6 rounded-lg shadow-md transition-all">
                    Refresh Page
                </button>
            </div>
        `;
    }
}

