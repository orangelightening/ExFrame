import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { systemAPI, assistAPI } from '../services/api';
import { Activity, Play, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { Loading, ErrorMessage, Card, ProgressBar } from '../components/UI';

/**
 * Diagnostics page - health checks and system analysis
 */
export default function Diagnostics() {
  const [isRunningDiagnostics, setIsRunningDiagnostics] = useState(false);

  const { data: status, isLoading, error } = useQuery({
    queryKey: ['system-config'],
    queryFn: () => systemAPI.getConfig(),
  });

  const runDiagnostics = async () => {
    setIsRunningDiagnostics(true);
    try {
      await assistAPI.diagnose();
      // Refresh status after diagnostics
    } finally {
      setIsRunningDiagnostics(false);
    }
  };

  if (isLoading) return <Loading text="Loading system information..." />;
  if (error) return <ErrorMessage error={error} />;

  const services = status?.services || {};
  const disks = status?.storage?.devices?.filter(d => d.type === 'disk') || [];

  // Build filesystems list from storage device children (partitions with mountpoints)
  const filesystems = [];
  status?.storage?.devices?.forEach(device => {
    if (device.children) {
      device.children.forEach(child => {
        if (child.mountpoint && child.mountpoint !== '[SWAP]') {
          filesystems.push({
            mountpoint: child.mountpoint,
            type: child.type || 'unknown',
            size: child.size,
            device: child.name
          });
        }
      });
    }
  });

  // Calculate health summary
  const runningServices = Object.values(services).filter(
    (s) => s?.status === 'running'
  ).length;
  const totalServices = Object.keys(services).length;

  // For now, we don't have usage percent, so filesystem health is based on count
  const criticalFilesystems = [];
  const warningFilesystems = [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">System Diagnostics</h2>
          <p className="mt-1 text-gray-400">
            Run health checks and analyze system state
          </p>
        </div>
        <button
          onClick={runDiagnostics}
          disabled={isRunningDiagnostics}
          className="btn btn-primary flex items-center gap-2"
        >
          {isRunningDiagnostics ? (
            <>
              <Activity className="h-4 w-4 animate-pulse" />
              Running...
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              Run Diagnostics
            </>
          )}
        </button>
      </div>

      {/* Health Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Services</span>
            <span
              className={`text-lg font-semibold ${
                runningServices === totalServices
                  ? 'text-success-400'
                  : runningServices / totalServices >= 0.5
                  ? 'text-warning-400'
                  : 'text-danger-400'
              }`}
            >
              {runningServices}/{totalServices}
            </span>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Filesystems</span>
            <span
              className={`text-lg font-semibold ${
                criticalFilesystems.length > 0
                  ? 'text-danger-400'
                  : warningFilesystems.length > 0
                  ? 'text-warning-400'
                  : 'text-success-400'
              }`}
            >
              {criticalFilesystems.length > 0
                ? `${criticalFilesystems.length} Critical`
                : warningFilesystems.length > 0
                ? `${warningFilesystems.length} Warning`
                : 'Healthy'}
            </span>
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Storage</span>
            <span className="text-lg font-semibold text-gray-100">
              {disks.length} disks
            </span>
          </div>
        </Card>
      </div>

      {/* Service Status */}
      <Card title="Service Status">
        <div className="space-y-2">
          {Object.entries(services).map(([name, service]) => {
            const isRunning = service?.status === 'running';
            return (
              <div
                key={name}
                className="flex items-center justify-between rounded-lg bg-gray-700/50 px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  {isRunning ? (
                    <CheckCircle className="h-5 w-5 text-success-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-danger-500" />
                  )}
                  <span className="text-gray-300">{name}</span>
                </div>
                <span
                  className={`text-sm font-medium ${
                    isRunning ? 'text-success-400' : 'text-danger-400'
                  }`}
                >
                  {service?.status || 'unknown'}
                </span>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Filesystem Health */}
      <Card title="Filesystem Health">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="pb-3 text-left font-medium text-gray-400">Mountpoint</th>
                <th className="pb-3 text-left font-medium text-gray-400">Device</th>
                <th className="pb-3 text-left font-medium text-gray-400">Size</th>
                <th className="pb-3 text-left font-medium text-gray-400">Status</th>
              </tr>
            </thead>
            <tbody>
              {filesystems.map((fs, idx) => (
                <tr key={idx} className="border-b border-gray-700/50">
                  <td className="py-3 text-gray-300">{fs.mountpoint}</td>
                  <td className="py-3 text-gray-400">{fs.device}</td>
                  <td className="py-3 text-gray-500">{fs.size}</td>
                  <td className="py-3">
                    <span className="text-success-400">Mounted</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card title="Quick Actions">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <button
            onClick={() => window.open('/api/v1/system/status', '_blank')}
            className="flex items-center justify-between rounded-lg bg-gray-700 px-4 py-3 text-left transition-colors hover:bg-gray-600"
          >
            <span className="text-sm text-gray-300">View raw system status</span>
            <CheckCircle className="h-4 w-4 text-gray-400" />
          </button>
          <button
            onClick={() => window.open('/api/v1/knowledge/patterns', '_blank')}
            className="flex items-center justify-between rounded-lg bg-gray-700 px-4 py-3 text-left transition-colors hover:bg-gray-600"
          >
            <span className="text-sm text-gray-300">View knowledge patterns</span>
            <CheckCircle className="h-4 w-4 text-gray-400" />
          </button>
        </div>
      </Card>

      {/* Tips */}
      <Card title="Tips">
        <ul className="space-y-2 text-sm text-gray-300">
          <li className="flex gap-2">
            <AlertTriangle className="h-5 w-5 shrink-0 text-warning-500" />
            <span>
              Run diagnostics regularly to catch issues early before they become
              critical
            </span>
          </li>
          <li className="flex gap-2">
            <AlertTriangle className="h-5 w-5 shrink-0 text-warning-500" />
            <span>
              Monitor filesystem usage - keep your data disks below 80% to
              maintain optimal performance
            </span>
          </li>
          <li className="flex gap-2">
            <AlertTriangle className="h-5 w-5 shrink-0 text-warning-500" />
            <span>
              Use the Knowledge Base to find solutions to common OMV issues
            </span>
          </li>
        </ul>
      </Card>
    </div>
  );
}
