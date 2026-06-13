/* ==========================================================================
   OS Agentico Leonz - Interactivity & Logic
   ========================================================================== */

// 1. Initial Tool Dataset
const initialTools = [
  {
    id: 'web-search',
    title: 'Web Search',
    description: 'Search the web and extract information from URLs in real-time.',
    version: 'v2.1.0',
    icon: 'globe',
    active: true,
    type: 'available'
  },
  {
    id: 'browser',
    title: 'Browser',
    description: 'Automate web browsing, click elements, fill forms, and interact with pages.',
    version: 'v1.8.3',
    icon: 'browser',
    active: true,
    type: 'available'
  },
  {
    id: 'terminal',
    title: 'Terminal',
    description: 'Execute shell commands and scripts securely inside a sandboxed environment.',
    version: 'v2.0.1',
    icon: 'terminal',
    active: true,
    type: 'available'
  },
  {
    id: 'file-operations',
    title: 'File Operations',
    description: 'Manage files and directories: read, write, copy, search, and delete.',
    version: 'v1.9.2',
    icon: 'file',
    active: false,
    type: 'available'
  },
  {
    id: 'code-execution',
    title: 'Code Execution',
    description: 'Execute Python, JavaScript, and other programming languages safely.',
    version: 'v2.3.0',
    icon: 'code',
    active: true,
    type: 'available'
  },
  {
    id: 'vision',
    title: 'Vision',
    description: 'Analyze images, perform OCR, and extract structured visual data.',
    version: 'v2.0.0',
    icon: 'eye',
    active: false,
    type: 'available'
  },
  {
    id: 'image-generation',
    title: 'Image Generation',
    description: 'Generate images using DALL-E, Stable Diffusion, and other visual models.',
    version: 'v2.1.3',
    icon: 'image',
    active: true,
    type: 'available'
  },
  {
    id: 'text-to-speech',
    title: 'Text-to-Speech',
    description: 'Convert text strings into natural-sounding speech audio outputs.',
    version: 'v1.7.1',
    icon: 'audio',
    active: false,
    type: 'available'
  },
  {
    id: 'skills',
    title: 'Skills',
    description: 'Create, manage, and execute reusable workflows and skills sequences.',
    version: 'v2.2.0',
    icon: 'puzzle',
    active: true,
    type: 'available'
  },
  {
    id: 'memory',
    title: 'Memory',
    description: 'Store and recall persistent agent knowledge and contextual vectors.',
    version: 'v2.4.1',
    icon: 'brain',
    active: true,
    type: 'available'
  },
  {
    id: 'session-search',
    title: 'Session Search',
    description: 'Search across historical agent conversation transcripts and logs.',
    version: 'v1.6.8',
    icon: 'search-list',
    active: false,
    type: 'available'
  },
  {
    id: 'clarifying-questions',
    title: 'Clarifying Questions',
    description: 'Intercept execution to ask the user for clarification when needed.',
    version: 'v1.5.2',
    icon: 'help',
    active: false,
    type: 'available'
  }
];

// In-memory databases
let tools = [...initialTools];
let activeAgents = [
  {
    name: 'LeonZ Prime',
    llm: 'Gemini 3.5 Pro',
    type: 'Orquestador',
    nodes: ['agent', 'desktop'],
    subagents: [
      { name: 'CodeWorker', llm: 'Llama 3.1 405B' },
      { name: 'QueryHelper', llm: 'Gemini Flash' }
    ]
  }
];
let activeModelsLoaded = 3;
let baseRAMUsage = 6.2; // GB

// UI state
let currentFilter = 'all';
let viewMode = 'grid';

// SVG Icons Map
const SVG_ICONS = {
  globe: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`,
  browser: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>`,
  terminal: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>`,
  file: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
  code: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>`,
  eye: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`,
  image: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>`,
  audio: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`,
  puzzle: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="M12 6v6l4 2"></path></svg>`,
  brain: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3 3 0 0 1 0-3.88 2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2zM14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 0-3.12 3 3 0 0 0 0-3.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2z"></path></svg>`,
  'search-list': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="8" x2="14" y2="8"></line><line x1="8" y1="12" x2="12" y2="12"></line></svg>`,
  help: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
  default: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`,
  
  // Custom high-fidelity brand logos for agent nodes
  hermes: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><path d="M5 8h14M12 2v20M8 12h8" /></svg>`,
  desktop: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" /><polyline points="6 8 10 11 6 14" /></svg>`,
  workspace: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2" /><polygon points="2 17 12 22 22 17" /><polygon points="2 12 12 17 22 12" /><line x1="12" y1="2" x2="12" y2="22" stroke-dasharray="2 2" /></svg>`,
  n8n: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="12" r="3.5" stroke="#ff6d00" stroke-width="2.5"/><circle cx="17" cy="12" r="3.5" stroke="#ff1744" stroke-width="2.5"/><path d="M10.5 12h3" stroke="currentColor" stroke-width="2.5"/><path d="M7 8.5a5 5 0 0 1 10 0" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/></svg>`,
  openclaw: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v5" /><path d="M14 10V5a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v5" /><path d="M10 10V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8" /><path d="M6 14v-2a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v6c0 4.5 4 7 8 7h3a5 5 0 0 0 5-5v-6" /></svg>`,
  crewai: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10" stroke-dasharray="3 3"/><circle cx="12" cy="7" r="2" fill="currentColor"/><circle cx="7" cy="15" r="2" fill="currentColor"/><circle cx="17" cy="15" r="2" fill="currentColor"/><path d="M12 9v4M7 13l5-1M17 13l-5-1" stroke-linecap="round"/></svg>`,
  autogpt: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2" /><path d="M12 2v3M9 5h6M7 11V9a5 5 0 0 1 10 0v2M8 15h.01M16 15h.01M12 18h2" /></svg>`,
  langflow: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="6" height="6" rx="1" /><rect x="15" y="3" width="6" height="6" rx="1" /><rect x="9" y="15" width="6" height="6" rx="1" /><path d="M6 9v2a2 2 0 0 0 2 2h4M18 9v2a2 2 0 0 1-2 2h-1" /><path d="M12 13l3 4.5M12 13l-3 4.5" /></svg>`,
  autogen: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3.2" /><circle cx="18" cy="6" r="3.2" /><circle cx="12" cy="18" r="3.2" /><line x1="8.12" y1="8.12" x2="15.88" y2="15.88" /><line x1="15.88" y1="8.12" x2="8.12" y2="15.88" /><line x1="9.2" y1="6" x2="14.8" y2="6" /></svg>`,
  langgraph: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2.5" fill="currentColor"/><circle cx="5" cy="15" r="2.5"/><circle cx="19" cy="15" r="2.5"/><path d="M10 6.5l-3.5 6M14 6.5l3.5 6M7.5 15h9M5.5 17.5c1 2.5 3.5 4 6.5 4s5.5-1.5 6.5-4" stroke-dasharray="2 2"/></svg>`,
  devika: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" /></svg>`,
  chatdev: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="14" rx="2" /><path d="M21 17l-4 4v-4H3" /><polyline points="8 8 11 10 8 12" /><line x1="13" y1="12" x2="16" y2="12" /></svg>`
};

// 2. Initialize App
document.addEventListener('DOMContentLoaded', () => {
  setupNavigationFlow();
  setupAuthFlow();
  setupSPARouter();
  
  setupNavbarInteractivity();
  setupFilterTabs();
  setupLayoutSwitches();
  setupSearch();
  setupModals();
  setupHardwareSimulation();
  setupAgentActivityChart();
  setupUptimeCounter();
  setupSidebarToggle();
  setupThemeToggle();
  setupVoiceCommands();
  
  setupOrchestratorBuilder();
  setupInteractiveChat();
  setupModelToggles();
  setupKnowledgeIngest();
  setupVectorMemorySearch();
  setupNodeServices();

  // Initial render
  updateCounts();
  filterAndRenderTools();
  renderAgentsGrid();
});

// ==========================================================================
// 3. Navigation flow: Landing -> Login -> MFA -> Dashboard
// ==========================================================================
function setupNavigationFlow() {
  const btnGotoLoginHeader = document.getElementById('btn-goto-login-header');
  const btnGotoLoginHero = document.getElementById('btn-goto-login-hero');
  const btnBackToLandingLogin = document.getElementById('btn-back-to-landing-login');
  
  const landingState = document.getElementById('app-landing');
  const authState = document.getElementById('app-auth');
  
  btnGotoLoginHeader.addEventListener('click', () => {
    landingState.classList.remove('active');
    authState.classList.add('active');
  });

  btnGotoLoginHero.addEventListener('click', () => {
    landingState.classList.remove('active');
    authState.classList.add('active');
  });

  btnBackToLandingLogin.addEventListener('click', () => {
    authState.classList.remove('active');
    landingState.classList.add('active');
  });

  // Logout trigger from profile card
  const profileTrigger = document.getElementById('profile-menu-trigger');
  if (profileTrigger) {
    profileTrigger.addEventListener('click', () => {
      if (confirm('¿Desea cerrar sesión y volver a la Landing Page?')) {
        document.getElementById('app-dashboard').classList.remove('active');
        landingState.classList.add('active');
        showToast('Sesión cerrada con éxito.', 'info');
      }
    });
  }
}

// ==========================================================================
// 4. Credentials & MFA Login Flow
// ==========================================================================
function setupAuthFlow() {
  const formLogin = document.getElementById('form-login');
  const formMfa = document.getElementById('form-mfa');
  const loginStep = document.getElementById('auth-login-step');
  const mfaStep = document.getElementById('auth-mfa-step');
  const btnBackToLogin = document.getElementById('btn-back-to-login');
  
  // Login Submitting
  formLogin.addEventListener('submit', (e) => {
    e.preventDefault();
    loginStep.style.display = 'none';
    mfaStep.style.display = 'block';
    
    showToast('Código MFA de 6 dígitos enviado (Prueba: 123456)', 'info');
    document.getElementById('digit-1').focus();
  });

  btnBackToLogin.addEventListener('click', () => {
    mfaStep.style.display = 'none';
    loginStep.style.display = 'block';
  });

  // MFA Digits Auto-focus & inputs shifting
  const mfaInputs = document.querySelectorAll('.mfa-digit-input');
  
  mfaInputs.forEach((input, index) => {
    // Focus next on input
    input.addEventListener('input', (e) => {
      const val = e.target.value;
      if (val && index < mfaInputs.length - 1) {
        mfaInputs[index + 1].focus();
      }
      
      // Auto submit on last digit
      const allFilled = Array.from(mfaInputs).every(inp => inp.value !== '');
      if (allFilled) {
        formMfa.dispatchEvent(new Event('submit'));
      }
    });

    // Go back on Backspace
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !input.value && index > 0) {
        mfaInputs[index - 1].focus();
      }
    });
  });

  // Verify MFA and enter Dashboard
  formMfa.addEventListener('submit', (e) => {
    e.preventDefault();
    showToast('Verificando código MFA de doble factor...', 'info');
    
    // Simulate API loading
    setTimeout(() => {
      document.getElementById('app-auth').classList.remove('active');
      document.getElementById('app-dashboard').classList.add('active');
      
      // Clear inputs
      mfaInputs.forEach(inp => inp.value = '');
      mfaStep.style.display = 'none';
      loginStep.style.display = 'block';
      
      showToast('Acceso verificado. ¡Bienvenido LeonZ Prime!', 'success');
      
      // Force redrawing the animated canvas chart
      setupAgentActivityChart();
    }, 1500);
  });
}

// ==========================================================================
// 5. SPA Dashboard Router
// ==========================================================================
function setupSPARouter() {
  const navLinks = document.querySelectorAll('.sidebar-nav .nav-link, .sidebar-nav-system .nav-link');
  
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      
      const targetHash = link.getAttribute('href');
      const targetPanelId = `section-${targetHash.replace('#', '')}`;
      
      // Hide all panels
      document.querySelectorAll('.section-panel').forEach(panel => {
        panel.classList.remove('active');
      });
      
      // Show target panel
      const targetPanel = document.getElementById(targetPanelId);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }
      
      // Toggle sidebar active link class
      document.querySelectorAll('.sidebar-nav .nav-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    });
  });
}

// ==========================================================================
// 6. Sidebar Navigation Link Updates
// ==========================================================================
function setupNavbarInteractivity() {
  // Overridden by SPA Router, but handles notifications if clicked.
}

// ==========================================================================
// 7. Tool Grid Rendering & Filtering
// ==========================================================================
function filterAndRenderTools() {
  const grid = document.getElementById('tools-grid');
  if (!grid) return;
  const query = document.getElementById('search-input').value.toLowerCase().trim();
  
  // Clear Grid
  grid.innerHTML = '';
  
  // Filter Array
  const filtered = tools.filter(tool => {
    const matchesSearch = tool.title.toLowerCase().includes(query) || 
                          tool.description.toLowerCase().includes(query);
                          
    if (!matchesSearch) return false;
    
    switch (currentFilter) {
      case 'active':
        return tool.active === true;
      case 'available':
        return tool.type === 'available';
      case 'disabled':
        return tool.active === false;
      case 'custom':
        return tool.type === 'custom';
      case 'all':
      default:
        return true;
    }
  });
  
  if (filtered.length === 0) {
    grid.innerHTML = `
      <div class="no-results">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="48" height="48" style="color: var(--text-muted); margin-bottom: 12px;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <p>No tools matched your criteria.</p>
      </div>
    `;
    return;
  }
  
  filtered.forEach(tool => {
    const card = document.createElement('div');
    card.className = `tool-card ${tool.active ? 'active-state' : ''}`;
    card.id = `card-${tool.id}`;
    
    const iconSvg = SVG_ICONS[tool.icon] || SVG_ICONS['default'];
    
    card.innerHTML = `
      <div class="tool-card-top">
        <div class="tool-icon-box">
          ${iconSvg}
        </div>
        <div class="tool-meta">
          <h3 class="tool-title">${tool.title}</h3>
        </div>
        <label class="switch" aria-label="Toggle ${tool.title}">
          <input type="checkbox" class="tool-toggle" data-id="${tool.id}" ${tool.active ? 'checked' : ''}>
          <span class="slider"></span>
        </label>
      </div>
      <p class="tool-desc">${tool.description}</p>
      <div class="tool-card-bottom">
        <span class="tool-status">
          <span class="tool-status-dot"></span>
          <span class="status-label-text">${tool.active ? 'Active' : 'Disabled'}</span>
        </span>
        <span class="tool-version">${tool.version}</span>
      </div>
    `;
    
    grid.appendChild(card);
  });
  
  setupCardToggles();
}

function setupCardToggles() {
  const toggles = document.querySelectorAll('.tool-toggle');
  toggles.forEach(toggle => {
    toggle.addEventListener('change', (e) => {
      const toolId = toggle.getAttribute('data-id');
      const isChecked = toggle.checked;
      
      const tool = tools.find(t => t.id === toolId);
      if (tool) {
        tool.active = isChecked;
        
        const card = document.getElementById(`card-${toolId}`);
        if (card) {
          if (isChecked) {
            card.classList.add('active-state');
            card.querySelector('.status-label-text').innerText = 'Active';
          } else {
            card.classList.remove('active-state');
            card.querySelector('.status-label-text').innerText = 'Disabled';
          }
        }
        
        updateCounts();
        
        if (currentFilter !== 'all') {
          setTimeout(() => {
            filterAndRenderTools();
          }, 350);
        }
        
        showToast(
          `Tool <strong>${tool.title}</strong> is now ${isChecked ? 'Active' : 'Disabled'}.`, 
          isChecked ? 'success' : 'warning'
        );
      }
    });
  });
}

function setupFilterTabs() {
  const tabs = document.querySelectorAll('.filter-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentFilter = tab.getAttribute('data-filter');
      filterAndRenderTools();
    });
  });
}

function updateCounts() {
  const activeCount = tools.filter(t => t.active).length;
  const availableCount = tools.filter(t => t.type === 'available').length;
  const disabledCount = tools.filter(t => !t.active).length;
  const customCount = tools.filter(t => t.type === 'custom').length;
  
  const cntAct = document.getElementById('count-active');
  const cntAvail = document.getElementById('count-available');
  const cntDis = document.getElementById('count-disabled');
  const cntCust = document.getElementById('count-custom');
  
  if (cntAct) cntAct.innerText = activeCount;
  if (cntAvail) cntAvail.innerText = availableCount;
  if (cntDis) cntDis.innerText = disabledCount;
  if (cntCust) cntCust.innerText = customCount;
  
  const sidebarActTools = document.getElementById('stat-active-tools');
  if (sidebarActTools) sidebarActTools.innerText = activeCount;
  
  const baseHealth = 85;
  const addedHealth = Math.min(15, activeCount * 1.5);
  const healthScore = Math.round(baseHealth + addedHealth);
  
  const healthScoreText = document.getElementById('health-score-val');
  if (healthScoreText) {
    healthScoreText.innerText = `${healthScore}%`;
  }
  
  const ringFill = document.getElementById('health-ring-fill');
  if (ringFill) {
    const strokeDash = 282.7;
    const offset = strokeDash - (strokeDash * healthScore) / 100;
    ringFill.style.strokeDashoffset = offset;
  }
}

function setupLayoutSwitches() {
  const gridBtn = document.getElementById('view-grid');
  const listBtn = document.getElementById('view-list');
  const toolsGrid = document.getElementById('tools-grid');
  if (!gridBtn || !listBtn) return;
  
  gridBtn.addEventListener('click', () => {
    gridBtn.classList.add('active');
    listBtn.classList.remove('active');
    toolsGrid.classList.remove('list-layout');
    toolsGrid.classList.add('grid-layout');
    viewMode = 'grid';
    filterAndRenderTools();
  });
  
  listBtn.addEventListener('click', () => {
    listBtn.classList.add('active');
    gridBtn.classList.remove('active');
    toolsGrid.classList.remove('grid-layout');
    toolsGrid.classList.add('list-layout');
    viewMode = 'list';
    filterAndRenderTools();
  });
}

// ==========================================================================
// 8. Search Filtering & Keyboard Shortcut
// ==========================================================================
function setupSearch() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;
  
  searchInput.addEventListener('input', () => {
    filterAndRenderTools();
  });
  
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
    }
  });
}

// ==========================================================================
// 9. Simulated Live Hardware Metrics
// ==========================================================================
function setupHardwareSimulation() {
  const sparklineHistory = [23, 22, 24, 25, 23, 21, 23, 24, 23, 25, 23];
  const sparklineCanvas = document.getElementById('sys-load-sparkline');
  
  function drawSparkline() {
    if (!sparklineCanvas) return;
    const ctx = sparklineCanvas.getContext('2d');
    const w = sparklineCanvas.width;
    const h = sparklineCanvas.height;
    
    ctx.clearRect(0, 0, w, h);
    
    const gradient = ctx.createLinearGradient(0, 0, w, 0);
    gradient.addColorStop(0, '#8147ff');
    gradient.addColorStop(1, '#00b0ff');
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 1.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    const len = sparklineHistory.length;
    const step = w / (len - 1);
    
    const minVal = Math.min(...sparklineHistory) - 1;
    const maxVal = Math.max(...sparklineHistory) + 1;
    const range = maxVal - minVal || 1;
    
    for (let i = 0; i < len; i++) {
      const x = i * step;
      const y = h - ((sparklineHistory[i] - minVal) / range) * (h - 4) - 2;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
  }
  
  drawSparkline();
  
  setInterval(() => {
    // Check if dashboard state is active before simulating hardware logs
    if (!document.getElementById('app-dashboard').classList.contains('active')) return;
    
    const cpuVal = Math.max(4, Math.min(95, Math.round(12 + (Math.random() * 8 - 4))));
    const cpuValEl = document.getElementById('val-cpu-usage');
    if (cpuValEl) cpuValEl.innerText = `${cpuVal}%`;
    const cpuProgress = document.getElementById('cpu-progress');
    if (cpuProgress) cpuProgress.style.width = `${cpuVal}%`;
    
    const ramVal = (baseRAMUsage + (Math.random() * 0.4 - 0.2)).toFixed(1);
    const ramValEl = document.getElementById('val-ram-usage');
    if (ramValEl) ramValEl.innerText = `${ramVal} GB / 16 GB`;
    const ramProgress = document.getElementById('ram-progress');
    if (ramProgress) ramProgress.style.width = `${(ramVal / 16 * 100).toFixed(2)}%`;
    
    const widgetMem = Math.max(10, Math.min(99, Math.round(68 + (Math.random() * 4 - 2))));
    const sidebarMem = document.getElementById('stat-memory-pct');
    if (sidebarMem) sidebarMem.innerText = `${widgetMem}%`;
    
    const loadVal = Math.max(10, Math.min(99, Math.round(23 + (Math.random() * 6 - 3))));
    const sysLoadEl = document.getElementById('val-sys-load');
    if (sysLoadEl) sysLoadEl.innerText = `${loadVal}%`;
    
    sparklineHistory.push(loadVal);
    if (sparklineHistory.length > 15) {
      sparklineHistory.shift();
    }
    drawSparkline();
  }, 2500);
}

// ==========================================================================
// 10. Animated Agent Activity Chart (Canvas Waves)
// ==========================================================================
function setupAgentActivityChart() {
  const canvas = document.getElementById('agent-activity-chart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  let animationFrameId;
  let phase = 0;
  
  let pPlanning = 32;
  let pExecuting = 45;
  let pWaiting = 15;
  let pIdle = 8;
  
  const waves = [
    { name: 'Executing', color: '#00e676', amp: 12, freq: 0.02, speed: 0.04, yOffset: 45 },
    { name: 'Planning', color: '#8147ff', amp: 8, freq: 0.015, speed: 0.02, yOffset: 65 },
    { name: 'Waiting', color: '#00b0ff', amp: 6, freq: 0.03, speed: -0.03, yOffset: 80 }
  ];
  
  function draw() {
    // Stop loop if dashboard is hidden to conserve performance
    if (!document.getElementById('app-dashboard').classList.contains('active')) {
      cancelAnimationFrame(animationFrameId);
      return;
    }
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
    ctx.lineWidth = 1;
    for (let i = 20; i < h; i += 20) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(w, i);
      ctx.stroke();
    }
    
    waves.forEach(wave => {
      ctx.beginPath();
      ctx.strokeStyle = wave.color;
      ctx.lineWidth = 1.8;
      
      ctx.shadowBlur = 6;
      ctx.shadowColor = wave.color;
      
      for (let x = 0; x < w; x++) {
        const y = wave.yOffset + Math.sin(x * wave.freq + phase * wave.speed) * wave.amp;
        if (x === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    });
    
    ctx.shadowBlur = 0;
    phase += 1;
    animationFrameId = requestAnimationFrame(draw);
  }
  
  draw();
  
  setInterval(() => {
    if (!document.getElementById('app-dashboard').classList.contains('active')) return;
    const planChange = Math.round(Math.random() * 2 - 1);
    const execChange = Math.round(Math.random() * 2 - 1);
    const waitChange = Math.round(Math.random() * 2 - 1);
    
    pPlanning = Math.max(20, Math.min(50, pPlanning + planChange));
    pExecuting = Math.max(30, Math.min(65, pExecuting + execChange));
    pWaiting = Math.max(10, Math.min(30, pWaiting + waitChange));
    pIdle = 100 - (pPlanning + pExecuting + pWaiting);
    
    const legPlan = document.getElementById('legend-planning-pct');
    const legExec = document.getElementById('legend-executing-pct');
    const legWait = document.getElementById('legend-waiting-pct');
    const legIdle = document.getElementById('legend-idle-pct');
    
    if (legPlan) legPlan.innerText = `${pPlanning}%`;
    if (legExec) legExec.innerText = `${pExecuting}%`;
    if (legWait) legWait.innerText = `${pWaiting}%`;
    if (legIdle) legIdle.innerText = `${pIdle}%`;
  }, 4000);
}

// ==========================================================================
// 11. Incrementing Uptime Counter
// ==========================================================================
function setupUptimeCounter() {
  const uptimeValEl = document.getElementById('val-uptime');
  if (!uptimeValEl) return;
  
  let days = 2;
  let hours = 14;
  let minutes = 32;
  let seconds = 0;
  
  setInterval(() => {
    if (!document.getElementById('app-dashboard').classList.contains('active')) return;
    seconds++;
    if (seconds >= 60) {
      seconds = 0;
      minutes++;
      if (minutes >= 60) {
        minutes = 0;
        hours++;
        if (hours >= 24) {
          hours = 0;
          days++;
        }
      }
    }
    
    const secStr = seconds.toString().padStart(2, '0');
    const minStr = minutes.toString().padStart(2, '0');
    const hrStr = hours.toString().padStart(2, '0');
    
    uptimeValEl.innerText = `${days}d ${hrStr}h ${minStr}m ${secStr}s`;
  }, 1000);
}

// ==========================================================================
// 12. Toast Notifications
// ==========================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let iconSvg = '';
  switch (type) {
    case 'success':
      iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
      break;
    case 'warning':
      iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-orange)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
      break;
    case 'info':
    default:
      iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="var(--accent-blue)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
  }
  
  toast.innerHTML = `
    ${iconSvg}
    <div class="toast-message">${message}</div>
    <span class="toast-close">&times;</span>
  `;
  
  container.appendChild(toast);
  
  toast.querySelector('.toast-close').addEventListener('click', () => {
    dismissToast(toast);
  });
  
  setTimeout(() => {
    dismissToast(toast);
  }, 4000);
}

function dismissToast(toast) {
  if (toast.parentNode) {
    toast.classList.add('fade-out');
    toast.addEventListener('animationend', () => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    });
  }
}

// ==========================================================================
// 13. Modal Dialog Controls
// ==========================================================================
function setupModals() {
  const addToolBtn = document.getElementById('btn-add-tool');
  const addToolModal = document.getElementById('modal-add-tool');
  const closeBtns = document.querySelectorAll('[data-close-modal]');
  
  if (addToolBtn) {
    addToolBtn.addEventListener('click', () => {
      addToolModal.classList.add('active');
    });
  }
  
  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-close-modal');
      const modal = document.getElementById(modalId);
      if (modal) modal.classList.remove('active');
    });
  });
  
  const overlays = document.querySelectorAll('.modal-overlay');
  overlays.forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
      }
    });
  });
  
  const formAddTool = document.getElementById('form-add-tool');
  if (formAddTool) {
    formAddTool.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const title = document.getElementById('new-tool-title').value.trim();
      const description = document.getElementById('new-tool-desc').value.trim();
      const version = document.getElementById('new-tool-version').value.trim();
      const category = document.getElementById('new-tool-category').value;
      const icon = document.getElementById('new-tool-icon').value;
      const isActive = document.getElementById('new-tool-active').checked;
      
      const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      
      if (tools.some(t => t.id === id)) {
        showToast('A tool with this name already exists.', 'warning');
        return;
      }
      
      const newTool = { id, title, description, version, icon, active: isActive, type: category };
      tools.unshift(newTool);
      formAddTool.reset();
      addToolModal.classList.remove('active');
      
      updateCounts();
      filterAndRenderTools();
      showToast(`Tool <strong>${title}</strong> created successfully!`, 'success');
    });
  }
  
  // Quick actions popups mapping
  const actionNewChat = document.getElementById('action-new-chat');
  const actionNewAgent = document.getElementById('action-new-agent');
  const actionImport = document.getElementById('action-import');
  const actionSettings = document.getElementById('action-settings');
  
  const interactiveModal = document.getElementById('modal-interactive');
  const modalTitle = document.getElementById('interactive-modal-title');
  const modalBody = document.getElementById('interactive-modal-body');
  const modalConfirm = document.getElementById('interactive-modal-confirm');
  
  if (actionNewChat) {
    actionNewChat.addEventListener('click', () => {
      modalTitle.innerText = 'Launch New Chat Session';
      modalBody.innerHTML = `
        <div class="form-group">
          <label for="chat-session-name">Session Name</label>
          <input type="text" id="chat-session-name" value="Session #${Math.floor(Math.random()*1000)}" placeholder="e.g. Code Review Chat">
        </div>
        <div class="form-group">
          <label for="chat-agent">Select Agent</label>
          <select id="chat-agent">
            <option value="leonz-prime">LeonZ Prime (Super Admin)</option>
            <option value="researcher">Research Specialist</option>
            <option value="coder">Code Expert</option>
          </select>
        </div>
      `;
      interactiveModal.classList.add('active');
      modalConfirm.onclick = () => {
        const sessionName = document.getElementById('chat-session-name').value;
        interactiveModal.classList.remove('active');
        showToast(`New session <strong>${sessionName}</strong> started!`, 'success');
        addRecentSession(sessionName, 'Just now', '0 tokens', 'blue-theme');
      };
    });
  }

  if (actionNewAgent) {
    actionNewAgent.addEventListener('click', () => {
      // Directs to Agents Panel SPA view instead of modal for richer building!
      interactiveModal.classList.remove('active');
      const agentsLink = document.getElementById('nav-agents');
      if (agentsLink) agentsLink.click();
      showToast('Redirigido al creador de agentes.', 'info');
    });
  }

  if (actionImport) {
    actionImport.addEventListener('click', () => {
      modalTitle.innerText = 'Import Knowledge Dataset';
      modalBody.innerHTML = `
        <div class="form-group">
          <label>File Upload</label>
          <div style="border: 2px dashed var(--border-color); border-radius: 8px; padding: 20px; text-align: center;">
            <p style="color: var(--text-secondary);">Drop files here to vectorise</p>
          </div>
        </div>
      `;
      interactiveModal.classList.add('active');
      modalConfirm.onclick = () => {
        interactiveModal.classList.remove('active');
        showToast('Document import scheduled...', 'info');
      };
    });
  }

  if (actionSettings) {
    actionSettings.addEventListener('click', () => {
      const settingsLink = document.getElementById('nav-settings');
      if (settingsLink) settingsLink.click();
    });
  }
}

// Add a new session to the list helper
function addRecentSession(title, time, tokenMetric, themeClass) {
  const sessionsList = document.getElementById('sessions-list');
  if (!sessionsList) return;
  
  const li = document.createElement('li');
  li.className = 'session-item';
  
  let iconSvg = '';
  if (themeClass === 'blue-theme') {
    iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`;
  } else if (themeClass === 'green-theme') {
    iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>`;
  } else {
    iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>`;
  }
  
  li.innerHTML = `
    <div class="session-icon-container ${themeClass}">
      ${iconSvg}
    </div>
    <div class="session-info-cols">
      <div class="session-meta">
        <span class="session-title">${title}</span>
        <span class="session-time">${time}</span>
      </div>
      <span class="session-metric">${tokenMetric}</span>
    </div>
  `;
  
  sessionsList.insertBefore(li, sessionsList.firstChild);
  
  if (sessionsList.children.length > 5) {
    sessionsList.removeChild(sessionsList.lastChild);
  }
}

// ==========================================================================
// 14. Sidebar Collapse/Expand Settings
// ==========================================================================
function setupSidebarToggle() {
  const toggleBtn = document.getElementById('sidebar-toggle-btn');
  const container = document.querySelector('.app-container');
  if (!toggleBtn || !container) return;
  
  const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
  if (isCollapsed) {
    container.classList.add('sidebar-collapsed');
  }
  
  toggleBtn.addEventListener('click', () => {
    const collapsed = container.classList.toggle('sidebar-collapsed');
    localStorage.setItem('sidebar-collapsed', collapsed);
    showToast(
      `Menú lateral <strong>${collapsed ? 'contraído' : 'expandido'}</strong>.`, 
      'info'
    );
  });
}

// ==========================================================================
// 15. Theme Toggle Settings
// ==========================================================================
function setupThemeToggle() {
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (!themeBtn) return;
  
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-mode');
    updateThemeIcons(true);
  }
  
  themeBtn.addEventListener('click', () => {
    const isLight = document.body.classList.toggle('light-mode');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    updateThemeIcons(isLight);
    showToast(
      `Tema cambiado a modo <strong>${isLight ? 'Claro' : 'Oscuro'}</strong>.`, 
      'info'
    );
  });
}

function updateThemeIcons(isLight) {
  const moonIcon = document.querySelector('.theme-icon-moon');
  const sunIcon = document.querySelector('.theme-icon-sun');
  if (moonIcon && sunIcon) {
    if (isLight) {
      moonIcon.style.display = 'none';
      sunIcon.style.display = 'block';
    } else {
      moonIcon.style.display = 'block';
      sunIcon.style.display = 'none';
    }
  }
}

// ==========================================================================
// 16. Voice Command Settings
// ==========================================================================
let speechRecognitionActive = false;
let recognition = null;

function setupVoiceCommands() {
  const voiceBtn = document.getElementById('voice-command-btn');
  if (!voiceBtn) return;
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = () => {
      speechRecognitionActive = true;
      voiceBtn.classList.add('listening');
      showToast('🎤 Escuchando comandos en español...', 'info');
    };
    
    recognition.onresult = (event) => {
      const command = event.results[0][0].transcript.toLowerCase().trim();
      processVoiceCommand(command);
    };
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'not-allowed') {
        showToast('Acceso al micrófono denegado.', 'warning');
      } else {
        showToast('Error en el reconocimiento de voz.', 'warning');
      }
      cleanupListeningState();
    };
    
    recognition.onend = () => {
      cleanupListeningState();
    };
  }
  
  voiceBtn.addEventListener('click', () => {
    if (speechRecognitionActive) {
      if (recognition) recognition.stop();
      cleanupListeningState();
    } else {
      if (recognition) {
        try {
          recognition.start();
        } catch (e) {
          console.error(e);
        }
      } else {
        simulateVoiceCommand();
      }
    }
  });
  
  function cleanupListeningState() {
    speechRecognitionActive = false;
    voiceBtn.classList.remove('listening');
  }
}

function simulateVoiceCommand() {
  const voiceBtn = document.getElementById('voice-command-btn');
  voiceBtn.classList.add('listening');
  showToast('🎤 Escuchando (Simulación - Navegador no soporta micrófono)...', 'info');
  
  const mockCommands = [
    'modo claro',
    'modo oscuro',
    'activar terminal',
    'desactivar terminal',
    'nuevo chat',
    'buscar código'
  ];
  
  const randomCmd = mockCommands[Math.floor(Math.random() * mockCommands.length)];
  
  setTimeout(() => {
    voiceBtn.classList.remove('listening');
    showToast(`Comando simulado recibido: "<strong>${randomCmd}</strong>"`, 'success');
    processVoiceCommand(randomCmd);
  }, 2500);
}

function processVoiceCommand(command) {
  const cmd = command.toLowerCase().trim();
  
  if (cmd.includes('modo claro') || cmd.includes('tema claro') || cmd.includes('poner claro')) {
    if (!document.body.classList.contains('light-mode')) {
      document.body.classList.add('light-mode');
      localStorage.setItem('theme', 'light');
      updateThemeIcons(true);
      showToast('Tema cambiado a <strong>Claro</strong> por voz.', 'success');
    }
    return;
  }
  
  if (cmd.includes('modo oscuro') || cmd.includes('tema oscuro') || cmd.includes('poner oscuro')) {
    if (document.body.classList.contains('light-mode')) {
      document.body.classList.remove('light-mode');
      localStorage.setItem('theme', 'dark');
      updateThemeIcons(false);
      showToast('Tema cambiado a <strong>Oscuro</strong> por voz.', 'success');
    }
    return;
  }
  
  if (cmd.includes('contraer menú') || cmd.includes('ocultar menú') || cmd.includes('minimizar menú')) {
    const container = document.querySelector('.app-container');
    if (container && !container.classList.contains('sidebar-collapsed')) {
      container.classList.add('sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', 'true');
      showToast('Menú lateral contraído por voz.', 'success');
    }
    return;
  }
  
  if (cmd.includes('expandir menú') || cmd.includes('mostrar menú')) {
    const container = document.querySelector('.app-container');
    if (container && container.classList.contains('sidebar-collapsed')) {
      container.classList.remove('sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', 'false');
      showToast('Menú lateral expandido por voz.', 'success');
    }
    return;
  }
  
  if (cmd.includes('nuevo chat') || cmd.includes('iniciar chat') || cmd.includes('abrir chat')) {
    const actionNewChat = document.getElementById('action-new-chat');
    if (actionNewChat) actionNewChat.click();
    return;
  }
  
  if (cmd.includes('nuevo agente') || cmd.includes('crear agente') || cmd.includes('sintetizar agente')) {
    const agentsLink = document.getElementById('nav-agents');
    if (agentsLink) agentsLink.click();
    return;
  }
  
  if (cmd.includes('importar datos') || cmd.includes('importar archivo')) {
    const actionImport = document.getElementById('action-import');
    if (actionImport) actionImport.click();
    return;
  }
  
  if (cmd.includes('configuración') || cmd.includes('ajustes')) {
    const actionSettings = document.getElementById('action-settings');
    if (actionSettings) actionSettings.click();
    return;
  }
  
  if (cmd.startsWith('buscar ')) {
    const searchTerm = cmd.replace('buscar ', '').trim();
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.value = searchTerm;
      searchInput.focus();
      filterAndRenderTools();
      showToast(`Filtrando herramientas por: "<strong>${searchTerm}</strong>"`, 'success');
    }
    return;
  }
  
  let matchedToolAction = false;
  tools.forEach(tool => {
    const toolNameLower = tool.title.toLowerCase();
    if (cmd === `activar ${toolNameLower}` || cmd === `iniciar ${toolNameLower}`) {
      matchedToolAction = true;
      if (!tool.active) {
        toggleToolState(tool.id, true);
        showToast(`Herramienta <strong>${tool.title}</strong> activada por voz.`, 'success');
      } else {
        showToast(`Herramienta <strong>${tool.title}</strong> ya estaba activa.`, 'info');
      }
    } else if (cmd === `desactivar ${toolNameLower}` || cmd === `apagar ${toolNameLower}`) {
      matchedToolAction = true;
      if (tool.active) {
        toggleToolState(tool.id, false);
        showToast(`Herramienta <strong>${tool.title}</strong> desactivada por voz.`, 'warning');
      } else {
        showToast(`Herramienta <strong>${tool.title}</strong> ya estaba inactiva.`, 'info');
      }
    }
  });
  
  if (!matchedToolAction) {
    showToast(`Comando no reconocido: "${command}".`, 'info');
  }
}

function toggleToolState(toolId, state) {
  const tool = tools.find(t => t.id === toolId);
  if (tool) {
    tool.active = state;
    const toggleCheckbox = document.querySelector(`.tool-toggle[data-id="${toolId}"]`);
    if (toggleCheckbox) {
      toggleCheckbox.checked = state;
      const event = new Event('change');
      toggleCheckbox.dispatchEvent(event);
    } else {
      updateCounts();
    }
  }
}

// ==========================================================================
// 17. Orchestration & Subagent Builder Logic
// ==========================================================================
function setupOrchestratorBuilder() {
  const btnAddSub = document.getElementById('btn-add-subagent-row');
  const subContainer = document.getElementById('subagents-list-container');
  const formOrch = document.getElementById('form-build-orchestrator');
  
  if (btnAddSub && subContainer) {
    btnAddSub.addEventListener('click', () => {
      const row = document.createElement('div');
      row.className = 'subagent-form-row';
      row.innerHTML = `
        <input type="text" class="sub-name" placeholder="Name, e.g. CodeWorker" required>
        <select class="sub-llm">
          <option value="llama-405b">Llama 3.1 405B</option>
          <option value="gemini-flash">Gemini 3.5 Flash</option>
          <option value="phi-3">Phi-3 Medium</option>
        </select>
        <button type="button" class="btn-remove-sub-row" onclick="this.closest('.subagent-form-row').remove();">&times;</button>
      `;
      subContainer.appendChild(row);
      subContainer.scrollTop = subContainer.scrollHeight;
    });
  }

  if (formOrch) {
    formOrch.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const name = document.getElementById('orch-name').value.trim();
      const llmText = document.getElementById('orch-llm').options[document.getElementById('orch-llm').selectedIndex].text;
      
      const nodeAgent = document.getElementById('node-agent').checked;
      const nodeDesktop = document.getElementById('node-desktop').checked;
      const nodeWorkspace = document.getElementById('node-workspace').checked;
      
      const nodes = [];
      if (nodeAgent) nodes.push('agent');
      if (nodeDesktop) nodes.push('desktop');
      if (nodeWorkspace) nodes.push('workspace');
      
      const subagentRows = document.querySelectorAll('.subagent-form-row');
      const subagents = [];
      subagentRows.forEach(row => {
        const subName = row.querySelector('.sub-name').value.trim();
        const subLlmSelect = row.querySelector('.sub-llm');
        const subLlmText = subLlmSelect.options[subLlmSelect.selectedIndex].text;
        subagents.push({ name: subName, llm: subLlmText });
      });

      const newAgent = { name, llm: llmText, type: 'Orquestador', nodes, subagents };
      activeAgents.unshift(newAgent);
      
      // Clear form
      formOrch.reset();
      subContainer.innerHTML = '';
      
      // Update Grid Directory
      renderAgentsGrid();
      
      // Increment stats
      const actAgentsEl = document.getElementById('stat-active-agents');
      if (actAgentsEl) {
        const cur = parseInt(actAgentsEl.innerText);
        actAgentsEl.innerText = cur + 1;
      }
      
      // Add a running session for this orchestrator
      const sessionTableBody = document.getElementById('sessions-table-body');
      if (sessionTableBody) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${name} Loop</td>
          <td>${name}</td>
          <td><span class="badge badge-success">Running</span></td>
          <td>0 tokens</td>
          <td>0m 01s</td>
          <td><button class="btn btn-secondary btn-xs">Pausar</button></td>
        `;
        sessionTableBody.insertBefore(tr, sessionTableBody.firstChild);
      }
      
      showToast(`Orquestador <strong>${name}</strong> instanciado y lanzado con éxito.`, 'success');
    });
  }
}

function renderAgentsGrid() {
  const container = document.getElementById('agents-grid-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  activeAgents.forEach(agent => {
    const card = document.createElement('div');
    card.className = 'agent-card';
    
    let subagentsHtml = '';
    if (agent.subagents.length > 0) {
      const listItems = agent.subagents.map(sub => `<li>${sub.name} ➔ ${sub.llm}</li>`).join('');
      subagentsHtml = `
        <div class="subagents-assigned-box" style="margin-top: 6px;">
          <h5>Subagentes (${agent.subagents.length}):</h5>
          <ul>${listItems}</ul>
        </div>
      `;
    }
    
    const nodePills = ['agent', 'desktop', 'workspace'].map(node => {
      const active = agent.nodes.includes(node);
      return `<span class="node-pill ${active ? 'active' : ''}">${node.charAt(0).toUpperCase() + node.slice(1)}</span>`;
    }).join('');

    card.innerHTML = `
      <div class="agent-card-header">
        <span class="agent-status-dot active"></span>
        <h4>${agent.name}</h4>
        <span class="agent-type-badge">${agent.type}</span>
      </div>
      <p class="agent-prompt"><strong>LLM Base:</strong> ${agent.llm}</p>
      <div class="agent-card-nodes" style="margin: 4px 0;">
        ${nodePills}
      </div>
      ${subagentsHtml}
    `;
    
    container.appendChild(card);
  });
}

// ==========================================================================
// 18. Interactive Chat Console & Simulated Replies
// ==========================================================================
function setupInteractiveChat() {
  const btnSend = document.getElementById('btn-chat-send');
  const inputField = document.getElementById('chat-input-field');
  const chatMessages = document.getElementById('chat-messages-container');
  const terminalConsole = document.getElementById('chat-terminal-console');
  
  if (!btnSend || !inputField || !chatMessages) return;
  
  function triggerSendMessage() {
    const text = inputField.value.trim();
    if (!text) return;
    
    // Clear Input
    inputField.value = '';
    
    // Append User Message
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    userBubble.innerHTML = `
      <span class="bubble-sender">Administrador</span>
      <p>${text}</p>
      <span class="bubble-time">Recién</span>
    `;
    chatMessages.appendChild(userBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Simulate terminal outputs
    simulateTerminalLogs(text);
    
    // Show typing bubble
    const typingBubble = document.createElement('div');
    typingBubble.className = 'chat-bubble agent typing-indicator-bubble';
    typingBubble.id = 'chat-typing-indicator';
    typingBubble.innerHTML = `
      <span class="bubble-sender">${document.getElementById('chat-agent-selector').value === 'leonz-prime' ? 'LeonZ Prime' : 'Subagente'}</span>
      <p style="color: var(--text-muted);">Analizando directiva...</p>
    `;
    chatMessages.appendChild(typingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  btnSend.addEventListener('click', triggerSendMessage);
  inputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      triggerSendMessage();
    }
  });

  function simulateTerminalLogs(directive) {
    const logs = [
      `[CORE] Directiva recibida: "${directive}"`,
      `[GATEWAY] Invocando agente selector: LeonZ Prime...`,
      `[MEMORY] Recuperando datos de la base "Leonz_Docs_Core"...`,
      `[MODEL] Evaluando contexto semántico y tokens...`,
      `[ORCHESTRATOR] Subagentes en espera de subtarea.`
    ];
    
    terminalConsole.innerHTML = '';
    
    logs.forEach((log, index) => {
      setTimeout(() => {
        const p = document.createElement('p');
        p.className = log.includes('[CORE]') ? 'con-info' : log.includes('[MEMORY]') ? 'con-success' : 'con-info';
        p.innerText = log;
        terminalConsole.appendChild(p);
        terminalConsole.scrollTop = terminalConsole.scrollHeight;
      }, index * 400);
    });
    
    // Respond to user
    setTimeout(() => {
      // Remove typing bubble
      const typing = document.getElementById('chat-typing-indicator');
      if (typing) typing.remove();
      
      // Determine Reply Content
      let replyText = 'Entendido. He procesado tu directiva. Iniciando ciclos lógicos correspondientes.';
      const cleanDir = directive.toLowerCase();
      
      if (cleanDir.includes('hola') || cleanDir.includes('saludos')) {
        replyText = 'Saludos, Comandante. ¿Deseas mapear un nuevo agente orquestador o necesitas un informe de rendimiento del sistema?';
      } else if (cleanDir.includes('ayuda')) {
        replyText = 'Lista de operaciones por chat:\n- "ayuda": Muestra esta lista.\n- "limpiar": Borra la consola.\n- "ejecutar [herramienta]": Lanza el ciclo de una herramienta.';
      } else if (cleanDir.includes('limpiar')) {
        chatMessages.innerHTML = '';
        replyText = 'Chat limpiado. Consola de directivas lista.';
      } else if (cleanDir.includes('modelos') || cleanDir.includes('llm')) {
        replyText = 'Actualmente contamos con 3 modelos cargados en RAM. Gemini 3.5 Pro está respondiendo en este chat.';
      } else if (cleanDir.includes('hardware') || cleanDir.includes('cpu')) {
        replyText = 'El hardware del núcleo se encuentra a un 12% de uso de CPU y 6.2GB de RAM usada.';
      }

      const agentBubble = document.createElement('div');
      agentBubble.className = 'chat-bubble agent';
      agentBubble.innerHTML = `
        <span class="bubble-sender">${document.getElementById('chat-agent-selector').options[document.getElementById('chat-agent-selector').selectedIndex].text}</span>
        <p>${replyText}</p>
        <span class="bubble-time">Hace un momento</span>
      `;
      chatMessages.appendChild(agentBubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      
      // Print final OK in console
      const finalP = document.createElement('p');
      finalP.className = 'con-success';
      finalP.innerText = '[OK] Directiva finalizada. Respuesta transmitida.';
      terminalConsole.appendChild(finalP);
      terminalConsole.scrollTop = terminalConsole.scrollHeight;
    }, 2400);
  }
}

// ==========================================================================
// 19. Model Load/Unload Memory Logic
// ==========================================================================
function setupModelToggles() {
  const toggles = document.querySelectorAll('.model-toggle');
  toggles.forEach(toggle => {
    toggle.addEventListener('change', () => {
      const isChecked = toggle.checked;
      const modelName = toggle.closest('.tool-card').querySelector('.tool-title').innerText;
      const ramUsage = parseFloat(toggle.getAttribute('data-ram'));
      
      const statusText = toggle.closest('.tool-card').querySelector('.tool-status');
      
      if (isChecked) {
        statusText.innerHTML = '<span class="tool-status-dot"></span>Active';
        statusText.closest('.tool-card').classList.add('active-state');
        
        baseRAMUsage += ramUsage;
        activeModelsLoaded++;
        showToast(`Modelo <strong>${modelName}</strong> cargado en memoria RAM (+${ramUsage} GB).`, 'success');
      } else {
        statusText.innerHTML = '<span class="tool-status-dot" style="background-color: var(--text-muted);"></span>Disabled';
        statusText.closest('.tool-card').classList.remove('active-state');
        
        baseRAMUsage = Math.max(1.5, baseRAMUsage - ramUsage);
        activeModelsLoaded = Math.max(0, activeModelsLoaded - 1);
        showToast(`Modelo <strong>${modelName}</strong> descargado de la memoria RAM (-${ramUsage} GB).`, 'warning');
      }
      
      // Update Overview stats counter
      const modelsStat = document.querySelector('.overview-stats .stat-row:nth-child(3) strong');
      if (modelsStat) {
        modelsStat.innerText = activeModelsLoaded;
      }
    });
  });
}

// ==========================================================================
// 20. Knowledge Base Ingest Logic
// ==========================================================================
function setupKnowledgeIngest() {
  const btnIngest = document.getElementById('btn-ingest-knowledge');
  const urlInput = document.getElementById('knowledge-url-input');
  
  if (btnIngest && urlInput) {
    btnIngest.addEventListener('click', () => {
      const val = urlInput.value.trim();
      if (!val) {
        showToast('Ingresa una URL o ruta de archivo válida.', 'warning');
        return;
      }
      
      urlInput.value = '';
      showToast(`Ingestando y analizando contenidos de: ${val}...`, 'info');
      
      // Simulate indexing progress
      setTimeout(() => {
        showToast('Vectores calculados e insertados en la base de datos.', 'success');
        
        // Add row to table
        const tableBody = document.querySelector('#section-knowledge table tbody');
        if (tableBody) {
          const tr = document.createElement('tr');
          const colName = val.replace('https://', '').replace('http://', '').split('/')[0] + '_Knowledge';
          tr.innerHTML = `
            <td>${colName}</td>
            <td>184 vectores</td>
            <td>512 chars</td>
            <td>Just now</td>
            <td><span class="badge badge-success">Completo</span></td>
          `;
          tableBody.appendChild(tr);
        }
      }, 2000);
    });
  }
}

// ==========================================================================
// 21. Vector Memory Search Engine
// ==========================================================================
function setupVectorMemorySearch() {
  const btnSearch = document.getElementById('btn-search-memory');
  const inputField = document.getElementById('memory-search-field');
  const resultsBox = document.getElementById('memory-search-results');
  
  if (!btnSearch || !inputField || !resultsBox) return;
  
  btnSearch.addEventListener('click', () => {
    const val = inputField.value.trim();
    if (!val) {
      showToast('Escribe una consulta de búsqueda.', 'warning');
      return;
    }
    
    resultsBox.innerHTML = '<p style="color: var(--accent-purple-active)">Buscando similitudes vectoriales en base "Leonz_Docs_Core"...</p>';
    
    setTimeout(() => {
      resultsBox.innerHTML = `
        <p class="con-success">[OK] Búsqueda finalizada. Distancia de coseno: 0.18</p>
        <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; margin-top: 8px;">
          <p style="color: var(--text-primary);"><strong>ID: Chunk_242_LeonzCore:</strong></p>
          <p style="color: var(--text-secondary); font-style: italic; margin-left: 10px;">"...la arquitectura SPA del sistema orquestador OS Agentico Leonz vincula los subagentes mediante hilos de ejecución WebSocket bidireccionales, permitiendo asignación granular de modelos..."</p>
        </div>
      `;
    }, 1200);
  });
}

// ==========================================================================
// 22. Third-Party Integration Nodes & Services Logic
// ==========================================================================
const nodeServices = [
  {
    id: 'hermes-agent',
    name: 'Hermes Agent',
    description: 'Núcleo autónomo de toma de decisiones vía API y CLI.',
    status: 'online',
    icon: 'hermes',
    port: '8081',
    color: '#8147ff',
    bgColor: 'rgba(129, 71, 255, 0.08)',
    borderColor: 'rgba(129, 71, 255, 0.2)'
  },
  {
    id: 'hermes-desktop',
    name: 'Hermes Desktop',
    description: 'Entorno de ejecución local con acceso a sistema de archivos y terminal.',
    status: 'online',
    icon: 'desktop',
    port: '8082',
    color: '#00b0ff',
    bgColor: 'rgba(0, 176, 255, 0.08)',
    borderColor: 'rgba(0, 176, 255, 0.2)'
  },
  {
    id: 'hermes-workspace',
    name: 'Hermes Workspace',
    description: 'Espacio de trabajo compartido en la nube con repositorios y directorios aislados.',
    status: 'offline',
    icon: 'workspace',
    port: '8083',
    color: '#00e676',
    bgColor: 'rgba(0, 230, 118, 0.08)',
    borderColor: 'rgba(0, 230, 118, 0.2)'
  },
  {
    id: 'n8n',
    name: 'n8n Automation',
    description: 'Automatización de flujos de trabajo conectando nodos y APIs de terceros.',
    status: 'offline',
    icon: 'n8n',
    port: '5678',
    color: '#ff6d00',
    bgColor: 'rgba(255, 109, 0, 0.08)',
    borderColor: 'rgba(255, 109, 0, 0.2)'
  },
  {
    id: 'openclaw',
    name: 'OpenClaw / OpenHands',
    description: 'Agente desarrollador autónomo que escribe código y ejecuta comandos en sandbox.',
    status: 'offline',
    icon: 'openclaw',
    port: '3000',
    color: '#00e5ff',
    bgColor: 'rgba(0, 229, 255, 0.08)',
    borderColor: 'rgba(0, 229, 255, 0.2)'
  },
  {
    id: 'crewai',
    name: 'CrewAI Framework',
    description: 'Orquestador de equipos de agentes AI colaborativos con roles definidos.',
    status: 'offline',
    icon: 'crewai',
    port: '8010',
    color: '#7c4dff',
    bgColor: 'rgba(124, 77, 255, 0.08)',
    borderColor: 'rgba(124, 77, 255, 0.2)'
  },
  {
    id: 'autogpt',
    name: 'AutoGPT Node',
    description: 'Agente autónomo de bucle continuo para resolución de objetivos complejos.',
    status: 'offline',
    icon: 'autogpt',
    port: '8012',
    color: '#00e676',
    bgColor: 'rgba(0, 230, 118, 0.08)',
    borderColor: 'rgba(0, 230, 118, 0.2)'
  },
  {
    id: 'langflow',
    name: 'Langflow UI',
    description: 'Constructor visual de flujos de trabajo e interfaces gráficas RAG.',
    status: 'offline',
    icon: 'langflow',
    port: '7860',
    color: '#d500f9',
    bgColor: 'rgba(213, 0, 249, 0.08)',
    borderColor: 'rgba(213, 0, 249, 0.2)'
  },
  {
    id: 'autogen',
    name: 'Microsoft AutoGen',
    description: 'Framework multi-agente para configurar flujos conversacionales de resolución de tareas.',
    status: 'offline',
    icon: 'autogen',
    port: '8015',
    color: '#2979ff',
    bgColor: 'rgba(41, 121, 255, 0.08)',
    borderColor: 'rgba(41, 121, 255, 0.2)'
  },
  {
    id: 'langgraph',
    name: 'LangGraph Nodes',
    description: 'Orquestación cíclica y persistente de agentes complejos basada en grafos.',
    status: 'offline',
    icon: 'langgraph',
    port: '8016',
    color: '#00e5ff',
    bgColor: 'rgba(0, 229, 255, 0.08)',
    borderColor: 'rgba(0, 229, 255, 0.2)'
  },
  {
    id: 'devika',
    name: 'Devika Agent',
    description: 'Asistente de codificación y desarrollo de software autónomo open-source.',
    status: 'offline',
    icon: 'devika',
    port: '8018',
    color: '#ffc400',
    bgColor: 'rgba(255, 196, 0, 0.08)',
    borderColor: 'rgba(255, 196, 0, 0.2)'
  },
  {
    id: 'chatdev',
    name: 'ChatDev Virtual',
    description: 'Entorno virtual simulado para creación cooperativa de software mediante agentes.',
    status: 'offline',
    icon: 'chatdev',
    port: '8020',
    color: '#00e676',
    bgColor: 'rgba(0, 230, 118, 0.08)',
    borderColor: 'rgba(0, 230, 118, 0.2)'
  }
];

async function setupNodeServices() {
  try {
    const response = await fetch('/api/v1/services');
    if (response.ok) {
      const services = await response.json();
      services.forEach(s => {
        const localSrv = nodeServices.find(ls => ls.id === s.id);
        if (localSrv) {
          localSrv.status = s.status === 'active' ? 'online' : 'offline';
        }
      });
    }
  } catch (e) {
    console.error("Failed to load backend services, falling back to local simulation:", e);
  }
  renderNodeServices();
  setupGlobalServiceButtons();
}

function renderNodeServices() {
  const container = document.getElementById('nodes-services-grid');
  if (!container) return;
  
  container.innerHTML = '';
  
  nodeServices.forEach(srv => {
    const card = document.createElement('div');
    const isRunning = srv.status === 'online';
    card.className = `node-service-card ${isRunning ? 'running' : ''}`;
    card.id = `srv-card-${srv.id}`;
    
    if (isRunning) {
      card.style.borderColor = srv.color;
      card.style.boxShadow = `0 8px 24px rgba(0, 0, 0, 0.45), 0 0 15px ${srv.bgColor}`;
    } else {
      card.style.borderColor = '';
      card.style.boxShadow = '';
    }
    
    const iconSvg = SVG_ICONS[srv.icon] || SVG_ICONS['default'];
    
    card.innerHTML = `
      <div class="node-service-card-top">
        <div class="node-icon-box" style="
          color: ${isRunning ? srv.color : 'var(--text-secondary)'};
          background-color: ${isRunning ? srv.bgColor : 'rgba(255, 255, 255, 0.02)'};
          border-color: ${isRunning ? srv.borderColor : 'rgba(255, 255, 255, 0.04)'};
        ">
          ${iconSvg}
        </div>
        <div class="node-meta">
          <h4 class="node-title">${srv.name}</h4>
        </div>
        <span class="node-port" style="
          background-color: ${isRunning ? srv.bgColor : 'rgba(255, 255, 255, 0.04)'};
          color: ${isRunning ? srv.color : 'var(--text-muted)'};
        ">Port ${srv.port}</span>
      </div>
      <p class="node-desc">${srv.description}</p>
      <div class="node-service-card-bottom">
        <span class="node-status" style="
          color: ${isRunning ? srv.color : 'var(--text-muted)'};
        ">
          <span class="node-status-dot" style="
            background-color: ${isRunning ? srv.color : 'var(--text-muted)'};
            box-shadow: ${isRunning ? `0 0 6px ${srv.color}` : 'none'};
          "></span>
          <span class="status-lbl">${isRunning ? 'Activo' : 'Apagado'}</span>
        </span>
        <button class="btn-node-toggle btn-node-action ${isRunning ? 'btn-stop' : 'btn-deploy'}" data-id="${srv.id}">
          ${isRunning ? 'Apagar' : 'Desplegar'}
        </button>
      </div>
    `;
    
    container.appendChild(card);
  });
  
  setupNodeToggleButtons();
}

function setupNodeToggleButtons() {
  const btns = document.querySelectorAll('.btn-node-action');
  btns.forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-id');
      const srv = nodeServices.find(s => s.id === id);
      if (!srv) return;
      
      const isOnline = srv.status === 'online';
      btn.disabled = true;
      
      if (isOnline) {
        showToast(`Deteniendo instancia de <strong>${srv.name}</strong>...`, 'warning');
        try {
          const resp = await fetch(`/api/v1/services/${id}/shutdown`, { method: 'POST' });
          if (resp.ok) {
            srv.status = 'offline';
            showToast(`Instancia <strong>${srv.name}</strong> apagada correctamente.`, 'info');
          } else {
            showToast(`Error al apagar <strong>${srv.name}</strong>.`, 'error');
          }
        } catch (e) {
          srv.status = 'offline';
          showToast(`Instancia <strong>${srv.name}</strong> apagada (Simulado).`, 'info');
        }
      } else {
        showToast(`Desplegando nodo de <strong>${srv.name}</strong> en puerto ${srv.port}...`, 'info');
        try {
          const resp = await fetch(`/api/v1/services/${id}/deploy`, { method: 'POST' });
          if (resp.ok) {
            srv.status = 'online';
            showToast(`Nodo <strong>${srv.name}</strong> desplegado y activo.`, 'success');
          } else {
            showToast(`Error al desplegar <strong>${srv.name}</strong>.`, 'error');
          }
        } catch (e) {
          srv.status = 'online';
          showToast(`Nodo <strong>${srv.name}</strong> desplegado (Simulado).`, 'success');
        }
      }
      
      btn.disabled = false;
      renderNodeServices();
      updateCoreActiveToolsMetric();
    });
  });
}

function setupGlobalServiceButtons() {
  const btnDeployAll = document.getElementById('btn-deploy-all-services');
  const btnShutdownAll = document.getElementById('btn-shutdown-all-services');
  
  if (btnDeployAll) {
    const newBtnDeployAll = btnDeployAll.cloneNode(true);
    btnDeployAll.parentNode.replaceChild(newBtnDeployAll, btnDeployAll);
    newBtnDeployAll.addEventListener('click', async () => {
      showToast('Iniciando despliegue de <strong>todos</strong> los servicios...', 'info');
      try {
        const resp = await fetch('/api/v1/services/deploy-all', { method: 'POST' });
        if (resp.ok) {
          nodeServices.forEach(s => s.status = 'online');
          showToast('Todos los servicios desplegados correctamente.', 'success');
        } else {
          showToast('Error en el despliegue global de servicios.', 'error');
        }
      } catch (e) {
        nodeServices.forEach(s => s.status = 'online');
        showToast('Todos los servicios encendidos (Simulado).', 'success');
      }
      renderNodeServices();
      updateCoreActiveToolsMetric();
    });
  }
  
  if (btnShutdownAll) {
    const newBtnShutdownAll = btnShutdownAll.cloneNode(true);
    btnShutdownAll.parentNode.replaceChild(newBtnShutdownAll, btnShutdownAll);
    newBtnShutdownAll.addEventListener('click', async () => {
      showToast('Deteniendo <strong>todos</strong> los servicios...', 'warning');
      try {
        const resp = await fetch('/api/v1/services/shutdown-all', { method: 'POST' });
        if (resp.ok) {
          nodeServices.forEach(s => s.status = 'offline');
          showToast('Todos los servicios apagados correctamente.', 'info');
        } else {
          showToast('Error al apagar todos los servicios.', 'error');
        }
      } catch (e) {
        nodeServices.forEach(s => s.status = 'offline');
        showToast('Todos los servicios apagados (Simulado).', 'info');
      }
      renderNodeServices();
      updateCoreActiveToolsMetric();
    });
  }
}

function updateCoreActiveToolsMetric() {
  const runningCount = nodeServices.filter(s => s.status === 'online').length;
  const dbConsole = document.getElementById('dashboard-console');
  if (dbConsole) {
    const p = document.createElement('p');
    p.className = 'con-info';
    p.innerText = `[GATEWAY] Nodes synchronization complete. Active third-party agents online: ${runningCount}.`;
    dbConsole.appendChild(p);
    dbConsole.scrollTop = dbConsole.scrollHeight;
  }
}


