import React, { useState } from 'react';

interface Memory {
  [key: string]: any;
}

const App: React.FC = () => {
  const [url, setUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [userId, setUserId] = useState('');
  const [query, setQuery] = useState('');
  const [memories, setMemories] = useState<Memory[]>([]);
  const [answer, setAnswer] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Get the base URL for API calls - use the same host as the current page
  const getApiBaseUrl = () => {
    if (url) return url; // If user provided a URL, use it
    // Otherwise, use the same host as the current page
    return window.location.origin;
  };

  const fetchMemories = async () => {
    const apiBaseUrl = getApiBaseUrl();
    if (!apiBaseUrl) return;
    setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/get_all_memories?user_id=${encodeURIComponent(userId)}`, {
        headers: { 'X-API-Key': apiKey }
      });
      const data = await res.json();
      setMemories(data.results || data.memories || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    const apiBaseUrl = getApiBaseUrl();
    if (!apiBaseUrl || !query) return;
    setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/search_memory`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({ query, user_id: userId })
      });
      const data = await res.json();
      setAnswer(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#333', textAlign: 'center', marginBottom: '30px' }}>Mem0 Browser</h1>
      
      <div style={{ marginBottom: '20px', backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px' }}>
        <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
          Instance URL (leave empty to use current host):
          <input 
            value={url} 
            onChange={e => setUrl(e.target.value)} 
            placeholder="https://your-api-host.com (or leave empty for current host)" 
            style={{ width: '100%', padding: '8px', marginTop: '5px', borderRadius: '4px', border: '1px solid #ddd' }}
          />
        </label>
        <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
          API Key:
          <input 
            value={apiKey} 
            onChange={e => setApiKey(e.target.value)} 
            type="password"
            style={{ width: '100%', padding: '8px', marginTop: '5px', borderRadius: '4px', border: '1px solid #ddd' }}
          />
        </label>
        <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
          User ID:
          <input 
            value={userId} 
            onChange={e => setUserId(e.target.value)} 
            style={{ width: '100%', padding: '8px', marginTop: '5px', borderRadius: '4px', border: '1px solid #ddd' }}
          />
        </label>
        <button 
          onClick={fetchMemories} 
          disabled={loading}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          {loading ? 'Loading...' : 'Fetch Memories'}
        </button>
      </div>

      {memories.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h2 style={{ color: '#333' }}>Memories ({memories.length})</h2>
          <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px', borderRadius: '4px', backgroundColor: 'white' }}>
            {memories.map((m, idx) => (
              <div key={idx} style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                <pre style={{ margin: 0, fontSize: '12px', whiteSpace: 'pre-wrap' }}>{JSON.stringify(m, null, 2)}</pre>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <h2 style={{ color: '#333' }}>Ask Questions</h2>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <input
            placeholder="Ask a question about your memories..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            onKeyPress={(e) => e.key === 'Enter' && askQuestion()}
          />
          <button 
            onClick={askQuestion} 
            disabled={loading}
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#28a745', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            {loading ? 'Asking...' : 'Ask'}
          </button>
        </div>
      </div>

      {answer && (
        <div>
          <h2 style={{ color: '#333' }}>Answer</h2>
          <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '4px', border: '1px solid #ddd' }}>
            <pre style={{ margin: 0, fontSize: '14px', whiteSpace: 'pre-wrap' }}>{JSON.stringify(answer, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
