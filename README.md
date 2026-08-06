# GAME RPG

Prosta gra RPG przygotowana w Django. Projekt pozwala rozwijać bohatera, kupować i zakładać wyposażenie oraz walczyć z przeciwnikami w systemie turowym.

## Funkcje

- konta użytkowników i logowanie;
- postacie przypisane do właścicieli;
- klasy: Wojownik, Łucznik i Mag;
- rasy posiadające różne bonusy;
- rozwój statystyk wraz z poziomem;
- sklep z kategoriami przedmiotów;
- wyposażenie zależne od klasy i poziomu;
- bonusy do statystyk, maksymalnego HP i many;
- mikstury zdrowia;
- walka turowa;
- umiejętności klasowe zużywające manę;
- doświadczenie, awansowanie i złoto;
- przeciwnicy o różnych poziomach trudności;
- blokowanie zbyt silnych przeciwników;
- symulator balansu walk;
- ochrona dostępu do cudzych postaci i walk;
- automatyczne testy.

## Technologie

- Python 3.12 lub nowszy;
- Django 6.0.6;
- SQLite;
- HTML;
- CSS.

## Pobranie projektu

Sklonuj repozytorium:

```powershell
git clone https://github.com/rawrqwe/GAME_RPG.git
```

Przejdź do folderu projektu:

```powershell
cd GAME_RPG
```

## Środowisko wirtualne

Utwórz środowisko wirtualne:

```powershell
py -3.13 -m venv venv
```

Jeśli korzystasz z Pythona 3.12:

```powershell
py -3.12 -m venv venv
```

Aktywuj środowisko:

```powershell
.\venv\Scripts\Activate.ps1
```

## Instalacja zależności

Zainstaluj pakiety zapisane w `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

## Przygotowanie bazy danych

Wykonaj migracje:

```powershell
python manage.py migrate
```

Wczytaj przedmioty, klasy, rasy i przeciwników:

```powershell
python manage.py load_game_data
```

Komenda ładuje fixture w prawidłowej kolejności.

## Konto administratora

Utwórz konto administratora:

```powershell
python manage.py createsuperuser
```

Podaj nazwę użytkownika, adres e-mail i hasło.

## Uruchomienie projektu

Uruchom serwer:

```powershell
python manage.py runserver
```

Gra będzie dostępna pod adresem:

```text
http://127.0.0.1:8000/game/
```

Panel administratora:

```text
http://127.0.0.1:8000/admin/
```

## Utworzenie postaci

Projekt nie posiada jeszcze osobnego formularza tworzenia postaci. Pierwszą postać można utworzyć w panelu administratora.

1. Zaloguj się pod adresem `/admin/`.
2. Otwórz sekcję postaci.
3. Dodaj nową postać.
4. Wybierz właściciela, nazwę, rasę i klasę.
5. Zapisz postać.
6. Przejdź pod adres `/game/`.

Podstawowe statystyki i broń startowa zostaną przydzielone automatycznie.

## Testy

Uruchom wszystkie testy:

```powershell
python manage.py test game
```

Testy korzystają z tymczasowej bazy danych. Nie zmieniają lokalnych postaci, złota ani wyposażenia.

## Kontrola konfiguracji

Sprawdź konfigurację Django:

```powershell
python manage.py check
```

Sprawdź, czy modele mają wszystkie migracje:

```powershell
python manage.py makemigrations --check
```

Jeśli projekt jest poprawny, zobaczysz:

```text
No changes detected
```

## Symulator walk

Najpierw wyświetl identyfikatory postaci:

```powershell
python manage.py shell -c "from game.models import Character; print(list(Character.objects.values_list('id', 'name', 'level')))"
```

Uruchom symulację dla wybranej postaci:

```powershell
python manage.py simulate_battles ID_POSTACI --attempts 500
```

Przykład dla postaci o ID `1`:

```powershell
python manage.py simulate_battles 1 --attempts 500
```

Możesz ograniczyć symulację do jednego przeciwnika:

```powershell
python manage.py simulate_battles 1 --attempts 500 --enemy-id 1
```

Symulator nie zmienia HP, many, doświadczenia ani złota postaci.

## Dane gry

Podstawowe dane znajdują się w folderze:

```text
game/fixtures/
```

Dostępne fixture:

- `items.json`;
- `class_weapons.json`;
- `armor_sets.json`;
- `resource_items.json`;
- `character_classes.json`;
- `races.json`;
- `enemies.json`.

Wszystkie można wczytać jedną komendą:

```powershell
python manage.py load_game_data
```

## Dane lokalne

Następujące pliki nie są przechowywane w repozytorium:

- `db.sqlite3`;
- środowisko `venv`;
- ustawienia `.idea`;
- pliki `.env`;
- przesłane pliki `media`;
- zebrane pliki `staticfiles`.

Każdy użytkownik tworzy własną lokalną bazę za pomocą migracji i fixture.

## Struktura testów

Testy znajdują się w folderze:

```text
game/tests/
```

Są podzielone według funkcjonalności:

- walka;
- balans;
- bonusy zasobów;
- umiejętności;
- bezpieczeństwo;
- komendy zarządzające.