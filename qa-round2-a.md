# QA Round 2 — Team A Report
**File audited:** `/Users/kaycapbot/.openclaw/workspace/thread-browser/index.html`
**QA Agent:** Round 2 — Team A (static code analysis)

---

## Checklist: 12 Items Verified

---

### 1. Pipe Corruption Fix — `cleanForCopy()`
**STATUS: ❌ BUG — FIX NOT IMPLEMENTED**

```js
function cleanForCopy(text) {
  return text.replace(/\[ADD:[^\]]*\]/g,'').replace(/\n{3,}/g,'\n\n').trim();
}
```

The `cleanForCopy()` function strips `[ADD:...]` flags and normalises newlines, but there is **zero pipe character stripping** anywhere in the codebase. No `.replace(/\|/g, '')` or equivalent exists.

**Displayed text path:** `formatPost(text)` calls `esc(text)` which only escapes `&`, `<`, `>` — pipes pass through unmodified and render as-is in the modal.

**Copied text path:** `cleanForCopy()` also leaves pipes intact.

**Impact:** If any post in the dataset contains `|` characters (e.g. used as visual dividers), they corrupt both the displayed and copied content. The claimed v2 fix simply doesn't exist in the code.

**Severity: HIGH** (if pipes exist in data) / **MEDIUM** (if current dataset is clean — the fix is still absent)

---

### 2. Unposted Filter — Default Behaviour
**STATUS: ✅ WORKS CORRECTLY**

- `activeStatus = 'unposted'` is set at declaration. ✅
- `init()` calls `document.querySelectorAll('.status-btn').forEach(b => { b.classList.toggle('active', b.dataset.status === activeStatus); })` — restores the "Unposted" button highlight on load. ✅
- `applyFilters()` correctly uses: `if (activeStatus === 'unposted' && postedIds.has(t.id)) return false;` ✅

**Fresh user (empty postedIds):** `postedIds = new Set([])`. Nothing has been `.has()` — all threads pass the filter. All threads show. ✅ Correct.

---

### 3. Random Thread Picker (🎲)
**STATUS: ⚠️ PARTIAL BUG — Works for primary use case, broken UX for "Posted" view**

```js
function randomThread() {
  const unposted = filtered.filter(t => !postedIds.has(t.id));
  if (!unposted.length) { alert('All threads in this view have been posted! 🎉'); return; }
  openModal(unposted[Math.floor(Math.random() * unposted.length)]);
}
```

**Good:** Picks from `filtered`, which already respects category + search + status filters. ✅

**Bug — "Posted" status view:** When `activeStatus === 'posted'`, `filtered` contains only already-posted threads. `randomThread()` then applies `!postedIds.has(t.id)` → empty array → fires alert: **"All threads in this view have been posted! 🎉"** — a completely misleading message. The user is intentionally browsing posted threads; the alert is incorrect.

**Bug — "All" status view:** Double-filtering is redundant but harmless. ✅

**Severity: LOW** (UX confusion, not a crash)

---

### 4. Escape Key — `closeModal()` When Modal Closed
**STATUS: ✅ SAFE**

```js
function closeModal() {
  document.getElementById('modal-bg').classList.remove('show');
  document.body.style.overflow = '';
  currentThread = null;
}
```

- `classList.remove('show')` on an element already without 'show' is a no-op. ✅
- `body.style.overflow = ''` resets to empty (harmless if already empty). ✅
- `currentThread = null` when already null is harmless. ✅

No errors thrown. Pressing Escape when modal is closed does nothing visible and throws nothing.

---

### 5. View Original Reel Link
**STATUS: ✅ WORKS CORRECTLY**

HTML: `<a ... target="_blank" rel="noopener" style="display:none">`
- Opens in new tab via `target="_blank"`. ✅
- `rel="noopener"` security attribute present. ✅

`openModal()`:
```js
if (t.url) {
  reelLink.href = t.url;
  reelLink.style.display = 'block';
} else {
  reelLink.style.display = 'none';
}
```
- Hidden when `t.url` is empty/falsy. ✅
- Shown with correct href when URL exists. ✅

---

### 6. Logout Button
**STATUS: ✅ WORKS CORRECTLY**

```js
function doLogout() {
  if (confirm('Log out?')) { localStorage.removeItem(AUTH_KEY); location.reload(); }
}
```

- `AUTH_KEY = 'kc_auth_v3'` — removes the right key. ✅
- `location.reload()` triggers page reload. ✅
- On reload, `checkAuth()` finds no auth key → shows login overlay. ✅

---

### 7. Search All 6 Posts — Performance
**STATUS: ✅ ACCEPTABLE (with minor caveat)**

```js
const hay = (t.topic+' '+t.post1+' '+t.post2+' '+t.post3+' '+t.post4+' '+t.post5+' '+t.post6).toLowerCase();
```

Debounce is 250ms. 2994 threads × ~2000 char concatenation + toLowerCase + includes runs in <50ms on modern hardware. The 250ms debounce is sufficient.

**Minor Bug:** If `t.post4`, `t.post5`, or `t.post6` is `undefined` (missing from data), JavaScript string concatenation converts it to the literal string `"undefined"`. Searching for "undefined" would match those threads as false positives.

Scanning the visible dataset, all examined threads have all 6 posts populated, so this is low practical impact.

**Severity: LOW** (data quality dependent)

---

### 8. localStorage Safety — Private Browsing
**STATUS: ❌ BUG — Auth system bypasses safeGet/safeSet**

`safeGet()` and `safeSet()` correctly wrap localStorage in try/catch. ✅

**However**, the auth system does NOT use these safe helpers:

```js
function checkAuth() {
  if (localStorage.getItem(AUTH_KEY) === PASS) {  // ← NO try/catch
```
```js
function doLogin() {
  ...
  localStorage.setItem(AUTH_KEY, PASS);  // ← NO try/catch
```
```js
function doLogout() {
  ...
  localStorage.removeItem(AUTH_KEY);  // ← NO try/catch
```

If localStorage is completely blocked (Firefox/Safari in certain private browsing modes, strict tracking protection, or corporate policies), `localStorage.getItem()` throws `SecurityError: The operation is insecure.`. This is an **uncaught exception** in `checkAuth()` which runs at startup — **the entire app crashes on load**, showing a blank/broken page.

`safeGet`/`safeSet` exist but auth was wired up bypassing them.

**Severity: MEDIUM** — App is completely unusable in affected environments.

---

### 9. Copy Fallback — `execCommand`
**STATUS: ⚠️ INCONSISTENCY BUG in `copyAll()`**

**`copyPost()` fallback — WORKS:**
```js
}).catch(() => {
    ...
    document.execCommand('copy');
    document.body.removeChild(el);
    btn.textContent = '✓ Copied!';  // ← feedback given ✅
    setTimeout(() => { btn.textContent = 'Copy'; }, 1500);
  });
```

**`copyAll()` fallback — BROKEN:**
```js
}).catch(() => {
    ...
    document.execCommand('copy');
    document.body.removeChild(el);
    // ← NO btn.textContent update! User gets zero feedback ❌
  });
```

In `copyAll()`, the `.catch()` block executes the copy but **never updates the "Copy All 6 Posts" button text**. When the clipboard API fails and the fallback fires, the user sees no confirmation that anything was copied. Content IS copied to clipboard, but visually the button stays frozen.

Compare: `copyPost()` DOES update button text in its fallback. This is an inconsistency.

**Severity: MEDIUM** — Silent failure UX, user may not know copy succeeded.

---

### 10. Category Persistence — Tab Highlight
**STATUS: ✅ WORKS CORRECTLY**

```js
let activeCategory = safeGet(CAT_KEY, 'ALL') || 'ALL';
```

In `init()`:
```js
btn.className = 'tab' + (cat === activeCategory ? ' active' : '');
```

On reload, `activeCategory` is restored from storage before `init()` runs, so the correct tab gets `active` class and the associated `background` color. Tab highlight correctly restores. ✅

`safeSet(CAT_KEY, cat)` is called on category change. ✅

---

### 11. Stats Bar — "X unposted" with 0 Posted Threads
**STATUS: ✅ CORRECT**

```js
function updateStats() {
  const total = THREADS.length;         // 2994
  const posted = postedIds.size;        // 0 for fresh user
  const showing = filtered.length;
  document.getElementById('stats-bar').textContent = 
    `${showing.toLocaleString()} shown · ${(total-posted).toLocaleString()} unposted`;
}
```

With 0 posted threads: `2994 - 0 = 2994 unposted` — displays correctly. ✅

Stats bar shows "X shown · Y unposted" where Y is always `total - postedIds.size` (global count, not filtered count). This is intentional and accurate. ✅

---

### 12. Modal Close on Outside Click
**STATUS: ✅ WORKS CORRECTLY**

```js
function onModalBgClick(e) {
  if (e.target === document.getElementById('modal-bg')) closeModal();
}
```

- Clicking the semi-transparent backdrop: `e.target` IS `#modal-bg` → `closeModal()` fires. ✅
- Clicking inside `.modal` content: events bubble up to `#modal-bg`'s onclick, but `e.target` is the inner element clicked (not `#modal-bg`) → strict equality fails → modal stays open. ✅

Correctly distinguishes backdrop from content clicks.

---

## Summary of Remaining Bugs

| # | Issue | Severity |
|---|-------|----------|
| 1 | `cleanForCopy()` has NO pipe stripping — the "fix" was never implemented | **HIGH** |
| 2 | Auth functions (`checkAuth`, `doLogin`, `doLogout`) access localStorage without try/catch — app crashes if localStorage is blocked | **MEDIUM** |
| 3 | `copyAll()` fallback has no visual feedback — button text not updated when clipboard API falls back | **MEDIUM** |
| 4 | 🎲 in "Posted" status view shows misleading "All threads posted!" alert | **LOW** |
| 5 | Search hay concatenates `undefined` as literal string for missing post fields | **LOW** |

---

## Verdict

**FAIL — 5 bugs remain, including 1 HIGH and 2 MEDIUM severity.**

The most critical issues: the pipe fix was simply never coded, and the auth layer is unsafe from localStorage errors. The `copyAll()` fallback feedback gap is a clean v2 regression compared to `copyPost()`.
