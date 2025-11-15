// src/components/ResumeUpload.jsx
import { useState } from 'react';
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { uploadResume } from '../services/api';

export default function ResumeUpload({ onResumeUploaded, resumeId }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF or DOCX file');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await uploadResume(file);
      setUploadResult(result);
      onResumeUploaded(result.resume_id);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload resume');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Upload Your Resume
      </h2>

      {/* Upload Area */}
      <div className="mb-6">
        <label
          htmlFor="resume-upload"
          className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary-500 transition-colors bg-gray-50"
        >
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload className="w-16 h-16 text-gray-400 mb-4" />
            <p className="mb-2 text-sm text-gray-600">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">PDF or DOCX (MAX. 10MB)</p>
          </div>
          <input
            id="resume-upload"
            type="file"
            className="hidden"
            accept=".pdf,.docx"
            onChange={handleFileChange}
          />
        </label>

        {file && (
          <div className="mt-4 flex items-center gap-3 p-4 bg-blue-50 rounded-lg">
            <FileText className="text-primary-600" size={24} />
            <span className="text-gray-700 font-medium">{file.name}</span>
            <span className="text-gray-500 text-sm ml-auto">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
          <XCircle className="text-red-500" size={20} />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="btn-primary w-full flex items-center justify-center gap-2"
      >
        {uploading ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Uploading...
          </>
        ) : (
          <>
            <Upload size={20} />
            Upload Resume
          </>
        )}
      </button>

      {/* Success Message */}
      {uploadResult && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="text-green-500" size={24} />
            <span className="text-green-700 font-semibold">
              Resume uploaded successfully!
            </span>
          </div>

          <div className="space-y-2 text-sm text-gray-700">
            <p><strong>Filename:</strong> {uploadResult.data.filename}</p>
            <p><strong>Skills Found:</strong> {uploadResult.data.skills_count}</p>
            <p><strong>Education Entries:</strong> {uploadResult.data.education_count}</p>
            <p><strong>Experience Entries:</strong> {uploadResult.data.experience_count}</p>
            
            {uploadResult.data.skills_extracted && (
              <div className="mt-3">
                <strong>Skills Extracted:</strong>
                <div className="flex flex-wrap gap-2 mt-2">
                  {uploadResult.data.skills_extracted.slice(0, 10).map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                  {uploadResult.data.skills_extracted.length > 10 && (
                    <span className="px-3 py-1 bg-gray-200 text-gray-600 rounded-full text-xs">
                      +{uploadResult.data.skills_extracted.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}