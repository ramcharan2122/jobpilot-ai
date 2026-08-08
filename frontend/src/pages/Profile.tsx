import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle2, User, Code } from 'lucide-react';
import { api } from '../api/client';
import type { Profile as ProfileType } from '../types';

export const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<ProfileType | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await api.getProfile();
      setProfile(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      await api.updateProfile(profile);
      alert('Profile saved successfully!');
    } catch (err: any) {
      alert(err.message || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploading(true);
    try {
      await api.uploadMasterResume(file);
      await fetchProfile();
      alert('Master resume uploaded & profile synced successfully!');
    } catch (err: any) {
      alert(err.message || 'Failed to upload resume');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>Verified Master Profile & Master Resume</h1>
          <p>This master profile represents verified factual information used for AI resume tailoring.</p>
        </div>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          <CheckCircle2 size={18} /> {saving ? 'Saving...' : 'Save Profile Changes'}
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div className="brand-icon" style={{ width: '44px', height: '44px' }}>
            <Upload size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Upload Master Resume (PDF / DOCX)</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Master resume remains untouched. Job-specific resumes are generated per job match.</p>
          </div>
        </div>

        <input type="file" accept=".pdf,.docx" onChange={handleResumeUpload} id="master-resume-input" style={{ display: 'none' }} />
        <label htmlFor="master-resume-input" className="btn-secondary" style={{ cursor: 'pointer' }}>
          {uploading ? 'Uploading & Parsing...' : 'Upload Master File'}
        </label>
      </div>

      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <User size={20} style={{ color: 'var(--accent-cyan)' }} /> Personal Details
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
          <div className="form-group">
            <label>First Name</label>
            <input className="form-control" value={profile?.first_name || ''} onChange={(e) => setProfile({ ...profile!, first_name: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Last Name</label>
            <input className="form-control" value={profile?.last_name || ''} onChange={(e) => setProfile({ ...profile!, last_name: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input className="form-control" value={profile?.email || ''} onChange={(e) => setProfile({ ...profile!, email: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input className="form-control" value={profile?.phone || ''} onChange={(e) => setProfile({ ...profile!, phone: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Current City</label>
            <input className="form-control" value={profile?.current_city || ''} onChange={(e) => setProfile({ ...profile!, current_city: e.target.value })} />
          </div>
          <div className="form-group">
            <label>LinkedIn URL</label>
            <input className="form-control" value={profile?.linkedin_url || ''} onChange={(e) => setProfile({ ...profile!, linkedin_url: e.target.value })} />
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Code size={20} style={{ color: 'var(--accent-cyan)' }} /> Categorized Skills
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {(profile?.skills || []).map((sk, idx) => (
            <span key={idx} style={{ background: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-cyan)', border: '1px solid rgba(56, 189, 248, 0.3)', padding: '6px 14px', borderRadius: 'var(--radius-full)', fontSize: '13px', fontWeight: 600 }}>
              {sk.name} ({sk.category})
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
