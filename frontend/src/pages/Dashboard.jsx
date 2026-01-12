import { useQuery } from '@tanstack/react-query';
import { domainsAPI } from '../services/api';
import { Link } from 'react-router-dom';

function Dashboard() {
  const { data: domainsData } = useQuery({
    queryKey: ['domains'],
    queryFn: () => domainsAPI.listDomains(),
  });

  // Get pattern counts from the universe API
  const { data: universeData } = useQuery({
    queryKey: ['universes'],
    queryFn: () => fetch('/api/universes').then(r => r.json()),
  });

  const totalPatterns = universeData?.universes?.[0]?.total_patterns || 0;
  const domainCount = universeData?.universes?.[0]?.domain_count || 0;
  const domains = domainsData?.domains || [];

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="text-3xl font-bold text-blue-400">{domainCount}</div>
          <div className="text-gray-400 mt-1">Domains</div>
        </div>
        <div className="card">
          <div className="text-3xl font-bold text-green-400">{totalPatterns}</div>
          <div className="text-gray-400 mt-1">Total Patterns</div>
        </div>
        <div className="card">
          <div className="text-3xl font-bold text-purple-400">0</div>
          <div className="text-gray-400 mt-1">Universal Patterns</div>
        </div>
      </div>

      {/* Domains */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Domains</h3>
        {domains.length === 0 ? (
          <p className="text-gray-400">No domains configured yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {domains.map((domain) => (
              <Link
                key={domain}
                to={`/patterns?domain=${domain}`}
                className="block p-4 rounded-lg bg-gray-700/50 border border-gray-600 hover:border-primary-500 hover:bg-gray-700 transition"
              >
                <h4 className="font-semibold text-lg text-gray-100">{domain}</h4>
                <p className="text-gray-400">View patterns</p>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-100 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Link
            to="/ingestion"
            className="flex items-center p-4 rounded-lg bg-gray-700/50 border border-gray-600 hover:bg-gray-700 transition"
          >
            <span className="text-2xl mr-3">📥</span>
            <div>
              <div className="font-semibold text-gray-100">Ingest Content</div>
              <div className="text-sm text-gray-400">Add patterns from URLs or text</div>
            </div>
          </Link>
          <Link
            to="/domains"
            className="flex items-center p-4 rounded-lg bg-gray-700/50 border border-gray-600 hover:bg-gray-700 transition"
          >
            <span className="text-2xl mr-3">🔍</span>
            <div>
              <div className="font-semibold text-gray-100">Explore Domains</div>
              <div className="text-sm text-gray-400">Browse patterns by domain</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
