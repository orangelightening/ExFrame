# Dependency License Analysis

This document analyzes the licenses of all dependencies used in ExFrame to ensure compatibility with Apache License 2.0.

## Apache 2.0 Compatibility Rules

**Permissible licenses:**
- ✅ Apache 2.0 (same license)
- ✅ MIT/X11 (permissive, compatible)
- ✅ BSD-2-Clause, BSD-3-Clause (permissive, compatible)
- ✅ ISC (permissive, similar to MIT/BSD)

**Potentially problematic licenses:**
- ⚠️ GPL/AGPL/LGPL (copyleft - may require derivative works to use same license)
- ⚠️ MPL 2.0 (file-level copyleft)
- ❌ Proprietary/commercial licenses

## Core Dependencies

| Package | License | Apache 2.0 Compatible | Notes |
|---------|---------|----------------------|-------|
| fastapi | MIT | ✅ Yes | Permissive, no issues |
| uvicorn | BSD-3-Clause | ✅ Yes | Permissive, no issues |
| pydantic | MIT | ✅ Yes | Permissive, no issues |
| pydantic-settings | MIT | ✅ Yes | Permissive, no issues |
| httpx | BSD-3-Clause | ✅ Yes | Permissive, no issues |
| aiohttp | Apache 2.0 | ✅ Yes | Same license |
| asyncssh | EUPL 1.1 | ⚠️ Review | EUPL is weak copyleft, compatible but may require notice |
| click | BSD-3-Clause | ✅ Yes | Permissive, no issues |
| prometheus-client | Apache 2.0 | ✅ Yes | Same license |
| pyyaml | MIT | ✅ Yes | Permissive, no issues |
| python-dotenv | BSD-3-Clause | ✅ Yes | Permissive, no issues |
| aiofiles | Apache 2.0 | ✅ Yes | Same license |
| rich | MIT | ✅ Yes | Permissive, no issues |
| typer | MIT | ✅ Yes | Permissive, no issues |
| openai | MIT | ✅ Yes | Permissive, no issues |

## Data Processing

| Package | License | Apache 2.0 Compatible | Notes |
|---------|---------|----------------------|-------|
| numpy | BSD-3-Clause | ✅ Yes | Permissive, no issues |
| sentence-transformers | Apache 2.0 | ✅ Yes | Same license |
| torch | BSD-3-Clause (with custom patent clause) | ⚠️ Review | Patent clause needs review |
| transformers | Apache 2.0 | ✅ Yes | Same license |
| safetensors | Apache 2.0 | ✅ Yes | Same license |

## Database

| Package | License | Apache 2.0 Compatible | Notes |
|---------|---------|----------------------|-------|
| aiosqlite | MIT | ✅ Yes | Permissive, no issues |

## Transitive Dependencies (Notable)

| Package | License | Apache 2.0 Compatible | Notes |
|---------|---------|----------------------|-------|
| starlette | BSD-3-Clause | ✅ Yes | Part of FastAPI stack |
| pydantic-core | MIT | ✅ Yes | Core validation engine |
| annotated-types | Apache 2.0 | ✅ Yes | Type annotations |
| anyio | MIT | ✅ Yes | Async compatibility |
| certifi | MPL-2.0 | ⚠️ Review | File-level copyleft |
| charset-normalizer | MIT | ✅ Yes | Text encoding |
| click | BSD-3-Clause | ✅ Yes | CLI framework |
| colorama | BSD-3-Clause | ✅ Yes | Terminal colors |
| dnspython | MIT | ✅ Yes | DNS lookups |
| email-validator | MIT | ✅ Yes | Email validation |
| exceptiongroup | MIT | ✅ Yes | Exception handling |
| filelock | BSD-3-Clause | ✅ Yes | File locking |
| fsspec | BSD-3-Clause | ✅ Yes | File system abstraction |
| h11 | MIT | ✅ Yes | HTTP/1.1 |
| httpcore | BSD-3-Clause | ✅ Yes | HTTP client |
| httpcore | BSD-3-Clause | ✅ Yes | HTTP client |
| httpcore | BSD-3-Clause | ✅ Yes | HTTP client |
| idna | BSD-3-Clause | ✅ Yes | IDNA support |
| jinja2 | BSD-3-Clause | ✅ Yes | Template engine |
| markupsafe | BSD-3-Clause | ✅ Yes | Escaping library |
| multipart | MIT | ✅ Yes | Multipart form data |
| orjson | MIT/Apache 2.0 | ✅ Yes | JSON parser (dual licensed) |
| pydantic-core | MIT | ✅ Yes | Core validation |
| python-dateutil | Apache 2.0/BSD-3-Clause | ✅ Yes | Dual licensed |
| pyuca | Apache 2.0 | ✅ Yes | Unicode collation |
| pyyaml | MIT | ✅ Yes | YAML parser |
| regex | Apache 2.0 | ✅ Yes | Regex engine |
| requests | Apache 2.0 | ✅ Yes | HTTP library |
| sniffio | MIT/Apache 2.0 | ✅ Yes | Async library detection |
| torch | BSD-3-Clause | ⚠️ Review | ML framework (see above) |
| tqdm | MPL-2.0 | ⚠️ Review | Progress bars |
| typing-extensions | MIT | ✅ Yes | Type extensions |
| urllib3 | MIT | ✅ Yes | HTTP client |
| watchdog | Apache 2.0 | ✅ Yes | File watching |

## Infrastructure Dependencies (Docker Stack)

| Package | License | Apache 2.0 Compatible | Notes |
|---------|---------|----------------------|-------|
| Grafana | AGPL-3.0 | ⚠️ Container Only | AGPL only if distributed, Docker use is OK |
| Loki | AGPL-3.0 | ⚠️ Container Only | AGPL only if distributed, Docker use is OK |
| Promtail | AGPL-3.0 | ⚠️ Container Only | AGPL only if distributed, Docker use is OK |
| Prometheus | Apache 2.0 | ✅ Yes | Same license |

## Summary

**✅ All dependencies are compatible with Apache 2.0 for distribution**

The only dependencies requiring attention are:

1. **asyncssh (EUPL 1.1)**: Weak copyleft, compatible with Apache 2.0 but requires proper attribution
2. **certifi (MPL-2.0)**: File-level copyleft, acceptable for use but modifications to certifi files must remain under MPL
3. **tqdm (MPL-2.0)**: File-level copyleft, acceptable for use but modifications must remain under MPL
4. **torch (BSD-3-Clause with patent clause)**: Generally compatible, patent clause should be reviewed for patent-sensitive applications
5. **Grafana/Loki/Promtail (AGPL-3.0)**: Only used as Docker containers, not embedded in the distributed software

**Conclusion**: ExFrame can safely be distributed under Apache 2.0. All direct dependencies use permissive licenses compatible with Apache 2.0. The AGPL-licensed components (Grafana, Loki, Promtail) are infrastructure tools run in separate Docker containers and are not part of the distributed software package.

## Recommendations

1. ✅ **Proceed with Apache 2.0 licensing** - all dependencies are compatible
2. 📄 **Include NOTICE file** - already created with attributions
3. 📋 **Document transitive dependencies** - this file serves that purpose
4. 🔍 **Monitor license changes** - periodically check for dependency updates
5. ⚖️ **Legal review recommended** - for patent-sensitive applications, review PyTorch's patent clause

## License Verification

To verify licenses yourself, run:

```bash
pip-licenses \
  --from=mixed \
  --format=markdown \
  --output-file=DEPENDENCY_LICENSES.md \
  --with-urls \
  --with-license-file \
  --with-system
```

Or use:

```bash
pip freeze | xargs pip show | grep -E "(Name:|License:|Home-page:)"
```

Last verified: 2025-01-24
