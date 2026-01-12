import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { universeAPI } from '../services/api';

const UniverseContext = createContext(null);

export const useUniverse = () => {
  const context = useContext(UniverseContext);
  if (!context) {
    throw new Error('useUniverse must be used within a UniverseProvider');
  }
  return context;
};

export const UniverseProvider = ({ children }) => {
  const [currentUniverse, setCurrentUniverse] = useState(null);
  const [universes, setUniverses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load all available universes
  const loadUniverses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await universeAPI.listUniverses();
      setUniverses(data.universes || []);

      // Set current universe if not set
      if (!currentUniverse && data.universes && data.universes.length > 0) {
        const defaultUniverse = data.universes.find(u => u.universe_id === 'default') || data.universes[0];
        setCurrentUniverse(defaultUniverse);
      }
    } catch (err) {
      setError(err.message);
      console.error('Failed to load universes:', err);
    } finally {
      setLoading(false);
    }
  }, [currentUniverse]);

  // Switch to a different universe
  const switchUniverse = useCallback(async (universeId) => {
    try {
      setLoading(true);
      setError(null);

      // Try to get the universe (may need to load it first)
      let universe = await universeAPI.getUniverse(universeId);

      // If universe exists but is unloaded, load it
      if (universe.state === 'unloaded') {
        await universeAPI.loadUniverse(universeId);
        universe = await universeAPI.getUniverse(universeId);
      }

      setCurrentUniverse(universe);

      // Refresh the list
      await loadUniverses();
    } catch (err) {
      setError(err.message);
      console.error('Failed to switch universe:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [loadUniverses]);

  // Create a new universe
  const createUniverse = useCallback(async (universeId, name, description, baseOn) => {
    try {
      setLoading(true);
      setError(null);
      await universeAPI.createUniverse(universeId, name, description, baseOn);
      await loadUniverses();
      return await switchUniverse(universeId);
    } catch (err) {
      setError(err.message);
      console.error('Failed to create universe:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [loadUniverses, switchUniverse]);

  // Refresh current universe data
  const refreshCurrentUniverse = useCallback(async () => {
    if (currentUniverse) {
      try {
        const updated = await universeAPI.getUniverse(currentUniverse.universe_id);
        setCurrentUniverse(updated);

        // Also update in the list
        setUniverses(prev => prev.map(u =>
          u.universe_id === updated.universe_id ? updated : u
        ));
      } catch (err) {
        console.error('Failed to refresh universe:', err);
      }
    }
  }, [currentUniverse]);

  // Initial load
  useEffect(() => {
    loadUniverses();
  }, [loadUniverses]);

  const value = {
    currentUniverse,
    universes,
    loading,
    error,
    switchUniverse,
    createUniverse,
    refreshCurrentUniverse,
    loadUniverses,
  };

  return (
    <UniverseContext.Provider value={value}>
      {children}
    </UniverseContext.Provider>
  );
};

export default UniverseContext;
