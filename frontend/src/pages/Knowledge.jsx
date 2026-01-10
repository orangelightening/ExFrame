import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { knowledgeAPI } from '../services/api';
import {
  Search,
  FolderOpen,
  FileText,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import { Loading, ErrorMessage, EmptyState, Card } from '../components/UI';

/**
 * Knowledge Base browser page
 */
export default function KnowledgeBase() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const { data: patternsData, isLoading, error } = useQuery({
    queryKey: ['knowledge-patterns'],
    queryFn: () => knowledgeAPI.getPatterns(),
  });

  const patterns = patternsData?.patterns || [];

  // Filter patterns
  const filteredPatterns = patterns.filter((pattern) => {
    const matchesSearch =
      !searchQuery ||
      pattern.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pattern.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pattern.symptoms?.some((s) =>
        s.toLowerCase().includes(searchQuery.toLowerCase())
      );

    const matchesCategory =
      selectedCategory === 'all' || pattern.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // Get unique categories
  const categories = ['all', ...new Set(patterns.map((p) => p.category))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-100">Knowledge Base</h2>
        <p className="mt-1 text-gray-400">
          Browse {patterns.length} curated OMV issue/solution patterns
        </p>
      </div>

      {/* Search and filters */}
      <Card>
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search patterns by keyword, symptom, or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Category filter */}
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                  selectedCategory === category
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {category === 'all' ? 'All Categories' : category}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Results */}
      {isLoading ? (
        <Loading text="Loading knowledge base..." />
      ) : error ? (
        <ErrorMessage error={error} />
      ) : filteredPatterns.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No patterns found"
          description="Try adjusting your search or filter criteria"
        />
      ) : (
        <div>
          <p className="mb-4 text-sm text-gray-400">
            Found {filteredPatterns.length} pattern
            {filteredPatterns.length !== 1 ? 's' : ''}
          </p>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {filteredPatterns.map((pattern) => (
              <PatternCard key={pattern.id} pattern={pattern} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Individual pattern card
 */
function PatternCard({ pattern }) {
  const [expanded, setExpanded] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  return (
    <Card className="h-full">
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-primary-400">
                {pattern.id}
              </span>
              <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-800">
                {pattern.category}
              </span>
            </div>
            <h3 className="mt-2 text-lg font-semibold text-gray-100">
              {pattern.title}
            </h3>
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => setShowRaw(!showRaw)}
              className="rounded p-1 text-gray-400 hover:bg-gray-700 hover:text-gray-100"
              title={showRaw ? 'Hide raw data' : 'View raw JSON'}
            >
              <FileText className="h-4 w-4" />
            </button>
            <button
              onClick={() => setExpanded(!expanded)}
              className="rounded p-1 text-gray-400 hover:bg-gray-700 hover:text-gray-100"
              title={expanded ? 'Collapse' : 'Expand'}
            >
              <FolderOpen className={`h-5 w-5 ${expanded ? 'rotate-180' : ''} transition-transform`} />
            </button>
          </div>
        </div>

        {/* Raw JSON Data */}
        {showRaw && (
          <div className="overflow-x-auto">
            <pre className="rounded bg-gray-900 p-3 text-xs text-gray-300">
              {JSON.stringify(pattern, null, 2)}
            </pre>
          </div>
        )}

        {/* Triggers */}
        {expanded && pattern.triggers && pattern.triggers.length > 0 && (
          <div>
            <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
              Search Triggers
            </h4>
            <div className="flex flex-wrap gap-1">
              {pattern.triggers.map((trigger, idx) => (
                <span
                  key={idx}
                  className="rounded bg-gray-700 px-2 py-1 text-xs text-gray-300"
                >
                  {trigger}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Symptoms */}
        {pattern.symptoms && pattern.symptoms.length > 0 && (
          <div>
            <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
              Symptoms
            </h4>
            <ul className="space-y-1">
              {pattern.symptoms.slice(0, expanded ? undefined : 2).map(
                (symptom, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-2 text-sm text-gray-300"
                  >
                    <AlertTriangle className="h-4 w-4 shrink-0 text-warning-500 mt-0.5" />
                    <span>{symptom}</span>
                  </li>
                )
              )}
            </ul>
            {!expanded && pattern.symptoms.length > 2 && (
              <button
                onClick={() => setExpanded(true)}
                className="mt-2 text-sm text-primary-400 hover:text-primary-300"
              >
                +{pattern.symptoms.length - 2} more symptoms
              </button>
            )}
          </div>
        )}

        {/* Diagnostics */}
        {expanded && pattern.diagnostics && pattern.diagnostics.length > 0 && (
          <div>
            <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
              Diagnostics to Run
            </h4>
            <ul className="space-y-1">
              {pattern.diagnostics.map((diag, idx) => (
                <li
                  key={idx}
                  className="flex gap-2 rounded bg-gray-700/50 p-2 text-sm text-gray-300"
                >
                  <span className="font-mono text-xs text-primary-400">{idx + 1}.</span>
                  <span>{diag}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Solutions */}
        {pattern.solutions && pattern.solutions.length > 0 && (
          <div>
            <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">
              Solutions {expanded && `(${pattern.solutions.length})`}
            </h4>
            <ul className="space-y-2">
              {pattern.solutions.slice(0, expanded ? undefined : 2).map(
                (solution, idx) => (
                  <li
                    key={idx}
                    className="flex gap-3 rounded-lg bg-gray-700/50 p-2"
                  >
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-success-100 text-xs font-semibold text-success-800">
                      {solution.priority}
                    </span>
                    <div className="flex-1 text-sm">
                      <p className="font-medium text-gray-200">
                        {solution.action}
                      </p>
                      {solution.command && (
                        <code className="mt-1 block rounded bg-gray-800 px-2 py-1 text-xs text-gray-400">
                          {solution.command}
                        </code>
                      )}
                    </div>
                  </li>
                )
              )}
            </ul>
            {!expanded && pattern.solutions.length > 2 && (
              <button
                onClick={() => setExpanded(true)}
                className="mt-2 text-sm text-primary-400 hover:text-primary-300"
              >
                +{pattern.solutions.length - 2} more solutions
              </button>
            )}
          </div>
        )}

        {/* Confidence */}
        {pattern.confidence !== undefined && (
          <div className="flex items-center gap-2">
            <CheckCircle
              className={`h-4 w-4 ${
                pattern.confidence >= 0.9
                  ? 'text-success-500'
                  : pattern.confidence >= 0.7
                  ? 'text-warning-500'
                  : 'text-danger-500'
              }`}
            />
            <span className="text-xs text-gray-400">
              Confidence: {Math.round(pattern.confidence * 100)}%
            </span>
          </div>
        )}
      </div>
    </Card>
  );
}
