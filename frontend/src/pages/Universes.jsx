import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useUniverse } from '../contexts/UniverseContext';
import { universeAPI } from '../services/api';
import {
  Plus,
  Globe,
  Database,
  Loader2,
  Check,
  X,
  GitMerge,
  Trash2,
  RefreshCw,
} from 'lucide-react';

export default function Universes() {
  const queryClient = useQueryClient();
  const { currentUniverse, universes, switchUniverse, createUniverse, refreshCurrentUniverse } = useUniverse();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [newUniverse, setNewUniverse] = useState({ id: '', name: '', description: '', baseOn: '' });
  const [mergeConfig, setMergeConfig] = useState({ source: '', target: '', strategy: 'merge_patterns' });
  const [creating, setCreating] = useState(false);
  const [merging, setMerging] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const { data: domains, isLoading: domainsLoading } = useQuery({
    queryKey: ['universe-domains', currentUniverse?.universe_id],
    queryFn: () => universeAPI.listDomains(currentUniverse?.universe_id || 'default'),
    enabled: !!currentUniverse,
  });

  const handleCreateUniverse = async (e) => {
    e.preventDefault();
    setCreating(true);
    setError(null);
    setSuccess(null);

    try {
      await createUniverse(newUniverse.id, newUniverse.name, newUniverse.description, newUniverse.baseOn || null);
      setSuccess(`Universe "${newUniverse.name}" created successfully!`);
      setShowCreateModal(false);
      setNewUniverse({ id: '', name: '', description: '', baseOn: '' });
    } catch (err) {
      setError(err.message || 'Failed to create universe');
    } finally {
      setCreating(false);
    }
  };

  const handleMergeUniverses = async (e) => {
    e.preventDefault();
    setMerging(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await universeAPI.mergeUniverses(mergeConfig.source, mergeConfig.target, mergeConfig.strategy);
      setSuccess(`Merged ${result.merged_domains} domains from ${mergeConfig.source} to ${mergeConfig.target}`);
      setShowMergeModal(false);
      queryClient.invalidateQueries(['universes']);
    } catch (err) {
      setError(err.message || 'Failed to merge universes');
    } finally {
      setMerging(false);
    }
  };

  const handleRefresh = async () => {
    await refreshCurrentUniverse();
    queryClient.invalidateQueries(['universes']);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">Universes</h1>
          <p className="text-gray-400">Manage runtime universes and their configurations</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 rounded-lg bg-gray-700 px-4 py-2 text-sm font-medium text-gray-100 hover:bg-gray-600"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            <Plus className="h-4 w-4" />
            New Universe
          </button>
          <button
            onClick={() => setShowMergeModal(true)}
            className="flex items-center gap-2 rounded-lg bg-gray-700 px-4 py-2 text-sm font-medium text-gray-100 hover:bg-gray-600"
          >
            <GitMerge className="h-4 w-4" />
            Merge
          </button>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="rounded-lg bg-red-900/50 border border-red-700 p-4 text-red-200">
          <div className="flex items-center gap-2">
            <X className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </div>
      )}
      {success && (
        <div className="rounded-lg bg-green-900/50 border border-green-700 p-4 text-green-200">
          <div className="flex items-center gap-2">
            <Check className="h-5 w-5" />
            <span>{success}</span>
          </div>
        </div>
      )}

      {/* Current Universe Info */}
      {currentUniverse && (
        <div className="rounded-lg bg-gray-800 border border-gray-700 p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-600">
                <Globe className="h-6 w-6 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-semibold text-gray-100">{currentUniverse.name}</h2>
                  <span className="rounded-full bg-green-500/20 px-2 py-0.5 text-xs font-medium text-green-400">
                    {currentUniverse.state}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mt-1">{currentUniverse.description}</p>
                <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-400">
                  <span>ID: {currentUniverse.universe_id}</span>
                  <span>Version: {currentUniverse.version}</span>
                  <span>Domains: {currentUniverse.domain_count}</span>
                  <span>Patterns: {currentUniverse.total_patterns}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Domains in current universe */}
          {domains && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-300 mb-3">Domains</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {domains.domains.map((domain) => (
                  <div
                    key={domain.domain_id}
                    className="rounded-lg bg-gray-700/50 border border-gray-600 p-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-100">{domain.domain_id}</span>
                      <span className="text-xs text-gray-400">{domain.patterns} patterns</span>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {domain.specialists} specialists
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* All Universes */}
      <div>
        <h2 className="text-lg font-semibold text-gray-100 mb-4">All Universes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {universes.map((universe) => (
            <div
              key={universe.universe_id}
              className={`rounded-lg border p-4 transition-colors ${
                universe.universe_id === currentUniverse?.universe_id
                  ? 'bg-primary-900/30 border-primary-600'
                  : 'bg-gray-800 border-gray-700 hover:bg-gray-750'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-700">
                    <Globe className="h-5 w-5 text-gray-300" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-100">{universe.name}</h3>
                    <p className="text-xs text-gray-400 mt-0.5">{universe.universe_id}</p>
                  </div>
                </div>
                {universe.state === 'active' && (
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                )}
              </div>

              <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-400">
                <span>{universe.domain_count} domains</span>
                <span>{universe.total_patterns} patterns</span>
              </div>

              {universe.universe_id !== currentUniverse?.universe_id && (
                <button
                  onClick={() => switchUniverse(universe.universe_id)}
                  className="mt-3 w-full rounded-lg bg-gray-700 px-3 py-2 text-sm font-medium text-gray-100 hover:bg-gray-600"
                >
                  Switch to this Universe
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Create Universe Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-gray-800 border border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-gray-100 mb-4">Create New Universe</h2>

            <form onSubmit={handleCreateUniverse} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Universe ID
                </label>
                <input
                  type="text"
                  required
                  pattern="[a-z][a-z0-9_]*"
                  title="Must start with a lowercase letter and contain only lowercase letters, numbers, and underscores"
                  value={newUniverse.id}
                  onChange={(e) => setNewUniverse({ ...newUniverse, id: e.target.value })}
                  className="w-full rounded-lg bg-gray-700 border border-gray-600 px-3 py-2 text-gray-100 placeholder-gray-400 focus:border-primary-500 focus:outline-none"
                  placeholder="e.g., testing, staging"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  required
                  value={newUniverse.name}
                  onChange={(e) => setNewUniverse({ ...newUniverse, name: e.target.value })}
                  className="w-full rounded-lg bg-gray-700 border border-gray-600 px-3 py-2 text-gray-100 placeholder-gray-400 focus:border-primary-500 focus:outline-none"
                  placeholder="e.g., Testing Universe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={newUniverse.description}
                  onChange={(e) => setNewUniverse({ ...newUniverse, description: e.target.value })}
                  className="w-full rounded-lg bg-gray-700 border border-gray-600 px-3 py-2 text-gray-100 placeholder-gray-400 focus:border-primary-500 focus:outline-none"
                  placeholder="Optional description"
                  rows={2}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Base on (optional)
                </label>
                <select
                  value={newUniverse.baseOn}
                  onChange={(e) => setNewUniverse({ ...newUniverse, baseOn: e.target.value })}
                  className="w-full rounded-lg bg-gray-700 border border-gray-600 px-3 py-2 text-gray-100 focus:border-primary-500 focus:outline-none"
                >
                  <option value="">Create empty universe</option>
                  {universes.map((u) => (
                    <option key={u.universe_id} value={u.universe_id}>
                      {u.name} ({u.universe_id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 rounded-lg bg-gray-700 px-4 py-2 text-sm font-medium text-gray-100 hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                >
                  {creating ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Creating...
                    </span>
                  ) : (
                    'Create'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Merge Universes Modal */}
      {showMergeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-gray-800 border border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-gray-100 mb-4">Merge Universes</h2>

            <form onSubmit={handleMergeUniverses} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Source Universe
                </label>
                <select
                  required
                  value={mergeConfig.source}
                  onChange={(e) => setMergeConfig({ ...mergeConfig, source: e.target.value })}
                  className="w-full rounded-lg bg-gray-700 border border-gray-600 px-3 py-2 text-gray-100 focus:border-primary-500 focus:outline-none"
                >
                  <option value="">Select source...</option>
                  {universes.map((u) => (
                    <option key={u.universe_id} value={u.universe_id}>
                      {u.name} ({u.universe_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Target Universe
                </label>
                <select
                  required
                  value={mergeConfig.target}
                  onChange={(e) => setMergeConfig({ ...mergeConfig, target: e.target.value })}
                  className="w-full rounded-lg bg-gray-700 border border-gray-600 px-3 py-2 text-gray-100 focus:border-primary-500 focus:outline-none"
                >
                  <option value="">Select target...</option>
                  {universes.map((u) => (
                    <option key={u.universe_id} value={u.universe_id}>
                      {u.name} ({u.universe_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Merge Strategy
                </label>
                <select
                  value={mergeConfig.strategy}
                  onChange={(e) => setMergeConfig({ ...mergeConfig, strategy: e.target.value })}
                  className="w-full rounded-lg bg-gray-700 border border-gray-600 px-3 py-2 text-gray-100 focus:border-primary-500 focus:outline-none"
                >
                  <option value="merge_patterns">Merge Patterns (combine)</option>
                  <option value="source_wins">Source Wins (overwrite)</option>
                  <option value="target_wins">Target Wins (keep existing)</option>
                  <option value="fail">Fail on Conflict</option>
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowMergeModal(false)}
                  className="flex-1 rounded-lg bg-gray-700 px-4 py-2 text-sm font-medium text-gray-100 hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={merging}
                  className="flex-1 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                >
                  {merging ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Merging...
                    </span>
                  ) : (
                    'Merge'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
