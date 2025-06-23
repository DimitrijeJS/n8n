#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ausführung einer definierten PS-Skriptreihe + Aufräumarbeiten.
• Erstellt für:  C:\Users\RDP9\Documents\Buntler
• Python ≥3.9, läuft unter Windows (benötigt PowerShell-Konsole)
"""

from pathlib import Path
from datetime import datetime
import subprocess
import shutil
import sys

# ---------------------------------------------------------------------------
# 1) Grund­pfade anlegen
# ---------------------------------------------------------------------------
SCRIPT_PATH = Path(r"C:\Users\RDP9\Documents\Buntler")       # ggf. anpassen
LOG_PATH    = SCRIPT_PATH / "Logs"
LOG_PATH.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 2) Welche PS1-Skripte sollen – in dieser Reihenfolge – laufen?
# ---------------------------------------------------------------------------
SCRIPTS = [
    "download.ps1",
    "Zusammenführen.ps1",
    "MerkmalwerteTausch.ps1",
    "importbase.ps1",
    "importcomponent.ps1",
    "importcustomFields.ps1",
    "importproperties.ps1",
    "importtexte.ps1",
    "importbilder.ps1",
]

# ---------------------------------------------------------------------------
# 3) Hilfs­funktion: PowerShell-Skript ausführen + gleichzeitiges „Tee-Logging“
# ---------------------------------------------------------------------------
def run_powershell(script_file: Path, log_file: Path) -> None:
    """
    Führt ein einzelnes .ps1-Skript aus, schreibt stdout+stderr live sowohl
    auf die Konsole als auch in eine Log-Datei („Tee“-Effekt) und ergänzt zum
    Schluss eine Erfolgs-/Fehlermeldung.
    """
    print(f"Starte {script_file.name} …")
    with log_file.open("w", encoding="utf-8", newline="") as lf:
        try:
            proc = subprocess.Popen(
                [
                    "powershell",
                    "-NoLogo",
                    "-ExecutionPolicy", "Bypass",
                    "-File", str(script_file),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # Zeilenweise durchleiten ↔ mitschreiben
            assert proc.stdout  # nur für den Typ-Checker
            for line in proc.stdout:
                print(line, end="")
                lf.write(line)

            proc.wait()
            if proc.returncode:
                lf.write(f"\nFehler: Skript wurde mit Exitcode {proc.returncode} beendet.")
            else:
                lf.write("\nSkript erfolgreich abgeschlossen.")
        except Exception as exc:  # pylint: disable=broad-except
            err = f"Fehler beim Ausführen von {script_file.name}:\n{exc}"
            print(err, file=sys.stderr)
            lf.write(f"{err}\n")
    print(f"{script_file.name} abgeschlossen.\n")


# ---------------------------------------------------------------------------
# 4) Alle PowerShell-Skripte hintereinander abarbeiten
# ---------------------------------------------------------------------------
for script in SCRIPTS:
    full_path = SCRIPT_PATH / script
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = LOG_PATH / f"Log_{full_path.stem}_{timestamp}.txt"

    if full_path.exists():
        run_powershell(full_path, log_file)
    else:
        msg = f"Fehler: {script} nicht gefunden unter {full_path}"
        print(msg)
        # trotzdem Logdatei anlegen – wie im PS-Original
        log_file.write_text(msg, encoding="utf-8")

print("Alle Skripte wurden verarbeitet.")

# ---------------------------------------------------------------------------
# 5) Aufräumen: bestimmte CSV-Dateien in Unterordner „alt“ verschieben
# ---------------------------------------------------------------------------
ALT_FOLDER = SCRIPT_PATH / "alt"
ALT_FOLDER.mkdir(exist_ok=True)

FILES_TO_MOVE = [
    "Artikelnummern.csv",
    "base-alle.csv",
    "bilder-alle.csv",
    "category-alle.csv",
    "component-alle.csv",
    "customFields-alle.csv",
    "Merkmal.csv",
    "properties-alle.csv",
    "Shortname.csv",
    "texte-alle.csv",
]

for fname in FILES_TO_MOVE:
    src = SCRIPT_PATH / fname
    dst = ALT_FOLDER / fname
    if src.exists():
        try:
            # existierende Zieldatei vorab entfernen, damit shutil.move nicht meckert
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))
            print(f"Datei {fname} wurde nach 'alt' verschoben (überschrieben falls vorhanden).")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Fehler beim Verschieben von {fname}: {exc}", file=sys.stderr)
    else:
        print(f"Hinweis: Datei {fname} wurde nicht gefunden und konnte nicht verschoben werden.")
