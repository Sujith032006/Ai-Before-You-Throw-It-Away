import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Clock, IndianRupee, Zap, ShieldAlert, CheckCircle, Wrench, Layers, CheckSquare, Square } from 'lucide-react';
import { fetchProjectDetails } from '../services/recommendationService';
import type { ProjectDetails } from '../types/recommendation';

export default function ProjectInstructions() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const projectId = searchParams.get('id') || 'plastic-bottle-self-watering-planter';

  const [project, setProject] = useState<ProjectDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchProjectDetails(projectId);
        setProject(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load project details.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [projectId]);

  const toggleStep = (index: number) => {
    if (completedSteps.includes(index)) {
      setCompletedSteps(completedSteps.filter(i => i !== index));
    } else {
      setCompletedSteps([...completedSteps, index]);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 p-6 bg-white flex flex-col items-center justify-center">
        <div className="w-12 h-12 border-4 border-green-200 border-t-green-600 rounded-full animate-spin mb-4"></div>
        <p className="text-gray-500 font-medium">Loading project steps...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex-1 p-6 bg-white flex flex-col items-center justify-center text-center">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Project Not Found</h2>
        <p className="text-sm text-gray-500 max-w-xs mb-6">{error || 'Could not find project instructions.'}</p>
        <Link to="/recommendations" className="bg-green-600 text-white font-bold px-5 py-2.5 rounded-xl">
          Back to Recommendations
        </Link>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-white overflow-y-auto pb-16">
      
      {/* Top Banner / Header */}
      <div className="bg-gradient-to-br from-green-700 to-emerald-600 text-white p-6 relative">
        <button 
          onClick={() => navigate('/recommendations')}
          className="p-2 bg-white/20 backdrop-blur-md rounded-full text-white hover:bg-white/30 transition-colors mb-4 inline-flex"
        >
          <ArrowLeft size={18} />
        </button>

        <span className="bg-white/20 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider block w-fit mb-2">
          DIY Upcycling Guide
        </span>
        <h1 className="text-2xl font-extrabold text-white mb-2 leading-tight">{project.name}</h1>
        <p className="text-green-100 text-xs leading-relaxed max-w-sm">{project.description}</p>

        {/* Quick Stats Pill */}
        <div className="flex items-center gap-4 bg-white/10 backdrop-blur-md rounded-xl p-3 mt-4 text-xs font-semibold text-white mb-4">
          <span className="flex items-center gap-1.5"><Zap size={14} className="text-green-300" /> {project.difficulty}</span>
          <span>•</span>
          <span className="flex items-center gap-1.5"><Clock size={14} className="text-amber-300" /> {project.estimated_time_minutes} mins</span>
          <span>•</span>
          <span className="flex items-center gap-1.5"><IndianRupee size={14} className="text-emerald-300" /> ₹{project.estimated_cost_min}–₹{project.estimated_cost_max}</span>
        </div>

        {/* Personalized Guide CTA */}
        <button
          onClick={() => navigate(`/personalized-guide?id=${project.project_id}`)}
          className="w-full bg-emerald-500 hover:bg-emerald-400 text-gray-900 font-extrabold py-3 px-4 rounded-xl shadow-lg transition-transform hover:-translate-y-0.5 flex items-center justify-center gap-2 text-sm border-2 border-white/40"
        >
          <span>✨ Create Personalized Guide</span>
        </button>
      </div>

      <div className="p-6">

        {/* Safety Warning Box */}
        {project.safety_notes && project.safety_notes.length > 0 && (
          <div className="mb-6 bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-start gap-3">
            <ShieldAlert size={20} className="text-amber-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-amber-900 text-xs uppercase tracking-wider mb-1">Safety Notes</h3>
              <ul className="list-disc list-inside text-xs text-amber-800 space-y-1">
                {project.safety_notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Required Tools & Materials */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-blue-50/70 border border-blue-100 p-4 rounded-2xl">
            <h3 className="flex items-center gap-1.5 font-bold text-blue-900 text-xs uppercase tracking-wider mb-2">
              <Wrench size={15} className="text-blue-600" /> Required Tools
            </h3>
            <div className="flex flex-wrap gap-1">
              {project.required_tools.length > 0 ? (
                project.required_tools.map((tool, idx) => (
                  <span key={idx} className="bg-white text-blue-800 text-xs px-2.5 py-1 rounded-lg font-medium border border-blue-200 capitalize">
                    {tool}
                  </span>
                ))
              ) : (
                <span className="text-xs text-blue-600">None required</span>
              )}
            </div>
          </div>

          <div className="bg-teal-50/70 border border-teal-100 p-4 rounded-2xl">
            <h3 className="flex items-center gap-1.5 font-bold text-teal-900 text-xs uppercase tracking-wider mb-2">
              <Layers size={15} className="text-teal-600" /> Materials
            </h3>
            <div className="flex flex-wrap gap-1">
              {project.required_materials.length > 0 ? (
                project.required_materials.map((mat, idx) => (
                  <span key={idx} className="bg-white text-teal-800 text-xs px-2.5 py-1 rounded-lg font-medium border border-teal-200 capitalize">
                    {mat}
                  </span>
                ))
              ) : (
                <span className="text-xs text-teal-600">None required</span>
              )}
            </div>
          </div>
        </div>

        {/* Step by Step Instructions */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">Step-by-Step Guide</h2>
            <span className="text-xs font-semibold text-green-700 bg-green-50 px-2.5 py-1 rounded-full border border-green-200">
              {completedSteps.length} of {project.steps.length} done
            </span>
          </div>

          <div className="space-y-3">
            {project.steps.map((stepText, idx) => {
              const isDone = completedSteps.includes(idx);
              return (
                <div
                  key={idx}
                  onClick={() => toggleStep(idx)}
                  className={`p-4 rounded-2xl border-2 transition-all cursor-pointer flex items-start gap-3 ${
                    isDone 
                      ? 'bg-green-50/80 border-green-300 text-gray-500' 
                      : 'bg-white border-gray-100 hover:border-gray-200 text-gray-800 shadow-sm'
                  }`}
                >
                  <button className="mt-0.5 flex-shrink-0">
                    {isDone ? (
                      <CheckSquare size={20} className="text-green-600" />
                    ) : (
                      <Square size={20} className="text-gray-300" />
                    )}
                  </button>

                  <div className="flex-1">
                    <span className="text-[11px] font-bold text-gray-400 uppercase tracking-widest block mb-0.5">
                      Step {idx + 1}
                    </span>
                    <p className={`text-sm leading-relaxed ${isDone ? 'line-through text-gray-400' : 'font-medium'}`}>
                      {stepText}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Completion Card */}
        {completedSteps.length === project.steps.length && project.steps.length > 0 && (
          <div className="mt-8 bg-green-600 text-white p-6 rounded-2xl text-center shadow-lg animate-bounce-short">
            <CheckCircle size={40} className="mx-auto mb-2 text-green-200" />
            <h3 className="text-lg font-bold">Project Complete! 🎉</h3>
            <p className="text-xs text-green-100 mt-1">You just saved item from being thrown away!</p>
          </div>
        )}

      </div>
    </div>
  );
}
