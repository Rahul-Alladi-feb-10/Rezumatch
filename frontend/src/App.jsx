// src/App.jsx
import { useState } from 'react';
import Navbar from './components/Navbar';
import ResumeUpload from './components/ResumeUpload';
import JobInput from './components/JobInput';
import MatchResults from './components/MatchResults';
import { FileText, Briefcase, BarChart3 } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [resumeId, setResumeId] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [matchResult, setMatchResult] = useState(null);

  const tabs = [
    { id: 'upload', label: 'Upload Resume', icon: FileText },
    { id: 'job', label: 'Job Description', icon: Briefcase },
    { id: 'results', label: 'Match Results', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Resume Matcher
          </h1>
          <p className="text-gray-600">
            AI-powered resume and job description matching system
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-white rounded-lg shadow-md p-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={20} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="max-w-6xl mx-auto">
          {activeTab === 'upload' && (
            <ResumeUpload
              onResumeUploaded={(id) => {
                setResumeId(id);
                setActiveTab('job');
              }}
              resumeId={resumeId}
            />
          )}

          {activeTab === 'job' && (
            <JobInput
              onJobCreated={(id) => {
                setJobId(id);
              }}
              jobId={jobId}
              resumeId={resumeId}
              onMatchComplete={(result) => {
                setMatchResult(result);
                setActiveTab('results');
              }}
            />
          )}

          {activeTab === 'results' && (
            <MatchResults
              matchResult={matchResult}
              onStartOver={() => {
                setResumeId(null);
                setJobId(null);
                setMatchResult(null);
                setActiveTab('upload');
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;