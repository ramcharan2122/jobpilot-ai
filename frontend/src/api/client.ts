import type { Profile, UserSettings, Job, Application, Campaign, DashboardStats } from '../types';

export const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const getDownloadUrl = (path: string): string => {
  if (!path) return '#';
  if (path.startsWith('http')) return path;
  const baseUrl = API_BASE.replace('/api/v1', '');
  return `${baseUrl}${path.startsWith('/') ? '' : '/'}${path}`;
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('jobpilot_token');
};

export const setAuthToken = (token: string) => {
  localStorage.setItem('jobpilot_token', token);
};

export const removeAuthToken = () => {
  localStorage.removeItem('jobpilot_token');
};

const authHeaders = (): Record<string, string> => {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  async register(data: any) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async login(data: any) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  async sendOtp(email: string) {
    const res = await fetch(`${API_BASE}/auth/send-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to send OTP');
    }
    return res.json();
  },

  async verifyOtp(email: string, otp_code: string) {
    const res = await fetch(`${API_BASE}/auth/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, otp_code })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Invalid OTP code');
    }
    return res.json();
  },

  async googleAuth(credentialToken: string, email?: string, fullName?: string) {
    const res = await fetch(`${API_BASE}/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        credential_token: credentialToken,
        email: email || undefined,
        full_name: fullName || undefined
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Google authentication failed');
    }
    return res.json();
  },

  async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Unauthorized');
    return res.json();
  },

  async getProfile(): Promise<Profile> {
    const res = await fetch(`${API_BASE}/profile`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async updateProfile(profile: Partial<Profile>): Promise<Profile> {
    const res = await fetch(`${API_BASE}/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(profile)
    });
    if (!res.ok) throw new Error('Failed to update profile');
    return res.json();
  },

  async uploadMasterResume(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/profile/upload-resume`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData
    });
    if (!res.ok) throw new Error('Failed to upload resume');
    return res.json();
  },

  async getSettings(): Promise<UserSettings> {
    const res = await fetch(`${API_BASE}/settings`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  },

  async updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(settings)
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  async getJobs(role?: string, minLpa?: number): Promise<Job[]> {
    let url = `${API_BASE}/jobs?`;
    if (role) url += `role=${encodeURIComponent(role)}&`;
    if (minLpa) url += `min_lpa=${minLpa}`;
    const res = await fetch(url, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch jobs');
    return res.json();
  },

  async generateResume(jobId: number) {
    const res = await fetch(`${API_BASE}/resumes/generate/${jobId}`, {
      method: 'POST',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to generate resume');
    return res.json();
  },

  async getResumes() {
    const res = await fetch(`${API_BASE}/resumes`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch resumes');
    return res.json();
  },

  async createApplication(jobId: number, mode: string = 'APPROVAL') {
    const res = await fetch(`${API_BASE}/applications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ job_id: jobId, application_mode: mode })
    });
    if (!res.ok) throw new Error('Failed to create application');
    return res.json();
  },

  async submitApplication(appId: number) {
    const res = await fetch(`${API_BASE}/applications/${appId}/submit`, {
      method: 'POST',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to submit application');
    return res.json();
  },

  async getApplications(): Promise<Application[]> {
    const res = await fetch(`${API_BASE}/applications`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch applications');
    return res.json();
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/applications/dashboard-stats`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch dashboard stats');
    return res.json();
  },

  async createCampaign(data: any): Promise<Campaign> {
    const res = await fetch(`${API_BASE}/campaigns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create campaign');
    return res.json();
  },

  async getCampaigns(): Promise<Campaign[]> {
    const res = await fetch(`${API_BASE}/campaigns`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch campaigns');
    return res.json();
  }
};
