import React from 'react';
import { LayoutDashboard, User, Sliders, Briefcase, FileCheck, Layers, FileText, Globe, LogOut, Link2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPath, onNavigate }) => {
  const { logout } = useAuth();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Profile & Resume', path: '/profile', icon: User },
    { label: 'LPA & Preferences', path: '/preferences', icon: Sliders },
    { label: 'Connected Platforms', path: '/platforms', icon: Link2 },
    { label: 'Jobs Discovery', path: '/jobs', icon: Briefcase },
    { label: 'Applications', path: '/applications', icon: FileCheck },
    { label: 'Resume Library', path: '/resumes', icon: FileText },
    { label: 'Mass Campaigns', path: '/campaigns', icon: Layers },
    { label: 'Mock ATS Simulator', path: '/mock-portal-sim', icon: Globe },
  ];

  return (
    <aside className="sidebar">
      <div className="brand-logo">
        <div className="brand-icon">
          <Briefcase size={20} />
        </div>
        <span>JobPilot AI</span>
        <span className="demo-badge">DEMO</span>
      </div>

      <nav className="nav-menu">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPath === item.path;
          return (
            <button
              key={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onNavigate(item.path)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
        <button className="nav-item" onClick={logout} style={{ width: '100%', color: 'var(--accent-rose)' }}>
          <LogOut size={18} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
