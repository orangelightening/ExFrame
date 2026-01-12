/**
 * API client for EEFrame unified backend.
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        error: response.statusText,
      }));
      throw new Error(error.error || error.message || 'API request failed');
    }

    return response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * System Status API
 */
export const systemAPI = {
  /**
   * Get current system status
   */
  getStatus: () => fetchAPI('/system/status'),

  /**
   * Get system metrics
   */
  getMetrics: () => fetchAPI('/system/metrics'),

  /**
   * Get system logs
   */
  getLogs: (since = 3600) => fetchAPI(`/system/logs?since=${since}`),

  /**
   * Get system configuration
   */
  getConfig: () => fetchAPI('/system/configuration'),
};

/**
 * AI Assistant API
 */
export const assistAPI = {
  /**
   * Query the AI assistant
   */
  query: (query, userId = 'web-user', passthrough = false) =>
    fetchAPI('/assist/query', {
      method: 'POST',
      body: JSON.stringify({ query, user_id: userId, passthrough }),
    }),

  /**
   * Run diagnostics
   */
  diagnose: () => fetchAPI('/assist/diagnostics', { method: 'POST' }),
};

/**
 * Knowledge Base API
 */
export const knowledgeAPI = {
  /**
   * Get all patterns
   */
  getPatterns: () => fetchAPI('/knowledge/patterns'),

  /**
   * Get a specific pattern
   */
  getPattern: (patternId) => fetchAPI(`/knowledge/patterns/${patternId}`),

  /**
   * Search patterns
   */
  searchPatterns: (query, category = null) => {
    const params = new URLSearchParams({ q: query });
    if (category) params.append('category', category);
    return fetchAPI(`/knowledge/search?${params}`);
  },

  /**
   * Submit feedback
   */
  submitFeedback: (query, response, feedback, userId = 'web-user') =>
    fetchAPI('/knowledge/feedback', {
      method: 'POST',
      body: JSON.stringify({
        query,
        response,
        feedback,
        user_id: userId,
      }),
    }),
};

/**
 * Alerts API
 */
export const alertsAPI = {
  /**
   * Get all alerts
   */
  getAlerts: () => fetchAPI('/alerts'),

  /**
   * Get a specific alert
   */
  getAlert: (alertId) => fetchAPI(`/alerts/${alertId}`),

  /**
   * Acknowledge an alert
   */
  acknowledgeAlert: (alertId) =>
    fetchAPI(`/alerts/acknowledge/${alertId}`, { method: 'POST' }),
};

/**
 * History API
 */
export const historyAPI = {
  /**
   * Get issue history
   */
  getIssues: () => fetchAPI('/history/issues'),

  /**
   * Get system snapshots
   */
  getSnapshots: () => fetchAPI('/history/snapshots'),

  /**
   * Add a note to history
   */
  addNote: (note) =>
    fetchAPI('/history/note', {
      method: 'POST',
      body: JSON.stringify(note),
    }),
};

/**
 * Tracing API
 */
export const traceAPI = {
  /**
   * List all traces
   */
  listTraces: (limit = 50, offset = 0) =>
    fetchAPI(`/traces?limit=${limit}&offset=${offset}`),

  /**
   * Get a specific trace
   */
  getTrace: (queryId) => fetchAPI(`/traces/${queryId}`),

  /**
   * Get Mermaid diagram for a trace
   */
  getTraceMermaid: (queryId) => fetchAPI(`/traces/${queryId}/mermaid`),
};

/**
 * Pattern Management API (from Expertise Scanner)
 */
export const patternAPI = {
  /**
   * List all patterns
   */
  listPatterns: (domain = null, limit = 50, offset = 0) => {
    const params = new URLSearchParams({ limit, offset });
    if (domain) params.append('domain', domain);
    return fetchAPI(`/patterns?${params}`);
  },

  /**
   * Get a specific pattern
   */
  getPattern: (patternId) => fetchAPI(`/patterns/${patternId}`),

  /**
   * Create a new pattern
   */
  createPattern: (pattern) =>
    fetchAPI('/patterns', {
      method: 'POST',
      body: JSON.stringify(pattern),
    }),

  /**
   * Update a pattern
   */
  updatePattern: (patternId, pattern) =>
    fetchAPI(`/patterns/${patternId}`, {
      method: 'PUT',
      body: JSON.stringify(pattern),
    }),

  /**
   * Delete a pattern
   */
  deletePattern: (patternId) =>
    fetchAPI(`/patterns/${patternId}`, { method: 'DELETE' }),

  /**
   * Search patterns
   */
  searchPatterns: (query, domain = null) => {
    const params = new URLSearchParams({ q: query });
    if (domain) params.append('domain', domain);
    return fetchAPI(`/patterns/search?${params}`);
  },
};

/**
 * Ingestion API (from Expertise Scanner)
 */
export const ingestionAPI = {
  /**
   * Ingest from URL
   */
  ingestFromUrl: (url, domain = 'cooking') =>
    fetchAPI('/ingestion/url', {
      method: 'POST',
      body: JSON.stringify({ url, domain }),
    }),

  /**
   * Ingest from text
   */
  ingestFromText: (text, domain = 'cooking') =>
    fetchAPI('/ingestion/text', {
      method: 'POST',
      body: JSON.stringify({ text, domain }),
    }),

  /**
   * Ingest from JSON
   */
  ingestFromJson: (json, domain = 'cooking') =>
    fetchAPI('/ingestion/json', {
      method: 'POST',
      body: JSON.stringify({ json, domain }),
    }),

  /**
   * Batch ingestion
   */
  batchIngest: (files, domain = 'cooking') =>
    fetchAPI('/ingestion/batch', {
      method: 'POST',
      body: JSON.stringify({ files, domain }),
    }),

  /**
   * Get ingestion status
   */
  getStatus: () => fetchAPI('/ingestion/status'),
};

/**
 * Knowledge Graph API (from Expertise Scanner)
 */
export const graphAPI = {
  /**
   * Get knowledge graph
   */
  getGraph: (domain = null) => {
    const params = domain ? `?domain=${domain}` : '';
    return fetchAPI(`/knowledge/graph${params}`);
  },

  /**
   * Get graph nodes
   */
  getNodes: (domain = null) => {
    const params = domain ? `?domain=${domain}` : '';
    return fetchAPI(`/knowledge/graph/nodes${params}`);
  },

  /**
   * Get graph edges
   */
  getEdges: (domain = null) => {
    const params = domain ? `?domain=${domain}` : '';
    return fetchAPI(`/knowledge/graph/edges${params}`);
  },

  /**
   * Query graph
   */
  queryGraph: (query) =>
    fetchAPI('/knowledge/graph/query', {
      method: 'POST',
      body: JSON.stringify(query),
    }),

  /**
   * Rebuild graph
   */
  rebuildGraph: () =>
    fetchAPI('/knowledge/graph/rebuild', { method: 'POST' }),

  /**
   * Get graph statistics
   */
  getStats: () => fetchAPI('/knowledge/graph/stats'),
};

/**
 * Universe API
 */
export const universeAPI = {
  /**
   * List all universes
   */
  listUniverses: () => fetchAPI('/universes'),

  /**
   * Get universe info
   */
  getUniverse: (universeId) => fetchAPI(`/universes/${universeId}`),

  /**
   * Load a universe on-demand
   */
  loadUniverse: (universeId) =>
    fetchAPI(`/universes/${universeId}/load`, { method: 'POST' }),

  /**
   * Create a new universe
   */
  createUniverse: (universeId, name, description = '', baseOn = null) =>
    fetchAPI('/universes', {
      method: 'POST',
      body: JSON.stringify({
        universe_id: universeId,
        name,
        description,
        base_on: baseOn,
      }),
    }),

  /**
   * List domains in a universe
   */
  listDomains: (universeId) => fetchAPI(`/universes/${universeId}/domains`),

  /**
   * Query within a universe
   */
  query: (universeId, domainId, query, includeTrace = false) =>
    fetchAPI(`/universes/${universeId}/domains/${domainId}/query`, {
      method: 'POST',
      body: JSON.stringify({
        query,
        domain: domainId,
        include_trace: includeTrace,
      }),
    }),

  /**
   * Merge universes
   */
  mergeUniverses: (source, target, strategy = 'merge_patterns') =>
    fetchAPI('/admin/universes/merge', {
      method: 'POST',
      body: JSON.stringify({
        source,
        target,
        strategy,
      }),
    }),
};

/**
 * Domains API
 */
export const domainsAPI = {
  /**
   * List all domains
   */
  listDomains: () => fetchAPI('/domains'),

  /**
   * Get domain info
   */
  getDomain: (domainId) => fetchAPI(`/domains/${domainId}`),

  /**
   * Get domain specialists
   */
  getSpecialists: (domainId) => fetchAPI(`/domains/${domainId}/specialists`),

  /**
   * Get domain patterns
   */
  getPatterns: (domainId, category = null) => {
    const params = category ? `?category=${category}` : '';
    return fetchAPI(`/domains/${domainId}/patterns${params}`);
  },

  /**
   * Get pattern details
   */
  getPattern: (domainId, patternId) =>
    fetchAPI(`/domains/${domainId}/patterns/${patternId}`),

  /**
   * Get domain health
   */
  getHealth: (domainId) => fetchAPI(`/domains/${domainId}/health`),

  /**
   * Query domain
   */
  query: (domainId, query, includeTrace = false) =>
    fetchAPI(`/query`, {
      method: 'POST',
      body: JSON.stringify({
        query,
        domain: domainId,
        include_trace: includeTrace,
      }),
    }),
};

/**
 * Admin API
 */
export const adminAPI = {
  /**
   * List all domains (admin view)
   */
  listAllDomains: () => fetchAPI('/admin/domains'),

  /**
   * Get domain config
   */
  getDomainConfig: (domainId) => fetchAPI(`/admin/domains/${domainId}`),

  /**
   * Create domain
   */
  createDomain: (domain) =>
    fetchAPI('/admin/domains', {
      method: 'POST',
      body: JSON.stringify(domain),
    }),

  /**
   * Update domain
   */
  updateDomain: (domainId, updates) =>
    fetchAPI(`/admin/domains/${domainId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),

  /**
   * Delete domain
   */
  deleteDomain: (domainId) =>
    fetchAPI(`/admin/domains/${domainId}`, { method: 'DELETE' }),

  /**
   * List all candidates
   */
  listCandidates: (domain = null, status = null, limit = 100) => {
    const params = new URLSearchParams({ limit });
    if (domain) params.append('domain', domain);
    if (status) params.append('status', status);
    return fetchAPI(`/admin/candidates?${params}`);
  },

  /**
   * Get candidate details
   */
  getCandidate: (domainId, patternId) =>
    fetchAPI(`/admin/candidates/${domainId}/${patternId}`),

  /**
   * Promote candidate
   */
  promoteCandidate: (domainId, patternId, reviewedBy = 'admin', reviewNotes = null) =>
    fetchAPI(`/admin/candidates/${domainId}/${patternId}/promote`, {
      method: 'POST',
      body: JSON.stringify({
        reviewed_by: reviewedBy,
        review_notes: reviewNotes,
      }),
    }),

  /**
   * Reject candidate
   */
  rejectCandidate: (domainId, patternId) =>
    fetchAPI(`/admin/candidates/${domainId}/${patternId}`, { method: 'DELETE' }),

  /**
   * Update pattern
   */
  updatePattern: (domainId, patternId, updates) =>
    fetchAPI(`/admin/domains/${domainId}/patterns/${patternId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),

  /**
   * Delete pattern
   */
  deletePattern: (domainId, patternId) =>
    fetchAPI(`/admin/domains/${domainId}/patterns/${patternId}`, { method: 'DELETE' }),
};

export default {
  system: systemAPI,
  assist: assistAPI,
  knowledge: knowledgeAPI,
  alerts: alertsAPI,
  history: historyAPI,
  traces: traceAPI,
  patterns: patternAPI,
  ingestion: ingestionAPI,
  graph: graphAPI,
  universes: universeAPI,
  domains: domainsAPI,
  admin: adminAPI,
};
