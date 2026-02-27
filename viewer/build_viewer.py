#!/usr/bin/env python3
"""
Generates a live HTML debate viewer from state.json.
Called by the debate-lead after each agent turn to update the view.

Usage:
    python viewer/build_viewer.py --init "Topic text"      # initializes state.json with topic
    python viewer/build_viewer.py --add \
        --agent critic --round 1 --content-file "..."      # appends an entry
    python viewer/build_viewer.py --status completed       # sets debate status
    python viewer/build_viewer.py --thinking advocate      # sets "currently thinking" agent
    python viewer/build_viewer.py --serve                  # start HTTP server (background)
"""

import argparse
import json
import os
import sys
import html as html_module
import hashlib
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

STATE_FILE = "debate-output/state.json"
HTML_FILE = "debate-output/debate-live.html"
PID_FILE = "debate-output/.server.pid"
PORT = 8150

AGENT_CONFIG = {
    "critic": {
        "name": "Critic",
        "role": "Adversarial Thinker",
        "color": "#EF4444",
        "bg": "#FEF2F2",
        "border": "#FECACA",
        "icon": "\u2694\ufe0f",
        "align": "left",
    },
    "advocate": {
        "name": "Advocate",
        "role": "Rigorous Defender",
        "color": "#3B82F6",
        "bg": "#EFF6FF",
        "border": "#BFDBFE",
        "icon": "\U0001f6e1\ufe0f",
        "align": "right",
    },
    "judge": {
        "name": "Judge",
        "role": "Impartial Arbiter",
        "color": "#8B5CF6",
        "bg": "#F5F3FF",
        "border": "#DDD6FE",
        "icon": "\u2696\ufe0f",
        "align": "left",
    },
    "scribe": {
        "name": "Scribe",
        "role": "Neutral Recorder",
        "color": "#10B981",
        "bg": "#ECFDF5",
        "border": "#A7F3D0",
        "icon": "\U0001f4dd",
        "align": "right",
    },
}


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "topic": "",
        "status": "in_progress",
        "thinking": None,
        "current_round": 1,
        "total_rounds": 3,
        "version": 0,
        "entries": [],
    }


def save_state(state: dict):
    state["version"] = state.get("version", 0) + 1
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def inline_format(text: str) -> str:
    """Apply inline markdown formatting: links, citations, bold, code."""
    import re
    # [Source: "Title", Author, Year](URL) -> citation badge with link
    text = re.sub(
        r'\[Source:\s*"([^"]+)"(?:,\s*([^]]*))?\]\(([^)]+)\)',
        lambda m: f'<a class="citation" href="{m.group(3)}" target="_blank" title="{m.group(1)}">'
                  f'[{m.group(1)}{", " + m.group(2) if m.group(2) else ""}]</a>',
        text,
    )
    # [Unsourced -- ...] -> unsourced badge
    text = re.sub(
        r'\[Unsourced\s*--\s*([^\]]+)\]',
        r'<span class="unsourced" title="\1">[Unsourced]</span>',
        text,
    )
    # Standard markdown links [text](url)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a class="source-link" href="\2" target="_blank">\1</a>',
        text,
    )
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def md_to_html(text: str) -> str:
    """Minimal markdown to HTML conversion for debate content."""
    import re

    lines = text.split("\n")
    result = []
    in_list = False
    in_table = False
    table_header_done = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_list:
                result.append("</ul>")
                in_list = False
            if in_table:
                result.append("</tbody></table>")
                in_table = False
                table_header_done = False
            result.append("")
            continue

        # Table rows (pipes)
        if "|" in stripped and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            # Skip separator rows (---|---|---)
            if all(re.match(r"^[-:]+$", c) for c in cells):
                continue
            if not in_table:
                result.append('<table class="debate-table"><thead><tr>')
                for c in cells:
                    result.append(f"<th>{inline_format(c)}</th>")
                result.append("</tr></thead><tbody>")
                in_table = True
                table_header_done = True
                continue
            result.append("<tr>")
            for c in cells:
                result.append(f"<td>{inline_format(c)}</td>")
            result.append("</tr>")
            continue

        if in_table:
            result.append("</tbody></table>")
            in_table = False
            table_header_done = False

        # Headers
        m = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if m:
            if in_list:
                result.append("</ul>")
                in_list = False
            level = min(len(m.group(1)) + 2, 6)
            result.append(f"<h{level}>{inline_format(m.group(2))}</h{level}>")
            continue

        # Bullet points
        m = re.match(r"^[-*]\s+(.+)$", stripped)
        if m:
            if not in_list:
                result.append('<ul class="debate-list">')
                in_list = True
            result.append(f"  <li>{inline_format(m.group(1))}</li>")
            continue

        # Numbered list
        m = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if m:
            if not in_list:
                result.append('<ul class="debate-list">')
                in_list = True
            result.append(f"  <li>{inline_format(m.group(1))}</li>")
            continue

        if in_list:
            result.append("</ul>")
            in_list = False

        # Regular paragraph
        result.append(f"<p>{inline_format(stripped)}</p>")

    if in_list:
        result.append("</ul>")
    if in_table:
        result.append("</tbody></table>")

    return "\n".join(result)


def build_agent_config_js() -> str:
    """Emit agent config as JS object for client-side rendering."""
    items = []
    for key, cfg in AGENT_CONFIG.items():
        items.append(
            f'    "{key}": {{'
            f' name: "{cfg["name"]}", role: "{cfg["role"]}",'
            f' color: "{cfg["color"]}", bg: "{cfg["bg"]}", border: "{cfg["border"]}",'
            f' icon: "{cfg["icon"]}", align: "{cfg["align"]}" }}'
        )
    return "{\n" + ",\n".join(items) + "\n  }"


def build_html(state: dict) -> str:
    topic = html_module.escape(state.get("topic", ""))
    agent_config_js = build_agent_config_js()

    # Pre-render all existing entries server-side for initial paint.
    # The JS will take over for live updates after that.
    entries = state.get("entries", [])
    status = state.get("status", "in_progress")
    thinking = state.get("thinking")
    current_round = state.get("current_round", 1)
    total_rounds = state.get("total_rounds", 3)
    version = state.get("version", 0)

    # Server-side render of current entries (so page loads with content immediately)
    ssr_entries = ""
    rounds: dict[int, list] = {}
    for e in entries:
        r = e.get("round", 1)
        rounds.setdefault(r, []).append(e)

    for round_num in sorted(rounds.keys()):
        round_label = "Final Synthesis" if round_num == 0 else f"Round {round_num}"
        ssr_entries += f'<div class="round-divider"><span>{round_label}</span></div>\n'
        for entry in rounds[round_num]:
            agent_key = entry.get("agent", "").lower()
            cfg = AGENT_CONFIG.get(agent_key, AGENT_CONFIG["critic"])
            content_html = md_to_html(entry.get("content", ""))
            ts = entry.get("timestamp", "")
            ssr_entries += f"""<div class="bubble-row {cfg['align']}">
  <div class="bubble" style="--agent-color:{cfg['color']};--agent-bg:{cfg['bg']};--agent-border:{cfg['border']};">
    <div class="bubble-header">
      <span class="agent-icon">{cfg['icon']}</span>
      <span class="agent-name" style="color:{cfg['color']};">{cfg['name']}</span>
      <span class="agent-role">{cfg['role']}</span>
      <span class="timestamp">{ts}</span>
    </div>
    <div class="bubble-content">{content_html}</div>
  </div>
</div>\n"""

    # Thinking indicator (SSR)
    ssr_thinking = ""
    if thinking and status == "in_progress":
        cfg = AGENT_CONFIG.get(thinking.lower(), AGENT_CONFIG["critic"])
        ssr_thinking = f"""<div class="bubble-row {cfg['align']}" id="thinking-bubble">
  <div class="bubble thinking" style="--agent-color:{cfg['color']};--agent-bg:{cfg['bg']};--agent-border:{cfg['border']};">
    <div class="bubble-header">
      <span class="agent-icon">{cfg['icon']}</span>
      <span class="agent-name" style="color:{cfg['color']};">{cfg['name']}</span>
      <span class="agent-role">{cfg['role']}</span>
    </div>
    <div class="typing-indicator"><span></span><span></span><span></span></div>
  </div>
</div>"""

    status_badge_html = (
        '<span class="status-badge completed">Debate Complete</span>'
        if status == "completed"
        else f'<span class="status-badge in-progress">Round {current_round} of {total_rounds}</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Debate: {topic}</title>
<style>
  :root {{
    --bg: #0F172A;
    --surface: #1E293B;
    --surface-2: #334155;
    --text: #E2E8F0;
    --text-muted: #94A3B8;
    --border: #475569;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    min-height: 100vh;
  }}
  .container {{
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 16px 80px;
  }}
  header {{
    text-align: center;
    padding: 32px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
  }}
  header h1 {{
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: #F8FAFC;
  }}
  .topic {{
    font-size: 1.1rem;
    color: var(--text-muted);
    font-style: italic;
    max-width: 700px;
    margin: 0 auto 16px;
  }}
  .status-badge {{
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.03em;
  }}
  .status-badge.in-progress {{
    background: #1E3A5F;
    color: #60A5FA;
    border: 1px solid #2563EB;
  }}
  .status-badge.completed {{
    background: #14532D;
    color: #4ADE80;
    border: 1px solid #16A34A;
  }}
  .round-divider {{
    text-align: center;
    margin: 36px 0 24px;
    position: relative;
  }}
  .round-divider::before {{
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--border);
  }}
  .round-divider span {{
    position: relative;
    background: var(--bg);
    padding: 0 20px;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
  }}
  .bubble-row {{
    display: flex;
    margin-bottom: 20px;
  }}
  .bubble-row.left {{ justify-content: flex-start; }}
  .bubble-row.right {{ justify-content: flex-end; }}
  .bubble-row.slide-in {{
    animation: slideIn 0.5s cubic-bezier(0.22, 1, 0.36, 1);
  }}
  @keyframes slideIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .bubble {{
    max-width: 78%;
    background: var(--surface);
    border-radius: 16px;
    padding: 16px 20px;
    border: 1px solid var(--agent-border);
    border-left: 4px solid var(--agent-color);
    position: relative;
  }}
  .bubble-row.right .bubble {{
    border-left: 1px solid var(--agent-border);
    border-right: 4px solid var(--agent-color);
  }}
  .bubble-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }}
  .agent-icon {{ font-size: 1.2rem; }}
  .agent-name {{
    font-weight: 700;
    font-size: 0.95rem;
  }}
  .agent-role {{
    font-size: 0.75rem;
    color: var(--text-muted);
    background: var(--surface-2);
    padding: 2px 8px;
    border-radius: 10px;
  }}
  .timestamp {{
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-left: auto;
  }}
  .bubble-content {{
    font-size: 0.9rem;
    line-height: 1.7;
    color: var(--text);
  }}
  .bubble-content h3, .bubble-content h4, .bubble-content h5, .bubble-content h6 {{
    margin: 16px 0 8px;
    color: #F8FAFC;
    font-size: 0.95rem;
  }}
  .bubble-content p {{ margin-bottom: 8px; }}
  .bubble-content ul.debate-list {{
    margin: 8px 0 8px 20px;
    list-style-type: disc;
  }}
  .bubble-content ul.debate-list li {{ margin-bottom: 4px; }}
  .bubble-content strong {{ color: #F8FAFC; }}
  .bubble-content code {{
    background: var(--surface-2);
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.85em;
  }}
  .bubble-content a.citation {{
    display: inline;
    background: #1E3A5F;
    color: #93C5FD;
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    text-decoration: none;
    border: 1px solid #2563EB44;
    white-space: nowrap;
  }}
  .bubble-content a.citation:hover {{
    background: #2563EB;
    color: #FFF;
  }}
  .bubble-content a.source-link {{
    color: #93C5FD;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 2px;
  }}
  .bubble-content a.source-link:hover {{
    color: #BFDBFE;
    text-decoration-style: solid;
  }}
  .bubble-content .unsourced {{
    display: inline;
    background: #44403C;
    color: #FBBF24;
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    border: 1px solid #92400E44;
    cursor: help;
  }}
  .bubble-content table.debate-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 0.85em;
  }}
  .bubble-content table.debate-table th {{
    background: var(--surface-2);
    color: #F8FAFC;
    padding: 8px 12px;
    text-align: left;
    border-bottom: 2px solid var(--border);
  }}
  .bubble-content table.debate-table td {{
    padding: 6px 12px;
    border-bottom: 1px solid var(--border);
  }}
  .typing-indicator {{
    display: flex;
    gap: 6px;
    padding: 8px 4px;
  }}
  .typing-indicator span {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--agent-color);
    opacity: 0.4;
    animation: blink 1.4s infinite both;
  }}
  .typing-indicator span:nth-child(2) {{ animation-delay: 0.2s; }}
  .typing-indicator span:nth-child(3) {{ animation-delay: 0.4s; }}
  @keyframes blink {{
    0%, 80%, 100% {{ opacity: 0.4; transform: scale(1); }}
    40% {{ opacity: 1; transform: scale(1.2); }}
  }}
  .bubble.thinking {{
    background: var(--agent-bg);
    border-style: dashed;
  }}
  .agent-legend {{
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 12px;
    flex-wrap: wrap;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.8rem;
    color: var(--text-muted);
  }}
  .legend-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }}
  .empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
  }}
  .empty-state p {{ font-size: 1.1rem; margin-bottom: 8px; }}
  .poll-status {{
    text-align: center;
    padding: 16px;
    font-size: 0.75rem;
    color: var(--text-muted);
    opacity: 0.6;
  }}
  .poll-dot {{
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
  }}
  .poll-dot.connected {{ background: #4ADE80; }}
  .poll-dot.disconnected {{ background: #EF4444; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Agent Debate</h1>
    <div class="topic">{topic}</div>
    <div id="status-badge">{status_badge_html}</div>
    <div class="agent-legend">
      <div class="legend-item"><div class="legend-dot" style="background:#EF4444;"></div> Critic</div>
      <div class="legend-item"><div class="legend-dot" style="background:#3B82F6;"></div> Advocate</div>
      <div class="legend-item"><div class="legend-dot" style="background:#8B5CF6;"></div> Judge</div>
      <div class="legend-item"><div class="legend-dot" style="background:#10B981;"></div> Scribe</div>
    </div>
  </header>

  <div id="debate-feed">
    {ssr_entries if ssr_entries else '<div class="empty-state" id="empty-state"><p>Waiting for the debate to begin...</p></div>'}
    {ssr_thinking}
  </div>

  <div class="poll-status" id="poll-status">
    <span class="poll-dot connected" id="poll-dot"></span>
    <span id="poll-text">Listening for updates</span>
  </div>
</div>

<script>
(function() {{
  const AGENTS = {agent_config_js};
  const POLL_INTERVAL = 2000;
  let knownVersion = {version};
  let pollTimer = null;
  let isCompleted = {"true" if status == "completed" else "false"};
  let renderedEntryCount = {len(entries)};

  const feed = document.getElementById('debate-feed');
  const statusBadge = document.getElementById('status-badge');
  const pollDot = document.getElementById('poll-dot');
  const pollText = document.getElementById('poll-text');

  function inlineFmt(t) {{
    // Citation links: [Source: "Title", Author](URL)
    t = t.replace(/\\[Source:\\s*"([^"]+)"(?:,\\s*([^\\]]*))?\\]\\(([^)]+)\\)/g,
      function(m, title, extra, url) {{
        return '<a class="citation" href="' + url + '" target="_blank" title="' + title + '">[' + title + (extra ? ', ' + extra : '') + ']</a>';
      }});
    // Unsourced badges
    t = t.replace(/\\[Unsourced\\s*--\\s*([^\\]]+)\\]/g,
      '<span class="unsourced" title="$1">[Unsourced]</span>');
    // Standard markdown links
    t = t.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g,
      '<a class="source-link" href="$2" target="_blank">$1</a>');
    // Bold
    t = t.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
    // Inline code
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
    return t;
  }}

  function mdToHtml(text) {{
    if (!text) return '';
    let lines = text.split('\\n');
    let result = [];
    let inList = false;
    let inTable = false;
    for (let line of lines) {{
      let s = line.trim();
      if (!s) {{
        if (inList) {{ result.push('</ul>'); inList = false; }}
        if (inTable) {{ result.push('</tbody></table>'); inTable = false; }}
        result.push('');
        continue;
      }}
      // Table rows
      if (s.startsWith('|') && s.includes('|')) {{
        let cells = s.split('|').slice(1, -1).map(c => c.trim());
        if (cells.every(c => /^[-:]+$/.test(c))) continue;
        if (!inTable) {{
          result.push('<table class="debate-table"><thead><tr>');
          cells.forEach(c => result.push('<th>' + inlineFmt(c) + '</th>'));
          result.push('</tr></thead><tbody>');
          inTable = true;
          continue;
        }}
        result.push('<tr>');
        cells.forEach(c => result.push('<td>' + inlineFmt(c) + '</td>'));
        result.push('</tr>');
        continue;
      }}
      if (inTable) {{ result.push('</tbody></table>'); inTable = false; }}
      let hm = s.match(/^(#{{1,4}})\\s+(.+)$/);
      if (hm) {{
        if (inList) {{ result.push('</ul>'); inList = false; }}
        let lvl = Math.min(hm[1].length + 2, 6);
        result.push('<h' + lvl + '>' + inlineFmt(hm[2]) + '</h' + lvl + '>');
        continue;
      }}
      let bm = s.match(/^[-*]\\s+(.+)$/);
      if (!bm) bm = s.match(/^\\d+[.)]\\s+(.+)$/);
      if (bm) {{
        if (!inList) {{ result.push('<ul class="debate-list">'); inList = true; }}
        result.push('  <li>' + inlineFmt(bm[1]) + '</li>');
        continue;
      }}
      if (inList) {{ result.push('</ul>'); inList = false; }}
      result.push('<p>' + inlineFmt(s) + '</p>');
    }}
    if (inList) result.push('</ul>');
    if (inTable) result.push('</tbody></table>');
    return result.join('\\n');
  }}

  function esc(t) {{
    let d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }}

  function renderBubble(entry, animate) {{
    let agentKey = (entry.agent || '').toLowerCase();
    let cfg = AGENTS[agentKey] || AGENTS['critic'];
    let html = '<div class="bubble-row ' + cfg.align + (animate ? ' slide-in' : '') + '">' +
      '<div class="bubble" style="--agent-color:' + cfg.color + ';--agent-bg:' + cfg.bg + ';--agent-border:' + cfg.border + ';">' +
        '<div class="bubble-header">' +
          '<span class="agent-icon">' + cfg.icon + '</span>' +
          '<span class="agent-name" style="color:' + cfg.color + ';">' + cfg.name + '</span>' +
          '<span class="agent-role">' + cfg.role + '</span>' +
          '<span class="timestamp">' + (entry.timestamp || '') + '</span>' +
        '</div>' +
        '<div class="bubble-content">' + mdToHtml(entry.content) + '</div>' +
      '</div></div>';
    return html;
  }}

  function renderThinking(agentKey) {{
    if (!agentKey) return '';
    let cfg = AGENTS[agentKey.toLowerCase()] || AGENTS['critic'];
    return '<div class="bubble-row ' + cfg.align + ' slide-in" id="thinking-bubble">' +
      '<div class="bubble thinking" style="--agent-color:' + cfg.color + ';--agent-bg:' + cfg.bg + ';--agent-border:' + cfg.border + ';">' +
        '<div class="bubble-header">' +
          '<span class="agent-icon">' + cfg.icon + '</span>' +
          '<span class="agent-name" style="color:' + cfg.color + ';">' + cfg.name + '</span>' +
          '<span class="agent-role">' + cfg.role + '</span>' +
        '</div>' +
        '<div class="typing-indicator"><span></span><span></span><span></span></div>' +
      '</div></div>';
  }}

  function renderRoundDivider(roundNum) {{
    let label = roundNum === 0 ? 'Final Synthesis' : 'Round ' + roundNum;
    return '<div class="round-divider"><span>' + label + '</span></div>';
  }}

  function applyUpdate(state) {{
    let entries = state.entries || [];
    let newEntries = entries.slice(renderedEntryCount);

    // Remove empty state if present
    let empty = document.getElementById('empty-state');
    if (empty && newEntries.length > 0) empty.remove();

    // Remove old thinking bubble
    let oldThinking = document.getElementById('thinking-bubble');
    if (oldThinking) oldThinking.remove();

    // Track which rounds we've already rendered dividers for
    let existingDividers = feed.querySelectorAll('.round-divider span');
    let renderedRounds = new Set();
    existingDividers.forEach(d => {{
      let m = d.textContent.match(/Round (\\d+)/);
      if (m) renderedRounds.add(parseInt(m[1]));
      if (d.textContent === 'Final Synthesis') renderedRounds.add(0);
    }});

    // Append new entries
    for (let entry of newEntries) {{
      let roundNum = entry.round || 1;
      if (!renderedRounds.has(roundNum)) {{
        feed.insertAdjacentHTML('beforeend', renderRoundDivider(roundNum));
        renderedRounds.add(roundNum);
      }}
      feed.insertAdjacentHTML('beforeend', renderBubble(entry, true));
    }}
    renderedEntryCount = entries.length;

    // Add thinking bubble if applicable
    if (state.thinking && state.status === 'in_progress') {{
      feed.insertAdjacentHTML('beforeend', renderThinking(state.thinking));
    }}

    // Update status badge
    if (state.status === 'completed') {{
      statusBadge.innerHTML = '<span class="status-badge completed">Debate Complete</span>';
      isCompleted = true;
    }} else {{
      statusBadge.innerHTML = '<span class="status-badge in-progress">Round ' +
        (state.current_round || 1) + ' of ' + (state.total_rounds || 3) + '</span>';
    }}

    // Scroll to bottom if new content
    if (newEntries.length > 0 || state.thinking) {{
      window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
    }}

    knownVersion = state.version || 0;
  }}

  async function poll() {{
    try {{
      let resp = await fetch('state.json?t=' + Date.now());
      if (!resp.ok) throw new Error('HTTP ' + resp.status);

      let state = await resp.json();
      let newVersion = state.version || 0;

      if (newVersion !== knownVersion) {{
        applyUpdate(state);
        pollDot.className = 'poll-dot connected';
        pollText.textContent = 'Listening for updates';
      }}

      // Stop polling if debate is complete (give a few extra polls for safety)
      if (isCompleted) {{
        pollText.textContent = 'Debate complete';
        return;
      }}

      pollTimer = setTimeout(poll, POLL_INTERVAL);
    }} catch(e) {{
      pollDot.className = 'poll-dot disconnected';
      pollText.textContent = 'Reconnecting...';
      pollTimer = setTimeout(poll, POLL_INTERVAL * 2);
    }}
  }}

  // Start polling
  window.addEventListener('load', () => {{
    window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
    if (!isCompleted) {{
      pollTimer = setTimeout(poll, POLL_INTERVAL);
    }} else {{
      pollText.textContent = 'Debate complete';
    }}
  }});
}})();
</script>
</body>
</html>"""


def start_server():
    """Start a background HTTP server serving debate-output/."""
    # Kill any existing server
    stop_server()

    output_dir = os.path.abspath("debate-output")
    os.makedirs(output_dir, exist_ok=True)

    # Use subprocess to spawn the server in the background (cross-platform)
    script = (
        "import os, sys; os.chdir(sys.argv[1]); "
        "from http.server import HTTPServer, SimpleHTTPRequestHandler; "
        "class H(SimpleHTTPRequestHandler):\n"
        "    def log_message(self, *a): pass\n"
        "    def end_headers(self):\n"
        "        self.send_header('Access-Control-Allow-Origin', '*');\n"
        "        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0');\n"
        "        SimpleHTTPRequestHandler.end_headers(self)\n"
        f"s = HTTPServer(('0.0.0.0', {PORT}), H); s.serve_forever()"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", script, output_dir],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0) if sys.platform == "win32" else 0,
        start_new_session=True,
    )
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    print(f"Server started on http://localhost:{PORT} (PID {proc.pid})")


def stop_server():
    """Stop the background HTTP server if running."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", str(pid), "/T"], capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, ValueError, OSError):
            pass
        try:
            os.remove(PID_FILE)
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser(description="Build debate live viewer")
    parser.add_argument("--init", metavar="TOPIC", help="Initialize state with topic")
    parser.add_argument("--add", action="store_true", help="Add an entry")
    parser.add_argument("--agent", help="Agent name (critic/advocate/judge/scribe)")
    parser.add_argument("--round", type=int, help="Round number")
    parser.add_argument("--content-file", help="Path to file containing the content")
    parser.add_argument("--content", help="Inline content (short entries only)")
    parser.add_argument("--type", default="turn", help="Entry type (turn/synthesis)")
    parser.add_argument("--status", help="Set debate status (in_progress/completed)")
    parser.add_argument("--thinking", help="Set which agent is currently thinking (or 'none')")
    parser.add_argument("--set-round", type=int, help="Set current round number")
    parser.add_argument("--serve", action="store_true", help="Start background HTTP server")
    parser.add_argument("--stop-server", action="store_true", help="Stop background HTTP server")
    args = parser.parse_args()

    if args.serve:
        start_server()
        return

    if args.stop_server:
        stop_server()
        print("Server stopped")
        return

    state = load_state()

    if args.init:
        state["topic"] = args.init
        state["status"] = "in_progress"
        state["thinking"] = None
        state["current_round"] = 1
        state["version"] = 0
        state["entries"] = []

    if args.add:
        content = ""
        if args.content_file and os.path.exists(args.content_file):
            with open(args.content_file, "r", encoding="utf-8") as f:
                content = f.read()
        elif args.content:
            content = args.content
        state["entries"].append({
            "round": args.round or state.get("current_round", 1),
            "agent": args.agent or "unknown",
            "content": content,
            "type": args.type,
            "timestamp": datetime.now().strftime("%H:%M"),
        })

    if args.status:
        state["status"] = args.status

    if args.thinking:
        state["thinking"] = None if args.thinking.lower() == "none" else args.thinking

    if args.set_round:
        state["current_round"] = args.set_round

    save_state(state)

    html = build_html(state)
    os.makedirs(os.path.dirname(HTML_FILE), exist_ok=True)
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Updated {HTML_FILE} (version {state['version']})")


if __name__ == "__main__":
    main()
