# Evidence Ledger — Registre des Preuves Réelles

Chaque statut `VERIFIED` doit impérativement provenir d'une entrée de ce registre avec commande, horodatage et sortie exacte.

| Horodatage (UTC) | Critère DoD | Commande Exécutée | Sortie Vérifiée | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| 2026-10-14 09:22 | Intégrité Projet | `bash scripts/verify.sh` | `OVERALL RESULT: ALL CHECKS PASSED` | VERIFIED |
| 2026-10-14 09:33 | Connectivité AWS Bedrock | `uv run python probe_bedrock.py` | `Statut: SUCCÈS, Latence: 1548.6ms, Coût: 0.0000080$` | VERIFIED |
