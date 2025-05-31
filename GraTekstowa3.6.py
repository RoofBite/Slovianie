# GraTekstowa3.6.py - WERSJA KOMPLETNA ZMODYFIKOWANA DLA PYODIDE

import random
# import time # Zastąpione przez asyncio
import math
import sys # Do przekierowania stdout
import asyncio # Do operacji asynchronicznych

# --- POCZĄTEK DODANEGO KODU DO INTEGRACJI Z JS ---
# Te funkcje (js_print_function, js_request_input_function)
# są dostarczane przez środowisko JavaScript poprzez pyodide.globals.set()







# --- Dodaj to u siebie w GraTekstowa3.6.py, pod innymi importami ---

import json
from js import window, Blob, URL, document

def get_state_as_json(game: "Game") -> str:
    """
    Zbiera najważniejsze pola gry i zwraca je jako JSON-string.
    (tu: bez kompresji, czyste json.dumps)
    """
    p = game.player
    player_state = {
        "lokacja_gracza": p.lokacja_gracza,
        "dni_w_podrozy": p.dni_w_podrozy,
        "godziny_w_tej_dobie": p.godziny_w_tej_dobie,
        "inventory": p.inventory,                   # np. {"jedzenie": 3, ...}
        "inventory_cenne": p.inventory_cenne,       # np. {"bursztyn": 2, ...}
        "inventory_towary_handlowe": p.inventory_towary_handlowe,
        "umiejetnosci": p.umiejetnosci,
        "punkty_umiejetnosci_do_wydania": p.punkty_umiejetnosci_do_wydania,
        "xp": p.xp,
        "poziom": p.poziom,
        "reputacja": p.reputacja,
        "wytrzymalosc": p.wytrzymalosc,
        "glod_pragnienie": p.glod_pragnienie,
        "komfort_psychiczny": p.komfort_psychiczny,
        "ma_ogien": p.ma_ogien,
        "ma_schronienie": p.ma_schronienie,
    }

    game_state = {
        "aktualny_etap_eksploracji_idx": game.aktualny_etap_eksploracji_idx,
        "lokacje_w_aktualnym_etapie": game.lokacje_w_aktualnym_etapie,
        "odkryte_typy_obszarow": list(game.odkryte_typy_obszarow),
        "aktywne_zadanie": game.aktywne_zadanie or None,
        "nazwa_aktualnej_wioski": game.nazwa_aktualnej_wioski,
        "wioski_info": list(game.wioski_info.keys()),
    }

    full = {
        "player": player_state,
        "game": game_state
    }
    # Używamy separators=(",",":") żeby JSON był trochę bardziej zwarty
    return json.dumps(full, separators=(",",":"))

def download_save(game: "Game"):
    """
    Generuje JSON (z get_state_as_json) i wywołuje JS, żeby pobrać plik save.json.
    """
    print("🔄 Wywołano download_save(game)")
    data_str = get_state_as_json(game)  # cały stan gry jako string JSON
    # Tworzymy Blob z tego stringa (ustawiamy typ "application/json")
    blob = Blob.new([data_str], { "type": "application/json" })
    # Tworzymy URL do bloba
    url = URL.createObjectURL(blob)
    # Dynamicznie tworzymy <a download="save.json" href="..."> i klikamy go
    a = document.createElement("a")
    a.href = url
    a.download = "save.json"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    # Zwolnij URL
    URL.revokeObjectURL(url)

def load_state_from_json(game: "Game", json_str: str):
    """
    Przyjmuje string JSON (tak jak wygenerowany w get_state_as_json)
    i przywraca stan gry (Game + Player).
    """
    try:
        full = json.loads(json_str)
    except Exception as e:
        print("Błąd parsowania JSON-a:", e)
        return False

    # 1) Przywróć Playera
    p = game.player
    ps = full.get("player", {})
    p.lokacja_gracza = ps.get("lokacja_gracza", p.lokacja_gracza)
    p.dni_w_podrozy = ps.get("dni_w_podrozy", p.dni_w_podrozy)
    p.godziny_w_tej_dobie = ps.get("godziny_w_tej_dobie", p.godziny_w_tej_dobie)
    p.inventory = ps.get("inventory", p.inventory)
    p.inventory_cenne = ps.get("inventory_cenne", p.inventory_cenne)
    p.inventory_towary_handlowe = ps.get("inventory_towary_handlowe", p.inventory_towary_handlowe)
    p.umiejetnosci = ps.get("umiejetnosci", p.umiejetnosci)
    p.punkty_umiejetnosci_do_wydania = ps.get("punkty_umiejetnosci_do_wydania", p.punkty_umiejetnosci_do_wydania)
    p.xp = ps.get("xp", p.xp)
    p.poziom = ps.get("poziom", p.poziom)
    p.reputacja = ps.get("reputacja", p.reputacja)
    p.wytrzymalosc = ps.get("wytrzymalosc", p.wytrzymalosc)
    p.glod_pragnienie = ps.get("glod_pragnienie", p.glod_pragnienie)
    p.komfort_psychiczny = ps.get("komfort_psychiczny", p.komfort_psychiczny)
    p.ma_ogien = ps.get("ma_ogien", p.ma_ogien)
    p.ma_schronienie = ps.get("ma_schronienie", p.ma_schronienie)
    # Po każdej istotnej zmianie: odśwież udźwig
    p.maks_udzwig = p.oblicz_maks_udzwig()
    p.oblicz_aktualny_udzwig()

    # 2) Przywróć stan Game’a
    gs = full.get("game", {})
    game.aktualny_etap_eksploracji_idx = gs.get("aktualny_etap_eksploracji_idx", game.aktualny_etap_eksploracji_idx)
    game.lokacje_w_aktualnym_etapie = gs.get("lokacje_w_aktualnym_etapie", game.lokacje_w_aktualnym_etapie)
    odkryte = gs.get("odkryte_typy_obszarow", list(game.odkryte_typy_obszarow))
    game.odkryte_typy_obszarow = set(odkryte)
    game.aktywne_zadanie = gs.get("aktywne_zadanie", game.aktywne_zadanie)
    game.nazwa_aktualnej_wioski = gs.get("nazwa_aktualnej_wioski", game.nazwa_aktualnej_wioski)
    # Otwórz wioski w game.wioski_info
    game.wioski_info = {}
    for nazwa in gs.get("wioski_info", []):
        game.wioski_info[nazwa] = Village(nazwa)

    print("🔄 Stan gry został wczytany z pliku save.json! Zatwierdź przyciskiem 'Wyślij'")
    return True




















class SimpleJsWriter:
    """Prosta klasa do przekierowania standardowego wyjścia do funkcji JavaScript."""
    def write(self, s):
        # Zakładamy, że js_print_function jest zdefiniowane globalnie przez Pyodide/JS
        js_print_function(s) # type: ignore
    def flush(self):
        # Pyodide zwykle automatycznie opróżnia bufor przy print
        pass

# Przekierowanie stdout i stderr na samym początku
# Upewnij się, że js_print_function jest ustawione przez JS zanim ten skrypt zacznie działać intensywnie
sys.stdout = SimpleJsWriter()
sys.stderr = SimpleJsWriter()


async def async_input(prompt=""):
    """Asynchroniczna funkcja do obsługi inputu od użytkownika poprzez JavaScript."""
    # js_request_input_function jest wstrzykiwane z JavaScript
    # Powinno wyświetlić prompt i zwrócić Promise, które rozwiązuje się z danymi od użytkownika.
    return await js_request_input_function(prompt) # type: ignore

# --- KONIEC DODANEGO KODU DO INTEGRACJI Z JS ---


# --- POCZĄTEK DODANYCH STAŁYCH I STRUKTUR DANYCH ---
PRODUKTY_ROLNE = "Produkty rolne"
MINERALY_I_SUROWCE = "Minerały i surowce"
PRODUKTY_RZEMIESLNICZE = "Produkty rzemieślnicze"
PRODUKTY_LUKSUSOWE = "Produkty luksusowe"
TECHNOLOGIE_I_INNOWACJE = "Technologie i innowacje"
# USLUGI = "Usługi" # Not for trading by player directly

PRODUKTY_HANDLOWE_INFO = {
    PRODUKTY_ROLNE: {"waga": 2.0, "bazowa_cena": 10, "opis": "Żywność, plony."},
    MINERALY_I_SUROWCE: {"waga": 3.0, "bazowa_cena": 15, "opis": "Rudy, kamienie, podstawowe surowce."},
    PRODUKTY_RZEMIESLNICZE: {"waga": 1.5, "bazowa_cena": 20, "opis": "Narzędzia, proste ubrania, ceramika."},
    PRODUKTY_LUKSUSOWE: {"waga": 0.5, "bazowa_cena": 50, "opis": "Biżuteria, drogie tkaniny, rzadkie przyprawy."},
    TECHNOLOGIE_I_INNOWACJE: {"waga": 1.0, "bazowa_cena": 30, "opis": "Fragmenty wiedzy, ulepszone narzędzia, wynalazki."},
} #
LISTA_PRODUKTOW_HANDLOWYCH = list(PRODUKTY_HANDLOWE_INFO.keys())

ASPEKTY_LISTA = [
    "Pogoda/klimat", "Ekonomia/gospodarka", "Hierarchia społeczna", "Geografia",
    "Infrastruktura", "Edukacja", "Różnice etniczne", "Legendy-wierzenia",
    "Bezpieczeństwo", "Prawo/praworządność", "Religia", "Rozrywka"
]

ASPEKTY_WPLYW_NA_PRODUKTY = {
    "Pogoda/klimat": [PRODUKTY_ROLNE],
    "Ekonomia/gospodarka": [PRODUKTY_ROLNE, MINERALY_I_SUROWCE, PRODUKTY_RZEMIESLNICZE, PRODUKTY_LUKSUSOWE, TECHNOLOGIE_I_INNOWACJE],
    "Hierarchia społeczna": [PRODUKTY_LUKSUSOWE],
    "Geografia": [PRODUKTY_ROLNE, MINERALY_I_SUROWCE],
    "Infrastruktura": [PRODUKTY_RZEMIESLNICZE],
    "Edukacja": [TECHNOLOGIE_I_INNOWACJE],
    "Różnice etniczne": [PRODUKTY_LUKSUSOWE],
    "Legendy-wierzenia": [PRODUKTY_LUKSUSOWE],
    "Bezpieczeństwo": [PRODUKTY_RZEMIESLNICZE],
    "Prawo/praworządność": [PRODUKTY_LUKSUSOWE],
    "Religia": [PRODUKTY_LUKSUSOWE],
    "Rozrywka": [PRODUKTY_LUKSUSOWE],
} #

def get_poziom_produkcji_opis(sumaryczny_wplyw):
    if sumaryczny_wplyw <= -2: return "Bardzo niski"
    if sumaryczny_wplyw == -1: return "Niski"
    if sumaryczny_wplyw == 0: return "Średni"
    if sumaryczny_wplyw == 1: return "Wysoki"
    if sumaryczny_wplyw >= 2: return "Bardzo wysoki"
    return "Średni"

CENY_MODYFIKATORY_PRODUKCJI = {
    "Bardzo niski": {"kupno_od_wioski_mod": 2.5, "sprzedaz_do_wioski_mod": 1.8},
    "Niski":        {"kupno_od_wioski_mod": 1.8, "sprzedaz_do_wioski_mod": 1.4},
    "Średni":       {"kupno_od_wioski_mod": 1.0, "sprzedaz_do_wioski_mod": 1.0},
    "Wysoki":       {"kupno_od_wioski_mod": 0.7, "sprzedaz_do_wioski_mod": 0.7},
    "Bardzo wysoki":{"kupno_od_wioski_mod": 0.5, "sprzedaz_do_wioski_mod": 0.5},
}

class Village:
    def __init__(self, name):
        self.name = name
        self.aspekty_wioski_numeric = {} #
        self.poziomy_produkcji_opis = {}
        self.ceny_produktow_finalne = {}

        self._generuj_aspekty_i_wplyw()
        self._oblicz_poziomy_produkcji_i_ceny()

    def _generuj_aspekty_i_wplyw(self):
        wybrane_nazwy_aspektow = random.sample(ASPEKTY_LISTA, 3)
        for nazwa_aspektu in wybrane_nazwy_aspektow:
            rzut = Game.rzut_koscia(4) #
            if rzut == 1: wplyw = -2 #
            elif rzut == 2: wplyw = -1 #
            elif rzut == 3: wplyw = 1
            else: wplyw = 2
            self.aspekty_wioski_numeric[nazwa_aspektu] = wplyw

    def _oblicz_poziomy_produkcji_i_ceny(self):
        for produkt, info_produktu in PRODUKTY_HANDLOWE_INFO.items():
            sumaryczny_wplyw_aspektow = 0 #
            for aspekt_wioski, wplyw_numeric_aspektu in self.aspekty_wioski_numeric.items():
                if produkt in ASPEKTY_WPLYW_NA_PRODUKTY.get(aspekt_wioski, []):
                    sumaryczny_wplyw_aspektow += wplyw_numeric_aspektu
            
            opis_poziomu_produkcji = get_poziom_produkcji_opis(sumaryczny_wplyw_aspektow)
            self.poziomy_produkcji_opis[produkt] = opis_poziomu_produkcji
            
            modyfikatory = CENY_MODYFIKATORY_PRODUKCJI[opis_poziomu_produkcji]
            bazowa_cena_produktu = info_produktu["bazowa_cena"]
            
            cena_kupna_od_wioski = int(bazowa_cena_produktu * modyfikatory["kupno_od_wioski_mod"])
            cena_sprzedazy_do_wioski = int(bazowa_cena_produktu * modyfikatory["sprzedaz_do_wioski_mod"])
            if cena_sprzedazy_do_wioski >= cena_kupna_od_wioski: # Gracz nie powinien sprzedawać drożej niż kupuje od wioski w tym samym momencie
                cena_sprzedazy_do_wioski = int(cena_kupna_od_wioski * 0.8) # Cena sprzedaży do wioski jest niższa
            
            self.ceny_produktow_finalne[produkt] = {
                "kupno_od_wioski": max(1, cena_kupna_od_wioski), # Cena, po której wioska sprzedaje graczowi
                "sprzedaz_do_wioski": max(1, cena_sprzedazy_do_wioski) # Cena, po której wioska kupuje od gracza
            }
    
    def get_village_goods_info_str(self, player_charisma_skill):
        output = f"\n--- Handel w {self.name} ---\n"
        output += "Aspekty wpływające na ekonomię wioski:\n"
        for aspekt, wplyw in self.aspekty_wioski_numeric.items():
            wplyw_str = {-2: "bardzo zły", -1: "zły", 1: "dobry", 2: "bardzo dobry"}.get(wplyw, "neutralny")
            output += f"  - {aspekt} (wpływ: {wplyw_str})\n"
        
        output += "\nDostępne towary handlowe (ceny uwzględniają Twoją charyzmę):\n"
        
        # Charyzma wpływa na cenę, jaką gracz płaci wiosce (kupno_od_wioski)
        # Charyzma NIE wpływa na cenę, jaką wioska płaci graczowi (sprzedaz_do_wioski) - to bardziej zależy od potrzeb wioski
        mnoznik_ceny_zakupu_przez_gracza = max(0.7, 1.0 - player_charisma_skill * 0.03) # Gracz kupuje taniej
        mnoznik_ceny_sprzedazy_przez_gracza = 1.0  # Brak wpływu charyzmy na to, ile wioska płaci graczowi

        for produkt_nazwa in LISTA_PRODUKTOW_HANDLOWYCH:
            info_produktu = PRODUKTY_HANDLOWE_INFO[produkt_nazwa]
            poziom_produkcji = self.poziomy_produkcji_opis.get(produkt_nazwa, "Brak danych")
            ceny_bazowe_wioski = self.ceny_produktow_finalne.get(produkt_nazwa, {})
            
            # Cena, po której gracz KUPUJE od wioski
            cena_kupna_dla_gracza = max(1, int(ceny_bazowe_wioski.get('kupno_od_wioski', 9999) * mnoznik_ceny_zakupu_przez_gracza))
            # Cena, po której gracz SPRZEDAJE do wioski
            cena_sprzedazy_dla_gracza = max(1, int(ceny_bazowe_wioski.get('sprzedaz_do_wioski', 0) * mnoznik_ceny_sprzedazy_przez_gracza))

            output += f"  - {produkt_nazwa} (Waga: {info_produktu['waga']})\n"
            output += f"    Produkcja wioski: {poziom_produkcji}\n"
            output += f"    Możesz kupić za: {cena_kupna_dla_gracza} zł\n"
            output += f"    Możesz sprzedać za: {cena_sprzedazy_dla_gracza} zł\n"
        return output

# --- KONIEC DODANYCH STAŁYCH I KLASY VILLAGE ---

class Player:
    def __init__(self):
        # --- Podstawowe Atrybuty ---
        self.wytrzymalosc = 6.0
        self.glod_pragnienie = 6.0
        self.komfort_psychiczny = 6.0
        
        # --- Ekwipunek ---
        self.inventory = {"jedzenie": 3, "woda": 3, "drewno": 1, "zloto": 50} #
        self.inventory_cenne = {"bursztyn": 0, "stara_moneta": 0, "rzadkie_zioło_lecznicze": 0, "fragment_mapy": 0} #
        # --- Nowy ekwipunek na towary handlowe ---
        self.inventory_towary_handlowe = {produkt: 0 for produkt in LISTA_PRODUKTOW_HANDLOWYCH}

        # --- Stan Gracza ---
        self.ma_schronienie = False
        self.ma_ogien = False
        self.lokacja_gracza = "WieśStartowa" # WAŻNE: Inicjalizacja tego atrybutu
        self.dni_w_podrozy = 0.0
        self.godziny_w_tej_dobie = 0.0
        
        # --- Bonusy Sytuacyjne ---
        self.ma_bonus_do_umiejetnosci = False #
        self.wartosc_bonusu_do_umiejetnosci = 0 #
        self.opis_bonusu_do_umiejetnosci = "" #

        # --- System Rozwoju ---
        self.poziom = 1
        self.xp = 0
        self.xp_do_nastepnego_poziomu = 100
        self.punkty_umiejetnosci_do_wydania = 1 #
        self.umiejetnosci = {
            "przetrwanie": 1, 
            "zielarstwo_tropienie": 1, 
            "walka": 1, 
            "charyzma_handel": 1,
            "udzwig": 1 #
        } #
        self.reputacja = {"WieśStartowa": 0}

        # --- System Udźwigu --- #
        self.maks_udzwig = self.oblicz_maks_udzwig()
        self.aktualny_udzwig = self.oblicz_aktualny_udzwig()


    def oblicz_maks_udzwig(self):
        return 5.0 + (self.umiejetnosci["udzwig"] * 5.0)

    def oblicz_aktualny_udzwig(self):
        current_weight = 0.0
        for towar, ilosc in self.inventory_towary_handlowe.items():
            if ilosc > 0:
                current_weight += ilosc * PRODUKTY_HANDLOWE_INFO[towar]["waga"]
        self.aktualny_udzwig = current_weight
        return current_weight
        
    def zmien_towar_handlowy(self, towar, ilosc_zmiana):
        if towar not in PRODUKTY_HANDLOWE_INFO:
            print(f"Błąd: Nieznany towar handlowy {towar}")
            return False

        waga_sztuki = PRODUKTY_HANDLOWE_INFO[towar]["waga"]
        
        if ilosc_zmiana < 0:
            if self.inventory_towary_handlowe.get(towar, 0) < abs(ilosc_zmiana):
                print(f"Nie masz wystarczająco dużo '{towar.lower()}' ({self.inventory_towary_handlowe.get(towar,0)} szt.), aby usunąć {abs(ilosc_zmiana)} szt.")
                return False
        
        if ilosc_zmiana > 0:
            potencjalna_zmiana_wagi = ilosc_zmiana * waga_sztuki
            if self.aktualny_udzwig + potencjalna_zmiana_wagi > self.maks_udzwig:
                print(f"Nie możesz tyle unieść. Przekraczasz udźwig o {(self.aktualny_udzwig + potencjalna_zmiana_wagi) - self.maks_udzwig:.1f} kg.")
                print(f"Masz: {self.aktualny_udzwig:.1f}/{self.maks_udzwig:.1f} kg. Próbujesz dodać {potencjalna_zmiana_wagi:.1f} kg.")
                return False

        self.inventory_towary_handlowe[towar] = self.inventory_towary_handlowe.get(towar, 0) + ilosc_zmiana
        self.oblicz_aktualny_udzwig()
        return True

    def __str__(self):
        cenne_str = ", ".join([f"{item.replace('_',' ').capitalize()}: {qty}" for item, qty in self.inventory_cenne.items() if qty > 0]) #
        if not cenne_str: cenne_str = "Brak" #

        wytrzymalosc_display = int(self.wytrzymalosc) if self.wytrzymalosc == int(self.wytrzymalosc) else f"{self.wytrzymalosc:.1f}"
        glod_pragnienie_display = int(self.glod_pragnienie) if self.glod_pragnienie == int(self.glod_pragnienie) else f"{self.glod_pragnienie:.1f}"
        komfort_psychiczny_display = int(self.komfort_psychiczny) if self.komfort_psychiczny == int(self.komfort_psychiczny) else f"{self.komfort_psychiczny:.1f}"

        umiejetnosci_str = ", ".join([f"{u.replace('_',' ').capitalize()}: {p}" for u, p in self.umiejetnosci.items()])
        
        towary_handlowe_str_list = []
        for towar, ilosc in self.inventory_towary_handlowe.items():
            if ilosc > 0:
                towary_handlowe_str_list.append(f"{towar}: {ilosc}")
        towary_handlowe_str = ", ".join(towary_handlowe_str_list) if towary_handlowe_str_list else "Brak"

        return (f"\n--- Stan Postaci ---\n"
                f"Poziom: {self.poziom}, XP: {self.xp}/{self.xp_do_nastepnego_poziomu}" + (f" (Punkty umiejętności: {self.punkty_umiejetnosci_do_wydania})" if self.punkty_umiejetnosci_do_wydania > 0 else "") + "\n" #
                f"Umiejętności: {umiejetnosci_str}\n"
                f"Wytrzymałość:         {wytrzymalosc_display}/11\n"
                f"Głód/Pragnienie:      {glod_pragnienie_display}/11 (Im niżej, tym gorzej)\n"
                f"Komfort Psychiczny:   {komfort_psychiczny_display}/11\n" #
                f"Ekwipunek: Jedzenie: {self.inventory['jedzenie']}, Woda: {self.inventory['woda']}, Drewno: {self.inventory['drewno']}, Złoto: {self.inventory['zloto']}\n" #
                f"Cenne Znaleziska:   {cenne_str}\n" #
                f"Towary Handlowe:    {towary_handlowe_str}\n"
                f"Udźwig:             {self.aktualny_udzwig:.1f}/{self.maks_udzwig:.1f} kg\n"
                f"Posiada ogień:      {'Tak' if self.ma_ogien else 'Nie'}\n" #
                f"Posiada schronienie:{'Tak' if self.ma_schronienie else 'Nie'}\n" #
                f"Dni w podróży: {int(self.dni_w_podrozy)}" + #
                (f"\nAktywny bonus: {self.opis_bonusu_do_umiejetnosci} (+{self.wartosc_bonusu_do_umiejetnosci} do następnego testu umiejętności)" if self.ma_bonus_do_umiejetnosci else "")) #

    async def dodaj_xp(self, ilosc): # ZMODYFIKOWANE: async
        if ilosc <= 0: return
        self.xp += ilosc
        print(f"Zdobywasz {ilosc} punktów doświadczenia!")
        while self.xp >= self.xp_do_nastepnego_poziomu:
            self.poziom += 1 #
            self.xp -= self.xp_do_nastepnego_poziomu #
            self.xp_do_nastepnego_poziomu = int(self.xp_do_nastepnego_poziomu * 1.5)  #
            self.punkty_umiejetnosci_do_wydania += 1  #
            self.wytrzymalosc = min(11.0, self.wytrzymalosc + 0.5) #
            self.glod_pragnienie = min(11.0, self.glod_pragnienie + 0.2) #
            self.komfort_psychiczny = min(11.0, self.komfort_psychiczny + 0.2) #
            print(f"AWANS! Osiągnąłeś {self.poziom} poziom postaci!") #
            print(f"Otrzymujesz 1 punkt umiejętności do rozdysponowania.") #
            print(f"Następny poziom za {self.xp_do_nastepnego_poziomu - self.xp} XP.") #
            await async_input("Naciśnij Enter, aby kontynuować...") # ZMODYFIKOWANE


    def zmien_potrzebe(self, potrzeba, wartosc, cicho=False):
        stara_wartosc = 0.0
        aktualna_wartosc = 0.0 
        wartosc_f = float(wartosc)
        
        if potrzeba == "wytrzymalosc": #
            # Jeśli to spadek i wytrzymałość jest wysoka, zmniejsz spadek o połowę
            if wartosc_f < 0 and self.wytrzymalosc >= 9.0:
                wartosc_f *= 0.5
            stara_wartosc = self.wytrzymalosc
            self.wytrzymalosc = max(1.0, min(11.0, self.wytrzymalosc + wartosc_f)) #
            aktualna_wartosc = self.wytrzymalosc
        elif potrzeba == "glod_pragnienie": #
            # Jeśli to spadek i głód/pragnienie są na wysokim poziomie, zmniejsz spadek o połowę
            if wartosc_f < 0 and self.glod_pragnienie >= 9.0:
                wartosc_f *= 0.5
            stara_wartosc = self.glod_pragnienie
            self.glod_pragnienie = max(1.0, min(11.0, self.glod_pragnienie + wartosc_f)) #
            aktualna_wartosc = self.glod_pragnienie #
        elif potrzeba == "komfort_psychiczny": #
            # Jeśli to spadek i komfort jest wysoki, zmniejsz spadek o połowę
            if wartosc_f < 0 and self.komfort_psychiczny >= 9.0:
                wartosc_f *= 0.5
            stara_wartosc = self.komfort_psychiczny
            self.komfort_psychiczny = max(1.0, min(11.0, self.komfort_psychiczny + wartosc_f)) #
            aktualna_wartosc = self.komfort_psychiczny
        else:
            if not cicho: print(f"Nieznana potrzeba: {potrzeba}") #
            return #

        if not cicho and wartosc_f != 0 and abs(stara_wartosc - aktualna_wartosc) > 0.01 : #
            # Obliczenie oryginalnej wartości spadku, aby poprawnie wyświetlić komunikat
            oryginalna_wartosc_f = float(wartosc)
            zmiana_display = f"{wartosc_f:+.1f}".replace(".0","")
            # Dodatkowy komunikat, jeśli spadek został zredukowany
            if wartosc_f != oryginalna_wartosc_f:
                zmiana_display += " (spadek został zmiejszony z powodu wysokiego zaspojenia tej potrzeby)"
            
            aktualna_display = f"{aktualna_wartosc:.1f}".replace(".0","")
            print(f" {potrzeba.replace('_',' ').capitalize()} zmienia się o {zmiana_display} (do: {aktualna_display}).") #


    def oblicz_modyfikator_rzutu(self):
        stany_potrzeb_wartosci = []
        epsilon = 0.1  #
        if self.wytrzymalosc <= 3.0 + epsilon: stany_potrzeb_wartosci.append(self.wytrzymalosc) #
        elif self.wytrzymalosc >= 9.0 - epsilon: stany_potrzeb_wartosci.append(self.wytrzymalosc) #
        if self.glod_pragnienie <= 3.0 + epsilon: stany_potrzeb_wartosci.append(self.glod_pragnienie) #
        elif self.glod_pragnienie >= 9.0 - epsilon: stany_potrzeb_wartosci.append(self.glod_pragnienie) #
        if self.komfort_psychiczny <= 3.0 + epsilon: stany_potrzeb_wartosci.append(self.komfort_psychiczny) #
        elif self.komfort_psychiczny >= 9.0 - epsilon: stany_potrzeb_wartosci.append(self.komfort_psychiczny) #
        
        if not stany_potrzeb_wartosci: return 0 #
        stany_potrzeb_wartosci.sort() #
        negatywne = [s for s in stany_potrzeb_wartosci if s <= 3.0 + epsilon] #
        pozytywne = [s for s in stany_potrzeb_wartosci if s >= 9.0 - epsilon] #
        
        while negatywne and pozytywne: negatywne.pop(0); pozytywne.pop() #
        pozostale_stany = negatywne + pozytywne #
        if not pozostale_stany: return 0 #
            
        final_mod = 0
        for stan in pozostale_stany:
            if stan <= 1.9 + epsilon: final_mod -= 2  #
            elif stan <= 2.9 + epsilon: final_mod -= 1 #
            elif stan <= 3.9 + epsilon: final_mod -= 1  #
            elif stan >= 9.0 - epsilon and stan < 10.0 - epsilon: final_mod += 1 #
            elif stan >= 10.0 - epsilon and stan < 11.0 - epsilon: final_mod += 1 #
            elif stan >= 11.0 - epsilon: final_mod += 2 #
        return final_mod #

    def uzyj_bonusu_umiejetnosci(self):
        if self.ma_bonus_do_umiejetnosci:
            bonus_val = self.wartosc_bonusu_do_umiejetnosci #
            print(f"Wykorzystujesz swój bonus '{self.opis_bonusu_do_umiejetnosci}' (+{bonus_val})!") #
            self.ma_bonus_do_umiejetnosci = False #
            self.wartosc_bonusu_do_umiejetnosci = 0 #
            self.opis_bonusu_do_umiejetnosci = "" #
            return bonus_val #
        return 0 #

    def przyznaj_bonus_umiejetnosci(self, wartosc, opis):
        self.ma_bonus_do_umiejetnosci = True #
        self.wartosc_bonusu_do_umiejetnosci = wartosc #
        self.opis_bonusu_do_umiejetnosci = opis #
        print(f"Otrzymujesz bonus '{opis}' (+{wartosc} do następnego testu umiejętności).") #


    async def uplyw_czasu(self, godziny=1, opis_czynnosci=""): # ZMODYFIKOWANE: async
        if godziny <=0: return
        godziny_f = float(godziny)

        modyfikator_przetrwania_czas = 1.0 - (self.umiejetnosci["przetrwanie"] * 0.02) #
        modyfikator_przetrwania_czas = max(0.5, modyfikator_przetrwania_czas)  #

        print(f"\nUpływa {godziny_f if godziny_f != int(godziny_f) else int(godziny_f)} godz. ({opis_czynnosci})...") #
        self.godziny_w_tej_dobie += godziny_f #
        
        self.zmien_potrzebe("glod_pragnienie", -0.5 * godziny_f * modyfikator_przetrwania_czas, cicho=True) #
        if not self.ma_ogien and self.lokacja_gracza != "WieśStartowa" and not self.ma_schronienie : #
             self.zmien_potrzebe("komfort_psychiczny", -0.2 * godziny_f * modyfikator_przetrwania_czas, cicho=True)  #

        if self.godziny_w_tej_dobie >= 24.0:
            przetrwane_dni_float = self.godziny_w_tej_dobie / 24.0 #
            przetrwane_dni_int = int(przetrwane_dni_float) #
            self.dni_w_podrozy += przetrwane_dni_float #
            self.godziny_w_tej_dobie %= 24.0 #
            if przetrwane_dni_int > 0:
                print(f"Mija {przetrwane_dni_int} dzień/dni. Jesteś w podróży od {int(self.dni_w_podrozy)} dni.") #
                await self.dodaj_xp(int(5 * przetrwane_dni_int)) # ZMODYFIKOWANE #

        epsilon = 0.5 #
        if self.wytrzymalosc <= 3.0 + epsilon and self.wytrzymalosc > 1.0: print("Jesteś bardzo zmęczony, każdy ruch to wysiłek.") #
        if self.glod_pragnienie <= 3.0 + epsilon and self.glod_pragnienie > 1.0: print("Dotkliwie odczuwasz głód i pragnienie.") #
        if self.komfort_psychiczny <= 3.0 + epsilon and self.komfort_psychiczny > 1.0: print("Czujesz się bardzo niekomfortowo i niespokojnie.") #


    async def odpocznij(self, godziny, jakosc_snu_mod=0, koszt_czasu=True, w_wiosce=False): # ZMODYFIKOWANE: async #
        godziny_f = float(godziny)
        print(f"Odpoczywasz przez {godziny_f if godziny_f != int(godziny_f) else int(godziny_f)} godzin.") #
        
        regeneracja_base = godziny_f * (0.5 + jakosc_snu_mod * 0.5)  #
        if self.komfort_psychiczny < 4.0 and jakosc_snu_mod < 3 and not w_wiosce:
            regeneracja_base *= 0.7 #
            print("Trudno było wypocząć w tych warunkach...") #

        self.zmien_potrzebe("wytrzymalosc", regeneracja_base) #
        if w_wiosce and jakosc_snu_mod >=2 : 
            self.zmien_potrzebe("komfort_psychiczny", min(godziny_f / 2.0, 3.0))  #

        if koszt_czasu:
            await self.uplyw_czasu(godziny_f, "odpoczynek") # ZMODYFIKOWANE #

    async def jedz_z_ekwipunku(self): # ZMODYFIKOWANE: async
        if self.inventory["jedzenie"] > 0:
            self.inventory["jedzenie"] -= 1 #
            self.zmien_potrzebe("glod_pragnienie", 4.0)  #
            print("Zjadasz porcję jedzenia z zapasów. Czujesz się pokrzepiony.") #
            if random.random() < 0.15:  #
                self.zmien_potrzebe("komfort_psychiczny", 1.0) #
                print("Ten posiłek był wyjątkowo smaczny i poprawił Ci humor!") #
            await self.uplyw_czasu(0.5, "jedzenie") # ZMODYFIKOWANE #
        else:
            print("Nie masz nic do jedzenia w ekwipunku.") #

    async def pij_z_ekwipunku(self): # ZMODYFIKOWANE: async #
        if self.inventory["woda"] > 0:
            self.inventory["woda"] -= 1 #
            self.zmien_potrzebe("glod_pragnienie", 3.0)  #
            print("Pijesz wodę z bukłaka. Pragnienie nieco maleje.") #
            await self.uplyw_czasu(0.2, "picie wody") # ZMODYFIKOWANE #
        else:
            print("Nie masz nic do picia w bukłaku.") #

    async def rozpal_ogien(self): # ZMODYFIKOWANE: async
        if self.inventory["drewno"] > 0:
            print("Próbujesz rozpalić ogień...") #
            bonus_um_stat = self.umiejetnosci["przetrwanie"] // 2  #
            bonus_um_sytuacyjny = self.uzyj_bonusu_umiejetnosci() #
            
            trudnosc_podstawowa_szansa_niepowodzenia = OBSZARY_DZICZY.get(self.lokacja_gracza, {}).get("trudnosc_ognia", 0.1) #
            prog_trudnosci_ognia = 4 + int(trudnosc_podstawowa_szansa_niepowodzenia * 10)  #
            prog_trudnosci_ognia = max(2, prog_trudnosci_ognia - bonus_um_stat)  #
            
            rzut_ogien = Game.rzut_koscia(10) + bonus_um_sytuacyjny #
            
            if rzut_ogien >= prog_trudnosci_ognia :
                self.inventory["drewno"] -= 1 #
                self.ma_ogien = True #
                self.zmien_potrzebe("komfort_psychiczny", 2.0)  #
                print(f"Sukces! (Rzut: {rzut_ogien} vs Próg: {prog_trudnosci_ognia}). Rozpalasz ognisko.") #
                await self.dodaj_xp(5)  # ZMODYFIKOWANE #
            else:
                print(f"Niestety, nie udaje Ci się rozpalić ognia (Rzut: {rzut_ogien} vs Próg: {prog_trudnosci_ognia}). Iskry gasną.") #
                self.inventory["drewno"] -= 1  #
                self.zmien_potrzebe("wytrzymalosc",-0.5)  #
            await self.uplyw_czasu(0.5, "rozpalanie ognia")  # ZMODYFIKOWANE #
        else:
            print("Nie masz drewna na opał.") #
            
    async def zbuduj_schronienie(self): # ZMODYFIKOWANE: async
        if self.inventory["drewno"] >=2:  #
            print("Próbujesz zbudować prowizoryczne schronienie...") #
            bonus_um_stat = self.umiejetnosci["przetrwanie"] // 2 #
            bonus_um_sytuacyjny = self.uzyj_bonusu_umiejetnosci() #
            prog_trudnosci_budowy = 6  #
            prog_trudnosci_budowy = max(3, prog_trudnosci_budowy - bonus_um_stat) #
            
            rzut_budowa = Game.rzut_koscia(10) + bonus_um_sytuacyjny #

            if rzut_budowa >= prog_trudnosci_budowy:
                self.inventory["drewno"] -=2 #
                self.ma_schronienie = True #
                bonus_komfort_schronienia = 2.0 + (self.umiejetnosci["przetrwanie"] / 3.0) + (1.0 if rzut_budowa >= prog_trudnosci_budowy + 3 else 0.0) #
                self.zmien_potrzebe("komfort_psychiczny", bonus_komfort_schronienia)  #
                print(f"Udało Ci się zbudować schronienie! (Rzut: {rzut_budowa} vs Próg: {prog_trudnosci_budowy}). Czujesz się bezpieczniej.") #
                await self.dodaj_xp(10)  # ZMODYFIKOWANE #
            else:
                self.inventory["drewno"] -=1  #
                print(f"Niestety, konstrukcja okazała się zbyt słaba (Rzut: {rzut_budowa} vs Próg: {prog_trudnosci_budowy}).") #

            self.zmien_potrzebe("wytrzymalosc", -1.0)  #
            await self.uplyw_czasu(1.5, "budowa schronienia")  # ZMODYFIKOWANE #
        else:
            print("Masz za mało drewna by zbudować schronienie.") #

OBSZARY_DZICZY = {
    "Gęsty Las": {
        "opis": "Przedzierasz się przez gęsty, mroczny las. Konary starych drzew tworzą nieprzenikniony baldachim.", #
        "kary_przy_wejsciu": {"wytrzymalosc": -0.5, "komfort_psychiczny": -0.5},  #
        "zasoby": {"drewno": (2, 0.7), "jedzenie_roslinne": (1, 0.5), "zwierzyna_mala": (1,0.3), "bursztyn": (1, 0.05)}, #
        "wydarzenia_specjalne": ["slady_bestii", "szelest_w_krzakach", "aura_demonow", "dzikie_zwierze"], # # Dodano dzikie_zwierze dla testów
        "trudnosc_ognia": 0.2,  #
        "opis_demonow": "Czujesz czyhające zło między drzewami, słyszysz nienaturalne szepty niesione przez wiatr.", #
        "xp_za_odkrycie": 15 #
    },
    "Mokradła": {
        "opis": "Stąpasz ostrożnie po zdradliwych mokradłach. Powietrze jest ciężkie od wilgoci i zapachu zgnilizny.", #
        "kary_przy_wejsciu": {"wytrzymalosc": -1.0, "komfort_psychiczny": -1.0, "glod_pragnienie":-0.5},  #
        "zasoby": {"woda_brudna": (2,0.8), "jedzenie_roslinne_bagienne": (1, 0.4), "rzadkie_zioło_lecznicze": (1, 0.1)}, #
        "wydarzenia_specjalne": ["uciqzliwe_insekty", "odglosy_z_bagien", "mgla", "aura_demonow", "dzikie_zwierze"], #
        "trudnosc_ognia": 0.7, #
        "opis_demonow": "Opary unoszące się nad bagnami zdają się przybierać kształty pełzających istot, a woda bulgocze wbrew naturze.", #
        "xp_za_odkrycie": 20 #
    },
    "Jałowe Wzgórza": {
        "opis": "Wędrujesz przez jałowe, smagane wiatrem wzgórza. Roślinność jest tu skąpa, a ziemia twarda.", #
        "kary_przy_wejsciu": {"glod_pragnienie": -0.5, "wytrzymalosc":-0.5},  #
        "zasoby": {"drewno_suche": (1, 0.3), "woda_skala": (1, 0.2), "stara_moneta": (1, 0.08)}, #
        "wydarzenia_specjalne": ["silny_wiatr", "poczucie_obserwacji", "kamienne_kregi", "dzikie_zwierze"], #
        "trudnosc_ognia": 0.1, #
        "opis_demonow": "Wiatr niesie echa dawnych, mrocznych rytuałów odprawianych na tych wzgórzach, a cienie skał wydają się nienaturalnie długie.", #
        "xp_za_odkrycie": 15 #
    },
    "Stary Święty Gaj": {  #
        "opis": "Trafiasz do starego, cichego gaju. Prastare dęby zdają się emanować spokojem.", #
        "bonusy_przy_wejsciu": {"komfort_psychiczny": 1.0, "wytrzymalosc": 0.5}, #
        "zasoby": {"jedzenie_roslinne_lecznicze": (1, 0.6), "woda_czysta_zrodlo": (2, 0.9), "drewno_swiete": (1,0.4), "rzadkie_zioło_lecznicze": (1,0.3)}, #
        "wydarzenia_specjalne": ["znalezisko_ziola_lecznicze", "chwila_kontemplacji", "przychylnosc_duchow_gaju"], #
        "trudnosc_ognia": 0.0,  #
        "pozytywny": True, #
        "xp_za_odkrycie": 30 #
    },
    "Opuszczona Chata": {
        "opis": "Natrafiasz na ślady dawnej bytności - opuszczoną, na wpół zrujnowaną chatę.", #
        "bonusy_przy_wejsciu": {"komfort_psychiczny": 0.5},  #
        "zasoby": {"drewno_stare": (2,0.8), "resztki_narzedzi": (1,0.2), "fragment_mapy": (1, 0.1)},  #
        "wydarzenia_specjalne": ["niepokojace_znalezisko_w_chacie", "schronienie_przed_deszczem", "slady_walki"], #
        "trudnosc_ognia": 0.1, #
        "pozytywny": True, #
        "xp_za_odkrycie": 25 #
    },
    "Spalona Ziemia": {
        "opis": "Przechodzisz przez krainę spustoszoną przez dawny pożar. Wszędzie widać zwęglone kikuty drzew i popiół.", #
        "kary_przy_wejsciu": {"komfort_psychiczny": -1.0, "glod_pragnienie": -0.5}, #
        "zasoby": {"drewno_opalone": (3, 0.5), "stara_moneta": (1, 0.03)}, #
        "wydarzenia_specjalne": ["poczucie_straty", "aura_demonow", "znalezisko_w_pogorzelisku", "dzikie_zwierze"], #
        "trudnosc_ognia": 0.3, #
        "opis_demonow": "Wydaje się, że cienie zgliszcz poruszają się same, a wiatr szepcze o cierpieniu tych, którzy tu zginęli.", #
        "xp_za_odkrycie": 20 #
    },
    "Kamieniste Pustkowie": { #
        "opis": "Bezkresne, kamieniste pustkowie rozciąga się przed Tobą. Nieliczne, karłowate krzewy walczą o życie.", #
        "kary_przy_wejsciu": {"wytrzymalosc": -1.0, "glod_pragnienie": -1.0}, #
        "zasoby": {"woda_skala": (1, 0.1), "drobna_zwierzyna_pustynna": (1, 0.1)}, #
        "wydarzenia_specjalne": ["ekstremalne_temperatury", "burza_piaskowa", "poczucie_osamotnienia", "dzikie_zwierze"], #
        "trudnosc_ognia": 0.5, #
        "opis_demonow": "W tej pustce czujesz, jakby sama ziemia była wroga życiu, a duchy zmarłych z pragnienia wędrowców jęczą na wietrze.", #
        "xp_za_odkrycie": 25 #
    }
}
ETAPY_EKSPLORACJI_KOSCI = [
    [10, 8, 6], [8, 10, 12], [10, 8, 6], [8, 10, 12] , [10, 8, 6],[8, 10, 12]
]
CENNE_PRZEDMIOTY_CENY = {
    "bursztyn": 20, "stara_moneta": 18, "rzadkie_zioło_lecznicze": 15, "fragment_mapy": 25 #
}

class Game:
    def __init__(self):
        self.player = Player()
        self.aktualny_etap_eksploracji_idx = 0
        self.lokacje_w_aktualnym_etapie = 0
        self.max_lokacji_na_etap = 3 
        self.odkryte_typy_obszarow = set()
        self.aktywne_zadanie = None
        self.nazwa_aktualnej_wioski = "WieśStartowa" #
        self.wioski_info = {}

    @staticmethod
    def rzut_koscia(k_max):
        if k_max <=0 : return 0
        return random.randint(1, k_max) #

    async def przyznaj_xp_za_odkrycie_obszaru(self, nazwa_obszaru): # ZMODYFIKOWANE: async
        if nazwa_obszaru not in self.odkryte_typy_obszarow:
            obszar_dane = OBSZARY_DZICZY.get(nazwa_obszaru) #
            if obszar_dane:
                xp = obszar_dane.get("xp_za_odkrycie", 0) #
                if xp > 0:
                    print(f"Odkrywasz nowy typ obszaru: {nazwa_obszaru}!") #
                    await self.player.dodaj_xp(xp) # ZMODYFIKOWANE #
                    self.odkryte_typy_obszarow.add(nazwa_obszaru) #

    async def generuj_zadanie(self): # ZMODYFIKOWANE: async (choć może nie być konieczne, jeśli nie robi nic async)
        if self.aktywne_zadanie: return #

        reputacja_wioski = self.player.reputacja.get(self.nazwa_aktualnej_wioski, 0) #
        typy_zadan = [] #
        typy_zadan.extend([ #
            {"typ": "przynies_skory_wilka", "cel_ilosc": Game.rzut_koscia(2)+1, "nagroda_xp": 30, "nagroda_zloto": 15, "opis": f"Starszy z {self.nazwa_aktualnej_wioski} potrzebuje skór wilków."}, #
            {"typ": "zbierz_ziola", "cel_ilosc": Game.rzut_koscia(2)+2, "nagroda_xp": 25, "nagroda_zloto": 10, "opis": f"Miejscowa znachorka prosi o zebranie rzadkich ziół leczniczych."}, #
        ])
        if reputacja_wioski >= 10: #
            typy_zadan.append({"typ": "zbadaj_miejsce", "cel_lokacja": random.choice(["Stary Święty Gaj","Opuszczona Chata","Spalona Ziemia"]), "nagroda_xp": 50, "nagroda_zloto": 20, "opis": f"Mieszkańcy są zaniepokojeni wieściami z pobliskiego miejsca. Proszą byś to sprawdził."}) #
        if reputacja_wioski >= 20: #
             typy_zadan.append({"typ": "upoluj_dzika", "cel_ilosc": 1, "nagroda_xp": 70, "nagroda_zloto": 35, "opis": f"Groźny dzik zagraża okolicznym polom. Starszy prosi o pomoc."}) #

        if not typy_zadan: 
            return #

        self.aktywne_zadanie = random.choice(typy_zadan) #
        if "cel_ilosc" in self.aktywne_zadanie:
            self.aktywne_zadanie["postep"] = 0 #
        self.aktywne_zadanie["zleceniodawca_wioska"] = self.nazwa_aktualnej_wioski #
        print(f"\nOtrzymujesz nowe zadanie: {self.aktywne_zadanie['opis']}") #
        if "cel_ilosc" in self.aktywne_zadanie:
            print(f"Cel: zebrać {self.aktywne_zadanie['cel_ilosc']} (Masz: {self.aktywne_zadanie['postep']})") #
        elif "cel_lokacja" in self.aktywne_zadanie:
             print(f"Cel: Zbadaj {self.aktywne_zadanie['cel_lokacja']}") #


    async def sprawdz_postep_zadania(self, typ_akcji, ilosc=1, dodatkowe_dane=None): # ZMODYFIKOWANE: async
        if not self.aktywne_zadanie: return #

        zad = self.aktywne_zadanie #
        ukonczone = False #

        if zad["typ"] == "przynies_skory_wilka" and typ_akcji == "pokonano_wilka": #
            zad["postep"] = min(zad["cel_ilosc"], zad["postep"] + ilosc) #
            print(f"Postęp w zadaniu '{zad['opis']}': {zad['postep']}/{zad['cel_ilosc']}") #
            if zad["postep"] >= zad["cel_ilosc"]: ukonczone = True #
        elif zad["typ"] == "zbierz_ziola" and typ_akcji == "zebrano_rzadkie_ziolo": #
            zad["postep"] = min(zad["cel_ilosc"], zad["postep"] + ilosc) #
            print(f"Postęp w zadaniu '{zad['opis']}': {zad['postep']}/{zad['cel_ilosc']}") #
            if zad["postep"] >= zad["cel_ilosc"]: ukonczone = True #
        elif zad["typ"] == "upoluj_dzika" and typ_akcji == "pokonano_dzika": #
            zad["postep"] = min(zad["cel_ilosc"], zad["postep"] + ilosc) #
            print(f"Postęp w zadaniu '{zad['opis']}': {zad['postep']}/{zad['cel_ilosc']}") #
            if zad["postep"] >= zad["cel_ilosc"]: ukonczone = True #
        elif zad["typ"] == "zbadaj_miejsce" and typ_akcji == "zbadano_lokacje": #
            if dodatkowe_dane and dodatkowe_dane.get("nazwa_lokacji") == zad["cel_lokacja"]: #
                print(f"Zebrałeś informacje o {zad['cel_lokacja']}. Wróć do {zad['zleceniodawca_wioska']}, by zdać raport.") #
                zad["postep"] = 1 #
            
        if ukonczone: 
            print(f"\nUkończyłeś zadanie (ilościowe): {zad['opis']}!") #
            await self.player.dodaj_xp(zad["nagroda_xp"]) # ZMODYFIKOWANE #
            self.player.inventory["zloto"] += zad["nagroda_zloto"] #
            print(f"Otrzymujesz {zad['nagroda_xp']} XP i {zad['nagroda_zloto']} złota.") #
            self.player.reputacja[zad["zleceniodawca_wioska"]] = self.player.reputacja.get(zad["zleceniodawca_wioska"],0) + 5 #
            self.aktywne_zadanie = None #


    async def menu_rozwoju_umiejetnosci(self): # ZMODYFIKOWANE: async
        if self.player.punkty_umiejetnosci_do_wydania <= 0: #
            print("Nie masz punktów umiejętności do rozdysponowania.") #
            return

        while self.player.punkty_umiejetnosci_do_wydania > 0: #
            print(f"\nMasz {self.player.punkty_umiejetnosci_do_wydania} punkt(ów) umiejętności do wydania.") #
            print("Wybierz umiejętność do rozwinięcia:") #
            um_lista = list(self.player.umiejetnosci.keys()) #
            for i, um_nazwa in enumerate(um_lista):
                print(f"{i+1}. {um_nazwa.replace('_',' ').capitalize()} (Poziom: {self.player.umiejetnosci[um_nazwa]})") #
            print("0. Zakończ rozwój na razie") #

            wybor = await async_input("> ") # ZMODYFIKOWANE #
            if not wybor.isdigit(): print("Nieprawidłowy wybór."); continue #
            
            wybor_idx = int(wybor) #
            if wybor_idx == 0: break #
            if 1 <= wybor_idx <= len(um_lista): #
                 wybrana_um = um_lista[wybor_idx-1] #
                 if self.player.umiejetnosci[wybrana_um] < 10: #
                    self.player.umiejetnosci[wybrana_um] += 1 #
                    self.player.punkty_umiejetnosci_do_wydania -= 1 #
                    print(f"Rozwinięto {wybrana_um.replace('_',' ').capitalize()} do poziomu {self.player.umiejetnosci[wybrana_um]}.") #
                    if wybrana_um == "udzwig":
                        self.player.maks_udzwig = self.player.oblicz_maks_udzwig()
                        print(f"Twój maksymalny udźwig wzrósł do {self.player.maks_udzwig:.1f} kg.")
                 else: print(f"{wybrana_um.replace('_',' ').capitalize()} osiągnęła już maksymalny poziom (10).") #
            else: print("Nieprawidłowy numer umiejętności.") #
        print("Zakończono rozwój umiejętności.") #

    async def kup_towary_handlowe_w_wiosce(self, wioska_obj): # ZMODYFIKOWANE: async
        print(wioska_obj.get_village_goods_info_str(self.player.umiejetnosci["charyzma_handel"]))
        
        while True:
            print("Wybierz towar do kupienia (lub wpisz '0' aby wyjść):")
            for i, towar_nazwa in enumerate(LISTA_PRODUKTOW_HANDLOWYCH):
                print(f"  {i+1}. {towar_nazwa}")
            
            wybor_towar_idx_str = await async_input("> ") # ZMODYFIKOWANE
            if not wybor_towar_idx_str.isdigit():
                print("Nieprawidłowy wybór, podaj numer.")
                continue
            wybor_towar_idx = int(wybor_towar_idx_str)

            if wybor_towar_idx == 0: return
            if not (1 <= wybor_towar_idx <= len(LISTA_PRODUKTOW_HANDLOWYCH)):
                print("Nieprawidłowy numer towaru.")
                continue
            
            wybrany_towar = LISTA_PRODUKTOW_HANDLOWYCH[wybor_towar_idx-1]
            
            mnoznik_zakupu = max(0.7, 1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03)
            cena_jednostkowa = max(1, int(wioska_obj.ceny_produktow_finalne[wybrany_towar]["kupno_od_wioski"] * mnoznik_zakupu))
            waga_jednostkowa = PRODUKTY_HANDLOWE_INFO[wybrany_towar]["waga"]

            print(f"Wybrałeś: {wybrany_towar}. Cena za sztukę: {cena_jednostkowa} zł. Waga za sztukę: {waga_jednostkowa} kg.")
            print(f"Twoje złoto: {self.player.inventory['zloto']}. Wolny udźwig: {self.player.maks_udzwig - self.player.aktualny_udzwig:.1f} kg.")

            ilosc_str = await async_input("Ile sztuk chcesz kupić? (0 aby anulować) > ") # ZMODYFIKOWANE
            if not ilosc_str.isdigit():
                print("Nieprawidłowa ilość.")
                continue
            ilosc = int(ilosc_str)
            if ilosc == 0: continue
            if ilosc < 0:
                print("Ilość nie może być ujemna.")
                continue

            koszt_calkowity = ilosc * cena_jednostkowa
            # waga_calkowita = ilosc * waga_jednostkowa # Niepotrzebne, zmien_towar_handlowy to obsłuży

            if self.player.inventory["zloto"] < koszt_calkowity:
                print(f"Nie masz wystarczająco złota. Potrzebujesz {koszt_calkowity}, masz {self.player.inventory['zloto']}.")
                continue
            
            if self.player.zmien_towar_handlowy(wybrany_towar, ilosc):
                self.player.inventory["zloto"] -= koszt_calkowity
                print(f"Kupiłeś {ilosc} szt. '{wybrany_towar.lower()}' za {koszt_calkowity} zł.")
                await self.player.uplyw_czasu(0.5, "handel towarami") # ZMODYFIKOWANE
                return 

    async def sprzedaj_towary_handlowe_w_wiosce(self, wioska_obj): # ZMODYFIKOWANE: async
        print(wioska_obj.get_village_goods_info_str(self.player.umiejetnosci["charyzma_handel"]))
        
        print("\nTwoje towary handlowe na sprzedaż:")
        dostepne_do_sprzedazy = []
        for i, (towar_nazwa, ilosc) in enumerate(self.player.inventory_towary_handlowe.items()):
            if ilosc > 0:
                dostepne_do_sprzedazy.append(towar_nazwa)
                print(f"  {len(dostepne_do_sprzedazy)}. {towar_nazwa} (Masz: {ilosc})")
        
        if not dostepne_do_sprzedazy:
            print("Nie masz żadnych towarów handlowych na sprzedaż.")
            return

        print("Wybierz towar do sprzedania (lub wpisz '0' aby wyjść):")
        wybor_towar_idx_str = await async_input("> ") # ZMODYFIKOWANE
        if not wybor_towar_idx_str.isdigit():
            print("Nieprawidłowy wybór, podaj numer.")
            return
        wybor_towar_idx = int(wybor_towar_idx_str)

        if wybor_towar_idx == 0: return
        if not (1 <= wybor_towar_idx <= len(dostepne_do_sprzedazy)):
            print("Nieprawidłowy numer towaru.")
            return
            
        wybrany_towar = dostepne_do_sprzedazy[wybor_towar_idx-1]
        
        mnoznik_sprzedazy = 1.0 
        cena_jednostkowa = max(1, int(wioska_obj.ceny_produktow_finalne[wybrany_towar]["sprzedaz_do_wioski"] * mnoznik_sprzedazy))
        
        print(f"Wybrałeś: {wybrany_towar}. Wioska oferuje: {cena_jednostkowa} zł za sztukę.")
        print(f"Masz {self.player.inventory_towary_handlowe[wybrany_towar]} szt. tego towaru.")

        ilosc_str = await async_input(f"Ile sztuk '{wybrany_towar.lower()}' chcesz sprzedać? (0 aby anulować) > ") # ZMODYFIKOWANE
        if not ilosc_str.isdigit():
            print("Nieprawidłowa ilość.")
            return
        ilosc_do_sprzedania = int(ilosc_str)

        if ilosc_do_sprzedania == 0: return
        if ilosc_do_sprzedania < 0:
            print("Ilość nie może być ujemna.")
            return
        if ilosc_do_sprzedania > self.player.inventory_towary_handlowe[wybrany_towar]:
            print(f"Nie masz tylu sztuk. Masz {self.player.inventory_towary_handlowe[wybrany_towar]}.")
            return

        if self.player.zmien_towar_handlowy(wybrany_towar, -ilosc_do_sprzedania):
            zysk_calkowity = ilosc_do_sprzedania * cena_jednostkowa
            self.player.inventory["zloto"] += zysk_calkowity
            print(f"Sprzedałeś {ilosc_do_sprzedania} szt. '{wybrany_towar.lower()}' za {zysk_calkowity} zł.")
            await self.player.uplyw_czasu(0.5, "handel towarami") # ZMODYFIKOWANE

    async def petla_wioski(self): # ZMODYFIKOWANE: async
        self.nazwa_aktualnej_wioski = self.player.lokacja_gracza #
        if self.nazwa_aktualnej_wioski not in self.player.reputacja: #
            self.player.reputacja[self.nazwa_aktualnej_wioski] = 0 #
        
        if self.nazwa_aktualnej_wioski not in self.wioski_info:
            self.wioski_info[self.nazwa_aktualnej_wioski] = Village(self.nazwa_aktualnej_wioski)
            print(f"\nPrzybywasz do wioski {self.nazwa_aktualnej_wioski} po raz pierwszy. Rozglądasz się po jej rynku...")
        aktualna_wioska_obj = self.wioski_info[self.nazwa_aktualnej_wioski]

        self.player.ma_ogien = False; self.player.ma_schronienie = False  #
        print(f"\n--- Jesteś w osadzie: {self.nazwa_aktualnej_wioski} ---") #
        print("Możesz tu odpocząć, uzupełnić zapasy i przygotować się do dalszej drogi.") #
        
        self.player.zmien_potrzebe("wytrzymalosc", 2.0, cicho=True) #
        self.player.zmien_potrzebe("komfort_psychiczny", 1.0, cicho=True) #
        print("Gościna w wiosce przynosi chwilę wytchnienia.") #

        if not self.aktywne_zadanie and random.random() < 0.6 + (self.player.reputacja.get(self.nazwa_aktualnej_wioski,0) * 0.01): #
            await self.generuj_zadanie() # ZMODYFIKOWANE #
        
        while True:
            await asyncio.sleep(0.02)  # ZMODYFIKOWANE, krótszy sen dla responsywności #
            self.player.oblicz_aktualny_udzwig() 
            print(self.player) #
            if self.aktywne_zadanie:
                zad_opis = self.aktywne_zadanie['opis'] #
                zad_progres = "" #
                if 'cel_ilosc' in self.aktywne_zadanie: #
                    zad_progres = f" (Postęp: {self.aktywne_zadanie.get('postep','N/A')}/{self.aktywne_zadanie.get('cel_ilosc','N/A')})" #
                elif 'cel_lokacja' in self.aktywne_zadanie and self.aktywne_zadanie.get('postep') == 1: #
                    zad_progres = " (Gotowe do zdania raportu)" #
                print(f"Aktywne zadanie: {zad_opis}{zad_progres}") #


            print("\nCo chcesz zrobić w wiosce?")
            print("1. Odpocznij dobrze w chacie") #
            print("2. Zjedz ciepły posiłek w karczmie") #
            print("3. Napij się wody/naparu ziołowego") #
            print("4. Kupuj podstawowe (Jedzenie / Woda / Drewno)") #
            print("5. Odwiedź znachora/kapłana (bonus do umiejętności)") #
            print("6. Sprzedaj cenne znaleziska") #
            print("7. Kupuj towary handlowe") 
            print("8. Sprzedaj towary handlowe") 
            print("9. Rozwiń Umiejętności (jeśli masz punkty)") #
            print("10. Porozmawiaj ze Starszym Wioski (zadania)") #
            print("11. Wyrusz w dzicz") #
            print("0. Zakończ grę") #

            wybor = await async_input("> ") # ZMODYFIKOWANE #

            if wybor == "1":
                if self.player.inventory["jedzenie"] > 0: #
                    self.player.inventory["jedzenie"] -=1 #
                    print("Postanawiasz solidnie odpocząć.") #
                    await self.player.odpocznij(godziny=8, jakosc_snu_mod=3, koszt_czasu=True, w_wiosce=True) # ZMODYFIKOWANE #
                else:
                    print("Nie masz jedzenia na posiłek. Odpoczniesz gorzej.") #
                    await self.player.odpocznij(godziny=6, jakosc_snu_mod=2, koszt_czasu=True, w_wiosce=True) # ZMODYFIKOWANE #
            elif wybor == "2": 
                koszt_posilku = max(1, int(4 * (1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03))) #
                if self.player.inventory["zloto"] >= koszt_posilku: #
                    self.player.inventory["zloto"] -= koszt_posilku #
                    self.player.zmien_potrzebe("glod_pragnienie", 5.0); self.player.zmien_potrzebe("komfort_psychiczny", 1.0) #
                    print(f"Zjadasz pożywny, ciepły posiłek w karczmie za {koszt_posilku} złota.") #
                    await self.player.uplyw_czasu(1, "posiłek w karczmie") # ZMODYFIKOWANE #
                else: print(f"Nie stać cię na posiłek (koszt: {koszt_posilku} złota).") #
            elif wybor == "3": 
                koszt_napitku = max(1, int(2 * (1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03))) #
                if self.player.inventory["zloto"] >= koszt_napitku: #
                    self.player.inventory["zloto"] -= koszt_napitku #
                    self.player.zmien_potrzebe("glod_pragnienie", 3.0) #
                    print(f"Wypijasz kubek naparu ziołowego za {koszt_napitku} złota.") #
                    await self.player.uplyw_czasu(0.5, "napitek w karczmie") # ZMODYFIKOWANE #
                else: print(f"Nie masz złota na napitek (koszt: {koszt_napitku} złota).") #
            elif wybor == "4":
                    
                    print("Co chcesz kupić?")
                    print(f"  a. Jedzenie (Cena bazowa: 3 złota)")
                    print(f"  b. Woda (Cena bazowa: 2 złota)")
                    print(f"  c. Drewno (Cena bazowa: 1 złoto)")
                    print("  0. Anuluj")
                    wybor_zakup = await async_input("Twój wybór: ")
                    wybor_zakup = wybor_zakup.strip().lower()
                
                    # Zniżka z charyzmy: im większa umiejętność "charyzma_handel", tym mniejsza cena
                    znizka_charyzma = (1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03)
                
                    if wybor_zakup == 'a':
                        # Jedzenie: bazowa cena 3 złota
                        unit_price = max(1, int(3 * znizka_charyzma))
                        qty_input = await async_input("Ile porcji jedzenia chcesz kupić? ")
                        try:
                            ilosc = int(qty_input)
                            if ilosc <= 0:
                                print("Niepoprawna ilość (musi być > 0).")
                            else:
                                koszt_calkowity = unit_price * ilosc
                                if self.player.inventory["zloto"] >= koszt_calkowity:
                                    self.player.inventory["jedzenie"] += ilosc
                                    self.player.inventory["zloto"] -= koszt_calkowity
                                    print(f"Kupujesz {ilosc} porcji jedzenia za {koszt_calkowity} złota ({unit_price} złota za sztukę).")
                                else:
                                    print(f"Nie masz wystarczająco złota (potrzebujesz {koszt_calkowity}).")
                        except ValueError:
                            print("Niepoprawny format liczby. Wprowadź liczbę całkowitą.")
                
                    elif wybor_zakup == 'b':
                        # Woda: bazowa cena 2 złota
                        unit_price = max(1, int(2 * znizka_charyzma))
                        qty_input = await async_input("Ile bukłaków wody chcesz kupić? ")
                        try:
                            ilosc = int(qty_input)
                            if ilosc <= 0:
                                print("Niepoprawna ilość (musi być > 0).")
                            else:
                                koszt_calkowity = unit_price * ilosc
                                if self.player.inventory["zloto"] >= koszt_calkowity:
                                    self.player.inventory["woda"] += ilosc
                                    self.player.inventory["zloto"] -= koszt_calkowity
                                    print(f"Kupujesz {ilosc} bukłaków wody za {koszt_calkowity} złota ({unit_price} złota za sztukę).")
                                else:
                                    print(f"Nie masz wystarczająco złota (potrzebujesz {koszt_calkowity}).")
                        except ValueError:
                            print("Niepoprawny format liczby. Wprowadź liczbę całkowitą.")
                
                    elif wybor_zakup == 'c':
                        # Drewno: bazowa cena 1 złota
                        unit_price = max(1, int(1 * znizka_charyzma))
                        qty_input = await async_input("Ile wiązek drewna chcesz kupić? ")
                        try:
                            ilosc = int(qty_input)
                            if ilosc <= 0:
                                print("Niepoprawna ilość (musi być > 0).")
                            else:
                                koszt_calkowity = unit_price * ilosc
                                if self.player.inventory["zloto"] >= koszt_calkowity:
                                    self.player.inventory["drewno"] += ilosc
                                    self.player.inventory["zloto"] -= koszt_calkowity
                                    print(f"Kupujesz {ilosc} wiązek drewna za {koszt_calkowity} złota ({unit_price} złota za sztukę).")
                                else:
                                    print(f"Nie masz wystarczająco złota (potrzebujesz {koszt_calkowity}).")
                        except ValueError:
                            print("Niepoprawny format liczby. Wprowadź liczbę całkowitą.")
                
                    elif wybor_zakup == '0':
                        print("Anulowano zakup.")
                    else:
                        print("Nieznana opcja zakupu.")
            #elif wybor == "4": 
#                print("Co chcesz kupić?") #
#                print(f"  a. Jedzenie (Cena bazowa: 3 złota)") #
#                print(f"  b. Woda (Cena bazowa: 2 złota)") #
#                print(f"  c. Drewno (Cena: 1 złoto)") #
#                print("  0. Anuluj") #
#                wybor_zakup = await async_input("Twój wybór: ") # ZMODYFIKOWANE #
#                wybor_zakup = wybor_zakup.strip().lower()
#                znizka_charyzma = (1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03) #
#                if wybor_zakup == 'a': #
#                    koszt = max(1, int(3 * znizka_charyzma)) #
#                    if self.player.inventory["zloto"] >= koszt :  #
#                        self.player.inventory["jedzenie"] += 1; self.player.inventory["zloto"] -= koszt #
#                        print(f"Kupujesz rację pożywnej strawy za {koszt} złota.") #
#                    else: print(f"Nie masz wystarczająco złota (potrzebujesz {koszt}).") #
#                elif wybor_zakup == 'b':
#                    koszt = max(1, int(2 * znizka_charyzma)) #
#                    if self.player.inventory["zloto"] >= koszt: #
#                        self.player.inventory["woda"] += 1; self.player.inventory["zloto"] -= koszt #
#                        print(f"Kupujesz bukłak czystej wody za {koszt} złota.") #
#                    else: print(f"Nie masz wystarczająco złota (potrzebujesz {koszt}).") #
#                elif wybor_zakup == 'c':
#                    if self.player.inventory["zloto"] >= 1:  #
#                        self.player.inventory["drewno"] += 1; self.player.inventory["zloto"] -=1 #
#                        print("Kupujesz wiązkę suchego drewna za 1 złoto.") #
#                    else: print("Nie masz wystarczająco złota.") #
            elif wybor == "5": 
                if self.player.inventory["zloto"] >= 5: #
                    self.player.inventory["zloto"] -= 5; #
                    print("Składasz drobną ofiarę znachorowi...") #
                    await self.player.uplyw_czasu(2, "wizyta u znachora") # ZMODYFIKOWANE #
                    if random.random() < 0.6:  #
                        bonus_val = self.rzut_koscia(2) +1; self.player.przyznaj_bonus_umiejetnosci(bonus_val, "Błogosławieństwo Starszyzny") #
                        self.player.zmien_potrzebe("komfort_psychiczny", 1.0) #
                    else: print("Znachor mamrocze coś pod nosem...") #
                else: print("Nie masz wystarczająco złota na dary/opłatę.") #
            elif wybor == "6": await self.sprzedaj_cenne_przedmioty() # ZMODYFIKOWANE #
            elif wybor == "7": await self.kup_towary_handlowe_w_wiosce(aktualna_wioska_obj) # ZMODYFIKOWANE
            elif wybor == "8": await self.sprzedaj_towary_handlowe_w_wiosce(aktualna_wioska_obj) # ZMODYFIKOWANE
            elif wybor == "9": await self.menu_rozwoju_umiejetnosci() # ZMODYFIKOWANE #
            elif wybor == "10": 
                if self.aktywne_zadanie and self.aktywne_zadanie["zleceniodawca_wioska"] == self.nazwa_aktualnej_wioski: #
                    zad = self.aktywne_zadanie #
                    print(f"Starszy pyta o postępy w zadaniu: {zad['opis']}") #
                    if zad.get("typ") == "zbadaj_miejsce" and zad.get("postep") == 1: #
                        print("Zdajesz Starszemu raport z wyprawy.") #
                        await self.player.dodaj_xp(zad["nagroda_xp"]) # ZMODYFIKOWANE #
                        self.player.inventory["zloto"] += zad["nagroda_zloto"] #
                        print(f"Otrzymujesz {zad['nagroda_xp']} XP i {zad['nagroda_zloto']} złota.") #
                        self.player.reputacja[self.nazwa_aktualnej_wioski] = self.player.reputacja.get(self.nazwa_aktualnej_wioski,0) + 10 #
                        self.aktywne_zadanie = None #
                    elif "cel_ilosc" in zad and zad["postep"] >= zad["cel_ilosc"]: #
                         print("Starszy dziękuje za wykonanie zadania (już nagrodzone).") #
                         self.aktywne_zadanie = None #
                    else:
                         print("Starszy zachęca do kontynuowania zadania.") #
                elif not self.aktywne_zadanie: #
                    print("Starszy Wioski wita Cię.") #
                    if random.random() < 0.7 + (self.player.reputacja.get(self.nazwa_aktualnej_wioski,0) * 0.01): #
                        await self.generuj_zadanie() # ZMODYFIKOWANE #
                    else:
                        print("Wygląda na to, że Starszy nie ma dla Ciebie obecnie żadnego zadania.") #
                else: 
                       print(f"Starszy z {self.nazwa_aktualnej_wioski} nie ma dla Ciebie zadania. Pamiętaj o zadaniu z {self.aktywne_zadanie['zleceniodawca_wioska']}.") #

            elif wybor == "11": 
                if self.player.wytrzymalosc <= 3.0 or self.player.glod_pragnienie <=3.0: #
                    print("Jesteś zbyt wyczerpany lub głodny/spragniony.") #
                else: 
                    self.lokacje_w_aktualnym_etapie = 0
                    # petla_eksploracji jest teraz async, więc nie można jej bezpośrednio zwrócić
                    # Zamiast tego, sygnalizujemy, że chcemy przejść do eksploracji
                    return "rozpocznij_eksploracje" # (zmodyfikowana obsługa)
            elif wybor == "0":  #
                print("Dziękujemy za grę!"); return "koniec_gry" #
            else: print("Nieznana komenda.") #

            if await self.sprawdz_stan_krytyczny("wioska"): return "koniec_gry" # ZMODYFIKOWANE #
        return "kontynuuj" # Powinno być nieosiągalne, chyba że pętla jakoś inaczej się zakończy

    async def sprzedaj_cenne_przedmioty(self): # ZMODYFIKOWANE: async
        print("\n--- Targowisko - Sprzedaż Cennych Przedmiotów ---") #
        if not any(self.player.inventory_cenne.values()): #
            print("Nie masz żadnych cennych przedmiotów na sprzedaż."); return #

        print("Dostępne przedmioty na sprzedaż:") #
        przedmioty_na_sprzedaz_lista = [] #
        for item, qty in self.player.inventory_cenne.items(): #
            if qty > 0: #
                przedmioty_na_sprzedaz_lista.append(item) #
                cena_bazowa = CENNE_PRZEDMIOTY_CENY.get(item, 0) #
                mnoznik_ceny = (1.0 + self.player.umiejetnosci["charyzma_handel"] * 0.03) #
                cena_zmodyfikowana = int(cena_bazowa * mnoznik_ceny) #
                print(f"{len(przedmioty_na_sprzedaz_lista)}. {item.replace('_',' ').capitalize()} (Ilość: {qty}, Cena za sztukę: ~{cena_zmodyfikowana} złota)") #
        print("0. Anuluj") #

        while True:
            wybor_sprzedaz = await async_input("Wybierz przedmiot do sprzedaży (numer) lub 0, aby anulować: ") # ZMODYFIKOWANE #
            if not wybor_sprzedaz.isdigit(): print("Podaj numer."); continue #
            wybor_idx = int(wybor_sprzedaz) #
            if wybor_idx == 0: return #
            if 1 <= wybor_idx <= len(przedmioty_na_sprzedaz_lista): #
                item_nazwa = przedmioty_na_sprzedaz_lista[wybor_idx-1] #
                item_qty = self.player.inventory_cenne[item_nazwa] #
                while True:
                    ile_sprzedac_str = await async_input(f"Ile sztuk {item_nazwa.replace('_',' ')} chcesz sprzedać (masz {item_qty}, 0 - anuluj)? ") # ZMODYFIKOWANE #
                    if not ile_sprzedac_str.isdigit(): print("Podaj liczbę."); continue #
                    ile_sprzedac = int(ile_sprzedac_str) #
                    if ile_sprzedac == 0: break #
                    if 0 < ile_sprzedac <= item_qty: #
                        cena_bazowa = CENNE_PRZEDMIOTY_CENY.get(item_nazwa, 0) #
                        mnoznik_ceny = (1.0 + self.player.umiejetnosci["charyzma_handel"] * 0.03) #
                        cena_finalna_szt = max(1, int(cena_bazowa * random.uniform(0.85, 1.15) * mnoznik_ceny)) #
                        suma_zlota = ile_sprzedac * cena_finalna_szt #
                        self.player.inventory_cenne[item_nazwa] -= ile_sprzedac #
                        self.player.inventory["zloto"] += suma_zlota #
                        print(f"Sprzedałeś {ile_sprzedac} szt. {item_nazwa.replace('_',' ')} za {suma_zlota} złota ({cena_finalna_szt} za sztukę).") #
                        await self.player.uplyw_czasu(0.5, "handel na targu"); return  # ZMODYFIKOWANE #
                    else: print(f"Nieprawidłowa ilość. Masz {item_qty} sztuk.") #
                break 
            else: print("Nieprawidłowy numer przedmiotu.") #


    async def petla_eksploracji(self):
        self.player.lokacja_gracza = "Dzicz"
        print("\n--- Wyruszasz w dzicz... ---")
    
        # 1) Deklarujemy etapy raz, na zewnątrz pętli, zamiast za każdym razem w jej wnętrzu:
        ETAPY_EKSPLORACJI = [
            {"kosci": [10, 8, 6],  "szanse_na_wies": [1]},
            {"kosci": [8, 10, 12], "szanse_na_wies": [1, 2, 3]},
            {"kosci": [10, 8, 6],  "szanse_na_wies": [1, 2, 3, 4]},
            {"kosci": [8, 10, 12], "szanse_na_wies": [1, 2, 3, 4]},
            {"kosci": [10, 8, 6],  "szanse_na_wies": [1, 2, 3, 4]},
        ]
        max_etap_idx = len(ETAPY_EKSPLORACJI) - 1
    
        while True:
            await asyncio.sleep(0.02)
            if await self.sprawdz_stan_krytyczny("dzicz"):
                return "koniec_gry"
    
            print(
                f"\n--- Dzień {int(self.player.dni_w_podrozy) + 1} "
                f"(Etap dziczy: {self.aktualny_etap_eksploracji_idx + 1}, "
                f"Lokacja: {self.lokacje_w_aktualnym_etapie + 1}/{self.max_lokacji_na_etap}) ---"
            )
    
            # 2) Pobieramy właściwy słownik-etap na podstawie indeksu (zabezpieczamy przed wyjściem poza zakres)
            etap_idx = min(self.aktualny_etap_eksploracji_idx, max_etap_idx)
            etap = ETAPY_EKSPLORACJI[etap_idx]
            kosci_etapu = etap["kosci"]
            nr_w_kroku = self.lokacje_w_aktualnym_etapie % len(kosci_etapu)
            glowna_kosc_eksploracji = kosci_etapu[nr_w_kroku]
            #glowna_kosc_eksploracji = kosci_etapu[0]
    
            modyfikator_gracza = self.player.oblicz_modyfikator_rzutu()
            print(self.player)
            print("nr w kroku ", nr_w_kroku)
            #print(f"Twój modyfikator do rzutu eksploracji (z potrzeb): {modyfikator_gracza}")
            print(f"Rzucasz K{glowna_kosc_eksploracji} w poszukiwaniu drogi ...")
            await asyncio.sleep(0.03)
    
            wynik_rzutu_eksploracji = self.rzut_koscia(glowna_kosc_eksploracji) #+ modyfikator_gracza
            wynik_rzutu_eksploracji = max(1, wynik_rzutu_eksploracji)
            print(f"Wynik rzutu: {wynik_rzutu_eksploracji} (na K{glowna_kosc_eksploracji})")
    
            # Koszt wytrzymałości podróży
            koszt_wytrzymalosci_podrozy = (self.rzut_koscia(2)+1) * (
                1.0 - self.player.umiejetnosci["przetrwanie"] * 0.05
            )
            koszt_wytrzymalosci_podrozy = max(0.5, koszt_wytrzymalosci_podrozy)
            self.player.zmien_potrzebe("wytrzymalosc", -koszt_wytrzymalosci_podrozy, cicho=True)
    
            await self.player.uplyw_czasu(self.rzut_koscia(2) + 2, "poszukiwanie drogi")
    
            # 3) Przechodzimy przez kolejne lokacje w danym etapie
            self.lokacje_w_aktualnym_etapie += 1
            if self.lokacje_w_aktualnym_etapie >= self.max_lokacji_na_etap:
                # ZAMIANA: sprawdzamy względem ETAPY_EKSPLORACJI (nie ETAPY_EKSPLORACJI_KOSCI)
                if self.aktualny_etap_eksploracji_idx < max_etap_idx:
                    self.aktualny_etap_eksploracji_idx += 1
                else:
                    print("Zapuszczasz się w najgłębsze ostępy dziczy...")
                self.lokacje_w_aktualnym_etapie = 0
                print(
                    f"Wkraczasz w nowy, głębszy rejon dziczy "
                    f"(Etap {self.aktualny_etap_eksploracji_idx + 1})."
                )
    
            # 4) Sprawdzamy, czy trafiamy na wieś zgodnie z listą progów dla etapu
            if wynik_rzutu_eksploracji in etap["szanse_na_wies"]:
                print("Niespodziewanie trafiasz na ślady prowadzące do ludzkiej osady!")
                nowa_nazwa_wioski = f"OsadaNadRzeką{Game.rzut_koscia(100)}"
                if nowa_nazwa_wioski not in self.wioski_info:
                    self.wioski_info[nowa_nazwa_wioski] = Village(nowa_nazwa_wioski)
                    print(f"Odkryłeś nową, niezbadaną osadę: {nowa_nazwa_wioski}!")
                else:
                    print(f"Droga prowadzi Cię do znanej osady: {nowa_nazwa_wioski}.")
    
                self.player.lokacja_gracza = nowa_nazwa_wioski
                zloto_znalezione = self.rzut_koscia(6) + self.rzut_koscia(6)
                self.player.inventory["zloto"] += zloto_znalezione
                print(f"Po drodze znajdujesz {zloto_znalezione} sztuk złota.")
                await self.player.dodaj_xp(50 + self.aktualny_etap_eksploracji_idx * 10)
                return "znaleziono_wioske"
    
            # 5) Jeśli nie wieś, to sprawdzamy, czy trafiamy na „obszar pozytywny”
            prog_pozytywny = max(10, int(glowna_kosc_eksploracji * 0.70))
            if wynik_rzutu_eksploracji >= prog_pozytywny:
                print("Odkrywasz szczególnie interesujący lub przyjazny obszar!")
                await self.obsluz_obszar_pozytywny()
            else:
                # Obszar „standardowy” w dziczy
                dostepne_obszary = [
                    nazwa for nazwa, dane in OBSZARY_DZICZY.items() if not dane.get("pozytywny")
                ]
                if not dostepne_obszary:
                    dostepne_obszary = list(OBSZARY_DZICZY.keys())
                nazwa_obszaru = random.choice(dostepne_obszary)
                self.player.lokacja_gracza = nazwa_obszaru
                await self.przyznaj_xp_za_odkrycie_obszaru(nazwa_obszaru)
                await self.obsluz_obszar_dziczy(nazwa_obszaru)
    
            # 6) Jeśli gracz ma zadanie „zbadaj_miejsce”, raportujemy mu postęp
            if self.aktywne_zadanie and self.aktywne_zadanie["typ"] == "zbadaj_miejsce":
                await self.sprawdz_postep_zadania(
                    "zbadano_lokacje",
                    dodatkowe_dane={"nazwa_lokacji": self.player.lokacja_gracza},
                )
    
            # 7) Inne akcje w dziczy (ogniska, schronienia itd.)
            akcja_status = await self.akcje_w_dziczy()
            if akcja_status == "koniec_gry":
                return "koniec_gry"
    
            if self.player.ma_ogien and random.random() < 0.4:
                self.player.ma_ogien = False
                self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
                print("Twój ogień przygasł i ostatecznie zgasł...")
            if self.player.ma_schronienie and random.random() < 0.15:
                self.player.ma_schronienie = False
                self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
                print("Twoje schronienie zostało uszkodzone.")
    async def obsluz_obszar_pozytywny(self): # ZMODYFIKOWANE: async
        pozytywne_obszary = [nazwa for nazwa, dane in OBSZARY_DZICZY.items() if dane.get("pozytywny")] #
        if not pozytywne_obszary: 
            nazwa_obszaru = random.choice(list(OBSZARY_DZICZY.keys()))
            await self.obsluz_obszar_dziczy(nazwa_obszaru); return # ZMODYFIKOWANE #
        nazwa_obszaru = random.choice(pozytywne_obszary) #
        self.player.lokacja_gracza = nazwa_obszaru  #
        await self.przyznaj_xp_za_odkrycie_obszaru(nazwa_obszaru) # ZMODYFIKOWANE #
        obszar = OBSZARY_DZICZY[nazwa_obszaru] #
        print(f"\nWchodzisz na obszar: {nazwa_obszaru}. {obszar['opis']}"); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
        await async_input("Naciśnij Enter, aby kontynuować...")
        for potrzeba, bonus in obszar.get("bonusy_przy_wejsciu", {}).items(): self.player.zmien_potrzebe(potrzeba, bonus) #
        await self.przeszukaj_obszar_dokladnie(obszar, kontekst="przybycie_pozytywny") # ZMODYFIKOWANE #
        await self.losowe_wydarzenie_pozytywne(obszar) # ZMODYFIKOWANE #

    async def obsluz_obszar_dziczy(self, nazwa_obszaru): # ZMODYFIKOWANE: async
        obszar = OBSZARY_DZICZY[nazwa_obszaru] #
        print(f"\nWchodzisz na obszar: {nazwa_obszaru}. {obszar['opis']}"); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
        await async_input("Naciśnij Enter, aby kontynuować...")
        for potrzeba, kara in obszar.get("kary_przy_wejsciu", {}).items(): self.player.zmien_potrzebe(potrzeba, kara) #
        await self.przeszukaj_obszar_dokladnie(obszar, kontekst="przybycie_negatywny") # ZMODYFIKOWANE #
        await self.losowe_wydarzenie_negatywne(obszar) # ZMODYFIKOWANE #
        
    async def przeszukaj_obszar_dokladnie(self, obszar_dane, kontekst=""): # ZMODYFIKOWANE: async
        if kontekst == "akcja_gracza": #
            print("Postanawiasz dokładnie przeszukać okolicę...") #
            czas_na_przeszukiwanie = self.rzut_koscia(2) + 2  #
            await self.player.uplyw_czasu(czas_na_przeszukiwanie, "dokładne przeszukiwanie") # ZMODYFIKOWANE #
            self.player.zmien_potrzebe("wytrzymalosc", - (czas_na_przeszukiwanie / (1.5 + self.player.umiejetnosci["przetrwanie"]*0.1) ))  #
            szansa_modyfikator = 1.0  #
        else: 
            print("Rozglądasz się pobieżnie po okolicy...") #
            szansa_modyfikator = 0.5  #
        
        znaleziono_cos = False; bonus_um_sytuacyjny = 0  #
        if kontekst == "akcja_gracza": bonus_um_sytuacyjny = self.player.uzyj_bonusu_umiejetnosci() #
        bonus_um_zielarstwo = self.player.umiejetnosci["zielarstwo_tropienie"] * 0.05  #

        for zasob_nazwa, (max_ilosc_tuple_val, szansa_znalezienia) in obszar_dane.get("zasoby", {}).items(): #
            max_ilosc = max_ilosc_tuple_val if isinstance(max_ilosc_tuple_val, (int, float)) else 1 #
            rzut_szansy = random.random() #
            if rzut_szansy < (szansa_znalezienia + bonus_um_zielarstwo) * szansa_modyfikator + (bonus_um_sytuacyjny * 0.05): #
                ilosc_mnoznik = 1.0 + (self.player.umiejetnosci["zielarstwo_tropienie"] * 0.05)  #
                ilosc_bazowa = self.rzut_koscia(int(max_ilosc)) if max_ilosc >= 1 else (1 if random.random() < max_ilosc else 0) #
                ilosc = int(ilosc_bazowa * ilosc_mnoznik); ilosc = max(1, ilosc) if ilosc_bazowa > 0 and ilosc == 0 else ilosc #
                if ilosc > 0: #
                    znaleziono_cos = True #
                    if "drewno" in zasob_nazwa: self.player.inventory["drewno"] += ilosc; print(f"Znajdujesz {ilosc} szt. drewna.") #
                    elif "jedzenie" in zasob_nazwa: #
                        self.player.inventory["jedzenie"] += ilosc; print(f"Zbierasz {ilosc} porcji pożywienia ({zasob_nazwa.replace('_',' ')}).") #
                        if "rzadkie_zioło_lecznicze" in zasob_nazwa : await self.sprawdz_postep_zadania("zbierz_ziola", ilosc) # ZMODYFIKOWANE #
                    elif "woda" in zasob_nazwa: #
                        self.player.inventory["woda"] += ilosc; print(f"Napełniasz bukłaki {ilosc} porcjami wody ({zasob_nazwa.replace('_',' ')}).") #
                        if "brudna" in zasob_nazwa: print("Woda wygląda na mętną.") #
                    elif zasob_nazwa in self.player.inventory_cenne:  #
                        self.player.inventory_cenne[zasob_nazwa] += ilosc; print(f"Odkrywasz {ilosc} szt. {zasob_nazwa.replace('_',' ')}!") #
                        if zasob_nazwa == "rzadkie_zioło_lecznicze": await self.sprawdz_postep_zadania("zbierz_ziola", ilosc) # ZMODYFIKOWANE #
                    elif "resztki_narzedzi" in zasob_nazwa: #
                        print(f"Znajdujesz {ilosc} resztek starych narzędzi.") #
                        if random.random() < 0.3: zloto_res = self.rzut_koscia(3); self.player.inventory["zloto"] += zloto_res; print(f"Wśród rupieci znajdujesz {zloto_res} starych monet!") #
        
        if kontekst == "akcja_gracza":  #
            if random.random() < 0.20 + (bonus_um_sytuacyjny * 0.05) + (self.player.umiejetnosci["zielarstwo_tropienie"] * 0.02): 
                await self.spotkanie_ze_zwierzeciem(agresywne=False); znaleziono_cos = True  # ZMODYFIKOWANE #
            if random.random() < 0.15 + (bonus_um_sytuacyjny * 0.03) + (self.player.umiejetnosci["zielarstwo_tropienie"] * 0.01):  #
                print("Twoja uwaga przykuwa coś niezwykłego..."); #
                if random.random() < 0.5 and "fragment_mapy" in self.player.inventory_cenne: 
                    self.player.inventory_cenne["fragment_mapy"] += 1; print("Odkrywasz kolejny fragment starej mapy!")
                    await self.player.dodaj_xp(15) # ZMODYFIKOWANE #
                else: zloto_extra = self.rzut_koscia(5) + 2; self.player.inventory["zloto"] += zloto_extra; print(f"Znajdujesz dobrze ukrytą sakiewkę z {zloto_extra} monetami!") #
                znaleziono_cos = True #
        if not znaleziono_cos and kontekst == "akcja_gracza": print("Niestety, pomimo wysiłków, niczego szczególnego nie udaje ci się znaleźć.") #
        elif not znaleziono_cos and kontekst != "akcja_gracza": print("Nie znajdujesz tu niczego od razu rzucającego się w oczy.") #

    async def losowe_wydarzenie_negatywne(self, obszar): # ZMODYFIKOWANE: async
        wydarzenia_obszaru = obszar.get("wydarzenia_specjalne", []) #
        mozliwe_wydarzenia = ["nic_szczegolnego", "niespodziewany_minus_potrzeby", "drobny_uraz"] + wydarzenia_obszaru #
        wydarzenie = random.choice(mozliwe_wydarzenia); print("\nZdarzenie losowe:"); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
        if wydarzenie == "nic_szczegolnego": print("Wokół panuje względny spokój.") #
        elif wydarzenie == "aura_demonow": print(obszar.get("opis_demonow", "Czujesz mroczną obecność...")); self.player.zmien_potrzebe("komfort_psychiczny", -self.rzut_koscia(3))  #
        elif wydarzenie == "dzikie_zwierze": await self.spotkanie_ze_zwierzeciem(agresywne=True) # ZMODYFIKOWANE #
        elif wydarzenie == "niespodziewany_minus_potrzeby": #
            potrzeba_do_spadku = random.choice(["wytrzymalosc", "glod_pragnienie", "komfort_psychiczny"]); spadek = -self.rzut_koscia(2); self.player.zmien_potrzebe(potrzeba_do_spadku, spadek) #
        elif wydarzenie == "drobny_uraz": print("Potykasz się niefortunnie..."); self.player.zmien_potrzebe("wytrzymalosc", -1.0); self.player.zmien_potrzebe("komfort_psychiczny", -1.0) #
        elif wydarzenie in ["slady_bestii", "poczucie_obserwacji", "odglosy_z_bagien", "szelest_w_krzakach"]: print("Dostrzegasz niepokojące znaki..."); self.player.zmien_potrzebe("komfort_psychiczny", -1.0) #
        elif wydarzenie == "uciqzliwe_insekty": print("Chmary natrętnych, gryzących insektów..."); self.player.zmien_potrzebe("komfort_psychiczny", -self.rzut_koscia(2)); self.player.zmien_potrzebe("wytrzymalosc", -1.0)  #
        elif wydarzenie == "silny_wiatr": print("Zrywa się porywisty, zimny wiatr..."); self.player.zmien_potrzebe("wytrzymalosc", -1.0); (self.player.zmien_potrzebe("komfort_psychiczny", -1.0) if not self.player.ma_schronienie and not self.player.ma_ogien else None) #
        elif wydarzenie == "mgla": print("Gęsta, wilgotna mgła spowija wszystko..."); self.player.zmien_potrzebe("komfort_psychiczny",-1.0); (print("Twój ogień ledwo się tli.") if self.player.ma_ogien else None) #
        elif wydarzenie == "kamienne_kregi": print("Natrafiasz na stary, kamienny krąg..."); self.player.zmien_potrzebe("komfort_psychiczny", -self.rzut_koscia(2)); (print("Przez chwilę masz wrażenie, że kamienie się poruszyły...") or self.player.zmien_potrzebe("komfort_psychiczny", -1.0) if random.random() < 0.2 else None) #
        elif wydarzenie == "znalezisko_w_pogorzelisku": #
            print("Przeszukując zgliszcza, znajdujesz coś, co przetrwało pożar.") #
            if random.random() < 0.3: #
                znalezione_zloto = self.rzut_koscia(6) #
                self.player.inventory["zloto"] += znalezione_zloto #
                print(f"To nadpalona sakiewka, a w niej {znalezione_zloto} monet!") #
            elif random.random() < 0.2 and "fragment_mapy" in self.player.inventory_cenne: #
                 self.player.inventory_cenne["fragment_mapy"] += 1; print("Odkrywasz kolejny, osmalony fragment starej mapy!")
                 await self.player.dodaj_xp(15) # ZMODYFIKOWANE #
            else: #
                print("Niestety, to tylko bezwartościowe, zwęglone resztki.") #
                self.player.zmien_potrzebe("komfort_psychiczny", -0.5) #
        elif wydarzenie == "ekstremalne_temperatury": #
            if random.random() < 0.5: #
                print("Słońce praży niemiłosiernie. Czujesz jak opadasz z sił.") #
                self.player.zmien_potrzebe("wytrzymalosc", -1.5) #
                self.player.zmien_potrzebe("glod_pragnienie", -1.0) #
            else: 
                print("Gdy zapada zmrok, temperatura gwałtownie spada. Trzęsiesz się z zimna.") #
                self.player.zmien_potrzebe("wytrzymalosc", -1.0) #
                self.player.zmien_potrzebe("komfort_psychiczny", -1.0) #
        elif wydarzenie == "burza_piaskowa": #
            print("Zrywa się gwałtowny wiatr, niosąc tumany piasku. Ledwo widzisz przed siebie i z trudem łapiesz oddech.") #
            self.player.zmien_potrzebe("wytrzymalosc", -2.0) #
            self.player.zmien_potrzebe("komfort_psychiczny", -1.5) #
            self.player.zmien_potrzebe("glod_pragnienie", -1.0) #
            if random.random() < 0.2: #
                zgubiony_przedmiot = random.choice(["jedzenie", "woda", "drewno"]) #
                if self.player.inventory[zgubiony_przedmiot] > 0: #
                    self.player.inventory[zgubiony_przedmiot] -= 1 #
                    print(f"Wiatr wyrywa ci z rąk i porywa część zapasów ({zgubiony_przedmiot})!") #
        elif wydarzenie == "poczucie_straty" or wydarzenie == "poczucie_osamotnienia": #
            print("Ogarnia Cię przygnębienie i poczucie beznadziei w tej niegościnnej krainie.") #
            self.player.zmien_potrzebe("komfort_psychiczny", -1.5) #
        await async_input("Naciśnij Enter, aby kontynuować...")


    async def losowe_wydarzenie_pozytywne(self, obszar): # ZMODYFIKOWANE: async
        wydarzenia_obszaru = obszar.get("wydarzenia_specjalne", []); mozliwe_wydarzenia = ["nic_specjalnego_pozytywnego"] + wydarzenia_obszaru #
        wydarzenie = random.choice(mozliwe_wydarzenia); print("\nZdarzenie losowe (pozytywne):"); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
        if wydarzenie == "nic_specjalnego_pozytywnego": print("Cieszysz się chwilą spokoju w tym przyjaznym miejscu.") #
        elif wydarzenie == "znalezisko_ziola_lecznicze": #
             print("Napotykasz kępę rzadkich ziół o znanych ci właściwościach leczniczych lub wzmacniających.") #
             self.player.zmien_potrzebe("wytrzymalosc", self.rzut_koscia(2)+1.0); self.player.zmien_potrzebe("komfort_psychiczny",1.0) #
             if "rzadkie_zioło_lecznicze" in self.player.inventory_cenne: 
                 self.player.inventory_cenne["rzadkie_zioło_lecznicze"] +=1
                 await self.sprawdz_postep_zadania("zbierz_ziola",1) # ZMODYFIKOWANE #
        elif wydarzenie == "chwila_kontemplacji": 
            print("Znajdujesz idealne miejsce na chwilę zadumy. Spokój natury koi Twoje nerwy.")
            self.player.zmien_potrzebe("komfort_psychiczny", self.rzut_koscia(2)+1.0)
            await self.player.dodaj_xp(5) # ZMODYFIKOWANE #
        elif wydarzenie == "przychylnosc_duchow_gaju": 
            print("Czujesz, że duchy opiekuńcze tego miejsca spoglądają na Ciebie łaskawie.")
            self.player.przyznaj_bonus_umiejetnosci(self.rzut_koscia(2)+1, "Przychylność Duchów Gaju")
            self.player.zmien_potrzebe("komfort_psychiczny",1.0)
            await self.player.dodaj_xp(10) # ZMODYFIKOWANE #
        elif wydarzenie == "niepokojace_znalezisko_w_chacie":  #
            print("W kącie chaty znajdujesz stare, podarte zapiski lub niepokojący rysunek..."); self.player.zmien_potrzebe("komfort_psychiczny", -1.0) #
            if random.random() < 0.2 and "fragment_mapy" in self.player.inventory_cenne: 
                self.player.inventory_cenne["fragment_mapy"] += 1; print("Wśród zapisków znajdujesz dziwny fragment mapy!")
                await self.player.dodaj_xp(15) # ZMODYFIKOWANE #
        elif wydarzenie == "schronienie_przed_deszczem": print("Nagle zaczyna padać ulewny deszcz. Na szczęście znajdujesz schronienie w samą porę."); self.player.zmien_potrzebe("komfort_psychiczny",1.0) #
        elif wydarzenie == "slady_walki":  #
            print("Odnajdujesz ślady niedawnej walki. Ktoś tu był przed Tobą..."); #
            if random.random() < 0.3: zloto = self.rzut_koscia(4); self.player.inventory["zloto"] += zloto; print(f"Przy szczątkach znajdujesz {zloto} sztuk złota!") #
            await async_input("Naciśnij Enter, aby kontynuować...")

    async def spotkanie_ze_zwierzeciem(self, agresywne=False): # ZMODYFIKOWANE: async
        lista_zwierzat = {
            "wilk": (5, 2, 5, True, 2, 10), "dzik": (7, 3, 4, True, 3, 15), 
            "niedźwiedź": (12, 4, 3, True, 5, 30), "jeleń": (4, 1, 8, False, 3, 5),
            "lis": (3,1,7,False,1, 3), "borsuk": (4, 2, 6, True, 1, 8) 
        } #
        nazwa_zwierzecia = random.choice(list(lista_zwierzat.keys())) #
        hp_przeciwnika, atak_przeciwnika, ucieczka_gracza_próg, agresywne_z_natury, jedzenie_drop, xp_za_pokonanie = lista_zwierzat[nazwa_zwierzecia] #
        if agresywne: agresywne_z_natury = True #
        print(f"Na twojej drodze staje {nazwa_zwierzecia}!"); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
        if not agresywne_z_natury and random.random() < 0.6: 
            print(f"{nazwa_zwierzecia.capitalize()} odchodzi.")
            await self.player.uplyw_czasu(0.5, "obserwacja") # ZMODYFIKOWANE #
            return 
        print(f"{nazwa_zwierzecia.capitalize()} wygląda na niespokojne" + (" i gotowe do ataku!" if agresywne_z_natury else ".")) #
        while True:
            decyzja = await async_input(f"Co robisz? (walcz / spróbuj_odstraszyć / uciekaj / obserwuj) > ") # ZMODYFIKOWANE #
            decyzja = decyzja.lower().strip()
            if decyzja in ["walcz", "spróbuj_odstraszyć", "uciekaj", "obserwuj"]: break #
            print("Nieznana komenda.") #
        await self.player.uplyw_czasu(0.5, "konfrontacja") # ZMODYFIKOWANE #
        modyfikator_sily_gracza = self.player.oblicz_modyfikator_rzutu() // 2 + self.player.umiejetnosci["walka"] //3  #
        bonus_um_do_akcji = self.player.uzyj_bonusu_umiejetnosci() #
        if decyzja == "uciekaj": #
            print("Próbujesz uciec..."); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
            rzut_ucieczki = self.rzut_koscia(10) + modyfikator_sily_gracza  #
            if rzut_ucieczki >= ucieczka_gracza_próg: print(f"Udało ci się oddalić!"); self.player.zmien_potrzebe("wytrzymalosc", -1.0)  #
            else: 
                print(f"Nie udało się uciec!")
                await self.walka(nazwa_zwierzecia, hp_przeciwnika, atak_przeciwnika, jedzenie_drop, xp_za_pokonanie) # ZMODYFIKOWANE #
        elif decyzja == "spróbuj_odstraszyć": #
            print(f"Próbujesz odstraszyć..."); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
            rzut_odstraszenia = self.rzut_koscia(10) + modyfikator_sily_gracza + bonus_um_do_akcji + (2 if self.player.ma_ogien else 0) #
            if rzut_odstraszenia >= 7: 
                print(f"{nazwa_zwierzecia.capitalize()} odchodzi (Rzut: {rzut_odstraszenia} vs 7).")
                self.player.zmien_potrzebe("wytrzymalosc",-1.0)
                await self.player.dodaj_xp(xp_za_pokonanie // 3)  # ZMODYFIKOWANE #
            else: 
                print(f"Twoje próby rozzłościły {nazwa_zwierzecia} (Rzut: {rzut_odstraszenia} vs 7)!")
                await self.walka(nazwa_zwierzecia, hp_przeciwnika, atak_przeciwnika, jedzenie_drop, xp_za_pokonanie) # ZMODYFIKOWANE #
        elif decyzja == "walcz": 
            await self.walka(nazwa_zwierzecia, hp_przeciwnika, atak_przeciwnika, jedzenie_drop, xp_za_pokonanie) # ZMODYFIKOWANE #
        elif decyzja == "obserwuj": #
            print(f"Obserwujesz..."); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
            if not agresywne_z_natury and random.random() < 0.7: print(f"{nazwa_zwierzecia.capitalize()} odchodzi.") #
            else: 
                print(f"Bierność ośmieliła {nazwa_zwierzecia}. Atakuje!")
                await self.walka(nazwa_zwierzecia, hp_przeciwnika, atak_przeciwnika, jedzenie_drop, xp_za_pokonanie) # ZMODYFIKOWANE #

    async def walka(self, przeciwnik_nazwa, hp_przeciwnika, atak_przeciwnika, jedzenie_drop, xp_za_pokonanie): # ZMODYFIKOWANE: async
        print(f"\n--- Walka z {przeciwnik_nazwa}! ---"); await asyncio.sleep(0.02); runda = 0 # ZMODYFIKOWANE #
        while hp_przeciwnika > 0 and self.player.wytrzymalosc > 1.0: #
            runda += 1; print(f"\n--- Runda {runda} ---") #
            wytrzymalosc_display = int(self.player.wytrzymalosc) if self.player.wytrzymalosc == int(self.player.wytrzymalosc) else f"{self.player.wytrzymalosc:.1f}" #
            print(f"Twoja Wytrzymałość: {wytrzymalosc_display}, {przeciwnik_nazwa.capitalize()} HP: {hp_przeciwnika}") #
            modyfikator_gracza_walka = self.player.oblicz_modyfikator_rzutu() #
            bonus_walka_um = self.player.umiejetnosci["walka"] // 2  #
            print("\nTwoja tura:") #
            while True:
                akcja_walka = await async_input("Akcja: (atak / blok / precyzyjny_atak) > ") # ZMODYFIKOWANE #
                akcja_walka = akcja_walka.strip().lower()
                if akcja_walka in ["atak", "blok", "precyzyjny_atak"]: break #
                print("Nieznana akcja.") #
            trafienie_gracza = False; obrazenia_gracza = 0 #
            if akcja_walka == "atak": #
                rzut_ataku_gracza = self.rzut_koscia(10) + modyfikator_gracza_walka + bonus_walka_um + (1 if self.player.wytrzymalosc > 7.0 else 0) #
                if rzut_ataku_gracza >= 6: trafienie_gracza = True; obrazenia_gracza = self.rzut_koscia(4) + bonus_walka_um + (1 if self.player.wytrzymalosc > 8.0 else 0)  #
                self.player.zmien_potrzebe("wytrzymalosc", -1.0, cicho=True); print(f"Rzut na atak (K10 + mod={modyfikator_gracza_walka} + um={bonus_walka_um}): {rzut_ataku_gracza}") #
            elif akcja_walka == "precyzyjny_atak":  #
                rzut_ataku_gracza = self.rzut_koscia(10) + modyfikator_gracza_walka + bonus_walka_um - 1  #
                if rzut_ataku_gracza >= 7: trafienie_gracza = True; obrazenia_gracza = self.rzut_koscia(6) + bonus_walka_um + 1 + (1 if self.player.wytrzymalosc > 8.0 else 0)  #
                self.player.zmien_potrzebe("wytrzymalosc", -1.5, cicho=True); print(f"Rzut na precyzyjny atak (K10 + mod={modyfikator_gracza_walka} + um={bonus_walka_um} -1): {rzut_ataku_gracza}") #
            elif akcja_walka == "blok": print("Przygotowujesz się do obrony..."); self.player.zmien_potrzebe("wytrzymalosc", -0.5, cicho=True) #
            if trafienie_gracza: #
                hp_przeciwnika -= obrazenia_gracza #
                print(f"Trafiasz {przeciwnik_nazwa}, zadając {obrazenia_gracza} obrażeń. HP przeciwnika: {max(0, hp_przeciwnika)}") #
            elif akcja_walka != "blok": print(f"Chybiasz {przeciwnik_nazwa}.") #
            await asyncio.sleep(0.02) # ZMODYFIKOWANE #
            if hp_przeciwnika <= 0: #
                print(f"\nPokonujesz {przeciwnik_nazwa}!")
                await self.player.dodaj_xp(xp_za_pokonanie) # ZMODYFIKOWANE #
                self.player.inventory["jedzenie"] += jedzenie_drop #
                self.player.inventory["zloto"] += self.rzut_koscia(xp_za_pokonanie//10 +1)-1  #
                print(f"Zdobywasz {jedzenie_drop} porcji mięsa.") #
                if przeciwnik_nazwa == "wilk": await self.sprawdz_postep_zadania("pokonano_wilka", 1) # ZMODYFIKOWANE #
                elif przeciwnik_nazwa == "dzik": await self.sprawdz_postep_zadania("upoluj_dzika", 1) # ZMODYFIKOWANE #
                self.player.zmien_potrzebe("komfort_psychiczny", 1.0)
                await self.player.uplyw_czasu(0.5, "oporządzenie zdobyczy"); return  # ZMODYFIKOWANE #
            if self.player.wytrzymalosc <= 1.0: print("Jesteś zbyt wyczerpany..."); break #
            print(f"\nTura {przeciwnik_nazwa}:"); await asyncio.sleep(0.02) # ZMODYFIKOWANE #
            rzut_ataku_przeciwnika = self.rzut_koscia(10); próg_trafienia_przeciwnika = 5 - (2 if akcja_walka == "blok" else 0) - (bonus_walka_um //2)  #
            if rzut_ataku_przeciwnika >= próg_trafienia_przeciwnika :  #
                print(f"{przeciwnik_nazwa.capitalize()} atakuje i trafia" + (" mimo bloku!" if akcja_walka == "blok" and rzut_ataku_przeciwnika >=5 else "!")) #
                obrazenia_od_przeciwnika = max(1, atak_przeciwnika - (1 if akcja_walka == "blok" else 0) - (bonus_walka_um//3))  #
                self.player.zmien_potrzebe("wytrzymalosc", -obrazenia_od_przeciwnika) #
                if self.player.wytrzymalosc < 4.0: self.player.zmien_potrzebe("komfort_psychiczny", -1.0) #
            else: print(f"{przeciwnik_nazwa.capitalize()} chybia" + (" dzięki blokowi!" if akcja_walka == "blok" else "!")) #
            await self.player.uplyw_czasu(0.2, "runda walki")  # ZMODYFIKOWANE #
            if await self.sprawdz_stan_krytyczny("walka"): return # ZMODYFIKOWANE #
        if hp_przeciwnika > 0 and self.player.wytrzymalosc <=1.0: #
            print(f"{przeciwnik_nazwa.capitalize()} powala Cię..."); self.player.zmien_potrzebe("komfort_psychiczny", -3.0) #
            utrata_zlota = self.rzut_koscia(self.player.inventory["zloto"] // 2 if self.player.inventory["zloto"] > 0 else 0) #
            self.player.inventory["zloto"] = max(0, self.player.inventory["zloto"] - utrata_zlota) #
            print(f"Gubisz {utrata_zlota} złota.")
            await self.player.uplyw_czasu(self.rzut_koscia(4), "dochodzenie do siebie") # ZMODYFIKOWANE #

    async def akcje_w_dziczy(self): # ZMODYFIKOWANE: async
        while True:
            await asyncio.sleep(0.02); print(self.player) # ZMODYFIKOWANE #
            print(f"\nJesteś w: {self.player.lokacja_gracza}. Co chcesz zrobić?") #
            print("1. Ruszaj dalej") #
            print("2. Spróbuj odpocząć") #
            print("3. Zjedz coś (z ekwipunku)") #
            print("4. Napij się (z ekwipunku)") #
            print(f"5. Rozpal ogień (Drewno: {self.player.inventory['drewno']}. Ogień: {'Płonie' if self.player.ma_ogien else 'Brak'})") #
            print(f"6. Zbuduj/Popraw schronienie (Drewno: {self.player.inventory['drewno']}. Schronienie: {'Jest' if self.player.ma_schronienie else 'Brak'})") #
            print("7. Przeszukaj dokładnie okolicę") #
            print("8. Nic nie rób (przeczekaj)") #
            wybor = await async_input("> ") # ZMODYFIKOWANE #
            wybor = wybor.strip()
            if wybor == "1": return "kontynuuj"  #
            elif wybor == "2": #
                jakosc_snu = 0 #
                if self.player.ma_schronienie and self.player.ma_ogien: jakosc_snu = 3 #
                elif self.player.ma_schronienie: jakosc_snu = 2 #
                elif self.player.ma_ogien: jakosc_snu = 1 #
                if jakosc_snu > 0: await self.player.odpocznij(godziny=self.rzut_koscia(4)+2, jakosc_snu_mod=jakosc_snu) # ZMODYFIKOWANE #
                else: await self.player.odpocznij(godziny=self.rzut_koscia(3)+1, jakosc_snu_mod=0) # ZMODYFIKOWANE #
            elif wybor == "3": await self.player.jedz_z_ekwipunku() # ZMODYFIKOWANE #
            elif wybor == "4": await self.player.pij_z_ekwipunku() # ZMODYFIKOWANE #
            elif wybor == "5": #
                if not self.player.ma_ogien: await self.player.rozpal_ogien() # ZMODYFIKOWANE #
                else: print("Ogień już płonie.") #
            elif wybor == "6": #
                if not self.player.ma_schronienie: await self.player.zbuduj_schronienie() # ZMODYFIKOWANE #
                else: #
                    print("Masz już schronienie.") #
                    if self.player.inventory["drewno"] > 0: #
                        popraw_schronienie_input = await async_input("Chcesz dołożyć drewna do schronienia (trwalsze, lepszy komfort)? (t/n) ") # ZMODYFIKOWANE
                        if popraw_schronienie_input.lower() == 't': #
                            self.player.inventory["drewno"] -= 1; self.player.zmien_potrzebe("komfort_psychiczny",0.5)
                            await self.player.uplyw_czasu(0.5, "poprawianie schronienia") # ZMODYFIKOWANE #
                            print("Poprawiasz schronienie.") #
                    else: print("Nie masz drewna na poprawki.") #
            elif wybor == "7": #
                obszar_dane_biezacy = OBSZARY_DZICZY.get(self.player.lokacja_gracza) #
                if obszar_dane_biezacy: await self.przeszukaj_obszar_dokladnie(obszar_dane_biezacy, kontekst="akcja_gracza") # ZMODYFIKOWANE #
                else: 
                    print("Jesteś w nieznanym miejscu...")
                    await self.player.uplyw_czasu(1, "bezowocne poszukiwania") # ZMODYFIKOWANE #
            elif wybor == "8": 
                print("Postanawiasz przeczekać chwilę...")
                await self.player.uplyw_czasu(1, "oczekiwanie") # ZMODYFIKOWANE #
            else: print("Nieznana komenda.") #
            if await self.sprawdz_stan_krytyczny("po_akcji_w_dziczy"): return "koniec_gry" # ZMODYFIKOWANE #

    async def sprawdz_stan_krytyczny(self, kontekst=""): # ZMODYFIKOWANE: async (chociaż nie musi, jeśli nie ma await wewnątrz)
        krytyczny = False; wiadomosc = ""; epsilon = 0.01  #
        w_kryt = self.player.wytrzymalosc <= 1.0 + epsilon; gp_kryt = self.player.glod_pragnienie <= 1.0 + epsilon; kp_kryt = self.player.komfort_psychiczny <= 1.0 + epsilon #
        w_niski = self.player.wytrzymalosc <= 2.0 + epsilon; gp_niski = self.player.glod_pragnienie <= 2.0 + epsilon; kp_niski = self.player.komfort_psychiczny <= 2.0 + epsilon #
        if w_kryt and gp_kryt and kp_kryt: krytyczny = True; wiadomosc = "Jesteś na absolutnym skraju..." #
        elif w_kryt and (gp_niski or kp_niski): krytyczny = True; wiadomosc = "Padłeś z wyczerpania..." #
        elif gp_kryt and (w_niski or kp_niski): krytyczny = True; wiadomosc = "Głód i pragnienie odebrały Ci resztki sił..." #
        elif kp_kryt and (w_niski or gp_niski): krytyczny = True; wiadomosc = "Twój duch został złamany..." #
        if krytyczny: #
            print(f"\n--- KONIEC GRY ({kontekst}) ---"); print(wiadomosc) #
            print(f"Twoja podróż dobiega końca w mrocznej dziczy po {int(self.player.dni_w_podrozy)} dniach na {self.player.poziom} poziomie.") #
            return True #
            
        return False #
        
    async def start_gry(self): # ZMODYFIKOWANE: async
        print("+" + "-"*70 + "+") #
        print("| Witaj w grze 'Słowiańska Dzicz' (X wiek)                          |") #
        print("| Twoim celem jest przetrwać, rozwijać się i odkrywać tajemnice    |") #
        print("| tych niebezpiecznych krain, dbając o swoje potrzeby.             |") #
        print("+" + "-"*70 + "+") #
        print("Powodzenia, wędrowcze!") #
        await asyncio.sleep(0.1) # ZMODYFIKOWANE, krótszy sen #
        
        if self.player.lokacja_gracza not in self.wioski_info:
            self.wioski_info[self.player.lokacja_gracza] = Village(self.player.lokacja_gracza)

        status_petli = "kontynuuj" 
        while status_petli != "koniec_gry": #
            if self.player.lokacja_gracza == "Dzicz":
                 status_petli = await self.petla_eksploracji() # ZMODYFIKOWANE
                 if status_petli == "znaleziono_wioske": 
                     status_petli = await self.petla_wioski() # ZMODYFIKOWANE
            else: # Gracz jest w wiosce
                 status_petli = await self.petla_wioski() # ZMODYFIKOWANE
                 if status_petli == "rozpocznij_eksploracje": # Jeśli petla_wioski chce przejść do eksploracji
                     self.player.lokacja_gracza = "Dzicz" # Ustawiamy lokację na Dzicz
                     # Pętla while naturalnie przejdzie do gałęzi if self.player.lokacja_gracza == "Dzicz":
                     status_petli = "kontynuuj_glowna_petle" # Aby pętla while kontynuowała


        print("\n--- OSTATECZNY STAN POSTACI ---"); print(self.player) #

async def run_game_async_entry_point():
    """Asynchroniczny punkt wejścia do gry, wywoływany z JavaScript."""
    random.seed()  #
    game = Game() #
    globals()["game"] = game
    await game.start_gry() #

# Stary blok if __name__ == "__main__": nie jest już potrzebny dla Pyodide,
# ponieważ run_game_async_entry_point() zostanie wywołane z JavaScriptu.
# Możesz go zostawić zakomentowany dla testów lokalnych z asyncio.run(), np.:
# if __name__ == "__main__":
#    asyncio.run(run_game_async_entry_point())
