import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
    X, Send, Loader2, FilePlus, ChevronRight, CheckCircle2,
    FileText, Shield, FileCheck, ExternalLink, BadgeCheck,
    Clock, Download, Anchor, ShieldAlert
} from 'lucide-react';
import { sblcService, authService } from '../services/api';
import { toast } from '../components/Toast';
import RoleGuard from '../components/RoleGuard';
import { useTranslation } from 'react-i18next';

const SBLCDetail = () => {
    const { t } = useTranslation();
    const { ledgerId, sblcId } = useParams();
    const [sblc, setSblc] = useState(null);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showAmend, setShowAmend] = useState(false);
    const [amendDesc, setAmendDesc] = useState('');
    const docInputRef = React.useRef(null);

    useEffect(() => {
        const load = async () => {
            try {
                const [sRes, uRes] = await Promise.all([
                    sblcService.get(ledgerId, sblcId),
                    authService.getMe()
                ]);
                setSblc(sRes.data);
                setUser(uRes.data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [ledgerId, sblcId]);

    const handleAction = async (action) => {
        setIsSubmitting(true);
        try {
            if (action === 'submit') {
                await sblcService.submit(ledgerId, sblcId);
                toast('Instrument submitted for review', 'success');
            }
            if (action === 'request_review') {
                await sblcService.requestReview(ledgerId, sblcId);
                toast('Review sequence initiated', 'info');
            }
            if (action === 'approve') {
                await sblcService.approve(ledgerId, sblcId);
                toast('Instrument signed and approved', 'success');
            }
            if (action === 'issue') {
                await sblcService.issue(ledgerId, sblcId);
                toast('Instrument issued and anchored to blockchain', 'success');
            }

            const res = await sblcService.get(ledgerId, sblcId);
            setSblc(res.data);
        } catch (e) {
            toast(e.response?.data?.detail || 'Action failed', 'error');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleAmend = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            await sblcService.amend(ledgerId, sblcId, {
                change_description: amendDesc,
                new_values: {}
            });
            toast('Amendment request recorded', 'info');
            setShowAmend(false);
            setAmendDesc('');
        } catch (e) {
            toast('Amendment failed', 'error');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsSubmitting(true);
        try {
            // Simulated institutional hashing
            const mockHash = `sha256:${Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('')}`;
            await sblcService.uploadAttachment(ledgerId, sblcId, {
                filename: file.name,
                file_type: file.type || 'application/pdf',
                file_hash: mockHash,
                visibility: 'internal'
            });
            toast('Document reference anchored and hashed', 'success');
            const res = await sblcService.get(ledgerId, sblcId);
            setSblc(res.data);
        } catch (e) {
            toast('Upload failed', 'error');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Syncing Instrument Ledger...</div>;

    const steps = [
        { id: 'draft', label: 'Draft' },
        { id: 'submitted', label: 'Submitted' },
        { id: 'under_review', label: 'Review' },
        { id: 'approved', label: 'Approved' },
        { id: 'issued', label: 'Issued' }
    ];

    const currentStepIndex = steps.findIndex(s => s.id === sblc.status);
    const isFinalized = sblc.status === 'issued' || sblc.status === 'closed';

    return (
        <div className="animate-institutional">
            <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-[var(--color-text-muted)] mb-10">
                <Link to="/ledgers" className="hover:text-[var(--color-gold)] transition-colors">Registry</Link>
                <ChevronRight size={12} />
                <Link to={`/ledgers/${ledgerId}`} className="hover:text-[var(--color-gold)] transition-colors">Corridor</Link>
                <ChevronRight size={12} />
                <span className="text-white">{sblc.reference_number}</span>
            </div>

            {/* Lifecycle Timeline */}
            <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded mb-16 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-[#d4af37] opacity-20"></div>

                <div className="flex justify-between items-center min-w-[600px] relative">
                    <div className="absolute top-[20px] left-[50px] right-[50px] h-[1px] bg-[#1a1a1a]"></div>
                    <div
                        className="absolute top-[20px] left-[50px] h-[1px] bg-[#d4af37] transition-all duration-1000 ease-in-out"
                        style={{ width: `${Math.max(0, (currentStepIndex / (steps.length - 1)) * 100 - 15)}%` }}
                    ></div>

                    {steps.map((step, idx) => {
                        const isActive = idx <= currentStepIndex;
                        const isCurrent = idx === currentStepIndex;
                        return (
                            <div key={step.id} className="relative z-10 flex flex-col items-center gap-4">
                                <div className={`w-10 h-10 rounded bg-[#000000] flex items-center justify-center border transition-all duration-700 ${isActive ? 'border-[#d4af37]' : 'border-[#1a1a1a]'
                                    }`}>
                                    {isActive && !isCurrent ? <CheckCircle2 size={16} className="text-[#d4af37]" /> :
                                        <div className={`w-1 h-1 rounded-full ${isActive ? 'bg-[#d4af37]' : 'bg-[#333333]'}`}></div>}
                                </div>
                                <span className={`text-[10px] font-black uppercase tracking-[0.2em] ${isActive ? 'text-[var(--color-gold)]' : 'text-[var(--color-text-muted)]'}`}>
                                    {step.label}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="flex justify-between items-start mb-16">
                <div className="flex items-center gap-8">
                    <div className="p-5 border border-[#d4af37] bg-[#1a160d] rounded">
                        <FileText className="text-[#d4af37]" size={36} />
                    </div>
                    <div>
                        <div className="flex items-center gap-4 mb-2">
                            <h1 className="text-4xl font-bold text-white tracking-tighter uppercase font-mono">{sblc.reference_number}</h1>
                            <div className={`badge ${sblc.status === 'issued' ? 'badge-gold' : 'badge-silver'}`}>
                                {sblc.status.replace('_', ' ')}
                            </div>
                        </div>
                        <p className="text-[10px] text-[var(--color-text-muted)] font-bold uppercase tracking-widest flex items-center gap-2">
                            <Shield size={10} className="text-[var(--color-gold)]" />
                            Immutable Registry ID: {sblc.id}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <Link
                        to={`/verify/${sblc.reference_number}`}
                        className="btn-secondary"
                    >
                        <div className="flex items-center gap-2">
                            <Shield size={16} />
                            <span>Public Verification</span>
                        </div>
                    </Link>

                    <RoleGuard roles={['IssuerOps', 'IssuerAdmin']} user={user}>
                        {sblc.status === 'draft' && (
                            <button
                                onClick={() => handleAction('submit')}
                                disabled={isSubmitting}
                                className="btn-primary"
                            >
                                Submit for Issuance
                            </button>
                        )}
                    </RoleGuard>

                    <RoleGuard roles={['IssuerOps', 'IssuerAdmin']} user={user}>
                        {sblc.status === 'submitted' && (
                            <button
                                onClick={() => handleAction('request_review')}
                                disabled={isSubmitting}
                                className="btn-primary flex items-center gap-2"
                            >
                                <FileCheck size={18} />
                                Initiate review
                            </button>
                        )}
                    </RoleGuard>

                    <RoleGuard roles={['IssuerSigner', 'IssuerAdmin']} user={user}>
                        {sblc.status === 'under_review' && (
                            <button
                                className="btn-primary"
                                onClick={() => handleAction('approve')}
                                disabled={isSubmitting}
                            >
                                Sign & Approve
                            </button>
                        )}
                    </RoleGuard>

                    <RoleGuard roles={['IssuerSigner', 'IssuerAdmin']} user={user}>
                        {sblc.status === 'approved' && (
                            <button
                                className="btn-primary"
                                onClick={() => handleAction('issue')}
                                disabled={isSubmitting}
                            >
                                Finalize & Anchor
                            </button>
                        )}
                    </RoleGuard>

                    <RoleGuard roles={['IssuerOps', 'IssuerAdmin']} user={user}>
                        {isFinalized && (
                            <button
                                onClick={() => setShowAmend(true)}
                                className="btn-secondary"
                            >
                                <div className="flex items-center gap-2">
                                    <ExternalLink size={18} />
                                    <span>Propose Amendment</span>
                                </div>
                            </button>
                        )}
                    </RoleGuard>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-16">
                <div className="lg:col-span-2 space-y-16">
                    <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-10 hidden pointer-events-none">
                            <Shield size={200} className="text-white" />
                        </div>

                        <div className="flex items-center gap-3 mb-10 pb-6 border-b border-[#1a1a1a]">
                            <BadgeCheck className="text-[#d4af37]" size={24} />
                            <h2 className="text-xs font-black text-[#a0a0a0] uppercase tracking-[0.3em]">Institutional instrument profile</h2>
                        </div>

                        <div className="grid grid-cols-2 gap-y-12 gap-x-16">
                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-widest">Face Value (Equivalent)</p>
                                <p className="text-4xl font-bold text-white tracking-tighter uppercase">{sblc.currency} {parseFloat(sblc.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                            </div>
                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-widest">Maturity Protocol</p>
                                <p className="text-2xl font-bold text-[var(--color-silver)] uppercase">{new Date(sblc.expiry_date).toLocaleDateString(undefined, { dateStyle: 'long' })}</p>
                            </div>
                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-widest">Governing Jurisdiction</p>
                                <p className="text-lg font-bold text-white border-l-2 border-[var(--color-gold)] pl-4">{sblc.governing_law || 'English Common Law'}</p>
                            </div>
                            <div className="space-y-2">
                                <p className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-widest">Applicable Ruleset</p>
                                <p className="text-lg font-bold text-white border-l-2 border-[var(--color-silver)] pl-4">{sblc.applicable_rules || 'UCP 600 / ISP 98'}</p>
                            </div>

                            <div className="col-span-2 mt-8 space-y-6">
                                <div className="flex items-center gap-2">
                                    <div className="w-8 h-[1px] bg-[var(--color-border-silver)]"></div>
                                    <p className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-widest">Participant Hierarchy</p>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="p-6 border border-[#1a1a1a] bg-[#000000] rounded-sm hover:bg-[#1a1a1a] transition-colors group">
                                        <p className="text-[9px] text-[#d4af37] font-black uppercase tracking-widest mb-3">Applicant (Primary Obligor)</p>
                                        <p className="text-lg font-bold text-white mb-1">Industrial Imports Ltd</p>
                                        <p className="text-[10px] text-[#a0a0a0] font-mono tracking-tighter">LEI: 254900X7RHV9PD93...</p>
                                    </div>
                                    <div className="p-6 border border-[#d4af37] bg-[#1a160d] rounded-sm hover:bg-[#201c12] transition-colors group">
                                        <p className="text-[9px] text-[#d4af37] font-black uppercase tracking-widest mb-3">Beneficiary (Payee Entity)</p>
                                        <p className="text-lg font-bold text-white mb-1">Textile Exports Inc</p>
                                        <div className="flex items-center gap-1.5 text-[9px] text-[#ffffff] font-bold uppercase tracking-widest">
                                            <CheckCircle2 size={10} className="text-[#d4af37]" /> Verified Record
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Support Documents */}
                    <section className="space-y-6">
                        <div className="flex items-center justify-between px-2">
                            <h3 className="text-xl font-bold text-white flex items-center gap-3">
                                <FileCheck size={24} className="text-[var(--color-gold)]" />
                                {t('institutional_hierarchy')}
                            </h3>
                            <RoleGuard roles={['IssuerOps', 'IssuerAdmin']} user={user}>
                                <button
                                    onClick={() => docInputRef.current?.click()}
                                    disabled={isSubmitting}
                                    className="text-[10px] font-black text-[var(--color-gold)] uppercase tracking-[0.2em] hover:underline flex items-center gap-2"
                                >
                                    <FilePlus size={16} /> Attach Primary Reference
                                </button>
                                <input
                                    type="file"
                                    ref={docInputRef}
                                    className="hidden"
                                    onChange={handleFileUpload}
                                    accept=".pdf,.doc,.docx,.jpg,.png"
                                />
                            </RoleGuard>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {(sblc.attachments || []).map((doc) => (
                                <div key={doc.id} className="bg-[#0a0a0a] border border-[#1a1a1a] p-6 rounded-sm space-y-4 group">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className="p-3 border border-[#1a1a1a] bg-[#000000] rounded text-white font-mono text-[10px] font-black uppercase">
                                                {doc.file_type?.split('/')[1] || 'PDF'}
                                            </div>
                                            <div>
                                                <p className="font-bold text-white text-sm tracking-tight">{doc.filename}</p>
                                                <p className="text-[9px] text-[#a0a0a0] font-bold uppercase tracking-widest">{new Date(doc.created_at).toLocaleDateString()} • {doc.visibility}</p>
                                            </div>
                                        </div>
                                        <button className="p-2 text-[#d4af37] hover:bg-[#1a160d] rounded transition-colors" title="Download Official Copy">
                                            <Download size={20} />
                                        </button>
                                    </div>
                                    <div className="p-3 bg-[#000000] rounded border border-[#1a1a1a] flex items-center gap-3">
                                        <Shield size={12} className="text-[#d4af37] shrink-0" />
                                        <span className="font-mono text-[9px] text-[#a0a0a0] truncate select-all">{doc.file_hash}</span>
                                    </div>
                                </div>
                            ))}
                            {(sblc.attachments || []).length === 0 && (
                                <div className="col-span-2 py-16 text-center glass rounded border-dashed border-2 border-white/5">
                                    <p className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-widest italic opacity-50">No primary documents anchored.</p>
                                </div>
                            )}
                        </div>
                    </section>

                    <div className="glass-gold p-10 rounded relative overflow-hidden">
                        <div className="flex items-center gap-4 mb-8">
                            <Anchor className="text-[var(--color-gold)]" size={28} />
                            <h2 className="text-xl font-bold text-white tracking-tight italic">Network Trust Anchor (Immutable Proof)</h2>
                        </div>

                        {sblc.onchain_status === 'anchored' ? (
                            <div className="space-y-6">
                                <div className="flex items-center gap-4 bg-emerald-500/5 p-6 rounded border border-emerald-500/20">
                                    <div className="p-3 bg-emerald-500/20 rounded-full text-emerald-400">
                                        <CheckCircle2 size={24} />
                                    </div>
                                    <div>
                                        <p className="font-bold text-white text-base">Node Validation Finalized</p>
                                        <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">This instrument has been anchored to the decentralized infrastructure. Every state transition is immutable and audited across the participant hierarchy.</p>
                                    </div>
                                </div>
                                <div className="flex justify-between items-center py-4 px-6 bg-black/40 rounded border border-white/5">
                                    <span className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-widest">Ledger Transaction Hash</span>
                                    <span className="font-mono text-[10px] text-[var(--color-gold)] flex items-center gap-2 hover:underline cursor-pointer bg-[var(--color-gold)]/5 px-3 py-1.5 rounded">
                                        {sblc.tx_hash}
                                        <ExternalLink size={12} />
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center text-center py-10">
                                <Clock className="text-white/10 mb-6" size={60} />
                                <h4 className="text-[var(--color-silver)] font-bold text-lg mb-3">Awaiting Ledger Concensus</h4>
                                <p className="text-xs text-[var(--color-text-muted)] leading-relaxed max-w-sm font-medium">
                                    Processing cryptographical consensus for the '{sblc.status.toUpperCase()}' state. Full anchor proof will populate upon 'ISSUED' confirmation.
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="space-y-12">
                    <section>
                        <div className="flex items-center justify-between mb-8 px-2">
                            <h2 className="text-lg font-bold text-white flex items-center gap-3">
                                <Clock size={20} className="text-[var(--color-gold)]" />
                                Audit Sequence
                            </h2>
                            <button className="text-[9px] text-[var(--color-gold)] font-black uppercase tracking-widest hover:underline">Download full log</button>
                        </div>

                        <div className="space-y-10 relative ml-6 before:content-[''] before:absolute before:left-[-1px] before:top-2 before:bottom-2 before:w-[1px] before:bg-white/5">
                            <div className="relative pl-10 animate-fade">
                                <div className="absolute left-[-5px] top-1.5 w-[10px] h-[10px] rounded-sm bg-[var(--color-gold)] ring-4 ring-[var(--color-gold)]/10"></div>
                                <p className="text-[9px] text-[var(--color-text-muted)] font-black uppercase mb-2 tracking-widest font-mono">{new Date(sblc.updated_at).toLocaleString()}</p>
                                <p className="font-bold text-white text-sm tracking-tight">{sblc.status.toUpperCase()} – STATE ANCHORED</p>
                                <div className="mt-2 p-3 bg-white/5 rounded-sm border border-white/5 text-[10px] text-[var(--color-text-muted)] italic leading-relaxed">
                                    Transition protocols validated by network nodes. Zero discrepancy detected.
                                </div>
                            </div>

                            <div className="relative pl-10 opacity-30">
                                <div className="absolute left-[-5px] top-1.5 w-[10px] h-[10px] rounded-sm bg-white/20"></div>
                                <p className="text-[9px] text-[var(--color-text-muted)] font-black uppercase mb-2 tracking-widest font-mono">{new Date(sblc.created_at).toLocaleString()}</p>
                                <p className="font-bold text-white text-sm">INSTRUMENT INITIALIZED</p>
                            </div>
                        </div>
                    </section>

                    {/* Compliance Matrix */}
                    <section className="glass p-10 rounded border-l-2 border-l-[var(--color-gold)]">
                        <div className="flex items-center gap-4 mb-10">
                            <ShieldAlert className="text-[var(--color-gold)]" size={24} />
                            <h3 className="text-[10px] font-black text-white uppercase tracking-[0.25em]">Compliance Matrix</h3>
                        </div>

                        <div className="space-y-8">
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-widest font-mono">KYC / AML Review</span>
                                    <span className={`text-[9px] font-black uppercase tracking-widest ${sblc.status !== 'draft' ? 'text-emerald-400' : 'text-white/20'}`}>
                                        {sblc.status !== 'draft' ? 'Secured' : 'Awaiting'}
                                    </span>
                                </div>
                                <div className="w-full h-0.5 bg-white/5 rounded-full overflow-hidden">
                                    <div className={`h-full bg-[var(--color-gold)] transition-all duration-1000 ${sblc.status !== 'draft' ? 'w-full' : 'w-0'}`}></div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-widest font-mono">Institutional Sign-off</span>
                                    <span className={`text-[9px] font-black uppercase tracking-widest ${isFinalized ? 'text-emerald-400' : 'text-white/20'}`}>
                                        {isFinalized ? 'Multi-sig complete' : 'In process'}
                                    </span>
                                </div>
                                <div className="w-full h-0.5 bg-white/5 rounded-full overflow-hidden">
                                    <div className={`h-full bg-[var(--color-silver)] transition-all duration-1000 ${isFinalized ? 'w-full' : 'w-0'}`}></div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-10 pt-8 border-t border-white/5">
                            <p className="text-[9px] text-[var(--color-text-muted)] italic leading-relaxed text-center font-medium">
                                Protocol Enforcement: Level 4 Multi-signature requirements are active for this treasury corridor.
                            </p>
                        </div>
                    </section>
                </div>
            </div>

            {/* Amendment Modal */}
            {showAmend && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
                    <div className="absolute inset-0 bg-[#000]/90 backdrop-blur-md" onClick={() => setShowAmend(false)}></div>
                    <div className="glass w-full max-w-xl p-10 rounded shadow-[0_0_100px_rgba(0,0,0,0.5)] relative z-10 animate-institutional border border-white/5">
                        <button onClick={() => setShowAmend(false)} className="absolute top-8 right-8 text-[var(--color-text-muted)] hover:text-white transition-colors">
                            <X size={28} />
                        </button>
                        <div className="mb-10">
                            <h2 className="text-3xl font-bold text-white mb-3 tracking-tight">Propose Amendment</h2>
                            <p className="text-[var(--color-text-muted)] text-xs font-medium leading-relaxed">Modify the execution terms of this treasury instrument. These changes will undergo formal institutional review sequences before final anchoring.</p>
                        </div>
                        <form onSubmit={handleAmend} className="space-y-8">
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em]">Change Specification</label>
                                <textarea
                                    required
                                    rows={5}
                                    className="w-full bg-white/5 border border-white/10 rounded-sm py-4 px-5 text-white focus:outline-none focus:border-[var(--color-gold)] transition-all font-bold text-sm resize-none"
                                    placeholder="Specify maturity extensions or volume adjustments..."
                                    value={amendDesc}
                                    onChange={(e) => setAmendDesc(e.target.value)}
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="w-full btn-primary h-14 flex items-center justify-center gap-4"
                            >
                                {isSubmitting ? <Loader2 className="animate-spin" size={24} /> : <><Send size={20} /> Submit for Review</>}
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SBLCDetail;
