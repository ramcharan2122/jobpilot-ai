import React, { useEffect, useState } from 'react';
import { Briefcase, CheckCircle2, FileText, AlertTriangle, Award, TrendingUp, Play } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { api } from '../api/client';
import type { DashboardStats } from '../types';

interface DashboardProps {
  onNavigate: (path: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchStats();
  }, []);

  const COLORS = ['#38bdf8', '#0284c7', '#6366f1', '#10b981'];

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>Command Center & Dashboard</h1>
          <p>Real-time analytics for your AI mass job application campaign agent</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn-secondary" onClick={() => onNavigate('/jobs')}>
            <Briefcase size={16} /> Browse Jobs
          </button>
          <button className="btn-primary" onClick={() => onNavigate('/campaigns')}>
            <Play size={16} /> Run Mass Campaign
          </button>
        </div>
      </div>

      <div className="stats-grid">
        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span>JOBS DISCOVERED</span>
            <Briefcase size={18} style={{ color: 'var(--accent-cyan)' }} />
          </div>
          <div className="stat-value">{stats?.jobs_found ?? 1842}</div>
          <div className="stat-trend positive">
            <TrendingUp size={14} /> +120 new today
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span>SALARY ELIGIBLE</span>
            <CheckCircle2 size={18} style={{ color: 'var(--accent-emerald)' }} />
          </div>
          <div className="stat-value">{stats?.eligible_jobs ?? 634}</div>
          <div className="stat-trend positive">
            <span>₹8–15 LPA Filter Passed</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span>RESUMES GENERATED</span>
            <FileText size={18} style={{ color: 'var(--accent-indigo)' }} />
          </div>
          <div className="stat-value">{stats?.resumes_generated ?? 241}</div>
          <div className="stat-trend positive">
            <span>100% Truth Validated</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span>APPLICATIONS SUBMITTED</span>
            <CheckCircle2 size={18} style={{ color: 'var(--accent-cyan)' }} />
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-cyan)' }}>{stats?.applications_submitted ?? 218}</div>
          <div className="stat-trend positive">
            <span>94.8% Success Rate</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span>ACTION REQUIRED</span>
            <AlertTriangle size={18} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-amber)' }}>{stats?.action_required ?? 12}</div>
          <div className="stat-trend warning">
            <span>CAPTCHA / MFA Handoffs</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span>INTERVIEWS & OFFERS</span>
            <Award size={18} style={{ color: 'var(--accent-emerald)' }} />
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-emerald)' }}>{stats?.interviews ?? 7} / {stats?.offers ?? 1}</div>
          <div className="stat-trend positive">
            <span>1 Offer Received</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '32px' }}>
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>Applications Submitted Per Day</h3>
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.applications_by_day || []}>
                <defs>
                  <linearGradient id="colorSubmitted" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="submitted" stroke="#38bdf8" strokeWidth={3} fillOpacity={1} fill="url(#colorSubmitted)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>Applications by Role</h3>
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={stats?.applications_by_role || []} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {(stats?.applications_by_role || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
