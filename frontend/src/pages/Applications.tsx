import React, { useState, useEffect } from 'react';
import { FileText, RefreshCw, Loader2, CheckCircle, ExternalLink, ShieldAlert, Monitor } from 'lucide-react';
import { api, getDownloadUrl } from '../api/client';
import type { Application } from '../types';

export const ApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [submittingId, setSubmittingId] = useState<number | null>(null);
  const [viewTab, setViewTab] = useState<'details' | 'embedded_portal'>('details');

  useEffect(() => {
    fetchApplications();
  }, []);

  // Polling mechanism to auto-refresh applications while resumes are generating or applying
  useEffect(() => {
    const hasPending = applications.some(
      (app) => app.status === 'GENERATING_RESUME' || app.status === 'APPLYING' || app.status === 'READY' || !app.pdf_url
    );

    if (hasPending) {
      const interval = setInterval(() => {
        fetchApplications(true);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [applications]);

  const fetchApplications = async (isSilent: boolean = false) => {
    if (!isSilent) setLoading(true);
    try {
      const data = await api.getApplications();
      setApplications(data);
    } catch (err) {
      console.error("Failed to fetch applications:", err);
    } finally {
      if (!isSilent) setLoading(false);
    }
  };

  const handleManualSubmit = async (appId: number) => {
    setSubmittingId(appId);
    try {
      await api.submitApplication(appId);
      await fetchApplications(true);
    } catch (err: any) {
      alert(err.message || 'Submission failed');
    } finally {
      setSubmittingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUBMITTED':
        return <span className="badge-status badge-submitted">SUBMITTED</span>;
      case 'APPLYING':
        return (
          <span className="badge-status" style={{ background: 'rgba(56, 189, 248, 0.2)', color: 'var(--accent-cyan)', border: '1px solid rgba(56, 189, 248, 0.4)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Loader2 size={12} className="spin" /> APPLYING VIA AI...
          </span>
        );
      case 'RESUME_READY':
        return <span className="badge-status" style={{ background: 'rgba(16, 185, 129, 0.2)', color: 'var(--accent-emerald)', border: '1px solid rgba(16, 185, 129, 0.4)' }}>RESUME READY</span>;
      case 'GENERATING_RESUME':
        return (
          <span className="badge-status" style={{ background: 'rgba(56, 189, 248, 0.2)', color: 'var(--accent-cyan)', border: '1px solid rgba(56, 189, 248, 0.4)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Loader2 size={12} className="spin" /> GENERATING RESUME
          </span>
        );
      case 'ACTION_REQUIRED':
        return <span className="badge-status badge-action" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><ShieldAlert size={12} /> ACTION REQUIRED</span>;
      case 'FAILED':
        return <span className="badge-status badge-failed">FAILED</span>;
      default:
        return <span className="badge-status badge-ready">{status}</span>;
    }
  };

  return (
    <div>
      <div className="top-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="page-title">
          <h1>Applications Tracker</h1>
          <p>Track job submission status, view tailored resumes, and complete verification handoffs.</p>
        </div>
        <button className="btn-secondary" onClick={() => fetchApplications()} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          Refresh Status
        </button>
      </div>

      <div className="glass-panel table-container">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Salary (LPA)</th>
              <th>Custom Resume</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {applications.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                  No job applications created yet. Go to <strong>Jobs Discovery</strong> and click <strong>Apply AI</strong>!
                </td>
              </tr>
            ) : (
              applications.map((app) => (
                <tr key={app.id}>
                  <td>
                    <strong>{app.job?.company || 'Company'}</strong>
                  </td>
                  <td>{app.job?.title || 'Role'}</td>
                  <td>
                    <span style={{ color: 'var(--accent-emerald)', fontWeight: 700 }}>
                      ₹{app.job?.salary_min_lpa || 10}–{app.job?.salary_max_lpa || 18} LPA
                    </span>
                  </td>
                  <td>
                    {app.pdf_url ? (
                      <a
                        href={getDownloadUrl(app.pdf_url)}
                        target="_blank"
                        rel="noreferrer"
                        className="btn-secondary"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', fontSize: '12px', color: 'var(--accent-cyan)', background: 'rgba(56, 189, 248, 0.1)' }}
                      >
                        <FileText size={14} /> Download PDF
                      </a>
                    ) : (
                      <span style={{ color: 'var(--accent-cyan)', fontSize: '13px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                        <Loader2 size={14} className="spin" /> Generating...
                      </span>
                    )}
                  </td>
                  <td>{getStatusBadge(app.status)}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <button
                        className="btn-secondary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => {
                          setSelectedApp(app);
                          setViewTab('details');
                        }}
                      >
                        Details
                      </button>

                      <button
                        className="btn-primary"
                        style={{ padding: '6px 12px', fontSize: '12px', background: 'rgba(56, 189, 248, 0.2)', color: 'var(--accent-cyan)', border: '1px solid rgba(56, 189, 248, 0.4)', display: 'inline-flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}
                        onClick={() => {
                          setSelectedApp(app);
                          setViewTab('embedded_portal');
                        }}
                      >
                        <Monitor size={12} /> Open Embedded Portal
                      </button>

                      {app.status === 'SUBMITTED' ? (
                        <span style={{ color: 'var(--accent-emerald)', fontWeight: 700, fontSize: '12.5px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle size={14} /> Submitted
                        </span>
                      ) : (
                        <button
                          className="btn-primary"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                          onClick={() => handleManualSubmit(app.id)}
                          disabled={submittingId === app.id || app.status === 'APPLYING'}
                        >
                          {submittingId === app.id || app.status === 'APPLYING' ? 'Submitting...' : 'Submit Application'}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Application Detail & Embedded View Modal */}
      {selectedApp && (
        <div className="modal-overlay" onClick={() => setSelectedApp(null)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px', width: '95%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 800 }}>
                {selectedApp.job?.company} — {selectedApp.job?.title}
              </h2>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  className={viewTab === 'details' ? 'btn-primary' : 'btn-secondary'}
                  style={{ padding: '4px 12px', fontSize: '12px' }}
                  onClick={() => setViewTab('details')}
                >
                  AI Field Answers
                </button>
                <button
                  className={viewTab === 'embedded_portal' ? 'btn-primary' : 'btn-secondary'}
                  style={{ padding: '4px 12px', fontSize: '12px' }}
                  onClick={() => setViewTab('embedded_portal')}
                >
                  Embedded Portal View
                </button>
              </div>
            </div>

            {viewTab === 'embedded_portal' ? (
              <div>
                <div style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '12px 16px', borderRadius: 'var(--radius-md)', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '13px', color: 'var(--accent-amber)' }}>
                    <strong>Verification Required:</strong> Complete CAPTCHA or sign-in on employer portal, then click <strong>"I Verified — Submit AI"</strong>.
                  </div>
                  {selectedApp.job?.application_url && (
                    <a
                      href={selectedApp.job.application_url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-secondary"
                      style={{ fontSize: '12px', display: 'inline-flex', alignItems: 'center', gap: '4px', background: 'rgba(245, 158, 11, 0.2)', color: 'var(--accent-amber)' }}
                    >
                      Open in New Tab <ExternalLink size={12} />
                    </a>
                  )}
                </div>

                {/* Embedded Live IFrame Frame */}
                {selectedApp.job?.application_url ? (
                  <div style={{ border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: 'var(--radius-md)', overflow: 'hidden', height: '400px', background: '#ffffff' }}>
                    <iframe
                      src={selectedApp.job.application_url}
                      title="Embedded Job Portal"
                      style={{ width: '100%', height: '100%', border: 'none' }}
                    />
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Application URL not available for embedded preview.</p>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px' }}>
                  <button className="btn-secondary" onClick={() => setSelectedApp(null)}>Close</button>
                  <button
                    className="btn-primary"
                    style={{ background: 'var(--accent-emerald)', color: '#0f172a' }}
                    onClick={() => {
                      handleManualSubmit(selectedApp.id);
                      setSelectedApp(null);
                    }}
                  >
                    ✓ I Verified — Re-Submit Application via AI
                  </button>
                </div>
              </div>
            ) : (
              <div>
                {selectedApp.pdf_url && (
                  <div style={{ marginBottom: '16px' }}>
                    <a
                      href={getDownloadUrl(selectedApp.pdf_url)}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-primary"
                      style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
                    >
                      <FileText size={16} /> Download Tailored PDF Resume
                    </a>
                  </div>
                )}

                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '16px', maxHeight: '250px', overflowY: 'auto' }}>
                  <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>AI Generated Custom Answer Fields:</strong>
                  {Object.keys(selectedApp.answers_json || {}).length === 0 ? (
                    <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '8px' }}>Answers being generated by Gemini AI...</p>
                  ) : (
                    Object.entries(selectedApp.answers_json || {}).map(([q, a], idx) => (
                      <div key={idx} style={{ marginTop: '12px', fontSize: '13px', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '8px' }}>
                        <div style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Q: {q}</div>
                        <div style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>A: {a}</div>
                      </div>
                    ))
                  )}
                </div>

                {selectedApp.cover_letter && (
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '16px' }}>
                    <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>AI Generated Cover Letter:</strong>
                    <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '8px', whiteSpace: 'pre-line', lineHeight: '1.5' }}>
                      {selectedApp.cover_letter}
                    </p>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <button className="btn-secondary" onClick={() => setSelectedApp(null)}>Close</button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
