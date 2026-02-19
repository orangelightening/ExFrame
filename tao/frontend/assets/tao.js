/**
 * Tao Frontend - Alpine.js Application
 *
 * Provides interactive knowledge analysis interface for query history.
 */

function taoApp() {
    return {
        // State
        currentDomain: localStorage.getItem('currentDomain') || 'peter',
        availableDomains: [],
        activeTab: 'sessions',
        loading: false,
        error: null,
        expandedQueries: {}, // Track which queries are expanded: {sessionId-queryIdx: true}

        // Modal State
        chainModal: {
            open: false,
            data: null
        },
        relatedModal: {
            open: false,
            data: null,
            targetQuery: ''
        },

        // Data
        sessions: [],
        concepts: [],
        depthExplorations: [],
        fullHistory: [], // Store complete query history for detail views

        /**
         * Initialize the application
         */
        async init() {
            console.log('Tao: Initializing...');
            console.log('Tao: Restored domain from localStorage:', this.currentDomain);
            await this.loadDomains();
            await this.loadDomain();
        },

        /**
         * Load available domains from API
         */
        async loadDomains() {
            try {
                const response = await fetch('/api/domains');
                if (!response.ok) {
                    throw new Error(`Failed to load domains: ${response.statusText}`);
                }

                const data = await response.json();
                // Handle both array format and object format {domains: [...]}
                if (Array.isArray(data)) {
                    this.availableDomains = data.map(d => d.domain_id || d.id || d.name);
                } else if (data.domains && Array.isArray(data.domains)) {
                    this.availableDomains = data.domains;
                } else {
                    throw new Error('Unexpected domains API response format');
                }

                // Set default domain if available
                if (this.availableDomains.length > 0 && !this.availableDomains.includes(this.currentDomain)) {
                    this.currentDomain = this.availableDomains[0];
                }

                console.log('Tao: Loaded domains:', this.availableDomains);
            } catch (err) {
                console.error('Tao: Error loading domains:', err);
                this.error = `Failed to load domains: ${err.message}`;
            }
        },

        /**
         * Load data for current domain
         */
        async loadDomain() {
            if (!this.currentDomain) {
                console.warn('Tao: No domain selected');
                return;
            }

            console.log('Tao: Loading domain:', this.currentDomain);

            // Save to localStorage when domain changes
            localStorage.setItem('currentDomain', this.currentDomain);

            this.loading = true;
            this.error = null;

            try {
                // Load all tabs data in parallel
                await Promise.all([
                    this.loadSessions(),
                    this.loadConcepts(),
                    this.loadDepth()
                ]);

                console.log('Tao: Domain loaded successfully');
            } catch (err) {
                console.error('Tao: Error loading domain:', err);
                this.error = `Failed to load domain data: ${err.message}`;
            } finally {
                this.loading = false;
            }
        },

        /**
         * Load session data with full query details
         */
        async loadSessions() {
            try {
                // Load both session summaries and full history
                const [sessionsRes, historyRes] = await Promise.all([
                    fetch(`/api/tao/sessions/${this.currentDomain}?gap_minutes=30&min_queries=1`),
                    this.loadFullHistory()
                ]);

                if (!sessionsRes.ok) {
                    throw new Error(`HTTP ${sessionsRes.status}: ${sessionsRes.statusText}`);
                }

                const sessions = await sessionsRes.json();

                // Enrich sessions with full query objects
                sessions.forEach(session => {
                    session.full_queries = this.getQueriesForSession(session);
                });

                this.sessions = sessions;
                console.log('Tao: Loaded sessions:', this.sessions.length);
            } catch (err) {
                console.error('Tao: Error loading sessions:', err);
                this.sessions = [];
            }
        },

        /**
         * Load full query history for the domain
         */
        async loadFullHistory() {
            try {
                // Use storage API to get full history (we'll need to add this endpoint)
                // For now, we'll fetch from a custom endpoint or parse from sessions
                const response = await fetch(`/api/tao/history/${this.currentDomain}`);

                if (response.ok) {
                    this.fullHistory = await response.json();
                } else {
                    // Fallback: build from sessions data
                    this.fullHistory = [];
                }

                console.log('Tao: Loaded full history:', this.fullHistory.length);
            } catch (err) {
                console.error('Tao: Error loading full history:', err);
                this.fullHistory = [];
            }
        },

        /**
         * Get full query objects for a session
         */
        getQueriesForSession(session) {
            // Try to match session queries with full history entries
            if (!this.fullHistory.length) {
                // Return queries as-is if no full history
                return session.queries.map((q, idx) => ({
                    query: q,
                    response: 'Loading...',
                    timestamp: session.start_time,
                    metadata: {}
                }));
            }

            // Match by query text and time range
            const startTime = new Date(session.start_time);
            const endTime = new Date(session.end_time);

            return this.fullHistory.filter(entry => {
                const entryTime = new Date(entry.timestamp);
                return entryTime >= startTime && entryTime <= endTime;
            });
        },

        /**
         * Load concept data
         */
        async loadConcepts() {
            try {
                const response = await fetch(`/api/tao/concepts/${this.currentDomain}?top_n=20&min_freq=2`);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                this.concepts = await response.json();
                console.log('Tao: Loaded concepts:', this.concepts.length);
            } catch (err) {
                console.error('Tao: Error loading concepts:', err);
                // Don't throw - allow other tabs to load
                this.concepts = [];
            }
        },

        /**
         * Load exploration depth data
         */
        async loadDepth() {
            try {
                const response = await fetch(`/api/tao/depth/${this.currentDomain}?min_depth=2&time_gap=10`);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                this.depthExplorations = await response.json();
                console.log('Tao: Loaded depth explorations:', this.depthExplorations.length);
            } catch (err) {
                console.error('Tao: Error loading depth:', err);
                // Don't throw - allow other tabs to load
                this.depthExplorations = [];
            }
        },

        /**
         * Format timestamp to readable format
         */
        formatTime(timestamp) {
            try {
                const date = new Date(timestamp);
                return date.toLocaleString();
            } catch {
                return timestamp;
            }
        },

        /**
         * Toggle query detail expansion
         */
        toggleQueryDetail(sessionId, queryIdx) {
            const key = `${sessionId}-${queryIdx}`;
            this.expandedQueries[key] = !this.expandedQueries[key];
        },

        /**
         * Check if query is expanded
         */
        isQueryExpanded(sessionId, queryIdx) {
            const key = `${sessionId}-${queryIdx}`;
            return !!this.expandedQueries[key];
        },

        /**
         * View query chain (before/after this query)
         */
        async viewChain(entryId) {
            if (!entryId) {
                console.warn('No entry ID provided for chain view');
                return;
            }

            try {
                this.loading = true;
                const response = await fetch(`/api/tao/chains/${this.currentDomain}/${entryId}?before=3&after=3`);

                if (response.ok) {
                    const chain = await response.json();
                    this.chainModal.data = chain;
                    this.chainModal.open = true;
                    console.log('Query chain loaded:', chain);
                } else {
                    throw new Error(`Failed to load chain: ${response.statusText}`);
                }
            } catch (err) {
                console.error('Error loading chain:', err);
                alert(`Error loading chain: ${err.message}`);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Close chain modal
         */
        closeChainModal() {
            this.chainModal.open = false;
            // Clear data after animation completes
            setTimeout(() => {
                this.chainModal.data = null;
            }, 300);
        },

        /**
         * Find related queries
         */
        async findRelated(entryId, targetQuery = '') {
            if (!entryId) {
                console.warn('No entry ID provided for related queries');
                return;
            }

            try {
                this.loading = true;
                const response = await fetch(`/api/tao/related/${this.currentDomain}/${entryId}?strategy=all&limit=10`);

                if (response.ok) {
                    const related = await response.json();
                    this.relatedModal.data = related;
                    this.relatedModal.targetQuery = targetQuery || `Entry #${entryId}`;
                    this.relatedModal.open = true;
                    console.log('Related queries loaded:', related);
                } else {
                    throw new Error(`Failed to load related queries: ${response.statusText}`);
                }
            } catch (err) {
                console.error('Error finding related:', err);
                alert(`Error finding related queries: ${err.message}`);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Close related modal
         */
        closeRelatedModal() {
            this.relatedModal.open = false;
            // Clear data after animation completes
            setTimeout(() => {
                this.relatedModal.data = null;
                this.relatedModal.targetQuery = '';
            }, 300);
        }
    }
}

// Log when script loads
console.log('Tao: Frontend script loaded');
