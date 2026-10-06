import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import { 
  Briefcase, 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  Layers, 
  BrainCircuit, 
  Award, 
  HelpCircle, 
  Trash2, 
  Copy, 
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Mail,
  Phone,
  ShieldCheck,
  Terminal
} from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000';

const SAMPLE_PRESETS = [
  {
    title: 'Senior Full-Stack AI Engineer',
    jd: `We are looking for a Senior Full-Stack AI Engineer with strong proficiency in Python, FastAPI, and React. 
The ideal candidate will have production experience with Machine Learning, RAG architectures, LangChain, 
and Vector Databases such as Qdrant or ChromaDB. 
Experience with Docker, Kubernetes, PostgreSQL, and AWS cloud deployment is essential. 
The candidate will design scalable microservices and deliver responsive, high-performance web interfaces.`
  },
  {
    title: 'Staff Machine Learning Engineer',
    jd: `Seeking a Staff Machine Learning Engineer to lead our generative AI initiatives. 
Must possess deep expertise in Python, PyTorch, Transformers, Deep Learning, and Natural Language Processing. 
Hands-on experience with HuggingFace, Model Quantization, Scikit-Learn, and distributed training is required. 
Experience with MLOps pipelines using Docker, Kubernetes, and CI/CD is a plus.`
  },
  {
    title: 'Cloud & DevOps Platform Lead',
    jd: `We need a Cloud & DevOps Platform Lead to design resilient cloud infrastructure. 
Required skills include AWS, Terraform, Docker, Kubernetes, CI/CD, Linux, and Bash scripting. 
Proficiency in Python or Go for infrastructure automation, along with PostgreSQL database management 
and microservices architecture experience, is highly desired.`
  }
];

export default function App() {
  const [jobDescription, setJobDescription] = useState(SAMPLE_PRESETS[0].jd);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isScreening, setIsScreening] = useState(false);
  const [screeningStep, setScreeningStep] = useState('');
  const [results, setResults] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [jdMode, setJdMode] = useState('paste'); // 'paste' | 'upload'
  const [jdFileName, setJdFileName] = useState('');
  const [isExtractingJd, setIsExtractingJd] = useState(false);
  const jdFileInputRef = useRef(null);
  const fileInputRef = useRef(null);

  // Fetch backend health on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then(res => res.json())
      .then(data => setHealthStatus(data))
      .catch(() => setHealthStatus({ status: 'offline' }));
  }, []);

  // Process a Job Description File (PDF, TXT, MD)
  const processJdFile = async (file) => {
    if (!file) return;
    const name = file.name.toLowerCase();
    setIsExtractingJd(true);
    setJdFileName(file.name);

    if (name.endsWith('.pdf')) {
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await fetch(`${API_BASE}/api/extract-text`, {
          method: 'POST',
          body: formData,
        });
        if (!res.ok) throw new Error('Failed to extract text from PDF JD.');
        const data = await res.json();
        setJobDescription(data.text);
      } catch (err) {
        alert(`Error extracting PDF JD: ${err.message}`);
        setJdFileName('');
      } finally {
        setIsExtractingJd(false);
      }
    } else {
      // Text or markdown file
      const reader = new FileReader();
      reader.onload = (e) => {
        setJobDescription(e.target.result);
        setIsExtractingJd(false);
      };
      reader.onerror = () => {
        alert('Failed to read text file.');
        setIsExtractingJd(false);
        setJdFileName('');
      };
      reader.readAsText(file);
    }
  };

  const handleJdDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      processJdFile(file);
    }
  };

  const handleJdFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processJdFile(e.target.files[0]);
    }
  };

  const clearJdFile = () => {
    setJdFileName('');
    setJobDescription(SAMPLE_PRESETS[0].jd);
  };

  // Handle Drag & Drop for Candidate Resumes
  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const pdfs = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf' || f.name.endsWith('.pdf'));
      setUploadedFiles(prev => [...prev, ...pdfs]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const pdfs = Array.from(e.target.files).filter(f => f.type === 'application/pdf' || f.name.endsWith('.pdf'));
      setUploadedFiles(prev => [...prev, ...pdfs]);
    }
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Helper to load sample resume for instant demo
  const loadSampleResume = async () => {
    try {
      const sampleText = "John Doe\nExperienced Python and Machine Learning Engineer with SQL, Docker, AWS and React experience.";
      const blob = new Blob([sampleText], { type: 'application/pdf' });
      const file = new File([blob], 'sample_resume.pdf', { type: 'application/pdf' });
      setUploadedFiles(prev => [...prev, file]);
    } catch (e) {
      console.error(e);
    }
  };


  const handleScreen = async () => {
    if (!jobDescription.trim()) {
      alert('Please provide a Job Description.');
      return;
    }
    if (uploadedFiles.length === 0) {
      alert('Please upload at least one PDF resume.');
      return;
    }

    setIsScreening(true);
    setScreeningStep('Parsing PDF geometry & extracting candidate sections...');

    const formData = new FormData();
    formData.append('job_description', jobDescription);
    uploadedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      setTimeout(() => setScreeningStep('Computing chunked sentence embeddings & aspect match...'), 800);
      setTimeout(() => setScreeningStep('Analyzing skill taxonomy & querying Groq AI Co-pilot...'), 1800);

      const res = await fetch(`${API_BASE}/api/screen`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Screening request failed.');
      }

      const data = await res.json();
      setResults(data);

      // Trigger celebratory confetti if any candidate scores >= 75%
      const topScore = data.candidates?.[0]?.ats_score || 0;
      if (topScore >= 75) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      }
    } catch (err) {
      alert(`Screening error: ${err.message}`);
    } finally {
      setIsScreening(false);
      setScreeningStep('');
    }
  };

  const copyQuestions = (questions) => {
    const text = questions.map((q, i) => `${i + 1}. ${q}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-wrapper">
          <div className="brand-icon">
            <BrainCircuit size={28} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 className="brand-title">Aegis ATS</h1>
              <span className="badge badge-indigo">v2.0 PRO</span>
            </div>
            <p className="brand-subtitle">AI Resume Screening, Chunked Embeddings & Recruiter Intelligence</p>
          </div>
        </div>

        <div className="system-status">
          <div className="status-pill">
            <span className="status-dot" style={{ background: healthStatus?.status === 'healthy' ? '#10b981' : '#f43f5e' }}></span>
            FastAPI: {healthStatus?.status === 'healthy' ? 'Online' : 'Connecting...'}
          </div>
          <div className="status-pill">
            <Layers size={13} color="#67e8f9" />
            {healthStatus?.embedding_model || 'SentenceTransformer'}
          </div>
          <div className="status-pill">
            <Terminal size={13} color="#a855f7" />
            MCP Server: Active
          </div>
          <div className="status-pill">
            <ShieldCheck size={13} color="#10b981" />
            Groq LLM: {healthStatus?.llm_configured ? 'Active' : 'Offline'}
          </div>
        </div>
      </header>

      {/* Main Workspace (JD + Upload) */}
      <div className="workspace-grid">
        {/* Left: Job Description */}
        <div 
          className="glass-panel section-card"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleJdDrop}
        >
          <div className="section-header">
            <span className="section-title">
              <Briefcase size={20} color="#818cf8" />
              Target Job Description
            </span>
            <div className="tab-switch">
              <button 
                className={`tab-btn ${jdMode === 'paste' ? 'active' : ''}`}
                onClick={() => setJdMode('paste')}
              >
                <FileText size={13} /> Text / Presets
              </button>
              <button 
                className={`tab-btn ${jdMode === 'upload' ? 'active' : ''}`}
                onClick={() => setJdMode('upload')}
              >
                <UploadCloud size={13} /> Drag & Drop File
              </button>
            </div>
          </div>

          {/* Active File Badge if a file was dropped */}
          {jdFileName && (
            <div className="jd-file-badge">
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={14} />
                Loaded from file: <strong>{jdFileName}</strong>
              </span>
              <button onClick={clearJdFile} title="Clear file and reset to default">
                <XCircle size={15} />
              </button>
            </div>
          )}

          {jdMode === 'paste' ? (
            <>
              <div className="preset-pills">
                <span style={{ fontSize: '0.75rem', color: 'var(--text-faint)', alignSelf: 'center' }}>Presets:</span>
                {SAMPLE_PRESETS.map((p, idx) => (
                  <button 
                    key={idx} 
                    className="preset-btn"
                    onClick={() => { setJdFileName(''); setJobDescription(p.jd); }}
                  >
                    {p.title}
                  </button>
                ))}
              </div>

              <div className="textarea-container">
                <textarea
                  className="jd-textarea"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste job description here, or drag & drop a PDF/TXT file directly into this box..."
                />
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', flex: 1 }}>
              <div 
                className="dropzone"
                onClick={() => jdFileInputRef.current?.click()}
                style={{ padding: '28px 16px' }}
              >
                <input 
                  type="file" 
                  ref={jdFileInputRef} 
                  style={{ display: 'none' }} 
                  accept=".pdf,.txt,.md,.doc,.docx"
                  onChange={handleJdFileSelect}
                />
                <div className="dropzone-icon" style={{ background: 'rgba(6, 182, 212, 0.1)', color: '#06b6d4' }}>
                  <UploadCloud size={26} />
                </div>
                <p style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                  {isExtractingJd ? 'Extracting Job Description text...' : 'Drag & Drop JD file here'}
                </p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Supports PDF, TXT, or Markdown • click to browse
                </p>
              </div>

              <div className="textarea-container">
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px', display: 'block' }}>
                  Extracted JD Preview (Editable)
                </label>
                <textarea
                  className="jd-textarea"
                  style={{ height: '140px' }}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Extracted job description text will appear here..."
                />
              </div>
            </div>
          )}
        </div>

        {/* Right: Resume Upload Dropzone */}
        <div className="glass-panel section-card">
          <div className="section-header">
            <span className="section-title">
              <UploadCloud size={20} color="#38bdf8" />
              Candidate Resumes (PDF)
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }} onClick={loadSampleResume}>
                + Add Demo Resume
              </button>
              <span className="badge badge-cyan">
                {uploadedFiles.length} file{uploadedFiles.length === 1 ? '' : 's'}
              </span>
            </div>
          </div>

          <div 
            className="dropzone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              multiple 
              accept=".pdf"
              onChange={handleFileChange}
            />
            <div className="dropzone-icon">
              <UploadCloud size={26} />
            </div>
            <p style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
              Drag & Drop PDF Resumes here
            </p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              or click to browse from your device
            </p>
          </div>

          {/* Uploaded files list */}
          {uploadedFiles.length > 0 && (
            <div className="uploaded-files-list">
              {uploadedFiles.map((file, idx) => (
                <div key={idx} className="file-item">
                  <span className="file-name">
                    <FileText size={15} color="#818cf8" />
                    {file.name}
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-faint)' }}>
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                  </span>
                  <button 
                    className="file-remove-btn" 
                    onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                    title="Remove file"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Action Banner */}
      <div className="action-banner">
        <div className="banner-content">
          <h3>Neural ATS Matching Engine</h3>
          <p>Multi-aspect chunked embeddings, exact skill coverage & generative recruiter interview co-pilot.</p>
        </div>
        <button 
          className="btn-primary" 
          disabled={isScreening || uploadedFiles.length === 0}
          onClick={handleScreen}
        >
          {isScreening ? (
            <>
              <Sparkles className="animate-pulse-glow" size={18} />
              {screeningStep || 'Screening Candidates...'}
            </>
          ) : (
            <>
              <Sparkles size={18} />
              Run AI Candidate Screening
            </>
          )}
        </button>
      </div>

      {/* Results Section */}
      {results && (
        <div>
          {/* Summary Row */}
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
                <FileText size={22} />
              </div>
              <div>
                <div className="stat-value">{results.total_candidates}</div>
                <div className="stat-label">Candidates Analyzed</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                <Award size={22} />
              </div>
              <div>
                <div className="stat-value">{results.candidates[0]?.ats_score || 0}%</div>
                <div className="stat-label">Top ATS Match Score</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#38bdf8' }}>
                <TrendingUp size={22} />
              </div>
              <div>
                <div className="stat-value">{results.job_description_skills?.length || 0}</div>
                <div className="stat-label">Target Skills Detected in JD</div>
              </div>
            </div>
          </div>

          {/* Target Skills in JD */}
          <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '24px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginRight: '12px' }}>
              Required JD Skills:
            </span>
            <div style={{ display: 'inline-flex', flexWrap: 'wrap', gap: '6px', verticalAlign: 'middle' }}>
              {results.job_description_skills.map((skill, idx) => (
                <span key={idx} className="badge badge-cyan">
                  {skill.toUpperCase()}
                </span>
              ))}
            </div>
          </div>

          {/* Leaderboard */}
          <h2 style={{ fontSize: '1.4rem', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Award color="#fbbf24" size={24} />
            Ranked Candidate Leaderboard
          </h2>

          <div className="leaderboard-container">
            {results.candidates.map((cand, idx) => (
              <div key={idx} className="glass-panel candidate-card">
                {/* Rank Badge */}
                <div className={`rank-circle ${idx === 0 ? 'rank-gold' : idx === 1 ? 'rank-silver' : 'rank-standard'}`}>
                  #{cand.rank}
                </div>

                {/* Info & Contact */}
                <div className="candidate-info">
                  <h4>
                    {cand.name}
                    <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>
                      {cand.filename}
                    </span>
                  </h4>
                  <div style={{ margin: '6px 0', fontSize: '0.88rem', fontWeight: 600, color: '#e2e8f0' }}>
                    {cand.decision}
                  </div>
                  <div className="contact-links">
                    {cand.contact.email ? (
                      <span><Mail size={13} /> {cand.contact.email}</span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)' }}><Mail size={13} /> Email not listed</span>
                    )}
                    {cand.contact.phone ? (
                      <span><Phone size={13} /> {cand.contact.phone}</span>
                    ) : (
                      <span style={{ color: 'var(--text-faint)' }}><Phone size={13} /> Phone not listed</span>
                    )}
                  </div>
                </div>

                {/* Skills Preview */}
                <div className="skills-pill-group">
                  <div>
                    <span className="skills-section-label">Matched Skills ({cand.matched_skills.length})</span>
                    <div className="skill-tags-wrapper" style={{ marginTop: '4px' }}>
                      {cand.matched_skills.slice(0, 5).map((s, i) => (
                        <span key={i} className="badge badge-emerald">✓ {s}</span>
                      ))}
                      {cand.matched_skills.length > 5 && (
                        <span className="badge badge-emerald">+{cand.matched_skills.length - 5} more</span>
                      )}
                      {cand.matched_skills.length === 0 && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-faint)' }}>None identified</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <span className="skills-section-label">Missing Gaps ({cand.missing_skills.length})</span>
                    <div className="skill-tags-wrapper" style={{ marginTop: '4px' }}>
                      {cand.missing_skills.slice(0, 4).map((s, i) => (
                        <span key={i} className="badge badge-rose">✗ {s}</span>
                      ))}
                      {cand.missing_skills.length === 0 && (
                        <span className="badge badge-emerald">100% Complete</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Score & Action Button */}
                <div className="score-display">
                  <div className="ats-metric-gauge">
                    {cand.ats_score}%
                  </div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    OVERALL ATS
                  </div>
                  <div className="gauge-submetrics">
                    <span>Semantic: {cand.semantic_score}%</span>
                    <span>•</span>
                    <span>Coverage: {cand.skill_coverage}%</span>
                  </div>

                  <button 
                    className="btn-secondary" 
                    style={{ marginTop: '14px', width: '100%', fontSize: '0.8rem' }}
                    onClick={() => setSelectedCandidate(cand)}
                  >
                    Inspect Candidate <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Candidate Deep-Dive Modal */}
      {selectedCandidate && (
        <div className="modal-overlay" onClick={() => setSelectedCandidate(null)}>
          <div className="modal-content glass-panel-elevated" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2 style={{ fontSize: '1.6rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {selectedCandidate.name}
                  <span className="badge badge-indigo">Rank #{selectedCandidate.rank}</span>
                </h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
                  File: {selectedCandidate.filename} • ATS Score: {selectedCandidate.ats_score}%
                </p>
              </div>
              <button className="close-modal-btn" onClick={() => setSelectedCandidate(null)}>
                ✕
              </button>
            </div>

            {/* Recruiter Decision */}
            <div style={{ marginBottom: '20px', padding: '12px 16px', background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: 'var(--radius-sm)' }}>
              <span style={{ fontWeight: 700, color: '#a5b4fc', marginRight: '8px' }}>Recruiter Verdict:</span>
              <span style={{ color: '#fff' }}>{selectedCandidate.decision}</span>
            </div>

            {selectedCandidate.ai ? (
              <>
                {/* Summary */}
                <div className="insight-block">
                  <h4><Sparkles size={16} color="#818cf8" /> AI Candidate Summary</h4>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: '1.7' }}>
                    {selectedCandidate.ai.candidate_summary}
                  </p>
                </div>

                {/* Strengths & Weaknesses Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                  <div className="insight-block" style={{ marginBottom: 0 }}>
                    <h4 style={{ color: '#6ee7b7' }}><CheckCircle2 size={16} /> Key Strengths</h4>
                    <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {selectedCandidate.ai.strengths.map((item, idx) => (
                        <li key={idx} style={{ marginBottom: '6px' }}>{item}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="insight-block" style={{ marginBottom: 0 }}>
                    <h4 style={{ color: '#fcd34d' }}><XCircle size={16} /> Flagged Gaps / Weaknesses</h4>
                    <ul style={{ paddingLeft: '18px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {selectedCandidate.ai.weaknesses.map((item, idx) => (
                        <li key={idx} style={{ marginBottom: '6px' }}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Technical Interview Questions */}
                <div className="insight-block">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h4><HelpCircle size={16} color="#38bdf8" /> Tailored Technical Questions</h4>
                    <button 
                      className="btn-secondary" 
                      style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                      onClick={() => copyQuestions(selectedCandidate.ai.technical_questions)}
                    >
                      <Copy size={12} /> {copySuccess ? 'Copied!' : 'Copy to Clipboard'}
                    </button>
                  </div>
                  <div className="question-list">
                    {selectedCandidate.ai.technical_questions.map((q, idx) => (
                      <div key={idx} className="question-item">
                        <span style={{ fontWeight: 700, color: 'var(--accent-primary)', minWidth: '20px' }}>Q{idx + 1}:</span>
                        <span>{q}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Behavioral Questions */}
                <div className="insight-block">
                  <h4><HelpCircle size={16} color="#a855f7" /> Tailored Behavioral Questions</h4>
                  <div className="question-list">
                    {selectedCandidate.ai.behavioral_questions.map((q, idx) => (
                      <div key={idx} className="question-item" style={{ borderLeftColor: 'var(--accent-purple)' }}>
                        <span style={{ fontWeight: 700, color: 'var(--accent-purple)', minWidth: '20px' }}>Q{idx + 1}:</span>
                        <span>{q}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="insight-block" style={{ textAlign: 'center', padding: '30px' }}>
                <p style={{ color: 'var(--text-muted)' }}>
                  Generative AI insights are inactive because GROQ_API_KEY is not set or network is offline.
                  Standard ATS scoring and skill extraction are displayed above.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
