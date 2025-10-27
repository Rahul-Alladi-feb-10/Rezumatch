// src/components/JobInput.jsx
import { useState } from 'react';
import { Briefcase, Loader2, CheckCircle, XCircle, Zap } from 'lucide-react';
import { uploadJob, matchResumeToJob } from '../services/api';

export default function JobInput({ onJobCreated, jobId, resumeId, onMatchComplete }) {
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [matching, setMatching] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.company || !formData.description) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await uploadJob(formData);
      setUploadResult(result);
      onJobCreated(result.job_id);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload job description');
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async () => {
    if (!resumeId || !uploadResult?.job_id) {
      setError('Please upload resume and job description first');
      return;
    }

    setMatching(true);
    setError(null);

    try {
      const result = await matchResumeToJob(resumeId, uploadResult.job_id);
      onMatchComplete(result);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to match resume with job');
    } finally {
      setMatching(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Job Description
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Job Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Title *
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g., Senior Python Developer"
            className="input-field"
          />
        </div>

        {/* Company Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company Name *
          </label>
          <input
            type="text"
            name="company"
            value={formData.company}
            onChange={handleChange}
            placeholder="e.g., Tech Corp"
            className="input-field"
          />
        </div>

        {/* Job Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Description *
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={12}
            placeholder="Paste the full job description here, including requirements, responsibilities, and required skills..."
            className="input-field resize-none"
          />
          <p className="text-xs text-gray-500 mt-1">
            Include required skills, experience level, and key responsibilities for better matching
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
            <XCircle className="text-red-500" size={20} />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              Processing...
            </>
          ) : (
            <>
              <Briefcase size={20} />
              Parse Job Description
            </>
          )}
        </button>
      </form>

      {/* Success Message */}
      {uploadResult && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="text-green-500" size={24} />
            <span className="text-green-700 font-semibold">
              Job description parsed successfully!
            </span>
          </div>

          <div className="space-y-2 text-sm text-gray-700">
            <p><strong>Title:</strong> {uploadResult.data.title}</p>
            <p><strong>Company:</strong> {uploadResult.data.company}</p>
            
            {uploadResult.data.required_skills && uploadResult.data.required_skills.length > 0 && (
              <div className="mt-3">
                <strong>Required Skills Detected:</strong>
                <div className="flex flex-wrap gap-2 mt-2">
                  {uploadResult.data.required_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Match Button */}
          {resumeId && (
            <button
              onClick={handleMatch}
              disabled={matching}
              className="btn-primary w-full mt-4 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-primary-600 hover:from-purple-700 hover:to-primary-700"
            >
              {matching ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Matching...
                </>
              ) : (
                <>
                  <Zap size={20} />
                  Match Resume with Job
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Resume Not Uploaded Warning */}
      {!resumeId && uploadResult && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-700 text-sm">
            ⚠️ Please upload a resume first to match with this job description
          </p>
        </div>
      )}
    </div>
  );
}