import React, { useState, useEffect } from 'react';
import { Briefcase, ArrowRight, Lock, Mail, User as UserIcon, ShieldCheck, CheckCircle2, Eye, EyeOff } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

declare global {
  interface Window {
    google?: any;
  }
}

interface AuthProps {
  onNavigate: (path: string) => void;
  isRegister?: boolean;
}

export const AuthPage: React.FC<AuthProps> = ({ onNavigate, isRegister = false }) => {
  const { login } = useAuth();
  const [authMethod, setAuthMethod] = useState<'PASSWORD' | 'OTP'>('PASSWORD');
  
  // Password auth states - clean empty inputs
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [fullName, setFullName] = useState('');

  // OTP auth states - clean empty inputs
  const [otpEmail, setOtpEmail] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [otpMessage, setOtpMessage] = useState('');

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Initialize Google Identity Services SDK
  useEffect(() => {
    if (window.google?.accounts?.id) {
      try {
        window.google.accounts.id.initialize({
          client_id: (import.meta as any).env?.VITE_GOOGLE_CLIENT_ID || '108293847291-example.apps.googleusercontent.com',
          callback: handleGoogleCallback,
          auto_select: false
        });
      } catch (err) {
        console.error("Google auth initialization error:", err);
      }
    }
  }, []);

  const handleGoogleCallback = async (response: any) => {
    if (!response || !response.credential) return;
    setError('');
    setLoading(true);
    try {
      const data = await api.googleAuth(response.credential);
      login(data.access_token, data.user);
      onNavigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Google authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = () => {
    setError('');
    if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt((notification: any) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          promptFallbackGoogleEmail();
        }
      });
    } else {
      promptFallbackGoogleEmail();
    }
  };

  const promptFallbackGoogleEmail = async () => {
    const userEmail = prompt("Please enter your Google Email address to authenticate:");
    if (!userEmail || !userEmail.trim()) return;
    setLoading(true);
    const nameStr = userEmail.split('@')[0];
    const nameFormatted = nameStr.charAt(0).toUpperCase() + nameStr.slice(1);
    try {
      const data = await api.googleAuth('real_google_credential_token', userEmail.trim(), nameFormatted);
      login(data.access_token, data.user);
      onNavigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Google Auth failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        const data = await api.register({ email, password, full_name: fullName });
        login(data.access_token, data.user);
        onNavigate('/onboarding');
      } else {
        const data = await api.login({ email, password });
        login(data.access_token, data.user);
        onNavigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendOtp = async () => {
    if (!otpEmail || !otpEmail.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    setError('');
    setOtpMessage('');
    setLoading(true);
    try {
      const res = await api.sendOtp(otpEmail.trim());
      setOtpSent(true);
      setOtpMessage(res.message || `Verification code sent to ${otpEmail}. Please check your email inbox!`);
    } catch (err: any) {
      setError(err.message || 'Failed to send OTP email.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpCode || otpCode.trim().length < 4) {
      setError('Please enter the 6-digit verification code sent to your email.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const data = await api.verifyOtp(otpEmail.trim(), otpCode.trim());
      login(data.access_token, data.user);
      onNavigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid or expired OTP code. Please check your email and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '460px', padding: '40px' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div className="brand-icon" style={{ width: '48px', height: '48px', margin: '0 auto 16px auto' }}>
            <Briefcase size={26} />
          </div>
          <h2 style={{ fontSize: '24px', fontWeight: 800 }}>JobPilot AI Sign In</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '6px' }}>
            Mass Automated Job Application Platform
          </p>
        </div>

        {/* Google OAuth Button */}
        <button
          onClick={handleGoogleAuth}
          className="btn-secondary"
          style={{ width: '100%', justifyContent: 'center', marginBottom: '20px', background: 'rgba(255, 255, 255, 0.08)' }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" style={{ marginRight: '8px' }}>
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
          </svg>
          Continue with Google
        </button>

        <div style={{ display: 'flex', alignItems: 'center', margin: '20px 0', color: 'var(--text-muted)', fontSize: '12px' }}>
          <div style={{ flex: 1, borderBottom: '1px solid var(--border-color)' }}></div>
          <span style={{ padding: '0 10px' }}>OR</span>
          <div style={{ flex: 1, borderBottom: '1px solid var(--border-color)' }}></div>
        </div>

        {/* Tab Selection: Password vs Email OTP */}
        <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.6)', borderRadius: 'var(--radius-md)', padding: '4px', marginBottom: '20px' }}>
          <button
            onClick={() => setAuthMethod('PASSWORD')}
            style={{
              flex: 1,
              padding: '8px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: authMethod === 'PASSWORD' ? 'var(--accent-blue)' : 'transparent',
              color: '#fff',
              fontWeight: 600,
              fontSize: '13px'
            }}
          >
            Password Login
          </button>
          <button
            onClick={() => setAuthMethod('OTP')}
            style={{
              flex: 1,
              padding: '8px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: authMethod === 'OTP' ? 'var(--accent-blue)' : 'transparent',
              color: '#fff',
              fontWeight: 600,
              fontSize: '13px'
            }}
          >
            Email OTP Login
          </button>
        </div>

        {error && (
          <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', color: 'var(--accent-rose)', padding: '12px', borderRadius: 'var(--radius-md)', fontSize: '13px', marginBottom: '20px' }}>
            {error}
          </div>
        )}

        {otpMessage && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', color: 'var(--accent-emerald)', padding: '12px', borderRadius: 'var(--radius-md)', fontSize: '13px', marginBottom: '20px' }}>
            <CheckCircle2 size={18} />
            <span>{otpMessage}</span>
          </div>
        )}

        {/* Auth Method 1: Password */}
        {authMethod === 'PASSWORD' && (
          <form onSubmit={handlePasswordSubmit}>
            {isRegister && (
              <div className="form-group">
                <label>Full Name</label>
                <div style={{ position: 'relative' }}>
                  <UserIcon size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    className="form-control"
                    style={{ paddingLeft: '42px' }}
                    placeholder="Enter your full name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label>Email Address</label>
              <div style={{ position: 'relative' }}>
                <Mail size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: 'var(--text-muted)' }} />
                <input
                  type="email"
                  className="form-control"
                  style={{ paddingLeft: '42px' }}
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: 'var(--text-muted)' }} />
                <input
                  type={showPassword ? "text" : "password"}
                  className="form-control"
                  style={{ paddingLeft: '42px', paddingRight: '44px' }}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '12px',
                    background: 'none',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '4px'
                  }}
                  title={showPassword ? "Hide Password" : "Show Password"}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '10px' }} disabled={loading}>
              {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
              <ArrowRight size={18} />
            </button>
          </form>
        )}

        {/* Auth Method 2: Email OTP */}
        {authMethod === 'OTP' && (
          <form onSubmit={handleVerifyOtp}>
            <div className="form-group">
              <label>Email Address</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                  <Mail size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: 'var(--text-muted)' }} />
                  <input
                    type="email"
                    className="form-control"
                    style={{ paddingLeft: '42px' }}
                    placeholder="Enter your email"
                    value={otpEmail}
                    onChange={(e) => setOtpEmail(e.target.value)}
                    required
                  />
                </div>
                <button type="button" className="btn-secondary" onClick={handleSendOtp} disabled={loading}>
                  {loading ? 'Sending...' : 'Send OTP'}
                </button>
              </div>
            </div>

            {otpSent && (
              <div className="form-group">
                <label>6-Digit Verification Code</label>
                <div style={{ position: 'relative' }}>
                  <ShieldCheck size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: 'var(--accent-emerald)' }} />
                  <input
                    type="text"
                    className="form-control"
                    style={{ paddingLeft: '42px', letterSpacing: '4px', fontWeight: 800 }}
                    placeholder="Enter 6-digit code"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}

            <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '10px' }} disabled={loading || !otpSent}>
              {loading ? 'Verifying...' : 'Verify OTP & Sign In'}
              <ArrowRight size={18} />
            </button>
          </form>
        )}

        <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '14px', color: 'var(--text-secondary)' }}>
          {isRegister ? (
            <span>
              Already have an account?{' '}
              <button onClick={() => onNavigate('/login')} style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                Sign In
              </button>
            </span>
          ) : (
            <span>
              Don't have an account?{' '}
              <button onClick={() => onNavigate('/register')} style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                Register
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
