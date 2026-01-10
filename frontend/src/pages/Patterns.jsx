import { useQuery } from '@tanstack/react-query';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../services/api';

function Patterns() {
  const [searchParams] = useSearchParams();
  const domain = searchParams.get('domain') || 'cooking';

  const { data: patternsData, isLoading } = useQuery({
    queryKey: ['patterns', domain],
    queryFn: () => api.patterns.listPatterns(domain),
  });

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Patterns</h2>
          <p className="text-gray-600 mt-1">
            {domain ? `Patterns from ${domain}` : 'All patterns'}
          </p>
        </div>
        <Link
          to="/patterns/new"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Create Pattern
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Loading...</div>
      ) : patternsData?.patterns?.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No patterns found.</p>
          <Link to="/ingestion" className="text-blue-600 hover:underline">
            Ingest some content to get started
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <span className="text-gray-600">
              {patternsData?.count || 0} patterns
            </span>
          </div>
          <div className="divide-y">
            {patternsData?.patterns?.map((pattern) => (
              <Link
                key={pattern.id}
                to={`/patterns/${pattern.id}`}
                className="block px-6 py-4 hover:bg-gray-50 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{pattern.name}</h4>
                    <p className="text-gray-600 text-sm mt-1">{pattern.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {pattern.type}
                      </span>
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {domain}
                      </span>
                      {pattern.tags?.slice(0, 3).map((tag) => (
                        <span key={tag} className="text-xs text-gray-500">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-gray-400">→</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Patterns;
