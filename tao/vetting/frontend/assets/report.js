/**
 * BrainUse Report Viewer - Alpine.js Application
 */

function reportApp() {
    return {
        // State
        loading: true,
        error: null,
        candidateId: null,
        candidate: null,
        assessment: null,
        report: null,

        /**
         * Initialize the report
         */
        async init() {
            console.log('Report viewer initializing...');

            // Extract candidate ID from URL
            this.candidateId = this.getCandidateIdFromUrl();

            if (!this.candidateId) {
                this.error = 'No candidate ID provided';
                this.loading = false;
                return;
            }

            await this.loadReport();
        },

        /**
         * Extract candidate ID from URL
         */
        getCandidateIdFromUrl() {
            // URL format: /brainuse/report/{candidate_id}
            const path = window.location.pathname;
            const match = path.match(/\/brainuse\/report\/([^\/]+)/);
            return match ? match[1] : null;
        },

        /**
         * Load report data from API
         */
        async loadReport() {
            try {
                this.loading = true;
                this.error = null;

                // Load candidate details
                const candidateResponse = await fetch(`/api/brainuse/candidates/${this.candidateId}`);
                if (!candidateResponse.ok) {
                    throw new Error(`Failed to load candidate (HTTP ${candidateResponse.status})`);
                }
                this.candidate = await candidateResponse.json();

                // Load report
                const reportResponse = await fetch(`/api/brainuse/candidates/${this.candidateId}/report`);
                if (!reportResponse.ok) {
                    const errorData = await reportResponse.json().catch(() => ({}));
                    throw new Error(errorData.detail || `Failed to load report (HTTP ${reportResponse.status})`);
                }
                const data = await reportResponse.json();

                this.report = data;
                this.assessment = {
                    tao_index: data.tao_index || 0,
                    percentile: data.percentile || 0,
                    learning_velocity: data.learning_velocity || 0,
                    avg_sophistication: data.avg_sophistication || 0,
                    chain_depth: data.chain_depth || 0,
                    interest_ratio: data.interest_ratio || 0,
                    domain_scores: data.domain_scores || {},
                    total_queries: data.total_queries || 0,
                    total_sessions: data.total_sessions || 0,
                    total_time_minutes: data.total_time_minutes || 0
                };

                console.log('Report loaded successfully:', this.report);

                // Set page title
                document.title = `Assessment Report - ${this.candidate.name} - BrainUse`;

            } catch (error) {
                console.error('Error loading report:', error);
                this.error = error.message || 'Failed to load report';
            } finally {
                this.loading = false;
            }
        },

        /**
         * Format recommendation for display
         */
        formatRecommendation(recommendation) {
            const recMap = {
                'hire': 'Strong Hire',
                'maybe': 'Maybe',
                'pass': 'Pass'
            };
            return recMap[recommendation] || recommendation;
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
         * Download report as PDF
         */
        async downloadPDF() {
            try {
                // For now, just trigger print dialog
                // In production, would generate PDF server-side
                window.print();

                // TODO: Implement server-side PDF generation
                // const response = await fetch(`/api/brainuse/candidates/${this.candidateId}/report/pdf`);
                // if (!response.ok) throw new Error('Failed to generate PDF');
                // const blob = await response.blob();
                // const url = window.URL.createObjectURL(blob);
                // const a = document.createElement('a');
                // a.href = url;
                // a.download = `assessment-report-${this.candidate.name.replace(/\s+/g, '-')}.pdf`;
                // document.body.appendChild(a);
                // a.click();
                // window.URL.revokeObjectURL(url);
                // document.body.removeChild(a);

            } catch (error) {
                console.error('Error downloading PDF:', error);
                alert('Failed to download PDF. Please use Print instead.');
            }
        },

        /**
         * Get percentile label
         */
        getPercentileLabel(percentile) {
            if (percentile >= 90) return 'Exceptional (Top 10%)';
            if (percentile >= 75) return 'Strong (Top 25%)';
            if (percentile >= 50) return 'Above Average';
            return 'Below Average';
        },

        /**
         * Get metric color class
         */
        getMetricColor(value, max, thresholds) {
            const percentage = (value / max) * 100;
            if (percentage >= thresholds.high) return 'text-emerald-400';
            if (percentage >= thresholds.medium) return 'text-yellow-400';
            return 'text-red-400';
        }
    };
}
