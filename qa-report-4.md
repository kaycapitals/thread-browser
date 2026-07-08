# QA Report 4 — KayCapitals Thread Browser
**Agent:** QA Agent 4 — Edge Cases & Breaking the App  
**Date:** 2026-07-07  
**File Audited:** `/thread-browser/index.html`  
**Method:** Full static code analysis of HTML/CSS/JS (lines 1–378, JS logic lines 151–378)

---

## 1. Race Conditions — Multiple Modal Opens

**Verdict: SAFE (no double modals possible)**

`openModal(t)` does not guard against rapid repeated calls, but `modal-bg.classList.add('show')` is idempotent — adding a class that's already there does nothing. Subsequent rapid clicks simply overwrite `currentThread` and re-render modal content. No duplicate modal state is possible.

`document.body.style.overflow = 'hidden'` is also idempotent.

**Edge:** If user rapidly opens Card A, then Card B, `currentThread` ends up as Card B. The modal shows B's content. If user then hits "Copy All" or "Mark as Posted", it acts on B. This is correct behavior. No corruption.

**No bug here.** ✅

---

## 2. Search Edge Cases

### 2a. Empty String Search
```js
searchQuery = document.getElementById('search').value.toLowerCase().trim();
// then in filter:
if (searchQuery) { ... } // empty string is falsy — skips filter
```
Empty string restores all results. **WORKS CORRECTLY.** ✅

### 2b. Special Characters `" ' < > &`
Search query is used only in:
```js
const hay = (t.topic + ' ' + t.post1 + ' ' + t.post2 + ' ' + t.post3).toLowerCase();
if (!hay.includes(searchQuery)) return false;
```
`hay` is raw unescaped string data. `searchQuery` is raw unescaped input. It's a pure string `.includes()` — no DOM injection, no eval. **No XSS risk in search.** ✅

`< > &` would simply fail to match (post data doesn't contain raw HTML entities except `&` which might appear in some posts — unlikely). No crash.

### 2c. Very Long Search Query (500+ chars)
No length validation. `.toLowerCase().trim()` and `.includes()` run fine on arbitrarily long strings. Would just never match, returning 0 results. No crash. **WORKS.** ✅

### 2d. Search While Category Filter Active
Both filters apply sequentially in `applyFilters()`:
```js
if (activeCategory !== 'ALL' && t.category !== activeCategory) return false;
if (searchQuery) { if (!hay.includes(searchQuery)) return false; }
```
They AND together correctly. **WORKS CORRECTLY.** ✅

---

## 3. Sort + Category + Search All Active Simultaneously

All three filter/sort values are independent state variables (`activeCategory`, `activeSort`, `searchQuery`). `applyFilters()` applies category filter → search filter → sort in sequence. All three active simultaneously AND-filters correctly, then sorts the result. **WORKS CORRECTLY.** ✅

---

## 4. Mark as Posted — Rapid Spam Clicking

```js
function togglePosted() {
  if (!currentThread) return;
  const id = currentThread.id;
  if (postedIds.has(id)) { postedIds.delete(id); ... }
  else { postedIds.add(id); ... }
  localStorage.setItem(POSTED_KEY, JSON.stringify([...postedIds]));
  applyFilters();   // <-- re-renders entire grid on every click
  updateStats();
}
```

State toggles correctly (Set operations are atomic). localStorage is always written with consistent state. **No data corruption.**

**HOWEVER:** Every single click triggers `applyFilters()` → full grid re-render → DOM wipe + re-build. On a large dataset, rapid spam clicking would cause visible jank/flicker and could be slow. At 60 threads per page this is manageable but still wasteful.

**Bug: MINOR** — `togglePosted()` calls `applyFilters()` which nukes and re-renders the entire grid instead of just updating the single card's posted state.

---

## 5. Load More When Filtered Results = 0

```js
function loadMore() {
  const slice = filtered.slice(displayed, displayed + PAGE); // empty array
  slice.forEach(...); // no iterations
  displayed += slice.length; // += 0
  btn.style.display = displayed < filtered.length ? 'block' : 'none';
  // 0 < 0 → false → hidden ✅
}
```

`no-results` div is shown when `filtered.length === 0`. Load More button stays hidden. **WORKS CORRECTLY.** ✅

---

## 6. Modal Close Edge Cases

### 6a. Click Outside Modal (on modal-bg backdrop)
```js
.modal-bg onclick="closeModal(event)"

function closeModal(e) {
  if (e && e.target !== document.getElementById('modal-bg')) return;
  // close...
}
```
Clicking directly on `modal-bg` → `e.target === modal-bg` → closes. ✅  
Clicking on `modal-content` or anything inside → event bubbles to `modal-bg`, but `e.target` is the inner element → early return, does NOT close. ✅

### 6b. Escape Key — Modal Close
```js
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.getElementById('auth-overlay').classList.contains('show')) doLogin();
});
```
**This is the ONLY keydown handler.** There is NO Escape key handler for the modal. Pressing Escape while modal is open does nothing.

**Bug: MINOR** — Escape key should close the modal. Standard UX expectation.

### 6c. Background Scroll Lock
```js
// openModal:
document.body.style.overflow = 'hidden';
// closeModal:
document.body.style.overflow = '';
```
`body.overflow = 'hidden'` locks background scroll on desktop browsers. **WORKS on desktop.** ✅

On iOS Safari, `overflow: hidden` on `body` is notoriously unreliable — the background can still scroll. Not tested but a known mobile limitation.

**Bug: MINOR** — No iOS-safe scroll lock (`position: fixed` + save/restore scroll position).

---

## 7. localStorage Corruption — CRITICAL BUG

```js
let postedIds = new Set(JSON.parse(localStorage.getItem(POSTED_KEY) || '[]'));
```

**This line has NO try/catch.** If `localStorage.getItem(POSTED_KEY)` returns any invalid JSON (e.g., `{broken`, `undefined`, `null-string`, or manually corrupted data), `JSON.parse()` throws a `SyntaxError`. This is an **uncaught exception at module load time**, which means:

- `postedIds` is never initialized
- `applyFilters()` is never called
- The entire app silently fails to render
- The user sees an empty page with no error message

**Reproduction:** Open DevTools → Application → localStorage → set `kc_posted` to `{invalid` → refresh. App breaks completely.

**Fix:**
```js
let postedIds;
try {
  postedIds = new Set(JSON.parse(localStorage.getItem(POSTED_KEY) || '[]'));
} catch(e) {
  postedIds = new Set();
  localStorage.removeItem(POSTED_KEY); // clear corrupt data
}
```

**Bug: CRITICAL** ❌

---

## 8. Thread With Missing/Empty Posts

```js
posts.forEach((p, i) => {
  if (!p) return; // skips falsy values (empty string, null, undefined)
  html += `<div class="post-block">...`;
});
```

Empty string posts are skipped cleanly. Modal still renders remaining posts. ✅

**However, `copyAll()` has a subtle renumbering issue:**
```js
const posts = [t.post1,...,t.post6].filter(Boolean); // removes empty posts
const text = posts.map((p,i) => `Post ${i+1}:\n${p}`).join('\n\n---\n\n');
```
If post3 is empty, the remaining posts get renumbered: Post 1, Post 2, Post 3 (was Post 4), Post 4 (was Post 5), Post 5 (was Post 6). The numbering in the copied text won't match the labels shown in the modal UI.

**Bug: MINOR** — Post numbering in `copyAll()` output doesn't match modal display when posts are missing.

---

## 9. Very Long Topic Names

CSS for `.card-topic`:
```css
.card-topic{font-size:.85rem;font-weight:700;line-height:1.3;margin-bottom:6px}
```
No `overflow:hidden`, no `text-overflow:ellipsis`, no `max-height`, no `-webkit-line-clamp`. A 100+ character topic would expand the card vertically, causing uneven grid card heights and broken layout in the CSS Grid.

Modal title similarly:
```css
.modal-title{font-size:1.1rem;font-weight:800;flex:1;padding-right:12px}
```
No truncation — wraps naturally (acceptable in modal).

**Bug: MINOR** — No text truncation on card topic — long topics break grid card height uniformity.

---

## 10. Category "RESULTS" — Not in CATS Array

```js
const CATS = ['ALL','STRATEGY','PSYCHOLOGY','RISK_MGMT','EDUCATION','MINDSET','LIFESTYLE','JOURNEY'];
// RESULTS is absent
```

**Analysis:**
- **Tab generated?** No. `init()` only iterates `CATS`. No RESULTS tab is created.
- **Shows under ALL?** Yes. `activeCategory = 'ALL'` doesn't filter by category, so RESULTS threads appear in ALL view.
- **Gets a colored badge?** Yes — CSS defines `.card-cat[data-cat="RESULTS"]{background:#374151}`.
- **Accessible via category filter?** NO. Users cannot filter to RESULTS-only. They're stranded in ALL.

One thread (`category: "RESULTS"`) exists in the data. It's visible under ALL, has a dark gray badge, but has no dedicated navigation tab.

**Bug: MINOR** — RESULTS category not in CATS array, no tab, no category-level access.

---

## 11. XSS Check — `esc()` Function Coverage

```js
function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
```

`esc()` only escapes `&`, `<`, `>`. Does **not** escape `"` or `'`.

### Where data is inserted:

**A. `makeCard()` — UNESCAPED CATEGORY in innerHTML:**
```js
card.innerHTML = `
  <span class="card-cat" data-cat="${t.category}">${t.category}</span>
  ...
`;
```
`t.category` is inserted TWICE without `esc()`:
1. As HTML attribute value: `data-cat="${t.category}"` — if category contained `"`, it would break the attribute. Worse: `" onmouseover="alert(1)` as a category would inject an event handler.
2. As text content between tags: `>${t.category}<` — if category contained `<script>`, it would execute.

Since thread data is internal/controlled, exploitability is low — but **this is technically unsafe**.

**B. `makeCard()` — `t.date` unescaped in innerHTML:**
```js
<div class="card-meta">👍 ${t.likes.toLocaleString()} · ${t.date}</div>
```
`t.date` is format `"2026-04-07"` — safe in practice, but not escaped.

**C. `openModal()` — SAFE:**
```js
document.getElementById('modal-title').textContent = t.topic; // textContent = safe ✅
```

**D. `formatPost()` — SAFE:**
```js
return esc(text).replace(/\[ADD:[^\]]*\]/g, m => `<span class="add-flag">${m}</span>`);
```
`esc()` called first, then regex matches on already-escaped text. Safe. ✅

**E. Post labels in `openModal()` — hardcoded strings, safe.** ✅

**Summary:** `t.category` is used unescaped in `innerHTML`. Since data is internal, not user-entered, real XSS risk is low — but if thread data were ever loaded from an external/user-editable source, this would be a live XSS vector.

**Bug: MAJOR** — `t.category` unescaped in `makeCard()` innerHTML (attribute + text content). Should use `esc(t.category)`.

---

## 12. Password Brute Force

```js
const PASS = 'getrichnow';
```

**CRITICAL SECURITY ISSUES:**

1. **Password is hardcoded in plain text in the page source.** Anyone who:
   - Opens DevTools → Sources
   - Does View Source (Ctrl+U)
   - Runs `fetch('/index.html').then(r=>r.text()).then(console.log)` from any page
   
   Will immediately see `const PASS = 'getrichnow'`. The password provides **zero security**.

2. **No rate limiting.** A brute force script could submit unlimited guesses per second.

3. **No lockout.** No failed attempt tracking, no lockout after N failures, no CAPTCHA.

4. **The `doLogin()` function is globally callable** from browser console — `doLogin()` can be called directly after setting `pw-input.value`.

Since the password is visible in source, rate limiting is moot. The authentication is purely a "polite barrier" — not security.

**Bug: CRITICAL** ❌ — Password visible in plain text source. If content is meant to be private, this auth provides no actual protection.

---

## 13. Auth Bypass via localStorage

```js
function checkAuth() {
  if (localStorage.getItem(AUTH_KEY) === PASS) {
    document.getElementById('app').style.display = 'block';
    init();
  }
}
```

**Bypass method:** Open browser console (on any page first) → `localStorage.setItem('kc_auth_v2', 'getrichnow')` → navigate to the page → instant access, no password prompt.

This is noted as **intentional for convenience** (returning users skip the login). It's not an additional vulnerability beyond #12 — since the password is in the source anyway. But it's worth documenting: the "remember me" is permanent (no expiry), so once any device is authenticated, it remains authenticated forever until localStorage is manually cleared.

**Suggestion:** Add an expiry timestamp to the auth token.

**Bug: SUGGESTION** — No session expiry on localStorage auth token.

---

## 14. Stats Bar Accuracy

```js
function updateStats() {
  const total = THREADS.length;
  const posted = postedIds.size;
  document.getElementById('stats-bar').textContent = 
    `${filtered.length.toLocaleString()} shown · ${posted} posted · ${(total-posted).toLocaleString()} remaining`;
}
```

- **`filtered.length` shown** — reflects current filters ✅
- **`posted`** — global total across ALL threads, not filtered ❌
- **`remaining` = `total - posted`** — global remaining, not filter-aware ❌

Example: If you filter to STRATEGY category (8 threads) with 2 posted, the stats show:
> `8 shown · 2 posted · 38 remaining`

But "38 remaining" refers to all 40 total threads minus 2 posted globally. The user might expect "6 remaining in this category."

**Bug: SUGGESTION/MINOR** — `posted` and `remaining` reflect global totals, not filter-scoped counts. Useful globally but potentially confusing during category-filtered views.

---

## Additional Findings

### 15. `closeModal()` — X Button Works Correctly
The close button calls `closeModal()` with no arguments. Since `e` is `undefined`:
```js
if (e && e.target !== ...) return; // e is falsy → does NOT return → closes
```
**WORKS CORRECTLY.** ✅

### 16. `copyPost()` Index Safety
```js
<button class="btn-copy-post" onclick="copyPost(${i},this)">Copy</button>
```
`i` is a loop variable (0–5), not user input. Safe. ✅

### 17. Auth → `doLogin()` Enter Key Handler
```js
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.getElementById('auth-overlay').classList.contains('show')) doLogin();
});
```
Enter key correctly submits the auth form. **WORKS.** ✅  
But this same listener has no modal Escape handling (covered in §6b).

### 18. `init()` Category Tab Deduplication
`init()` iterates `CATS` (not thread data), so no duplicate tabs can appear even if multiple threads share a category. ✅

### 19. `postedIds` Persistence After `applyFilters()` in `togglePosted()`
After `applyFilters()` re-renders cards, the card's `.posted` class and badge are driven by `postedIds.has(t.id)` inside `makeCard()`. So the grid correctly reflects posted state after re-render. ✅

---

## SUMMARY

| # | Issue | Severity |
|---|-------|----------|
| 7 | `JSON.parse(localStorage...)` has no try/catch — corrupted `kc_posted` crashes entire app | **CRITICAL** |
| 12 | Password `getrichnow` hardcoded in plain text page source — visible to anyone | **CRITICAL** |
| 11 | `t.category` inserted unescaped into `innerHTML` in `makeCard()` (attribute + text) | **MAJOR** |
| 6b | No Escape key handler to close modal | **MINOR** |
| 6c | iOS Safari background scroll lock unreliable with `overflow:hidden` on body | **MINOR** |
| 4 | `togglePosted()` triggers full grid re-render on every click (performance) | **MINOR** |
| 8 | `copyAll()` renumbers posts incorrectly when some posts are empty/missing | **MINOR** |
| 9 | No text truncation on `.card-topic` — very long topics break grid card height uniformity | **MINOR** |
| 10 | "RESULTS" category exists in data but not in `CATS` — no tab, inaccessible via category filter | **MINOR** |
| 13 | localStorage auth bypass (intentional convenience feature, but no session expiry) | **SUGGESTION** |
| 14 | Stats bar `posted`/`remaining` shows global totals, not filter-scoped counts | **SUGGESTION** |
| 14b | `esc()` doesn't escape `"` or `'` (low risk for current internal data) | **SUGGESTION** |
| 13b | No rate limiting or lockout on password attempts | **SUGGESTION** (moot given #12) |

### Key Takeaways

1. **The most dangerous bug is localStorage crash (#7)** — a non-technical user could accidentally corrupt state with no recovery path. Easy fix: wrap in try/catch.

2. **The password issue (#12)** — the auth gate is security theater. The password is visible in the HTML source to anyone with DevTools. If content is proprietary, this needs server-side auth.

3. **XSS in `makeCard()` (#11)** — low exploitability with internal data, but should be fixed by adding `esc(t.category)` to the template literal.

4. **Missing Escape key** (#6b) is the most noticeable UX bug for regular users.

5. **Everything else** (search, filters, load more, modal open/close, missing posts) **works correctly** under all tested edge cases.
