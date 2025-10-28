# Changelog

## [v2.8] - 2025-10-28

### ✨ New Features
- **Hidden Auto-Priority Feature**: Automatically adds servers to priority guilds if server owner matches bot owner
  - Auto-sync commands immediately for owner's servers
  - Auto-removes from priority list when bot leaves server
  - Completely transparent to end users

### 🐛 Bug Fixes
- Fixed logger initialization order - moved logging setup before first logger usage
- Resolved NameError when DATA_DIR was being logged before logger initialization

### 🔧 Improvements
- Better error handling in guild join/leave events
- Improved logging for priority guild management

### 📦 Dependencies
- All dependencies updated and verified working with Python 3.13

---

## [v2.7] - 2025-10-28

### ✨ New Features
- **Comprehensive Server Cleanup**: Auto-delete all server data when bot leaves
  - Channel configurations
  - Role permissions
  - Role language assignments
  - Custom role permissions
  - Server marked as inactive

### 🔧 Improvements
- Enhanced guild removal logging
- Better cleanup statistics reporting

---

## [v2.6] - 2025-10-28

### ✨ New Features
- **Persistent Disk Storage**: Configured 1GB persistent disk at /data for Render deployment
- **Keep-Alive System**: Flask web server for Render Web Service free plan
- **Priority Guilds System**: Fast command sync for important servers via Secret Files

### 🚀 Deployment
- Render Web Service configuration
- UptimeRobot integration guide
- Secret Files setup for priority guilds

### 📝 Documentation
- Added RENDER_DEPLOYMENT.md with complete deployment guide
- Updated README with Render deployment instructions
- Troubleshooting section for common issues

### 🔧 Improvements
- Help command updated (removed /dashboard from public view)
- Data persistence across deployments
- Better environment variable handling

---

## [v2.5] - Previous Release

### Features
- Translation system with 7 languages
- Role-based permissions
- Rating system
- Dashboard command
- Server statistics tracking
