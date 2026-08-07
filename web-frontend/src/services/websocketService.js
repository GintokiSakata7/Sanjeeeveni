class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = {};
    this.sosId = null;
    this.reconnectAttempts = 0;
  }

  connect(sosId) {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      if (this.sosId === sosId) return; // Already connected to this SOS
      this.disconnect();
    }
    
    this.sosId = sosId;
    
    // Determine WS protocol based on current location protocol
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // Use the backend URL from config, but change protocol to ws/wss
    // Fallback to localhost if not configured
    let backendUrl = 'http://localhost:8000';
    if (import.meta.env.VITE_BACKEND_URL) {
      backendUrl = import.meta.env.VITE_BACKEND_URL;
    }
    
    const wsUrl = backendUrl.replace(/^https?:/, protocol) + `/api/v1/ws/sos/${sosId}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`WebSocket connected for SOS ${sosId}`);
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit(data.type, data);
      } catch (e) {
        console.error('WebSocket message parsing error', e);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this._scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.onclose = null; // Prevent reconnect
      this.ws.close();
      this.ws = null;
    }
    this.sosId = null;
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('Cannot send message, WebSocket is not open');
    }
  }

  on(type, callback) {
    if (!this.listeners[type]) {
      this.listeners[type] = [];
    }
    this.listeners[type].push(callback);
  }

  off(type, callback) {
    if (this.listeners[type]) {
      this.listeners[type] = this.listeners[type].filter(cb => cb !== callback);
    }
  }

  emit(type, data) {
    if (this.listeners[type]) {
      this.listeners[type].forEach(cb => cb(data));
    }
  }

  _scheduleReconnect() {
    if (this.reconnectAttempts >= 5) {
      console.error('WebSocket max reconnect attempts reached.');
      return;
    }
    
    const timeout = Math.pow(2, this.reconnectAttempts) * 1000;
    setTimeout(() => {
      if (this.sosId) {
        console.log(`Attempting to reconnect (${this.reconnectAttempts + 1})...`);
        this.reconnectAttempts++;
        this.connect(this.sosId);
      }
    }, timeout);
  }
}

// Export as singleton
export const wsService = new WebSocketService();
