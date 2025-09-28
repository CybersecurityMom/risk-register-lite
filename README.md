
cat > README.md <<'MD'
# 📊 Mini Risk Register (GRC)

Tiny Python CLI to log risks, score them (Likelihood × Impact), list, export, and show stats. Zero dependencies; JSON store.

## Run
```bash
python3 risk_register.py add "S3 bucket public access" --likelihood 4 --impact 4 --category cloud --owner "SecOps"
python3 risk_register.py add "Vendor lacks SOC 2" --likelihood 3 --impact 5 --category vendor --owner "GRC"
python3 risk_register.py list
python3 risk_register.py stats
python3 risk_register.py update <ID_FROM_LIST> --status mitigating --notes "Applied bucket policy"
python3 risk_register.py export --output risks_2025Q4.csv
Levels: Low (≤5), Moderate (≤10), High (≤15), Critical (>15)
