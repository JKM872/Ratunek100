"""
Szybki test volleyball - tylko pierwsze 5 meczów
"""
import subprocess
import sys

print("🧪 Szybki test volleyball - 5 pierwszych meczów")
print("="*70)

# Uruchom scraper z limitowaną liczbą wydarzeń
cmd = [
    sys.executable,
    "scrape_and_notify.py",
    "--date", "2025-10-06",
    "--sports", "volleyball",
    "--headless",
    "--skip-no-odds",
    "--only-form-advantage",
    "--max-events", "5"  # Tylko 5 meczów
]

print(f"Komenda: {' '.join(cmd)}\n")

result = subprocess.run(cmd, capture_output=False, text=True)

print("\n" + "="*70)
if result.returncode == 0:
    print("✅ Test zakończony sukcesem!")
else:
    print(f"⚠️ Test zakończony z kodem: {result.returncode}")
