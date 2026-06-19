# osagentico — Agent Rules
<!-- BEGIN:headroom -->
## Compresión de contexto (Headroom)

Este proyecto usa **Headroom** como capa de compresión de contexto para Claude Code.

### MCP tools disponibles
- headroom_compress — comprime mensajes/tool outputs antes de procesarlos
- headroom_retrieve — recupera el contenido original de un chunk comprimido  
- headroom_stats — muestra tokens ahorrados en la sesión actual

### Cuándo usar headroom_retrieve
Llamá a headroom_retrieve cuando:
- Necesitás el detalle completo de un tool output que fue comprimido
- La respuesta comprimida no tiene suficiente información
- Estás debuggeando y necesitás ver el output original

### Activar Headroom
`ash
# Instalar (requiere Python 3.10+ y VS Build Tools en Windows)
pip install "headroom-ai[proxy,mcp]"

# Registrar MCP en Claude Code
claude mcp add headroom -- headroom mcp serve

# O wrappear directamente
headroom wrap claude --memory --code-graph
`
<!-- END:headroom -->
