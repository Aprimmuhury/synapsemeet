/**
 * SynapseMeet - api.js
 * Thin fetch wrapper around the Django REST backend. Handles JWT storage,
 * automatic refresh, and consistent error shapes for the rest of the app.
 */
const SynapseAPI = (() => {
  const isAndroidWebView = /Android/i.test(navigator.userAgent) || (window.location && window.location.protocol === 'file:');
  const isStandaloneFrontend = window.location && window.location.port === '5500';
  const fallbackBase = isAndroidWebView ? 'http://10.0.2.2:8000/api' : 'http://127.0.0.1:8000/api';
  const configuredBase = window.SYNAPSEMEET_API_BASE;
  const sameOriginBase = !isAndroidWebView && !isStandaloneFrontend && window.location && window.location.origin !== 'null'
    ? `${window.location.origin}/api`
    : null;
  const BASE_URL = configuredBase || sameOriginBase || fallbackBase;

  function getTokens() {
    return {
      access: localStorage.getItem('sm_access'),
      refresh: localStorage.getItem('sm_refresh'),
    };
  }

  function setTokens({ access, refresh }) {
    if (access) localStorage.setItem('sm_access', access);
    if (refresh) localStorage.setItem('sm_refresh', refresh);
  }

  function clearTokens() {
    localStorage.removeItem('sm_access');
    localStorage.removeItem('sm_refresh');
    localStorage.removeItem('sm_user');
  }

  function isAuthenticated() {
    return !!getTokens().access;
  }

  async function refreshAccessToken() {
    const { refresh } = getTokens();
    if (!refresh) throw new Error('No refresh token available');
    const res = await fetch(`${BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) throw new Error('Session expired');
    const data = await res.json();
    setTokens({ access: data.access });
    return data.access;
  }

  async function request(path, { method = 'GET', body, auth = true, retry = true } = {}) {
    const isFormData = body instanceof FormData;
    const headers = isFormData ? {} : { 'Content-Type': 'application/json' };
    if (auth) {
      const { access } = getTokens();
      if (access) headers['Authorization'] = `Bearer ${access}`;
    }

    const res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
    });

    if (res.status === 401 && auth && retry) {
      try {
        await refreshAccessToken();
        return request(path, { method, body, auth, retry: false });
      } catch (e) {
        clearTokens();
        window.location.href = 'index.html';
        throw e;
      }
    }

    let data = null;
    try { data = await res.json(); } catch (e) { /* empty body */ }

    if (!res.ok) {
      const message = (data && (data.detail || JSON.stringify(data))) || `Request failed (${res.status})`;
      throw new Error(message);
    }
    return data;
  }

  return {
    // Auth
    register: (payload) => request('/auth/register/', { method: 'POST', body: payload, auth: false }),
    login: async (username, password) => {
      const data = await request('/auth/login/', { method: 'POST', body: { username, password }, auth: false });
      setTokens({ access: data.access, refresh: data.refresh });
      localStorage.setItem('sm_user', JSON.stringify(data.user));
      return data;
    },
    logout: () => clearTokens(),
    isAuthenticated,
    getCurrentUser: () => JSON.parse(localStorage.getItem('sm_user') || 'null'),
    fetchMe: () => request('/auth/me/'),
    updateProfile: (payload) => request('/auth/profile/', { method: 'PATCH', body: payload }),
    changePassword: (payload) => request('/auth/change-password/', { method: 'POST', body: payload }),
    requestPasswordReset: (email) => request('/auth/forgot-password/', { method: 'POST', body: { email }, auth: false }),
    confirmPasswordReset: (uid, token, password) => request('/auth/reset-password/', { method: 'POST', body: { uid, token, password }, auth: false }),

    // Meetings
    listMeetings: () => request('/meetings/'),
    getMeeting: (id) => request(`/meetings/${id}/`),
    createMeeting: (payload) => request('/meetings/', { method: 'POST', body: payload }),
    joinMeeting: (id) => request(`/meetings/${id}/join/`, { method: 'POST' }),
    joinByCode: (roomCode) => request('/meetings/join_by_code/', { method: 'POST', body: { room_code: roomCode } }),
    leaveMeeting: (id) => request(`/meetings/${id}/leave/`, { method: 'POST' }),
    startMeeting: (id) => request(`/meetings/${id}/start/`, { method: 'POST' }),
    endMeeting: (id) => request(`/meetings/${id}/end/`, { method: 'POST' }),
    getChat: (id) => request(`/meetings/${id}/chat/`),
    postChat: (id, content) => request(`/meetings/${id}/chat/`, { method: 'POST', body: { content } }),
    getActionItems: (id) => request(`/meetings/${id}/action-items/`),
    createActionItem: (id, payload) => request(`/meetings/${id}/action-items/`, { method: 'POST', body: payload }),

    // AI assistant
    uploadTranscriptSegment: (meetingId, payload) =>
      request(`/ai/meetings/${meetingId}/transcript/`, { method: 'POST', body: payload }),
    getSummary: (meetingId) => request(`/ai/meetings/${meetingId}/summary/`),
    generateSummary: (meetingId) => request(`/ai/meetings/${meetingId}/summary/`, { method: 'POST' }),
  };
})();
