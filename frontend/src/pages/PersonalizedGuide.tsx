import { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, Clock, IndianRupee, Zap, ShieldAlert, CheckCircle2, 
  Wrench, Layers, AlertTriangle, Sparkles, ChevronRight, 
  ChevronLeft, Send, Lightbulb, Bot, CheckCircle, RotateCcw
} from 'lucide-react';

import { useScan } from '../context/ScanContext';
import { fetchPersonalizedGuide, sendProjectChatMessage } from '../services/aiService';
import { markProjectComplete } from '../services/dashboardService';
import type { PersonalizedGuideResponse, ChatMessage, PersonalizedGuideRequest } from '../types/ai';

export default function PersonalizedGuide() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { detectionResult, lastPreferences, recordProjectCompletion } = useScan();

  const projectId = searchParams.get('id') || 'plastic-bottle-self-watering-planter';
  const objectName = searchParams.get('object') || detectionResult?.displayName || 'bottle';

  const [guide, setGuide] = useState<PersonalizedGuideResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  // AI Assistant Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([
    "Make it cheaper",
    "Make it easier",
    "Give another idea",
    "I don't have this material",
    "Explain this step"
  ]);
  const [inputMsg, setInputMsg] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    async function loadGuide() {
      setLoading(true);
      setError(null);

      const requestPayload: PersonalizedGuideRequest = {
        project_id: projectId,
        object_name: objectName,
        goal: lastPreferences?.goal || 'gardening',
        available_tools: lastPreferences?.tools || ['scissors'],
        available_materials: lastPreferences?.materials || ['soil'],
        budget_min: lastPreferences?.budget_min || 0,
        budget_max: lastPreferences?.budget_max || 50,
        difficulty: lastPreferences?.difficulty || 'easy',
        max_time_minutes: lastPreferences?.max_time_minutes || 30
      };

      try {
        const data = await fetchPersonalizedGuide(requestPayload);
        setGuide(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load personalized instructions.');
      } finally {
        setLoading(false);
      }
    }

    loadGuide();
  }, [projectId, objectName, lastPreferences]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (customText?: string) => {
    const textToSend = customText || inputMsg;
    if (!textToSend.trim() || chatLoading) return;

    const userMessage: ChatMessage = { role: 'user', content: textToSend };
    const updatedConversation = [...messages, userMessage];

    setMessages(updatedConversation);
    if (!customText) setInputMsg('');
    setChatLoading(true);

    try {
      const response = await sendProjectChatMessage({
        project_context: {
          object: {
            name: objectName,
            material: detectionResult?.material || 'unknown',
            condition: 'used'
          },
          selected_project: {
            title: guide?.title || 'Upcycling Project',
            difficulty: guide?.difficulty || 'easy',
            estimated_time_minutes: guide?.estimated_time_minutes || 30,
            estimated_cost: { min: 0, max: lastPreferences?.budget_max || 50, currency: 'INR' }
          },
          user_preferences: {
            goal: lastPreferences?.goal || 'gardening',
            custom_goal: lastPreferences?.custom_goal,
            budget: lastPreferences?.budget_max || 50,
            time_minutes: lastPreferences?.max_time_minutes || 30,
            difficulty: lastPreferences?.difficulty || 'easy'
          },
          tools: lastPreferences?.tools || [],
          materials: lastPreferences?.materials || [],
          current_step: currentStepIndex + 1
        },
        conversation: updatedConversation,
        message: textToSend
      });

      const assistantMessage: ChatMessage = { role: 'assistant', content: response.message };
      setMessages([...updatedConversation, assistantMessage]);

      if (response.suggestions && response.suggestions.length > 0) {
        setSuggestions(response.suggestions);
      }

      // Handle AI project modifications
      if (response.updated_project && guide) {
        setGuide({
          ...guide,
          title: response.updated_project.title || guide.title,
          estimated_cost: response.updated_project.estimated_cost_max ? `₹0–₹${response.updated_project.estimated_cost_max}` : guide.estimated_cost,
          difficulty: response.updated_project.difficulty || guide.difficulty,
          steps: response.updated_project.steps 
            ? response.updated_project.steps.map((st: string, i: number) => ({ step_number: i + 1, title: `Step ${i + 1}`, description: st }))
            : guide.steps
        });
      }
    } catch {
      setMessages([...updatedConversation, { 
        role: 'assistant', 
        content: 'Regarding your question, proceed carefully using your available tools and materials!' 
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleRestartProject = () => {
    setMessages([]);
    setCurrentStepIndex(0);
  };

  if (loading) {
    return (
      <div className="w-full flex-1 bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 border-4 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mb-4"></div>
        <h2 className="text-2xl font-black text-white mb-2">Generating Personalized Guide...</h2>
        <p className="text-sm text-slate-400 max-w-sm">
          Structuring step-by-step upcycling instructions tailored to your tools and goal.
        </p>
      </div>
    );
  }

  if (error || !guide) {
    return (
      <div className="w-full flex-1 bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
        <AlertTriangle size={48} className="text-amber-400 mb-3" />
        <h2 className="text-2xl font-black text-white mb-2">Personalization Error</h2>
        <p className="text-sm text-slate-400 max-w-sm mb-6">{error || 'Unable to generate personalized instructions.'}</p>
        <Link
          to={`/instructions?id=${projectId}`}
          className="bg-emerald-500 text-slate-950 font-black px-8 py-3.5 rounded-2xl shadow-lg hover:bg-emerald-400 transition-colors"
        >
          View Standard Guide
        </Link>
      </div>
    );
  }

  const steps = guide.steps || [];
  const currentStep = steps[currentStepIndex];
  const isLastStep = currentStepIndex === steps.length - 1;
  const isComplete = currentStepIndex >= steps.length;

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-20">
      
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-6 space-y-6">

        {/* TOP HEADER HERO CARD */}
        <div className="bg-gradient-to-r from-slate-900 via-emerald-950 to-slate-900 rounded-3xl p-6 sm:p-8 border border-emerald-500/30 shadow-2xl relative overflow-hidden">
          
          <div className="flex items-center justify-between mb-4">
            <button 
              onClick={() => navigate('/recommendations')}
              className="p-2.5 bg-slate-950/80 hover:bg-slate-800 text-slate-300 rounded-2xl border border-slate-800 transition-colors inline-flex"
            >
              <ArrowLeft size={20} />
            </button>

            <div className="flex items-center gap-2">
              <button
                onClick={handleRestartProject}
                className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-bold px-3 py-1.5 rounded-xl transition-colors"
              >
                <RotateCcw size={14} /> Start Over
              </button>

              <div className="flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-black px-3.5 py-1.5 rounded-full uppercase tracking-wider">
                <Sparkles size={14} />
                {guide.is_ai_generated ? 'AI Personalized Guide' : 'Standard DIY Guide'}
              </div>
            </div>
          </div>

          <h1 className="text-2xl sm:text-4xl font-black text-white mb-2 leading-tight">🌱 {guide.title}</h1>
          <p className="text-slate-300 text-xs sm:text-sm leading-relaxed max-w-3xl mb-4">{guide.summary}</p>

          <div className="flex flex-wrap items-center gap-4 bg-slate-950/80 p-3 rounded-2xl border border-slate-800 text-xs font-semibold text-slate-300 max-w-xl">
            <span className="flex items-center gap-1.5 text-amber-400"><Clock size={15} /> {guide.estimated_time_minutes} mins</span>
            <span>•</span>
            <span className="flex items-center gap-1.5 text-emerald-400"><IndianRupee size={15} /> {guide.estimated_cost}</span>
            <span>•</span>
            <span className="flex items-center gap-1.5 text-purple-400"><Zap size={15} /> {guide.difficulty}</span>
          </div>

        </div>

        {/* 2-COLUMN DESKTOP RESPONSIVE GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">

          {/* LEFT COLUMN: Materials, Tools & Safety Notes */}
          <div className="space-y-6">

            <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-6">
              <div>
                <h3 className="flex items-center gap-2 font-extrabold text-white text-sm uppercase tracking-wider mb-3">
                  <Layers size={18} className="text-emerald-400" /> Your Materials
                </h3>
                <div className="space-y-2">
                  {guide.materials.map((mat, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-slate-950 rounded-2xl border border-slate-800 text-xs">
                      <span className="font-bold text-white">{mat.name}</span>
                      {mat.available ? (
                        <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1">
                          <CheckCircle size={12} /> Available
                        </span>
                      ) : (
                        <span className="text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 flex items-center gap-1">
                          <AlertTriangle size={12} /> Substitute Needed
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="flex items-center gap-2 font-extrabold text-white text-sm uppercase tracking-wider mb-3">
                  <Wrench size={18} className="text-blue-400" /> Your Tools
                </h3>
                <div className="space-y-2">
                  {guide.tools.map((tool, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-slate-950 rounded-2xl border border-slate-800 text-xs">
                      <span className="font-bold text-white">{tool.name}</span>
                      <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center gap-1">
                        <CheckCircle size={12} /> Available
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {guide.safety_notes && guide.safety_notes.length > 0 && (
              <div className="bg-amber-950/30 rounded-3xl border border-amber-500/20 p-6 shadow-xl">
                <h3 className="flex items-center gap-2 font-extrabold text-amber-400 text-sm uppercase tracking-wider mb-3">
                  <ShieldAlert size={18} /> Safety Considerations
                </h3>
                <ul className="space-y-2 text-xs text-amber-200">
                  {guide.safety_notes.map((note, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{note}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

          </div>

          {/* RIGHT COLUMN: Interactive Step Navigator & AI Assistant */}
          <div className="lg:col-span-2 space-y-6">

            {/* STEP INSTRUCTIONS CARD */}
            <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 sm:p-8 shadow-xl space-y-6">
              
              <div>
                <div className="flex items-center justify-between text-xs font-bold text-slate-400 mb-2">
                  <span>Step {currentStepIndex + 1} of {steps.length}</span>
                  <span className="text-emerald-400">{Math.round(((currentStepIndex + 1) / steps.length) * 100)}% Complete</span>
                </div>
                <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div 
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-300"
                    style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
                  ></div>
                </div>
              </div>

              {!isComplete && currentStep ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center font-black text-base">
                        {currentStep.step_number}
                      </div>
                      <h2 className="font-black text-xl text-white">{currentStep.title}</h2>
                    </div>

                    <button
                      onClick={() => handleSendMessage(`Explain step ${currentStepIndex + 1}`)}
                      className="px-3.5 py-1.5 rounded-xl bg-emerald-950/60 hover:bg-emerald-900/80 text-emerald-400 border border-emerald-500/30 font-bold text-xs flex items-center gap-1.5 transition-colors"
                    >
                      <Lightbulb size={14} /> Explain with AI
                    </button>
                  </div>

                  <p className="text-slate-300 text-sm leading-relaxed font-normal bg-slate-950 p-4 rounded-2xl border border-slate-800">
                    {currentStep.description}
                  </p>

                  {currentStep.tip && (
                    <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-2xl flex items-start gap-3">
                      <Lightbulb size={20} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                      <div className="text-xs text-emerald-200">
                        <strong className="block text-emerald-400 mb-0.5 font-extrabold">Pro Tip:</strong>
                        {currentStep.tip}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                    <button
                      onClick={() => setCurrentStepIndex(prev => Math.max(0, prev - 1))}
                      disabled={currentStepIndex === 0}
                      className="flex items-center gap-1.5 font-bold text-xs px-5 py-3 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 disabled:opacity-40 transition-colors"
                    >
                      <ChevronLeft size={16} />
                      Previous
                    </button>

                    <button
                      onClick={async () => {
                        setCurrentStepIndex(prev => prev + 1);
                        recordProjectCompletion(projectId);
                        await markProjectComplete(projectId);
                      }}
                      className="flex items-center gap-2 font-black text-xs sm:text-sm px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 shadow-lg transition-transform hover:scale-105"
                    >
                      {isLastStep ? 'Mark Project Complete 🎉' : 'Next Step'}
                      <ChevronRight size={18} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 space-y-4">
                  <div className="w-20 h-20 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30">
                    <CheckCircle2 size={48} />
                  </div>
                  <h2 className="text-3xl font-black text-white">Project Complete! 🎉</h2>
                  <p className="text-sm text-slate-300 max-w-sm mx-auto">
                    Awesome job! You successfully upcycled your item and saved it from landfill waste.
                  </p>
                  <div className="flex justify-center gap-4 pt-2">
                    <Link
                      to="/"
                      className="bg-emerald-500 text-slate-950 font-black px-6 py-3 rounded-2xl shadow-lg hover:bg-emerald-400 transition-colors text-sm"
                    >
                      Back to Dashboard
                    </Link>
                  </div>
                </div>
              )}

            </div>

            {/* AI ASSISTANT CHAT PANEL */}
            <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
              
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                    <Bot size={20} />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-white text-sm">✨ Ask AI About Your Project</h3>
                    <p className="text-[10px] text-slate-400">Context-aware assistant for modifications & step guidance</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button 
                    onClick={handleRestartProject}
                    className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 bg-slate-800/60 px-2.5 py-1 rounded-lg"
                  >
                    Clear Chat
                  </button>
                  <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
                    Online
                  </span>
                </div>
              </div>

              {/* Chat Feed */}
              <div className="bg-slate-950 rounded-2xl p-4 border border-slate-800 h-64 overflow-y-auto space-y-3">
                {messages.length === 0 && (
                  <div className="text-center py-6 text-xs text-slate-500 space-y-3">
                    <Bot size={28} className="mx-auto text-slate-600" />
                    <p>Have questions or need to modify this project?</p>
                    <div className="flex flex-wrap justify-center gap-2 pt-1">
                      {suggestions.map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSendMessage(q)}
                          className="bg-slate-900 hover:bg-slate-800 text-emerald-400 text-[11px] font-semibold px-3 py-1.5 rounded-xl border border-slate-800 transition-colors"
                        >
                          "{q}"
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex items-start gap-2 text-xs ${
                      msg.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {msg.role === 'assistant' && (
                      <div className="w-7 h-7 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0 mt-1">
                        <Bot size={14} />
                      </div>
                    )}
                    <div
                      className={`p-3 rounded-2xl max-w-[80%] leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-emerald-500 text-slate-950 font-bold rounded-tr-none'
                          : 'bg-slate-900 text-slate-200 border border-slate-800 rounded-tl-none'
                      }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex items-center gap-2 text-xs text-emerald-400">
                    <Bot size={14} className="animate-spin" /> Thinking...
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Quick Action Chips */}
              <div className="flex flex-wrap gap-1.5">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => handleSendMessage(s)}
                    className="text-[11px] font-semibold text-emerald-400 bg-emerald-950/40 hover:bg-emerald-900/60 px-2.5 py-1 rounded-lg border border-emerald-500/20 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>

              {/* Chat Input Bar */}
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={inputMsg}
                  onChange={(e) => setInputMsg(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask anything about this project..."
                  className="flex-1 bg-slate-950 text-xs text-white px-4 py-3 rounded-2xl border border-slate-800 focus:outline-none focus:border-emerald-500 transition-colors placeholder:text-slate-500"
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={chatLoading || !inputMsg.trim()}
                  className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black p-3 rounded-2xl shadow-md transition-colors disabled:opacity-40 flex-shrink-0"
                >
                  <Send size={18} />
                </button>
              </div>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}
