import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import { UniverseProvider } from './contexts/UniverseContext';

// Generic Framework Pages
import Dashboard from './pages/Dashboard';
import Assistant from './pages/Assistant';
import KnowledgeBase from './pages/Knowledge';
import Diagnostics from './pages/Diagnostics';
import Traces from './pages/Traces';

// Expertise Scanner Pages (Pattern Management)
import Domains from './pages/Domains';
import Patterns from './pages/Patterns';
import CreatePattern from './pages/CreatePattern';
import PatternDetail from './pages/PatternDetail';
import Ingestion from './pages/Ingestion';
import BatchIngestion from './pages/BatchIngestion';

// Universe Management
import Universes from './pages/Universes';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <UniverseProvider>
        <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            {/* Assistant - Default landing page */}
            <Route index element={<Assistant />} />

            {/* Dashboard */}
            <Route path="dashboard" element={<Dashboard />} />

            {/* Generic Framework Routes */}
            <Route path="assistant" element={<Assistant />} />
            <Route path="knowledge" element={<KnowledgeBase />} />
            <Route path="diagnostics" element={<Diagnostics />} />
            <Route path="traces" element={<Traces />} />
            <Route path="universes" element={<Universes />} />
            
            {/* Pattern Management Routes (from Expertise Scanner) */}
            <Route path="domains" element={<Domains />} />
            <Route path="patterns" element={<Patterns />} />
            <Route path="patterns/new" element={<CreatePattern />} />
            <Route path="patterns/:patternId" element={<PatternDetail />} />
            <Route path="ingestion" element={<Ingestion />} />
            <Route path="batch" element={<BatchIngestion />} />
            
            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
      </UniverseProvider>
    </QueryClientProvider>
  );
}

export default App;
