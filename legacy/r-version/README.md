# AutoSHUD - R Version (Archived)

**Status**: 🔴 **DEPRECATED**

This directory contains the original R-based AutoSHUD implementation, archived on 2025-10-22.

---

## ⚠️ This Version is No Longer Maintained

**The R version has been replaced by [pyAutoSHUD](../../pyAutoSHUD/)** - a complete Python rewrite with:

- ✅ Better performance
- ✅ Modern CLI interface
- ✅ GPU acceleration support (5-20x faster)
- ✅ Better documentation
- ✅ Active development

## 📦 Archive Contents

```
r-version/
├── *.R (19 files)          # Main workflow scripts
├── Rfunction/ (32 files)   # R function library
├── SubScript/ (13 files)   # Helper scripts
└── Table/                  # Lookup tables
```

## 🔄 Migrating to Python

Please see: [../../MIGRATION_R_TO_PYTHON.md](../../MIGRATION_R_TO_PYTHON.md)

Quick start with Python version:

```bash
cd ../../pyAutoSHUD
pip install -r requirements.txt
pyautoshud init myproject
pyautoshud run myproject/config.yaml
```

## 📚 Historical Reference

This R version is preserved for:
- Historical reference
- Users who need to compare implementations
- Academic reproducibility of past research

**For all new projects, use pyAutoSHUD.**

---

**Archived**: 2025-10-22
**Preserved in branch**: `r-version-legacy`
