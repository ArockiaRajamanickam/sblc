import React, { useState, useEffect } from 'react';
import { Shield, Globe } from 'lucide-react';
import { nodeService } from '../services/api';
import { useTranslation } from 'react-i18next';

const Participants = () => {
    const { t } = useTranslation();
    const [nodes, setNodes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        nodeService.list().then(res => {
            setNodes(res.data);
            setLoading(false);
        });
    }, []);

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Accessing Sovereign Registry...</div>;

    return (
        <div className="animate-institutional">
            <div className="mb-20">
                <h1 className="text-5xl font-bold text-white tracking-tighter mb-4">{t('participants')}</h1>
                <p className="text-[var(--color-text-muted)] font-black uppercase tracking-[0.25em] text-[10px] flex items-center gap-2">
                    <div className="w-8 h-[1px] bg-[var(--color-silver)]"></div>
                    Verified Institutional Protocol Nodes
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                {nodes.map(node => (
                    <div key={node.id} className="bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded-sm group transition-all hover:border-[#ffffff] relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-10 hidden pointer-events-none group-hover:block transition-opacity">
                            <Shield size={120} className="text-[#111111]" />
                        </div>

                        <div className="flex justify-between items-start mb-10">
                            <div className="p-4 border border-[#1a1a1a] bg-[#000000] rounded group-hover:border-[#ffffff] transition-colors">
                                <Globe className="text-white" size={28} />
                            </div>
                            <div className="badge badge-gold">Verified Authority</div>
                        </div>

                        <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">{node.legal_name}</h3>
                        <p className="text-[10px] text-[#a0a0a0] font-black uppercase tracking-[0.2em] mb-10">
                            {node.node_type.replace('_', ' ')} Registry
                        </p>

                        <div className="pt-8 border-t border-[#1a1a1a] space-y-4">
                            <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-wider">
                                <span className="text-[#a0a0a0]">Node Identity Signature</span>
                                <span className="text-white font-mono opacity-60">{(node.id).substring(0, 12)}...</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                <span className="text-[#a0a0a0]">Connectivity State</span>
                                <span className="text-white flex items-center gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                                    ACTIVE NODE
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Participants;
