import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';
import { adminService } from '../services/api';
import { useTranslation } from 'react-i18next';

const Onboarding = () => {
    const { t } = useTranslation();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const token = searchParams.get('token');

    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirm) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        setError('');
        try {
            await adminService.setupPassword(token, password);
            setSuccess(true);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Activation failed');
        } finally {
            setLoading(false);
        }
    };

    if (success) return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0b0d] p-10">
            <div className="glass p-16 rounded-sm text-center max-w-xl animate-institutional">
                <CheckCircle2 className="text-[var(--color-gold)] mx-auto mb-10" size={80} />
                <h2 className="text-4xl font-bold text-white mb-4 tracking-tighter uppercase">Protocol Ready</h2>
                <p className="text-[var(--color-text-muted)] font-black uppercase tracking-widest text-xs">Your institutional credentials have been established. Redirecting to secure login...</p>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0b0d] p-10 relative overflow-hidden">
            <div className="w-full max-w-xl glass p-16 rounded-sm animate-institutional relative z-10 border border-white/5">
                <div className="flex flex-col items-center mb-16">
                    <div className="p-5 border border-[var(--color-border-gold)] bg-[var(--color-gold)]/5 rounded-sm mb-8">
                        <ShieldCheck className="text-[var(--color-gold)]" size={48} />
                    </div>
                    <h1 className="text-4xl font-bold text-white tracking-tighter uppercase mb-3">{t('onboarding')}</h1>
                    <p className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-[0.3em] text-center">
                        Establish Network Authority Keys
                    </p>
                </div>

                {error && (
                    <div className="mb-10 p-5 border border-red-500/20 bg-red-500/5 rounded-sm text-red-500 text-xs font-bold flex items-center gap-4">
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full"></div>
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-10">
                    <div className="space-y-4">
                        <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em] ml-1">{t('setup_password')}</label>
                        <div className="relative group">
                            <Lock className="absolute left-6 top-5 text-[var(--color-silver)]/40 group-focus-within:text-[var(--color-gold)] transition-colors" size={20} />
                            <input
                                type="password"
                                required
                                minLength={8}
                                className="w-full bg-white/5 border border-white/10 rounded-sm py-5 pl-16 pr-6 text-white focus:outline-none focus:border-[var(--color-gold)] transition-all font-bold text-sm h-16 placeholder:text-white/10"
                                placeholder="••••••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="space-y-4">
                        <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em] ml-1">Confirm Session Key</label>
                        <div className="relative group">
                            <Lock className="absolute left-6 top-5 text-[var(--color-silver)]/40 group-focus-within:text-[var(--color-gold)] transition-colors" size={20} />
                            <input
                                type="password"
                                required
                                className="w-full bg-white/5 border border-white/10 rounded-sm py-5 pl-16 pr-6 text-white focus:outline-none focus:border-[var(--color-gold)] transition-all font-bold text-sm h-16 placeholder:text-white/10"
                                placeholder="••••••••••••"
                                value={confirm}
                                onChange={(e) => setConfirm(e.target.value)}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading || !token}
                        className="w-full btn-primary h-18 text-base flex items-center justify-center gap-5"
                    >
                        {loading ? <Loader2 className="animate-spin" size={24} /> : <>{t('onboarding')} <ArrowRight size={20} /></>}
                    </button>
                    {!token && <p className="text-[9px] text-red-500 text-center font-black uppercase tracking-widest mt-6">Missing Invitation Anchor</p>}
                </form>
            </div>
        </div>
    );
};

export default Onboarding;
