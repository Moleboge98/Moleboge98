import React, { useState, useEffect } from 'react';
import { collection, query, where, onSnapshot } from 'firebase/firestore';
import Spinner from '../components/Spinner.js';
import StatusBadge from '../components/StatusBadge.js';
import NewSubmissionForm from './NewSubmissionForm.js';
import { createPdfCertificate, downloadPdf } from '../utils/certificateGenerator.js'; // Import certificate functions
import { db, appId } from '../utils/firebase.js'; // Import db and appId

const StudentDashboard = ({ userId, userEmail, isAuthReady }) => {
    const [submissions, setSubmissions] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [stats, setStats] = useState({ total: 0, graded: 0, average: 0 });
    const [isGeneratingCert, setIsGeneratingCert] = useState(null); // State to track certificate generation for a specific submission

    useEffect(() => {
        // Ensure Firebase services are ready and user ID is available
        if (!isAuthReady || !db || !userId) {
            if (isAuthReady && !db) {
                setError("Database service unavailable.");
            }
            setIsLoading(false);
            return;
        }

        setIsLoading(true); // Start loading

        // Create a query to fetch submissions for the current student
        const q = query(collection(db, `artifacts/${appId}/public/data/submissions`), where("studentId", "==", userId));

        // Set up a real-time listener for submissions
        const unsubscribe = onSnapshot(q, (querySnapshot) => {
            const subs = [];
            let gradedCount = 0;
            let sumOfGrades = 0;

            querySnapshot.forEach((doc) => {
                const data = { id: doc.id, ...doc.data() };
                subs.push(data);

                // Calculate graded count and sum of grades for average
                if (data.status === 'graded' && data.grade !== null && !isNaN(parseFloat(data.grade))) {
                    gradedCount++;
                    sumOfGrades += parseFloat(data.grade);
                }
            });

            // Sort submissions by submittedAt in descending order (most recent first)
            subs.sort((a, b) => (b.submittedAt?.toDate()?.getTime() || 0) - (a.submittedAt?.toDate()?.getTime() || 0));

            setSubmissions(subs); // Update submissions state
            const totalSubmissions = subs.length;
            const averageGrade = gradedCount > 0 ? (sumOfGrades / gradedCount).toFixed(1) : 0;
            setStats({ total: totalSubmissions, graded: gradedCount, average: averageGrade }); // Update stats
            setIsLoading(false); // End loading
            setError(null); // Clear any errors
        }, (err) => {
            console.error("Error fetching student submissions:", err);
            setError("Failed to load submissions.");
            setIsLoading(false); // End loading on error
        });

        // Cleanup the listener on component unmount
        return () => unsubscribe();
    }, [userId, isAuthReady, db, appId]); // Dependencies for the useEffect hook

    // Handle certificate download
    const handleDownloadCertificate = async (submission) => {
        // Check if certificate is eligible and full name is provided
        if (!submission.certificateEligible || !submission.fullNameForCertificate) {
            // Using a custom message box instead of alert()
            const messageBox = document.createElement('div');
            messageBox.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50';
            messageBox.innerHTML = `
                <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-2xl w-full max-w-sm text-center">
                    <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Certificate Not Available</h3>
                    <p class="text-gray-700 dark:text-gray-300 mb-6">This certificate is not yet available or your full name for the certificate is missing.</p>
                    <button class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg" onclick="this.parentNode.parentNode.remove()">OK</button>
                </div>
            `;
            document.body.appendChild(messageBox);
            return;
        }

        setIsGeneratingCert(submission.id); // Set loading state for the specific submission

        try {
            // Format the graded date, or use current date if not available
            const gradeDate = submission.gradedAt?.toDate() ? new Date(submission.gradedAt.toDate()).toLocaleDateString() : new Date().toLocaleDateString();
            
            // Generate the PDF certificate
            const pdfBytes = await createPdfCertificate(submission.fullNameForCertificate, gradeDate);
            
            // Trigger the PDF download
            downloadPdf(pdfBytes, `Certificate_${submission.fullNameForCertificate.replace(/ /g, '_')}.pdf`);
        } catch (e) {
            console.error("Failed to download certificate:", e);
            // Error handling for createPdfCertificate is done internally, so no alert here
        } finally {
            setIsGeneratingCert(null); // Clear loading state
        }
    };

    // Show a loading spinner if Firebase services are not yet ready
    if (!isAuthReady || !db) {
        return (
            <div className="text-center p-10">
                <div className="mb-4"><Spinner size={32} /></div>
                <p className="text-gray-600 dark:text-gray-300">Waiting for essential services...</p>
            </div>
        );
    }
            
    return (
        <div className="space-y-6 md:space-y-8 animate-fade-in">
            {/* Dashboard Header */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 p-4 bg-white dark:bg-gray-800 shadow rounded-lg">
                <div>
                    <h2 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-gray-100">My Submissions</h2>
                    <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                        {stats.total} assignments submitted &bull; {stats.graded} graded &bull; Average Grade: {stats.average > 0 ? stats.average : 'N/A'}
                    </p>
                </div>
                {/* Button to open new submission form */}
                <button
                    onClick={() => setIsFormOpen(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-6 rounded-lg shadow-md transition-all whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
                    aria-label="Submit New Notebook"
                >
                    + New Submission
                </button>
            </header>

            {/* New Submission Form Modal */}
            {isFormOpen && (
                <NewSubmissionForm 
                    userId={userId} 
                    userEmail={userEmail} 
                    onClose={() => setIsFormOpen(false)} 
                    appId={appId} 
                    db={db} 
                />
            )}

            {/* Loading and Error States */}
            {isLoading && <div className="text-center py-10"><Spinner size={32} /></div>}
            {error && (
                <div className="text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900 p-4 rounded-lg shadow text-center">
                    {error}
                </div>
            )}

            {/* No Submissions Message */}
            {!isLoading && !error && submissions.length === 0 && (
                <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                    <div className="text-gray-400 dark:text-gray-500 mb-6">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-20 w-20 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">No submissions yet!</h3>
                    <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-6">
                        Click "+ New Submission" to get started.
                    </p>
                </div>
            )}

            {/* Submissions Table */}
            {!isLoading && !error && submissions.length > 0 && (
                <div className="bg-white dark:bg-gray-800 shadow-xl rounded-lg overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Assignment/Course</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Grade</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Submitted</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Certificate</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                            {submissions.map(sub => (
                                <React.Fragment key={sub.id}>
                                    <tr className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="font-semibold text-blue-600 dark:text-blue-400">{sub.assignmentTitle}</div>
                                            <div className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-xs">
                                                <a href={sub.notebookLink} target="_blank" rel="noopener noreferrer" className="hover:underline" title={sub.notebookLink}>
                                                    {sub.notebookLink || "No link"}
                                                </a>
                                            </div>
                                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Name for Cert: {sub.fullNameForCertificate || 'N/A'}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <StatusBadge status={sub.status} />
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {sub.status === 'graded' && sub.grade !== null ? (
                                                <p className="text-lg font-bold text-green-600 dark:text-green-400">{sub.grade}</p>
                                            ) : (
                                                <p className="text-gray-500 dark:text-gray-400">-</p>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                            {sub.submittedAt?.toDate() ? new Date(sub.submittedAt.toDate()).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric'}) : 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {sub.certificateEligible && parseFloat(sub.grade) >= 50 ? (
                                                <button
                                                    onClick={() => handleDownloadCertificate(sub)}
                                                    disabled={isGeneratingCert === sub.id} // Disable button while generating
                                                    className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-3 rounded-lg text-xs shadow-md transition-all focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                                                >
                                                    {isGeneratingCert === sub.id ? <Spinner size={16} color="border-white"/> : 'Download Cert'}
                                                </button>
                                            ) : (
                                                <p className="text-xs text-gray-400 dark:text-gray-500">
                                                    {sub.status === 'graded' && parseFloat(sub.grade) < 50 ? 'Grade < 50' : 'Not eligible'}
                                                </p>
                                            )}
                                        </td>
                                    </tr>
                                    {/* Display feedback row if graded and feedback exists */}
                                    {sub.status === 'graded' && sub.feedback && (
                                        <tr className="bg-gray-50 dark:bg-gray-700/30">
                                            <td colSpan="5" className="px-6 py-3">
                                                <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-md border border-gray-200 dark:border-gray-600">
                                                    <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">Feedback:</p>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{sub.feedback}</p>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default StudentDashboard;
