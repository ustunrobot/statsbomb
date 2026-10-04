# Football Intelligence - Build System Index

Complete reference for the multi-platform deployment system.

## Quick Navigation

**Starting Fresh?** → Start with [QUICK_START.md](build/QUICK_START.md)  
**First Time Building?** → Read [EXECUTION_GUIDE.md](build/EXECUTION_GUIDE.md)  
**Understanding Setup?** → See [BUILD_REQUIREMENTS.md](build/BUILD_REQUIREMENTS.md)  
**Need Details?** → Check [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md)

---

## Directory Structure

```
football_analytics/
├── DEPLOYMENT_STRATEGY.md          # Main deployment guide (overview)
├── BUILD_SYSTEM_INDEX.md           # This file
├── build/
│   ├── QUICK_START.md              # 5-minute quick start
│   ├── EXECUTION_GUIDE.md          # Step-by-step instructions
│   ├── BUILD_REQUIREMENTS.md       # System requirements & tools
│   ├── SOURCE_CODE_PROTECTION.md   # Security & obfuscation methods
│   ├── DISTRIBUTION_GUIDE.md       # Publishing & signing
│   ├── launcher/
│   │   ├── launcher.py             # Cross-platform launcher
│   │   ├── launcher_win.py         # Windows-specific
│   │   ├── launcher_linux.sh       # Linux launcher script
│   │   └── launcher_mac.py         # macOS-specific
│   ├── build_windows.py            # Windows build script
│   ├── build_linux.sh              # Linux build script
│   ├── build_macos.py              # macOS build script
│   ├── pyinstaller.spec            # PyInstaller configuration
│   ├── inno_setup.iss              # Windows installer config
│   └── snapcraft.yaml              # Linux snap config
├── app_backend/
│   ├── app.py                      # Flask application
│   ├── requirements.txt            # Python dependencies
│   └── ...
├── app_frontend/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── ...
└── dist/                           # Output directory (after build)
    ├── football-intelligence.exe   # (Windows)
    ├── football-intelligence       # (Linux executable)
    ├── football-intelligence-*.AppImage  # (Linux portable)
    ├── football-intelligence.app/  # (macOS app bundle)
    └── ...
```

---

## Building for Each Platform

### Quick Build Summary

| Platform | Time | Command | Output |
|----------|------|---------|--------|
| Windows | 2-10 min | `python build/build_windows.py` | `.exe` file |
| Linux | 5-15 min | `bash build/build_linux.sh` | Binary + AppImage |
| macOS | 10-20 min | `python3 build/build_macos.py` | `.app` + `.dmg` |
| iPad/Web | 15-30 min | Deploy to server | URL |

### Full Build Process

**For All Platforms:**
1. Setup environment (Python 3.8+, pip packages)
2. Install dependencies (PyInstaller, PyArmor)
3. Run platform build script
4. Test executable
5. (Optional) Sign & notarize
6. Distribute

---

## File Reference

### Documentation Files

| File | Purpose | Read When |
|------|---------|-----------|
| [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md) | Architecture & overview | First time, architecture questions |
| [build/QUICK_START.md](build/QUICK_START.md) | 5-minute quick start | Impatient to build |
| [build/EXECUTION_GUIDE.md](build/EXECUTION_GUIDE.md) | Detailed step-by-step | Following exact instructions |
| [build/BUILD_REQUIREMENTS.md](build/BUILD_REQUIREMENTS.md) | System requirements | Setting up build environment |
| [build/SOURCE_CODE_PROTECTION.md](build/SOURCE_CODE_PROTECTION.md) | Security methods | Protecting source code |
| [build/DISTRIBUTION_GUIDE.md](build/DISTRIBUTION_GUIDE.md) | Publishing & signing | Releasing to users |

### Launcher Scripts

| File | Platform | Purpose |
|------|----------|---------|
| [launcher.py](build/launcher/launcher.py) | All | Cross-platform launcher (main) |
| [launcher_win.py](build/launcher/launcher_win.py) | Windows | Windows-specific enhancements |
| [launcher_linux.sh](build/launcher/launcher_linux.sh) | Linux | Linux bash launcher |
| [launcher_mac.py](build/launcher/launcher_mac.py) | macOS | macOS-specific features |

### Build Scripts

| File | Platform | Purpose |
|------|----------|---------|
| [build_windows.py](build/build_windows.py) | Windows | Python build automation |
| [build_linux.sh](build/build_linux.sh) | Linux | Bash build automation |
| [build_macos.py](build/build_macos.py) | macOS | Python build automation |

### Configuration Files

| File | Purpose | Platform |
|------|---------|----------|
| [pyinstaller.spec](build/pyinstaller.spec) | PyInstaller config | All |
| [inno_setup.iss](build/inno_setup.iss) | Windows installer | Windows |
| [snapcraft.yaml](build/snapcraft.yaml) | Linux snap package | Linux |

---

## Common Workflows

### Scenario 1: "I want to build right now"
```bash
# Go to build/
cd football_analytics/build

# For your platform:
python build_windows.py          # Windows
bash build_linux.sh              # Linux
python3 build_macos.py           # macOS

# Output appears in dist/
```
**Time: 5-15 minutes**

---

### Scenario 2: "I need to understand the system first"

1. Read [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md) - understand overview
2. Read [build/QUICK_START.md](build/QUICK_START.md) - quick walkthrough
3. Read [build/BUILD_REQUIREMENTS.md](build/BUILD_REQUIREMENTS.md) - check prerequisites
4. Follow [build/EXECUTION_GUIDE.md](build/EXECUTION_GUIDE.md) - detailed steps

**Time: 30-60 minutes**

---

### Scenario 3: "I want to protect source code"

1. Read [build/SOURCE_CODE_PROTECTION.md](build/SOURCE_CODE_PROTECTION.md)
2. Choose method:
   - Basic: PyInstaller only (default)
   - Recommended: PyInstaller + PyArmor obfuscation
   - Maximum: Hybrid (Cython + PyArmor)
3. Add flag to build script:
   ```bash
   python build/build_windows.py --obfuscate
   ```

**Time: 5 extra minutes for obfuscation**

---

### Scenario 4: "I want to sign and publish"

1. Read [build/DISTRIBUTION_GUIDE.md](build/DISTRIBUTION_GUIDE.md)
2. Get code signing certificate
3. Build with signing:
   ```bash
   python build/build_windows.py --sign "certificate.pfx"
   python3 build/build_macos.py --sign "Developer ID"
   ```
4. Publish to GitHub Releases or web server

**Time: 30-60 minutes (depending on certificate process)**

---

### Scenario 5: "Deploy to cloud for iPad access"

1. Choose cloud platform (Heroku, AWS, Google Cloud, etc.)
2. Follow deployment instructions for platform
3. Deploy backend to cloud URL
4. Users access via Safari URL or PWA
5. (Optional) Build native iPad app with Capacitor

**Time: 30-60 minutes**

---

## Build Output Files

### Windows Output
```
dist/
├── football-intelligence.exe           (50-70 MB)
├── football-intelligence-setup.exe     (30-50 MB, if installer built)
├── _internal/                          (runtime libraries)
└── BUILD_INFO.json                     (metadata)
```

### Linux Output
```
dist/
├── football-intelligence                (70-90 MB)
├── football-intelligence-x86_64.AppImage (80-100 MB)
├── football-intelligence.sh             (launcher)
├── football-intelligence.desktop        (launcher entry)
└── BUILD_INFO.json                     (metadata)
```

### macOS Output
```
dist/
├── football-intelligence.app/           (app bundle)
│   ├── Contents/
│   │   ├── Info.plist
│   │   ├── MacOS/football-intelligence
│   │   └── Resources/
│   └── ... (supporting files)
├── football-intelligence-1.0.0.dmg     (100-150 MB)
└── BUILD_INFO.json                     (metadata)
```

---

## Key Features

### Multi-Platform Support
- ✓ Windows 10/11 (.exe)
- ✓ Linux Ubuntu 20.04+ (binary + AppImage + snap)
- ✓ macOS 10.13+ (.app + .dmg)
- ✓ iPad (web + native app option)

### Source Code Protection
- ✓ PyInstaller (bytecode only, no .py files)
- ✓ PyArmor obfuscation (unreadable if decompiled)
- ✓ Cython compilation (machine code, maximum protection)
- ✓ Code signing (tamper detection)

### Automatic Features
- ✓ Backend Flask server auto-start
- ✓ Browser auto-open
- ✓ Port conflict detection
- ✓ Graceful shutdown
- ✓ Error handling & logging

### Distribution
- ✓ Single executable per platform
- ✓ No Python installation needed
- ✓ GitHub Releases integration
- ✓ Auto-update capability (Windows/macOS)
- ✓ Code signing & notarization

---

## Troubleshooting Quick Reference

### Build Fails
→ [Build Requirements](build/BUILD_REQUIREMENTS.md#troubleshooting)

### App Won't Start
→ [Execution Guide](build/EXECUTION_GUIDE.md#troubleshooting-windows)

### Distribution Questions
→ [Distribution Guide](build/DISTRIBUTION_GUIDE.md#troubleshooting-distribution-issues)

### Source Code Protection
→ [Source Code Protection](build/SOURCE_CODE_PROTECTION.md)

### Platform-Specific
- Windows → [Execution Guide Windows section](build/EXECUTION_GUIDE.md#windows-build)
- Linux → [Execution Guide Linux section](build/EXECUTION_GUIDE.md#linux-build)
- macOS → [Execution Guide macOS section](build/EXECUTION_GUIDE.md#macos-build)
- iPad → [Execution Guide iPad section](build/EXECUTION_GUIDE.md#ipad--web-deployment)

---

## Version Information

- **Build System**: PyInstaller + Custom Scripts
- **Launcher**: Cross-platform Python
- **Supported Python**: 3.8+
- **Last Updated**: September 2026

---

## Dependencies

### Build-Time (needed to build)
- Python 3.8+
- PyInstaller 5.x
- PyArmor 8.x (optional)
- Cython (optional)
- Platform-specific tools

### Run-Time (bundled in executable)
- Python runtime
- Flask 2.3.0
- All app dependencies (bundled automatically)

See [BUILD_REQUIREMENTS.md](build/BUILD_REQUIREMENTS.md) for complete list.

---

## Environment Setup

### Quick Setup (All Platforms)
```bash
# 1. Navigate to project
cd football_analytics

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate (Linux/Mac: source venv/bin/activate)
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r app_backend/requirements.txt
pip install pyinstaller pyarmor

# 5. Build
python build/build_windows.py  # or Linux/Mac equivalent
```

---

## Performance Benchmarks

| Metric | Expected |
|--------|----------|
| Build time | 2-15 minutes (depending on options) |
| Startup time | 2-5 seconds |
| App size | 40-100 MB (single file) |
| Memory usage | 150-350 MB runtime |
| CPU impact | Minimal (~5% idle) |

---

## Security & Compliance

- ✓ No hardcoded secrets (uses environment variables)
- ✓ Local-only networking (no internet access)
- ✓ Source code protected (obfuscated)
- ✓ Code can be signed (Windows/macOS)
- ✓ HTTPS ready (for cloud deployment)
- ✓ GDPR compliant (no data collection)

---

## Release Checklist

Before each release:

- [ ] All platforms build successfully
- [ ] All platforms tested
- [ ] Version numbers updated
- [ ] Release notes prepared
- [ ] Executables signed (Windows/macOS)
- [ ] macOS binary notarized (if required)
- [ ] Uploaded to distribution channels
- [ ] Installation instructions clear
- [ ] Support contact information included
- [ ] Auto-update mechanism tested

---

## Support Matrix

| Task | Resource |
|------|----------|
| Environment setup | [BUILD_REQUIREMENTS.md](build/BUILD_REQUIREMENTS.md) |
| First build | [QUICK_START.md](build/QUICK_START.md) |
| Detailed instructions | [EXECUTION_GUIDE.md](build/EXECUTION_GUIDE.md) |
| Source protection | [SOURCE_CODE_PROTECTION.md](build/SOURCE_CODE_PROTECTION.md) |
| Publishing | [DISTRIBUTION_GUIDE.md](build/DISTRIBUTION_GUIDE.md) |
| Architecture | [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md) |

---

## Next Steps

1. **Start here**: [build/QUICK_START.md](build/QUICK_START.md)
2. **Understand requirements**: [build/BUILD_REQUIREMENTS.md](build/BUILD_REQUIREMENTS.md)
3. **Follow exact steps**: [build/EXECUTION_GUIDE.md](build/EXECUTION_GUIDE.md)
4. **Build your platform**: Run appropriate build script
5. **Test thoroughly**: Follow testing checklist
6. **Protect source**: Apply obfuscation if needed
7. **Sign & publish**: Follow distribution guide

---

## Additional Resources

- PyInstaller Documentation: https://pyinstaller.readthedocs.io/
- PyArmor Documentation: https://pyarmor.readthedocs.io/
- Python Official: https://www.python.org/
- Inno Setup: https://jrsoftware.org/
- Snapcraft: https://snapcraft.io/
- AppImage: https://appimage.org/

---

## File Sizes Summary

This build system was designed to create single-file distributions:

- **Windows .exe**: 50-70 MB (includes Python runtime + all dependencies)
- **Linux binary**: 70-90 MB (statically linked where possible)
- **macOS .app**: 80-100 MB (self-contained)
- **Compressed (zip)**: 20-40 MB

Users download once, extract/install once, run directly. No Python installation required.

---

**Ready to build? Start with [build/QUICK_START.md](build/QUICK_START.md)**
