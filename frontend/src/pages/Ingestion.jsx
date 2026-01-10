import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import api from '../services/api';

function Ingestion() {
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [domain, setDomain] = useState('cooking');
  const [activeTab, setActiveTab] = useState('url');
  const [jobId, setJobId] = useState(null);

  const { data: domains } = useQuery({
    queryKey: ['domains'],
    queryFn: () => api.getDomains(),
  });

  const urlMutation = useMutation({
    mutationFn: (data) => api.ingestUrl(data.url, data.domain),
    onSuccess: (data) => {
      setJobId(data.job_id);
      setUrl('');
    },
    onError: (error) => {
      alert(`Error: ${error.message}`);
    },
  });

  const textMutation = useMutation({
    mutationFn: (data) => api.ingestText(data.text, data.domain),
    onSuccess: (data) => {
      setJobId(data.job_id);
      setText('');
    },
    onError: (error) => {
      alert(`Error: ${error.message}`);
    },
  });

  const handleSubmitUrl = (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    urlMutation.mutate({ url, domain });
  };

  const handleSubmitText = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    textMutation.mutate({ text, domain });
  };

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Ingestion</h2>
        <p className="text-gray-600 mt-1">Add patterns from URLs or text</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Ingestion Form */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b">
            <div className="flex">
              <button
                onClick={() => setActiveTab('url')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'url'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                From URL
              </button>
              <button
                onClick={() => setActiveTab('text')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'text'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                From Text
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Domain selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Domain
              </label>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="cooking">Cooking</option>
                <option value="python">Python (coming soon)</option>
                <option value="diy">DIY (coming soon)</option>
                <option value="first_aid">First Aid (coming soon)</option>
                <option value="gardening">Gardening (coming soon)</option>
              </select>
            </div>

            {activeTab === 'url' ? (
              <form onSubmit={handleSubmitUrl}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL
                  </label>
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://www.allrecipes.com/recipe/..."
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={urlMutation.isPending}
                  />
                </div>
                <button
                  type="submit"
                  disabled={urlMutation.isPending || !url.trim()}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                >
                  {urlMutation.isPending ? 'Processing...' : 'Ingest URL'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleSubmitText}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Text Content
                  </label>
                  <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste your content here..."
                    rows={8}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={textMutation.isPending}
                  />
                </div>
                <button
                  type="submit"
                  disabled={textMutation.isPending || !text.trim()}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
                >
                  {textMutation.isPending ? 'Processing...' : 'Ingest Text'}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Job Status */}
        <div>
          {jobId && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold mb-4">Job Status</h3>
              <JobMonitor jobId={jobId} />
            </div>
          )}

          {!jobId && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold mb-4">How it works</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-600">
                <li>Enter a URL or paste text content</li>
                <li>Select the domain (cooking, python, etc.)</li>
                <li>Click ingest to start extraction</li>
                <li>Patterns are automatically extracted</li>
                <li>View results in the Patterns page</li>
              </ol>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function JobMonitor({ jobId }) {
  const { data: job } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => api.getJobStatus(jobId),
    refetchInterval: (data) => (data?.status === 'completed' || data?.status === 'failed' ? false : 2000),
  });

  if (!job) {
    return <div className="text-gray-500">Loading job status...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className={`px-2 py-1 rounded text-xs ${
          job.status === 'completed' ? 'bg-green-100 text-green-800' :
          job.status === 'failed' ? 'bg-red-100 text-red-800' :
          'bg-yellow-100 text-yellow-800'
        }`}>
          {job.status}
        </span>
        <span className="text-sm text-gray-600">{job.progress}%</span>
      </div>

      {job.progress < 100 && job.status !== 'failed' && (
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${job.progress}%` }}
          />
        </div>
      )}

      {job.patterns_extracted > 0 && (
        <div className="text-green-600">
          ✓ Extracted {job.patterns_extracted} patterns
        </div>
      )}

      {job.errors?.length > 0 && (
        <div className="text-red-600">
          Errors: {job.errors.join(', ')}
        </div>
      )}

      {job.status === 'completed' && (
        <a href="/patterns" className="text-blue-600 hover:underline">
          View patterns →
        </a>
      )}
    </div>
  );
}

export default Ingestion;
