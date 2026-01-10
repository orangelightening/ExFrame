import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useState } from 'react';

function PatternDetail() {
  const { patternId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: pattern, isLoading } = useQuery({
    queryKey: ['pattern', patternId],
    queryFn: () => api.patterns.getPattern(patternId),
    enabled: !!patternId,
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.patterns.deletePattern(patternId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patterns'] });
      queryClient.invalidateQueries({ queryKey: ['domains'] });
      navigate('/patterns');
    },
    onError: (error) => {
      alert(`Failed to delete pattern: ${error.message}`);
    },
  });

  const handleDelete = () => {
    deleteMutation.mutate();
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (!pattern) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Pattern not found</p>
        <Link to="/patterns" className="text-blue-600 hover:underline">
          Back to patterns
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <Link to="/patterns" className="text-blue-600 hover:underline">
          ← Back to patterns
        </Link>
        <button
          onClick={() => setShowDeleteConfirm(true)}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          disabled={deleteMutation.isPending}
        >
          {deleteMutation.isPending ? 'Deleting...' : 'Delete Pattern'}
        </button>
      </div>

      {showDeleteConfirm && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 mb-4">
            Are you sure you want to delete "{pattern.name}"? This action cannot be undone.
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              disabled={deleteMutation.isPending}
            >
              Yes, delete it
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
              disabled={deleteMutation.isPending}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
              {pattern.pattern_type}
            </span>
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
              {pattern.domain}
            </span>
          </div>
          <h2 className="text-2xl font-bold">{pattern.name}</h2>
        </div>

        <div className="p-6 space-y-6">
          {pattern.description && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700">{pattern.description}</p>
            </div>
          )}

          {pattern.problem && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Problem</h3>
              <p className="text-gray-700">{pattern.problem}</p>
            </div>
          )}

          {pattern.solution && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Solution</h3>
              <p className="text-gray-700">{pattern.solution}</p>
            </div>
          )}

          {pattern.steps?.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Steps</h3>
              <ol className="list-decimal list-inside space-y-2">
                {pattern.steps.map((step, i) => (
                  <li key={i} className="text-gray-700">
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {pattern.tags?.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {pattern.tags.map((tag) => (
                  <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {pattern.sources?.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Sources</h3>
              <ul className="list-disc list-inside">
                {pattern.sources.map((source, i) => (
                  <li key={i} className="text-gray-700">
                    <a href={source} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      {source}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="pt-4 border-t text-sm text-gray-500">
            Confidence: {Math.round((pattern.confidence || 0) * 100)}%
          </div>
        </div>
      </div>
    </div>
  );
}

export default PatternDetail;
