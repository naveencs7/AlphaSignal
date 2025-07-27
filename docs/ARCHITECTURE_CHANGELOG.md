# Architecture Changelog

| Version | Date       | Summary                                 | Technical Rationale                | Business Rationale                | Link |
|---------|------------|-----------------------------------------|------------------------------------|-----------------------------------|------|
| v1.0    | 2024-07-01 | Initial MVP: single RSS, SQLite         | Simple, fast to build              | Quick market validation           | [ARCHITECTURE_v1.md](ARCHITECTURE_v1.md) |
| v2.0    | 2024-07-10 | Multi-source news, dedup, Alembic, etc. | Scalability, future ML integration | More robust, better news quality  | [ARCHITECTURE_v2.md](ARCHITECTURE_v2.md) |

---

## v2.0 (2024-07-10)

### Summary
- Added multi-source news aggregation pipeline
- Introduced deduplication logic (rule-based)
- Switched to Alembic migrations for DB schema

### Technical Rationale
- Needed scalable, maintainable news ingestion
- Prepares for ML-based deduplication in future

### Business Rationale
- More reliable news for users
- Easier to add new sources and features

### Full Architecture
See: [ARCHITECTURE_v2.md](ARCHITECTURE_v2.md) 