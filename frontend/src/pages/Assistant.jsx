import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { assistAPI } from '../services/api';
import {
  Send,
  Loader2,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Zap,
} from 'lucide-react';
import { Loading, ErrorMessage, Card } from '../components/UI';

/**
 * AI Assistant page for querying the system
 */
export default function Assistant() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const [passthrough, setPassthrough] = useState(false);

  const queryMutation = useMutation({
    mutationFn: (q) => assistAPI.query(q, undefined, passthrough),
    onSuccess: (data) => {
      setResponse(data);
    },
    onSettled: () => {
      setIsQuerying(false);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isQuerying) return;

    setIsQuerying(true);
    setResponse(null);
    queryMutation.mutate(query);
  };

  const exampleQueries = [
    'My disk is full, what do I do?',
    'SMB share not accessible from Windows',
    'How do I check RAID status?',
    'High CPU usage, what could be causing it?',
    'How do I add a new disk to OMV?',
  ];

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-100">AI Assistant</h2>
        <p className="mt-1 text-gray-400">
          Ask questions about your OMV server and get intelligent guidance
        </p>
      </div>

      {/* Query form */}
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Direct Chat Mode Toggle */}
          <div className="flex items-center justify-between rounded-lg bg-gray-700/50 px-4 py-3">
            <div className="flex items-center gap-3">
              <Zap className={`h-5 w-5 ${passthrough ? 'text-yellow-400' : 'text-gray-500'}`} />
              <div>
                <div className="text-sm font-medium text-gray-200">Direct Chat Mode</div>
                <div className="text-xs text-gray-400">
                  {passthrough
                    ? 'Bypass knowledge base - chat directly with AI'
                    : 'Use knowledge base for OMV-specific assistance'}
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setPassthrough(!passthrough)}
              disabled={isQuerying}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                passthrough ? 'bg-yellow-600' : 'bg-gray-600'
              } ${isQuerying ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  passthrough ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div>
            <label htmlFor="query" className="mb-2 block text-sm font-medium text-gray-300">
              Your Question
            </label>
            <textarea
              id="query"
              rows={3}
              className="input min-h-[100px] resize-none"
              placeholder={passthrough
                ? 'Ask me anything...'
                : 'Ask me anything about your OMV server...'}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isQuerying}
            />
          </div>

          <button
            type="submit"
            disabled={!query.trim() || isQuerying}
            className="btn btn-primary flex items-center gap-2"
          >
            {isQuerying ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Thinking...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Ask Assistant
              </>
            )}
          </button>
        </form>
      </Card>

      {/* Example queries */}
      {!response && !isQuerying && (
        <div>
          <h3 className="mb-3 text-sm font-medium text-gray-400">
            Example questions:
          </h3>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(example)}
                className="rounded-lg bg-gray-800 px-3 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Response */}
      {queryMutation.error && (
        <ErrorMessage
          error={queryMutation.error}
          onRetry={() => queryMutation.mutate(query)}
        />
      )}

      {response && (
        <ResponseDisplay response={response} query={query} />
      )}
    </div>
  );
}

/**
 * Response display component
 */
function ResponseDisplay({ response, query }) {
  const {
    analysis,
    suggested_diagnostics,
    possible_causes,
    recommended_actions,
    explanation,
    follow_up_questions,
    context_used,
    confidence,
    matched_patterns,
    error,
    passthrough_mode,
  } = response;

  const confidencePercent = confidence ? Math.round(confidence * 100) : 50;
  const confidenceColor = confidence >= 0.8 ? 'success' : confidence >= 0.6 ? 'warning' : 'danger';

  return (
    <div className="space-y-4">
      {/* Error display */}
      {error && (
        <Card>
          <div className="flex gap-3 rounded-lg bg-danger-900/30 border border-danger-700 p-4">
            <AlertTriangle className="h-5 w-5 shrink-0 text-danger-500 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-danger-400">AI Error</h3>
              <p className="mt-1 text-sm text-gray-300">{error}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Header with context and confidence */}
      <div className="flex flex-wrap items-center gap-3">
        {passthrough_mode ? (
          <>
            <Zap className="h-4 w-4 text-yellow-400" />
            <span className="rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
              Direct Chat Mode
            </span>
          </>
        ) : (
          <>
            <span className="text-sm text-gray-400">Context:</span>
            <span className="rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-800">
              {context_used}
            </span>

            {confidence !== undefined && (
              <>
                <span className="text-sm text-gray-400 ml-2">Confidence:</span>
                <span className={`rounded-full bg-${confidenceColor}-100 px-2.5 py-0.5 text-xs font-medium text-${confidenceColor}-800`}>
                  {confidencePercent}%
                </span>
              </>
            )}
          </>
        )}
      </div>

      {/* Matched Patterns */}
      {matched_patterns && matched_patterns.length > 0 && (
        <Card title={`Matched Knowledge Patterns (${matched_patterns.length})`}>
          <div className="space-y-2">
            {matched_patterns.map((pattern, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between rounded-lg bg-gray-700/50 px-3 py-2"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-primary-400">
                      {pattern.id}
                    </span>
                    <span className="text-sm font-medium text-gray-200">
                      {pattern.title}
                    </span>
                  </div>
                  <div className="mt-1 flex gap-2 text-xs text-gray-400">
                    <span>Score: {(pattern.score || 0).toFixed(2)}</span>
                    <span>•</span>
                    <span>{pattern.category}</span>
                  </div>
                </div>
                <CheckCircle className={`h-4 w-4 ${pattern.score > 0.7 ? 'text-success-500' : pattern.score > 0.4 ? 'text-warning-500' : 'text-danger-500'}`} />
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Analysis */}
      {analysis && (
        <Card title="Analysis">
          <p className="text-gray-300 whitespace-pre-wrap">{analysis}</p>
        </Card>
      )}

      {/* Suggested Diagnostics */}
      {suggested_diagnostics?.length > 0 && (
        <Card title="Suggested Diagnostics">
          <ul className="space-y-2">
            {suggested_diagnostics.map((diag, idx) => (
              <li key={idx} className="flex gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-100 text-xs font-semibold text-primary-800">
                  {idx + 1}
                </span>
                <span className="text-gray-300">{diag}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Possible Causes */}
      {possible_causes?.length > 0 && (
        <Card title="Possible Causes">
          <ul className="space-y-2">
            {possible_causes.map((cause, idx) => (
              <li key={idx} className="flex gap-3">
                <AlertTriangle className="h-5 w-5 shrink-0 text-warning-500" />
                <span className="text-gray-300">{cause}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Recommended Actions */}
      {recommended_actions?.length > 0 && (
        <Card title="Recommended Actions">
          <ul className="space-y-3">
            {recommended_actions.map((action, idx) => (
              <li
                key={idx}
                className="flex gap-3 rounded-lg bg-gray-700/50 p-3"
              >
                <CheckCircle className="h-5 w-5 shrink-0 text-success-500" />
                <span className="text-sm text-gray-300">{action}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Explanation */}
      {explanation && (
        <Card title="Explanation">
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{explanation}</p>
        </Card>
      )}

      {/* Follow-up Questions */}
      {follow_up_questions?.length > 0 && (
        <Card title="Questions to help resolve this">
          <ul className="space-y-2">
            {follow_up_questions.map((question, idx) => (
              <li key={idx} className="flex gap-3">
                <HelpCircle className="h-5 w-5 shrink-0 text-primary-500" />
                <span className="text-sm text-gray-300">{question}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Feedback actions */}
      <div className="flex items-center justify-between rounded-lg bg-gray-800 px-4 py-3">
        <span className="text-sm text-gray-400">Was this helpful?</span>
        <div className="flex gap-2">
          <button className="btn btn-secondary text-sm">Yes</button>
          <button className="btn btn-secondary text-sm">No</button>
        </div>
      </div>
    </div>
  );
}
