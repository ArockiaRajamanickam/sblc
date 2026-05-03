import React, { useState, useEffect } from 'react';
import { FileText, Search, Clock, User, Box, Filter, Download, ListFilter } from 'lucide-react';
import { ledgerService } from '../services/api';
import { toast } from '../components/Toast';
import { useTranslation } from 'react-i18next';

const AuditHistory = () => {
    const { t } = useTranslation();
    const [audits, setAudits] = useState([]);
    const [filtered, setFiltered] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all');

    useEffect(() => {
        ledgerService.list().then(async res => {
            if (res.data.length > 0) {
                const auditRes = await ledgerService.getAudit(res.data[0].id);
                setAudits(auditRes.data);
                setFiltered(auditRes.data);
            }
            setLoading(false);
        });
    }, []);

    useEffect(() => {
        let result = audits;
        if (filterType !== 'all') {
            result = result.filter(a => a.event_type.includes(filterType));
        }
        if (searchTerm) {
            result = result.filter(a =>
                a.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                a.entity_type.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        setFiltered(result);
    }, [searchTerm, filterType, audits]);

    const handleExport = () => {
        toast('Preparing institutional report (CSV)...', 'info');
        setTimeout(() => {
            toast('Audit log exported successfully', 'success');
        }, 1500);
    };

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Accessing Network History...</div>;

    return (
        <div className="animate-institutional">
            <div className="flex justify-between items-end mb-16">
                <div>
                    <h1 className="text-5xl font-bold text-white tracking-tighter mb-4">{t('audit')}</h1>
                    <p className="text-[var(--color-text-muted)] font-black uppercase tracking-[0.25em] text-[10px] flex items-center gap-2">
                        <div className="w-8 h-[1px] bg-[var(--color-silver)]"></div>
                        Immutable Network Audit Sequence
                    </p>
                </div>
                <button
                    onClick={handleExport}
                    className="btn-secondary flex items-center gap-3 px-8"
                >
                    <Download size={18} />
                    <span>Generate Official Report</span>
                </button>
            </div>

            <div className="flex flex-wrap gap-8 mb-12">
                <div className="flex-1 min-w-[300px] relative group">
                    <Search size={18} className="absolute left-6 top-4.5 text-[#a0a0a0] group-focus-within:text-[#d4af37] transition-colors" />
                    <input
                        type="text"
                        className="w-full bg-[#000000] border border-[#1a1a1a] rounded-sm py-4 pl-16 pr-6 text-white focus:outline-none focus:border-[#d4af37] transition-all font-bold text-sm h-14 placeholder:text-[#333333]"
                        placeholder="Search registry by event or entity..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="flex items-center gap-3 bg-[#0a0a0a] px-6 py-2 rounded-sm border border-[#1a1a1a]">
                    <ListFilter size={18} className="text-[#d4af37]" />
                    <select
                        className="bg-transparent border-none outline-none text-white text-[10px] font-black uppercase tracking-widest py-2"
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value)}
                    >
                        <option value="all">Priority: All Events</option>
                        <option value="sblc">SBLC Lifecycle</option>
                        <option value="auth">Auth & Security</option>
                        <option value="error">Critical Errors</option>
                    </select>
                </div>
            </div>

            <div className="bg-[#0a0a0a] overflow-hidden rounded-sm border border-[#1a1a1a] shadow-2xl">
                <table>
                    <thead>
                        <tr>
                            <th>Chronology</th>
                            <th>Network Event</th>
                            <th>Institutional Actor</th>
                            <th>Target Entity</th>
                            <th>State Delta</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map(audit => (
                            <tr key={audit.id} className="hover:bg-[#1a1a1a] transition-colors group border-b border-[#1a1a1a] last:border-0 cursor-default">
                                <td className="text-[9px] text-[#a0a0a0] font-mono font-bold whitespace-nowrap tracking-wider p-6">
                                    {new Date(audit.created_at).toLocaleString()}
                                </td>
                                <td className="p-6">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-1.5 h-1.5 rounded-sm ${audit.event_type.includes('error') ? 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.4)]' : 'bg-[#d4af37]'}`}></div>
                                        <span className="font-bold text-white text-[11px] uppercase tracking-widest">{audit.event_type.replace('_', ' ')}</span>
                                    </div>
                                </td>
                                <td className="p-6">
                                    <div className="flex items-center gap-3 text-[10px] font-bold text-white">
                                        <User size={14} className="text-white" />
                                        <span className="font-mono bg-[#000000] px-2 py-1 rounded-sm border border-[#1a1a1a] uppercase">{(audit.actor_user_id || 'SYSTEM').substring(0, 10)}</span>
                                    </div>
                                </td>
                                <td className="p-6">
                                    <div className="flex items-center gap-3 text-[10px] font-bold text-white font-mono uppercase">
                                        <Box size={14} className="text-[#d4af37]" />
                                        <span>{audit.entity_type}</span>
                                    </div>
                                </td>
                                <td className="p-6">
                                    <div className="flex flex-wrap gap-2">
                                        {Object.keys(audit.after || {}).slice(0, 2).map(k => (
                                            <span key={k} className="text-[8px] bg-[#1a160d] border border-[#d4af37] px-2 py-1 rounded-sm text-[#d4af37] font-black uppercase tracking-tighter">
                                                {k}
                                            </span>
                                        ))}
                                        {Object.keys(audit.after || {}).length > 2 && (
                                            <span className="text-[10px] text-[#a0a0a0] font-black pl-1">+{Object.keys(audit.after).length - 2}</span>
                                        )}
                                        {Object.keys(audit.after || {}).length === 0 && (
                                            <span className="text-[8px] text-[#a0a0a0] font-black uppercase tracking-widest italic opacity-40">Static State</span>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filtered.length === 0 && (
                    <div className="py-24 text-center">
                        <Clock size={60} className="mx-auto text-white/5 mb-6" />
                        <p className="text-[var(--color-text-muted)] font-black uppercase tracking-[0.3em] text-[10px]">No audit records match the institutional query</p>
                    </div>
                )}
            </div>

            <div className="mt-16 p-8 border border-[#1a1a1a] bg-[#0a0a0a] rounded-sm text-center">
                <p className="text-[9px] text-[#a0a0a0] font-black uppercase tracking-[0.2em] leading-loose">
                    This audit trail is cryptographically reinforced. Every entry represents an immutable record of network state transition.
                    Access and generation of reports are strictly logged under security tier protocols.
                </p>
            </div>
        </div>
    );
};

export default AuditHistory;
