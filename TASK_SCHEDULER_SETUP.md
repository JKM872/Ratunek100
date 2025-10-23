# 📅 INSTRUKCJA: Windows Task Scheduler

## 🎯 Automatyczne uruchamianie scrapera codziennie

Dzięki Windows Task Scheduler możesz ustawić automatyczne uruchamianie scrapera **codziennie o określonej godzinie** (np. o 9:00 rano).

---

## 📋 **KROK PO KROKU**

### **Krok 1: Wybierz wersję scrapera**

Masz 3 wersje do wyboru:

| Plik | Sporty | Czas wykonania | Kiedy używać |
|------|--------|----------------|--------------|
| `daily_scraper_football_only.bat` | ⚽ Tylko piłka nożna | 15-30 min | **POLECANE** - najszybsze, najwięcej meczów |
| `daily_scraper_weekend.bat` | ⚽🏀🎾 Football + Basketball + Tennis | 45-90 min | Weekendy, gdy jest więcej czasu |
| `daily_scraper_all_sports.bat` | ⚽🏀🎾🏒🏐🤾 WSZYSTKIE sporty | 2-4 godziny | Gdy chcesz pełny obraz |

**💡 Rekomendacja:** Zacznij od `daily_scraper_football_only.bat` - to najszybsza i najskuteczniejsza opcja!

---

### **Krok 2: Otwórz Task Scheduler**

1. Naciśnij **Win + R**
2. Wpisz: `taskschd.msc`
3. Naciśnij **Enter**

Alternatywnie:
- Wyszukaj w menu Start: "Harmonogram zadań" lub "Task Scheduler"

---

### **Krok 3: Utwórz nowe zadanie**

1. W prawym panelu kliknij **"Utwórz zadanie podstawowe..."** (lub "Create Basic Task...")

2. **Nazwa:** `Flashscore Daily Scraper`
3. **Opis:** `Automatyczne scrapowanie meczów i wysyłanie emaili`
4. Kliknij **Dalej**

---

### **Krok 4: Ustaw wyzwalacz (Trigger)**

1. Wybierz: **"Codziennie"** (Daily)
2. Kliknij **Dalej**

3. **Data rozpoczęcia:** Dzisiaj (lub kiedy chcesz zacząć)
4. **Godzina:** `09:00:00` (lub inna godzina - **WAŻNE:** wybierz taką porę, gdy komputer będzie włączony!)
5. **Co ile dni:** `1` (codziennie)
6. Kliknij **Dalej**

**💡 Porady:**
- **Rano (8-10):** Dostajesz analizę przed południem
- **Wieczór (18-20):** Analiza przed wieczornymi meczami
- **Noc (23-01):** Jeśli chcesz mieć raport na rano (dla pełnego scrapingu 2-4h)

---

### **Krok 5: Ustaw akcję**

1. Wybierz: **"Uruchom program"** (Start a program)
2. Kliknij **Dalej**

3. **Program/skrypt:**
   ```
   C:\Users\jakub\Downloads\Flashscore2\daily_scraper_football_only.bat
   ```
   
   Lub użyj przycisku **Przeglądaj** i wybierz plik `.bat`

4. **Katalog roboczy (opcjonalne, ale zalecane):**
   ```
   C:\Users\jakub\Downloads\Flashscore2
   ```

5. Kliknij **Dalej**

---

### **Krok 6: Sprawdź i zakończ**

1. Przejrzyj ustawienia
2. ✅ Zaznacz: **"Otwórz okno Właściwości po kliknięciu Zakończ"**
3. Kliknij **Zakończ**

---

### **Krok 7: Zaawansowane ustawienia (WAŻNE!)**

W oknie właściwości, które się otworzyło:

#### **Zakładka "Ogólne" (General):**
- ✅ Zaznacz: **"Uruchom z najwyższymi uprawnieniami"** (Run with highest privileges)
- ✅ Ustaw: **"Skonfiguruj dla: Windows 10"**

#### **Zakładka "Warunki" (Conditions):**
- ❌ **ODZNACZ:** "Uruchom zadanie tylko wtedy, gdy komputer jest zasilany z sieci"
  - *Dzięki temu zadanie uruchomi się nawet na laptopie na baterii*
- ❌ **ODZNACZ:** "Zatrzymaj, jeśli komputer przełączy się na zasilanie bateryjne"
  - *Dzięki temu scraping nie zostanie przerwany*

#### **Zakładka "Ustawienia" (Settings):**
- ✅ Zaznacz: **"Zezwalaj na ręczne uruchomienie zadania"** (Allow task to be run on demand)
- ✅ Zaznacz: **"Uruchom zadanie tak szybko, jak to możliwe po pominięciu zaplanowanego uruchomienia"**
- ✅ Zaznacz: **"Jeśli zadanie zakończy się niepowodzeniem, uruchom ponownie co:"** → Ustaw `10 minut`, `Liczba prób: 2`
- **Jeśli zadanie działa dłużej niż:** → Ustaw `5 godzin` (dla pełnego scrapingu)

#### **Kliknij OK** aby zapisać

---

### **Krok 8: Testuj! 🧪**

Nie czekaj do jutra - **przetestuj TERAZ!**

1. W Task Scheduler znajdź swoje zadanie
2. Kliknij prawym przyciskiem
3. Wybierz **"Uruchom"** (Run)

Pojawi się okno konsoli (czarne okno) pokazujące postęp.

**✅ Sprawdź:**
- Czy scraping się rozpoczął?
- Czy po zakończeniu otrzymałeś email?
- Czy nie było błędów?

---

## 🔧 **ROZWIĄZYWANIE PROBLEMÓW**

### **Problem 1: Zadanie się nie uruchamia**

**Przyczyna:** Komputer jest wyłączony o godzinie uruchomienia

**Rozwiązanie:**
- W Task Scheduler → Właściwości zadania → Zakładka "Ustawienia"
- ✅ Zaznacz: "Uruchom zadanie tak szybko, jak to możliwe po pominięciu zaplanowanego uruchomienia"

To uruchomi scraper zaraz po włączeniu komputera!

---

### **Problem 2: Okno konsoli znika natychmiast**

**Przyczyna:** Błąd w ścieżce lub uprawnieniach

**Rozwiązanie:**
1. Otwórz `daily_scraper_football_only.bat` w Notatniku
2. Dodaj na końcu pliku:
   ```batch
   pause
   ```
3. Zapisz i uruchom ponownie
4. Teraz zobaczysz komunikat błędu (jeśli jest)

---

### **Problem 3: "Python not found"**

**Przyczyna:** Python nie jest w PATH dla Task Scheduler

**Rozwiązanie 1 (ŁATWE):**
Zmień w pliku `.bat` linię:
```batch
python scrape_and_notify.py ^
```
Na pełną ścieżkę do Pythona:
```batch
C:\Users\jakub\AppData\Local\Programs\Python\Python39\python.exe scrape_and_notify.py ^
```

**Rozwiązanie 2:**
W Task Scheduler → Właściwości → Zakładka "Akcje" → Edytuj akcję
- **Katalog roboczy:** `C:\Users\jakub\Downloads\Flashscore2`

---

### **Problem 4: Email się nie wysyła**

**Sprawdź:**
1. Czy masz poprawne hasło App Password w pliku `.bat`?
2. Czy masz internet o godzinie uruchomienia?
3. Sprawdź log: `scraper_log.txt` w katalogu projektu

---

### **Problem 5: Komputer zasypia podczas scrapingu**

**Rozwiązanie:**
1. Panel Sterowania → Opcje zasilania
2. Edytuj plan zasilania
3. **Uśpij komputer po:** Ustaw na `Nigdy` lub dłuższy czas (np. 4 godziny)

Alternatywnie użyj `daily_scraper_football_only.bat` (szybszy, 15-30 min)

---

## 📊 **MONITOROWANIE**

### **Sprawdzanie historii**

1. W Task Scheduler kliknij prawym na zadanie
2. Wybierz **"Historia"** (History)
3. Zobacz wszystkie uruchomienia, błędy, kody wyjścia

### **Log z uruchomień**

Sprawdź plik `scraper_log.txt` w katalogu projektu:
```
2025-10-05 09:00:15 - Football scraping completed
2025-10-06 09:00:22 - Football scraping completed
2025-10-07 09:00:18 - Football scraping completed
```

---

## 🎛️ **ZAAWANSOWANE OPCJE**

### **Różne dni tygodnia → Różne sporty**

Możesz stworzyć kilka zadań:

| Zadanie | Dni | Sporty | Czas |
|---------|-----|--------|------|
| `Flashscore Weekday` | Pon-Pt | ⚽ Football | 9:00 |
| `Flashscore Weekend` | Sob-Nie | ⚽🏀🎾 Football+Basketball+Tennis | 8:00 |
| `Flashscore Full` | Niedziela | 🌟 WSZYSTKIE | 2:00 (w nocy) |

**Jak to zrobić:**
1. Utwórz 3 oddzielne zadania
2. Każde z innym plikiem `.bat`
3. W kroku "Trigger" ustaw różne dni tygodnia

---

### **Uruchamianie przy starcie systemu**

Jeśli chcesz uruchomić scraper **zawsze przy włączeniu komputera** (zamiast o określonej godzinie):

1. Przy tworzeniu zadania wybierz trigger: **"Przy uruchamianiu komputera"**
2. Dodaj opóźnienie: `10 minut` (aby system się w pełni załadował)

---

### **Wysyłanie do wielu osób**

Edytuj plik `.bat` i zmień linię `--to`:
```batch
--to jakub.majka.zg@gmail.com,kolega@gmail.com,przyjaciel@gmail.com ^
```

Albo utwórz kopię zadania dla każdego odbiorcy!

---

### **Różne godziny sortowania**

Możesz zmieniać sposób sortowania w emailu:

**Sortowanie po godzinie (domyślnie):**
```batch
--sort time
```

**Sortowanie po liczbie wygranych:**
```batch
--sort wins
```

**Sortowanie alfabetyczne:**
```batch
--sort team
```

---

## ✅ **CHECKLIST: Czy wszystko działa?**

Po skonfigurowaniu sprawdź:

- [ ] Zadanie jest widoczne w Task Scheduler
- [ ] Test ręczny (Run) działa poprawnie
- [ ] Otrzymujesz email po zakończeniu
- [ ] Log `scraper_log.txt` zapisuje wpisy
- [ ] CSV jest zapisywany w folderze `outputs/`
- [ ] Ustawienia zasilania nie przerywają zadania
- [ ] Komputer będzie włączony o godzinie uruchomienia

---

## 🎉 **GOTOWE!**

Teraz **każdego dnia automatycznie** otrzymasz email z kwalifikującymi się meczami! 📧⚽

**Przykład:** Ustawiłeś na 9:00 → codziennie o 9:00 scraper analizuje mecze → o 9:30 masz email w skrzynce!

---

## 📧 **PYTANIA?**

- Nie działa? Sprawdź sekcję "Rozwiązywanie problemów"
- Chcesz zmienić godzinę? Edytuj zadanie w Task Scheduler
- Chcesz zmienić sporty? Edytuj plik `.bat`
- Chcesz dodać więcej funkcji? Daj znać!

**Powodzenia! 🚀**

