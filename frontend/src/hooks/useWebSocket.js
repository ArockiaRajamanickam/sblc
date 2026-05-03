import { useEffect } from 'react';
import { toast } from '../components/Toast';

const useWebSocket = () => {
    useEffect(() => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // For demo, we assume the backend is on the same host but port 8000
        const ws = new WebSocket(`${protocol}//localhost:8000/ws/events`);

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'SBLC_STATUS_CHANGE') {
                    toast(`Network Event: SBLC ${data.reference_number} is now ${data.status}`, 'info');
                }
            } catch (e) {
                console.warn('WS Message Error:', e);
            }
        };

        ws.onerror = (err) => console.error('WS Connection Error:', err);
        ws.onclose = () => console.warn('WS Connected Closed');

        return () => ws.close();
    }, []);
};

export default useWebSocket;
