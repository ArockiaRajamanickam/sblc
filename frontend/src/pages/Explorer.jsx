import React, { useState, useEffect } from 'react';
import { Box, Hash, Clock, Link as LinkIcon, Database, ArrowRight, ShieldCheck } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const Explorer = () => {
    const { t } = useTranslation();
    const [blocks, setBlocks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Generate mock blocks based on the "Truth Anchor" concept
        const mockBlocks = Array.from({ length: 10 }).map((_, i) => ({
            height: 4829310 - i,
            hash: Math.random().toString(16).substring(2, 10) + '...0x' + Math.random().toString(16).substring(2, 6),
            time: new Date(Date.now() - i * 600000).toLocaleString(),
            txCount: Math.floor(Math.random() * 5) + 1,
            validator: 'Node_' + (i % 3 + 1)
        }));

        setTimeout(() => {
            setBlocks(mockBlocks);
            setLoading(false);
        }, 800);
    }, []);

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Syncing Ledger Protocol...</div>;

    return (
        <div className="animate-institutional">
            <div className="mb-20">
                <h1 className="text-5xl font-bold text-white tracking-tighter mb-4">{t('explorer')}</h1>
                <p className="text-[var(--color-text-muted)] font-black uppercase tracking-[0.25em] text-[10px] flex items-center gap-2">
                    <div className="w-8 h-[1px] bg-[var(--color-gold)]"></div>
                    Real-time Protocol Layer Inspection
                </p>
            </div>

            <div className="grid grid-cols-1 gap-4">
                {blocks.map((block) => (
                    <div key={block.height} className="bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded-sm hover:border-[#ffffff] transition-all group overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-10 hidden group-hover:block pointer-events-none">
                            <ShieldCheck size={160} className="text-[#111111]" />
                        </div>

                        <div className="flex flex-wrap items-center justify-between gap-10 relative z-10">
                            <div className="flex items-center gap-8">
                                <div className="p-4 bg-[#000000] border border-[#1a1a1a] rounded group-hover:border-[#ffffff] transition-colors">
                                    <Box className="text-white" size={28} />
                                </div>
                                <div>
                                    <h3 className="text-[10px] font-black text-[#a0a0a0] uppercase tracking-widest mb-2">Block Sequence</h3>
                                    <p className="text-3xl font-mono font-bold text-white tracking-tight">{block.height}</p>
                                </div>
                            </div>

                            <div className="flex-1 min-w-[300px]">
                                <div className="flex items-center gap-3 mb-3">
                                    <Hash size={14} className="text-[#d4af37]" />
                                    <span className="text-[10px] font-black text-[#a0a0a0] uppercase tracking-widest">Merkle Anchor Hash</span>
                                </div>
                                <p className="text-[11px] font-mono text-[#d4af37] bg-[#1a160d] px-4 py-2 rounded border border-[#d4af37] truncate select-all">{block.hash}</p>
                            </div>

                            <div className="flex items-center gap-10">
                                <div>
                                    <div className="flex items-center gap-2 mb-1 text-[var(--text-muted)]">
                                        <Clock size={14} />
                                        <span className="text-[10px] font-bold uppercase tracking-wider">Timestamp</span>
                                    </div>
                                    <p className="text-sm font-medium">{block.time}</p>
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1 text-[var(--text-muted)]">
                                        <LinkIcon size={14} />
                                        <span className="text-[10px] font-bold uppercase tracking-wider">Payload</span>
                                    </div>
                                    <p className="text-sm font-bold text-emerald-400">{block.txCount} TXs</p>
                                </div>
                            </div>

                            <button className="p-3 bg-[#000000] rounded-sm hover:border-[#d4af37] hover:text-[#d4af37] transition-all border border-[#1a1a1a]">
                                <ArrowRight size={20} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Explorer;
