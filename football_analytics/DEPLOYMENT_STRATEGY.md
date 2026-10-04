# Football Intelligence - Multi-Platform Deployment Strategy

## Overview

This document describes the deployment architecture and process for packaging the Football Intelligence application for Windows, Linux, macOS, and iPad platforms with source code protection.

## Architecture

### Application Structure
```
Football Intelligence
├── Backend (Flask/Python)
│   ├── Core Logic (Event Processing, Report Generation)
│   ├── StatsBomb Service
│   └── API Routes
├── Frontend (JavaScript/HTML/CSS)
│   ├── UI Components
│   ├── Data Visualization
│   └── Reports Display
└── Native Launcher (Platform-Specific)
    ├── Windows (.exe)
    ├── Linux (AppImage/snap)
    ├── macOS (.app)
    └── iPad (Web wrapper)
```

### Deployment Flow

```
Source Code
    ↓
PyInstaller (Compile Python → Binary)
    ↓
Obfuscate/Encrypt (Optional Layer)
    ↓
Platform-Specific Bundler
    ├─→ Windows: Inno Setup Installer
    ├─→ Linux: AppImage or snap package
    ├─→ macOS: Create .app bundle
    └─→ iPad: Web wrapper/PWA
    ↓
Distribution (GitHub Releases, S3, etc.)
    ↓
End User (Download & Run)
```

## Platform-Specific Strategies

### 1. Windows (.exe)

**Approach**: PyInstaller → Inno Setup → Signed Executable

**Advantages**:
- Single .exe file download
- No Python installation required
- Can auto-launch with Windows startup
- Signed executables prevent security warnings

**Process**:
1. Bundle Flask backend with PyInstaller
2. Include frontend assets
3. Create launcher executable
4. Package with Inno Setup installer
5. (Optional) Code sign with certificate

**Output**: `football-intelligence-setup.exe` (20-50 MB)

### 2. Linux (AppImage + snap)

**Approach A - AppImage**: PyInstaller → AppImage (portable, no installation)
**Approach B - snap**:SnapCraft packaging (distribution via snap store)

**Advantages**:
- AppImage: Universal binary, works on most distributions
- snap: Automatic updates, sandboxing, app store distribution
- Both: No Python installation needed

**Process** (AppImage):
1. Bundle with PyInstaller for Linux
2. Package with AppImage runtime
3. Create desktop launcher
4. Single portable binary

**Process** (snap):
1. Create snapcraft.yaml
2. Define stage and prime steps
3. Publish to snap store
4. Users install via `snap install`

**Output**: 
- `football-intelligence-1.0.0.AppImage` (25-50 MB)
- Or snap package installable from store

### 3. macOS (.app Bundle)

**Approach**: PyInstaller → macOS .app Bundle → DMG or ZIP

**Advantages**:
- Native .app bundle format
- Integrates with macOS Finder
- Can sign and notarize for Gatekeeper
- Auto-update capable

**Process**:
1. Bundle with PyInstaller for macOS
2. Create .app bundle structure
3. Add proper Info.plist
4. Code sign and notarize
5. Package as DMG or ZIP

**Output**: `football-intelligence-1.0.0.dmg` (30-60 MB)

### 4. iPad (Web Wrapper / PWA)

**Approach**: Progressive Web App (PWA) + Optional Native Wrapper

**Options**:
- **Option A**: Pure PWA (no installation needed)
  - Accessed via URL on Safari
  - Works offline with service worker
  - No native wrapper required
  
- **Option B**: Native iPad App
  - Wrap with Capacitor/Ionic + Xcode
  - Requires Apple Developer account
  - Available on App Store

**Process** (PWA):
1. Deploy backend to cloud server
2. Frontend already works in Safari
3. Create PWA manifest for install prompt
4. Service worker for offline capability
5. Share URL with users

**Process** (Native App):
1. Use Capacitor to wrap web app
2. Build with Xcode
3. Sign with Apple Developer credentials
4. Submit to App Store

**Output**: 
- PWA: Just share URL
- Native: `.ipa` file or App Store listing

## Source Code Protection Strategy

### Method 1: PyInstaller (Basic - Recommended for Start)

**How it works**:
- Compiles Python code to bytecode
- Packages with Python runtime
- Creates single executable
- .py files are not included

**Setup**:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --hidden-import=flask app_backend/app.py
```

**Protection Level**: Medium (bytecode decompilation possible but non-trivial)

**Pros**: Simple, fast, works out of the box
**Cons**: Can be decompiled with effort

---

### Method 2: Code Obfuscation + PyInstaller

**Tools**: PyArmor, Cython compilation

**Process**:
1. Convert critical Python files to Cython (`.pyx`)
2. Compile Cython to C extensions (`.so` / `.pyd`)
3. Obfuscate remaining Python code
4. Bundle with PyInstaller

**Protection Level**: High (binary C extensions + obfuscated Python)

**Example**:
```bash
# Install PyArmor
pip install pyarmor

# Obfuscate source code
pyarmor obfuscate --restrict app_backend/app.py

# PyInstaller uses obfuscated version
pyinstaller --onefile app_backend/app.py
```

---

### Method 3: Cython Compilation (Maximum Protection)

**How it works**:
- Converts Python to C/C++
- Compiles to machine code
- No Python bytecode at all
- Nearly impossible to decompile

**Setup**:
```bash
pip install cython
cythonize -i app_backend/app.py  # Creates .so/.pyd binary
```

**Protection Level**: Very High (machine code, source irretrievable)

**Cons**: Slower to build, some compatibility issues

---

### Method 4: Hybrid Approach (Recommended for Production)

**Strategy**: Critical modules as Cython, rest with PyInstaller + obfuscation

**Structure**:
```
app_backend/
├── app.py (PyInstaller)
├── core/
│   ├── event_processor.pyx (Cython → .so/.pyd)
│   ├── report_generator.pyx (Cython → .so/.pyd)
│   └── __init__.py (PyInstaller)
└── services/
    └── statsbomb_service.py (PyInstaller)
```

**Process**:
1. Identify critical/valuable code → Cythonize
2. Obfuscate Python code
3. Bundle everything with PyInstaller
4. No .py files in final package

## Launcher Implementation

### Unified Launcher (All Platforms)

The launcher must:
1. Start Flask backend silently
2. Wait for Flask to be ready
3. Open browser to http://127.0.0.1:5000
4. Handle graceful shutdown
5. Detect port conflicts

See: `build/launcher/launcher.py` (cross-platform)

### Platform-Specific Launchers

- **Windows**: `build/launcher/launcher_win.py` (uses subprocess, minimized window)
- **Linux**: `build/launcher/launcher_linux.sh` (bash script)
- **macOS**: `build/launcher/launcher_mac.py` (uses AppleScript for browser)

## Build Process Overview

### Step 1: Prepare Source Code
```bash
# Install build dependencies
pip install pyinstaller pyarmor cython

# Obfuscate source code
pyarmor obfuscate --restrict app_backend/

# Convert critical modules to Cython (optional)
cythonize -i app_backend/event_based/event_processor.pyx
```

### Step 2: Build Platform-Specific Executable

**Windows**:
```bash
python build/build_windows.py
# Output: dist/football-intelligence/football-intelligence.exe
```

**Linux**:
```bash
bash build/build_linux.sh
# Output: dist/football-intelligence-x86_64.AppImage
```

**macOS**:
```bash
python build/build_macos.py
# Output: dist/football-intelligence-1.0.0.dmg
```

### Step 3: Package & Sign (Optional)

- **Windows**: Sign .exe with certificate (Inno Setup integration)
- **macOS**: Notarize with Apple Developer account
- **Linux**: GPG sign AppImage

### Step 4: Distribute

- GitHub Releases (automatic)
- Direct download links
- Auto-update mechanism (Sparkle for Mac, WinSparkle for Windows)

## Configuration Files Provided

1. **`build/pyinstaller.spec`** - PyInstaller configuration for all platforms
2. **`build/launcher/launcher.py`** - Cross-platform launcher
3. **`build/launcher/launcher_win.py`** - Windows-specific launcher
4. **`build/launcher/launcher_linux.sh`** - Linux launcher script
5. **`build/launcher/launcher_mac.py`** - macOS launcher
6. **`build/build_windows.py`** - Windows build script
7. **`build/build_linux.sh`** - Linux build script
8. **`build/build_macos.py`** - macOS build script
9. **`build/inno_setup.iss`** - Windows installer configuration
10. **`build/snapcraft.yaml`** - Linux snap configuration

## Installation Instructions for End Users

### Windows
1. Download `football-intelligence-setup.exe`
2. Run installer
3. Select installation directory
4. Check "Create Start Menu shortcut"
5. Finish - shortcut appears on desktop/Start Menu
6. Click shortcut to launch

### Linux (AppImage)
1. Download `football-intelligence-x86_64.AppImage`
2. Make executable: `chmod +x football-intelligence-*.AppImage`
3. Double-click to run (or via terminal)
4. (Optional) Install: `./football-intelligence-*.AppImage --install-app-launcher`

### Linux (snap)
1. Install from snap store: `snap install football-intelligence`
2. Launch from Activities menu or: `football-intelligence`
3. Automatic updates enabled

### macOS
1. Download `football-intelligence-1.0.0.dmg`
2. Open DMG file
3. Drag `football-intelligence.app` to Applications folder
4. Launch from Applications or Spotlight search
5. (First time) Click "Open" when macOS asks about unidentified developer

### iPad (PWA)
1. Open Safari
2. Navigate to: `https://football-intelligence.example.com`
3. Tap Share button
4. Select "Add to Home Screen"
5. Name app and tap "Add"
6. App appears on home screen, launches in full-screen mode

### iPad (Native App)
1. Search "Football Intelligence" in App Store
2. Tap "Get"
3. Authenticate with Face ID/Touch ID
4. Wait for installation
5. Tap "Open" to launch

## Auto-Updates

### Windows
- Use **WinSparkle** library
- Checks for updates at startup
- Downloads and installs automatically
- Prompts user before restart

### macOS
- Use **Sparkle** framework
- Integrated into .app bundle
- Automatic background updates
- User receives notification

### Linux (snap)
- Automatic updates enabled by default
- Updates check daily
- User can control: `snap set system snapd.refresh.timer=...`

### iPad (PWA)
- Service worker handles updates
- Automatic in background
- New version loads on next open

### iPad (Native App)
- App Store handles updates
- User controls via app settings
- Can enable automatic updates

## Troubleshooting

### Port Already in Use
- Launcher detects conflict
- Automatically tries next available port
- User notified in error message

### Firewall Issues
- App only listens on 127.0.0.1 (localhost)
- No internet access required
- No firewall exceptions needed

### Browser Won't Open
- Falls back to manual URL display
- User can copy/paste URL
- Retries up to 3 times

### App Won't Start
- Check system requirements:
  - Windows: Windows 10+, 4GB RAM
  - Linux: glibc 2.29+, 4GB RAM
  - macOS: macOS 10.13+, 4GB RAM
  - iPad: iOS 13+

## Performance Optimization

### Bundle Size Reduction
- Use `--onefile` and `--strip` in PyInstaller
- Remove unused dependencies
- Lazy load heavy libraries
- Expected size: 40-80 MB depending on dependencies

### Startup Time
- Current: ~2-5 seconds
- Optimization: Cache compiled bytecode
- Use lazy imports in app.py

### Memory Usage
- Flask backend: ~100-150 MB
- Browser frontend: ~100-200 MB
- Total: ~250-350 MB

## Security Considerations

1. **Port Binding**: Only localhost (127.0.0.1), no network access
2. **API Keys**: Loaded from environment variables, not hardcoded
3. **HTTPS**: Can be enabled for cloud deployment
4. **Code Signing**: Sign executables to prevent tampering
5. **SSL/TLS**: Optional for local-only deployments
6. **Data**: No sensitive data stored in app files

## Next Steps

1. Create `build/` directory structure
2. Run build scripts for each platform
3. Test on each platform (Windows 10+, Ubuntu 20.04+, macOS 11+)
4. Sign executables (Windows/macOS)
5. Set up distribution pipeline (GitHub Actions, etc.)
6. Implement auto-update mechanism
7. Create user documentation
8. Plan release schedule

## References

- PyInstaller: https://pyinstaller.org/
- PyArmor: https://pyarmor.readthedocs.io/
- Cython: https://cython.readthedocs.io/
- Inno Setup: https://jrsoftware.org/isinfo.php
- AppImage: https://appimage.org/
- Snapcraft: https://snapcraft.io/
- Capacitor: https://capacitorjs.com/
