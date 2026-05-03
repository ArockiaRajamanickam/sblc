import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  ArrowRightLeft, 
  ShieldCheck, 
  Globe, 
  Wallet, 
  Lock, 
  Activity,
  ChevronRight,
  PlusCircle,
  AlertCircle,
  FileText,
  Zap,
  Cpu,
  Server,
  RefreshCw,
  TrendingUp,
  CreditCard
} from 'lucide-react';
import api from '../services/api';

const BankingCompliance = () => {
    const [accounts, setAccounts] = useState([]);
    const [instruments, setInstruments] = useState([]);
    const [wallets, setWallets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('accounts');

    const fetchData = async () => {
        setLoading(true);
        try {
            const [accRes, instRes, walletRes] = await Promise.all([
                api.get('/banking/accounts'),
                api.get('/banking/instruments'),
                api.get('/banking/wallets')
            ]);
            setAccounts(accRes.data);
            setInstruments(instRes.data);
            setWallets(walletRes.data);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch banking data", err);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const tabs = [
        { id: 'accounts', label: 'Treasury & Nostro', icon: Building2 },
        { id: 'instruments', label: 'Debt & Securities', icon: FileText },
        { id: 'wallets', label: 'Digital Assets', icon: Wallet },
        { id: 'compliance', label: 'CB Portals & AML', icon: ShieldCheck }
    ];

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter text-white mb-2 italic">Institutional Command</h1>
                    <p className="text-slate-400 max-w-2xl text-sm font-medium tracking-wide">
                        Global settlement engine interconnecting bank portals, digital wallets, and fixed-income portfolios in real-time.
                    </p>
                </div>
                <div className="flex gap-4">
                    <button 
                        onClick={fetchData}
                        className="p-3 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 rounded-xl transition-all shadow-xl"
                    >
                        <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
                    </button>
                    <button className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-black text-xs uppercase tracking-[0.2em] transition-all flex items-center gap-3 shadow-2xl shadow-indigo-900/40 ring-1 ring-indigo-400/50">
                        <Zap size={18} fill="currentColor" />
                        Execute Real-Time Move
                    </button>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex gap-2 p-1.5 bg-slate-950 border border-slate-800 rounded-2xl w-fit shadow-2xl">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-8 py-3 rounded-xl flex items-center gap-3 text-xs font-black uppercase tracking-widest transition-all ${
                            activeTab === tab.id 
                            ? 'bg-slate-800 text-white shadow-inner ring-1 ring-slate-700/50' 
                            : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900'
                        }`}
                    >
                        <tab.icon size={18} className={activeTab === tab.id ? 'text-indigo-400' : ''} />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content Area */}
            {activeTab === 'accounts' && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 slide-in-from-bottom-4 animate-in">
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-slate-950 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-slate-900 text-slate-500 font-black uppercase tracking-[0.3em] text-[10px]">
                                    <tr>
                                        <th className="px-8 py-6">Identity / Account</th>
                                        <th className="px-4 py-6">Compliance</th>
                                        <th className="px-4 py-6">Classification</th>
                                        <th className="px-8 py-6 text-right">Available Balance</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800/50">
                                    {accounts.map(acc => (
                                        <tr key={acc.id} className="hover:bg-slate-900/50 transition-colors group cursor-pointer">
                                            <td className="px-8 py-6">
                                                <div className="text-white font-black font-mono text-base tracking-tighter">{acc.account_number}</div>
                                                <div className="text-[10px] text-slate-500 flex items-center gap-2 mt-1.5 font-bold uppercase tracking-widest">
                                                    <Cpu size={12} className="text-indigo-500" /> NODE: {acc.node_id.slice(0, 8)}
                                                </div>
                                            </td>
                                            <td className="px-4 py-6">
                                                <div className="flex items-center gap-2">
                                                    <div className={`w-2 h-2 rounded-full ${acc.is_active ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-rose-500'}`}></div>
                                                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">{acc.is_active ? 'Sanctioned' : 'Flagged'}</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-6">
                                               <span className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest border ${
                                                   acc.is_nostro 
                                                   ? 'bg-amber-500/10 text-amber-500 border-amber-500/30' 
                                                   : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
                                               }`}>
                                                   {acc.is_nostro ? 'Nostro Registry' : `Inst: ${acc.account_type.replace('_', ' ')}`}
                                               </span>
                                            </td>
                                            <td className="px-8 py-6 text-right font-mono">
                                                <div className="text-white font-black text-xl tracking-tighter">
                                                    {parseFloat(acc.balance).toLocaleString()} <span className="text-xs text-slate-500 font-bold">{acc.currency}</span>
                                                </div>
                                                <div className="text-[10px] text-rose-500 font-black uppercase tracking-widest mt-1">
                                                    -{parseFloat(acc.reserved_funds).toLocaleString()} Held on Compliance
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className="space-y-6 font-bold uppercase tracking-widest text-[10px]">
                        <div className="bg-gradient-to-br from-indigo-950 to-slate-950 border border-indigo-500/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
                            <TrendingUp className="absolute -bottom-4 -right-4 text-indigo-500/10 group-hover:text-indigo-500/20 transition-all pointer-events-none" size={160} />
                            <h3 className="text-white font-black mb-6 flex items-center gap-3 text-xs italic">
                                <Activity size={20} className="text-indigo-400" />
                                Hierarchy Aggregation
                            </h3>
                            <div className="space-y-6 relative z-10">
                                <div className="flex justify-between items-center py-2 border-b border-indigo-500/10">
                                    <span className="text-slate-500">Master Entities</span>
                                    <span className="text-sm font-black text-white">{accounts.filter(a => a.account_type === 'master').length}</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-indigo-500/10">
                                    <span className="text-slate-500">Managed Sub-Accounts</span>
                                    <span className="text-sm font-black text-white">{accounts.filter(a => a.account_type === 'sub_account').length}</span>
                                </div>
                                <div className="mt-8">
                                    <div className="text-slate-400 mb-2">Institutional NAV (Aggregate)</div>
                                    <div className="text-3xl font-black text-white tracking-tighter">$142.8M <span className="text-xs text-indigo-400">EQV</span></div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-slate-900/40 border border-slate-800 p-8 rounded-3xl space-y-4 shadow-xl">
                             <div className="flex items-center gap-4 text-emerald-500 mb-4">
                                <ShieldCheck size={28} />
                                <h4 className="font-black text-white text-xs tracking-[0.2em]">Fenced Liquidity</h4>
                             </div>
                             <p className="text-[10px] text-slate-500 leading-relaxed font-medium normal-case tracking-normal">
                                Automated fencing protocols prevent unauthorized cross-jurisdictional leakage. Every move requires a CB Gateway allowance.
                             </p>
                             <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 w-4/5 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                             </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'instruments' && (
                <div className="space-y-6 slide-in-from-bottom-4 animate-in">
                    <div className="bg-slate-950 border border-slate-800 rounded-3xl p-0 overflow-hidden shadow-2xl">
                        <div className="px-8 py-6 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
                             <h3 className="font-black text-white uppercase tracking-[0.3em] text-[10px] flex items-center gap-3">
                                <Zap className="text-amber-500" size={18} fill="currentColor" />
                                Institutional Debt Portfolio
                             </h3>
                             <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-indigo-400 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all">
                                 <PlusCircle size={14} /> New Issuance
                             </button>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 divide-x divide-y divide-slate-800/50">
                            {instruments.map(inst => (
                                <div key={inst.id} className="p-8 hover:bg-slate-900/50 transition-all group flex flex-col justify-between">
                                    <div>
                                        <div className="flex justify-between items-start mb-6">
                                            <div className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest ${
                                                inst.is_national_debt ? 'bg-amber-900/30 text-amber-500 border border-amber-900/50' : 'bg-indigo-900/30 text-indigo-400 border border-indigo-900/50'
                                            }`}>
                                                {inst.is_national_debt ? 'Sovereign Debt' : inst.instrument_type}
                                            </div>
                                            <div className="text-slate-600 group-hover:text-indigo-500 transition-colors">
                                                <CreditCard size={20} />
                                            </div>
                                        </div>
                                        <div className="text-xl font-black text-white group-hover:text-indigo-100 transition-colors leading-tight tracking-tight mb-2 italic">
                                            {inst.name}
                                        </div>
                                        <div className="font-mono text-[10px] text-slate-500 uppercase font-black tracking-widest mb-8">
                                            ISIN: {inst.isin || 'UNREGISTERED'}
                                        </div>
                                    </div>
                                    
                                    <div className="space-y-4 border-t border-slate-800 pt-6">
                                        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                            <span className="text-slate-500">Par / Principal</span>
                                            <span className="text-white tracking-widest">{parseFloat(inst.par_value).toLocaleString()} {inst.currency}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                            <span className="text-slate-500">Fixed Yield</span>
                                            <span className="text-emerald-500 tracking-widest">{(inst.coupon_rate * 100).toFixed(2)}% APR</span>
                                        </div>
                                        <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest">
                                            <span className="text-slate-500">Maturity Window</span>
                                            <span className="text-indigo-400 tracking-widest">DEC 2026</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'wallets' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 slide-in-from-bottom-4 animate-in">
                    <div className="bg-slate-950 border border-slate-800 rounded-3xl p-8 shadow-2xl">
                        <div className="flex justify-between items-center mb-10">
                            <h3 className="text-2xl font-black text-white flex items-center gap-4 italic tracking-tighter">
                                <Wallet className="text-emerald-500" />
                                Vault Inventory
                            </h3>
                            <button className="flex items-center gap-2 text-[10px] font-black text-indigo-400 hover:text-indigo-300 uppercase tracking-[0.2em]">
                                <PlusCircle size={16} /> Link Wallet
                            </button>
                        </div>
                        <div className="space-y-5">
                            {wallets.map(w => (
                                <div key={w.id} className="p-6 bg-slate-900/50 border border-slate-800/80 rounded-2xl hover:border-emerald-500/40 transition-all cursor-pointer group shadow-lg">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-4">
                                            <div className="p-3 bg-slate-950 rounded-xl text-emerald-500 border border-slate-800 group-hover:scale-110 transition-all duration-300">
                                                <Activity size={20} />
                                            </div>
                                            <div>
                                                <div className="text-xs font-black text-white uppercase tracking-[0.2em]">{w.wallet_type.replace('_', ' ')} Registry</div>
                                                <div className="text-[10px] text-slate-500 font-mono mt-1 tracking-tighter select-all">{w.address}</div>
                                            </div>
                                        </div>
                                        <div className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest ${
                                            w.is_verified_by_bank 
                                            ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]' 
                                            : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                                        }`}>
                                            {w.is_verified_by_bank ? 'Verified Custody' : 'Awaiting Audit'}
                                        </div>
                                    </div>
                                    {w.is_verified_by_bank && (
                                        <div className="pt-4 border-t border-slate-800 flex items-center gap-3 text-[9px] text-slate-500 font-bold uppercase tracking-widest">
                                            <ShieldCheck size={14} className="text-emerald-500" />
                                            Attested by Banking Node: {w.verifying_bank_id.slice(0, 16).toUpperCase()}...
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-slate-950 via-slate-950 to-indigo-950/20 border border-slate-800 rounded-3xl p-10 flex flex-col justify-center items-center text-center shadow-2xl relative overflow-hidden group">
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.05)_0%,transparent_70%)] pointer-events-none"></div>
                        <div className="w-24 h-24 bg-indigo-500/10 rounded-3xl flex items-center justify-center mb-8 text-indigo-400 ring-8 ring-indigo-500/5 group-hover:scale-105 transition-all duration-500">
                            <RefreshCw size={48} className="group-hover:rotate-180 transition-all duration-700" />
                        </div>
                        <h4 className="text-3xl font-black text-white mb-4 italic tracking-tighter">Instant Settlement Bridge</h4>
                        <p className="text-slate-500 text-sm max-w-sm mb-10 leading-relaxed font-medium">
                            Atomic cross-asset swaps between fiat treasury balances and digital custody vaults. Powered by DAO-style executionMove protocols.
                        </p>
                        <button className="px-12 py-5 bg-white text-black font-black uppercase tracking-[0.3em] text-[10px] rounded-full hover:bg-slate-100 transition-all shadow-2xl shadow-indigo-500/20 hover:scale-105 active:scale-95 ring-4 ring-white/10">
                            Launch Bridge Protocol
                        </button>
                    </div>
                </div>
            )}

            {activeTab === 'compliance' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 slide-in-from-bottom-4 animate-in">
                    <div className="space-y-6">
                        <div className="bg-slate-950 border border-slate-800 rounded-3xl p-8 shadow-2xl">
                            <h3 className="text-lg font-black text-white mb-8 flex items-center gap-4 italic tracking-widest uppercase text-xs">
                                <Globe className="text-blue-400" />
                                CB Gateway Infrastructure
                            </h3>
                            <div className="space-y-4">
                                {[
                                    { name: 'Bank of England', flag: '🇬🇧', status: 'SYNCHRONIZED', response: '0.04s', limit: '$1.2B' },
                                    { name: 'Bank of China', flag: '🇨🇳', status: 'SYNCHRONIZED', response: '0.12s', limit: '$500M' },
                                    { name: 'Federal Reserve US', flag: '🇺🇸', status: 'STANDBY', response: '-', limit: '$2.4B' }
                                ].map((cb, i) => (
                                    <div key={i} className="flex items-center justify-between p-5 bg-slate-900/60 rounded-2xl border border-slate-800/80 hover:border-blue-500/30 transition-all cursor-pointer">
                                        <div className="flex items-center gap-5">
                                            <span className="text-3xl drop-shadow-md">{cb.flag}</span>
                                            <div>
                                                <div className="text-sm font-black text-white tracking-tight">{cb.name}</div>
                                                <div className="text-[9px] text-slate-500 uppercase tracking-[0.2em] font-black mt-1">Status: {cb.status} &bull; Lat: {cb.response}</div>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-xs font-black text-white tracking-widest font-mono">{cb.limit}</div>
                                            <div className="text-[8px] text-slate-500 uppercase font-black tracking-widest mt-1">Allowance</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="bg-rose-950/10 border border-rose-900/40 rounded-3xl p-8 relative overflow-hidden group shadow-2xl">
                        <div className="absolute -top-10 -right-10 p-12 text-rose-500/5 group-hover:text-rose-500/10 transition-all pointer-events-none">
                            <AlertCircle size={240} />
                        </div>
                        <h3 className="text-white font-black mb-8 flex items-center gap-4 italic tracking-widest uppercase text-xs">
                            <ShieldCheck className="text-rose-500" />
                            Global Sanction Oversight
                        </h3>
                        <div className="space-y-4 relative z-10">
                             <div className="p-5 bg-rose-500/5 border border-rose-500/20 rounded-2xl backdrop-blur-sm">
                                <div className="flex justify-between items-center mb-4">
                                    <span className="text-[10px] font-black text-rose-500 uppercase tracking-[0.3em]">AML Violation Detected</span>
                                    <span className="text-[9px] text-rose-400 font-mono font-black italic">NODE: LUX-04</span>
                                </div>
                                <div className="text-base text-white font-black mb-1 tracking-tight italic">Velocity Overload Trigger</div>
                                <div className="text-[10px] text-rose-400/70 font-bold uppercase tracking-widest">Entity: Restricted Jurisdiction Leakage Check</div>
                             </div>
                             <div className="p-5 bg-slate-900/40 border border-slate-800 rounded-2xl opacity-40">
                                <div className="flex justify-between items-center mb-4">
                                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Audit Trace pass</span>
                                    <span className="text-[9px] text-slate-600 font-mono font-black">NODE: SIN-12</span>
                                </div>
                                <div className="text-sm text-slate-300 font-black mb-1">Institutional Corridor Clear</div>
                                <div className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">Verified Nostro Settlement Logic</div>
                             </div>
                        </div>
                    </div>
                </div>
            )}

            {loading && (
                <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-lg flex items-center justify-center z-50">
                    <div className="bg-slate-900 border border-slate-800 p-12 rounded-[40px] flex flex-col items-center gap-6 shadow-[0_0_100px_rgba(99,102,241,0.1)]">
                        <div className="relative">
                            <RefreshCw className="text-indigo-500 animate-[spin_2s_linear_infinite]" size={60} />
                            <Cpu className="absolute inset-0 m-auto text-indigo-400 animate-pulse" size={24} />
                        </div>
                        <span className="text-indigo-400 font-black uppercase tracking-[0.6em] text-[10px] animate-pulse">Synchronizing Universal Ledger</span>
                    </div>
                </div>
            )}
        </div>
    );
};

export default BankingCompliance;
