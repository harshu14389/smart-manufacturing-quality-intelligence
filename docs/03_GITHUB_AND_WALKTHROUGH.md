# GitHub and portfolio walkthrough

Do this after running locally and adding real SAP evidence.
1. Sign in at github.com. Click + → New repository.
2. Name it `smart-manufacturing-quality-intelligence`. Select Public only if you want the synthetic project publicly visible. Do not initialise README (this folder already has one).
3. In VS Code open Terminal → Git Bash. Run one command per line:
```bash
git init
git add .
git commit -m "Build synthetic paint shop quality intelligence platform"
git branch -M main
git remote add origin https://github.com/chdt2004/smart-manufacturing-quality-intelligence.git
git push -u origin main
```
Authenticate through the normal browser flow if requested. Never paste passwords/tokens into chat. If remote already exists, run `git remote -v` and verify it before changing anything. If Git asks for identity, configure your own GitHub name and verified/noreply email.

Walkthrough (3–5 minutes): explain synthetic scope → show local validation summary → show train/validation/test metrics and baseline → show Datasphere facts/dimensions → show SAC quality and downtime → investigate a held-out risk example and explain a false positive → state limitations. Update README with real evidence links after you build SAP.
