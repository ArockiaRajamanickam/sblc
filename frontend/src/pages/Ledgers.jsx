import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Database, Globe } from 'lucide-react';
import { ledgerService } from '../services/api';
import { useTranslation } from 'react-i18next';

const Ledgers = () => {
    const { t } = useTranslation();
    const [ledgers, setLedgers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        ledgerService.list().then(res => {
            setLedgers(res.data);
            setLoading(false);
        });
    }, []);

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Accessing Active Registries...</div>;

    return (
        <div className="animate-institutional">
            <div className="flex justify-between items-end mb-16">
                <div>
                    <h1 className="text-5xl font-bold text-white tracking-tighter mb-4">{t('ledgers')}</h1>
                    <p className="text-[var(--color-text-muted)] font-black uppercase tracking-[0.25em] text-[10px] flex items-center gap-2">
                        <div className="w-8 h-[1px] bg-[var(--color-silver)]"></div>
                        Institutional High-Volume Corridors
                    </p>
                </div>
                <button className="btn-primary flex items-center gap-3">
                    <Plus size={18} />
                    <span>Initialize Corridor</span>
                </button>
            </div>

            <div className="flex gap-6 mb-12">
                <div className="flex-1 bg-[#0a0a0a] h-14 rounded flex items-center px-6 border border-[#1a1a1a]">
                    <Search className="text-[var(--color-text-muted)] mr-4" size={18} />
                    <input type="text" placeholder="Search registry by identifier..." className="bg-transparent border-none outline-none text-white w-full text-xs font-bold tracking-widest uppercase placeholder:text-[#333333]" />
                </div>
                <button className="btn-secondary h-14 flex items-center gap-3 px-8">
                    <Filter size={18} />
                    <span>Specifications</span>
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                {ledgers.map(l => (
                    <Link to={`/ledgers/${l.id}`} key={l.id} className="bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded-sm group transition-all hover:border-[#d4af37] relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-10 hidden pointer-events-none group-hover:block transition-opacity">
                            <Database size={120} className="text-[#111111]" />
                        </div>

                        <div className="flex justify-between items-start mb-8">
                            <div className="p-4 border border-[#1a1a1a] bg-[#000000] rounded group-hover:border-[#d4af37] transition-colors">
                                <Globe className="text-white group-hover:text-[#d4af37] transition-colors" size={24} />
                            </div>
                            <div className={`badge ${l.is_active ? 'badge-gold' : 'badge-silver'}`}>
                                {l.is_active ? 'Active Corridor' : 'Registry Archived'}
                            </div>
                        </div>

                        <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">{l.name}</h3>
                        <p className="text-[11px] text-[var(--color-text-muted)] font-medium leading-relaxed mb-8 h-10 line-clamp-2">
                            {l.description || 'Global institutional trading corridor with multi-node consensus enforcement.'}
                        </p>

                        <div className="pt-8 border-t border-[#1a1a1a] grid grid-cols-2 gap-8">
                            <div className="space-y-1">
                                <p className="text-[9px] text-[var(--color-text-muted)] font-black uppercase tracking-widest">Stakeholders</p>
                                <p className="text-lg font-bold text-white">{l.memberships?.length || 4}</p>
                            </div>
                            <div className="space-y-1">
                                <p className="text-[9px] text-[var(--color-text-muted)] font-black uppercase tracking-widest">Network Load</p>
                                <p className="text-[#d4af37] font-black text-sm uppercase tracking-widest">Sovereign High</p>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
};

export default Ledgers;
