// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Resume APIs
export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/resume/upload/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAllResumes = async () => {
  const response = await api.get('/resumes/');
  return response.data;
};

export const getResume = async (resumeId) => {
  const response = await api.get(`/resume/${resumeId}/`);
  return response.data;
};

export const deleteResume = async (resumeId) => {
  const response = await api.delete(`/resume/${resumeId}/delete/`);
  return response.data;
};

// Job APIs
export const uploadJob = async (jobData) => {
  const response = await api.post('/job/upload/', jobData);
  return response.data;
};

export const getAllJobs = async () => {
  const response = await api.get('/jobs/');
  return response.data;
};

export const getJob = async (jobId) => {
  const response = await api.get(`/job/${jobId}/`);
  return response.data;
};

export const deleteJob = async (jobId) => {
  const response = await api.delete(`/job/${jobId}/delete/`);
  return response.data;
};

// Matching APIs
export const matchResumeToJob = async (resumeId, jobId) => {
  const response = await api.post('/match/', {
    resume_id: resumeId,
    job_id: jobId,
  });
  return response.data;
};

export const matchResumeToAllJobs = async (resumeId) => {
  const response = await api.post('/match/resume-to-jobs/', {
    resume_id: resumeId,
  });
  return response.data;
};

export const matchJobToAllResumes = async (jobId) => {
  const response = await api.post('/match/job-to-resumes/', {
    job_id: jobId,
  });
  return response.data;
};

export default api;