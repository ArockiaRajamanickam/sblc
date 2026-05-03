import React, { useState } from 'react';
import { ShieldCheck, Lock, Mail, Loader2, Globe } from 'lucide-react';
import { authService } from '../services/api';

const Login = ({ onLoginSuccess }) => {
    const [identity, setIdentity] = useState(null); // 'issuer', 'applicant', 'beneficiary', 'auditor'
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const data = await authService.login(email, password);
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            const userRes = await authService.getMe();
            onLoginSuccess(userRes.data);
            window.location.href = '/';
        } catch (err) {
            setError(err.response?.data?.detail || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    const identities = [
        { id: 'issuer', title: 'Institutional Issuer', icon: ShieldCheck, desc: 'Central Banks & Financial Institutions' },
        { id: 'applicant', title: 'Corporate Applicant', icon: Globe, desc: 'Importers & Credit Requesters' },
        { id: 'beneficiary', title: 'Trade Beneficiary', icon: Mail, desc: 'Exporters & Commodity Suppliers' },
        { id: 'auditor', title: 'Network Auditor', icon: Lock, desc: 'Regulatory & Compliance Oversight' }
    ];

    if (!identity) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center p-10 bg-[#000000] relative overflow-hidden">
                <div className="text-center mb-20 animate-institutional">
                    <h1 className="text-5xl font-black text-white tracking-tighter uppercase mb-4">Sovereign Gateway</h1>
                    <div className="flex items-center justify-center gap-4">
                        <div className="h-[1px] w-12 bg-[#d4af37]"></div>
                        <p className="text-[10px] text-[#a0a0a0] font-black uppercase tracking-[0.5em]">Who am I?</p>
                        <div className="h-[1px] w-12 bg-[#d4af37]"></div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-5xl animate-institutional">
                    {identities.map((id) => (
                        <button
                            key={id.id}
                            onClick={() => setIdentity(id.id)}
                            className="group p-12 bg-[#0a0a0a] border border-[#1a1a1a] rounded-sm hover:border-[#d4af37] transition-all text-left flex items-start gap-8"
                        >
                            <div className="p-5 bg-[#000000] border border-[#1a1a1a] rounded-sm group-hover:border-[#d4af37] transition-colors">
                                <id.icon className="text-[#a0a0a0] group-hover:text-[#d4af37] transition-colors" size={32} />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-white mb-2">{id.title}</h3>
                                <p className="text-[10px] text-[#a0a0a0] font-black uppercase tracking-widest">{id.desc}</p>
                            </div>
                        </button>
                    ))}
                </div>

                <div className="mt-20">
                    <p className="text-[9px] text-[#333333] font-black uppercase tracking-[0.2em]">SBLC Ledger Governance Tier-1 Encryption Enabled</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center p-10 bg-[#000000] relative overflow-hidden">
            <div className="w-full max-w-xl bg-[#0a0a0a] border border-[#1a1a1a] p-16 rounded-sm animate-institutional relative z-10">
                <button
                    onClick={() => setIdentity(null)}
                    className="absolute top-10 left-10 text-[9px] text-[#a0a0a0] font-black uppercase tracking-widest hover:text-[#d4af37] transition-colors"
                >
                    &larr; Switch Identity
                </button>

                <div className="flex flex-col items-center mb-16 mt-4">
                    <div className="p-5 border border-[#d4af37] bg-[#1a160d] rounded-sm mb-8">
                        {(() => {
                            const ActiveIcon = identities.find(id => id.id === identity).icon;
                            return <ActiveIcon className="text-[#d4af37]" size={48} />;
                        })()}
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tighter uppercase mb-3">Authorize Session</h1>
                    <p className="text-[10px] text-[#a0a0a0] font-black uppercase tracking-[0.3em] text-center">
                        Accessing as {identity.charAt(0).toUpperCase() + identity.slice(1)} Channel
                    </p>
                </div>

                {error && (
                    <div className="mb-10 p-5 border border-red-900 bg-[#0a0000] rounded-sm text-red-500 text-xs font-bold flex items-center gap-4">
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full"></div>
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-10">
                    <div className="space-y-4">
                        <label className="text-[10px] font-black text-[#a0a0a0] uppercase tracking-[0.2em] ml-1">Institutional Email</label>
                        <div className="relative group">
                            <Mail className="absolute left-6 top-5 text-[#333333] group-focus-within:text-[#d4af37] transition-colors" size={20} />
                            <input
                                type="email"
                                required
                                className="w-full bg-[#000000] border border-[#1a1a1a] rounded-sm py-5 pl-16 pr-6 text-white focus:outline-none focus:border-[#d4af37] transition-all font-bold text-sm h-16 placeholder:text-[#333333]"
                                placeholder="officer@sovereign.bank"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="space-y-4">
                        <label className="text-[10px] font-black text-[#a0a0a0] uppercase tracking-[0.2em] ml-1">Authorization Key</label>
                        <div className="relative group">
                            <Lock className="absolute left-6 top-5 text-[#333333] group-focus-within:text-[#d4af37] transition-colors" size={20} />
                            <input
                                type="password"
                                required
                                className="w-full bg-[#000000] border border-[#1a1a1a] rounded-sm py-5 pl-16 pr-6 text-white focus:outline-none focus:border-[#d4af37] transition-all font-bold text-sm h-16 placeholder:text-[#333333]"
                                placeholder="••••••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full btn-primary h-18 text-base flex items-center justify-center gap-5"
                    >
                        {loading ? (
                            <Loader2 className="animate-spin" size={24} />
                        ) : (
                            <>
                                <span>Sign Protocol Entry</span>
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-16 pt-10 border-t border-[#1a1a1a] flex flex-col items-center gap-4">
                    <p className="text-center text-[9px] text-[#333333] font-black uppercase tracking-[0.2em] leading-relaxed max-w-xs">
                        Unauthorized access is strictly prohibited. All sessions are cryptographically logged.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
