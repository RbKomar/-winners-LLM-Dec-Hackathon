# Architektura Funkcjonalna Rozwiązania

## Ogólny Zarys
Rozwiązanie składa się z dwóch głównych etapów: ekstrakcji wiedzy z repozytorium i użytkowania z wykorzystaniem modelu językowego.

### Etap 1: Ekstrakcja Wiedzy
Ten etap koncentruje się na analizie i przetwarzaniu kodu źródłowego z repozytorium.

#### 1.1 Generowanie Grafu Zależności
- **Cel**: Tworzenie deterministycznego grafu zależności, który wizualizuje powiązania między różnymi elementami kodu (np. funkcje, klasy).
- **Proces**: Analiza kodu źródłowego w celu identyfikacji zależności i tworzenie grafu.

#### 1.2 Filtracja Kodu
- **Cel**: Wyselekcjonowanie istotnych fragmentów kodu do zbudowania bazy wiedzy.
- **Proces**: Ocena kodu pod kątem jego znaczenia i wpływu na funkcjonalność aplikacji.

#### 1.3 Dokumentacja Kodu
- **Cel**: Tworzenie lub ulepszanie istniejącej dokumentacji (docstringi).
- **Proces**: Analiza komentarzy i dokumentacji kodu, generowanie ulepszeń i propozycji.

#### 1.4 Generowanie Historii Zmian
- **Cel**: Tworzenie dokumentacji zmian w kodzie i danych.
- **Proces**: Śledzenie i rejestrowanie zmian w kodzie oraz w danych.

#### 1.5 Generowanie Testów
- **Cel**: Automatyczne tworzenie testów (np. unittesty).
- **Proces**: Analiza struktury i funkcjonalności kodu, generowanie odpowiednich testów.

#### 1.6 Baza Wiedzy
- **Cel**: Tworzenie indeksowanej bazy wiedzy z osadzeniami (vectorstore).
- **Proces**: Przetwarzanie i organizacja danych w formie łatwo dostępnej bazy.

### Etap 2: Użytkowanie
Etap ten dotyczy interakcji użytkowników z systemem przy użyciu modelu językowego.

#### 2.1 Zadawanie Pytań
- **Funkcja**: Umożliwienie użytkownikom zadawania pytań dotyczących istniejącego kodu.
- **Mechanizm**: Wykorzystanie modelu językowego do interpretacji zapytań i dostarczania odpowiedzi.

#### 2.2 Modyfikacja Kodu
- **Funkcja**: Pozwala na modyfikowanie istniejącego kodu.
- **Mechanizm**: Interfejs umożliwiający wprowadzanie zmian w kodzie poprzez komendy językowe.

#### 2.3 Dodawanie Funkcjonalności
- **Funkcja**: Umożliwienie dodawania nowych funkcjonalności do kodu.
- **Mechanizm**: Interakcja z modelem językowym w celu generowania propozycji kodu.

#### 2.4 Analiza Kodu
- **Funkcja**: Analiza wskazanych fragmentów kodu (np. pod kątem poprawności, podatności na błędy).
- **Mechanizm**: Wykorzystanie zaawansowanych funkcji modelu językowego do analizy i oceny kodu.