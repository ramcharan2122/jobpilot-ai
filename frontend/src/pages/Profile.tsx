import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle2, User, Code, Briefcase, GraduationCap, Plus, Trash2 } from 'lucide-react';
import { api } from '../api/client';
import type { Profile as ProfileType, Experience, Education } from '../types';

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

  const addExperience = () => {
    if (!profile) return;
    const newExp: Experience = {
      company: 'My Company',
      job_title: 'Software Developer',
      location: 'Hyderabad',
      start_date: '2023-01',
      is_current: true,
      technologies: 'Python, FastAPI, SQL'
    };
    setProfile({
      ...profile,
      experiences: [...(profile.experiences || []), newExp]
    });
  };

  const removeExperience = (idx: number) => {
    if (!profile) return;
    const updated = (profile.experiences || []).filter((_, i) => i !== idx);
    setProfile({ ...profile, experiences: updated });
  };

  const updateExpField = (idx: number, field: keyof Experience, value: any) => {
    if (!profile) return;
    const updated = [...(profile.experiences || [])];
    updated[idx] = { ...updated[idx], [field]: value };
    setProfile({ ...profile, experiences: updated });
  };

  const addEducation = () => {
    if (!profile) return;
    const newEdu: Education = {
      degree: 'B.Tech',
      specialization: 'Computer Science',
      university: 'My University',
      location: 'Hyderabad',
      start_date: '2019',
      end_date: '2023'
    };
    setProfile({
      ...profile,
      education: [...(profile.education || []), newEdu]
    });
  };

  const removeEducation = (idx: number) => {
    if (!profile) return;
    const updated = (profile.education || []).filter((_, i) => i !== idx);
    setProfile({ ...profile, education: updated });
  };

  const updateEduField = (idx: number, field: keyof Education, value: any) => {
    if (!profile) return;
    const updated = [...(profile.education || [])];
    updated[idx] = { ...updated[idx], [field]: value };
    setProfile({ ...profile, education: updated });
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
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Upload your PDF/DOCX to automatically parse and populate your profile facts.</p>
          </div>
        </div>

        <input type="file" accept=".pdf,.docx" onChange={handleResumeUpload} id="master-resume-input" style={{ display: 'none' }} />
        <label htmlFor="master-resume-input" className="btn-secondary" style={{ cursor: 'pointer' }}>
          {uploading ? 'Uploading & Parsing...' : 'Upload Master File'}
        </label>
      </div>

      {/* Personal Info */}
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

      {/* Work Experiences */}
      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Briefcase size={20} style={{ color: 'var(--accent-cyan)' }} /> Professional Work Experience
          </h3>
          <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }} onClick={addExperience}>
            <Plus size={14} /> Add Experience
          </button>
        </div>

        {(profile?.experiences || []).length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No work experience added yet. Upload your master resume or click "Add Experience" above.</p>
        ) : (
          (profile?.experiences || []).map((exp, idx) => (
            <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ fontSize: '15px', fontWeight: 700 }}>Experience #{idx + 1}</h4>
                <button style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }} onClick={() => removeExperience(idx)}>
                  <Trash2 size={16} />
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label>Company Name</label>
                  <input className="form-control" value={exp.company || ''} onChange={(e) => updateExpField(idx, 'company', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Job Title</label>
                  <input className="form-control" value={exp.job_title || ''} onChange={(e) => updateExpField(idx, 'job_title', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Location</label>
                  <input className="form-control" value={exp.location || ''} onChange={(e) => updateExpField(idx, 'location', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Start Date</label>
                  <input className="form-control" value={exp.start_date || ''} onChange={(e) => updateExpField(idx, 'start_date', e.target.value)} placeholder="e.g. 2023-01" />
                </div>
                <div className="form-group">
                  <label>End Date / Status</label>
                  <input className="form-control" value={exp.is_current ? 'Present' : exp.end_date || ''} onChange={(e) => updateExpField(idx, 'end_date', e.target.value)} placeholder="e.g. Present" />
                </div>
                <div className="form-group">
                  <label>Technologies Used</label>
                  <input className="form-control" value={exp.technologies || ''} onChange={(e) => updateExpField(idx, 'technologies', e.target.value)} placeholder="Python, FastAPI, SQL" />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Education */}
      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <GraduationCap size={20} style={{ color: 'var(--accent-cyan)' }} /> Education & Degrees
          </h3>
          <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }} onClick={addEducation}>
            <Plus size={14} /> Add Education
          </button>
        </div>

        {(profile?.education || []).length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No education entries added yet. Upload your master resume or click "Add Education" above.</p>
        ) : (
          (profile?.education || []).map((edu, idx) => (
            <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ fontSize: '15px', fontWeight: 700 }}>Education #{idx + 1}</h4>
                <button style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }} onClick={() => removeEducation(idx)}>
                  <Trash2 size={16} />
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label>Degree</label>
                  <input className="form-control" value={edu.degree || ''} onChange={(e) => updateEduField(idx, 'degree', e.target.value)} placeholder="B.Tech, B.E., M.S." />
                </div>
                <div className="form-group">
                  <label>Specialization / Major</label>
                  <input className="form-control" value={edu.specialization || ''} onChange={(e) => updateEduField(idx, 'specialization', e.target.value)} placeholder="Computer Science" />
                </div>
                <div className="form-group">
                  <label>University / Institution</label>
                  <input className="form-control" value={edu.university || ''} onChange={(e) => updateEduField(idx, 'university', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Start Date</label>
                  <input className="form-control" value={edu.start_date || ''} onChange={(e) => updateEduField(idx, 'start_date', e.target.value)} placeholder="2019" />
                </div>
                <div className="form-group">
                  <label>Graduation / End Date</label>
                  <input className="form-control" value={edu.end_date || ''} onChange={(e) => updateEduField(idx, 'end_date', e.target.value)} placeholder="2023" />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Skills */}
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
