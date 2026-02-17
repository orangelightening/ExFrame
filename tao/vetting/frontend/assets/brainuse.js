/**
 * BrainUse Dashboard - Alpine.js Application
 */

function brainuseApp() {
    return {
        // State
        loading: false,
        creating: false,
        candidates: [],
        filteredCandidates: [],
        selectedCandidate: null,
        availableDomains: [],
        availableRoles: [],
        companies: [],

        // UI State
        showCreateModal: false,
        showDetailModal: false,
        showReportModal: false,

        // Filters
        searchQuery: '',
        statusFilter: 'all',
        companyFilter: 'all',

        // Stats
        stats: {
            total: 0,
            pending: 0,
            in_progress: 0,
            completed: 0,
            hired: 0,
            rejected: 0
        },

        // New Candidate Form
        newCandidate: {
            name: '',
            email: '',
            role: '',
            company: '',
            assessment_domains: [],
            recruiter_notes: ''
        },

        // Toast Notification
        toast: {
            show: false,
            type: 'info',
            message: ''
        },

        // Report Data
        reportData: null,

        /**
         * Initialize the application
         */
        async init() {
            console.log('BrainUse Dashboard initializing...');
            await this.loadInitialData();
        },

        /**
         * Load all initial data
         */
        async loadInitialData() {
            await Promise.all([
                this.loadCandidates(),
                this.loadDomains(),
                this.loadRoles()
            ]);
        },

        /**
         * Load candidates from API
         */
        async loadCandidates() {
            try {
                this.loading = true;
                const response = await fetch('/api/brainuse/candidates');

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                this.candidates = await response.json();
                this.filterCandidates();
                this.updateStats();
                this.extractCompanies();

                console.log(`Loaded ${this.candidates.length} candidates`);
            } catch (error) {
                console.error('Error loading candidates:', error);
                this.showToast('error', 'Failed to load candidates');
            } finally {
                this.loading = false;
            }
        },

        /**
         * Load available assessment domains
         */
        async loadDomains() {
            try {
                const response = await fetch('/api/brainuse/assessment-domains');

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                this.availableDomains = await response.json();
                console.log(`Loaded ${this.availableDomains.length} assessment domains`);
            } catch (error) {
                console.error('Error loading domains:', error);
                this.showToast('error', 'Failed to load assessment domains');
            }
        },

        /**
         * Load available roles (benchmarks)
         */
        async loadRoles() {
            try {
                const response = await fetch('/api/brainuse/benchmarks');

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                this.availableRoles = await response.json();
                console.log(`Loaded ${this.availableRoles.length} roles`);
            } catch (error) {
                console.error('Error loading roles:', error);
                this.showToast('error', 'Failed to load roles');
            }
        },

        /**
         * Filter candidates based on search and filters
         */
        filterCandidates() {
            let filtered = this.candidates;

            // Search filter
            if (this.searchQuery.trim()) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(c =>
                    c.name.toLowerCase().includes(query) ||
                    c.email.toLowerCase().includes(query) ||
                    c.company.toLowerCase().includes(query)
                );
            }

            // Status filter
            if (this.statusFilter !== 'all') {
                filtered = filtered.filter(c => c.status === this.statusFilter);
            }

            // Company filter
            if (this.companyFilter !== 'all') {
                filtered = filtered.filter(c => c.company === this.companyFilter);
            }

            this.filteredCandidates = filtered;
        },

        /**
         * Update statistics
         */
        updateStats() {
            this.stats = {
                total: this.candidates.length,
                pending: this.candidates.filter(c => c.status === 'pending').length,
                in_progress: this.candidates.filter(c => c.status === 'in_progress').length,
                completed: this.candidates.filter(c => c.status === 'completed').length,
                hired: this.candidates.filter(c => c.status === 'hired').length,
                rejected: this.candidates.filter(c => c.status === 'rejected').length
            };
        },

        /**
         * Extract unique companies
         */
        extractCompanies() {
            const companySet = new Set(this.candidates.map(c => c.company));
            this.companies = Array.from(companySet).sort();
        },

        /**
         * Create new candidate
         */
        async createCandidate() {
            try {
                // Validate
                if (!this.newCandidate.name.trim()) {
                    this.showToast('error', 'Name is required');
                    return;
                }
                if (!this.newCandidate.email.trim()) {
                    this.showToast('error', 'Email is required');
                    return;
                }
                if (!this.newCandidate.role) {
                    this.showToast('error', 'Role is required');
                    return;
                }
                if (!this.newCandidate.company.trim()) {
                    this.showToast('error', 'Company is required');
                    return;
                }
                if (this.newCandidate.assessment_domains.length < 3) {
                    this.showToast('error', 'Please select at least 3 assessment domains');
                    return;
                }

                this.creating = true;

                // Check if updating existing candidate
                const isUpdate = !!this.newCandidate.candidate_id;
                const url = isUpdate
                    ? `/api/brainuse/candidates/${this.newCandidate.candidate_id}`
                    : '/api/brainuse/candidates';
                const method = isUpdate ? 'PUT' : 'POST';

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.newCandidate)
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || `Failed to ${isUpdate ? 'update' : 'create'} candidate`);
                }

                const candidate = await response.json();

                // Reload all candidates to get fresh data
                await this.loadCandidates();

                // Reset form
                this.resetNewCandidateForm();

                // Close modal
                this.showCreateModal = false;

                // Show success
                this.showToast('success', `Candidate ${candidate.name} ${isUpdate ? 'updated' : 'created'} successfully`);

                console.log(`${isUpdate ? 'Updated' : 'Created'} candidate:`, candidate.candidate_id);
            } catch (error) {
                console.error('Error saving candidate:', error);
                this.showToast('error', error.message || 'Failed to save candidate');
            } finally {
                this.creating = false;
            }
        },

        /**
         * Reset new candidate form
         */
        resetNewCandidateForm() {
            this.newCandidate = {
                name: '',
                email: '',
                role: '',
                company: '',
                assessment_domains: [],
                recruiter_notes: ''
            };
        },

        /**
         * Select a candidate for detail view
         */
        selectCandidate(candidate) {
            this.selectedCandidate = candidate;
            this.showDetailModal = true;
        },

        /**
         * Record consent for candidate
         */
        async recordConsent(candidateId, consentGiven) {
            try {
                const response = await fetch(`/api/brainuse/candidates/${candidateId}/consent`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        candidate_id: candidateId,
                        consent_given: consentGiven
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to record consent');
                }

                // Reload candidates
                await this.loadCandidates();
                this.selectedCandidate = this.candidates.find(c => c.candidate_id === candidateId);

                this.showToast('success', consentGiven ? 'Consent recorded' : 'Consent revoked');
            } catch (error) {
                console.error('Error recording consent:', error);
                this.showToast('error', error.message || 'Failed to record consent');
                // Revert checkbox
                this.selectedCandidate.consent_given = !consentGiven;
            }
        },

        /**
         * Edit candidate
         */
        editCandidate(candidate) {
            // Pre-fill form with candidate data
            this.newCandidate = {
                candidate_id: candidate.candidate_id, // Include ID for update
                name: candidate.name,
                email: candidate.email,
                role: candidate.role,
                company: candidate.company,
                assessment_domains: [...candidate.assessment_domains],
                recruiter_notes: candidate.recruiter_notes || ''
            };

            // Close detail modal, open create modal
            this.showDetailModal = false;
            this.showCreateModal = true;
        },

        /**
         * Delete candidate
         */
        async deleteCandidate(candidateId) {
            if (!confirm('Are you sure you want to delete this candidate? This action cannot be undone.')) {
                return;
            }

            try {
                const response = await fetch(`/api/brainuse/candidates/${candidateId}`, {
                    method: 'DELETE'
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to delete candidate');
                }

                await this.loadCandidates();
                this.showDetailModal = false;
                this.showToast('success', 'Candidate deleted successfully');
            } catch (error) {
                console.error('Error deleting candidate:', error);
                this.showToast('error', error.message || 'Failed to delete candidate');
            }
        },

        /**
         * Start assessment for candidate
         */
        async startAssessment(candidateId) {
            try {
                // Start assessment (consent should already be recorded)
                const response = await fetch(`/api/brainuse/candidates/${candidateId}/start`, {
                    method: 'POST'
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to start assessment');
                }

                // Reload candidates to get updated status
                await this.loadCandidates();

                // Update selected candidate
                this.selectedCandidate = this.candidates.find(c => c.candidate_id === candidateId);

                this.showToast('success', 'Assessment started successfully');

                console.log('Started assessment for:', candidateId);
            } catch (error) {
                console.error('Error starting assessment:', error);
                this.showToast('error', error.message || 'Failed to start assessment');
            }
        },

        /**
         * Complete assessment for candidate
         */
        async completeAssessment(candidateId) {
            try {
                const response = await fetch(`/api/brainuse/candidates/${candidateId}/complete`, {
                    method: 'POST'
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to complete assessment');
                }

                const assessment = await response.json();

                // Reload candidates
                await this.loadCandidates();

                // Update selected candidate
                this.selectedCandidate = this.candidates.find(c => c.candidate_id === candidateId);

                this.showToast('success', `Assessment completed. Tao Index: ${assessment.tao_index.toFixed(1)}`);

                console.log('Completed assessment:', assessment);
            } catch (error) {
                console.error('Error completing assessment:', error);
                this.showToast('error', error.message || 'Failed to complete assessment');
            }
        },

        /**
         * View report for candidate
         */
        async viewReport(candidateId) {
            try {
                const response = await fetch(`/api/brainuse/candidates/${candidateId}/report`);

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Failed to load report');
                }

                this.reportData = await response.json();
                this.showReportModal = true;
                this.showDetailModal = false;

                console.log('Loaded report:', this.reportData);

                // Open report in new window/tab (for now, just log)
                // In production, navigate to report viewer page
                window.location.href = `/brainuse/report/${candidateId}`;
            } catch (error) {
                console.error('Error loading report:', error);
                this.showToast('error', error.message || 'Failed to load report');
            }
        },

        /**
         * Refresh candidates
         */
        async refreshCandidates() {
            await this.loadCandidates();
            this.showToast('info', 'Candidates refreshed');
        },

        /**
         * Show toast notification
         */
        showToast(type, message) {
            this.toast = {
                show: true,
                type: type,
                message: message
            };

            // Auto-hide after 3 seconds
            setTimeout(() => {
                this.toast.show = false;
            }, 3000);
        },

        /**
         * Format status for display
         */
        formatStatus(status) {
            const statusMap = {
                'pending': 'Pending',
                'in_progress': 'In Progress',
                'completed': 'Completed',
                'hired': 'Hired',
                'rejected': 'Rejected'
            };
            return statusMap[status] || status;
        },

        /**
         * Format domain name for display
         */
        formatDomain(domain) {
            return domain
                .replace('_assessment', '')
                .replace(/_/g, ' ')
                .split(' ')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
        },

        /**
         * Format date (short format)
         */
        formatDate(dateString) {
            if (!dateString) return '-';

            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

            if (diffDays === 0) return 'Today';
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${diffDays} days ago`;

            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        },

        /**
         * Format date and time (full format)
         */
        formatDateTime(dateString) {
            if (!dateString) return '-';

            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        }
    };
}
