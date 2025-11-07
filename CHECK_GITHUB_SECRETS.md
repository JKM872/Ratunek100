# ✅ SPRAWDŹ GITHUB SECRETS

## Gdzie sprawdzić:
https://github.com/JKM872/Ratunek100/settings/secrets/actions

## Wymagane secrets:

### 1. APP_URL
```
https://livesport-scraper-ui-0393f6f2096e.herokuapp.com
```

### 2. APP_API_KEY
```
super-secret-key-12345
```

### 3. EMAIL_USERNAME
```
(Twój email)
```

### 4. EMAIL_PASSWORD
```
(Hasło do email)
```

## ⚠️ WAŻNE:
`APP_API_KEY` w GitHub **MUSI BYĆ IDENTYCZNY** z `SCRAPER_API_KEY` na Heroku!

Heroku ma: `super-secret-key-12345`
GitHub też musi mieć: `super-secret-key-12345`

## Jak sprawdzić:
1. Idź do https://github.com/JKM872/Ratunek100/settings/secrets/actions
2. Kliknij "Update" przy APP_API_KEY
3. Sprawdź czy wartość to: `super-secret-key-12345`
4. Jeśli nie - zmień na prawidłową
