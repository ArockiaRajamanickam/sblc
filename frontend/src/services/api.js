import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
});

// Request Interceptor for JWT
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response Interceptor for Token Refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    const res = await axios.post('/api/auth/refresh', {}, {
                        headers: { Authorization: `Bearer ${refreshToken}` }
                    });

                    const { access_token, refresh_token } = res.data;
                    localStorage.setItem('access_token', access_token);
                    localStorage.setItem('refresh_token', refresh_token);

                    return api(originalRequest);
                } catch (refreshError) {
                    localStorage.clear();
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                }
            }
        }
        return Promise.reject(error);
    }
);

export const authService = {
    login: async (email, password) => {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        const res = await api.post('/auth/login', formData);
        return res.data;
    },
    logout: () => {
        localStorage.clear();
        return api.post('/auth/logout');
    },
    getMe: () => api.get('/auth/me'),
};

export const ledgerService = {
    list: () => api.get('/ledgers'),
    get: (id) => api.get(`/ledgers/${id}`),
    getAudit: (id) => api.get(`/ledgers/${id}/audit`),
};

export const sblcService = {
    list: (ledgerId) => api.get(`/ledgers/${ledgerId}/sblcs`),
    get: (ledgerId, sblcId) => api.get(`/ledgers/${ledgerId}/sblcs/${sblcId}`),
    create: (ledgerId, data) => api.post(`/ledgers/${ledgerId}/sblcs`, data),
    submit: (ledgerId, sblcId) => api.post(`/ledgers/${ledgerId}/sblcs/${sblcId}/submit`),
    requestReview: (ledgerId, sblcId) => api.post(`/ledgers/${ledgerId}/sblcs/${sblcId}/request_review`),
    approve: (ledgerId, sblcId) => api.post(`/ledgers/${ledgerId}/sblcs/${sblcId}/approve`),
    issue: (ledgerId, sblcId) => api.post(`/ledgers/${ledgerId}/sblcs/${sblcId}/issue`),
    amend: (ledgerId, sblcId, data) => api.post(`/ledgers/${ledgerId}/sblcs/${sblcId}/amendments`, data),
    uploadAttachment: (ledgerId, sblcId, data) => api.post(`/ledgers/${ledgerId}/sblcs/${sblcId}/attachments`, data),
};

export const nodeService = {
    list: () => api.get('/nodes'),
};

export const publicService = {
    verify: (ref) => api.get(`/public/verify/${ref}`),
};

export const adminService = {
    invite: (data) => api.post('/admin/invites', data),
    setupPassword: (token, password) => api.post('/auth/setup_password', { token, password }),
    getAnalyticsSummary: () => api.get('/analytics/summary'),
};

export default api;
