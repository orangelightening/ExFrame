import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { Link } from 'react-router-dom';

function Dashboard() {
  const { data: domains } = useQuery({
    queryKey: ['domains'],
    queryFn: () => api.getDomains(),
  });

  const totalPatterns = domains?.domains?.reduce((sum, d) => sum + d.pattern_count, 0) || 0;

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">Overview of the expertise scanner system</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-blue-600">{domains?.domains?.length || 0}</div>
          <div className="text-gray-600 mt-1">Domains</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-green-600">{totalPatterns}</div>
          <div className="text-gray-600 mt-1">Total Patterns</div>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-purple-600">0</div>
          <div className="text-gray-600 mt-1">Universal Patterns</div>
        </div>
      </div>

      {/* Domains */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Domains</h3>
        </div>
        <div className="p-6">
          {domains?.domains?.length === 0 ? (
            <p className="text-gray-500">No domains configured yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {domains?.domains?.map((domain) => (
                <Link
                  key={domain.id}
                  to={`/patterns?domain=${domain.id}`}
                  className="block p-4 border rounded-lg hover:border-blue-500 hover:shadow-md transition"
                >
                  <h4 className="font-semibold text-lg">{domain.name}</h4>
                  <p className="text-gray-600">{domain.pattern_count} patterns</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Quick Actions</h3>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            to="/ingestion"
            className="flex items-center p-4 border rounded-lg hover:bg-blue-50 transition"
          >
            <span className="text-2xl mr-3">📥</span>
            <div>
              <div className="font-semibold">Ingest Content</div>
              <div className="text-sm text-gray-600">Add patterns from URLs or text</div>
            </div>
          </Link>
          <Link
            to="/domains"
            className="flex items-center p-4 border rounded-lg hover:bg-purple-50 transition"
          >
            <span className="text-2xl mr-3">🔍</span>
            <div>
              <div className="font-semibold">Explore Domains</div>
              <div className="text-sm text-gray-600">Browse patterns by domain</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
