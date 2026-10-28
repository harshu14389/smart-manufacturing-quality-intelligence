# Start here — Windows beginner instructions

## 1. Extract the ZIP
1. Download the ZIP. Press Windows + E to open File Explorer.
2. Click Downloads. Right-click the ZIP → Extract All → Extract.
3. Open the extracted folder until you can see README.md, requirements.txt and src together. Do not run inside the ZIP preview.

## 2. Open in VS Code
1. Open Visual Studio Code.
2. Press Ctrl + K, release both keys, then press Ctrl + O.
3. Select the folder containing requirements.txt. Click Select Folder.
4. Trust the folder if prompted (this is the project you downloaded).
5. Click Terminal → New Terminal.
6. In the terminal panel, click the small down arrow next to + → Git Bash. If unavailable use Command Prompt; the .venv Python commands below work in either.

## 3. Check Python
Type this and press Enter:
```bash
py --version
```
Use Python 3.11 or 3.12. If `py` is unavailable try `python --version` and replace `py` in the next command with `python`. If neither works install Python from python.org with “Add Python to PATH” checked, then restart VS Code.

## 4. Create your environment
Copy one line at a time. Click the terminal, paste with Ctrl + Shift + V (or right-click → Paste), then press Enter.
```bash
py -m venv .venv
```
The prompt returns after creation. No success text is normal.
```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```
Wait until the prompt returns without a red error. Then run:
```bash
.venv/Scripts/python.exe src/run_project.py
```
Expected: `SUCCESS: 3,600 batches; ... checks passed.`
Direct environment commands avoid activation and PowerShell execution-policy issues.

## 5. Inspect results
In the left Explorer panel expand outputs. Click RUN_SUMMARY.md. Press Ctrl + Shift + V to preview Markdown. Open model_evaluation.png and model_evaluation.json. Expand data → sap_import to see SAP upload files.

## Common problems
- “requirements.txt not found”: wrong folder. File → Open Folder and select the folder containing it.
- “No module named ...”: rerun the installation using the exact .venv command above.
- Access denied writing CSV: close the CSV in Excel and run again.
- To stop a running command: click terminal and press Ctrl + C.
- Do not paste the `$` prompt symbol or Markdown backticks.

## Next
Finish the local run first. Then follow docs/02_SAP_BUILD_GUIDE.md. Ask for help with the exact screen or error; tenant screens vary.
