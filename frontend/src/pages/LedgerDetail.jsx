import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronRight, Globe, UserPlus, FilePlus, Activity, Loader2, CheckCircle2, X } from 'lucide-react';
import { ledgerService, sblcService, adminService } from '../services/api';
import RoleGuard from '../components/RoleGuard';
import { useTranslation } from 'react-i18next';

const LedgerDetail = () => {
    const { t } = useTranslation();
    const { ledgerId } = useParams();
    const [ledger, setLedger] = useState(null);
    const [sblcs, setSblcs] = useState([]);
    const [loading, setLoading] = useState(true);

    // Modals & Forms
    const [showDraft, setShowDraft] = useState(false);
    const [draftData, setDraftData] = useState({
        amount: 1000000,
        currency: 'USD',
        expiry_date: new Date(Date.now() + 90 * 86400000).toISOString().split('T')[0],
        governing_law: 'English Common Law',
        applicable_rules: 'UCP 600'
    });
    const [drafting, setDrafting] = useState(false);

    const [showInvite, setShowInvite] = useState(false);
    const [inviteEmail, setInviteEmail] = useState('');
    const [inviteRole, setInviteRole] = useState('IssuerOps');
    const [inviteResult, setInviteResult] = useState(null);
    const [inviting, setInviting] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const [lRes, sRes] = await Promise.all([
                    ledgerService.get(ledgerId),
                    sblcService.list(ledgerId)
                ]);
                setLedger(lRes.data);
                setSblcs(sRes.data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [ledgerId]);

    const handleInvite = async (e) => {
        e.preventDefault();
        setInviting(true);
        try {
            const res = await adminService.invite({
                email: inviteEmail,
                role_name: inviteRole,
                ledger_id: ledgerId
            });
            setInviteResult(res.data);
        } catch (err) {
            alert('Failed to send invite');
        } finally {
            setInviting(false);
        }
    };

    const handleDraft = async (e) => {
        e.preventDefault();
        setDrafting(true);
        try {
            const res = await sblcService.create(ledgerId, draftData);
            setSblcs([...sblcs, res.data]);
            setShowDraft(false);
            alert('SBLC Draft Created Successfully');
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to create draft');
        } finally {
            setDrafting(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Syncing Corridor Registry...</div>;

    const user = JSON.parse(localStorage.getItem('user'));

    return (
        <div className="animate-institutional">
            <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-[var(--color-text-muted)] mb-10">
                <Link to="/ledgers" className="hover:text-[var(--color-gold)] transition-colors">Registry</Link>
                <ChevronRight size={12} />
                <span className="text-white">{ledger.name}</span>
            </div>

            <div className="flex justify-between items-end mb-16">
                <div className="flex items-center gap-10">
                    <div className="p-5 border border-[#1a1a1a] bg-[#0a0a0a] rounded">
                        <Globe className="text-white" size={32} />
                    </div>
                    <div>
                        <div className="flex items-center gap-5 mb-2">
                            <h1 className="text-4xl font-bold text-white tracking-tighter">{ledger.name}</h1>
                            <div className="badge badge-gold">Sovereign Active</div>
                        </div>
                        <p className="text-[11px] text-[#a0a0a0] font-medium max-w-2xl leading-relaxed italic">{ledger.description}</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <RoleGuard roles={['IssuerAdmin']} user={user}>
                        <button
                            onClick={() => setShowInvite(true)}
                            className="btn-secondary flex items-center gap-3"
                        >
                            <UserPlus size={18} />
                            <span>Invite Personnel</span>
                        </button>
                    </RoleGuard>

                    <RoleGuard roles={['IssuerOps', 'IssuerAdmin']} user={user}>
                        <button
                            onClick={() => setShowDraft(true)}
                            className="btn-primary flex items-center gap-3"
                        >
                            <FilePlus size={18} />
                            <span>Draft Instrument</span>
                        </button>
                    </RoleGuard>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
                <div className="lg:col-span-3 space-y-12">
                    <section className="space-y-6">
                        <div className="flex justify-between items-center px-2">
                            <h2 className="text-xl font-bold text-white flex items-center gap-4">
                                <Activity size={20} className="text-[var(--color-gold)]" />
                                <span>Active Instrument Pipeline</span>
                            </h2>
                            <div className="text-[9px] text-[var(--color-text-muted)] font-black uppercase tracking-widest">
                                Total Registry Volume: {sblcs.length}
                            </div>
                        </div>

                        <div className="bg-[#0a0a0a] border border-[#1a1a1a] overflow-hidden rounded">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Identifier</th>
                                        <th>Legal Entities</th>
                                        <th>Face Value</th>
                                        <th>Maturity</th>
                                        <th>Node State</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {sblcs.map(s => (
                                        <tr key={s.id} className="hover:bg-[#1a1a1a] cursor-pointer"
                                            onClick={() => window.location.href = `/ledgers/${ledgerId}/sblcs/${s.id}`}>
                                            <td className="font-mono text-[11px] font-bold text-white tracking-wider">{s.reference_number}</td>
                                            <td>
                                                <div className="flex flex-col gap-1">
                                                    <span className="text-[11px] font-bold text-white tracking-tight">Industrial Imports Ltd</span>
                                                    <span className="text-[9px] text-[#a0a0a0] font-black uppercase tracking-widest">Textile Exports Inc</span>
                                                </div>
                                            </td>
                                            <td><span className="text-[9px] font-black text-[var(--color-gold)] uppercase tracking-widest mr-2">{s.currency}</span> <span className="font-bold text-white text-sm">{parseFloat(s.amount).toLocaleString()}</span></td>
                                            <td className="text-[11px] font-bold text-[var(--color-silver)]">{new Date(s.expiry_date).toLocaleDateString()}</td>
                                            <td>
                                                <div className={`badge ${s.status === 'issued' ? 'badge-gold' : 'badge-silver'}`}>
                                                    {s.status.replace('_', ' ')}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                    {sblcs.length === 0 && (
                                        <tr>
                                            <td colSpan="5" className="text-center py-20 text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-widest italic opacity-50">No active instruments detected in this registry corridor.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </section>
                </div>

                <div className="space-y-10">
                    <section className="space-y-6">
                        <h2 className="text-lg font-bold text-white flex items-center gap-4 px-2 tracking-tight">
                            <Users size={20} className="text-[var(--color-gold)]" />
                            <span>Key Stakeholders</span>
                        </h2>

                        <div className="space-y-4">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="bg-[#0a0a0a] border border-[#1a1a1a] p-5 rounded-sm flex items-center gap-4 group hover:bg-[#1a1a1a] transition-colors border-l-2 border-l-[#ffffff]">
                                    <div className="w-10 h-10 rounded border border-[#1a1a1a] bg-[#000000] flex items-center justify-center font-bold text-[#d4af37] group-hover:border-[#d4af37]">
                                        {i === 1 ? 'GT' : i === 2 ? 'ST' : 'IN'}
                                    </div>
                                    <div>
                                        <p className="text-xs font-bold text-white tracking-tight">
                                            {i === 1 ? 'Global Trade Bank' : i === 2 ? 'Standard Advise' : 'Industrial Imports'}
                                        </p>
                                        <p className="text-[9px] text-[#a0a0a0] font-black uppercase tracking-[0.15em] mt-1">
                                            {i === 1 ? 'Primary Issuer' : i === 2 ? 'Advising Node' : 'Applicant Entity'}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-8 rounded border-t-2 border-t-emerald-500 relative overflow-hidden">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            <p className="text-[10px] font-black text-white uppercase tracking-widest">Network Consensus</p>
                        </div>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-[10px] text-[#a0a0a0] font-bold uppercase">Node Integrity</span>
                                <span className="text-[9px] font-black text-emerald-400 uppercase tracking-widest">Optimal</span>
                            </div>
                            <div className="w-full bg-[#333333] h-0.5 rounded-full overflow-hidden">
                                <div className="bg-emerald-500 h-full w-[100%]"></div>
                            </div>
                        </div>
                        <p className="mt-6 text-[9px] text-[#a0a0a0] leading-relaxed italic border-t border-[#1a1a1a] pt-4">This corridor is currently synchronized across all primary nodes.</p>
                    </div>
                </div>
            </div>

            {/* Modals remain similarly styled but with institutional tokens */}
            {showDraft && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
                    <div className="absolute inset-0 bg-[#000000] opacity-95" onClick={() => setShowDraft(false)}></div>
                    <div className="bg-[#0a0a0a] border border-[#1a1a1a] w-full max-w-xl p-12 rounded relative z-10 animate-institutional">
                        <button onClick={() => setShowDraft(false)} className="absolute top-8 right-8 text-[#a0a0a0] hover:text-white transition-colors">
                            <X size={28} />
                        </button>
                        <div className="mb-10 text-center">
                            <h2 className="text-3xl font-bold text-white mb-3 tracking-tighter uppercase">Initialize Instrument</h2>
                            <p className="text-[var(--color-text-muted)] text-[11px] font-black uppercase tracking-widest">Mission-Critical Registry Draft</p>
                        </div>
                        <form onSubmit={handleDraft} className="space-y-8">
                            <div className="grid grid-cols-2 gap-8">
                                <div className="space-y-3">
                                    <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em]">Denomination</label>
                                    <select
                                        className="w-full bg-[#000000] border border-[#1a1a1a] rounded-sm py-4 px-5 text-white focus:outline-none focus:border-[#d4af37] transition-all font-bold text-sm h-14"
                                        value={draftData.currency}
                                        onChange={(e) => setDraftData({ ...draftData, currency: e.target.value })}
                                    >
                                        <option value="USD">USD</option>
                                        <option value="EUR">EUR</option>
                                        <option value="GBP">GBP</option>
                                    </select>
                                </div>
                                <div className="space-y-3">
                                    <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em]">Face Value</label>
                                    <input
                                        type="number"
                                        required
                                        className="w-full bg-white/5 border border-white/10 rounded-sm py-4 px-5 text-white focus:outline-none focus:border-[var(--color-gold)] transition-all font-bold text-sm h-14"
                                        value={draftData.amount}
                                        onChange={(e) => setDraftData({ ...draftData, amount: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em]">Execution Date</label>
                                <input
                                    type="date"
                                    required
                                    className="w-full bg-white/5 border border-white/10 rounded-sm py-4 px-5 text-white focus:outline-none focus:border-[var(--color-gold)] transition-all font-bold text-sm h-14"
                                    value={draftData.expiry_date}
                                    onChange={(e) => setDraftData({ ...draftData, expiry_date: e.target.value })}
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={drafting}
                                className="w-full btn-primary h-16 flex items-center justify-center gap-4 text-base"
                            >
                                {drafting ? <Loader2 className="animate-spin" size={24} /> : <span>Establish Instrument Record</span>}
                            </button>
                        </form>
                    </div>
                </div>
            )}

            {/* Invite Modal styled similarly */}
            {showInvite && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
                    <div className="absolute inset-0 bg-black/90 backdrop-blur-md" onClick={() => setShowInvite(false)}></div>
                    <div className="glass w-full max-w-xl p-12 rounded relative z-10 animate-institutional border border-white/5">
                        <button
                            onClick={() => { setShowInvite(false); setInviteResult(null); }}
                            className="absolute top-8 right-8 text-[var(--color-text-muted)] hover:text-white transition-colors"
                        >
                            <X size={28} />
                        </button>

                        {!inviteResult ? (
                            <>
                                <div className="mb-10 text-center">
                                    <h2 className="text-3xl font-bold text-white mb-3 tracking-tighter uppercase">Invite Stakeholder</h2>
                                    <p className="text-[var(--color-text-muted)] text-[11px] font-black uppercase tracking-widest">Authorization of Network Personnel</p>
                                </div>

                                <form onSubmit={handleInvite} className="space-y-8">
                                    <div className="space-y-3">
                                        <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em]">Institutional Email</label>
                                        <input
                                            type="email"
                                            required
                                            className="w-full bg-[#000000] border border-[#1a1a1a] rounded-sm py-4 px-5 text-white focus:outline-none focus:border-[#d4af37] transition-all font-bold text-sm h-14"
                                            placeholder="officer@sovereignbank.com"
                                            value={inviteEmail}
                                            onChange={(e) => setInviteEmail(e.target.value)}
                                        />
                                    </div>
                                    <div className="space-y-3">
                                        <label className="text-[10px] font-black text-[var(--color-text-muted)] uppercase tracking-[0.2em]">Security Tier</label>
                                        <select
                                            className="w-full bg-white/5 border border-white/10 rounded-sm py-4 px-5 text-white focus:outline-none focus:border-[var(--color-gold)] transition-all font-bold text-sm h-14"
                                            value={inviteRole}
                                            onChange={(e) => setInviteRole(e.target.value)}
                                        >
                                            <option value="IssuerOps">Issuer Operations</option>
                                            <option value="IssuerSigner">Institutional Signer</option>
                                            <option value="Auditor">Network Auditor (Audit Only)</option>
                                            <option value="IssuerAdmin">Institutional Administrator</option>
                                        </select>
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={inviting}
                                        className="w-full btn-primary h-16 flex items-center justify-center gap-4 text-base"
                                    >
                                        {inviting ? <Loader2 className="animate-spin" size={24} /> : <span>Authorize Personnel Access</span>}
                                    </button>
                                </form>
                            </>
                        ) : (
                            <div className="py-12 text-center animate-institutional">
                                <div className="w-24 h-24 border border-emerald-500/50 bg-emerald-500/5 rounded-full flex items-center justify-center mx-auto mb-8 shadow-[0_0_50px_rgba(16,185,129,0.1)]">
                                    <CheckCircle2 className="text-emerald-400" size={48} />
                                </div>
                                <h2 className="text-3xl font-bold text-white mb-3 tracking-tighter uppercase">Authorization Generated</h2>
                                <p className="text-[var(--color-text-muted)] font-black uppercase tracking-widest text-xs mb-10">Access Tier: <span className="text-[var(--color-gold)]">{inviteRole}</span></p>

                                <div className="p-8 bg-black/40 rounded border border-white/5 mb-10 text-left">
                                    <p className="text-[10px] text-[var(--color-text-muted)] font-black uppercase tracking-[0.2em] mb-4">Secure invitation signature</p>
                                    <div className="flex bg-white/5 p-4 rounded-sm border border-white/10 gap-4 items-center overflow-hidden">
                                        <input
                                            readOnly
                                            value={`${window.location.origin}${inviteResult.invite_link}`}
                                            className="flex-1 bg-transparent border-none outline-none text-[var(--color-gold)] font-mono text-[10px] truncate"
                                        />
                                        <button
                                            className="text-[var(--color-silver)] hover:text-white transition-colors"
                                            onClick={() => {
                                                navigator.clipboard.writeText(`${window.location.origin}${inviteResult.invite_link}`);
                                                alert('Invitation signature copied to clipboard');
                                            }}
                                        >
                                            <Activity size={20} />
                                        </button>
                                    </div>
                                </div>

                                <button
                                    onClick={() => { setShowInvite(false); setInviteResult(null); }}
                                    className="text-[var(--color-gold)] font-black uppercase tracking-widest text-xs hover:underline decoration-2 underline-offset-8"
                                >
                                    Return to Registry Command
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default LedgerDetail;
