import React, { useState, useEffect } from 'react';
import { Link2, CheckCircle2, ShieldCheck, RefreshCw, Unlink, Lock, Key } from 'lucide-react';
import { api } from '../api/client';

interface PlatformStatus {
  platform_name: string;
  display_name: string;
  username_or_email: string | null;
  is_connected: boolean;
  last_synced_at: string | null;
}

export const ConnectedPlatformsPage: React.FC = () => {
  const [platforms, setPlatforms] = useState<PlatformStatus[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedPlatform, setSelectedPlatform] = useState<PlatformStatus | null>(null);
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [connecting, setConnecting] = useState<boolean>(false);

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    setLoading(true);
    try {
      const data = await api.getConnectedPlatforms();
      setPlatforms(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenConnect = (plat: PlatformStatus) => {
    setSelectedPlatform(plat);
    setUsername(plat.username_or_email || '');
    setPassword('');
  };

  const handleSaveConnection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlatform || !username) return;
    setConnecting(true);
    try {
      const res = await api.connectPlatform({
        platform_name: selectedPlatform.platform_name,
        username_or_email: username,
        auth_credentials: password || 'session_token_verified'
      });
      alert(res.message || `Successfully linked ${selectedPlatform.display_name}!`);
      setSelectedPlatform(null);
      await fetchPlatforms();
    } catch (err: any) {
      alert(err.message || 'Failed to connect platform account');
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async (platformName: string) => {
    if (!confirm(`Are you sure you want to disconnect ${platformName}?`)) return;
    try {
      await api.disconnectPlatform(platformName);
      await fetchPlatforms();
    } catch (err: any) {
      alert(err.message || 'Failed to disconnect platform');
    }
  };

  const getPlatformIcon = (name: string) => {
    switch (name) {
      case 'LINKEDIN':
        return <div style={{ background: '#0a66c2', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>in</div>;
      case 'NAUKRI':
        return <div style={{ background: '#004080', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>Naukri</div>;
      case 'INDEED':
        return <div style={{ background: '#003a9b', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>Indeed</div>;
      case 'INSTAHYRE':
        return <div style={{ background: '#6b21a8', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>Instahyre</div>;
      case 'WELLFOUND':
        return <div style={{ background: '#f97316', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>Wellfound</div>;
      case 'FOUNDIT':
        return <div style={{ background: '#059669', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>Foundit</div>;
      case 'UNSTOP':
        return <div style={{ background: '#0284c7', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>Unstop</div>;
      default:
        return <div style={{ background: '#16a34a', color: '#fff', padding: '10px 14px', borderRadius: 'var(--radius-md)', fontWeight: 800, fontSize: '14px' }}>Glassdoor</div>;
    }
  };

  return (
    <div>
      <div className="top-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="page-title">
          <h1>Connected Platforms & Auto-Apply Integrations</h1>
          <p>Link your candidate hiring accounts to let JobPilot AI auto-apply directly from your authenticated profile.</p>
        </div>
        <button className="btn-secondary" onClick={() => fetchPlatforms()} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh Integrations
        </button>
      </div>

      <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '16px 20px', borderRadius: 'var(--radius-md)', marginBottom: '28px', display: 'flex', alignItems: 'center', gap: '14px' }}>
        <ShieldCheck size={24} style={{ color: 'var(--accent-emerald)', flexShrink: 0 }} />
        <div style={{ fontSize: '13.5px', color: 'var(--text-primary)', lineHeight: '1.5' }}>
          <strong>Secure OAuth & Encrypted Session Credentials:</strong> Your platform integration tokens and credentials are encrypted using AES-256 standards. Playwright browser engines reuse your authenticated session state to execute direct 1-click applications.
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
        {platforms.map((plat) => (
          <div key={plat.platform_name} className="glass-panel stat-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '200px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {getPlatformIcon(plat.platform_name)}
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 800 }}>{plat.display_name}</h3>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {plat.username_or_email || 'No account linked'}
                    </div>
                  </div>
                </div>
              </div>

              {plat.is_connected ? (
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '4px 10px', borderRadius: '999px', fontSize: '11.5px', fontWeight: 700, marginBottom: '16px' }}>
                  <CheckCircle2 size={13} /> CONNECTED & AUTO-APPLY ACTIVE
                </div>
              ) : (
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(148, 163, 184, 0.15)', color: 'var(--text-muted)', border: '1px solid rgba(148, 163, 184, 0.3)', padding: '4px 10px', borderRadius: '999px', fontSize: '11.5px', fontWeight: 600, marginBottom: '16px' }}>
                  <Lock size={12} /> NOT LINKED
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                className="btn-primary"
                style={{ flex: 1, padding: '8px 12px', fontSize: '12.5px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                onClick={() => handleOpenConnect(plat)}
              >
                <Link2 size={14} /> {plat.is_connected ? 'Update Credentials' : 'Link Account'}
              </button>
              {plat.is_connected && (
                <button
                  className="btn-secondary"
                  style={{ padding: '8px 12px', fontSize: '12.5px', color: '#fca5a5', border: '1px solid rgba(239, 68, 68, 0.3)' }}
                  onClick={() => handleDisconnect(plat.platform_name)}
                  title="Disconnect Platform"
                >
                  <Unlink size={14} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Link Account Modal */}
      {selectedPlatform && (
        <div className="modal-overlay" onClick={() => setSelectedPlatform(null)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '500px', width: '90%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              {getPlatformIcon(selectedPlatform.platform_name)}
              <div>
                <h2 style={{ fontSize: '18px', fontWeight: 800 }}>Connect {selectedPlatform.display_name}</h2>
                <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>Enter your registered profile email or username to enable direct account application submission.</p>
              </div>
            </div>

            <form onSubmit={handleSaveConnection}>
              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600 }}>Registered Account Email / Candidate Username</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. candidate@gmail.com"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600 }}>Account Password / OAuth Access Token (Optional)</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Enter password or session key to enable 1-click submit"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <Key size={16} style={{ position: 'absolute', right: '12px', top: '12px', color: 'var(--text-muted)' }} />
                </div>
                <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                  Credentials are encrypted in Supabase Vault and used strictly by Playwright for account login.
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="btn-secondary" onClick={() => setSelectedPlatform(null)}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={connecting} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  <Link2 size={14} /> {connecting ? 'Connecting & Verifying...' : 'Save & Enable Auto-Apply'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
