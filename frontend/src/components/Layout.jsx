import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  Database,
  Activity,
  GitBranch,
  Menu,
  X,
  Globe,
  ChevronDown,
  Loader2,
  Layers,
} from 'lucide-react';
import { useState } from 'react';
import { useUniverse } from '../contexts/UniverseContext';

const navigation = [
  { name: 'AI Assistant', href: '/', icon: MessageSquare },
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Knowledge Base', href: '/knowledge', icon: Database },
  { name: 'Universes', href: '/universes', icon: Layers },
  { name: 'Diagnostics', href: '/diagnostics', icon: Activity },
  { name: 'Execution Traces', href: '/traces', icon: GitBranch },
];

function UniverseSelector() {
  const { currentUniverse, universes, switchUniverse, loading } = useUniverse();
  const [isOpen, setIsOpen] = useState(false);

  if (loading && !currentUniverse) {
    return (
      <div className="flex items-center gap-2 text-gray-400">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">Loading...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg bg-gray-700 px-3 py-2 text-sm font-medium text-gray-100 hover:bg-gray-600 transition-colors"
      >
        <Globe className="h-4 w-4" />
        <span>{currentUniverse?.name || currentUniverse?.universe_id || 'Select Universe'}</span>
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full z-20 mt-2 w-56 rounded-lg bg-gray-800 border border-gray-700 shadow-lg py-1">
            <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase">
              Available Universes
            </div>
            {universes.map((universe) => (
              <button
                key={universe.universe_id}
                onClick={() => {
                  switchUniverse(universe.universe_id);
                  setIsOpen(false);
                }}
                className={`w-full px-3 py-2 text-left text-sm transition-colors ${
                  universe.universe_id === currentUniverse?.universe_id
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>{universe.name}</span>
                  {universe.state === 'active' && (
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                  )}
                </div>
                <div className="text-xs text-gray-400 mt-0.5">
                  {universe.domain_count} domains · {universe.total_patterns} patterns
                </div>
              </button>
            ))}
            {universes.length === 0 && (
              <div className="px-3 py-2 text-sm text-gray-400">
                No universes available
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-gray-800 border-r border-gray-700 transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-gray-700">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
                <span className="text-sm font-bold text-white">OMV</span>
              </div>
              <span className="text-lg font-semibold text-gray-100">
                Co-Pilot
              </span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-400 hover:text-gray-100"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`
                }
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          <div className="border-t border-gray-700 p-4">
            <div className="text-xs text-gray-400">
              <p>OMV Co-Pilot v2.0.0</p>
              <p className="mt-1">Connected to: 192.168.3.68</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-gray-700 bg-gray-800/80 px-6 backdrop-blur-sm lg:px-8">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden text-gray-400 hover:text-gray-100"
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex flex-1 items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-100">
              {navigation.find(
                (item) => item.href === window.location.pathname
              )?.name || 'OMV Co-Pilot'}
            </h1>

            <div className="flex items-center gap-4">
              <UniverseSelector />
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-success-500" />
                <span className="text-sm text-gray-400">Online</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
