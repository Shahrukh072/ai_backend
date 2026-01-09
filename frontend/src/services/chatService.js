import api from './api';

export const chatService = {
  createChat: async (chatData) => {
    const response = await api.post('/api/chat/', chatData);
    return response.data;
  },

  getChats: async (documentId = null) => {
    const params = documentId ? { document_id: documentId } : {};
    const response = await api.get('/api/chat/', { params });
    return response.data;
  },

  getChat: async (chatId) => {
    if (!chatId || (typeof chatId !== 'string' && typeof chatId !== 'number') || (typeof chatId === 'string' && chatId.trim().length === 0)) {
      throw new Error('Invalid chatId');
    }
    const response = await api.get(`/api/chat/${chatId}`);
    return response.data;
  },

  createAgentChat: async (chatData) => {
    const response = await api.post('/api/chat/agent', chatData);
    return response.data;
  },
};

