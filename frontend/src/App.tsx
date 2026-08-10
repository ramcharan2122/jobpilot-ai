import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { AuthPage } from './pages/Login';
import { Onboarding } from './pages/Onboarding';
import { Dashboard } from './pages/Dashboard';
import { ProfilePage } from './pages/Profile';
import { PreferencesPage } from './pages/Preferences';
import { JobsPage } from './pages/Jobs';
import { ApplicationsPage } from './pages/Applications';
import { ResumesPage } from './pages/Resumes';
import { CampaignsPage } from './pages/Campaigns';
import { MockPortalSimPage } from './pages/MockPortal';
import { ConnectedPlatformsPage } from './pages/ConnectedPlatforms';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();
  const [currentPath, setCurrentPath] = useState('/dashboard');

  if (loading) {
    return (
      <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
        Loading JobPilot AI...
      </div>
    );
  }

  if (!user) {
    if (currentPath === '/register') {
      return <AuthPage onNavigate={setCurrentPath} isRegister={true} />;
    }
    return <AuthPage onNavigate={setCurrentPath} isRegister={false} />;
  }

  if (currentPath === '/onboarding') {
    return <Onboarding onComplete={() => setCurrentPath('/dashboard')} />;
  }

  const renderPageComponent = () => {
    switch (currentPath) {
      case '/dashboard':
        return <Dashboard onNavigate={setCurrentPath} />;
      case '/profile':
        return <ProfilePage />;
      case '/preferences':
        return <PreferencesPage />;
      case '/platforms':
        return <ConnectedPlatformsPage />;
      case '/jobs':
        return <JobsPage />;
      case '/applications':
        return <ApplicationsPage />;
      case '/resumes':
        return <ResumesPage />;
      case '/campaigns':
        return <CampaignsPage />;
      case '/mock-portal-sim':
        return <MockPortalSimPage />;
      default:
        return <Dashboard onNavigate={setCurrentPath} />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar currentPath={currentPath} onNavigate={setCurrentPath} />
      <main className="main-content">
        {renderPageComponent()}
      </main>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
