// API client for 智备小语 backend
const API_BASE = '/api';

const ZhibeiAPI = {
    // === Data endpoints ===

    async getCurriculum() {
        const resp = await fetch(`${API_BASE}/curriculum`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    },

    async getFocusOptions(textType) {
        const resp = await fetch(`${API_BASE}/focus-options?textType=${encodeURIComponent(textType)}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    },

    async getLessonDetail(grade, unit, lesson) {
        const params = new URLSearchParams({ grade, unit, lesson });
        const resp = await fetch(`${API_BASE}/lesson-detail?${params}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    },

    async getKeywordLibrary() {
        const resp = await fetch(`${API_BASE}/keyword-library`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    },

    async getUnitKeywords(grade, unit) {
        const params = new URLSearchParams({ grade, unit });
        const resp = await fetch(`${API_BASE}/unit-keywords?${params}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    },

    async getProviders() {
        const resp = await fetch(`${API_BASE}/providers`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    },

    // === SSE streaming generation ===

    async streamGenerate(endpoint, params, onChunk, onDone, onError, signal) {
        try {
            const resp = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...params, stream: true }),
                signal: signal || undefined
            });

            if (!resp.ok) {
                // Try non-streaming fallback
                const errData = await resp.json().catch(() => ({}));
                throw new Error(errData.error || `HTTP ${resp.status}`);
            }

            const reader = resp.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            onDone();
                            return;
                        }
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.content) onChunk(parsed.content);
                        } catch (e) { /* skip malformed */ }
                    }
                }
            }
            onDone();
        } catch (error) {
            onError(error);
        }
    },

    // === Non-streaming generation (fallback) ===

    async generatePromptSync(params) {
        const resp = await fetch(`${API_BASE}/generate-prompt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...params, stream: false })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    },

    async generateFragmentSync(params) {
        const resp = await fetch(`${API_BASE}/generate-fragment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...params, stream: false })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return resp.json();
    }
};
