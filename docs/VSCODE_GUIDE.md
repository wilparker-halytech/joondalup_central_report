# 🚀 VS Code Deployment Guide for Streamlit Cloud

**For developers who use VS Code**

---

## Prerequisites

- ✅ VS Code installed
- ✅ Python 3.11+ installed
- ✅ Git installed (comes with VS Code on Windows)

---

## Quick Start (10 minutes)

### 1. Extract & Open Project (1 min)

```bash
# Extract the ZIP
cd ~/Projects  # or wherever you keep projects
unzip streamlit_vscode_package.zip -d illuminator-billing
cd illuminator-billing

# Open in VS Code
code .
```

Or use VS Code UI:
- File → Open Folder → select `illuminator-billing`

---

### 2. Test Locally (2 min - Optional)

**Open integrated terminal:** `` Ctrl+` ``

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501` 

Press `Ctrl+C` to stop.

---

### 3. Push to GitHub (3 min)

#### **Option A: VS Code UI (Easier)**

1. **Source Control icon** (left sidebar, looks like branches)
2. Click **"Initialize Repository"**
3. Click **"+"** next to "Changes" (stages all files)
4. Type commit message: `"Initial commit"`
5. Click **✓ Commit**
6. Click **"..."** → **"Remote"** → **"Add Remote"**
7. Select **"Create new repository on GitHub"**
8. Name: `illuminator-billing`
9. Public ✅
10. Click **"OK"**
11. Click **"..."** → **"Push"**

Done! Your code is on GitHub.

#### **Option B: Terminal Commands**

```bash
# Initialize Git
git init

# Stage files
git add .

# Commit
git commit -m "Initial commit - billing processor"

# Create GitHub repo (if you have GitHub CLI)
gh repo create illuminator-billing --public --source=. --push

# Or manually:
# 1. Create repo on github.com
# 2. Copy the remote URL
git remote add origin https://github.com/YOUR-USERNAME/illuminator-billing.git
git branch -M main
git push -u origin main
```

---

### 4. Deploy to Streamlit Cloud (3 min)

1. Go to https://share.streamlit.io
2. **Sign in with GitHub**
3. Click **"New app"**
4. Fill in:
   - Repository: `YOUR-USERNAME/illuminator-billing`
   - Branch: `main`
   - Main file: `streamlit_app.py`
   - App URL: Choose subdomain (e.g., `coj-billing`)
5. Click **"Deploy!"**
6. Wait 2-3 minutes
7. ✨ **App is live!**

---

## VS Code Features You'll Love

### **1. Integrated Git**

All Git operations in UI - no terminal needed:
- ✓ Commit
- ✓ Push/Pull
- ✓ Branch management
- ✓ Merge conflicts
- ✓ History view

### **2. Live Editing**

Edit code while Streamlit runs:
```bash
streamlit run streamlit_app.py
```
- Save file → Streamlit auto-reloads
- See changes instantly in browser

### **3. IntelliSense**

Auto-complete for:
- Python functions
- Streamlit functions
- Pandas methods
- Variable names

Just start typing and press `Ctrl+Space`

### **4. Debugging**

Press `F5` to debug:
- Set breakpoints
- Step through code
- Inspect variables
- See stack trace

### **5. Multi-cursor Editing**

Update all scenario mappings at once:
- Select word
- `Ctrl+Shift+L` (select all occurrences)
- Type to edit all at once

---

## Project Structure in VS Code

```
illuminator-billing/
├── .vscode/
│   ├── settings.json      ← Workspace settings (included!)
│   └── launch.json        ← Debug config (included!)
├── streamlit_app.py       ← Open this most often
├── requirements.txt
├── README.md
├── .gitignore
└── DEPLOYMENT_GUIDE.md
```

---

## Common VS Code Tasks

### **Update Code & Deploy**

```bash
# 1. Edit streamlit_app.py in VS Code
# 2. Test locally (optional):
streamlit run streamlit_app.py

# 3. Commit & push (UI or terminal):
git add .
git commit -m "Updated scenario mappings"
git push

# Streamlit Cloud auto-redeploys!
```

### **View Git History**

- Install **GitLens** extension
- Timeline view in sidebar
- Right-click file → "View File History"

### **Compare Files**

- Source Control → click modified file
- See diff side-by-side
- Stage specific lines with "Stage Selected Ranges"

### **Search Everything**

- `Ctrl+Shift+F` - Search in all files
- `Ctrl+P` - Quick open file
- `Ctrl+T` - Search symbols (functions, classes)

---

## Recommended Extensions

Install via `Ctrl+Shift+X`:

### **Essential**
1. **Python** (Microsoft) - Python support
2. **Pylance** (Microsoft) - Fast IntelliSense
3. **GitHub Pull Requests** - Better Git integration

### **Helpful**
4. **GitLens** (GitKraken) - Git supercharged
5. **Better Comments** - Prettier comment highlighting
6. **Error Lens** - Inline error messages
7. **Path Intellisense** - Autocomplete file paths

### **Optional**
8. **Streamlit Snippets** - Streamlit code snippets
9. **Python Docstring Generator** - Auto-generate docstrings
10. **Rainbow CSV** - Colorize CSV files

---

## Configuration Files Included

### **.vscode/settings.json**
```json
{
  "python.defaultInterpreterPath": "python3",
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

Enables:
- Auto-formatting on save
- Python linting
- Better file exclusion

### **.vscode/launch.json**
```json
{
  "name": "Python: Streamlit",
  "type": "python",
  "request": "launch",
  "module": "streamlit",
  "args": ["run", "${file}"]
}
```

Enables:
- Press `F5` to debug
- Set breakpoints
- Step through code

---

## Troubleshooting

### "Python not found"

1. Install Python 3.11+
2. `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose Python 3.11 or higher

### "Git not found"

1. Install Git: https://git-scm.com
2. Restart VS Code

### "Streamlit not found"

```bash
pip install streamlit
# or if using venv:
source venv/bin/activate
pip install -r requirements.txt
```

### "Port already in use"

```bash
# Kill existing Streamlit process
pkill -f streamlit
# or specify different port:
streamlit run streamlit_app.py --server.port 8502
```

---

## Keyboard Shortcuts Cheat Sheet

| Action | Shortcut |
|--------|----------|
| Command Palette | `Ctrl+Shift+P` |
| Quick Open File | `Ctrl+P` |
| Terminal | `` Ctrl+` `` |
| Search Files | `Ctrl+Shift+F` |
| Git: Commit | `Ctrl+Enter` (in Source Control) |
| Save All | `Ctrl+K S` |
| Format Document | `Shift+Alt+F` |
| Multi-cursor | `Alt+Click` |
| Select All Occurrences | `Ctrl+Shift+L` |
| Debug | `F5` |
| Toggle Breakpoint | `F9` |
| Go to Definition | `F12` |
| Find References | `Shift+F12` |

---

## Tips for Customizing the App

### **Update Scenario Mappings**

Line ~170 in `streamlit_app.py`:
```python
scenario_mappings = {
    'Admiral Park - North 50 lux': 'Admiral Park - Field 1',
    'Admiral Park - North 100 lux': 'Admiral Park - Field 1',
    # Add your facilities here:
    'Seacrest Park - East 50 lux': 'Seacrest Park - Field 1',
}
```

**Pro tip:** Use multi-cursor to add multiple mappings fast!

### **Update Composite Rules**

Line ~180:
```python
composite_rules = {
    'Admiral Park - North 100 lux': {
        'includes': ['Admiral Park - North 50 lux'],
        'power_kw': 2
    },
    # Add more rules
}
```

### **Change Default Rate**

Line ~122:
```python
rate_per_kwh = st.number_input(
    "Rate per kWh ($)",
    value=1.0,  # Change this default
)
```

---

## Going Production

### **Before Deploying:**

1. ✅ Update all scenario mappings
2. ✅ Define composite rules for all facilities
3. ✅ Set correct default billing rate
4. ✅ Test with real data locally
5. ✅ Add password protection (optional)

### **After Deploying:**

1. ✅ Test on live URL
2. ✅ Share with CoJ team
3. ✅ Monitor Streamlit Cloud logs
4. ✅ Gather feedback
5. ✅ Iterate based on usage

---

## Resources

- **VS Code Docs:** https://code.visualstudio.com/docs
- **Streamlit Docs:** https://docs.streamlit.io
- **GitHub Docs:** https://docs.github.com
- **Python Docs:** https://docs.python.org

---

## Need Help?

1. Check the main DEPLOYMENT_GUIDE.md
2. Streamlit Community: https://discuss.streamlit.io
3. VS Code issues: https://github.com/microsoft/vscode/issues
4. Email: support@halytech.com.au

---

**Happy coding in VS Code! 🚀**