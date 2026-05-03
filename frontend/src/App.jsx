import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { LayoutDashboard, Database, Users, FileText, LogOut, ShieldCheck, Bell, Globe } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Ledgers from './pages/Ledgers';
import LedgerDetail from './pages/LedgerDetail';
import SBLCDetail from './pages/SBLCDetail';
import Participants from './pages/Participants';
import AuditHistory from './pages/AuditHistory';
import PublicVerify from './pages/PublicVerify';
import Onboarding from './pages/Onboarding';
import Analytics from './pages/Analytics';
import Explorer from './pages/Explorer';
import BankingCompliance from './pages/BankingCompliance';
import { authService } from './services/api';
import RoleGuard from './components/RoleGuard';
import ToastContainer, { toast } from './components/Toast';
import './i18n';
import { useTranslation } from 'react-i18next';
import { Sun, Moon, Languages, BarChart3 } from 'lucide-react';

const ProtectedRoute = ({ children }) => {
    // Auth bypass enabled by user request
    return children;
};

const Layout = ({ user, children, onLogout }) => {
    const { t, i18n } = useTranslation();

    useEffect(() => {
        const dir = i18n.language === 'ar' ? 'rtl' : 'ltr';
        document.documentElement.dir = dir;
        document.documentElement.lang = i18n.language;
    }, [i18n.language]);

    const changeLang = (lang) => {
        i18n.changeLanguage(lang);
    };

    const languages = [
        { code: 'en', label: 'English' },
        { code: 'ar', label: 'العربية' },
        { code: 'zh', label: '中文' },
        { code: 'ru', label: 'Русский' },
        { code: 'hi', label: 'हिन्दी' },
        { code: 'fr', label: 'Français' },
        { code: 'de', label: 'Deutsch' },
        { code: 'es', label: 'Español' }
    ];

    return (
        <div className="app-container">
            <aside className="sidebar">
                <div className="flex items-center gap-3 mb-10 px-6">
                    <div className="p-2 border border-[var(--color-border-gold)] bg-[#000000] rounded">
                        <ShieldCheck className="text-[var(--color-gold)]" size={28} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-white tracking-tight">SBLC Ledger</h2>
                        <p className="text-[9px] text-[var(--color-gold)] uppercase tracking-[0.2em] font-black">Bullion Registry</p>
                    </div>
                </div>

                <nav className="flex flex-col gap-1 px-4">
                    <Link to="/" className="nav-link">
                        <LayoutDashboard size={18} />
                        <span>{t('dashboard')}</span>
                    </Link>
                    <Link to="/ledgers" className="nav-link">
                        <Database size={18} />
                        <span>{t('ledgers')}</span>
                    </Link>
                    <Link to="/analytics" className="nav-link">
                        <BarChart3 size={18} />
                        <span>{t('analytics')}</span>
                    </Link>
                    <Link to="/explorer" className="nav-link">
                        <Database size={18} className="text-[var(--color-gold)]" />
                        <span>{t('explorer')}</span>
                    </Link>
                    <Link to="/banking" className="nav-link">
                        <Globe size={18} className="text-blue-400" />
                        <span>Banking</span>
                    </Link>
                    <Link to="/participants" className="nav-link">
                        <Users size={18} />
                        <span>{t('participants')}</span>
                    </Link>
                    <Link to="/audits" className="nav-link">
                        <FileText size={18} />
                        <span>{t('audit')}</span>
                    </Link>
                </nav>

                <div className="mt-auto px-4 pb-8 space-y-6">
                    <div className="metallic-line mb-6"></div>

                    <div className="relative group px-2">
                        <div className="flex items-center gap-2 p-2 bg-[#0a0a0a] border border-[#1a1a1a] rounded cursor-pointer hover:bg-[#1a1a1a] transition-colors">
                            <Languages size={16} className="text-white" />
                            <span className="text-[10px] font-bold uppercase text-white">{i18n.language}</span>
                        </div>
                        <div className="absolute bottom-full mb-2 left-0 w-32 bg-[#000000] border border-[#1a1a1a] rounded shadow-2xl opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-all z-50 overflow-hidden">
                            {languages.map(lang => (
                                <button
                                    key={lang.code}
                                    onClick={() => changeLang(lang.code)}
                                    className="w-full text-left p-2 text-[10px] hover:bg-[#1a1a1a] text-white font-bold transition-colors border-b border-[#1a1a1a] last:border-0"
                                >
                                    {lang.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="p-4 bg-[#0a0a0a] rounded border border-[#1a1a1a]">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded bg-[#000000] flex items-center justify-center text-white font-bold border border-[#1a1a1a]">
                                {user?.full_name?.charAt(0) || 'U'}
                            </div>
                            <div className="overflow-hidden">
                                <p className="font-bold text-xs text-white truncate">{user?.full_name || 'User'}</p>
                                <p className="text-[9px] text-[#a0a0a0] truncate font-mono">{user?.role_name || 'Participant'}</p>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={onLogout}
                        className="flex items-center gap-3 w-full p-3 text-[#a0a0a0] hover:text-white transition-colors"
                    >
                        <LogOut size={18} />
                        <span className="font-bold text-xs uppercase tracking-widest">{t('sign_out')}</span>
                    </button>
                </div>
            </aside>

            <main className="main-content px-12">
                <header className="flex justify-between items-center py-8 mb-16 border-b border-[#1a1a1a]">
                    <div className="flex items-center gap-4 text-[#a0a0a0]">
                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                        <span className="text-[10px] font-black uppercase tracking-[0.4em]">Institutional Network Secure</span>
                    </div>
                    <div className="flex items-center gap-8">
                        <div className="badge badge-gold">
                            <div className="w-1.5 h-1.5 bg-[#d4af37] rounded-full animate-pulse"></div>
                            {t('live')}
                        </div>
                        <Bell size={18} className="text-white cursor-pointer hover:text-[#d4af37] transition-colors" />
                    </div>
                </header>
                {children}
            </main>
        </div>
    );
};

const App = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');

    // Real-time Network Events
    const useNetworkWS = () => {
        useEffect(() => {
            const ws = new WebSocket(`ws://localhost:8000/ws/events`);
            ws.onmessage = (event) => {
                const d = JSON.parse(event.data);
                if (d.type) toast(`Institutional Event: ${d.type}`, 'info');
            };
            return () => ws.close();
        }, []);
    };
    useNetworkWS();

    useEffect(() => {
        // Auth bypass: Fetch the rescue user from the backend unconditionally
        authService.getMe()
            .then(res => setUser(res.data))
            .catch(() => {
                // If backend somehow fails, then and only then provide a safety mock
                setUser({
                    id: 'guest-uuid',
                    full_name: 'Guest Administrator',
                    email: 'guest@institutional.ledger',
                    role_name: 'IssuerOps'
                });
            })
            .finally(() => setLoading(false));
    }, []);

    const handleLogout = async () => {
        try {
            await authService.logout();
        } catch (e) { }
        localStorage.clear();
        setUser(null);
        window.location.href = '/login';
    };

    const toggleTheme = () => {
        const next = theme === 'dark' ? 'light' : 'dark';
        setTheme(next);
        localStorage.setItem('theme', next);
    };

    if (loading) return null;

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="/" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <Dashboard user={user} />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/analytics" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <Analytics />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/explorer" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <Explorer />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/ledgers" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <Ledgers />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/ledgers/:ledgerId" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <LedgerDetail />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/ledgers/:ledgerId/sblcs/:sblcId" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <SBLCDetail />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/participants" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <Participants />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/audits" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <AuditHistory />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/banking" element={
                    <ProtectedRoute>
                        <Layout user={user} onLogout={handleLogout} theme={theme} onThemeToggle={toggleTheme}>
                            <BankingCompliance />
                        </Layout>
                    </ProtectedRoute>
                } />
                <Route path="/verify/:reference" element={<PublicVerify />} />
                <Route path="/onboarding" element={<Onboarding />} />
            </Routes>
            <ToastContainer />
        </Router>
    );
};

export default App;
