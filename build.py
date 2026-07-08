#!/usr/bin/env python3
import csv
import json
import os

# Read CSV
csv_path = '/Users/kaycapbot/.openclaw/workspace/kaycapitals-threads-FINAL.csv'
threads = []

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        thread = {
            'id': row['ID'].strip(),
            'date': row['Date'].strip(),
            'likes': int(row['Likes'].strip()) if row['Likes'].strip().isdigit() else 0,
            'views': int(row['Views'].strip()) if row['Views'].strip().isdigit() else 0,
            'category': row['Category'].strip(),
            'topic': row['Topic'].strip(),
            'preview': row['Transcript Preview'].strip(),
            'post1': row['Post 1 (Hook)'].strip(),
            'post2': row['Post 2 (Story)'].strip(),
            'post3': row['Post 3 (Value)'].strip(),
            'post4': row['Post 4 (Deep Truth)'].strip(),
            'post5': row['Post 5 (CTA - Message)'].strip(),
            'post6': row['Post 6 (CTA - Comment)'].strip(),
            'url': row['Instagram URL'].strip(),
            'status': row['Status'].strip(),
        }
        threads.append(thread)

print(f"Parsed {len(threads)} threads")

# Convert to JSON
threads_json = json.dumps(threads, ensure_ascii=False, separators=(',', ':'))

# Save data file
data_js = f'const threads = {threads_json};'
with open('/Users/kaycapbot/.openclaw/workspace/thread-browser/threads-data.js', 'w', encoding='utf-8') as f:
    f.write(data_js)

data_size = os.path.getsize('/Users/kaycapbot/.openclaw/workspace/thread-browser/threads-data.js')
print(f"Data file: {data_size/1024/1024:.2f} MB")

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Kay Capitals — Thread Browser</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0d0d0d;
  --bg2:#1a1a1a;
  --bg3:#252525;
  --border:#2a2a2a;
  --text:#f0f0f0;
  --text2:#a0a0a0;
  --blue:#3b82f6;
  --purple:#8b5cf6;
  --red:#ef4444;
  --green:#22c55e;
  --orange:#f97316;
  --gold:#eab308;
  --teal:#14b8a6;
  --accent:#3b82f6;
}}
html,body{{height:100%;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;overflow-x:hidden}}
/* HEADER */
.header{{position:sticky;top:0;z-index:100;background:var(--bg);border-bottom:1px solid var(--border);padding:10px 12px 0}}
.stats-bar{{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--text2);margin-bottom:8px}}
.stats-bar span{{font-weight:600;color:var(--text)}}
.search-row{{display:flex;gap:8px;margin-bottom:10px}}
.search-input{{flex:1;background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:9px 14px;font-size:15px;outline:none;-webkit-appearance:none}}
.search-input:focus{{border-color:var(--accent)}}
.search-input::placeholder{{color:var(--text2)}}
.sort-select{{background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:9px 10px;font-size:13px;outline:none;-webkit-appearance:none;cursor:pointer;white-space:nowrap}}
/* TABS */
.tabs{{display:flex;gap:4px;overflow-x:auto;padding-bottom:10px;scrollbar-width:none;-ms-overflow-style:none}}
.tabs::-webkit-scrollbar{{display:none}}
.tab{{flex-shrink:0;background:var(--bg3);border:1px solid var(--border);color:var(--text2);border-radius:20px;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;transition:all .15s;user-select:none;-webkit-tap-highlight-color:transparent}}
.tab.active{{color:#fff;border-color:transparent}}
.tab[data-cat="ALL"].active{{background:var(--accent)}}
.tab[data-cat="STRATEGY"].active{{background:var(--blue)}}
.tab[data-cat="PSYCHOLOGY"].active{{background:var(--purple)}}
.tab[data-cat="RISK_MGMT"].active{{background:var(--red)}}
.tab[data-cat="EDUCATION"].active{{background:var(--green)}}
.tab[data-cat="MINDSET"].active{{background:var(--orange)}}
.tab[data-cat="LIFESTYLE"].active{{background:var(--gold);color:#000}}
.tab[data-cat="JOURNEY"].active{{background:var(--teal)}}
.tab[data-cat="RESULTS"].active{{background:#ec4899}}
/* GRID */
.grid-container{{padding:12px;display:grid;grid-template-columns:1fr 1fr;gap:10px}}
@media(min-width:600px){{.grid-container{{grid-template-columns:repeat(3,1fr)}}}}
@media(min-width:900px){{.grid-container{{grid-template-columns:repeat(4,1fr)}}}}
@media(min-width:1200px){{.grid-container{{grid-template-columns:repeat(5,1fr)}}}}
/* CARD */
.card{{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:12px;cursor:pointer;transition:border-color .15s,transform .1s;position:relative;-webkit-tap-highlight-color:transparent}}
.card:active{{transform:scale(0.98)}}
.card:hover{{border-color:var(--accent)}}
.card.posted{{border-color:var(--green);opacity:.8}}
.card-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:6px;margin-bottom:8px}}
.card-topic{{font-size:13px;font-weight:700;line-height:1.3;flex:1}}
.posted-badge{{background:var(--green);color:#000;font-size:10px;font-weight:800;border-radius:4px;padding:2px 5px;white-space:nowrap;flex-shrink:0}}
.cat-badge{{display:inline-block;font-size:10px;font-weight:700;border-radius:4px;padding:2px 6px;margin-bottom:6px;letter-spacing:.4px}}
.cat-STRATEGY{{background:rgba(59,130,246,.2);color:#60a5fa}}
.cat-PSYCHOLOGY{{background:rgba(139,92,246,.2);color:#a78bfa}}
.cat-RISK_MGMT{{background:rgba(239,68,68,.2);color:#f87171}}
.cat-EDUCATION{{background:rgba(34,197,94,.2);color:#4ade80}}
.cat-MINDSET{{background:rgba(249,115,22,.2);color:#fb923c}}
.cat-LIFESTYLE{{background:rgba(234,179,8,.2);color:#fbbf24}}
.cat-JOURNEY{{background:rgba(20,184,166,.2);color:#2dd4bf}}
.cat-RESULTS{{background:rgba(236,72,153,.2);color:#f472b6}}
.cat-default{{background:rgba(160,160,160,.15);color:#a0a0a0}}
.card-meta{{display:flex;gap:8px;align-items:center;font-size:11px;color:var(--text2);margin-bottom:6px}}
.card-preview{{font-size:12px;color:var(--text2);line-height:1.4;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
/* EMPTY STATE */
.empty-state{{text-align:center;padding:60px 20px;color:var(--text2)}}
.empty-state h3{{font-size:20px;margin-bottom:8px;color:var(--text)}}
/* LOAD MORE */
.load-more-wrap{{text-align:center;padding:16px}}
.load-more-btn{{background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:10px 24px;font-size:14px;cursor:pointer}}
/* MODAL OVERLAY */
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:1000;overflow-y:auto;-webkit-overflow-scrolling:touch}}
.modal-overlay.open{{display:block}}
.modal{{background:var(--bg2);border-radius:16px 16px 0 0;min-height:60vh;max-width:700px;margin:60px auto 0;padding:20px;position:relative;border:1px solid var(--border)}}
@media(max-width:700px){{.modal{{border-radius:16px 16px 0 0;margin-top:40px}}}}
.modal-close{{position:absolute;top:16px;right:16px;background:var(--bg3);border:none;color:var(--text2);width:34px;height:34px;border-radius:50%;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:10}}
.modal-header{{margin-bottom:16px;padding-right:44px}}
.modal-topic{{font-size:18px;font-weight:800;line-height:1.3;margin-bottom:8px}}
.modal-meta{{display:flex;gap:10px;align-items:center;font-size:13px;color:var(--text2);flex-wrap:wrap}}
.modal-actions{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}}
.btn{{border:none;border-radius:8px;padding:10px 16px;font-size:14px;font-weight:700;cursor:pointer;transition:opacity .15s;-webkit-tap-highlight-color:transparent}}
.btn:active{{opacity:.7}}
.btn-primary{{background:var(--accent);color:#fff}}
.btn-green{{background:var(--green);color:#000}}
.btn-secondary{{background:var(--bg3);border:1px solid var(--border);color:var(--text)}}
.btn-posted{{background:var(--green);color:#000}}
/* POSTS */
.posts{{display:flex;flex-direction:column;gap:16px}}
.post-block{{background:var(--bg3);border-radius:10px;padding:14px;border:1px solid var(--border)}}
.post-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}}
.post-label{{font-size:11px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:.5px}}
.copy-btn{{background:var(--bg);border:1px solid var(--border);color:var(--text2);border-radius:6px;padding:4px 10px;font-size:12px;font-weight:600;cursor:pointer}}
.copy-btn.copied{{background:var(--green);border-color:var(--green);color:#000}}
.post-content{{font-size:14px;line-height:1.6;white-space:pre-wrap;word-break:break-word}}
/* Flag highlighting */
.post-content .flag{{color:#f97316;font-weight:600}}
/* TOAST */
.toast{{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#333;color:#fff;border-radius:8px;padding:10px 20px;font-size:14px;font-weight:600;z-index:2000;opacity:0;transition:opacity .3s;pointer-events:none}}
.toast.show{{opacity:1}}
/* URL link */
.modal-url{{display:inline-block;margin-top:6px;font-size:12px;color:var(--accent);text-decoration:none;word-break:break-all}}
</style>
</head>
<body>

<div class="header">
  <div class="stats-bar">
    <div id="statsText">Loading...</div>
    <div id="filterCount" style="color:var(--text2);font-size:11px"></div>
  </div>
  <div class="search-row">
    <input class="search-input" id="searchInput" type="search" placeholder="🔍 Search topics, posts..." autocomplete="off" autocorrect="off" spellcheck="false">
    <select class="sort-select" id="sortSelect">
      <option value="likes">👍 Likes</option>
      <option value="date_new">📅 Newest</option>
      <option value="date_old">📅 Oldest</option>
    </select>
  </div>
  <div class="tabs" id="tabs"></div>
</div>

<div id="gridContainer" class="grid-container"></div>
<div class="load-more-wrap" id="loadMoreWrap" style="display:none">
  <button class="load-more-btn" id="loadMoreBtn">Load more</button>
</div>
<div class="empty-state" id="emptyState" style="display:none">
  <h3>No threads found</h3>
  <p>Try a different search or category</p>
</div>

<!-- MODAL -->
<div class="modal-overlay" id="modalOverlay">
  <div class="modal" id="modal">
    <button class="modal-close" id="modalClose">✕</button>
    <div class="modal-header">
      <div class="modal-topic" id="modalTopic"></div>
      <div class="modal-meta" id="modalMeta"></div>
      <a class="modal-url" id="modalUrl" target="_blank" rel="noopener"></a>
    </div>
    <div class="modal-actions">
      <button class="btn btn-primary" id="copyAllBtn">📋 Copy All Posts</button>
      <button class="btn btn-secondary" id="markPostedBtn">Mark as Posted</button>
    </div>
    <div class="posts" id="modalPosts"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const threads = {threads_json};

// Category config
const CAT_ORDER = ['ALL','STRATEGY','PSYCHOLOGY','RISK_MGMT','EDUCATION','MINDSET','LIFESTYLE','JOURNEY','RESULTS'];

// State
let activeCategory = 'ALL';
let searchQuery = '';
let sortMode = 'likes';
let filteredThreads = [];
let renderedCount = 0;
const PAGE_SIZE = 60;

// Posted IDs from localStorage
let postedIds = new Set(JSON.parse(localStorage.getItem('posted_ids') || '[]'));

function savePosted() {{
  localStorage.setItem('posted_ids', JSON.stringify([...postedIds]));
}}

// Category counts
const catCounts = {{}};
threads.forEach(t => {{
  catCounts[t.category] = (catCounts[t.category] || 0) + 1;
}});
catCounts['ALL'] = threads.length;

// Build tabs
function buildTabs() {{
  const tabsEl = document.getElementById('tabs');
  CAT_ORDER.forEach(cat => {{
    if (cat !== 'ALL' && !catCounts[cat]) return;
    const tab = document.createElement('div');
    tab.className = 'tab' + (cat === activeCategory ? ' active' : '');
    tab.dataset.cat = cat;
    const count = catCounts[cat] || 0;
    tab.textContent = cat + ' (' + count + ')';
    tab.addEventListener('click', () => {{
      activeCategory = cat;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      applyFilters();
    }});
    tabsEl.appendChild(tab);
  }});
}}

// Filter & sort
function applyFilters() {{
  const q = searchQuery.toLowerCase().trim();
  filteredThreads = threads.filter(t => {{
    if (activeCategory !== 'ALL' && t.category !== activeCategory) return false;
    if (q) {{
      const hay = (t.topic + ' ' + t.preview + ' ' + t.post1 + ' ' + t.post2 + ' ' + t.post3 + ' ' + t.post4 + ' ' + t.post5 + ' ' + t.post6).toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    return true;
  }});

  // Sort
  if (sortMode === 'likes') {{
    filteredThreads.sort((a, b) => b.likes - a.likes);
  }} else if (sortMode === 'date_new') {{
    filteredThreads.sort((a, b) => b.date.localeCompare(a.date));
  }} else {{
    filteredThreads.sort((a, b) => a.date.localeCompare(b.date));
  }}

  renderedCount = 0;
  document.getElementById('gridContainer').innerHTML = '';
  renderMore();
  updateStats();
}}

function catBadgeClass(cat) {{
  const map = {{STRATEGY:'STRATEGY',PSYCHOLOGY:'PSYCHOLOGY',RISK_MGMT:'RISK_MGMT',EDUCATION:'EDUCATION',MINDSET:'MINDSET',LIFESTYLE:'LIFESTYLE',JOURNEY:'JOURNEY',RESULTS:'RESULTS'}};
  return 'cat-badge cat-' + (map[cat] || 'default');
}}

function formatLikes(n) {{
  if (n >= 1000000) return (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n/1000).toFixed(1) + 'k';
  return n.toString();
}}

function renderMore() {{
  const container = document.getElementById('gridContainer');
  const emptyState = document.getElementById('emptyState');
  const loadMoreWrap = document.getElementById('loadMoreWrap');

  if (filteredThreads.length === 0) {{
    emptyState.style.display = 'block';
    loadMoreWrap.style.display = 'none';
    return;
  }}
  emptyState.style.display = 'none';

  const end = Math.min(renderedCount + PAGE_SIZE, filteredThreads.length);
  const frag = document.createDocumentFragment();

  for (let i = renderedCount; i < end; i++) {{
    const t = filteredThreads[i];
    const isPosted = postedIds.has(t.id);
    const card = document.createElement('div');
    card.className = 'card' + (isPosted ? ' posted' : '');
    card.dataset.id = t.id;
    const preview = (t.post1 || '').substring(0, 100);

    card.innerHTML = `
      <div class="card-top">
        <div class="card-topic">${{escHtml(t.topic)}}</div>
        ${{isPosted ? '<div class="posted-badge">Posted ✓</div>' : ''}}
      </div>
      <div class="${{catBadgeClass(t.category)}}">${{t.category}}</div>
      <div class="card-meta">
        <span>👍 ${{formatLikes(t.likes)}}</span>
        <span>${{t.date}}</span>
      </div>
      <div class="card-preview">${{escHtml(preview)}}${{t.post1.length > 100 ? '…' : ''}}</div>
    `;
    card.addEventListener('click', () => openModal(t.id));
    frag.appendChild(card);
  }}

  container.appendChild(frag);
  renderedCount = end;

  if (renderedCount < filteredThreads.length) {{
    loadMoreWrap.style.display = 'block';
  }} else {{
    loadMoreWrap.style.display = 'none';
  }}
}}

function updateStats() {{
  const total = threads.length;
  const posted = postedIds.size;
  const remaining = total - posted;
  document.getElementById('statsText').innerHTML = `<span>${{total.toLocaleString()}}</span> threads &nbsp;·&nbsp; <span style="color:var(--green)">${{posted}}</span> posted &nbsp;·&nbsp; <span>${{remaining}}</span> remaining`;
  const fc = filteredThreads.length;
  document.getElementById('filterCount').textContent = fc < total ? fc.toLocaleString() + ' shown' : '';
}}

// HTML escape
function escHtml(s) {{
  return (s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

// Highlight [ADD: ...] flags in post content
function formatPostContent(text) {{
  const escaped = escHtml(text);
  return escaped.replace(/(\[ADD:[^\]]*\])/g, '<span class="flag">$1</span>');
}}

// Modal
let currentThreadId = null;

function openModal(id) {{
  const t = threads.find(x => x.id === id);
  if (!t) return;
  currentThreadId = id;

  document.getElementById('modalTopic').textContent = t.topic;

  const isPosted = postedIds.has(id);
  document.getElementById('modalMeta').innerHTML = `
    <span class="${{catBadgeClass(t.category)}}" style="margin:0">${{t.category}}</span>
    <span>👍 ${{formatLikes(t.likes)}}</span>
    <span>${{t.date}}</span>
    ${{isPosted ? '<span style="color:var(--green);font-weight:700">✓ Posted</span>' : ''}}
  `;

  const urlEl = document.getElementById('modalUrl');
  if (t.url) {{
    urlEl.href = t.url;
    urlEl.textContent = '🔗 View on Instagram';
    urlEl.style.display = 'inline-block';
  }} else {{
    urlEl.style.display = 'none';
  }}

  // Mark as posted button
  const mpBtn = document.getElementById('markPostedBtn');
  if (isPosted) {{
    mpBtn.textContent = '✓ Posted';
    mpBtn.className = 'btn btn-posted';
  }} else {{
    mpBtn.textContent = 'Mark as Posted';
    mpBtn.className = 'btn btn-secondary';
  }}

  // Build posts
  const postLabels = ['Post 1 — Hook','Post 2 — Story','Post 3 — Value','Post 4 — Deep Truth','Post 5 — CTA (Message)','Post 6 — CTA (Comment)'];
  const posts = [t.post1, t.post2, t.post3, t.post4, t.post5, t.post6];
  const postsEl = document.getElementById('modalPosts');
  postsEl.innerHTML = '';
  posts.forEach((p, i) => {{
    if (!p) return;
    const block = document.createElement('div');
    block.className = 'post-block';
    block.innerHTML = `
      <div class="post-header">
        <div class="post-label">${{postLabels[i]}}</div>
        <button class="copy-btn" data-idx="${{i}}">Copy</button>
      </div>
      <div class="post-content">${{formatPostContent(p)}}</div>
    `;
    block.querySelector('.copy-btn').addEventListener('click', (e) => {{
      e.stopPropagation();
      copyText(p, e.target);
    }});
    postsEl.appendChild(block);
  }});

  document.getElementById('modalOverlay').classList.add('open');
  document.getElementById('modal').scrollTop = 0;
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
  currentThreadId = null;
}}

function copyText(text, btn) {{
  navigator.clipboard.writeText(text).then(() => {{
    if (btn) {{
      const orig = btn.textContent;
      btn.textContent = '✓';
      btn.classList.add('copied');
      setTimeout(() => {{ btn.textContent = orig; btn.classList.remove('copied'); }}, 1500);
    }}
    showToast('Copied!');
  }}).catch(() => {{
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('Copied!');
  }});
}}

function showToast(msg) {{
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => toast.classList.remove('show'), 2000);
}}

// Events
document.getElementById('modalClose').addEventListener('click', closeModal);
document.getElementById('modalOverlay').addEventListener('click', (e) => {{
  if (e.target === document.getElementById('modalOverlay')) closeModal();
}});

document.getElementById('copyAllBtn').addEventListener('click', () => {{
  if (!currentThreadId) return;
  const t = threads.find(x => x.id === currentThreadId);
  if (!t) return;
  const postLabels = ['Post 1 — Hook','Post 2 — Story','Post 3 — Value','Post 4 — Deep Truth','Post 5 — CTA (Message)','Post 6 — CTA (Comment)'];
  const posts = [t.post1, t.post2, t.post3, t.post4, t.post5, t.post6];
  const allText = posts.map((p, i) => p ? `${{postLabels[i]}}\\n${{p}}` : null).filter(Boolean).join('\\n\\n---\\n\\n');
  copyText(allText, document.getElementById('copyAllBtn'));
}});

document.getElementById('markPostedBtn').addEventListener('click', () => {{
  if (!currentThreadId) return;
  const id = currentThreadId;
  const btn = document.getElementById('markPostedBtn');
  if (postedIds.has(id)) {{
    postedIds.delete(id);
    btn.textContent = 'Mark as Posted';
    btn.className = 'btn btn-secondary';
    // Update modal meta
    const metaEl = document.getElementById('modalMeta');
    metaEl.querySelector('[style*="green"]')?.remove();
  }} else {{
    postedIds.add(id);
    btn.textContent = '✓ Posted';
    btn.className = 'btn btn-posted';
    const metaEl = document.getElementById('modalMeta');
    const postedSpan = document.createElement('span');
    postedSpan.style.cssText = 'color:var(--green);font-weight:700';
    postedSpan.textContent = '✓ Posted';
    metaEl.appendChild(postedSpan);
    showToast('Marked as posted ✓');
  }}
  savePosted();
  updateStats();
  // Update card in grid
  const card = document.querySelector(`.card[data-id="${{id}}"]`);
  if (card) {{
    if (postedIds.has(id)) {{
      card.classList.add('posted');
      if (!card.querySelector('.posted-badge')) {{
        const badge = document.createElement('div');
        badge.className = 'posted-badge';
        badge.textContent = 'Posted ✓';
        card.querySelector('.card-top').appendChild(badge);
      }}
    }} else {{
      card.classList.remove('posted');
      card.querySelector('.posted-badge')?.remove();
    }}
  }}
}});

document.getElementById('searchInput').addEventListener('input', (e) => {{
  searchQuery = e.target.value;
  clearTimeout(window._searchTimer);
  window._searchTimer = setTimeout(applyFilters, 250);
}});

document.getElementById('sortSelect').addEventListener('change', (e) => {{
  sortMode = e.target.value;
  applyFilters();
}});

document.getElementById('loadMoreBtn').addEventListener('click', renderMore);

// Init
buildTabs();
applyFilters();
</script>
</body>
</html>'''

# Write HTML
html_path = '/Users/kaycapbot/.openclaw/workspace/thread-browser/index.html'
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

html_size = os.path.getsize(html_path)
print(f"HTML file: {html_size/1024/1024:.2f} MB")
print(f"DONE - file size: {html_size/1024/1024:.2f} MB")
