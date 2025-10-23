# 📧 Email o 11:00 - Instrukcja krok po kroku

## 🎯 CEL: Dostawać email z WSZYSTKIMI sportami dokładnie o 11:00

---

## 📋 KROK PO KROKU:

### **Krok 1: Otwórz Task Scheduler**

1. Naciśnij **Win + R**
2. Wpisz: `taskschd.msc`
3. Naciśnij **Enter**

---

### **Krok 2: Utwórz zadanie**

1. Kliknij **"Utwórz zadanie podstawowe..."** (prawy panel)
2. **Nazwa:** `Flashscore - Email o 11:00`
3. **Opis:** `Scraping wszystkich sportów, email około 11:00`
4. Kliknij **Dalej**

---

### **Krok 3: Ustaw trigger (WAŻNE!)**

1. Wybierz: **"Codziennie"**
2. Kliknij **Dalej**
3. **Data rozpoczęcia:** Dzisiaj
4. **Godzina:** `07:00:00` ⬅️ **UWAGA: 7 rano, nie 11!**
5. **Co ile dni:** `1`
6. Kliknij **Dalej**

**💡 Dlaczego 7:00?**
- Scraping zajmuje ~4 godziny
- 7:00 + 4h = 11:00 → Dokładnie wtedy dostaniesz email!

---

### **Krok 4: Ustaw akcję**

1. Wybierz: **"Uruchom program"**
2. Kliknij **Dalej**
3. **Program/skrypt:**
   ```
   C:\Users\jakub\Downloads\Flashscore2\daily_scraper_all_sports_for_11am.bat
   ```
4. **Katalog roboczy:**
   ```
   C:\Users\jakub\Downloads\Flashscore2
   ```
5. Kliknij **Dalej**

---

### **Krok 5: Zakończ**

1. Przejrzyj ustawienia
2. ✅ Zaznacz: **"Otwórz okno Właściwości po kliknięciu Zakończ"**
3. Kliknij **Zakończ**

---

### **Krok 6: Zaawansowane ustawienia (KRYTYCZNE!)**

W oknie właściwości:

#### **Zakładka "Ogólne":**
- ✅ Zaznacz: **"Uruchom z najwyższymi uprawnieniami"**

#### **Zakładka "Warunki":**
- ❌ **ODZNACZ:** "Uruchom zadanie tylko wtedy, gdy komputer jest zasilany z sieci"
- ❌ **ODZNACZ:** "Zatrzymaj, jeśli komputer przełączy się na zasilanie bateryjne"
- ❌ **ODZNACZ:** "Zatrzymaj, jeśli komputer przestanie być bezczynny"

💡 **Dlaczego to ważne?**
Scraping trwa 4 godziny - nie chcesz żeby laptop zasnął w trakcie!

#### **Zakładka "Ustawienia":**
- ✅ Zaznacz: **"Zezwalaj na ręczne uruchomienie zadania"**
- ✅ Zaznacz: **"Uruchom zadanie tak szybko, jak to możliwe po pominięciu zaplanowanego uruchomienia"**
- **Jeśli zadanie działa dłużej niż:** → Ustaw `6 godzin` (dla bezpieczeństwa)

#### **Kliknij OK**

---

### **Krok 7: TEST! 🧪**

Nie czekaj do jutra - przetestuj TERAZ!

1. W Task Scheduler znajdź: `Flashscore - Email o 11:00`
2. Kliknij **prawym przyciskiem myszy**
3. Wybierz **"Uruchom"**

Pojawi się czarne okno (konsola) pokazujące postęp:
```
[1/1200] Przetwarzam...
[2/1200] Przetwarzam...
...
🔄 AUTO-RESTART: Restartowanie przeglądarki po 200 meczach...
...
```

**⏱️ To potrwa 2-4 godziny!** Możesz minimalizować okno i robić swoje sprawy.

**Sprawdź:**
- ✅ Czy scraping się rozpoczął?
- ✅ Czy komputer nie zasnął?
- ✅ Czy po zakończeniu dostałeś email?

---

## 📊 **CO BĘDZIE DZIAŁO SIĘ KAŻDEGO DNIA:**

```
🌅 07:00 - Komputer włączony, Task Scheduler uruchamia scraper
      ↓
🔄 07:00-11:00 - Scraping w tle (możesz korzystać z komputera!)
      - Football (~600 meczów)
      - Basketball (~300 meczów)
      - Tennis (~250 meczów)
      - Hockey (~150 meczów)
      - Volleyball (~100 meczów)
      - Handball (~50 meczów)
      ↓
📧 ~11:00 - EMAIL! Lista wszystkich kwalifikujących się meczów
      ↓
✅ Gotowe! Dane zapisane w outputs/
```

---

## ⚠️ **WAŻNE WYMAGANIA:**

### **1. Komputer musi być włączony o 7:00!**

Jeśli komputer jest wyłączony:
- ✅ Task Scheduler uruchomi scraper gdy komputer się włączy (jeśli zaznaczyłeś opcję)
- ⏰ Email przyjdzie 4h po włączeniu komputera

### **2. Komputer nie może zasnąć w trakcie!**

**Ustaw opcje zasilania:**
1. Panel Sterowania → Opcje zasilania
2. Edytuj plan zasilania
3. **Uśpij komputer po:** Ustaw na `Nigdy` lub `5 godzin`

### **3. Internet musi działać!**

Scraper potrzebuje internetu aby:
- Pobrać dane z Livesport.com
- Wysłać email przez Gmail

---

## 🎛️ **ALTERNATYWNE OPCJE:**

### **Opcja 1: Jeśli komputer śpi w nocy**

Uruchom scraper wieczorem poprzedniego dnia:
- **Trigger:** Codziennie o **23:00** (11 PM)
- Email przychodzi o **3:00 w nocy**
- Rano czytasz email z meczami na dzisiaj!

### **Opcja 2: Jeśli chcesz email wcześniej (8:00)**

- **Trigger:** Codziennie o **04:00** (4 rano)
- Email przychodzi o **8:00**

### **Opcja 3: Jeśli chcesz email później (13:00)**

- **Trigger:** Codziennie o **09:00** (9 rano)
- Email przychodzi o **13:00**

**💡 Wzór:** Godzina trigera + 4h = Godzina emaila

---

## 📧 **PRZYKŁADOWY EMAIL (co dostaniesz):**

```
Od: jakub.majka.zg@gmail.com
Do: jakub.majka.zg@gmail.com
Temat: 🏆 50 kwalifikujących się meczów na 2025-10-05

🏆 Kwalifikujące się mecze na dzień: 2025-10-05

═════════════════════════════════

⚽ PIŁKA NOŻNA (15 meczów)

🕐 12:00  Real Madrid vs Barcelona
   📊 H2H: 5/5 wygranych gospodarzy

🕐 15:00  Manchester United vs Liverpool
   📊 H2H: 4/5 wygranych gospodarzy

... (więcej meczów)

═════════════════════════════════

🏀 KOSZYKÓWKA (8 meczów)

🕐 18:00  Lakers vs Warriors
   📊 H2H: 3/5 wygranych gospodarzy

... (więcej meczów)

═════════════════════════════════

🎾 TENIS (12 meczów)
🏒 HOKEJ (5 meczów)
🏐 SIATKÓWKA (6 meczów)
🤾 PIŁKA RĘCZNA (4 meczów)

═════════════════════════════════

📊 Łącznie: 50 kwalifikujących się meczów
📅 Data: 2025-10-05
```

---

## 🔧 **ROZWIĄZYWANIE PROBLEMÓW:**

### **Problem: Email nie przychodzi o 11:00, tylko później**

**Przyczyna:** Scraping zajął więcej niż 4 godziny

**Rozwiązanie:** Przesuń trigger wcześniej (np. na 6:00 zamiast 7:00)

---

### **Problem: Komputer zasnął w trakcie scrapingu**

**Przyczyna:** Opcje zasilania

**Rozwiązanie:**
1. Panel Sterowania → Opcje zasilania
2. **Uśpij komputer po:** `Nigdy`
3. **Wyłącz dysk twardy po:** `Nigdy`

Lub użyj **PowerShell command** w Task Scheduler:
```powershell
powercfg /change standby-timeout-ac 0
```

---

### **Problem: Zadanie nie uruchomiło się o 7:00**

**Przyczyna:** Komputer był wyłączony

**Rozwiązanie:**
1. Task Scheduler → Właściwości zadania
2. Zakładka "Ustawienia"
3. ✅ Zaznacz: "Uruchom zadanie tak szybko, jak to możliwe po pominięciu zaplanowanego uruchomienia"

Teraz scraper uruchomi się gdy włączysz komputer!

---

### **Problem: Chcę przerwać scraping w trakcie**

**Rozwiązanie:**
1. Znajdź czarne okno (konsola)
2. Naciśnij **Ctrl + C**
3. Lub zamknij okno (X)

Dane które już zebrał są bezpieczne w pamięci!

---

## 📱 **MONITOROWANIE:**

### **Sprawdź czy działa:**

**1. Log file:**
```
C:\Users\jakub\Downloads\Flashscore2\scraper_log.txt
```

Zawiera:
```
2025-10-05 11:03:15 - All sports scraping completed
2025-10-06 11:01:22 - All sports scraping completed
2025-10-07 11:04:18 - All sports scraping completed
```

**2. Pliki CSV:**
```
C:\Users\jakub\Downloads\Flashscore2\outputs\
```

Każdego dnia nowy plik:
- `livesport_h2h_2025-10-05_football_basketball_tennis_hockey_volleyball_handball_EMAIL.csv`

**3. Historia w Task Scheduler:**
1. Task Scheduler → Twoje zadanie
2. Zakładka "Historia"
3. Zobacz wszystkie uruchomienia

---

## ✅ **CHECKLIST:**

Przed pierwszym uruchomieniem sprawdź:

- [ ] Zadanie utworzone w Task Scheduler
- [ ] Trigger ustawiony na 07:00 (codziennie)
- [ ] Akcja wskazuje na `daily_scraper_all_sports_for_11am.bat`
- [ ] "Uruchom z najwyższymi uprawnieniami" ✅
- [ ] Opcje zasilania wyłączone (komputer nie zaśnie)
- [ ] Test ręczny zakończony sukcesem
- [ ] Email otrzymany poprawnie
- [ ] Komputer będzie włączony o 7:00

---

## 🎉 **GOTOWE!**

**Od jutra (i każdego dnia):**
- 🕐 7:00 - Scraper startuje automatycznie
- ⏳ 4 godziny scrapowania w tle
- 📧 11:00 - Email w Twojej skrzynce!

**Nie musisz nic robić - wszystko jest automatyczne!** 🚀

Powodzenia! 🎯

