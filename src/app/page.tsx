'use client';

import { useState } from 'react';

interface WebsiteResponse {
  success: boolean;
  content: string;
  title: string | null;
  description: string | null;
}

export default function Home() {
  const [formData, setFormData] = useState({
    website: '',
    description: '',
    industry: '',
    aiUsage: [] as string[],
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const industries = [
    'Technology',
    'Healthcare',
    'Finance',
    'Education',
    'Manufacturing',
    'Retail',
    'Other'
  ];

  const aiUsageOptions = [
    'Machine Learning Models',
    'Natural Language Processing',
    'Computer Vision',
    'Automated Decision Making',
    'Chatbots/Virtual Assistants',
    'Predictive Analytics',
    'Robotics/Automation'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // First, analyze the website
      const websiteResponse = await fetch('/api/analyze-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: formData.website }),
      });

      if (!websiteResponse.ok) {
        throw new Error('Failed to analyze website');
      }

      const websiteData = await websiteResponse.json();
      if (!websiteData.success) {
        throw new Error(websiteData.content);
      }

      // For now, just show the scraped content
      setResult({
        success: true,
        analysis: `Website Title: ${websiteData.data.title}\n\nWebsite Data: ${websiteData.data.raw}`,
        timestamp: new Date().toISOString()
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 text-blue-900">AI Regulation Impact Analyzer</h1>
          <p className="text-lg text-gray-600">Understand how AI regulations affect your business</p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg mb-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-2">
                  Company Website
                </label>
                <input
                  type="url"
                  id="website"
                  value={formData.website}
                  onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
                  className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black bg-white !text-black"
                  placeholder="https://your-company.com"
                  style={{ color: 'black' }}
                  required
                />
              </div>

              <div>
                <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <select
                  id="industry"
                  value={formData.industry}
                  onChange={(e) => setFormData(prev => ({ ...prev, industry: e.target.value }))}
                  className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black bg-white !text-black"
                  style={{ color: 'black' }}
                  required
                >
                  <option value="">Select an industry</option>
                  {industries.map(industry => (
                    <option key={industry} value={industry}>{industry}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Business Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={4}
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black bg-white !text-black"
                style={{ color: 'black' }}
                placeholder="Describe your business operations, goals, and current challenges..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Technologies Used
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {aiUsageOptions.map(option => (
                  <div key={option} className="flex items-center">
                    <input
                      type="checkbox"
                      id={option}
                      checked={formData.aiUsage.includes(option)}
                      onChange={(e) => {
                        const newAiUsage = e.target.checked
                          ? [...formData.aiUsage, option]
                          : formData.aiUsage.filter(item => item !== option);
                        setFormData(prev => ({ ...prev, aiUsage: newAiUsage }));
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor={option} className="ml-2 text-sm text-gray-600">
                      {option}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-center pt-4">
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-3 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300 transform transition hover:scale-105"
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing...
                  </span>
                ) : 'Generate Impact Report'}
              </button>
            </div>
          </form>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-8">
            {error}
          </div>
        )}

        {result && result.success && (
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-blue-900">AI Regulation Impact Analysis</h2>
              <button
                onClick={() => {/* TODO: Implement PDF download */}}
                className="flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download PDF Report
              </button>
            </div>

            <div className="prose max-w-none">
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-2">Company Profile</h3>
                <p><strong>Industry:</strong> {formData.industry}</p>
                <p><strong>AI Technologies:</strong> {formData.aiUsage.join(', ')}</p>
              </div>

              <div className="space-y-6">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <pre className="whitespace-pre-wrap text-gray-700 text-sm">
                    {result.analysis}
                  </pre>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between text-sm text-gray-500">
              <div>
                Generated on: {new Date(result.timestamp).toLocaleString()}
              </div>
              <div className="flex items-center">
                <button
                  onClick={() => {/* TODO: Implement sharing */}}
                  className="flex items-center text-blue-600 hover:text-blue-800"
                >
                  <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                  Share Report
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
