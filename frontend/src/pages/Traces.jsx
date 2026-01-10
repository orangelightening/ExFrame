import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock, ChevronRight, Activity, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { traceAPI } from '../services/api';

function Card({ children, className = '' }) {
  return (
    <div className={`rounded-lg bg-gray-800 border border-gray-700 p-4 ${className}`}>
      {children}
    </div>
  );
}

function EventRow({ event, index }) {
  const getEventIcon = () => {
    switch (event.event_type) {
      case 'enter':
        return <Activity className="h-4 w-4 text-blue-400" />;
      case 'decision':
        return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case 'result':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-400" />;
      default:
        return <ChevronRight className="h-4 w-4 text-gray-400" />;
    }
  };

  const formatData = (data) => {
    if (typeof data === 'object') {
      return Object.entries(data).map(([key, value]) => (
        <div key={key} className="ml-4 text-xs text-gray-400">
          <span className="text-gray-500">{key}:</span>{' '}
          <span className={typeof value === 'boolean' ? (value ? 'text-green-400' : 'text-red-400') : 'text-gray-300'}>
            {typeof value === 'boolean' ? (value ? 'true' : 'false') : String(value)}
          </span>
        </div>
      ));
    }
    return String(data);
  };

  return (
    <div className="flex items-start gap-3 py-2 border-b border-gray-700/50 last:border-0">
      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center text-xs font-mono text-gray-400">
        {index + 1}
      </div>
      <div className="flex-shrink-0 mt-0.5">
        {getEventIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-200">{event.stage}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            event.event_type === 'enter' ? 'bg-blue-900/50 text-blue-300' :
            event.event_type === 'decision' ? 'bg-yellow-900/50 text-yellow-300' :
            event.event_type === 'result' ? 'bg-green-900/50 text-green-300' :
            event.event_type === 'error' ? 'bg-red-900/50 text-red-300' :
            'bg-gray-700 text-gray-300'
          }`}>
            {event.event_type}
          </span>
          {event.duration_ms !== null && (
            <span className="text-xs text-gray-500">
              {event.duration_ms?.toFixed(1)}ms
            </span>
          )}
        </div>
        {event.data && Object.keys(event.data).length > 0 && (
          <div className="mt-1">
            {formatData(event.data)}
          </div>
        )}
        <div className="text-xs text-gray-600 mt-1">
          {new Date(event.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

function TraceDetail({ trace, onClose }) {
  const { data: mermaid, isLoading: mermaidLoading } = useQuery({
    queryKey: ['trace-mermaid', trace.query_id],
    queryFn: () => traceAPI.getTraceMermaid(trace.query_id),
    enabled: !!trace.query_id,
  });

  const confidencePercent = trace.final_result?.confidence
    ? Math.round(trace.final_result.confidence * 100)
    : 0;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div>
            <h2 className="text-lg font-semibold text-white">Execution Trace</h2>
            <p className="text-sm text-gray-400 mt-1">{trace.query}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <XCircle className="h-6 w-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {/* Summary */}
          <Card className="mb-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-xs text-gray-500">Total Duration</div>
                <div className="text-lg font-semibold text-white">
                  {trace.total_duration_ms?.toFixed(0)}ms
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Events</div>
                <div className="text-lg font-semibold text-white">
                  {trace.events?.length || 0}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Context</div>
                <div className="text-lg font-semibold text-white">
                  {trace.final_result?.context_used || 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Confidence</div>
                <div className={`text-lg font-semibold ${
                  confidencePercent >= 80 ? 'text-green-400' :
                  confidencePercent >= 60 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {confidencePercent}%
                </div>
              </div>
            </div>
          </Card>

          {/* Mermaid Diagram */}
          {mermaid && (
            <Card className="mb-4">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Execution Flow</h3>
              <pre className="text-xs text-gray-400 overflow-x-auto bg-gray-950 p-3 rounded">
                {mermaid.mermaid}
              </pre>
            </Card>
          )}

          {/* Events Timeline */}
          <Card>
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Decision Points</h3>
            <div className="space-y-0">
              {trace.events?.map((event, index) => (
                <EventRow key={index} event={event} index={index} />
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Traces() {
  const [selectedTrace, setSelectedTrace] = useState(null);

  const { data: tracesData, isLoading, error } = useQuery({
    queryKey: ['traces'],
    queryFn: () => traceAPI.listTraces(50),
    refetchInterval: 10000,
  });

  const traces = tracesData?.traces || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading traces...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-400">Error loading traces: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Execution Traces</h1>
        <p className="text-gray-400 mt-1">
          View detailed execution paths and decision points from AI queries
        </p>
      </div>

      {traces.length === 0 ? (
        <Card>
          <div className="text-center py-8">
            <Activity className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No traces available yet.</p>
            <p className="text-sm text-gray-500 mt-1">
              Run a query in the AI Assistant to generate traces.
            </p>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-700">
                  <th className="pb-3 font-medium">Query</th>
                  <th className="pb-3 font-medium">Context</th>
                  <th className="pb-3 font-medium">Confidence</th>
                  <th className="pb-3 font-medium">Duration</th>
                  <th className="pb-3 font-medium">Events</th>
                  <th className="pb-3 font-medium">Time</th>
                  <th className="pb-3 font-medium"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/50">
                {traces.map((trace) => {
                  const confidencePercent = trace.confidence ? Math.round(trace.confidence * 100) : 0;
                  return (
                    <tr key={trace.query_id} className="text-sm">
                      <td className="py-3">
                        <div className="max-w-md truncate text-gray-200">
                          {trace.query}
                        </div>
                      </td>
                      <td className="py-3">
                        <span className="px-2 py-1 rounded-full bg-primary-100 text-primary-800 text-xs font-medium">
                          {trace.context_used || 'N/A'}
                        </span>
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                confidencePercent >= 80 ? 'bg-green-500' :
                                confidencePercent >= 60 ? 'bg-yellow-500' :
                                'bg-red-500'
                              }`}
                              style={{ width: `${confidencePercent}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-400">{confidencePercent}%</span>
                        </div>
                      </td>
                      <td className="py-3 text-gray-400">
                        {trace.total_duration_ms?.toFixed(0)}ms
                      </td>
                      <td className="py-3 text-gray-400">
                        {trace.event_count}
                      </td>
                      <td className="py-3 text-gray-400 text-xs">
                        {new Date(trace.start_time).toLocaleString()}
                      </td>
                      <td className="py-3 text-right">
                        <button
                          onClick={() => setSelectedTrace(trace)}
                          className="text-primary-400 hover:text-primary-300 text-sm font-medium"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {selectedTrace && (
        <TraceDetail
          trace={selectedTrace}
          onClose={() => setSelectedTrace(null)}
        />
      )}
    </div>
  );
}

export default Traces;
