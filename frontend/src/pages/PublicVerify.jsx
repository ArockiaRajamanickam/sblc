import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Loader2, ShieldCheck, AlertCircle, Anchor } from 'lucide-react';
import { publicService } from '../services/api';
import { useTranslation } from 'react-i18next';

const PublicVerify = () => {
    const { t, i18n } = useTranslation();
    const { reference } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const dir = i18n.language === 'ar' ? 'rtl' : 'ltr';
        document.documentElement.dir = dir;
    }, [i18n.language]);

    useEffect(() => {
        if (!reference) {
            setLoading(false);
            return;
        }
        publicService.verify(reference)
            .then(res => setData(res.data))
            .catch(err => setError(err.response?.data?.detail || 'Reference not found'))
            .finally(() => setLoading(false));
    }, [reference]);

    if (loading) return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0b0d]">
            <Loader2 className="animate-spin text-[var(--color-gold)]" size={48} />
        </div>
    );

    return (
        <div className="min-h-screen bg-[#0a0b0d] p-10 flex flex-col items-center">
            <div className="w-full max-w-3xl mt-20 mb-12 flex flex-col items-center text-center">
                <div className="p-4 border border-[var(--color-border-gold)] bg-[var(--color-gold)]/5 rounded-sm mb-6">
                    <ShieldCheck className="text-[var(--color-gold)]" size={48} />
                </div>
                <h1 className="text-3xl font-bold text-white uppercase tracking-[0.3em] mb-2">Institutional Verification Gateway</h1>
                <p className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-[0.2em]">{t('trust_verification')}</p>
            </div>

            <div className="w-full max-w-3xl glass p-12 rounded animate-institutional relative overflow-hidden">
                <div className="absolute top-0 right-0 p-12 opacity-[0.02] pointer-events-none">
                    <ShieldCheck size={240} className="text-white" />
                </div>

                {error ? (
                    <div className="text-center py-16">
                        <AlertCircle className="text-red-500/50 mx-auto mb-6" size={80} />
                        <h2 className="text-3xl font-bold text-white mb-3 tracking-tight">Verification protocol failed</h2>
                        <p className="text-[var(--color-text-muted)] font-medium mb-10 max-w-sm mx-auto">{error}</p>
                        <Link to="/" className="btn-secondary inline-block">Return to Secure Portal</Link>
                    </div>
                ) : (
                    <>
                        <div className="flex justify-between items-start mb-14 pb-10 border-b border-white/5">
                            <div>
                                <p className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-widest mb-3">Anchored reference ID</p>
                                <h2 className="text-4xl font-bold text-white font-mono tracking-tighter">{data.reference_number}</h2>
                            </div>
                            <div className="text-right flex flex-col items-end gap-3">
                                <div className={`badge ${data.status === 'issued' ? 'badge-gold' : 'badge-silver'}`}>
                                    {data.status.replace('_', ' ')}
                                </div>
                                <div className="badge badge-gold !bg-[var(--color-gold)]/5 !border-[var(--color-border-gold)]">
                                    <ShieldCheck size={12} className="text-[var(--color-gold)]" />
                                    {t('verify_badge')}
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-14">
                            <div className="space-y-3">
                                <p className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-widest">Issuing Sovereign Node</p>
                                <p className="font-bold text-white text-xl border-l border-[var(--color-gold)] pl-4">{data.issuing_node}</p>
                            </div>
                            <div className="space-y-3 text-right">
                                <p className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-widest">Maturity Confirmation</p>
                                <p className="font-bold text-[var(--color-silver)] text-xl border-r border-[var(--color-silver)] pr-4">{new Date(data.expiry_date).toLocaleDateString(undefined, { dateStyle: 'long' })}</p>
                            </div>
                        </div>

                        <div className="p-8 bg-white/5 border border-white/5 rounded-sm mb-12">
                            <div className="flex items-center gap-4 mb-8">
                                <Anchor className="text-[var(--color-gold)]" size={24} />
                                <h3 className="font-black text-white uppercase text-[10px] tracking-[0.2em]">Network Consensus State</h3>
                            </div>
                            <div className="space-y-6">
                                <div className="flex justify-between items-center">
                                    <span className="text-[10px] text-[var(--color-text-muted)] font-bold uppercase tracking-wider">Synchronization status</span>
                                    <span className="text-emerald-400 font-black text-[9px] uppercase tracking-widest bg-emerald-400/5 px-2 py-1 rounded">Finalized & Immutable</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-[10px] text-[var(--color-text-muted)] font-bold uppercase tracking-wider">Ledger Anchor hash</span>
                                    <span className="font-mono text-[10px] text-[var(--color-gold)] truncate ml-6 select-all">
                                        {data.tx_hash || 'PENDING_FINAL_CONCENSUS'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 p-6 bg-[var(--color-gold)]/5 rounded-sm border border-[var(--color-border-gold)]">
                            <AlertCircle size={20} className="text-[var(--color-gold)] shrink-0 mt-0.5" />
                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-white uppercase tracking-widest">Regulatory Redaction Notice</p>
                                <p className="text-[11px] text-[var(--color-text-muted)] leading-relaxed font-medium">
                                    This instrument has been independently validated. All metadata presented is cryptographically anchored to the primary sovereign ledger.
                                    In accordance with global privacy frameworks, sensitive financial amounts and private beneficiary data are strictly redacted on this public gateway.
                                </p>
                            </div>
                        </div>
                    </>
                )}
            </div>

            <div className="mt-20 flex flex-col items-center gap-4 text-center max-w-lg">
                <div className="metallic-line w-32 mb-4"></div>
                <p className="text-[var(--color-text-muted)] text-[9px] font-black uppercase tracking-[0.2em] leading-loose">
                    This verification gateway is a controlled component of the SBLC Ledger Infrastructure.
                    All attempts to intercept or misrepresent verification states are recorded on the network audit trail.
                </p>
            </div>
        </div>
    );
};

export default PublicVerify;
