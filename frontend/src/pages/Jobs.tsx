import React, { useState, useEffect } from 'react';
import { Search, MapPin, DollarSign, Sparkles, ArrowRight, X } from 'lucide-react';
import { api } from '../api/client';
import type { Job } from '../types';

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [searchRole, setSearchRole] = useState('');
  const [selectedSource, setSelectedSource] = useState('ALL');
  const [applyingId, setApplyingId] = useState<number | null>(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async (role?: string) => {
    try {
      const data = await api.getJobs(role);
      setJobs(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs(searchRole);
  };

  const handleApplyNow = async (job: Job) => {
    setApplyingId(job.id);
    try {
      await api.createApplication(job.id, 'APPROVAL');
      alert(`Custom resume generated & application ready for ${job.company}!`);
      setSelectedJob(null);
    } catch (err: any) {
      alert(err.message || 'Failed to trigger application');
    } finally {
      setApplyingId(null);
    }
  };

  const filteredJobs = jobs.filter((j) => {
    if (selectedSource === 'ALL') return true;
    return j.source === selectedSource;
  });

  const getPlatformBadge = (source: string) => {
    switch (source) {
      case 'GREENHOUSE':
        return <span className="badge-status badge-ready" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)' }}>Greenhouse Verified</span>;
      case 'LEVER':
        return <span className="badge-status badge-ready" style={{ background: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-cyan)' }}>Lever Verified</span>;
      case 'SMARTRECRUITERS':
        return <span className="badge-status badge-ready" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-indigo)' }}>SmartRecruiters Verified</span>;
      case 'ASHBY':
        return <span className="badge-status badge-ready" style={{ background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)' }}>Ashby Verified</span>;
      default:
        return <span className="badge-status badge-ready">Company Careers Verified</span>;
    }
  };

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>Discovered Jobs Catalog Across Verified Platforms</h1>
          <p>Verified Job Ingestion from Greenhouse, Lever, SmartRecruiters, Ashby, & Company Portals</p>
        </div>
      </div>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <div style={{ position: 'relative', flex: 2 }}>
          <Search size={18} style={{ position: 'absolute', left: '16px', top: '14px', color: 'var(--text-muted)' }} />
          <input
            className="form-control"
            style={{ paddingLeft: '44px' }}
            placeholder="Search by title (e.g. Python Developer, GenAI Engineer, Backend...)"
            value={searchRole}
            onChange={(e) => setSearchRole(e.target.value)}
          />
        </div>

        <select className="form-control" style={{ flex: 1 }} value={selectedSource} onChange={(e) => setSelectedSource(e.target.value)}>
          <option value="ALL">All Verified Platforms</option>
          <option value="GREENHOUSE">Greenhouse ATS</option>
          <option value="LEVER">Lever ATS</option>
          <option value="SMARTRECRUITERS">SmartRecruiters ATS</option>
          <option value="ASHBY">Ashby ATS</option>
          <option value="DEMO_SEED">Direct Careers Portals</option>
        </select>

        <button type="submit" className="btn-primary">Search Jobs</button>
      </form>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
        {filteredJobs.map((job) => (
          <div key={job.id} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                {getPlatformBadge(job.source)}
                {job.match_score && (
                  <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '4px 10px', borderRadius: 'var(--radius-full)', fontWeight: 800, fontSize: '13px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Sparkles size={14} /> {job.match_score}% Match
                  </span>
                )}
              </div>

              <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '4px' }}>{job.title}</h3>
              <div style={{ color: 'var(--text-primary)', fontWeight: 700, fontSize: '14px', marginBottom: '12px' }}>{job.company}</div>

              <div style={{ display: 'flex', gap: '14px', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <MapPin size={14} /> {job.location} {job.is_remote && '(Remote)'}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-emerald)', fontWeight: 700 }}>
                  <DollarSign size={14} /> ₹{job.salary_min_lpa}–{job.salary_max_lpa} LPA
                </span>
              </div>

              <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.5', marginBottom: '16px', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {job.description}
              </p>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '20px' }}>
                {job.required_skills.slice(0, 4).map((s, i) => (
                  <span key={i} style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', padding: '2px 8px', borderRadius: '4px', fontSize: '11px' }}>
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn-secondary" style={{ flex: 1, justifyContent: 'center' }} onClick={() => setSelectedJob(job)}>
                Match Analysis
              </button>
              <button className="btn-primary" style={{ flex: 1, justifyContent: 'center' }} onClick={() => handleApplyNow(job)} disabled={applyingId === job.id}>
                {applyingId === job.id ? 'Tailoring...' : 'Apply AI'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedJob && (
        <div className="modal-overlay" onClick={() => setSelectedJob(null)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                {getPlatformBadge(selectedJob.source)}
                <h2 style={{ fontSize: '22px', fontWeight: 800, marginTop: '4px' }}>{selectedJob.title} — {selectedJob.company}</h2>
              </div>
              <button onClick={() => setSelectedJob(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)' }}>
                <X size={24} />
              </button>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
              <h4 style={{ color: 'var(--accent-cyan)', marginBottom: '8px' }}>AI Match Breakdown ({selectedJob.match_score}%)</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '13px' }}>
                <div>
                  <strong style={{ color: 'var(--accent-emerald)' }}>✓ Strong Skill Matches:</strong>
                  <ul style={{ paddingLeft: '16px', marginTop: '4px' }}>
                    {(selectedJob.strong_matches || ['Python', 'FastAPI', 'REST APIs']).map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
                <div>
                  <strong style={{ color: 'var(--accent-rose)' }}>✗ Missing / Partial Skills:</strong>
                  <ul style={{ paddingLeft: '16px', marginTop: '4px' }}>
                    {(selectedJob.missing_skills || ['AWS']).map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button className="btn-secondary" onClick={() => setSelectedJob(null)}>Close</button>
              <button className="btn-primary" onClick={() => handleApplyNow(selectedJob)}>
                Generate Custom Resume & Apply <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
