import api from './api';

export const documentService = {
  uploadDocument: async (file) => {
    if (!file || !(file instanceof File || file instanceof Blob)) {
      throw new Error('Invalid file: file must be a File or Blob object');
    }
    const formData = new FormData();
    formData.append('file', file);
    
    // Don't set Content-Type header - let axios set it with boundary
    const response = await api.post('/api/rag/upload', formData);
    return response.data;
  },

  getDocuments: async () => {
    const response = await api.get('/api/rag/');
    return response.data;
  },

  getDocument: async (documentId) => {
    if (!documentId || (typeof documentId !== 'string' && typeof documentId !== 'number') || (typeof documentId === 'string' && documentId.trim().length === 0)) {
      throw new Error('Invalid documentId');
    }
    const response = await api.get(`/api/rag/${documentId}`);
    return response.data;
  },

  deleteDocument: async (documentId) => {
    if (!documentId || (typeof documentId !== 'string' && typeof documentId !== 'number') || (typeof documentId === 'string' && documentId.trim().length === 0)) {
      throw new Error('Invalid documentId');
    }
    await api.delete(`/api/rag/${documentId}`);
  },
};

