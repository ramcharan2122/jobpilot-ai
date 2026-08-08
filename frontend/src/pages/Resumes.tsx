import React, { useState, useEffect } from 'react';
import { Download, ShieldCheck, Eye, X } from 'lucide-react';
import { api, getDownloadUrl } from '../api/client';
import type { GeneratedResume } from '../types';

export const ResumesPage: React.FC = () => {
  const [resumes, setResumes] = useState<GeneratedResume[]>([]);
  const [selectedResume, setSelectedResume] = useState<GeneratedResume | null>(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      const data = await api.getResumes();
      setResumes(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>Generated Resume Library</h1>
          <p>Every generated resume is tailored specifically to a target job and validated for factual truth.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {resumes.map((res) => (
          <div key={res.id} className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span className="badge-status badge-ready">Job Match #{res.job_id}</span>
              <span style={{ color: 'var(--accent-emerald)', fontSize: '12px', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <ShieldCheck size={14} /> Fact-Check Verified
              </span>
            </div>

            <h3 style={{ fontSize: '16px', fontWeight: 800, marginBottom: '6px' }}>{res.file_name}</h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Generated: {new Date(res.generated_at).toLocaleDateString()}
            </p>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn-secondary" style={{ flex: 1, padding: '8px', fontSize: '13px', justifyContent: 'center' }} onClick={() => setSelectedResume(res)}>
                <Eye size={14} /> Preview
              </button>
              <a href={getDownloadUrl(res.pdf_url)} target="_blank" rel="noreferrer" className="btn-primary" style={{ padding: '8px 12px', fontSize: '13px' }}>
                <Download size={14} /> PDF
              </a>
              <a href={getDownloadUrl(res.docx_url)} target="_blank" rel="noreferrer" className="btn-secondary" style={{ padding: '8px 12px', fontSize: '13px' }}>
                <Download size={14} /> DOCX
              </a>
            </div>
          </div>
        ))}
      </div>

      {selectedResume && (
        <div className="modal-overlay" onClick={() => setSelectedResume(null)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3>Resume Preview: {selectedResume.file_name}</h3>
              <button onClick={() => setSelectedResume(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ background: '#fff', color: '#1e293b', padding: '32px', borderRadius: '8px', fontFamily: 'sans-serif', fontSize: '13px', lineHeight: '1.5' }}>
              <h2 style={{ textAlign: 'center', fontSize: '20px', color: '#0f172a' }}>
                {selectedResume.content_json?.personal_info?.name || 'CANDIDATE'}
              </h2>
              <div style={{ textAlign: 'center', color: '#64748b', marginBottom: '16px' }}>
                {selectedResume.content_json?.personal_info?.email} | {selectedResume.content_json?.personal_info?.phone} | {selectedResume.content_json?.personal_info?.location}
              </div>

              <h4 style={{ borderBottom: '1px solid #cbd5e1', paddingBottom: '4px', marginTop: '16px', color: '#0f172a' }}>PROFESSIONAL SUMMARY</h4>
              <p>{selectedResume.content_json?.summary}</p>

              <h4 style={{ borderBottom: '1px solid #cbd5e1', paddingBottom: '4px', marginTop: '16px', color: '#0f172a' }}>EXPERIENCE</h4>
              {(selectedResume.content_json?.experiences || []).map((exp: any, idx: number) => (
                <div key={idx} style={{ marginTop: '8px' }}>
                  <strong>{exp.job_title}</strong> — <i>{exp.company}</i> ({exp.dates})
                  <ul>
                    {(exp.bullets || []).map((b: string, bi: number) => <li key={bi}>{b}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
