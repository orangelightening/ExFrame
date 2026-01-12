# EEFrame Breakage Summary
## Date: 2026-01-10

## PROBLEM
Application is completely broken - page loads but Alpine.js does not initialize, leaving a blank/white screen.

## CHANGES MADE BEFORE BREAKAGE

### Files Modified:
1. `/home/peter/development/eeframe/generic_framework/frontend/index.html`
2. `/home/peter/development/eeframe/generic_framework/api/app.py`

### Changes to index.html:

#### 1. Changed Edit Icon (line 542)
- Changed from pencil icon to gear/settings icon
- Changed title from "Edit" to "Edit Settings"

#### 2. Added Plugin Settings Section to Domain Form (after line 722)
- **New section:** Router Configuration (dropdown + confidence threshold input)
- **New section:** Formatter Configuration (dropdown + max examples input)
- **New section:** Enrichers Configuration (list with add/remove)
- **New section:** Specialist Plugins Configuration (list)
- All sections wrapped in: `<div x-show="editingDomain && !creatingDomain">`

#### 3. Added Separate Plugin Settings Modal (after line 763)
- This is a DUPLICATE/REDUNDANT modal that was meant to be removed
- Contains same sections as above but uses `pluginSettings` state instead of `domainForm`

#### 4. Modified JavaScript State (line 1201)
**BEFORE:**
```javascript
domainForm: {
    domain_id: '',
    domain_name: '',
    description: '',
    categories: [],
    tags: [],
    specialists: []
}
```

**AFTER:**
```javascript
domainForm: {
    domain_id: '',
    domain_name: '',
    description: '',
    categories: [],
    tags: [],
    specialists: [],
    // Plugin pipeline settings
    router: {
        module: 'plugins.routers.confidence_router',
        class: 'ConfidenceBasedRouter',
        config: { threshold: 0.30 }
    },
    formatter: {
        module: 'plugins.formatters.markdown_formatter',
        class: 'MarkdownFormatter',
        config: { max_examples_per_pattern: 3 }
    },
    enrichers: [],
    plugins: []
}
```

#### 5. Modified editDomain() Method (line 1598)
**ADDED at end of domainForm assignment:**
```javascript
// Plugin pipeline settings
router: data.router || { ...defaults... },
formatter: data.formatter || { ...defaults... },
enrichers: data.enrichers || [],
plugins: data.plugins || []
```

#### 6. Modified saveDomain() Method (line 1642)
**ADDED after basic domain save:**
```javascript
// If editing (not creating), also save plugin settings
if (!this.creatingDomain) {
    const pluginPayload = {
        router: this.domainForm.router,
        formatter: this.domainForm.formatter,
        enrichers: this.domainForm.enrichers,
        plugins: this.domainForm.plugins
    };

    const pluginRes = await fetch(`/api/admin/domains/${this.domainForm.domain_id}/plugins`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pluginPayload)
    });

    if (!pluginRes.ok) {
        const error = await pluginRes.json();
        throw new Error('Domain saved but plugin settings failed: ' + (error.detail || 'Unknown error'));
    }
}
```

#### 7. Modified cancelDomainEdit() Method (line 1710)
**ADDED plugin fields reset:**
```javascript
router: { ...defaults... },
formatter: { ...defaults... },
enrichers: [],
plugins: []
```

#### 8. Added Plugin Settings Methods (NEW - line 1739)
- `async editPluginSettings(domainId)` - Opens separate modal
- `cancelPluginEdit()` - Closes separate modal
- `async savePluginSettings()` - Saves to `/api/admin/domains/{id}/plugins`
- `addEnricher()` - Adds enricher to `pluginSettings.enrichers`
- `removeEnricher(index)` - Removes enricher

### Changes to api/app.py:

#### Modified get_domain_config() endpoint (line 715)
**ADDED defaults:**
```python
# Add default router if not present
if "router" not in domain_config:
    domain_config["router"] = {
        "module": "plugins.routers.confidence_router",
        "class": "ConfidenceBasedRouter",
        "config": {"threshold": 0.30}
    }

# Add default formatter if not present
if "formatter" not in domain_config:
    domain_config["formatter"] = {
        "module": "plugins.formatters.markdown_formatter",
        "class": "MarkdownFormatter",
        "config": {"max_examples_per_pattern": 3}
    }

# Add default enrichers if not present
if "enrichers" not in domain_config:
    domain_config["enrichers"] = []
```

---

## LIKELY CAUSE OF BREAKAGE

The breakage is likely due to **one of these issues**:

### 1. DUPLICATE MODAL CONFLICT
There are now TWO plugin settings modals:
- One integrated into domain form (uses `domainForm`)
- One separate modal (uses `pluginSettings`)

The separate modal code references `pluginSettings` but may have typos or inconsistencies.

### 2. MISSING OR BROKEN Alpine.js DATA BINDING
The new sections use:
- `x-model="domainForm.router.class"`
- `x-model="domainForm.router.config.threshold"`
- `x-model="domainForm.formatter.class"`
- etc.

If any of these paths are malformed or reference undefined properties during initialization, Alpine.js will fail to initialize.

### 3. TEMPLATE RENDERING ERROR
The `<template x-for="(enricher, index) in domainForm.enrichers">` loops may fail if:
- `domainForm.enrichers` is undefined during initial render
- The enricher objects don't have expected properties

### 4. JAVASCRIPT SYNTAX ERROR
Check for:
- Missing commas between methods
- Unclosed braces
- Missing quotes in strings

---

## HOW TO REVERT

### Quick Revert (to restore working app):

```bash
# Revert to last working commit
git checkout HEAD -- generic_framework/frontend/index.html
git checkout HEAD -- generic_framework/api/app.py

# Rebuild container
docker-compose build eeframe-app && docker-compose restart eeframe-app
```

### OR Manual Revert Steps:

1. **Remove the plugin settings section from domain form** (lines ~726-846)
2. **Remove the separate plugin settings modal** (lines ~886-1062)
3. **Restore original domainForm state** (remove router, formatter, enrichers, plugins)
4. **Restore original editDomain() method**
5. **Restore original saveDomain() method**
6. **Restore original cancelDomainEdit() method**
7. **Remove plugin settings methods** (editPluginSettings, cancelPluginEdit, savePluginSettings, addEnricher, removeEnricher)
8. **Keep API changes** (they provide defaults and don't break anything)

---

## SAFE WAY FORWARD (if keeping the feature)

1. **Keep only ONE plugin settings UI** - remove the duplicate modal
2. **Add defensive null checks** in templates:
   ```html
   <div x-show="editingDomain && domainForm.enrichers && domainForm.enrichers.length > 0">
   ```
3. **Initialize all array properties** with `[]` not undefined
4. **Test in browser console** before building container:
   ```javascript
   // In browser console after page load:
   Alpine.store('app').domainForm.router
   ```

---

## FILES TO CHECK FOR ERRORS

1. **generic_framework/frontend/index.html**
   - Lines 726-846: Plugin settings in domain form
   - Lines 886-1062: Separate plugin settings modal (DUPLICATE - should remove)
   - Lines 1201-1221: domainForm state
   - Lines 1598-1633: editDomain method
   - Lines 1642-1708: saveDomain method
   - Lines 1710-1736: cancelDomainEdit method
   - Lines 1739-1820+: Plugin settings methods

---

## CONTAINER STATUS

Current container: `eeframe-app` (running but serving broken frontend)
Built from: `/home/peter/development/eeframe/generic_framework/frontend/index.html`
API endpoint: `http://192.168.3.68:3000`

Health check passes but frontend Alpine.js does not initialize.

---

## NEXT STEPS

1. **Quick revert** to restore working app
2. **Add browser console error logs** to this document
3. **Implement feature incrementally** with testing at each step
