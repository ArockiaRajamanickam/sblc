import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

let toastTimeout;
let observers = [];

export const toast = (message, type = 'info') => {
    observers.forEach(o => o(message, type));
};

const ToastContainer = () => {
    const [active, setActive] = useState(false);
    const [data, setData] = useState({ message: '', type: 'info' });

    useEffect(() => {
        observers.push((message, type) => {
            setData({ message, type });
            setActive(true);
            if (toastTimeout) clearTimeout(toastTimeout);
            toastTimeout = setTimeout(() => setActive(false), 5000);
        });
        return () => { observers = []; };
    }, []);

    if (!active) return null;

    const icons = {
        success: <CheckCircle2 className="text-[var(--color-gold)]" size={18} />,
        error: <AlertCircle className="text-red-500" size={18} />,
        info: <Info className="text-[var(--color-silver)]" size={18} />
    };

    return (
        <div className="fixed bottom-12 right-12 z-[200] animate-institutional">
            <div className={`glass flex items-center gap-5 px-8 py-5 rounded-sm border-l-4 shadow-2xl ${data.type === 'error' ? 'border-l-red-500/80 bg-red-500/[0.02]' :
                data.type === 'success' ? 'border-l-[var(--color-gold)] bg-[var(--color-gold)]/[0.02]' :
                    'border-l-[var(--color-silver)] bg-white/[0.02]'
                }`}>
                <div className="shrink-0">{icons[data.type]}</div>
                <div className="space-y-0.5 min-w-[240px]">
                    <p className="text-[9px] font-black uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
                        {data.type === 'error' ? 'System Warning' : 'Network Notification'}
                    </p>
                    <p className="text-sm font-bold text-white tracking-tight">{data.message}</p>
                </div>
                <button
                    onClick={() => setActive(false)}
                    className="ml-6 text-[var(--color-text-muted)] hover:text-white transition-colors p-1"
                >
                    <X size={16} />
                </button>
            </div>
        </div>
    );
};

export default ToastContainer;
