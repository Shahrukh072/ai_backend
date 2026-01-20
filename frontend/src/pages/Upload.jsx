import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { documentService } from '../services/documentService';
import { Upload as UploadIcon, FileText, Trash2, ArrowLeft, CheckCircle } from 'lucide-react';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  const loadDocuments = useCallback(async () => {
    try {
      const docs = await documentService.getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file size (10MB limit)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      // Check file extension
      const allowedExtensions = ['.pdf', '.txt', '.docx', '.md'];
      const fileExtension = '.' + selectedFile.name.split('.').pop().toLowerCase();
      if (!allowedExtensions.includes(fileExtension)) {
        setError('Only PDF, TXT, DOCX, and MD files are allowed');
        return;
      }
      setFile(selectedFile);
      setError('');
      setSuccess('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const result = await documentService.uploadDocument(file);
      setSuccess('Document uploaded successfully!');
      setFile(null);
      setUploading(false);
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
      // Reload documents list
      await loadDocuments();
      // Navigate to chat page after a short delay to show success message
      setTimeout(() => {
        navigate('/chat', { replace: true });
      }, 1500);
    } catch (err) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Upload failed. Please try again.';
      setError(errorMessage);
      setUploading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await documentService.deleteDocument(documentId);
      loadDocuments();
      setSuccess('Document deleted successfully');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Prevent blank screen on errors
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to upload documents</p>
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/chat')}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-600" />
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Document Management</h1>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Document</h2>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded flex items-center gap-2">
              <CheckCircle className="h-5 w-5" />
              {success}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select File (PDF, TXT, DOCX, MD - Max 10MB)
              </label>
              <div className="flex items-center gap-4">
                <label className="flex-1 cursor-pointer">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
                    <UploadIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      {file ? file.name : 'Click to select a file or drag and drop'}
                    </p>
                    {file && (
                      <p className="text-xs text-gray-500 mt-1">
                        {formatFileSize(file.size)}
                      </p>
                    )}
                  </div>
                  <input
                    id="file-input"
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    accept=".pdf,.txt,.docx,.md"
                  />
                </label>
              </div>
            </div>

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Uploading...
                </>
              ) : (
                <>
                  <UploadIcon className="h-5 w-5" />
                  Upload Document
                </>
              )}
            </button>
          </div>
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Your Documents</h2>

          {documents.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p>No documents uploaded yet</p>
              <p className="text-sm mt-2">Upload your first document to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <FileText className="h-8 w-8 text-blue-600" />
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{doc.title}</h3>
                      <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                        <span>{(doc.file_type || 'unknown').toUpperCase()}</span>
                        <span>•</span>
                        <span>{doc.file_size != null ? formatFileSize(doc.file_size) : '-'}</span>
                        <span>•</span>
                        <span>{doc.created_at ? formatDate(doc.created_at) : '-'}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

