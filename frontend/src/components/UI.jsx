import { Loader2, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';

/**
 * Loading spinner component
 */
export function Loading({ size = 'default', text = 'Loading...' }) {
  const sizeClasses = {
    small: 'h-4 w-4',
    default: 'h-8 w-8',
    large: 'h-12 w-12',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <Loader2 className={`animate-spin text-primary-500 ${sizeClasses[size]}`} />
      {text && <p className="text-sm text-gray-400">{text}</p>}
    </div>
  );
}

/**
 * Error message component
 */
export function ErrorMessage({ error, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-danger-100">
        <XCircle className="h-6 w-6 text-danger-600" />
      </div>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-100">Something went wrong</h3>
        <p className="mt-1 text-sm text-gray-400">{error?.message || 'An error occurred'}</p>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-primary">
          Try again
        </button>
      )}
    </div>
  );
}

/**
 * Empty state component
 */
export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      {Icon && (
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-800">
          <Icon className="h-8 w-8 text-gray-400" />
        </div>
      )}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-100">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-gray-400">{description}</p>
        )}
      </div>
      {action && action}
    </div>
  );
}

/**
 * Status badge component
 */
export function StatusBadge({ status, children }) {
  const statusConfig = {
    success: {
      className: 'bg-success-100 text-success-800',
      icon: CheckCircle,
    },
    warning: {
      className: 'bg-warning-100 text-warning-800',
      icon: AlertTriangle,
    },
    error: {
      className: 'bg-danger-100 text-danger-800',
      icon: XCircle,
    },
    info: {
      className: 'bg-primary-100 text-primary-800',
      icon: Info,
    },
  };

  const config = statusConfig[status] || statusConfig.info;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${config.className}`}>
      <Icon className="h-3 w-3" />
      {children || status}
    </span>
  );
}

/**
 * Card component
 */
export function Card({ children, title, subtitle, action }) {
  return (
    <div className="card">
      {(title || subtitle || action) && (
        <div className="mb-4 flex items-start justify-between">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-100">{title}</h3>}
            {subtitle && <p className="mt-1 text-sm text-gray-400">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

/**
 * Metric card component
 */
export function MetricCard({ title, value, unit, trend, icon: Icon }) {
  const trendColor = trend > 0 ? 'text-success-500' : trend < 0 ? 'text-danger-500' : 'text-gray-500';

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-100">
            {value}
            {unit && <span className="text-lg text-gray-400"> {unit}</span>}
          </p>
          {trend !== undefined && (
            <p className={`mt-2 text-sm ${trendColor}`}>
              {trend > 0 && '+'}
              {trend}% from last week
            </p>
          )}
        </div>
        {Icon && (
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gray-700">
            <Icon className="h-6 w-6 text-gray-400" />
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Progress bar component
 */
export function ProgressBar({ value, max = 100, color = 'primary' }) {
  const percentage = Math.min((value / max) * 100, 100);

  const colorClasses = {
    primary: 'bg-primary-500',
    success: 'bg-success-500',
    warning: 'bg-warning-500',
    danger: 'bg-danger-500',
  };

  const barColor =
    percentage >= 90
      ? colorClasses.danger
      : percentage >= 75
      ? colorClasses.warning
      : colorClasses[color] || colorClasses.primary;

  return (
    <div className="w-full">
      <div className="mb-1 flex justify-between text-sm">
        <span className="text-gray-400">{value}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-700">
        <div
          className={`h-full transition-all duration-500 ${barColor}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
