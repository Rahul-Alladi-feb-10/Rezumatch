// src/components/MatchResults.jsx
import { CheckCircle, XCircle, TrendingUp, RotateCcw, Award } from 'lucide-react';
import SkillsChart from './SkillsChart';

export default function MatchResults({ matchResult, onStartOver }) {
  if (!matchResult) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500 text-lg">
          No match results yet. Please upload a resume and job description first.
        </p>
      </div>
    );
  }

  const { result } = matchResult;
  const overallScore = result.overall_score;
  const matchQuality = result.match_quality;
  const componentScores = result.component_scores;
  const skillsDetails = result.skills_details;

  // Determine color based on score
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 65) return 'text-blue-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 65) return 'bg-blue-100';
    if (score >= 50) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <div className="card bg-gradient-to-br from-primary-500 to-purple-600 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Match Result</h2>
            <p className="text-blue-100 text-lg">{matchQuality}</p>
          </div>
          <div className="text-right">
            <div className="text-6xl font-bold">{overallScore}%</div>
            <p className="text-blue-100 mt-2">Overall Score</p>
          </div>
        </div>
      </div>

      {/* Component Scores */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <TrendingUp size={24} />
          Score Breakdown
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(componentScores).map(([key, score]) => {
            const labels = {
              keyword_match: 'Keyword Match',
              semantic_match: 'Semantic Match',
              skills_match: 'Skills Match',
              experience_match: 'Experience Match',
            };

            return (
              <div key={key} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-700">{labels[key]}</span>
                  <span className={`font-bold text-lg ${getScoreColor(score)}`}>
                    {score}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      score >= 80
                        ? 'bg-green-500'
                        : score >= 65
                        ? 'bg-blue-500'
                        : score >= 50
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Score Explanation */}
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Keyword Match:</strong> Measures exact term overlap using TF-IDF (25% weight)<br/>
            <strong>Semantic Match:</strong> Analyzes meaning similarity using AI (35% weight)<br/>
            <strong>Skills Match:</strong> Compares required vs. present skills (30% weight)<br/>
            <strong>Experience Match:</strong> Evaluates years of experience alignment (10% weight)
          </p>
        </div>
      </div>

      {/* Skills Analysis */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Award size={24} />
          Skills Analysis
        </h3>

        {/* Matching Skills */}
        {skillsDetails.matching_skills && skillsDetails.matching_skills.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="text-green-500" size={20} />
              <h4 className="font-semibold text-gray-700">
                Matching Skills ({skillsDetails.match_count}/{skillsDetails.total_required})
              </h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {skillsDetails.matching_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium border border-green-300"
                >
                  ✓ {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Missing Skills */}
        {skillsDetails.missing_skills && skillsDetails.missing_skills.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <XCircle className="text-red-500" size={20} />
              <h4 className="font-semibold text-gray-700">
                Missing Skills ({skillsDetails.missing_skills.length})
              </h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {skillsDetails.missing_skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium border border-red-300"
                >
                  ✗ {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Fuzzy Matches */}
        {skillsDetails.fuzzy_matches && skillsDetails.fuzzy_matches.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="text-yellow-500" size={20} />
              <h4 className="font-semibold text-gray-700">
                Similar Skills Found ({skillsDetails.fuzzy_matches.length})
              </h4>
            </div>
            <div className="space-y-2">
              {skillsDetails.fuzzy_matches.map((match, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-gray-600">Required:</span>
                    <span className="font-medium text-gray-800">{match.required}</span>
                    <span className="text-gray-400">→</span>
                    <span className="text-gray-600">Found:</span>
                    <span className="font-medium text-gray-800">{match.found}</span>
                  </div>
                  <span className="text-sm font-semibold text-yellow-700">
                    {match.similarity}% match
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Skills Chart */}
        <div className="mt-6">
          <SkillsChart
            matchingCount={skillsDetails.match_count}
            missingCount={skillsDetails.missing_skills?.length || 0}
            totalRequired={skillsDetails.total_required}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center gap-4">
        <button
          onClick={onStartOver}
          className="btn-secondary flex items-center gap-2"
        >
          <RotateCcw size={20} />
          Start Over
        </button>
      </div>
    </div>
  );
}