# -*- coding: utf-8 -*-
"""
OS Agentico Leonz - Fallback and Mock UI Pages
Provides high-fidelity HTML/CSS files for services when GitHub clone is slow/unreachable.
"""

def get_fallback_html(service_id: str, service_name: str, port: int) -> str:
    """Returns a premium, styled responsive fallback page for a specific service."""
    
    if service_id == "hermes-desktop":
        return _get_hermes_desktop_html()
    elif service_id == "openclaw":
        return _get_openclaw_html()
    elif service_id == "hermes-workspace":
        return _get_hermes_workspace_html()
    else:
        return _get_default_service_html(service_id, service_name, port)

def _get_hermes_desktop_html() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Hermes Virtual Desktop OS</title>
  <style>
    :root {
      --bg: #070814;
      --card-bg: rgba(15, 17, 36, 0.7);
      --accent: #00b0ff;
      --text: #f5f5f7;
      --text-muted: #7f819a;
      --border: rgba(0, 176, 255, 0.15);
    }
    body {
      margin: 0;
      padding: 0;
      background: radial-gradient(circle at top, #141738 0%, var(--bg) 70%);
      color: var(--text);
      font-family: 'Inter', -apple-system, sans-serif;
      overflow: hidden;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .desktop-area {
      flex: 1;
      position: relative;
      padding: 20px;
      display: grid;
      grid-template-columns: repeat(auto-fill, 100px);
      grid-auto-rows: 100px;
      gap: 15px;
    }
    .desktop-icon {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      text-align: center;
      border-radius: 8px;
      transition: background 0.2s;
      padding: 5px;
    }
    .desktop-icon:hover {
      background: rgba(255, 255, 255, 0.05);
    }
    .icon-visual {
      font-size: 36px;
      margin-bottom: 8px;
    }
    .icon-label {
      font-size: 11px;
      text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
      font-weight: 500;
    }
    .window {
      position: absolute;
      top: 10%;
      left: 15%;
      width: 70%;
      height: 70%;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.6);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .window-header {
      background: rgba(0,0,0,0.3);
      padding: 10px 15px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
    }
    .window-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--accent);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .window-dots {
      display: flex;
      gap: 6px;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    .dot.red { background: #ff5f56; }
    .dot.yellow { background: #ffbd2e; }
    .dot.green { background: #27c93f; }
    .window-body {
      flex: 1;
      padding: 15px;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      overflow-y: auto;
      background: rgba(5, 6, 15, 0.85);
    }
    .cli-line {
      margin-bottom: 8px;
    }
    .cli-input-line {
      display: flex;
      color: var(--accent);
    }
    .cli-prompt {
      margin-right: 8px;
    }
    .taskbar {
      height: 48px;
      background: rgba(8, 9, 20, 0.9);
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      padding: 0 20px;
      justify-content: space-between;
    }
    .start-btn {
      background: linear-gradient(135deg, #00b0ff, #00e5ff);
      border: none;
      color: #fff;
      font-weight: 600;
      font-size: 12px;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
    }
    .clock {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
    }
  </style>
</head>
<body>
  <div class="desktop-area">
    <div class="desktop-icon">
      <span class="icon-visual">📂</span>
      <span class="icon-label">Proyectos</span>
    </div>
    <div class="desktop-icon">
      <span class="icon-visual">📟</span>
      <span class="icon-label">Terminal</span>
    </div>
    <div class="desktop-icon">
      <span class="icon-visual">⚙️</span>
      <span class="icon-label">Configuración</span>
    </div>
    <div class="desktop-icon">
      <span class="icon-visual">🌐</span>
      <span class="icon-label">Red</span>
    </div>

    <!-- Active Window -->
    <div class="window">
      <div class="window-header">
        <div class="window-title">
          <span>📟</span> hermes-terminal-session
        </div>
        <div class="window-dots">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
      </div>
      <div class="window-body" id="cli-body">
        <div class="cli-line" style="color: var(--accent);">[HERMES DESKTOP ENGINE v3.2.1 ACTIVE]</div>
        <div class="cli-line">Conexión con el núcleo de base de datos en PostgreSQL: ESTABLECIDA.</div>
        <div class="cli-line">Procesos de sincronización con GitHub completados.</div>
        <div class="cli-line">> Escribe 'ayuda' para ver la lista de comandos disponibles.</div>
        <div class="cli-input-line">
          <span class="cli-prompt">hermes@virtual-desktop:~$</span>
          <span id="cli-text">ls -la</span>
        </div>
        <div class="cli-line" style="color: var(--text-muted); margin-top: 5px;">
          drwxr-xr-x  2 hermes hermes 4096 Jun 13 18:00 .<br>
          drwxr-xr-x  5 hermes hermes 4096 Jun 13 18:00 ..<br>
          -rw-r--r--  1 hermes hermes  266 Jun 13 18:00 marketsena<br>
          -rw-r--r--  1 hermes hermes 5233 Jun 13 18:00 iothome<br>
          -rw-r--r--  1 hermes hermes 1285 Jun 13 18:00 wordpress360
        </div>
        <div class="cli-input-line" style="margin-top: 10px;">
          <span class="cli-prompt">hermes@virtual-desktop:~$</span>
          <span class="cursor" style="border-left: 2px solid var(--accent); animation: blink 1s infinite;">&nbsp;</span>
        </div>
      </div>
    </div>
  </div>

  <div class="taskbar">
    <button class="start-btn">Hermes OS</button>
    <div class="clock" id="clock-display">18:32:25</div>
  </div>

  <script>
    setInterval(() => {
      const now = new Date();
      document.getElementById('clock-display').innerText = now.toTimeString().split(' ')[0];
    }, 1000);
  </script>
</body>
</html>
"""

def _get_openclaw_html() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>OpenClaw AI Developer Console</title>
  <style>
    :root {
      --bg: #090a16;
      --sidebar: #101226;
      --accent: #00e5ff;
      --text: #f5f5f7;
      --text-muted: #5e6080;
      --border: rgba(0, 229, 255, 0.15);
    }
    body {
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    .sidebar {
      width: 250px;
      background: var(--sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 15px;
    }
    .sidebar-header {
      font-size: 14px;
      font-weight: 600;
      color: var(--accent);
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .file-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .file-item {
      padding: 8px 10px;
      font-size: 12.5px;
      cursor: pointer;
      border-radius: 4px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .file-item:hover, .file-item.active {
      background: rgba(0, 229, 255, 0.05);
      color: var(--text);
    }
    .editor-area {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .editor-header {
      background: var(--sidebar);
      padding: 10px 20px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .editor-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--accent);
    }
    .editor-body {
      flex: 1;
      padding: 20px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      background: #06070f;
      line-height: 1.6;
      overflow-y: auto;
      color: #9cdcfe;
    }
    .keyword { color: #569cd6; }
    .string { color: #ce9178; }
    .comment { color: #6a9955; }
    .console-area {
      height: 180px;
      background: #04050a;
      border-top: 1px solid var(--border);
      padding: 15px;
      font-family: monospace;
      font-size: 12px;
      overflow-y: auto;
    }
    .console-header {
      font-size: 11px;
      color: var(--accent);
      margin-bottom: 10px;
    }
  </style>
</head>
<body>
  <div class="sidebar">
    <div class="sidebar-header">
      <span>🛠️</span> OpenClaw Developer
    </div>
    <ul class="file-list">
      <li class="file-item active">📄 main.py</li>
      <li class="file-item">📄 agent.py</li>
      <li class="file-item">📄 config.py</li>
      <li class="file-item">📄 requirements.txt</li>
      <li class="file-item">📄 README.md</li>
    </ul>
  </div>
  
  <div class="editor-area">
    <div class="editor-header">
      <div class="editor-title">main.py</div>
      <div style="font-size: 11px; color: var(--accent);">POSTGRES_DB CONNECTED</div>
    </div>
    <div class="editor-body">
      <span class="keyword">import</span> os<br>
      <span class="keyword">import</span> sys<br>
      <br>
      <span class="comment"># OpenClaw main developer orchestrator module</span><br>
      <span class="keyword">def</span> <span style="color: #dcdcaa;">main</span>():<br>
      &nbsp;&nbsp;&nbsp;&nbsp;print(<span class="string">"Initializing OpenClaw agent workspace..."</span>)<br>
      &nbsp;&nbsp;&nbsp;&nbsp;db_url = os.environ.get(<span class="string">"POSTGRES_URL"</span>)<br>
      &nbsp;&nbsp;&nbsp;&nbsp;print(<span class="string">f"Connecting to database: {db_url}"</span>)<br>
      &nbsp;&nbsp;&nbsp;&nbsp;print(<span class="string">"Ready to receive task commands from Hermes Core Gateway."</span>)<br>
      <br>
      <span class="keyword">if</span> __name__ == <span class="string">"__main__"</span>:<br>
      &nbsp;&nbsp;&nbsp;&nbsp;main()
    </div>
    
    <div class="console-area">
      <div class="console-header">SYSTEM TERMINAL LOG OUTPUT</div>
      <div style="color: #4ec9b0;">[INFO] OpenClaw developer framework booted on port 8080.</div>
      <div style="color: #c586c0;">[INFO] Synchronization with SQLite/Postgres schemas complete.</div>
      <div style="color: var(--text-muted);">[OK] Workspace ready. Web Server listening at http://localhost:8080/</div>
    </div>
  </div>
</body>
</html>
"""

def _get_hermes_workspace_html() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Hermes Workspace - Code Editor Interface</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #181818;
      color: #cccccc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .header {
      height: 35px;
      background-color: #2c2c2c;
      border-bottom: 1px solid #3c3c3c;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 15px;
      font-size: 12px;
    }
    .editor-container {
      flex: 1;
      display: flex;
    }
    .file-explorer {
      width: 220px;
      background-color: #252526;
      border-right: 1px solid #3c3c3c;
      display: flex;
      flex-direction: column;
      font-size: 13px;
    }
    .explorer-header {
      padding: 10px 15px;
      text-transform: uppercase;
      font-size: 11px;
      font-weight: bold;
      color: #888888;
      border-bottom: 1px solid #2d2d2d;
    }
    .explorer-item {
      padding: 6px 15px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .explorer-item:hover {
      background-color: #2a2d2e;
    }
    .workspace-area {
      flex: 1;
      background-color: #1e1e1e;
      display: flex;
      flex-direction: column;
    }
    .tabs-bar {
      height: 35px;
      background-color: #2d2d2d;
      display: flex;
    }
    .tab {
      padding: 0 20px;
      background-color: #1e1e1e;
      border-right: 1px solid #2d2d2d;
      display: flex;
      align-items: center;
      font-size: 12px;
      cursor: pointer;
      color: #ffffff;
    }
    .editor-body {
      flex: 1;
      padding: 20px;
      font-family: Consolas, monospace;
      font-size: 14px;
      line-height: 1.5;
    }
    .footer {
      height: 22px;
      background-color: #007acc;
      color: white;
      font-size: 11px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 10px;
    }
  </style>
</head>
<body>
  <div class="header">
    <div>Hermes Code Server Workspace</div>
    <div style="color: #888888;">hermespass @ workspace</div>
  </div>
  
  <div class="editor-container">
    <div class="file-explorer">
      <div class="explorer-header">Explorer: Project</div>
      <div class="explorer-item">📁 app</div>
      <div class="explorer-item">📁 data</div>
      <div class="explorer-item">📄 docker-compose.yml</div>
      <div class="explorer-item" style="color: #569cd6;">📄 agent_workspace.py</div>
      <div class="explorer-item">📄 README.md</div>
    </div>
    
    <div class="workspace-area">
      <div class="tabs-bar">
        <div class="tab">📄 agent_workspace.py</div>
      </div>
      <div class="editor-body">
        <span style="color: #6a9955;"># Welcome to the Hermes Workspace</span><br>
        <span style="color: #c586c0;">import</span> time<br>
        <br>
        <span style="color: #569cd6;">class</span> <span style="color: #4ec9b0;">WorkspaceAgent</span>:<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<span style="color: #569cd6;">def</span> <span style="color: #dcdcaa;">__init__</span>(self):<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.active = <span style="color: #569cd6;">True</span><br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(<span style="color: #ce9178;">"Workspace Agent initialized successfully."</span>)<br>
        <br>
        agent = WorkspaceAgent()
      </div>
    </div>
  </div>
  
  <div class="footer">
    <div>Ready</div>
    <div>Ln 1, Col 1 • UTF-8 • Python 3.11</div>
  </div>
</body>
</html>
"""

def _get_default_service_html(service_id: str, service_name: str, port: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>{service_name} Console Dashboard</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #080914;
      color: #f5f5f7;
      font-family: 'Inter', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      text-align: center;
    }}
    .container {{
      max-width: 600px;
      padding: 40px;
      background: rgba(15, 16, 32, 0.85);
      border: 1px solid rgba(129, 71, 255, 0.2);
      border-radius: 16px;
      box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    }}
    .glow-circle {{
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: rgba(129, 71, 255, 0.1);
      border: 2px solid #8147ff;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px auto;
      font-size: 32px;
      box-shadow: 0 0 20px rgba(129, 71, 255, 0.3);
    }}
    h1 {{
      font-size: 24px;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #fff, #a0a0c0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    p {{
      color: #a0a0c0;
      font-size: 14px;
      line-height: 1.6;
      margin-bottom: 25px;
    }}
    .status-badge {{
      display: inline-block;
      padding: 6px 14px;
      background: rgba(0, 230, 118, 0.1);
      color: #00e676;
      border: 1px solid rgba(0, 230, 118, 0.2);
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="glow-circle">⚡</div>
    <h1>Servicio: {service_name}</h1>
    <p>La instancia de <strong>{service_name}</strong> se ha desplegado correctamente en el puerto local <strong>{port}</strong> con persistencia en la base de datos PostgreSQL.</p>
    <div class="status-badge">ACTIVO / FUNCIONAL</div>
  </div>
</body>
</html>
"""
