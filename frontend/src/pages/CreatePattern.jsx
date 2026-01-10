import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import api from '../services/api';

function CreatePattern() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    domain: 'cooking',
    name: '',
    pattern_type: 'procedure',
    description: '',
    problem: '',
    solution: '',
    steps: '',
    conditions: '',
    related_patterns: '',
    prerequisites: '',
    alternatives: '',
    confidence: 0.7,
    sources: '',
    tags: '',
    examples: '',
  });

  const createMutation = useMutation({
    mutationFn: (pattern) => api.createPattern(pattern),
    onSuccess: (data) => {
      navigate(`/patterns/${data.id}`);
    },
    onError: (error) => {
      alert(`Error creating pattern: ${error.message}`);
    },
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Parse list fields
    const pattern = {
      ...formData,
      steps: formData.steps.split('\n').filter(s => s.trim()),
      conditions: formData.conditions ? { custom: formData.conditions } : {},
      related_patterns: formData.related_patterns.split(',').map(s => s.trim()).filter(s => s),
      prerequisites: formData.prerequisites.split(',').map(s => s.trim()).filter(s => s),
      alternatives: formData.alternatives.split(',').map(s => s.trim()).filter(s => s),
      sources: formData.sources.split('\n').filter(s => s.trim()),
      tags: formData.tags.split(',').map(s => s.trim()).filter(s => s),
      examples: formData.examples.split('\n').filter(s => s.trim()),
    };

    createMutation.mutate(pattern);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Create Expertise Pattern</h2>
        <p className="text-gray-600 mt-1">Manually create a synthetic pattern for testing</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Domain *
            </label>
            <select
              name="domain"
              value={formData.domain}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="cooking">Cooking</option>
              <option value="python">Python</option>
              <option value="omv">OMV</option>
              <option value="diy">DIY</option>
              <option value="first_aid">First Aid</option>
              <option value="gardening">Gardening</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pattern Type *
            </label>
            <select
              name="pattern_type"
              value={formData.pattern_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="troubleshooting">Troubleshooting</option>
              <option value="procedure">Procedure</option>
              <option value="substitution">Substitution</option>
              <option value="decision">Decision</option>
              <option value="diagnostic">Diagnostic</option>
              <option value="preparation">Preparation</option>
              <option value="optimization">Optimization</option>
              <option value="principle">Principle</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pattern Name *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., 'Ingredient Substitution: Butter for Oil'"
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description * (1-2 sentences)
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="What does this pattern do?"
            rows={2}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        {/* Problem & Solution */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Problem Solved *
            </label>
            <textarea
              name="problem"
              value={formData.problem}
              onChange={handleChange}
              placeholder="What problem does this pattern solve?"
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Solution *
            </label>
            <textarea
              name="solution"
              value={formData.solution}
              onChange={handleChange}
              placeholder="How is it solved?"
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        {/* Steps */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Procedural Steps (one per line)
          </label>
          <textarea
            name="steps"
            value={formData.steps}
            onChange={handleChange}
            placeholder="Step 1&#10;Step 2&#10;Step 3"
            rows={5}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          />
        </div>

        {/* Conditions (for decision patterns) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Decision Conditions (for branching patterns)
          </label>
          <textarea
            name="conditions"
            value={formData.conditions}
            onChange={handleChange}
            placeholder="If X then Y, if A then B..."
            rows={2}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Relationships */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Related Patterns (comma-separated IDs)
            </label>
            <input
              type="text"
              name="related_patterns"
              value={formData.related_patterns}
              onChange={handleChange}
              placeholder="cooking_001, cooking_002"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prerequisites (comma-separated)
            </label>
            <input
              type="text"
              name="prerequisites"
              value={formData.prerequisites}
              onChange={handleChange}
              placeholder="Basic knife skills"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Alternatives (comma-separated)
            </label>
            <input
              type="text"
              name="alternatives"
              value={formData.alternatives}
              onChange={handleChange}
              placeholder="Alternative method 1, Alternative 2"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Confidence */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Confidence Score: {formData.confidence}
          </label>
          <input
            type="range"
            name="confidence"
            min="0"
            max="1"
            step="0.1"
            value={formData.confidence}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>Uncertain</span>
            <span>Very Confident</span>
          </div>
        </div>

        {/* Sources */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sources (one per line)
          </label>
          <textarea
            name="sources"
            value={formData.sources}
            onChange={handleChange}
            placeholder="https://example.com/source1&#10;https://example.com/source2"
            rows={3}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
          />
        </div>

        {/* Tags & Examples */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="baking, substitution, ingredients"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Examples (one per line)
            </label>
            <textarea
              name="examples"
              value={formData.examples}
              onChange={handleChange}
              placeholder="Example 1&#10;Example 2"
              rows={3}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={() => navigate('/patterns')}
            className="px-6 py-2 border rounded-lg hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Pattern'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreatePattern;
