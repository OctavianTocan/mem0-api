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

  const fetchMemories = async () => {
    if (!url) return;
    setLoading(true);
    try {
      const res = await fetch(`${url}/get_all_memories?user_id=${encodeURIComponent(userId)}`, {
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
    if (!url || !query) return;
    setLoading(true);
    try {
      const res = await fetch(`${url}/search_memory`, {
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
    <div>
      <h1>Mem0 Viewer</h1>
      <label>
        Instance URL:
        <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://..." />
      </label>
      <label>
        API Key:
        <input value={apiKey} onChange={e => setApiKey(e.target.value)} />
      </label>
      <label>
        User ID:
        <input value={userId} onChange={e => setUserId(e.target.value)} />
      </label>
      <button onClick={fetchMemories} disabled={loading}>Fetch Memories</button>

      {memories.length > 0 && (
        <div>
          <h2>Memories</h2>
          <ul>
            {memories.map((m, idx) => (
              <li key={idx}><pre>{JSON.stringify(m, null, 2)}</pre></li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <input
          placeholder="Ask a question..."
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <button onClick={askQuestion} disabled={loading}>Ask</button>
      </div>

      {answer && (
        <div>
          <h2>Answer</h2>
          <pre>{JSON.stringify(answer, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
