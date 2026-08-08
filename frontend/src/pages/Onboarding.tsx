import React, { useState } from 'react';
import { Upload, CheckCircle2, ArrowRight, ArrowLeft } from 'lucide-react';
import { api } from '../api/client';

interface OnboardingProps {
  onComplete: () => void;
}

export const Onboarding: React.FC<OnboardingProps> = ({ onComplete }) => {
  const [step, setStep] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [resumeUploaded, setResumeUploaded] = useState(false);
  
  const [firstName, setFirstName] = useState('Shashi');
  const [lastName, setLastName] = useState('Kiran');
  const [city, setCity] = useState('Bangalore');
  const [phone, setPhone] = useState('+91 9876543210');
  
  const [minLpa, setMinLpa] = useState(8.0);
  const [maxLpa, setMaxLpa] = useState(15.0);
  const [appMode, setAppMode] = useState<'MANUAL' | 'APPROVAL' | 'AUTO'>('APPROVAL');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploading(true);
    try {
      await api.uploadMasterResume(file);
      setResumeUploaded(true);
    } catch {
      alert('File upload failed. Defaulting to sample profile facts.');
    } finally {
      setUploading(false);
    }
  };

  const handleFinish = async () => {
    try {
      await api.updateProfile({
        first_name: firstName,
        last_name: lastName,
        current_city: city,
        phone: phone,
        country: 'India',
        skills: [
          { category: 'Programming', name: 'Python', proficiency: 'Expert' },
          { category: 'Frameworks', name: 'FastAPI', proficiency: 'Expert' },
          { category: 'Databases', name: 'PostgreSQL', proficiency: 'Intermediate' },
          { category: 'Cloud', name: 'AWS', proficiency: 'Intermediate' }
        ],
        experiences: [
          {
            company: 'Tech Solutions Inc',
            job_title: 'Software Developer',
            location: 'Bangalore',
            start_date: '2023-06',
            is_current: true,
            technologies: 'Python, FastAPI, REST APIs, PostgreSQL'
          }
        ],
        education: [
          {
            degree: 'B.Tech',
            specialization: 'Computer Science & Engineering',
            university: 'National Institute of Technology',
            start_date: '2019',
            end_date: '2023'
          }
        ]
      });

      await api.updateSettings({
        min_lpa: minLpa,
        max_lpa: maxLpa,
        application_mode: appMode,
        auto_apply_enabled: appMode === 'AUTO'
      });

      onComplete();
    } catch (err: any) {
      alert(err.message || 'Setup failed');
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '60px auto', padding: '0 20px' }}>
      <div className="wizard-steps">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
          <div key={s} className={`wizard-step-pill ${s <= step ? 'active' : ''}`} />
        ))}
      </div>

      <div className="glass-panel" style={{ padding: '40px' }}>
        {step === 1 && (
          <div>
            <span className="badge-status badge-ready" style={{ marginBottom: '16px' }}>STEP 1 OF 8</span>
            <h2 style={{ fontSize: '24px', fontWeight: 800 }}>Upload Your Master Resume</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '6px', marginBottom: '24px' }}>
              Upload your PDF or DOCX resume. JobPilot AI will extract your master profile. Your original resume remains untouched.
            </p>

            <div style={{ border: '2px dashed var(--border-color)', borderRadius: 'var(--radius-lg)', padding: '40px', textAlign: 'center', background: 'rgba(15, 23, 42, 0.4)' }}>
              <Upload size={40} style={{ color: 'var(--accent-cyan)', marginBottom: '16px' }} />
              <h4>{resumeUploaded ? 'Master Resume Processed!' : 'Click to Upload PDF or DOCX'}</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>Supports PDF/DOCX up to 10MB</p>
              
              <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} style={{ display: 'none' }} id="resume-upload-input" />
              <label htmlFor="resume-upload-input" className="btn-secondary" style={{ marginTop: '20px', cursor: 'pointer' }}>
                {uploading ? 'Parsing Resume...' : resumeUploaded ? 'Replace File' : 'Select Resume File'}
              </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '32px' }}>
              <button className="btn-primary" onClick={() => setStep(2)}>
                Continue <ArrowRight size={18} />
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <span className="badge-status badge-ready" style={{ marginBottom: '16px' }}>STEP 2 & 3 OF 8</span>
            <h2 style={{ fontSize: '24px', fontWeight: 800 }}>Verify Profile Details</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '6px', marginBottom: '24px' }}>
              Review the extracted facts. The AI will never hallucinate or claim details outside this profile.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="form-group">
                <label>First Name</label>
                <input className="form-control" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input className="form-control" value={lastName} onChange={(e) => setLastName(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Current City</label>
                <input className="form-control" value={city} onChange={(e) => setCity(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input className="form-control" value={phone} onChange={(e) => setPhone(e.target.value)} />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
              <button className="btn-secondary" onClick={() => setStep(1)}><ArrowLeft size={18} /> Back</button>
              <button className="btn-primary" onClick={() => setStep(5)}>Next: Job Preferences <ArrowRight size={18} /></button>
            </div>
          </div>
        )}

        {step === 5 && (
          <div>
            <span className="badge-status badge-ready" style={{ marginBottom: '16px' }}>STEP 5 & 6 OF 8</span>
            <h2 style={{ fontSize: '24px', fontWeight: 800 }}>Define LPA Salary Requirements</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '6px', marginBottom: '24px' }}>
              Specify your strict Lakhs Per Annum (LPA) compensation boundaries. Jobs below minimum LPA will be automatically filtered out.
            </p>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '24px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontWeight: 700 }}>
                <span>Target Compensation:</span>
                <span style={{ color: 'var(--accent-cyan)' }}>₹{minLpa} LPA – ₹{maxLpa} LPA</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div className="form-group">
                  <label>Minimum Salary (INR LPA)</label>
                  <input type="number" step="0.5" className="form-control" value={minLpa} onChange={(e) => setMinLpa(parseFloat(e.target.value))} />
                </div>
                <div className="form-group">
                  <label>Maximum Target (INR LPA)</label>
                  <input type="number" step="0.5" className="form-control" value={maxLpa} onChange={(e) => setMaxLpa(parseFloat(e.target.value))} />
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
              <button className="btn-secondary" onClick={() => setStep(2)}><ArrowLeft size={18} /> Back</button>
              <button className="btn-primary" onClick={() => setStep(7)}>Next: Application Mode <ArrowRight size={18} /></button>
            </div>
          </div>
        )}

        {step === 7 && (
          <div>
            <span className="badge-status badge-ready" style={{ marginBottom: '16px' }}>STEP 7 & 8 OF 8</span>
            <h2 style={{ fontSize: '24px', fontWeight: 800 }}>Select Application Automation Mode</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '6px', marginBottom: '24px' }}>
              Choose how JobPilot AI handles job application submissions.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '32px' }}>
              <div
                onClick={() => setAppMode('MANUAL')}
                style={{
                  padding: '20px',
                  borderRadius: 'var(--radius-md)',
                  border: `2px solid ${appMode === 'MANUAL' ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
                  background: appMode === 'MANUAL' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(15, 23, 42, 0.4)',
                  cursor: 'pointer'
                }}
              >
                <h4 style={{ fontWeight: 700, marginBottom: '6px' }}>1. Manual Mode</h4>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Prepares job matches and custom resumes. You click Apply manually.</p>
              </div>

              <div
                onClick={() => setAppMode('APPROVAL')}
                style={{
                  padding: '20px',
                  borderRadius: 'var(--radius-md)',
                  border: `2px solid ${appMode === 'APPROVAL' ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
                  background: appMode === 'APPROVAL' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(15, 23, 42, 0.4)',
                  cursor: 'pointer'
                }}
              >
                <h4 style={{ fontWeight: 700, marginBottom: '6px' }}>2. Approval Mode</h4>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Generates custom resume & answers. You review & approve before submit.</p>
              </div>

              <div
                onClick={() => setAppMode('AUTO')}
                style={{
                  padding: '20px',
                  borderRadius: 'var(--radius-md)',
                  border: `2px solid ${appMode === 'AUTO' ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
                  background: appMode === 'AUTO' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(15, 23, 42, 0.4)',
                  cursor: 'pointer'
                }}
              >
                <h4 style={{ fontWeight: 700, marginBottom: '6px' }}>3. Auto-Apply</h4>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Fully automated Playwright application agent submitting eligible jobs.</p>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
              <button className="btn-secondary" onClick={() => setStep(5)}><ArrowLeft size={18} /> Back</button>
              <button className="btn-primary" onClick={handleFinish}>
                Launch Dashboard <CheckCircle2 size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
