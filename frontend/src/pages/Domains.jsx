import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { Link } from 'react-router-dom';

function Domains() {
  const { data: domains, isLoading } = useQuery({
    queryKey: ['domains'],
    queryFn: () => api.getDomains(),
  });

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Domains</h2>
        <p className="text-gray-600 mt-1">Browse expertise by domain</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {domains?.domains?.map((domain) => (
          <Link
            key={domain.id}
            to={`/patterns?domain=${domain.id}`}
            className="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">{domain.name}</h3>
              <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-800">
                Active
              </span>
            </div>
            <div className="text-gray-600">
              {domain.pattern_count} patterns
            </div>
          </Link>
        ))}
      </div>

      {domains?.domains?.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No domains configured yet.</p>
          <Link to="/ingestion" className="text-blue-600 hover:underline">
            Start by ingesting some content
          </Link>
        </div>
      )}
    </div>
  );
}

export default Domains;
