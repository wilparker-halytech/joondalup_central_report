# ✅ Configuration Now Externalized!

## What Changed

### Before (Hardcoded):
```python
# In streamlit_app.py - line 170
scenario_mappings = {
    'Admiral Park - North 50 lux': 'Admiral Park',
    # ... hardcoded in code
}
```
**Problem:** Needed to edit Python code to add facilities ❌

### After (External Config):
```yaml
# In config.yaml - easy to edit!
scenario_mappings:
  "Admiral Park - North 50 lux": "Admiral Park"
  "Admiral Park - North 100 lux": "Admiral Park"
  # Add more here - no code changes!
```
**Solution:** Edit simple YAML file, no programming needed! ✅

---

## Benefits

✅ **Non-programmers can edit** - It's just a text file  
✅ **No code changes** - Add facilities without touching Python  
✅ **Easy to understand** - Clear, readable format  
✅ **Version controlled** - Track changes in git  
✅ **Less error-prone** - Can't break Python syntax  
✅ **Self-documenting** - Comments explain everything  

---

## Files You Need

### Essential (3 files):
1. **config.yaml** ⭐ - All your facility mappings
2. **streamlit_app.py** ⭐ - Updated to read config
3. **requirements.txt** ⭐ - Updated (added pyyaml)

### Documentation (2 files):
4. **CONFIG_GUIDE.md** ⭐ - Complete editing guide
5. **LIGHTING_MAPPING_GUIDE.md** - Facility structure explanation

### Setup (same as before):
6. setup.sh / setup.bat
7. .gitignore
8. .vscode/ configs

---

## Quick Start

### 1. Download Files
Get these 3 essential files:
- [config.yaml](config.yaml)
- [streamlit_app.py](streamlit_app.py)
- [requirements.txt](requirements.txt)

### 2. Set Up Project
```bash
cd ~/illuminator_central_billing_poc

# Place files in folder, then:
./setup.sh  # or setup.bat on Windows

# Or manually:
source venv/bin/activate
pip install -r requirements.txt  # Installs pyyaml
```

### 3. Edit config.yaml
```bash
# Open in VS Code (recommended)
code config.yaml

# Or any text editor
nano config.yaml
```

### 4. Add Your Facilities
Copy the Admiral Park pattern:
```yaml
  # Your facility
  "Seacrest Park - North 50 lux": "Seacrest Park"
  "Seacrest Park - North 100 lux": "Seacrest Park"
  # ... etc
```

### 5. Test
```bash
streamlit run streamlit_app.py
```

Check sidebar shows: ✅ config.yaml loaded

---

## Example: Adding Seacrest Park

### Step 1: Open config.yaml

Find the `scenario_mappings:` section

### Step 2: Add mappings

```yaml
scenario_mappings:
  # Admiral Park (already there)
  "Admiral Park - North 50 lux": "Admiral Park"
  "Admiral Park - North 100 lux": "Admiral Park"
  "Admiral Park - South 50 lux": "Admiral Park"
  "Admiral Park - South 100 lux": "Admiral Park"
  
  # Seacrest Park (ADD THIS)
  "Seacrest Park - North 50 lux": "Seacrest Park"
  "Seacrest Park - North 100 lux": "Seacrest Park"
  "Seacrest Park - South 50 lux": "Seacrest Park"
  "Seacrest Park - South 100 lux": "Seacrest Park"
```

### Step 3: Add composite rules

```yaml
composite_rules:
  # Admiral Park (already there)
  "Admiral Park - North 100 lux":
    includes:
      - "Admiral Park - North 50 lux"
    power_kw: 2.0
  
  "Admiral Park - South 100 lux":
    includes:
      - "Admiral Park - South 50 lux"
    power_kw: 2.0
  
  # Seacrest Park (ADD THIS)
  "Seacrest Park - North 100 lux":
    includes:
      - "Seacrest Park - North 50 lux"
    power_kw: 2.0
  
  "Seacrest Park - South 100 lux":
    includes:
      - "Seacrest Park - South 50 lux"
    power_kw: 2.0
```

### Step 4: Save and test

1. Save config.yaml
2. Refresh Streamlit (press 'R' in browser)
3. Sidebar shows updated count: "Mappings: 8 scenarios"
4. Test with data!

**That's it! No code changes needed!** ✅

---

## Config File Structure

```yaml
# config.yaml
├── billing:                    # Electricity rates
│   ├── rate_per_kwh
│   └── default_rate
│
├── scenario_mappings:          # Your facilities (MAIN SECTION)
│   ├── "Facility - Zone Lux": "Bookable Area"
│   └── ... (add all your facilities)
│
├── composite_rules:            # Prevent double-charging
│   ├── "High Level Scenario":
│   │   ├── includes: [low level scenarios]
│   │   └── power_kw: X.X
│   └── ... (one per high-level scenario)
│
├── power_ratings:              # Optional individual ratings
│
├── facilities:                 # Optional metadata (for docs)
│
└── validation:                 # Optional validation rules
```

---

## What the App Shows

### Sidebar:
```
⚙️ Configuration
Rate per kWh ($): 1.00

📋 Configuration
✅ config.yaml loaded

Mappings: 4 scenarios
Rules: 2 composite rules

📄 View Config
(expandable - shows full config)
```

### If config missing:
```
❌ Configuration file not found!

Please create a config.yaml file...
```

### If config has errors:
```
❌ Error reading configuration file!

The config.yaml file has a syntax error:
[detailed error message]
```

---

## YAML Syntax Cheat Sheet

### Strings
```yaml
simple: value
"with spaces": "needs quotes"
"with-dashes": "needs quotes"
```

### Lists
```yaml
items:
  - "Item 1"
  - "Item 2"
  - "Item 3"
```

### Nested
```yaml
parent:
  child:
    grandchild: value
```

### Comments
```yaml
# This is a comment
key: value  # Inline comment
```

### Important Rules
- ✅ Use 2 spaces for indentation
- ✅ Never use tabs
- ✅ Be consistent with spacing
- ✅ Quotes for strings with special chars
- ✅ Dash + space for list items

---

## Validation

### Online Validator
http://www.yamllint.com/

Copy/paste your config to check syntax

### Command Line
```bash
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

No error = valid YAML ✅

### In VS Code
Install: **YAML** extension by Red Hat
- Real-time syntax checking
- Auto-formatting
- Error highlighting

---

## Deployment

### Local Development
1. Edit config.yaml
2. Save
3. Streamlit auto-reloads
4. Changes live immediately ✅

### Streamlit Cloud
1. Edit config.yaml locally
2. Test: `streamlit run streamlit_app.py`
3. Commit: `git add config.yaml && git commit -m "Added facilities"`
4. Push: `git push`
5. Streamlit Cloud redeploys (1-2 min)
6. Config now live in production ✅

---

## Common Tasks

### Add New Facility
1. Open config.yaml
2. Copy Admiral Park pattern
3. Replace facility name
4. Save
5. Done! ✅

### Update Electricity Rate
1. Open config.yaml
2. Change `rate_per_kwh: 1.00` to actual rate
3. Save
4. Done! ✅

### Change Bookable Area Name
1. Open config.yaml
2. Find scenario mapping
3. Change right side: `"Scenario": "New Area Name"`
4. Save
5. Done! ✅

### View Current Config
1. Open Streamlit app
2. Sidebar → Expand "📄 View Config"
3. See entire loaded configuration

---

## Troubleshooting

### "config.yaml not found"
- Check file is in same folder as streamlit_app.py
- Check filename is exactly `config.yaml` (not .yml)

### "YAML syntax error"
- Use yamllint.com to validate
- Check indentation (2 spaces, no tabs)
- Check quotes around strings with spaces/dashes

### "Scenario not mapping"
- Check spelling matches EXACTLY (case-sensitive)
- Check quotes are present
- Compare with Admiral Park working example

### "Changes not appearing"
- Save the file
- Refresh Streamlit (press 'R')
- Check sidebar for config reload
- If needed, restart Streamlit

---

## Documentation

**Complete editing guide:** [CONFIG_GUIDE.md](CONFIG_GUIDE.md)

Topics covered:
- YAML syntax rules
- Common patterns
- Adding facilities
- Error messages
- Testing changes
- Version control
- Deployment
- Troubleshooting

---

## Summary

**Before:** Edit Python code (scary for non-programmers) ❌  
**After:** Edit simple config file (anyone can do it!) ✅

**Configuration is now:**
- ✅ External (config.yaml)
- ✅ Easy to understand
- ✅ Easy to modify
- ✅ Self-documenting
- ✅ Version controlled
- ✅ No coding required

**Perfect for City of Joondalup staff to maintain!** 🎯
