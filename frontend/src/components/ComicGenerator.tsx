"use client";

import { useState, useRef } from 'react';
import { Book, Loader, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type StatusUpdate = {
  status: string;
  details: string | null;
};

export default function ComicGenerator() {
  const [topic, setTopic] = useState('');
  const [status, setStatus] = useState<StatusUpdate[]>([]);
  const [finalComic, setFinalComic] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const handleGenerate = () => {
    if (isGenerating) return;

    setIsGenerating(true);
    setStatus([{ status: 'Connecting to server...', details: null }]);
    setFinalComic(null);

    // Allow using same hostname as page when accessed over LAN
    const apiHost = typeof window !== 'undefined' ? (window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname) : '127.0.0.1';
    const url = `http://${apiHost}:8002/generate-comic/?topic=${encodeURIComponent(topic)}`;
    console.log('Opening SSE to', url);
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('SSE connection opened');
      setStatus(prev => [...prev, { status: 'Connected. Waiting for crew start...', details: null }]);
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('SSE message', data);

      if (data.status === 'complete') {
        setFinalComic(data.markdown);
        setStatus(prev => [...prev, { status: 'Comic generation complete!', details: 'Scroll down to see your comic.' }]);
        eventSource.close();
        setIsGenerating(false);
      } else if (data.status === 'error') {
        setStatus(prev => [...prev, { status: 'An error occurred', details: data.details }]);
        eventSource.close();
        setIsGenerating(false);
      } else {
        setStatus(prev => [...prev, data]);
      }
    };

    eventSource.onerror = (err) => {
      console.error('EventSource failed:', err);
      setStatus(prev => [...prev, { status: 'Connection Error', details: 'Could not connect to the generation server.' }]);
      eventSource.close();
      setIsGenerating(false);
    };
  };

  return (
    <div className="container mx-auto p-4">
      <div className="bg-gray-800 shadow-lg rounded-lg p-8 max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-6 text-white flex items-center justify-center">
          <Book className="mr-3 text-purple-400" />
          AI Comic Book Creator
        </h1>

        <div className="flex flex-col gap-4">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a topic for your comic..."
            className="p-3 bg-gray-700 text-white rounded-md border border-gray-600 focus:ring-2 focus:ring-purple-500 focus:outline-none"
            disabled={isGenerating}
          />
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !topic}
            className="bg-purple-600 text-white font-bold py-3 px-6 rounded-md hover:bg-purple-700 disabled:bg-gray-500 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
          >
            {isGenerating ? (
              <>
                <Loader className="animate-spin mr-2" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="mr-2" />
                Generate Comic
              </>
            )}
          </button>
        </div>
      </div>

      {isGenerating && (
        <div className="mt-8 max-w-2xl mx-auto bg-gray-800 shadow-lg rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Generation Progress</h2>
          <ul className="space-y-2">
            {status.map((s, index) => (
              <li key={index} className="text-gray-300">
                <span className="font-bold text-purple-400">{s.status}</span>
                {s.details && <span className="text-sm text-gray-400 block">{s.details}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {finalComic && (
        <div className="mt-8 max-w-4xl mx-auto bg-gray-800 shadow-lg rounded-lg p-8">
          <h2 className="text-2xl font-bold text-white mb-4 border-b border-gray-700 pb-2">Your Comic Strip</h2>
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{finalComic}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
