import React, { useState, useEffect } from 'react';
import { Newspaper, ShieldCheck, Activity, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ledgerService, sblcService } from '../services/api';
import { useTranslation } from 'react-i18next';

const Dashboard = ({ user }) => {
    const { t } = useTranslation();
    const [stats, setStats] = useState({ ledgers: 0, sblcs: 0, active: 0 });
    const [recentSblcs, setRecentSblcs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const ledgersRes = await ledgerService.list();
                const allLedgers = ledgersRes.data;

                let allSblcs = [];
                for (const l of allLedgers) {
                    const sRes = await sblcService.list(l.id);
                    allSblcs = [...allSblcs, ...sRes.data];
                }

                setStats({
                    ledgers: allLedgers.length,
                    sblcs: allSblcs.length,
                    active: allSblcs.filter(s => s.status === 'issued').length
                });

                setRecentSblcs(allSblcs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5));
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Syncing Network Overview...</div>;

    return (
        <div className="animate-institutional">
            <div className="mb-14">
                <h1 className="text-5xl font-bold text-white tracking-tighter mb-3">{t('dashboard')}</h1>
                <p className="text-[var(--color-text-muted)] font-bold uppercase tracking-[0.25em] text-[10px] flex items-center gap-2">
                    <div className="w-8 h-[1px] bg-[var(--color-gold)]"></div>
                    Global Trade Corridor • Real-time Monitoring
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-8 rounded-sm">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <p className="text-[10px] font-black text-[#505050] uppercase tracking-widest mb-2">{t('ledgers')}</p>
                            <p className="text-4xl font-bold text-white tracking-tighter">{stats.ledgers}</p>
                        </div>
                        <div className="p-3 border border-[#1a1a1a] rounded-sm bg-[#000000]">
                            <Newspaper className="text-white" size={24} />
                        </div>
                    </div>
                    <div className="h-[1px] w-full bg-[#111111] mb-5"></div>
                    <p className="text-[9px] text-[#ffffff] font-bold uppercase tracking-[0.2em] flex items-center gap-2">
                        <Activity size={10} className="text-[#d4af37]" />
                        Active Propagation
                    </p>
                </div>

                <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-8 rounded-sm">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <p className="text-[10px] font-black text-[#505050] uppercase tracking-widest mb-2">Active Instruments</p>
                            <p className="text-4xl font-bold text-white tracking-tighter">{stats.active}</p>
                        </div>
                        <div className="p-3 border border-[#332b14] rounded-sm bg-[#1a160d]">
                            <ShieldCheck className="text-[#d4af37]" size={24} />
                        </div>
                    </div>
                    <div className="h-[1px] w-full bg-[#111111] mb-5"></div>
                    <p className="text-[9px] text-[#a0a0a0] font-black uppercase tracking-[0.2em]">Total Issued: {stats.sblcs}</p>
                </div>

                <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-8 rounded-sm">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <p className="text-[10px] font-black text-[#505050] uppercase tracking-widest mb-2">Network Volume</p>
                            <p className="text-4xl font-bold text-white tracking-tighter">4.2M</p>
                        </div>
                        <div className="p-3 border border-[#1a1a1a] rounded-sm bg-[#000000]">
                            <Activity className="text-white" size={24} />
                        </div>
                    </div>
                    <div className="h-[1px] w-full bg-[#111111] mb-5"></div>
                    <div className="flex items-center gap-2">
                        <div className="px-2 py-0.5 border border-[#d4af37] text-[#d4af37] text-[8px] font-black uppercase tracking-widest bg-[#1a160d]">USD EQUIVALENT</div>
                        <span className="text-[9px] text-white font-bold tracking-widest">+12% vs LY</span>
                    </div>
                </div>
            </div>

            <div className="mt-20 grid grid-cols-1 lg:grid-cols-3 gap-12">
                <div className="lg:col-span-2 space-y-8">
                    <div className="flex justify-between items-center px-2">
                        <h2 className="text-xl font-bold text-white tracking-tight">Recent Custody Logs</h2>
                        <Link to="/ledgers" className="text-[#d4af37] text-[10px] font-black uppercase tracking-widest flex items-center gap-2 hover:underline">
                            Full Registry <ArrowRight size={12} />
                        </Link>
                    </div>

                    <div className="bg-[#0a0a0a] border border-[#1a1a1a] overflow-hidden rounded-sm">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-[#111111]">
                                    <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-widest text-[#505050]">Instrument ID</th>
                                    <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-widest text-[#505050]">Ccy / Amount</th>
                                    <th className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-widest text-[#505050]">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentSblcs.map(s => (
                                    <tr key={s.id} className="border-b border-[#111111] hover:bg-[#000000] cursor-pointer transition-colors group"
                                        onClick={() => window.location.href = `/ledgers/${s.ledger_id}/sblcs/${s.id}`}>
                                        <td className="px-6 py-5 font-mono text-[11px] font-bold text-white tracking-wider">{s.reference_number}</td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-3">
                                                <span className="text-[9px] font-black text-[#d4af37] uppercase tracking-widest">{s.currency}</span>
                                                <span className="font-bold text-white text-sm">{parseFloat(s.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-sm text-[9px] font-black uppercase tracking-widest ${s.status === 'issued' ? 'bg-[#1a160d] border border-[#332b14] text-[#d4af37]' : 'bg-[#111111] border border-[#1a1a1a] text-[#a0a0a0]'}`}>
                                                {s.status === 'issued' && <ShieldCheck size={10} />}
                                                {s.status.replace('_', ' ')}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="space-y-8">
                    <h2 className="text-xl font-bold text-white px-2 tracking-tight">Identity Anchor</h2>
                    <div className="glass p-8 rounded space-y-8 relative overflow-hidden border border-[#1a1a1a]">
                        <div className="absolute top-0 right-0 p-8 hidden pointer-events-none">
                            <ShieldCheck size={160} className="text-white" />
                        </div>

                        <div className="flex items-center gap-6">
                            <div className="p-4 border border-[#1a1a1a] bg-[#0a0a0a] rounded">
                                <ShieldCheck className="text-[#d4af37]" size={32} />
                            </div>
                            <div>
                                <p className="text-[9px] text-[var(--color-text-muted)] font-black uppercase tracking-widest mb-1">Authenticated Entity</p>
                                <p className="font-bold text-white text-lg">Global Trade Bank</p>
                            </div>
                        </div>

                        <div className="space-y-6 pt-6 border-t border-[#1a1a1a]">
                            <div className="flex justify-between items-center">
                                <span className="text-[10px] text-[var(--color-text-muted)] font-bold uppercase tracking-wider">Node Signature</span>
                                <span className="font-mono text-[10px] text-white bg-[#0a0a0a] border border-[#1a1a1a] px-2 py-1 rounded">GTB-E2-X04</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-[10px] text-[var(--color-text-muted)] font-bold uppercase tracking-wider">Operational Tier</span>
                                <span className="text-[#d4af37] font-black text-[10px] uppercase tracking-[0.1em]">Primary Sovereign Issuer</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-[10px] text-[var(--color-text-muted)] font-bold uppercase tracking-wider">Security State</span>
                                <span className="text-white font-bold text-[10px] uppercase tracking-widest">Validated Entry V3</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
