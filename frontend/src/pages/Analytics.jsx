import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { PieChart as PieIcon, Activity, DollarSign } from 'lucide-react';
import { adminService } from '../services/api';
import { useTranslation } from 'react-i18next';

const Analytics = () => {
    const { t } = useTranslation();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        adminService.getAnalyticsSummary().then(res => {
            setData(res.data);
            setLoading(false);
        });
    }, []);

    if (loading) return <div className="p-12 text-center text-[var(--color-silver)] font-bold tracking-widest uppercase text-xs">Processing Network Intelligence...</div>;

    const COLORS = ['var(--color-gold)', 'var(--color-silver)', '#ffffff', '#22c55e', '#ef4444'];

    return (
        <div className="animate-institutional space-y-16">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-5xl font-bold text-white tracking-tighter mb-4">{t('analytics')}</h1>
                    <p className="text-[var(--color-text-muted)] font-black uppercase tracking-[0.25em] text-[10px] flex items-center gap-2">
                        <div className="w-8 h-[1px] bg-[var(--color-silver)]"></div>
                        Direct Intelligence Oversight
                    </p>
                </div>
                <div className="px-6 py-3 border border-[#d4af37] bg-[#1a160d] rounded-sm">
                    <p className="text-[10px] text-[#d4af37] font-black uppercase tracking-widest">Network Consensus</p>
                    <p className="text-xl font-bold text-white tracking-tight">Active & Auditable</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                {/* Status Distribution */}
                <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded-sm relative overflow-hidden">
                    <div className="flex items-center gap-4 mb-10">
                        <PieIcon className="text-[#d4af37]" size={24} />
                        <h2 className="text-xs font-black text-white uppercase tracking-[0.2em]">{t('status_distribution')}</h2>
                    </div>
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={data.status_distribution}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={70}
                                    outerRadius={110}
                                    paddingAngle={8}
                                    dataKey="count"
                                    nameKey="status"
                                    stroke="none"
                                >
                                    {data.status_distribution.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ background: '#000000', border: '1px solid #ffffff', borderRadius: '0px', fontSize: '10px' }}
                                    itemStyle={{ color: '#fff', fontWeight: 'bold', textTransform: 'uppercase' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Volume by Currency */}
                <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded-sm relative overflow-hidden">
                    <div className="flex items-center gap-4 mb-10">
                        <DollarSign className="text-white" size={24} />
                        <h2 className="text-xs font-black text-white uppercase tracking-[0.2em]">{t('total_volume')} (%)</h2>
                    </div>
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.volume_by_currency}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
                                <XAxis dataKey="currency" stroke="rgba(255,255,255,0.2)" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="rgba(255,255,255,0.2)" fontSize={10} tickLine={false} axisLine={false} />
                                <Tooltip
                                    cursor={{ fill: '#111111' }}
                                    contentStyle={{ background: '#000000', border: '1px solid #ffffff', borderRadius: '0px' }}
                                />
                                <Bar dataKey="total" fill="url(#institutionalGold)" />
                                <defs>
                                    <linearGradient id="institutionalGold" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#d4af37" />
                                        <stop offset="100%" stopColor="#d4af37" />
                                    </linearGradient>
                                </defs>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="lg:col-span-2 bg-[#0a0a0a] border border-[#1a1a1a] p-10 rounded-sm relative overflow-hidden">
                    <div className="flex items-center gap-4 mb-10">
                        <Activity className="text-white" size={24} />
                        <h2 className="text-xs font-black text-white uppercase tracking-[0.2em]">{t('recent_activity')}</h2>
                    </div>
                    <div className="h-[450px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data.recent_activity}>
                                <defs>
                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ffffff" />
                                        <stop offset="95%" stopColor="#ffffff" />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.02)" vertical={false} />
                                <XAxis dataKey="date" hide />
                                <YAxis stroke="rgba(255,255,255,0.2)" fontSize={10} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ background: 'rgba(10,11,13,0.95)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '2px' }}
                                />
                                <Area type="monotone" dataKey="amount" stroke="var(--color-silver)" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="p-10 border border-[#1a1a1a] bg-[#0a0a0a] rounded-sm text-center">
                <p className="text-[9px] text-[#a0a0a0] font-black uppercase tracking-[0.3em] leading-loose">
                    This intelligence hub provides real-time oversight of the ledger network.
                    All metrics are mathematically derived from verified on-chain state transitions.
                </p>
            </div>
        </div>
    );
};

export default Analytics;
