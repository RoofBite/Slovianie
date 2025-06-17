# GraTekstowa3.8.py - WERSJA Z MODYFIKATORAMI ŚRODOWISKOWYMI, WIEDZĄ I PROBLEMAMI WIOSKI

import random
import math
import sys
import asyncio
import json
from js import window, Blob, URL, document #js_print_function, js_request_input_function, #js_set_game_instance

# --- Konfiguracja Środowiska (Pyodide/JS) ---
class SimpleJsWriter:
    def write(self, s):
        js_print_function(s)
    def flush(self):
        pass

sys.stdout = SimpleJsWriter()
sys.stderr = SimpleJsWriter()

async def async_input(prompt=""):
    return await js_request_input_function(prompt)

# --- Stałe Gry ---
PRODUKTY_ROLNE = "Produkty rolne"
MINERALY_I_SUROWCE = "Minerały i surowce"
PRODUKTY_RZEMIESLNICZE = "Produkty rzemieślnicze"
PRODUKTY_LUKSUSOWE = "Produkty luksusowe"
TECHNOLOGIE_I_INNOWACJE = "Technologie i innowacje"

PRODUKTY_HANDLOWE_INFO = {
    PRODUKTY_ROLNE: {"waga": 2.0, "bazowa_cena": 10, "opis": "Żywność, plony."},
    MINERALY_I_SUROWCE: {"waga": 3.0, "bazowa_cena": 15, "opis": "Rudy, kamienie, podstawowe surowce."},
    PRODUKTY_RZEMIESLNICZE: {"waga": 1.5, "bazowa_cena": 20, "opis": "Narzędzia, proste ubrania, ceramika."},
    PRODUKTY_LUKSUSOWE: {"waga": 0.5, "bazowa_cena": 50, "opis": "Biżuteria, drogie tkaniny, rzadkie przyprawy."},
    TECHNOLOGIE_I_INNOWACJE: {"waga": 1.0, "bazowa_cena": 30, "opis": "Fragmenty wiedzy, ulepszone narzędzia, wynalazki."},
}
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
}

# --- NOWOŚĆ: Wiedza Zdobywana przez Gracza ---
WIEDZA_DO_ODKRYCIA = {
    "tech_rolnicza_1": {"nazwa": "Prosta technika uprawy", "opis": "Wiesz, jak lepiej przygotować ziemię pod zasiew.", "warunek": {"przetrwanie": 2}, "typ": "Technologia"},
    "spol_organizacja_1": {"nazwa": "Organizacja pracy zbiorowej", "opis": "Rozumiesz, jak efektywniej rozdzielać zadania w małej grupie.", "warunek": {"odkryte_wioski": 2}, "typ": "Rozwiązanie społeczne"},
    "tech_narzedzia_1": {"nazwa": "Ulepszone narzędzia z drewna", "opis": "Potrafisz tworzyć wytrzymalsze i skuteczniejsze drewniane narzędzia.", "warunek": {"przetrwanie": 3}, "typ": "Know-how"},
    "rytual_ochronny_1": {"nazwa": "Rytuał odpędzania złych duchów", "opis": "Znasz gesty i słowa, które dodają otuchy i poczucia bezpieczeństwa.", "warunek": {"przezyte_dni": 10}, "typ": "Rytuał"},
    "roslina_lecznicza_1": {"nazwa": "Identyfikacja pospolitej rośliny leczniczej", "opis": "Potrafisz rozpoznać zioło, które łagodzi ból i przyspiesza gojenie.", "warunek": {"zielarstwo_tropienie": 3}, "typ": "Roślina"},
    "know_how_handel_1": {"nazwa": "Podstawy negocjacji", "opis": "Nauczyłeś się, jak rozmawiać z kupcami, by uzyskać lepszą cenę.", "warunek": {"charyzma_handel": 3}, "typ": "Know-how"},
    "tech_budowlana_1": {"nazwa": "Wzmacnianie prostych konstrukcji", "opis": "Wiesz, jak budować trwalsze schronienia i płoty.", "warunek": {"przetrwanie": 4}, "typ": "Technologia"},
    "napar_wzmacniajacy_1": {"nazwa": "Napar wzmacniający", "opis": "Umiesz przygotować napar, który krzepi ciało i umysł.", "warunek": {"zielarstwo_tropienie": 4}, "typ": "Napar"},
    "rozw_spoleczne_konflikt": {"nazwa": "Metoda rozwiązywania sporów", "opis": "Znasz sposób na łagodzenie napięć między zwaśnionymi stronami.", "warunek": {"reputacja_total": 30}, "typ": "Rozwiązanie społeczne"},
    "typ_rzadow_rada_starszych": {"nazwa": "Koncepcja rady starszych", "opis": "Widziałeś, jak wspólne podejmowanie decyzji przez najmądrzejszych może pomóc społeczności.", "warunek": {"odkryte_wioski": 4}, "typ": "Typ rządów"},
}

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

OBSZARY_DZICZY = {
    "Gęsty Las": {"opis": "Przedzierasz się przez gęsty, mroczny las...", "kary_przy_wejsciu": {"wytrzymalosc": -0.5, "komfort_psychiczny": -0.5}, "zasoby": {"drewno": (2, 0.7), "jedzenie_roslinne": (1, 0.5), "zwierzyna_mala": (1,0.3), "bursztyn": (1, 0.05)}, "wydarzenia_specjalne": ["slady_bestii", "szelest_w_krzakach", "aura_demonow", "dzikie_zwierze"], "trudnosc_ognia": 0.2, "opis_demonow": "Czujesz czyhające zło...", "xp_za_odkrycie": 15 },
    "Mokradła": {"opis": "Stąpasz ostrożnie po zdradliwych mokradłach...", "kary_przy_wejsciu": {"wytrzymalosc": -1.0, "komfort_psychiczny": -1.0, "glod_pragnienie":-0.5}, "zasoby": {"woda_brudna": (2,0.8), "jedzenie_roslinne_bagienne": (1, 0.4), "rzadkie_zioło_lecznicze": (1, 0.1)}, "wydarzenia_specjalne": ["uciqzliwe_insekty", "odglosy_z_bagien", "mgla", "aura_demonow", "dzikie_zwierze"], "trudnosc_ognia": 0.7, "opis_demonow": "Opary unoszące się nad bagnami...", "xp_za_odkrycie": 20 },
    "Jałowe Wzgórza": {"opis": "Wędrujesz przez jałowe, smagane wiatrem wzgórza...", "kary_przy_wejsciu": {"glod_pragnienie": -0.5, "wytrzymalosc":-0.5}, "zasoby": {"drewno_suche": (1, 0.3), "woda_skala": (1, 0.2), "stara_moneta": (1, 0.08)}, "wydarzenia_specjalne": ["silny_wiatr", "poczucie_obserwacji", "kamienne_kregi", "dzikie_zwierze"], "trudnosc_ognia": 0.1, "opis_demonow": "Wiatr niesie echa dawnych rytuałów...", "xp_za_odkrycie": 15 },
    "Stary Święty Gaj": {"opis": "Trafiasz do starego, cichego gaju...", "bonusy_przy_wejsciu": {"komfort_psychiczny": 1.0, "wytrzymalosc": 0.5}, "zasoby": {"jedzenie_roslinne_lecznicze": (1, 0.6), "woda_czysta_zrodlo": (2, 0.9), "drewno_swiete": (1,0.4), "rzadkie_zioło_lecznicze": (1,0.3)}, "wydarzenia_specjalne": ["znalezisko_ziola_lecznicze", "chwila_kontemplacji", "przychylnosc_duchow_gaju"], "trudnosc_ognia": 0.0, "pozytywny": True, "xp_za_odkrycie": 30 },
    "Opuszczona Chata": {"opis": "Natrafiasz na opuszczoną, na wpół zrujnowaną chatę.", "bonusy_przy_wejsciu": {"komfort_psychiczny": 0.5}, "zasoby": {"drewno_stare": (2,0.8), "resztki_narzedzi": (1,0.2), "fragment_mapy": (1, 0.1)}, "wydarzenia_specjalne": ["niepokojace_znalezisko_w_chacie", "schronienie_przed_deszczem", "slady_walki"], "trudnosc_ognia": 0.1, "pozytywny": True, "xp_za_odkrycie": 25 },
    "Spalona Ziemia": {"opis": "Przechodzisz przez krainę spustoszoną przez pożar.", "kary_przy_wejsciu": {"komfort_psychiczny": -1.0, "glod_pragnienie": -0.5}, "zasoby": {"drewno_opalone": (3, 0.5), "stara_moneta": (1, 0.03)}, "wydarzenia_specjalne": ["poczucie_straty", "aura_demonow", "znalezisko_w_pogorzelisku", "dzikie_zwierze"], "trudnosc_ognia": 0.3, "opis_demonow": "Cienie zgliszcz poruszają się same...", "xp_za_odkrycie": 20 },
    "Kamieniste Pustkowie": {"opis": "Bezkresne, kamieniste pustkowie.", "kary_przy_wejsciu": {"wytrzymalosc": -1.0, "glod_pragnienie": -1.0}, "zasoby": {"woda_skala": (1, 0.1), "drobna_zwierzyna_pustynna": (1, 0.1)}, "wydarzenia_specjalne": ["ekstremalne_temperatury", "burza_piaskowa", "poczucie_osamotnienia", "dzikie_zwierze"], "trudnosc_ognia": 0.5, "opis_demonow": "Pustka wroga życiu...", "xp_za_odkrycie": 25 }
}

MODYFIKATORY_SRODOWISKOWE = {
    "Ulewny Deszcz": {
        "opis": "Z nieba leją się strugi deszczu. Wszystko jest mokre i zimne.",
        "efekty": {
            "zmien_potrzebe": {"komfort_psychiczny": -1.5, "wytrzymalosc": -0.5},
            "modyfikator_akcji": { "rozpal_ogien_prog": 3, }
        }
    },
    "Gęsta Mgła": {
        "opis": "Gęsta, mleczna mgła ogranicza widoczność do kilku kroków. Dźwięki są stłumione i dziwnie bliskie.",
        "efekty": { "zmien_potrzebe": {"komfort_psychiczny": -1.0}, "opis_dodatkowy": "We mgle łatwo stracić orientację." }
    },
    "Duszny Zapar": {
        "opis": "Powietrze stoi w miejscu, jest ciężkie i wilgotne. Trudno złapać oddech.",
        "efekty": { "zmien_potrzebe": {"wytrzymalosc": -1.0, "glod_pragnienie": -0.5}, "opis_dodatkowy": "Każdy wysiłek męczy podwójnie." }
    },
    "Silny Wiatr": {
        "opis": "Porywisty wiatr targa drzewami i utrudnia marsz.",
        "efekty": {
            "zmien_potrzebe": {"wytrzymalosc": -1.0},
            "modyfikator_akcji": { "rozpal_ogien_prog": 2 },
            "nowe_wydarzenie": { "szansa": 0.2, "tekst": "Wiatr zrywa ci z pleców część ekwipunku!", "akcja": "utrata_przedmiotu" }
        }
    },
    "Czyste Niebo i Ciepło": { "opis": "Słońce przyjemnie grzeje, a na niebie nie ma ani jednej chmury.", "efekty": { "zmien_potrzebe": {"komfort_psychiczny": 1.0} } },
    "Przymrozek": {
        "opis": "Zimno staje się dotkliwe, a szron pokrywa ziemię. Twój oddech zamienia się w parę.",
        "efekty": {
            "zmien_potrzebe": {"komfort_psychiczny": -1.0, "wytrzymalosc": -0.5},
            "modyfikator_akcji": { "rozpal_ogien_prog": 1 }, "opis_dodatkowy": "Bez ciepłego ognia trudno będzie przetrwać noc."
        }
    },
    "Rój Insektów": {
        "opis": "Chmary natrętnych, gryzących insektów unoszą się w powietrzu. Nie dają ci spokoju.",
        "efekty": { "zmien_potrzebe": {"komfort_psychiczny": -2.0}, "opis_dodatkowy": "Ciągłe bzyczenie i ukąszenia doprowadzają cię do szału." }
    },
    "Nienaturalna Cisza": {
        "opis": "W lesie zapada nagła, głucha cisza. Nie słychać ptaków, wiatru ani owadów.",
        "efekty": { "zmien_potrzebe": {"komfort_psychiczny": -1.5}, "opis_dodatkowy": "Ta cisza jest gorsza niż najgłośniejszy hałas. Czujesz na plecach czyjś wzrok." }
    },
    "Gwieździsta Noc": {
        "opis": "Niebo jest bezchmurne i usiane milionami gwiazd. Czasem widać spadającą gwiazdę.",
        "efekty": { "zmien_potrzebe": {"komfort_psychiczny": 1.5}, "opis_dodatkowy": "Widok ten napawa cię nadzieją i spokojem." }
    },
    "Zapach Zgnilizny": {
        "opis": "W powietrzu unosi się ciężki, słodkawy odór rozkładu. Coś dużego musiało tu umrzeć.",
        "efekty": {
            "zmien_potrzebe": {"komfort_psychiczny": -1.0, "glod_pragnienie": -0.5},
             "nowe_wydarzenie": { "szansa": 0.15, "tekst": "Odór jest tak silny, że psuje ci część zapasów jedzenia.", "akcja": "utrata_przedmiotu" }
        }
    }
}

ETAPY_EKSPLORACJI = [
    {"kosci": [10, 8, 6],  "szanse_na_wies": [1]},
    {"kosci": [8, 10, 12], "szanse_na_wies": [1, 2, 3]},
    {"kosci": [10, 8, 6],  "szanse_na_wies": [1, 2, 3, 4]},
    {"kosci": [8, 10, 12], "szanse_na_wies": [1, 2, 3, 4]},
    {"kosci": [10, 8, 6],  "szanse_na_wies": [1, 2, 3, 4]},
]
CENNE_PRZEDMIOTY_CENY = { "bursztyn": 20, "stara_moneta": 18, "rzadkie_zioło_lecznicze": 15, "fragment_mapy": 25 }

# --- Funkcje Zapisu/Odczytu ---
def get_state_as_json(game: "Game") -> str:
    p = game.player
    player_state = {
        "lokacja_gracza": p.lokacja_gracza, "dni_w_podrozy": p.dni_w_podrozy,
        "godziny_w_tej_dobie": p.godziny_w_tej_dobie, "inventory": p.inventory,
        "inventory_cenne": p.inventory_cenne, "inventory_towary_handlowe": p.inventory_towary_handlowe,
        "umiejetnosci": p.umiejetnosci, "punkty_umiejetnosci_do_wydania": p.punkty_umiejetnosci_do_wydania,
        "xp": p.xp, "poziom": p.poziom, "reputacja": p.reputacja,
        "wytrzymalosc": p.wytrzymalosc, "glod_pragnienie": p.glod_pragnienie,
        "komfort_psychiczny": p.komfort_psychiczny, "ma_ogien": p.ma_ogien, "ma_schronienie": p.ma_schronienie,
        "odkryta_wiedza": list(p.odkryta_wiedza), # NOWOŚĆ
    }
    wioski_full_info_to_save = {}
    for nazwa, wioska_obj in game.wioski_info.items():
        wioski_full_info_to_save[nazwa] = {
            "aspekty_wioski_numeric": wioska_obj.aspekty_wioski_numeric,
            "problem": wioska_obj.problem, # NOWOŚĆ
        }
    game_state_dict = {
        "aktualny_etap_eksploracji_idx": game.aktualny_etap_eksploracji_idx,
        "lokacje_w_aktualnym_etapie": game.lokacje_w_aktualnym_etapie,
        "odkryte_typy_obszarow": list(game.odkryte_typy_obszarow),
        "aktywne_zadanie": game.aktywne_zadanie or None,
        "nazwa_aktualnej_wioski": game.nazwa_aktualnej_wioski,
        "wioski_full_info": wioski_full_info_to_save,
        "odkryte_wioski_lista_nazw": list(game.odkryte_wioski_lista_nazw)
    }
    full = { "player": player_state, "game": game_state_dict }
    return json.dumps(full, separators=(",",":"))

def download_save(game: "Game"):
    data_str = get_state_as_json(game)
    blob = Blob.new([data_str], { "type": "application/json" })
    url = URL.createObjectURL(blob)
    a = document.createElement("a")
    a.href = url
    a.download = "save_slowianska_dzicz.json"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    print("💾 Rozpoczęto pobieranie zapisu gry.")

def load_state_from_json(game: "Game", json_str: str):
    try:
        full = json.loads(json_str)
    except Exception as e:
        print(f"Błąd parsowania JSON-a przy wczytywaniu: {e}")
        return False
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
    p.odkryta_wiedza = set(ps.get("odkryta_wiedza", [])) # NOWOŚĆ
    p.maks_udzwig = p.oblicz_maks_udzwig()
    p.oblicz_aktualny_udzwig()

    gs = full.get("game", {})
    game.aktualny_etap_eksploracji_idx = gs.get("aktualny_etap_eksploracji_idx", game.aktualny_etap_eksploracji_idx)
    game.lokacje_w_aktualnym_etapie = gs.get("lokacje_w_aktualnym_etapie", game.lokacje_w_aktualnym_etapie)
    game.odkryte_typy_obszarow = set(gs.get("odkryte_typy_obszarow", []))
    game.aktywne_zadanie = gs.get("aktywne_zadanie", game.aktywne_zadanie)
    game.nazwa_aktualnej_wioski = gs.get("nazwa_aktualnej_wioski", game.nazwa_aktualnej_wioski)
    
    game.odkryte_wioski_lista_nazw = gs.get("odkryte_wioski_lista_nazw", [])
    game.wioski_info = {}
    loaded_wioski_data = gs.get("wioski_full_info", {})

    all_village_names_to_ensure = set(game.odkryte_wioski_lista_nazw)
    if game.nazwa_aktualnej_wioski and game.nazwa_aktualnej_wioski not in ["Dzicz", None]:
         all_village_names_to_ensure.add(game.nazwa_aktualnej_wioski)
    if "Ukryta Dolina" not in all_village_names_to_ensure: # Upewnij się, że Ukryta Dolina jest na liście
        all_village_names_to_ensure.add("Ukryta Dolina")
        if "Ukryta Dolina" not in game.odkryte_wioski_lista_nazw: # Dodaj do listy, jeśli brakuje
            game.odkryte_wioski_lista_nazw.insert(0, "Ukryta Dolina")


    for nazwa_wioski in all_village_names_to_ensure:
        village_obj = Village(nazwa_wioski)
        if nazwa_wioski in loaded_wioski_data:
             if "aspekty_wioski_numeric" in loaded_wioski_data[nazwa_wioski]:
                village_obj.aspekty_wioski_numeric = loaded_wioski_data[nazwa_wioski]["aspekty_wioski_numeric"]
             village_obj.problem = loaded_wioski_data[nazwa_wioski].get("problem", None) # NOWOŚĆ
        
        village_obj._oblicz_poziomy_produkcji_i_ceny()
        if not village_obj.problem and nazwa_wioski != "Ukryta Dolina": # NOWOŚĆ - generuj problem, jeśli go nie ma
             village_obj.generuj_problem()
        game.wioski_info[nazwa_wioski] = village_obj
    
    if p.lokacja_gracza not in ["Dzicz", None] and p.lokacja_gracza not in game.wioski_info:
        print(f"Ostrzeżenie: Lokacja gracza '{p.lokacja_gracza}' nie znaleziona, resetowanie do Ukrytej Doliny.")
        p.lokacja_gracza = "Ukryta Dolina"
        game.nazwa_aktualnej_wioski = "Ukryta Dolina"

    print("🔄 Stan gry został wczytany! Możesz kontynuować.")
    return True

# --- Klasy Gry ---
class Village:
    def __init__(self, name):
        self.name = name
        self.aspekty_wioski_numeric = {}
        self.poziomy_produkcji_opis = {}
        self.ceny_produktow_finalne = {}
        self.problem = None # NOWOŚĆ
        if not self.aspekty_wioski_numeric:
            self._generuj_aspekty_i_wplyw()
        self._oblicz_poziomy_produkcji_i_ceny()
        if self.name != "Ukryta Dolina": # Domowa wioska nie ma problemów
             self.generuj_problem() # NOWOŚĆ

    def _generuj_aspekty_i_wplyw(self):
        wybrane_nazwy_aspektow = random.sample(ASPEKTY_LISTA, 3)
        for nazwa_aspektu in wybrane_nazwy_aspektow:
            rzut = Game.rzut_koscia(4)
            if rzut == 1: wplyw = -2
            elif rzut == 2: wplyw = -1
            elif rzut == 3: wplyw = 1
            else: wplyw = 2
            self.aspekty_wioski_numeric[nazwa_aspektu] = wplyw
    
    def generuj_problem(self): # NOWOŚĆ
        if self.problem: return # Już ma problem
        negatywne_aspekty = [a for a, w in self.aspekty_wioski_numeric.items() if w < 0]
        if not negatywne_aspekty: return # Brak negatywnych aspektów, brak problemu

        aspekt_problemu = random.choice(negatywne_aspekty)
        typ_problemu = random.choice(["prosty_negatywny", "konflikt_z_innym", "spor_wewnetrzny"])

        if typ_problemu == "prosty_negatywny":
            self.problem = {
                "typ": "prosty_negatywny", "aspekt": aspekt_problemu,
                "opis": f"Mieszkańcy narzekają, że negatywny wpływ '{aspekt_problemu}' bardzo utrudnia im życie."
            }
        elif typ_problemu == "konflikt_z_innym":
            pozostale_aspekty = [a for a in self.aspekty_wioski_numeric.keys() if a != aspekt_problemu]
            if pozostale_aspekty:
                drugi_aspekt = random.choice(pozostale_aspekty)
                self.problem = {
                    "typ": "konflikt_z_innym", "aspekt": aspekt_problemu, "drugi_aspekt": drugi_aspekt,
                    "opis": f"Problem z '{aspekt_problemu}' powoduje dodatkowe napięcia na tle '{drugi_aspekt}'."
                }
            else: # Fallback
                self.problem = { "typ": "prosty_negatywny", "aspekt": aspekt_problemu, "opis": f"Mieszkańcy narzekają, że negatywny wpływ '{aspekt_problemu}' bardzo utrudnia im życie."}
        else: # spor_wewnetrzny
             self.problem = {
                "typ": "spor_wewnetrzny", "aspekt": aspekt_problemu,
                "opis": f"Starszyzna i lud nie mogą dojść do porozumienia w kwestii '{aspekt_problemu}', co prowadzi do sporów."
            }
        print(f"DEBUG: Wioska {self.name} ma nowy problem: {self.problem['opis']}")

    def rozwiaz_problem(self): # NOWOŚĆ
        if not self.problem: return
        aspekt_do_poprawy = self.problem['aspekt']
        if aspekt_do_poprawy in self.aspekty_wioski_numeric:
            stary_wplyw = self.aspekty_wioski_numeric[aspekt_do_poprawy]
            if stary_wplyw < 0:
                self.aspekty_wioski_numeric[aspekt_do_poprawy] += 1
                print(f"Wpływ aspektu '{aspekt_do_poprawy}' w wiosce {self.name} poprawił się z {stary_wplyw} na {stary_wplyw+1}.")
                self._oblicz_poziomy_produkcji_i_ceny()
                self.problem = None # Problem rozwiązany
            else: # Już nie jest negatywny, coś poszło nie tak
                self.problem = None
        else:
             print(f"BŁĄD: Próbowano rozwiązać problem z nieistniejącym aspektem '{aspekt_do_poprawy}'")


    def _oblicz_poziomy_produkcji_i_ceny(self):
        for produkt, info_produktu in PRODUKTY_HANDLOWE_INFO.items():
            sumaryczny_wplyw_aspektow = 0
            for aspekt_wioski, wplyw_numeric_aspektu in self.aspekty_wioski_numeric.items():
                if produkt in ASPEKTY_WPLYW_NA_PRODUKTY.get(aspekt_wioski, []):
                    sumaryczny_wplyw_aspektow += wplyw_numeric_aspektu
            opis_poziomu_produkcji = get_poziom_produkcji_opis(sumaryczny_wplyw_aspektow)
            self.poziomy_produkcji_opis[produkt] = opis_poziomu_produkcji
            modyfikatory = CENY_MODYFIKATORY_PRODUKCJI[opis_poziomu_produkcji]
            bazowa_cena_produktu = info_produktu["bazowa_cena"]
            cena_kupna_od_wioski = int(bazowa_cena_produktu * modyfikatory["kupno_od_wioski_mod"])
            cena_sprzedazy_do_wioski = int(bazowa_cena_produktu * modyfikatory["sprzedaz_do_wioski_mod"])
            if cena_sprzedazy_do_wioski > cena_kupna_od_wioski:
                cena_sprzedazy_do_wioski = cena_kupna_od_wioski
            if cena_sprzedazy_do_wioski == cena_kupna_od_wioski and cena_kupna_od_wioski > 1:
                 cena_sprzedazy_do_wioski = max(1, cena_kupna_od_wioski -1)
            self.ceny_produktow_finalne[produkt] = {
                "kupno_od_wioski": max(1, cena_kupna_od_wioski),
                "sprzedaz_do_wioski": max(1, cena_sprzedazy_do_wioski)
            }
    
    def get_village_goods_info_str(self, player_charisma_skill):
        output = f"\n--- Handel w {self.name} ---\n"
        output += "Aspekty wpływające na ekonomię wioski:\n"
        for aspekt, wplyw in self.aspekty_wioski_numeric.items():
            wplyw_str = {-2: "bardzo zły", -1: "zły", 1: "dobry", 2: "bardzo dobry"}.get(wplyw, "neutralny")
            output += f"  - {aspekt} (wpływ: {wplyw_str})\n"
        output += "\nDostępne towary handlowe (ceny uwzględniają Twoją charyzmę):\n"
        mnoznik_ceny_zakupu_przez_gracza = max(0.7, 1.0 - player_charisma_skill * 0.03)
        mnoznik_ceny_sprzedazy_przez_gracza = 1.0 + player_charisma_skill * 0.03
        for produkt_nazwa in LISTA_PRODUKTOW_HANDLOWYCH:
            info_produktu = PRODUKTY_HANDLOWE_INFO[produkt_nazwa]
            poziom_produkcji = self.poziomy_produkcji_opis.get(produkt_nazwa, "Brak danych")
            ceny_bazowe_wioski = self.ceny_produktow_finalne.get(produkt_nazwa, {})
            cena_kupna_dla_gracza = max(1, int(ceny_bazowe_wioski.get('kupno_od_wioski', 9999) * mnoznik_ceny_zakupu_przez_gracza))
            cena_sprzedazy_dla_gracza = max(1, int(ceny_bazowe_wioski.get('sprzedaz_do_wioski', 0) * mnoznik_ceny_sprzedazy_przez_gracza))
            output += f"  - {produkt_nazwa} (Waga: {info_produktu['waga']})\n"
            output += f"    Produkcja wioski: {poziom_produkcji}\n"
            output += f"    Możesz kupić za: {cena_kupna_dla_gracza} zł\n"
            output += f"    Możesz sprzedać za: {cena_sprzedazy_dla_gracza} zł\n"
        return output

    def get_aspekty_summary(self):
        if not self.aspekty_wioski_numeric: return "(Brak danych o aspektach)"
        summary_parts = []
        for aspekt, wplyw_num in self.aspekty_wioski_numeric.items():
            wplyw_str = {-2: "Bb. zły", -1: "Zły", 1: "Dobry", 2: "Bb. dobry"}.get(wplyw_num, "N/A")
            aspekt_short = aspekt.split('/')[0]
            if len(aspekt_short) > 10: aspekt_short = aspekt_short[:8]+".."
            summary_parts.append(f"{aspekt_short}: {wplyw_str}")
        return "(" + ", ".join(summary_parts) + ")"

class Player:
    def __init__(self):
        self.wytrzymalosc = 6.0; self.glod_pragnienie = 6.0; self.komfort_psychiczny = 6.0
        self.inventory = {"jedzenie": 3, "woda": 3, "drewno": 1, "zloto": 50}
        self.inventory_cenne = {"bursztyn": 0, "stara_moneta": 0, "rzadkie_zioło_lecznicze": 0, "fragment_mapy": 0}
        self.inventory_towary_handlowe = {produkt: 0 for produkt in LISTA_PRODUKTOW_HANDLOWYCH}
        self.ma_schronienie = False; self.ma_ogien = False
        self.lokacja_gracza = "Ukryta Dolina" # ZMIANA
        self.dni_w_podrozy = 0.0; self.godziny_w_tej_dobie = 0.0
        self.ma_bonus_do_umiejetnosci = False; self.wartosc_bonusu_do_umiejetnosci = 0; self.opis_bonusu_do_umiejetnosci = ""
        self.poziom = 1; self.xp = 0; self.xp_do_nastepnego_poziomu = 100
        self.punkty_umiejetnosci_do_wydania = 1
        self.umiejetnosci = {"przetrwanie": 1, "zielarstwo_tropienie": 1, "walka": 1, "charyzma_handel": 1, "udzwig": 1}
        self.reputacja = {"Ukryta Dolina": 0} # ZMIANA
        self.odkryta_wiedza = set() # NOWOŚĆ
        self.maks_udzwig = self.oblicz_maks_udzwig()
        self.aktualny_udzwig = self.oblicz_aktualny_udzwig()

    def oblicz_maks_udzwig(self): return 5.0 + (self.umiejetnosci["udzwig"] * 5.0)
    def oblicz_aktualny_udzwig(self):
        current_weight = 0.0
        for towar, ilosc in self.inventory_towary_handlowe.items():
            if ilosc > 0: current_weight += ilosc * PRODUKTY_HANDLOWE_INFO[towar]["waga"]
        self.aktualny_udzwig = current_weight
        return current_weight
    def zmien_towar_handlowy(self, towar, ilosc_zmiana):
        if towar not in PRODUKTY_HANDLOWE_INFO: print(f"Błąd: Nieznany towar handlowy {towar}"); return False
        waga_sztuki = PRODUKTY_HANDLOWE_INFO[towar]["waga"]
        if ilosc_zmiana < 0 and self.inventory_towary_handlowe.get(towar, 0) < abs(ilosc_zmiana):
            print(f"Nie masz wystarczająco '{towar.lower()}' ({self.inventory_towary_handlowe.get(towar,0)} szt.) do usunięcia {abs(ilosc_zmiana)} szt.")
            return False
        if ilosc_zmiana > 0:
            potencjalna_zmiana_wagi = ilosc_zmiana * waga_sztuki
            if self.aktualny_udzwig + potencjalna_zmiana_wagi > self.maks_udzwig:
                print(f"Nie możesz tyle unieść. Przekraczasz udźwig o {(self.aktualny_udzwig + potencjalna_zmiana_wagi) - self.maks_udzwig:.1f} kg.")
                print(f"Masz: {self.aktualny_udzwig:.1f}/{self.maks_udzwig:.1f} kg. Próbujesz dodać {potencjalna_zmiana_wagi:.1f} kg.")
                return False
        self.inventory_towary_handlowe[towar] = self.inventory_towary_handlowe.get(towar, 0) + ilosc_zmiana
        self.oblicz_aktualny_udzwig(); return True
    def __str__(self):
        cenne_str = ", ".join([f"{item.replace('_',' ').capitalize()}: {qty}" for item, qty in self.inventory_cenne.items() if qty > 0]) or "Brak"
        w_d = int(self.wytrzymalosc) if self.wytrzymalosc == int(self.wytrzymalosc) else f"{self.wytrzymalosc:.1f}"
        gp_d = int(self.glod_pragnienie) if self.glod_pragnienie == int(self.glod_pragnienie) else f"{self.glod_pragnienie:.1f}"
        kp_d = int(self.komfort_psychiczny) if self.komfort_psychiczny == int(self.komfort_psychiczny) else f"{self.komfort_psychiczny:.1f}"
        um_str = ", ".join([f"{u.replace('_',' ').capitalize()}: {p}" for u, p in self.umiejetnosci.items()])
        th_str = ", ".join([f"{t}: {i}" for t, i in self.inventory_towary_handlowe.items() if i > 0]) or "Brak"
        bonus_str = f"\nAktywny bonus: {self.opis_bonusu_do_umiejetnosci} (+{self.wartosc_bonusu_do_umiejetnosci} do testu)" if self.ma_bonus_do_umiejetnosci else ""
        return (f"\n--- Stan Postaci ---\nPoziom: {self.poziom}, XP: {self.xp}/{self.xp_do_nastepnego_poziomu}" +
                (f" (Punkty umiejętności: {self.punkty_umiejetnosci_do_wydania})" if self.punkty_umiejetnosci_do_wydania > 0 else "") +
                f"\nUmiejętności: {um_str}\nWytrzymałość: {w_d}/11\nGłód/Pragnienie: {gp_d}/11\nKomfort Psychiczny: {kp_d}/11\n" +
                f"Ekwipunek: Jedzenie: {self.inventory['jedzenie']}, Woda: {self.inventory['woda']}, Drewno: {self.inventory['drewno']}, Złoto: {self.inventory['zloto']}\n" +
                f"Cenne Znaleziska: {cenne_str}\nTowary Handlowe: {th_str}\nUdźwig: {self.aktualny_udzwig:.1f}/{self.maks_udzwig:.1f} kg\n" +
                f"Ogień: {'Tak' if self.ma_ogien else 'Nie'}, Schronienie: {'Tak' if self.ma_schronienie else 'Nie'}\n" +
                f"Dni w podróży: {int(self.dni_w_podrozy)}{bonus_str}")
    async def dodaj_xp(self, ilosc, game): # Zmienione by przyjmować game
        if ilosc <= 0: return
        self.xp += ilosc; print(f"Zdobywasz {ilosc} XP!")
        while self.xp >= self.xp_do_nastepnego_poziomu:
            self.poziom += 1; self.xp -= self.xp_do_nastepnego_poziomu
            self.xp_do_nastepnego_poziomu = int(self.xp_do_nastepnego_poziomu * 1.5)
            self.punkty_umiejetnosci_do_wydania += 1
            for p in ["wytrzymalosc", "glod_pragnienie", "komfort_psychiczny"]: setattr(self, p, min(11.0, getattr(self,p) + 0.5 if p=="wytrzymalosc" else getattr(self,p) + 0.2))
            print(f"AWANS! Poziom {self.poziom}! Otrzymujesz 1 pkt umiejętności. Następny za {self.xp_do_nastepnego_poziomu - self.xp} XP.")
            await game.sprawdz_odblokowanie_wiedzy() # NOWOŚĆ
            await async_input("Naciśnij Enter...")
            
    def zmien_potrzebe(self, potrzeba, wartosc, cicho=False):
        stara_wartosc = getattr(self, potrzeba, 0.0)
        oryginalna_wartosc_f = float(wartosc)
        wartosc_f = oryginalna_wartosc_f
        if wartosc_f < 0 and stara_wartosc >= 10.5: wartosc_f *= 0.8
        nowa_wartosc = max(1.0, min(11.0, stara_wartosc + wartosc_f))
        setattr(self, potrzeba, nowa_wartosc)
        if not cicho and abs(stara_wartosc - nowa_wartosc) > 0.01:
            zm_disp = f"{wartosc_f:+.1f}".replace(".0","")
            if wartosc_f != oryginalna_wartosc_f: zm_disp += " (zredukowany spadek dzięki wysokiemu zaspokojeniu potrzeby)"
            akt_disp = f"{nowa_wartosc:.1f}".replace(".0","")
            print(f" {potrzeba.replace('_',' ').capitalize()} {zm_disp} (do: {akt_disp}).")
    def oblicz_modyfikator_rzutu(self):
        stany = [self.wytrzymalosc, self.glod_pragnienie, self.komfort_psychiczny]
        neg = sum(1 for s in stany if s <= 3.0)
        poz = sum(1 for s in stany if s >= 9.0)
        mod = 0
        if neg > poz: mod = -min(2, neg - poz) if min(s for s in stany if s <= 3.0) <= 1.9 else -1
        elif poz > neg: mod = min(2, poz - neg) if max(s for s in stany if s >= 9.0) >= 11.0 else 1
        return mod
    def uzyj_bonusu_umiejetnosci(self):
        if self.ma_bonus_do_umiejetnosci:
            val = self.wartosc_bonusu_do_umiejetnosci
            print(f"Wykorzystujesz '{self.opis_bonusu_do_umiejetnosci}' (+{val})!")
            self.ma_bonus_do_umiejetnosci = False; self.wartosc_bonusu_do_umiejetnosci = 0; self.opis_bonusu_do_umiejetnosci = ""
            return val
        return 0
    def przyznaj_bonus_umiejetnosci(self, wartosc, opis):
        self.ma_bonus_do_umiejetnosci = True; self.wartosc_bonusu_do_umiejetnosci = wartosc; self.opis_bonusu_do_umiejetnosci = opis
        print(f"Otrzymujesz bonus '{opis}' (+{wartosc} do testu).")
    async def uplyw_czasu(self, game, godziny=1, opis_czynnosci=""): # Zmienione by przyjmować game
        if godziny <=0: return
        godz_f = float(godziny)
        mod_p_czas = max(0.5, 1.0 - (self.umiejetnosci["przetrwanie"] * 0.02))
        print(f"\nUpływa {godz_f if godz_f != int(godz_f) else int(godz_f)} godz. ({opis_czynnosci})...")
        self.godziny_w_tej_dobie += godz_f
        self.zmien_potrzebe("glod_pragnienie", -0.5 * godz_f * mod_p_czas, cicho=True)
        if not self.ma_ogien and self.lokacja_gracza != "Ukryta Dolina" and not self.ma_schronienie:
             self.zmien_potrzebe("komfort_psychiczny", -0.2 * godz_f * mod_p_czas, cicho=True)
        if self.godziny_w_tej_dobie >= 24.0:
            dni_f = self.godziny_w_tej_dobie / 24.0; dni_i = int(dni_f)
            self.dni_w_podrozy += dni_f; self.godziny_w_tej_dobie %= 24.0
            if dni_i > 0:
                 print(f"Mija {dni_i} dzień/dni. Jesteś w podróży od {int(self.dni_w_podrozy)} dni.");
                 await self.dodaj_xp(int(5 * dni_i), game)
                 await game.sprawdz_odblokowanie_wiedzy() # NOWOŚĆ
        epsilon = 0.5
        if self.wytrzymalosc <= 3.0 + epsilon and self.wytrzymalosc > 1.0: print("Jesteś bardzo zmęczony...")
        if self.glod_pragnienie <= 3.0 + epsilon and self.glod_pragnienie > 1.0: print("Dotkliwie odczuwasz głód i pragnienie.")
        if self.komfort_psychiczny <= 3.0 + epsilon and self.komfort_psychiczny > 1.0: print("Czujesz się bardzo niekomfortowo.")
    async def odpocznij(self, game, godziny, jakosc_snu_mod=0, koszt_czasu=True, w_wiosce=False):
        godz_f = float(godziny); print(f"Odpoczywasz przez {godz_f if godz_f != int(godz_f) else int(godz_f)} godzin.")
        regen = godz_f * (0.5 + jakosc_snu_mod * 0.5)
        if self.komfort_psychiczny < 4.0 and jakosc_snu_mod < 3 and not w_wiosce: regen *= 0.7; print("Trudno było wypocząć...")
        self.zmien_potrzebe("wytrzymalosc", regen)
        if w_wiosce and jakosc_snu_mod >=2: self.zmien_potrzebe("komfort_psychiczny", min(godz_f / 2.0, 3.0))
        if koszt_czasu: await self.uplyw_czasu(game, godz_f, "odpoczynek")
    async def jedz_z_ekwipunku(self, game):
        if self.inventory["jedzenie"] > 0:
            self.inventory["jedzenie"] -= 1; self.zmien_potrzebe("glod_pragnienie", 4.0)
            print("Zjadasz porcję jedzenia. Czujesz się pokrzepiony.")
            if random.random() < 0.15: self.zmien_potrzebe("komfort_psychiczny", 1.0); print("Ten posiłek był wyjątkowo smaczny!")
            await self.uplyw_czasu(game, 0.5, "jedzenie")
        else: print("Nie masz nic do jedzenia.")
    async def pij_z_ekwipunku(self, game):
        if self.inventory["woda"] > 0:
            self.inventory["woda"] -= 1; self.zmien_potrzebe("glod_pragnienie", 3.0)
            print("Pijesz wodę. Pragnienie nieco maleje.")
            await self.uplyw_czasu(game, 0.2, "picie wody")
        else: print("Nie masz nic do picia.")
    async def rozpal_ogien(self, game_instance):
        if self.inventory["drewno"] > 0:
            print("Próbujesz rozpalić ogień...")
            bonus_s = self.umiejetnosci["przetrwanie"] // 2 + self.uzyj_bonusu_umiejetnosci()
            trud_ognia = OBSZARY_DZICZY.get(self.lokacja_gracza, {}).get("trudnosc_ognia", 0.1)
            dodatkowa_trudnosc_z_mod = 0
            for mod_nazwa, mod_dane in game_instance.aktywne_modyfikatory_srodowiskowe.items():
                dodatkowa_trudnosc_z_mod += mod_dane.get("efekty", {}).get("modyfikator_akcji", {}).get("rozpal_ogien_prog", 0)
            if dodatkowa_trudnosc_z_mod > 0:
                print(f"Warunki ({', '.join(game_instance.aktywne_modyfikatory_srodowiskowe.keys())}) znacznie utrudniają zadanie.")
            prog = max(2, 4 + int(trud_ognia * 10) - bonus_s + dodatkowa_trudnosc_z_mod)
            rzut = Game.rzut_koscia(10)
            if rzut >= prog :
                self.inventory["drewno"] -= 1; self.ma_ogien = True; self.zmien_potrzebe("komfort_psychiczny", 2.0)
                print(f"Sukces! (Rzut: {rzut} vs Próg: {prog}). Rozpalasz ognisko."); await self.dodaj_xp(5, game_instance)
            else:
                print(f"Niestety, nie udaje się (Rzut: {rzut} vs Próg: {prog})."); self.inventory["drewno"] -= 1; self.zmien_potrzebe("wytrzymalosc",-0.5)
            await self.uplyw_czasu(game_instance, 0.5, "rozpalanie ognia")
        else: print("Nie masz drewna na opał.")
    async def zbuduj_schronienie(self, game):
        if self.inventory["drewno"] >=2:
            print("Próbujesz zbudować schronienie...")
            bonus_s = self.umiejetnosci["przetrwanie"] // 2 + self.uzyj_bonusu_umiejetnosci()
            prog = max(3, 6 - bonus_s)
            rzut = Game.rzut_koscia(10)
            if rzut >= prog:
                self.inventory["drewno"] -=2; self.ma_schronienie = True
                bonus_komf = 2.0 + (self.umiejetnosci["przetrwanie"] / 3.0) + (1.0 if rzut >= prog + 3 else 0.0)
                self.zmien_potrzebe("komfort_psychiczny", bonus_komf)
                print(f"Udało się! (Rzut: {rzut} vs Próg: {prog}). Czujesz się bezpieczniej."); await self.dodaj_xp(10, game)
            else:
                self.inventory["drewno"] -=1; print(f"Konstrukcja słaba (Rzut: {rzut} vs Próg: {prog}).")
            self.zmien_potrzebe("wytrzymalosc", -1.0); await self.uplyw_czasu(game, 1.5, "budowa schronienia")
        else: print("Za mało drewna.")

class Game:
    def __init__(self):
        self.player = Player()
        self.aktualny_etap_eksploracji_idx = 0; self.lokacje_w_aktualnym_etapie = 0
        self.max_lokacji_na_etap = 3; self.odkryte_typy_obszarow = set(); self.aktywne_zadanie = None
        self.nazwa_aktualnej_wioski = "Ukryta Dolina" # ZMIANA
        self.odkryte_wioski_lista_nazw = [self.nazwa_aktualnej_wioski]
        self.wioski_info = {self.nazwa_aktualnej_wioski: Village(self.nazwa_aktualnej_wioski)}
        self.cel_podrozy_nazwa_global = None; self.czy_daleka_podroz_global = False
        self.aktywne_modyfikatory_srodowiskowe = {}

    @staticmethod
    def rzut_koscia(k_max): return random.randint(1, k_max) if k_max > 0 else 0
    
    async def przyznaj_xp_za_odkrycie_obszaru(self, nazwa_obszaru):
        if nazwa_obszaru not in self.odkryte_typy_obszarow:
            xp = OBSZARY_DZICZY.get(nazwa_obszaru, {}).get("xp_za_odkrycie", 0)
            if xp > 0: print(f"Odkrywasz: {nazwa_obszaru}!"); await self.player.dodaj_xp(xp, self); self.odkryte_typy_obszarow.add(nazwa_obszaru)

    async def sprawdz_odblokowanie_wiedzy(self): # NOWA METODA
        for wiedza_id, dane in WIEDZA_DO_ODKRYCIA.items():
            if wiedza_id in self.player.odkryta_wiedza: continue
            
            warunek = dane["warunek"]
            spelniony = False
            if "przetrwanie" in warunek and self.player.umiejetnosci["przetrwanie"] >= warunek["przetrwanie"]: spelniony = True
            elif "zielarstwo_tropienie" in warunek and self.player.umiejetnosci["zielarstwo_tropienie"] >= warunek["zielarstwo_tropienie"]: spelniony = True
            elif "charyzma_handel" in warunek and self.player.umiejetnosci["charyzma_handel"] >= warunek["charyzma_handel"]: spelniony = True
            elif "odkryte_wioski" in warunek and len(self.odkryte_wioski_lista_nazw) >= warunek["odkryte_wioski"]: spelniony = True
            elif "przezyte_dni" in warunek and self.player.dni_w_podrozy >= warunek["przezyte_dni"]: spelniony = True
            elif "reputacja_total" in warunek and sum(self.player.reputacja.values()) >= warunek["reputacja_total"]: spelniony = True

            if spelniony:
                self.player.odkryta_wiedza.add(wiedza_id)
                print("\n" + "="*20)
                print("NOWA WIEDZA ZDOBYTA!")
                print(f"Twoje doświadczenia pozwoliły ci zrozumieć: '{dane['nazwa']}'")
                print(f"Opis: {dane['opis']}")
                print("Ta wiedza może pomóc rozwiązać problemy napotkanych społeczności.")
                print("="*20)
                await async_input("Naciśnij Enter...")

    async def _generuj_i_zastosuj_modyfikatory_srodowiskowe(self):
        self.aktywne_modyfikatory_srodowiskowe = {}
        if random.random() > 0.4:
            nazwa_mod = random.choice(list(MODYFIKATORY_SRODOWISKOWE.keys()))
            mod_dane = MODYFIKATORY_SRODOWISKOWE[nazwa_mod]
            self.aktywne_modyfikatory_srodowiskowe[nazwa_mod] = mod_dane
            print(f"\nWarunki pogodowe: {nazwa_mod}. {mod_dane['opis']}")
            if "zmien_potrzebe" in mod_dane["efekty"]:
                for potrzeba, wartosc in mod_dane["efekty"]["zmien_potrzebe"].items():
                    self.player.zmien_potrzebe(potrzeba, wartosc)
            if "nowe_wydarzenie" in mod_dane["efekty"]:
                event = mod_dane["efekty"]["nowe_wydarzenie"]
                if random.random() < event["szansa"]:
                    print(event["tekst"])
                    if event["akcja"] == "utrata_przedmiotu":
                        przedm = random.choice(["jedzenie", "woda", "drewno"])
                        if self.player.inventory[przedm] > 0:
                            self.player.inventory[przedm] -= 1
                            print(f"Tracisz 1 szt. {przedm}!")
            await async_input("Naciśnij Enter...")

    async def generuj_zadanie(self):
        if self.aktywne_zadanie: return
        rep = self.player.reputacja.get(self.nazwa_aktualnej_wioski, 0)
        typy = [{"typ": "przynies_skory_wilka", "cel": Game.rzut_koscia(2)+1, "xp": 60, "zloto": 45, "opis_f": "Starszy z {} potrzebuje skór wilków."},
                {"typ": "zbierz_ziola", "cel": Game.rzut_koscia(2)+2, "xp": 45, "zloto": 30, "opis_f": "Znachorka z {} prosi o rzadkie zioła."}]
        if rep >= 10: typy.append({"typ": "zbadaj_miejsce", "cel_lok": random.choice(["Stary Święty Gaj","Opuszczona Chata","Spalona Ziemia"]), "xp": 80, "zloto": 40, "opis_f": "Mieszkańcy {} są zaniepokojeni wieściami z {}."})
        if rep >= 20: typy.append({"typ": "upoluj_dzika", "cel": 1, "xp": 90, "zloto": 55, "opis_f": "Groźny dzik zagraża polom {}."})
        if not typy: return
        zad_def = random.choice(typy)
        self.aktywne_zadanie = {"typ": zad_def["typ"], "nagroda_xp": zad_def["xp"], "nagroda_zloto": zad_def["zloto"], "zleceniodawca_wioska": self.nazwa_aktualnej_wioski}
        if "cel_lok" in zad_def:
            self.aktywne_zadanie["opis"] = zad_def["opis_f"].format(self.nazwa_aktualnej_wioski, zad_def["cel_lok"])
            self.aktywne_zadanie["cel_lokacja"] = zad_def["cel_lok"]
            print(f"\nNowe zadanie: {self.aktywne_zadanie['opis']}\nCel: Zbadaj {zad_def['cel_lok']}")
        else:
            self.aktywne_zadanie["opis"] = zad_def["opis_f"].format(self.nazwa_aktualnej_wioski)
            self.aktywne_zadanie["cel_ilosc"] = zad_def["cel"]
            self.aktywne_zadanie["postep"] = 0
            print(f"\nNowe zadanie: {self.aktywne_zadanie['opis']}\nCel: zebrać {zad_def['cel']} (Masz: 0)")
            
    async def sprawdz_postep_zadania(self, typ_akcji, ilosc=1, dodatkowe_dane=None):
        if not self.aktywne_zadanie: return
        zad = self.aktywne_zadanie; ukonczone = False
        if zad["typ"] == "przynies_skory_wilka" and typ_akcji == "pokonano_wilka": zad["postep"] = min(zad["cel_ilosc"], zad["postep"] + ilosc); ukonczone = zad["postep"] >= zad["cel_ilosc"]
        # Poprawiona linia
        elif zad["typ"] == "zbierz_ziola" and typ_akcji == "zbierz_ziola": zad["postep"] = min(zad["cel_ilosc"], zad["postep"] + ilosc); ukonczone = zad["postep"] >= zad["cel_ilosc"]
        elif zad["typ"] == "upoluj_dzika" and typ_akcji == "pokonano_dzika": zad["postep"] = min(zad["cel_ilosc"], zad["postep"] + ilosc); ukonczone = zad["postep"] >= zad["cel_ilosc"]
        elif zad["typ"] == "zbadaj_miejsce" and typ_akcji == "zbadano_lokacje" and dodatkowe_dane and dodatkowe_dane.get("nazwa_lokacji") == zad["cel_lokacja"]:
            print(f"Zebrałeś info o {zad['cel_lokacja']}. Wróć do {zad['zleceniodawca_wioska']}."); zad["postep"] = 1
        if "postep" in zad and "cel_ilosc" in zad: print(f"Postęp w zadaniu '{zad['opis']}': {zad['postep']}/{zad['cel_ilosc']}")
        if ukonczone:
            print(f"\nUkończyłeś zadanie (ilościowe): {zad['opis']}!"); await self.player.dodaj_xp(zad["nagroda_xp"], self)
            self.player.inventory["zloto"] += zad["nagroda_zloto"]; print(f"Otrzymujesz {zad['nagroda_xp']} XP i {zad['nagroda_zloto']} złota.")
            self.player.reputacja[zad["zleceniodawca_wioska"]] = self.player.reputacja.get(zad["zleceniodawca_wioska"],0) + 5
            self.aktywne_zadanie = None
            
    async def menu_rozwoju_umiejetnosci(self):
        if self.player.punkty_umiejetnosci_do_wydania <= 0: print("Brak punktów umiejętności."); return
        while self.player.punkty_umiejetnosci_do_wydania > 0:
            print(f"\nMasz {self.player.punkty_umiejetnosci_do_wydania} pkt. Wybierz umiejętność:"); um_lista = list(self.player.umiejetnosci.keys())
            for i, um in enumerate(um_lista): print(f"{i+1}. {um.replace('_',' ').capitalize()} (Poziom: {self.player.umiejetnosci[um]})")
            print("0. Zakończ"); wybor = await async_input("> ")
            if not wybor.isdigit(): print("Nieprawidłowy wybór."); continue
            idx = int(wybor)
            if idx == 0: break
            if 1 <= idx <= len(um_lista):
                 um_wyb = um_lista[idx-1]
                 if self.player.umiejetnosci[um_wyb] < 10:
                    self.player.umiejetnosci[um_wyb] += 1; self.player.punkty_umiejetnosci_do_wydania -= 1
                    print(f"Rozwinięto {um_wyb.replace('_',' ').capitalize()} do {self.player.umiejetnosci[um_wyb]}.")
                    if um_wyb == "udzwig": self.player.maks_udzwig = self.player.oblicz_maks_udzwig(); print(f"Max udźwig: {self.player.maks_udzwig:.1f} kg.")
                    await self.sprawdz_odblokowanie_wiedzy() # NOWOŚĆ
                 else: print(f"{um_wyb.replace('_',' ').capitalize()} max poziom (10).")
            else: print("Nieprawidłowy numer.")
        print("Zakończono rozwój.")
        
    async def kup_towary_handlowe_w_wiosce(self, wioska_obj):
        print(wioska_obj.get_village_goods_info_str(self.player.umiejetnosci["charyzma_handel"]))
        while True:
            print("Wybierz towar do kupienia (0 aby wyjść):"); [print(f"  {i+1}. {t_n}") for i, t_n in enumerate(LISTA_PRODUKTOW_HANDLOWYCH)]
            w_idx_s = await async_input("> ");
            if not w_idx_s.isdigit(): print("Nieprawidłowy wybór."); continue
            w_idx = int(w_idx_s)
            if w_idx == 0: return
            if not (1 <= w_idx <= len(LISTA_PRODUKTOW_HANDLOWYCH)): print("Nieprawidłowy numer."); continue
            towar = LISTA_PRODUKTOW_HANDLOWYCH[w_idx-1]
            mnoz_zak = max(0.7, 1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03)
            cena_j = max(1, int(wioska_obj.ceny_produktow_finalne[towar]["kupno_od_wioski"] * mnoz_zak))
            waga_j = PRODUKTY_HANDLOWE_INFO[towar]["waga"]
            print(f"Wybrano: {towar}. Cena/szt: {cena_j} zł. Waga/szt: {waga_j} kg. Złoto: {self.player.inventory['zloto']}. Udźwig: {self.player.maks_udzwig - self.player.aktualny_udzwig:.1f} kg.")
            il_s = await async_input("Ile sztuk chcesz kupić? (0 anuluj) > ")
            if not il_s.isdigit(): print("Nieprawidłowa ilość."); continue
            il = int(il_s);
            if il == 0: continue;
            if il < 0: print("Ilość nie może być ujemna."); continue
            koszt_c = il * cena_j
            if self.player.inventory["zloto"] < koszt_c: print(f"Brak złota. Potrzeba {koszt_c}, masz {self.player.inventory['zloto']}."); continue
            if self.player.zmien_towar_handlowy(towar, il):
                self.player.inventory["zloto"] -= koszt_c; print(f"Kupiłeś {il} szt. '{towar.lower()}' za {koszt_c} zł.")
                await self.player.uplyw_czasu(self, 0.5, "handel towarami"); return
                
    async def sprzedaj_towary_handlowe_w_wiosce(self, wioska_obj):
        print(wioska_obj.get_village_goods_info_str(self.player.umiejetnosci["charyzma_handel"]))
        print("\nTwoje towary na sprzedaż:"); dostepne = []
        for t_n, il in self.player.inventory_towary_handlowe.items():
            if il > 0: dostepne.append(t_n); print(f"  {len(dostepne)}. {t_n} (Masz: {il})")
        if not dostepne: print("Brak towarów na sprzedaż."); return
        print("Wybierz towar (0 aby wyjść):"); w_idx_s = await async_input("> ")
        if not w_idx_s.isdigit(): print("Nieprawidłowy wybór."); return
        w_idx = int(w_idx_s)
        if w_idx == 0: return
        if not (1 <= w_idx <= len(dostepne)): print("Nieprawidłowy numer."); return
        towar = dostepne[w_idx-1]
        mnoz_sprz = 1.0 + self.player.umiejetnosci["charyzma_handel"] * 0.03
        cena_j = max(1, int(wioska_obj.ceny_produktow_finalne[towar]["sprzedaz_do_wioski"] * mnoz_sprz))
        print(f"Wybrano: {towar}. Wioska oferuje: {cena_j} zł/szt. Masz {self.player.inventory_towary_handlowe[towar]} szt.")
        il_s = await async_input(f"Ile '{towar.lower()}' sprzedać? (0 anuluj) > ")
        if not il_s.isdigit(): print("Nieprawidłowa ilość."); return
        il_sprz = int(il_s)
        if il_sprz == 0: return;
        if il_sprz < 0: print("Ilość nie może być ujemna."); return
        if il_sprz > self.player.inventory_towary_handlowe[towar]: print(f"Nie masz tyle. Masz {self.player.inventory_towary_handlowe[towar]}."); return
        if self.player.zmien_towar_handlowy(towar, -il_sprz):
            zysk_c = il_sprz * cena_j; self.player.inventory["zloto"] += zysk_c
            print(f"Sprzedałeś {il_sprz} szt. '{towar.lower()}' za {zysk_c} zł."); await self.player.uplyw_czasu(self, 0.5, "handel towarami")

    async def menu_podrozy_do_wioski(self):
        if len(self.odkryte_wioski_lista_nazw) <= 1:
            print("Nie odkryłeś jeszcze żadnych innych osad."); await async_input("Enter..."); return "kontynuuj_w_wiosce"
        curr_w_nazwa = self.player.lokacja_gracza
        try: curr_w_idx = self.odkryte_wioski_lista_nazw.index(curr_w_nazwa)
        except ValueError: print(f"Błąd: Aktualna wioska '{curr_w_nazwa}' nie na liście."); await async_input("Enter..."); return "kontynuuj_w_wiosce"
        
        podrozowalne = []
        for i, nazwa in enumerate(self.odkryte_wioski_lista_nazw):
            if nazwa != curr_w_nazwa: podrozowalne.append((nazwa, self.wioski_info[nazwa], i))
        
        if not podrozowalne: print("Brak innych odkrytych osad."); await async_input("Enter..."); return "kontynuuj_w_wiosce"
        
        podrozowalne.sort(key=lambda x: abs(x[2] - curr_w_idx))
        
        str_rozmiar = 6; akt_str = 0
        while True:
            print("\n--- Wybierz cel podróży ---"); pocz_idx = akt_str * str_rozmiar; kon_idx = pocz_idx + str_rozmiar
            wioski_na_stronie = podrozowalne[pocz_idx:kon_idx]
            if not wioski_na_stronie and akt_str > 0:
                akt_str -=1; pocz_idx = akt_str * str_rozmiar; kon_idx = pocz_idx + str_rozmiar
                wioski_na_stronie = podrozowalne[pocz_idx:kon_idx]
            if not wioski_na_stronie and akt_str == 0: print("Brak wiosek do wyświetlenia."); await async_input("Enter..."); return "kontynuuj_w_wiosce"

            for i, (nazwa, w_obj, _) in enumerate(wioski_na_stronie):
                podsum_aspektow = w_obj.get_aspekty_summary()
                czy_daleka = akt_str > 0
                print(f"{i+1}. {nazwa} {podsum_aspektow} {'(Podróż z utrudnieniem)' if czy_daleka else ''}")
            
            print("---")
            if akt_str > 0: print("p. Poprzednia strona")
            if kon_idx < len(podrozowalne): print("n. Następna strona")
            print("0. Powrót do wioski")
            wybor = await async_input("> "); wybor = wybor.strip().lower()

            if wybor == '0': return "kontynuuj_w_wiosce"
            elif wybor == 'n' and kon_idx < len(podrozowalne): akt_str += 1
            elif wybor == 'p' and akt_str > 0: akt_str -= 1
            elif wybor.isdigit():
                idx_wyb = int(wybor) - 1
                if 0 <= idx_wyb < len(wioski_na_stronie):
                    nazwa_celu, _, _ = wioski_na_stronie[idx_wyb]
                    czy_daleka_final = akt_str > 0
                    print(f"Wybrano podróż do: {nazwa_celu}{' z utrudnieniem.' if czy_daleka_final else '.'}")
                    potwierdzenie_input = await async_input("Potwierdź (t/n): ")
                    if potwierdzenie_input.strip().lower() == 't':
                                self.cel_podrozy_nazwa_global = nazwa_celu
                                self.czy_daleka_podroz_global = czy_daleka_final
                                return "rozpocznij_eksploracje_do_celu"
            else: print("Nieprawidłowy wybór.")
            await asyncio.sleep(0.01)

    async def petla_wioski(self):
        self.nazwa_aktualnej_wioski = self.player.lokacja_gracza
        if self.nazwa_aktualnej_wioski not in self.player.reputacja: self.player.reputacja[self.nazwa_aktualnej_wioski] = 0
        if self.nazwa_aktualnej_wioski not in self.wioski_info:
            print(f"KRYTYCZNY BŁĄD: Wioska {self.nazwa_aktualnej_wioski} nie w wioski_info!")
            self.wioski_info[self.nazwa_aktualnej_wioski] = Village(self.nazwa_aktualnej_wioski)
            if self.nazwa_aktualnej_wioski not in self.odkryte_wioski_lista_nazw: self.odkryte_wioski_lista_nazw.append(self.nazwa_aktualnej_wioski)
        akt_w_obj = self.wioski_info[self.nazwa_aktualnej_wioski]
        self.player.ma_ogien = False; self.player.ma_schronienie = False
        print(f"\n--- Jesteś w osadzie: {self.nazwa_aktualnej_wioski} ---");
        if self.nazwa_aktualnej_wioski != "Ukryta Dolina":
            print("Możesz tu odpocząć i przygotować się do drogi.")
            self.player.zmien_potrzebe("wytrzymalosc", 2.0, cicho=True); self.player.zmien_potrzebe("komfort_psychiczny", 1.0, cicho=True)
            print("Gościna w wiosce przynosi wytchnienie.")
        if not self.aktywne_zadanie and self.nazwa_aktualnej_wioski != "Ukryta Dolina" and random.random() < 0.6 + (self.player.reputacja.get(self.nazwa_aktualnej_wioski,0) * 0.01): await self.generuj_zadanie()

        while True:
            await asyncio.sleep(0.02); self.player.oblicz_aktualny_udzwig(); print(self.player)
            if self.aktywne_zadanie:
                zad = self.aktywne_zadanie; zad_prog = ""
                if 'cel_ilosc' in zad: zad_prog = f" (Postęp: {zad.get('postep','N/A')}/{zad.get('cel_ilosc','N/A')})"
                elif 'cel_lokacja' in zad and zad.get('postep') == 1: zad_prog = " (Raport gotowy)"
                print(f"Aktywne zadanie: {zad['opis']}{zad_prog}")
            
            # --- Menu ---
            print("\nCo chcesz zrobić?");
            menu_opcje = [
                ("1", "Odpocznij dobrze w chacie"), ("2", "Zjedz ciepły posiłek w karczmie"),
                ("3", "Napij się wody/naparu ziołowego"), ("4", "Kupuj podstawowe (Jedzenie/Woda/Drewno)"),
                ("5", "Odwiedź znachora/kapłana"), ("6", "Sprzedaj cenne znaleziska"),
                ("7", "Kupuj towary handlowe"), ("8", "Sprzedaj towary handlowe"),
                ("9", "Rozwiń Umiejętności"), ("10", "Zobacz swoją zdobytą wiedzę"), # NOWOŚĆ
                ("11", "Porozmawiaj ze Starszym Wioski"),
                ("12", "Wyrusz w dzicz (eksploruj)"), ("13", "Podróżuj do znanej osady"),
                ("s", "ZAPISZ GRĘ"), ("l", "WCZYTAJ GRĘ"),("0", "Zakończ grę")
            ]
            [print(f"{key}. {val}") for key, val in menu_opcje]
            wybor = await async_input("> "); wybor = wybor.strip().lower()

            if wybor == "1":
                if self.player.inventory["jedzenie"] > 0: self.player.inventory["jedzenie"] -=1; print("Solidnie odpoczniesz."); await self.player.odpocznij(self, 8, 3, True, True)
                else: print("Brak jedzenia na posiłek, odpoczniesz gorzej."); await self.player.odpocznij(self, 6, 2, True, True)
            elif wybor == "2":
                koszt = max(1, int(4 * (1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03)))
                if self.player.inventory["zloto"] >= koszt:
                    self.player.inventory["zloto"] -= koszt; self.player.zmien_potrzebe("glod_pragnienie", 5.0); self.player.zmien_potrzebe("komfort_psychiczny", 1.0)
                    print(f"Zjadasz pożywny posiłek za {koszt} zł."); await self.player.uplyw_czasu(self, 1, "posiłek w karczmie")
                else: print(f"Brak złota (koszt: {koszt}).")
            elif wybor == "3":
                koszt = max(1, int(2 * (1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03)))
                if self.player.inventory["zloto"] >= koszt:
                    self.player.inventory["zloto"] -= koszt; self.player.zmien_potrzebe("glod_pragnienie", 3.0)
                    print(f"Wypijasz napar za {koszt} zł."); await self.player.uplyw_czasu(self, 0.5, "napitek w karczmie")
                else: print(f"Brak złota (koszt: {koszt}).")
            elif wybor == "4":
                print("Co chcesz kupić?\n a. Jedzenie[3zł]\nb. Woda[2zł]\n c. Drewno[1zł]\n 0. Anuluj)"); wyb_zak = await async_input("> ")
                znizka = (1.0 - self.player.umiejetnosci["charyzma_handel"] * 0.03)
                if wyb_zak == 'a': koszt = max(1, int(3 * znizka)); towar_nazwa = "jedzenie"
                elif wyb_zak == 'b': koszt = max(1, int(2 * znizka)); towar_nazwa = "woda"
                elif wyb_zak == 'c': koszt = max(1, int(1 * znizka)); towar_nazwa = "drewno"
                else: towar_nazwa = None
                if towar_nazwa:
                    il_s = await async_input(f"Ile {towar_nazwa} (cena: {koszt}/szt)? "); il = int(il_s) if il_s.isdigit() else 0
                    if il > 0:
                        koszt_c = koszt * il
                        if self.player.inventory["zloto"] >= koszt_c: self.player.inventory[towar_nazwa] += il; self.player.inventory["zloto"] -= koszt_c; print(f"Kupiono {il} {towar_nazwa} za {koszt_c} zł."); await self.player.uplyw_czasu(self, 0.2, "zakupy")
                        else: print(f"Brak złota (potrzeba {koszt_c}).")
            elif wybor == "5":
                if self.player.inventory["zloto"] >= 5:
                    self.player.inventory["zloto"] -= 5; print("Składasz ofiarę znachorowi..."); await self.player.uplyw_czasu(self, 2, "wizyta u znachora")
                    if random.random() < 0.6: self.player.przyznaj_bonus_umiejetnosci(self.rzut_koscia(2)+1, "Błogosławieństwo"); self.player.zmien_potrzebe("komfort_psychiczny", 1.0)
                    else: print("Znachor mamrocze...")
                else: print("Brak złota na dary.")
            elif wybor == "6": await self.sprzedaj_cenne_przedmioty()
            elif wybor == "7": await self.kup_towary_handlowe_w_wiosce(akt_w_obj)
            elif wybor == "8": await self.sprzedaj_towary_handlowe_w_wiosce(akt_w_obj)
            elif wybor == "9": await self.menu_rozwoju_umiejetnosci()
            elif wybor == "10": await self.menu_wiedzy() # NOWOŚĆ
            elif wybor == "11":
                if self.nazwa_aktualnej_wioski == "Ukryta Dolina":
                    print("Starszyzna z twojej rodzinnej osady uśmiecha się, widząc twoje postępy.")
                    print("'Pamiętaj o naszej tradycji. Zdobywaj wiedzę, by wzmocnić naszą społeczność, gdy wrócisz na stałe.'")
                elif akt_w_obj.problem:
                    print(f"Starszy wioski wzdycha: '{akt_w_obj.problem['opis']}'")
                    if (await async_input("Chcesz spróbować pomóc? (t/n) > ")).lower() == 't':
                         await self.menu_pomocy_wiosce(akt_w_obj)
                else:
                     print("Starszy Wioski wita cię serdecznie. Wydaje się, że społeczność radzi sobie dobrze.")

                if self.aktywne_zadanie and self.aktywne_zadanie["zleceniodawca_wioska"] == self.nazwa_aktualnej_wioski:
                    zad = self.aktywne_zadanie; print(f"Starszy pyta o: {zad['opis']}")
                    if zad.get("typ") == "zbadaj_miejsce" and zad.get("postep") == 1:
                        print("Zdajesz raport."); await self.player.dodaj_xp(zad["nagroda_xp"], self); self.player.inventory["zloto"] += zad["nagroda_zloto"]
                        print(f"Otrzymujesz {zad['nagroda_xp']} XP i {zad['nagroda_zloto']} zł."); self.player.reputacja[self.nazwa_aktualnej_wioski] += 10; self.aktywne_zadanie = None
                    elif "cel_ilosc" in zad and zad.get("postep", 0) >= zad["cel_ilosc"]: print("Starszy dziękuje (już nagrodzone)."); self.aktywne_zadanie = None
                    else: print("Starszy zachęca do kontynuowania.")
                elif not self.aktywne_zadanie:
                    if self.nazwa_aktualnej_wioski != "Ukryta Dolina":
                        await self.generuj_zadanie() if random.random() < 0.7 + (self.player.reputacja.get(self.nazwa_aktualnej_wioski,0)*0.01) else print("Starszy nie ma dla ciebie żadnych zadań.")
                else: print(f"Starszy z {self.nazwa_aktualnej_wioski} nie ma zadań. Pamiętaj o zadaniu z {self.aktywne_zadanie['zleceniodawca_wioska']}.")

            elif wybor == "12":
                if self.player.wytrzymalosc <= 3.0 or self.player.glod_pragnienie <=3.0: print("Jesteś zbyt wyczerpany.")
                else: self.lokacje_w_aktualnym_etapie = 0; self.cel_podrozy_nazwa_global = None; self.czy_daleka_podroz_global = False; return "rozpocznij_eksploracje"
            elif wybor == "13":
                status_podr = await self.menu_podrozy_do_wioski()
                if status_podr == "rozpocznij_eksploracje_do_celu": return "rozpocznij_eksploracje_do_celu"
            elif wybor == "s": download_save(self); print("Stan gry zapisany (próba pobrania).")
            elif wybor == "l":
                json_str_input = await async_input("Wklej zawartość pliku save.json lub wpisz 'anuluj': ")
                if json_str_input.lower() != 'anuluj' and json_str_input.strip():
                    if load_state_from_json(self, json_str_input):
                        return "przeladuj_petle_wioski"
                else: print("Anulowano wczytywanie.")

            elif wybor == "0": print("Dziękujemy za grę!"); return "koniec_gry"
            else: print("Nieznana komenda.")
            if await self.sprawdz_stan_krytyczny("wioska"): return "koniec_gry"
        return "kontynuuj"

    async def menu_wiedzy(self): # NOWA METODA
        print("\n--- Twoja Zdobyta Wiedza ---")
        if not self.player.odkryta_wiedza:
            print("Twoja podróż dopiero się zaczęła. Wędruj, ucz się i przetrwaj, by zdobyć wiedzę, która pomoże innym.")
        else:
            print("Doświadczenia z podróży nauczyły cię:")
            for wiedza_id in sorted(list(self.player.odkryta_wiedza)):
                wiedza = WIEDZA_DO_ODKRYCIA.get(wiedza_id)
                if wiedza:
                    print(f"- [{wiedza['typ']}] {wiedza['nazwa']}: {wiedza['opis']}")
        print("--------------------------")
        await async_input("Naciśnij Enter, aby kontynuować...")
    
    async def menu_pomocy_wiosce(self, wioska_obj): # NOWA METODA
        print("\n--- Próba Pomocy Wiosce ---")
        if not wioska_obj.problem:
            print("Ta wioska zdaje się nie mieć obecnie żadnych poważnych problemów."); return
        
        print(f"Problem do rozwiązania: {wioska_obj.problem['opis']}")
        
        if not self.player.odkryta_wiedza:
            print("Niestety, nie posiadasz jeszcze wiedzy, która mogłaby im pomóc."); return

        print("\nWybierz rozwiązanie, które chcesz zaproponować:")
        dostepna_wiedza = []
        for i, wiedza_id in enumerate(sorted(list(self.player.odkryta_wiedza))):
            wiedza = WIEDZA_DO_ODKRYCIA[wiedza_id]
            dostepna_wiedza.append(wiedza_id)
            print(f"{i+1}. [{wiedza['typ']}] {wiedza['nazwa']}")
        print("0. Anuluj")
        
        wybor_s = await async_input("> ")
        if not wybor_s.isdigit(): print("Nieprawidłowy wybór."); return
        wybor = int(wybor_s)
        if not (0 < wybor <= len(dostepna_wiedza)): print("Anulowano."); return
        
        # Rzut na sukces
        await self.player.uplyw_czasu(self, 3, "pomoc wiosce")
        bonus_um = self.player.umiejetnosci['charyzma_handel'] + self.player.umiejetnosci['przetrwanie'] // 2
        prog = 15 - bonus_um
        rzut = self.rzut_koscia(20)
        print(f"Próbujesz wdrożyć swoje rozwiązanie... (Rzut K20: {rzut}, Próg sukcesu: {prog})")

        if rzut >= prog:
            print("\nPo zbadaniu tematu i wysłuchaniu społeczności wpadłeś na pomysł jak rozwiązać problem.")
            print("Twoja rada została przyjęta z nadzieją! Czas pokaże, czy przyniesie owoce.")
            print("Sukces! Udało ci się pomóc wiosce.")
            wioska_obj.rozwiaz_problem()
            await self.player.dodaj_xp(100, self)
            self.player.reputacja[wioska_obj.name] = self.player.reputacja.get(wioska_obj.name, 0) + 15
            self.player.zmien_potrzebe("komfort_psychiczny", 2.0)
        else:
            print("\nNiestety, mimo twoich starań, społeczność nie jest gotowa na zmiany lub twoje rozwiązanie okazało się nieodpowiednie.")
            print("Nie udało się. Może następnym razem...")
            self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
            self.player.reputacja[wioska_obj.name] = self.player.reputacja.get(wioska_obj.name, 0) - 2

        await async_input("Naciśnij Enter, aby kontynuować...")


    async def sprzedaj_cenne_przedmioty(self):
        print("\n--- Targowisko - Cenne Przedmioty ---");
        if not any(self.player.inventory_cenne.values()): print("Brak cennych przedmiotów."); return
        print("Dostępne na sprzedaż:"); lista_sprz = []
        for item, qty in self.player.inventory_cenne.items():
            if qty > 0:
                lista_sprz.append(item); cena_b = CENNE_PRZEDMIOTY_CENY.get(item, 0)
                cena_mod = int(cena_b * (1.0 + self.player.umiejetnosci["charyzma_handel"] * 0.03))
                print(f"{len(lista_sprz)}. {item.replace('_',' ').capitalize()} (Ilość: {qty}, Cena/szt: ~{cena_mod} zł)")
        print("0. Anuluj"); wyb_s = await async_input("> ")
        if not wyb_s.isdigit(): print("Podaj numer."); return
        idx = int(wyb_s)
        if idx == 0: return
        if 1 <= idx <= len(lista_sprz):
            nazwa_it = lista_sprz[idx-1]; il_it = self.player.inventory_cenne[nazwa_it]
            while True:
                il_s_s = await async_input(f"Ile {nazwa_it.replace('_',' ')} sprzedać (masz {il_it}, 0 - anuluj)? ")
                if not il_s_s.isdigit(): print("Podaj liczbę."); continue
                il_s = int(il_s_s)
                if il_s == 0: break
                if 0 < il_s <= il_it:
                    cena_b = CENNE_PRZEDMIOTY_CENY.get(nazwa_it, 0)
                    mnoz_c = (1.0 + self.player.umiejetnosci["charyzma_handel"] * 0.03)
                    cena_f_szt = max(1, int(cena_b * random.uniform(0.85, 1.15) * mnoz_c))
                    suma_zl = il_s * cena_f_szt
                    self.player.inventory_cenne[nazwa_it] -= il_s; self.player.inventory["zloto"] += suma_zl
                    print(f"Sprzedałeś {il_s} {nazwa_it.replace('_',' ')} za {suma_zl} zł ({cena_f_szt}/szt).")
                    await self.player.uplyw_czasu(self, 0.5, "handel na targu"); return
                else: print(f"Nieprawidłowa ilość. Masz {il_it}.")
        else: print("Nieprawidłowy numer.")

    async def petla_eksploracji(self, cel_podrozy_nazwa=None, czy_daleka_podroz=False):
        self.player.lokacja_gracza = "Dzicz"
        print(f"\n--- Wyruszasz w dzicz{' do celu: ' + cel_podrozy_nazwa if cel_podrozy_nazwa else ''}... ---")
        await async_input("Naciśnij Enter, aby kontynuować...")
        
        akt_etapy_ekspl = ETAPY_EKSPLORACJI
        if cel_podrozy_nazwa and czy_daleka_podroz:
            print("To daleka podróż, warunki będą trudniejsze."); await asyncio.sleep(0.01)
            akt_etapy_ekspl_kopia = []
            for etap_org in ETAPY_EKSPLORACJI:
                nowy_etap = etap_org.copy(); nowy_etap["szanse_na_wies"] = [max(0, s - 1) for s in etap_org["szanse_na_wies"]]
                akt_etapy_ekspl_kopia.append(nowy_etap)
            akt_etapy_ekspl = akt_etapy_ekspl_kopia
        
        max_etap_idx = len(akt_etapy_ekspl) - 1
        
        for _ in range(self.max_lokacji_na_etap):
            if await self.sprawdz_stan_krytyczny("dzicz_start_kroku"): return "koniec_gry"
            
            print(f"\n--- Dzień {int(self.player.dni_w_podrozy)+1} (Etap dziczy: {self.aktualny_etap_eksploracji_idx+1}, Krok: {self.lokacje_w_aktualnym_etapie+1}/{self.max_lokacji_na_etap}) ---")
            etap_idx = min(self.aktualny_etap_eksploracji_idx, max_etap_idx)
            etap = akt_etapy_ekspl[etap_idx]
            kosci_etapu = etap["kosci"]
            nr_w_kroku = self.lokacje_w_aktualnym_etapie % len(kosci_etapu)
            glowna_kosc = kosci_etapu[nr_w_kroku]
            
            print(self.player); print(f"Rzucasz K{glowna_kosc} w poszukiwaniu drogi..."); await asyncio.sleep(0.01)
            wynik_rzutu = self.rzut_koscia(glowna_kosc); print(f"Wynik rzutu: {wynik_rzutu} (na K{glowna_kosc})")
            
            koszt_wytrz = max(0.5, (self.rzut_koscia(2)+1) * (1.0 - self.player.umiejetnosci["przetrwanie"] * 0.05))
            self.player.zmien_potrzebe("wytrzymalosc", -koszt_wytrz, cicho=True)
            await self.player.uplyw_czasu(self, self.rzut_koscia(2) + 2, "poszukiwanie drogi")
            
            self.lokacje_w_aktualnym_etapie += 1
            
            if wynik_rzutu in etap["szanse_na_wies"]:
                if cel_podrozy_nazwa:
                    print(f"Po trudach podróży docierasz do celu: {cel_podrozy_nazwa}!"); self.player.lokacja_gracza = cel_podrozy_nazwa
                    if cel_podrozy_nazwa not in self.wioski_info: self.wioski_info[cel_podrozy_nazwa] = Village(cel_podrozy_nazwa)
                    if cel_podrozy_nazwa not in self.odkryte_wioski_lista_nazw: self.odkryte_wioski_lista_nazw.append(cel_podrozy_nazwa)
                    await self.player.dodaj_xp(20 + etap_idx * 5, self); return "znaleziono_wioske"
                else:
                    print("Niespodziewanie trafiasz na ślady prowadzące do osady!");
                    nowa_nazwa = f"OsadaNr{Game.rzut_koscia(100) + len(self.odkryte_wioski_lista_nazw)}"
                    if nowa_nazwa not in self.wioski_info:
                        self.wioski_info[nowa_nazwa] = Village(nowa_nazwa)
                        self.odkryte_wioski_lista_nazw.append(nowa_nazwa)
                        print(f"Odkryłeś nową osadę: {nowa_nazwa}!");
                        await self.player.dodaj_xp(50 + etap_idx * 10, self)
                        await self.sprawdz_odblokowanie_wiedzy() # NOWOŚĆ
                    else: print(f"Droga prowadzi do znanej osady: {nowa_nazwa}."); await self.player.dodaj_xp(10, self)
                    self.player.lokacja_gracza = nowa_nazwa
                    zloto = self.rzut_koscia(3)+self.rzut_koscia(3); self.player.inventory["zloto"] += zloto; print(f"Znajdujesz {zloto} złota.")
                    return "znaleziono_wioske"
            
            await self._generuj_i_zastosuj_modyfikatory_srodowiskowe()
            
            prog_poz_dyn = max(int(glowna_kosc * 0.6), glowna_kosc - 3)
            if wynik_rzutu >= prog_poz_dyn: print("Odkrywasz interesujący obszar!"); await self.obsluz_obszar_pozytywny()
            else:
                dost_obsz = [n for n, d in OBSZARY_DZICZY.items() if not d.get("pozytywny")] or list(OBSZARY_DZICZY.keys())
                nazwa_ob = random.choice(dost_obsz); self.player.lokacja_gracza = nazwa_ob
                await self.przyznaj_xp_za_odkrycie_obszaru(nazwa_ob); await self.obsluz_obszar_dziczy(nazwa_ob)
            
            if self.aktywne_zadanie and self.aktywne_zadanie["typ"] == "zbadaj_miejsce":
                await self.sprawdz_postep_zadania("zbadano_lokacje", dodatkowe_dane={"nazwa_lokacji": self.player.lokacja_gracza})
            
            status_akcji = await self.akcje_w_dziczy()
            if status_akcji == "koniec_gry": return "koniec_gry"
            if status_akcji == "kontynuuj": pass
            
            if self.player.ma_ogien and random.random() < 0.4: self.player.ma_ogien = False; self.player.zmien_potrzebe("komfort_psychiczny", -1.0); print("Ogień zgasł...")
            if self.player.ma_schronienie and random.random() < 0.15: self.player.ma_schronienie = False; self.player.zmien_potrzebe("komfort_psychiczny", -1.0); print("Schronienie uszkodzone.")

        if self.lokacje_w_aktualnym_etapie >= self.max_lokacji_na_etap:
            self.lokacje_w_aktualnym_etapie = 0
            if self.aktualny_etap_eksploracji_idx < max_etap_idx: self.aktualny_etap_eksploracji_idx +=1
            else: print("Zapuszczasz się w najgłębsze ostępy dziczy...")
            print(f"Wkraczasz w nowy rejon dziczy (Etap {self.aktualny_etap_eksploracji_idx + 1}).")
        
        self.player.lokacja_gracza = "Dzicz"
        return "kontynuuj_eksploracje"

    async def obsluz_obszar_pozytywny(self):
        poz_obsz = [n for n,d in OBSZARY_DZICZY.items() if d.get("pozytywny")] or list(OBSZARY_DZICZY.keys())
        nazwa_ob = random.choice(poz_obsz); self.player.lokacja_gracza = nazwa_ob
        await self.przyznaj_xp_za_odkrycie_obszaru(nazwa_ob); obszar = OBSZARY_DZICZY[nazwa_ob]
        print(f"\nWchodzisz na: {nazwa_ob}. {obszar['opis']}"); await asyncio.sleep(0.01); await async_input("Enter...")
        for pot, bon in obszar.get("bonusy_przy_wejsciu", {}).items(): self.player.zmien_potrzebe(pot, bon)
        await self.przeszukaj_obszar_dokladnie(obszar, "przybycie_pozytywny"); await self.losowe_wydarzenie_pozytywne(obszar)
        
    async def obsluz_obszar_dziczy(self, nazwa_obszaru):
        obszar = OBSZARY_DZICZY[nazwa_obszaru]
        print(f"\nWchodzisz na: {nazwa_obszaru}. {obszar['opis']}"); await asyncio.sleep(0.01); await async_input("Enter...")
        for pot, kar in obszar.get("kary_przy_wejsciu", {}).items(): self.player.zmien_potrzebe(pot, kar)
        await self.przeszukaj_obszar_dokladnie(obszar, "przybycie_negatywny"); await self.losowe_wydarzenie_negatywne(obszar)
        
    async def przeszukaj_obszar_dokladnie(self, obszar_dane, kontekst=""):
        if kontekst == "akcja_gracza":
            print("Dokładnie przeszukujesz okolicę..."); czas = self.rzut_koscia(2)+2; await self.player.uplyw_czasu(self, czas, "przeszukiwanie")
            self.player.zmien_potrzebe("wytrzymalosc", -(czas / (1.5 + self.player.umiejetnosci["przetrwanie"]*0.1)))
            szansa_mod = 1.0
        else: print("Rozglądasz się pobieżnie..."); szansa_mod = 0.5
        znaleziono = False; bonus_syt = self.player.uzyj_bonusu_umiejetnosci() if kontekst == "akcja_gracza" else 0
        bonus_ziel = self.player.umiejetnosci["zielarstwo_tropienie"] * 0.05
        for zas, (max_il, sz) in obszar_dane.get("zasoby", {}).items():
            if random.random() < (sz + bonus_ziel) * szansa_mod + (bonus_syt * 0.05):
                il_b = self.rzut_koscia(int(max_il)) if max_il >= 1 else (1 if random.random() < max_il else 0)
                il = max(1, int(il_b * (1.0 + bonus_ziel))) if il_b > 0 else 0
                if il > 0:
                    znaleziono = True
                    if "drewno" in zas: self.player.inventory["drewno"] += il; print(f"Znajdujesz {il} drewna.")
                    elif "jedzenie" in zas: self.player.inventory["jedzenie"] += il; print(f"Zbierasz {il} pożywienia ({zas.replace('_',' ')})."); await self.sprawdz_postep_zadania("zbierz_ziola" if "rzadkie_zioło" in zas else "", il)
                    elif "woda" in zas: self.player.inventory["woda"] += il; print(f"Napełniasz bukłaki {il} wodą ({zas.replace('_',' ')})."); print("Woda mętna." if "brudna" in zas else "")
                    elif zas in self.player.inventory_cenne: self.player.inventory_cenne[zas] += il; print(f"Odkrywasz {il} {zas.replace('_',' ')}!"); await self.sprawdz_postep_zadania("zbierz_ziola" if zas == "rzadkie_zioło_lecznicze" else "", il)
                    elif "resztki_narzedzi" in zas: print(f"Znajdujesz {il} resztek narzędzi.");
        if kontekst == "akcja_gracza":
            if random.random() < 0.20 + (bonus_syt * 0.05) + (self.player.umiejetnosci["zielarstwo_tropienie"] * 0.02): await self.spotkanie_ze_zwierzeciem(False); znaleziono = True
            if random.random() < 0.15 + (bonus_syt * 0.03) + (self.player.umiejetnosci["zielarstwo_tropienie"] * 0.01):
                print("Coś niezwykłego przykuwa uwagę...");
                if random.random() < 0.5 and "fragment_mapy" in self.player.inventory_cenne: self.player.inventory_cenne["fragment_mapy"] += 1; print("Kolejny fragment mapy!"); await self.player.dodaj_xp(15, self)
                else: zl_ex = self.rzut_koscia(5)+2; self.player.inventory["zloto"] += zl_ex; print(f"Ukryta sakiewka z {zl_ex} monetami!")
                znaleziono = True
        if not znaleziono and kontekst == "akcja_gracza": print("Niczego szczególnego nie znajdujesz.")
        elif not znaleziono: print("Niczego od razu nie widać.")
        
    async def losowe_wydarzenie_negatywne(self, obszar):
        wyd_ob = obszar.get("wydarzenia_specjalne", []); moz_wyd = ["nic_szczegolnego", "minus_potrzeby", "uraz"] + wyd_ob
        wyd = random.choice(moz_wyd); print("\nZdarzenie losowe:"); await asyncio.sleep(0.01)
        if wyd == "nic_szczegolnego": print("Względny spokój.")
        elif wyd == "aura_demonow": print(obszar.get("opis_demonow", "Mroczna obecność...")); self.player.zmien_potrzebe("komfort_psychiczny", -self.rzut_koscia(3))
        elif wyd == "dzikie_zwierze": await self.spotkanie_ze_zwierzeciem(True)
        elif wyd == "minus_potrzeby": pot = random.choice(["wytrzymalosc", "glod_pragnienie", "komfort_psychiczny"]); self.player.zmien_potrzebe(pot, -self.rzut_koscia(2))
        elif wyd == "uraz": print("Potykasz się..."); self.player.zmien_potrzebe("wytrzymalosc", -1.0); self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
        elif wyd in ["slady_bestii", "obserwacja", "odglosy_bagien", "szelest"]: print("Niepokojące znaki..."); self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
        elif wyd == "uciqzliwe_insekty": print("Chmary insektów..."); self.player.zmien_potrzebe("komfort_psychiczny", -self.rzut_koscia(2)); self.player.zmien_potrzebe("wytrzymalosc", -1.0)
        elif wyd == "silny_wiatr":
            print("Porywisty wiatr...")
            self.player.zmien_potrzebe("wytrzymalosc", -1.0)
            if not self.player.ma_schronienie and not self.player.ma_ogien:
                self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
        elif wyd == "mgla":
            print("Gęsta mgła...")
            self.player.zmien_potrzebe("komfort_psychiczny",-1.0)
            if self.player.ma_ogien: print("Ogień ledwo się tli.")
        elif wyd == "kamienne_kregi":
            print("Stary kamienny krąg...")
            self.player.zmien_potrzebe("komfort_psychiczny", -self.rzut_koscia(2))
            if random.random() < 0.2: print("Kamienie się poruszyły..."); self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
        elif wyd == "znalezisko_w_pogorzelisku":
            print("Przeszukując zgliszcza, znajdujesz coś.")
            if random.random() < 0.3: zl = self.rzut_koscia(6); self.player.inventory["zloto"] += zl; print(f"Nadpalona sakiewka z {zl} monet!")
            elif random.random() < 0.2 and "fragment_mapy" in self.player.inventory_cenne: self.player.inventory_cenne["fragment_mapy"] += 1; print("Osmalony fragment mapy!"); await self.player.dodaj_xp(15, self)
            else: print("Bezwartościowe resztki."); self.player.zmien_potrzebe("komfort_psychiczny", -0.5)
        elif wyd == "ekstremalne_temperatury":
            if random.random() < 0.5: print("Słońce praży."); self.player.zmien_potrzebe("wytrzymalosc", -1.5); self.player.zmien_potrzebe("glod_pragnienie", -1.0)
            else: print("Gwałtowny spadek temperatury."); self.player.zmien_potrzebe("wytrzymalosc", -1.0); self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
        elif wyd == "burza_piaskowa":
            print("Gwałtowny wiatr z piaskiem."); self.player.zmien_potrzebe("wytrzymalosc", -2.0); self.player.zmien_potrzebe("komfort_psychiczny", -1.5); self.player.zmien_potrzebe("glod_pragnienie", -1.0)
            if random.random() < 0.2: przedm = random.choice(["jedzenie", "woda", "drewno"]);
            if self.player.inventory[przedm] > 0: self.player.inventory[przedm] -= 1; print(f"Wiatr porywa część {przedm}!")
        elif wyd == "poczucie_straty" or wyd == "poczucie_osamotnienia": print("Ogarnia Cię przygnębienie."); self.player.zmien_potrzebe("komfort_psychiczny", -1.5)
        await async_input("Enter...");
        
    async def losowe_wydarzenie_pozytywne(self, obszar):
        wyd_ob = obszar.get("wydarzenia_specjalne", []); moz_wyd = ["nic_specjalnego"] + wyd_ob
        wyd = random.choice(moz_wyd); print("\nZdarzenie losowe (pozytywne):"); await asyncio.sleep(0.01)
        if wyd == "nic_specjalnego": print("Cieszysz się chwilą spokoju.")
        elif wyd == "znalezisko_ziola_lecznicze":
            print("Napotykasz kępę rzadkich ziół."); self.player.zmien_potrzebe("wytrzymalosc", self.rzut_koscia(2)+1.0); self.player.zmien_potrzebe("komfort_psychiczny",1.0)
            if "rzadkie_zioło_lecznicze" in self.player.inventory_cenne: self.player.inventory_cenne["rzadkie_zioło_lecznicze"] +=1; await self.sprawdz_postep_zadania("zbierz_ziola",1)
        elif wyd == "chwila_kontemplacji": print("Miejsce na zadumę. Spokój koi nerwy."); self.player.zmien_potrzebe("komfort_psychiczny", self.rzut_koscia(2)+1.0); await self.player.dodaj_xp(5, self)
        elif wyd == "przychylnosc_duchow_gaju": print("Duchy spoglądają łaskawie."); self.player.przyznaj_bonus_umiejetnosci(self.rzut_koscia(2)+1, "Przychylność Duchów"); self.player.zmien_potrzebe("komfort_psychiczny",1.0); await self.player.dodaj_xp(10, self)
        elif wyd == "niepokojace_znalezisko_w_chacie":
            print("W kącie chaty znajdujesz stare zapiski..."); self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
            if random.random() < 0.2 and "fragment_mapy" in self.player.inventory_cenne: self.player.inventory_cenne["fragment_mapy"] += 1; print("Wśród zapisków znajdujesz fragment mapy!"); await self.player.dodaj_xp(15, self)
        elif wyd == "schronienie_przed_deszczem": print("Zaczyna padać. Na szczęście znajdujesz schronienie."); self.player.zmien_potrzebe("komfort_psychiczny",1.0)
        elif wyd == "slady_walki":
            print("Odnajdujesz ślady walki...")
            if random.random() < 0.3: zl = self.rzut_koscia(4); self.player.inventory["zloto"] += zl; print(f"Przy szczątkach znajdujesz {zl} złota!")
        await async_input("Enter...");
        
    async def spotkanie_ze_zwierzeciem(self, agresywne=False):
        zwierzeta = {"wilk": (5,2,5,True,2,10),"dzik":(7,3,4,True,3,15),"niedźwiedź":(12,4,3,True,5,30),"jeleń":(4,1,8,False,3,5),"lis":(3,1,7,False,1,3),"borsuk":(4,2,6,True,1,8)}
        nazwa_zw = random.choice(list(zwierzeta.keys())); hp, atk, ucieczka_prog, agres, jedz_drop, xp_drop = zwierzeta[nazwa_zw]
        if agresywne: agres = True
        print(f"Na drodze staje {nazwa_zw}!"); await asyncio.sleep(0.01)
        if not agres and random.random() < 0.6: print(f"{nazwa_zw.capitalize()} odchodzi."); await self.player.uplyw_czasu(self, 0.5, "obserwacja"); return
        print(f"{nazwa_zw.capitalize()} wygląda niespokojnie" + (" i gotowe do ataku!" if agres else "."))
        while True:
            decyzja = await async_input("Co robisz? (walcz / odstrasz / uciekaj / obserwuj) > "); dec = decyzja.lower().strip().replace("spróbuj_","")
            if dec in ["walcz", "odstrasz", "uciekaj", "obserwuj"]: break;
            print("Nieznana komenda.")
        await self.player.uplyw_czasu(self, 0.5, "konfrontacja")
        mod_sily = self.player.oblicz_modyfikator_rzutu() // 2 + self.player.umiejetnosci["walka"] //3 + self.player.uzyj_bonusu_umiejetnosci()
        if dec == "uciekaj":
            print("Próbujesz uciec..."); await asyncio.sleep(0.01); rzut = self.rzut_koscia(10) + mod_sily
            if rzut >= ucieczka_prog: print("Udało się!"); self.player.zmien_potrzebe("wytrzymalosc", -1.0)
            else: print("Nie udało się!"); await self.walka(nazwa_zw, hp, atk, jedz_drop, xp_drop)
        elif dec == "odstrasz":
            print("Próbujesz odstraszyć..."); await asyncio.sleep(0.01); rzut = self.rzut_koscia(10) + mod_sily + (2 if self.player.ma_ogien else 0)
            if rzut >= 7: print(f"{nazwa_zw.capitalize()} odchodzi (Rzut: {rzut} vs 7)."); self.player.zmien_potrzebe("wytrzymalosc",-1.0); await self.player.dodaj_xp(xp_drop // 3, self)
            else: print(f"Próby rozzłościły {nazwa_zw} (Rzut: {rzut} vs 7)!"); await self.walka(nazwa_zw, hp, atk, jedz_drop, xp_drop)
        elif dec == "walcz": await self.walka(nazwa_zw, hp, atk, jedz_drop, xp_drop)
        elif dec == "obserwuj":
            print("Obserwujesz..."); await asyncio.sleep(0.01)
            if not agres and random.random() < 0.7: print(f"{nazwa_zw.capitalize()} odchodzi.")
            else: print(f"Bierność ośmieliła {nazwa_zw}. Atakuje!"); await self.walka(nazwa_zw, hp, atk, jedz_drop, xp_drop)
            
    async def walka(self, przeciwnik_nazwa, hp_przeciwnika, atak_przeciwnika, jedzenie_drop, xp_za_pokonanie):
        print(f"\n--- Walka z {przeciwnik_nazwa}! ---"); await asyncio.sleep(0.01); runda = 0
        while hp_przeciwnika > 0 and self.player.wytrzymalosc > 1.0:
            runda += 1; print(f"\n--- Runda {runda} ---")
            w_d = int(self.player.wytrzymalosc) if self.player.wytrzymalosc == int(self.player.wytrzymalosc) else f"{self.player.wytrzymalosc:.1f}"
            print(f"Twoja Wytrzymałość: {w_d}, {przeciwnik_nazwa.capitalize()} HP: {hp_przeciwnika}")
            mod_gr_walka = self.player.oblicz_modyfikator_rzutu(); bonus_um_walka = self.player.umiejetnosci["walka"] // 2
            print("\nTwoja tura:");
            while True:
                akcja = await async_input("Akcja: (atak / blok / precyzyjny_atak) > ")
                akcja = akcja.strip().lower()
                if akcja in ["atak","blok","precyzyjny_atak"]: break; print("Nieznana akcja.")
            traf = False; obr_gr = 0
            if akcja == "atak":
                rzut = self.rzut_koscia(10) + mod_gr_walka + bonus_um_walka + (1 if self.player.wytrzymalosc > 7 else 0)
                if rzut >= 6: traf = True; obr_gr = self.rzut_koscia(4) + bonus_um_walka + (1 if self.player.wytrzymalosc > 8 else 0)
                self.player.zmien_potrzebe("wytrzymalosc", -1.0, True); print(f"Rzut na atak (K10+mod={mod_gr_walka}+um={bonus_um_walka}): {rzut}")
            elif akcja == "precyzyjny_atak":
                rzut = self.rzut_koscia(10) + mod_gr_walka + bonus_um_walka -1
                if rzut >= 7: traf = True; obr_gr = self.rzut_koscia(6) + bonus_um_walka + 1 + (1 if self.player.wytrzymalosc > 8 else 0)
                self.player.zmien_potrzebe("wytrzymalosc", -1.5, True); print(f"Rzut na precyzyjny (K10+mod={mod_gr_walka}+um={bonus_um_walka}-1): {rzut}")
            elif akcja == "blok": print("Przygotowujesz się do obrony..."); self.player.zmien_potrzebe("wytrzymalosc", -0.5, True)
            if traf: hp_przeciwnika -= obr_gr; print(f"Trafiasz {przeciwnik_nazwa}, -{obr_gr} HP. HP wroga: {max(0,hp_przeciwnika)}")
            elif akcja != "blok": print(f"Chybiasz {przeciwnik_nazwa}.")
            await asyncio.sleep(0.01)
            if hp_przeciwnika <= 0:
                print(f"\nPokonujesz {przeciwnik_nazwa}!"); await self.player.dodaj_xp(xp_za_pokonanie, self)
                self.player.inventory["jedzenie"] += jedzenie_drop; self.player.inventory["zloto"] += self.rzut_koscia(xp_za_pokonanie//10 +1)-1
                print(f"Zdobywasz {jedzenie_drop} mięsa.");
                if przeciwnik_nazwa=="wilk": await self.sprawdz_postep_zadania("pokonano_wilka",1)
                elif przeciwnik_nazwa=="dzik": await self.sprawdz_postep_zadania("upoluj_dzika",1)
                self.player.zmien_potrzebe("komfort_psychiczny", 1.0); await self.player.uplyw_czasu(self, 0.5, "oporządzenie zdobyczy"); return
            if self.player.wytrzymalosc <= 1.0: print("Jesteś zbyt wyczerpany..."); break
            print(f"\nTura {przeciwnik_nazwa}:"); await asyncio.sleep(0.01)
            rzut_w = self.rzut_koscia(10); prog_w = 5 - (2 if akcja=="blok" else 0) - (bonus_um_walka//2)
            if rzut_w >= prog_w:
                print(f"{przeciwnik_nazwa.capitalize()} atakuje i trafia" + (" mimo bloku!" if akcja=="blok" and rzut_w>=5 else "!"))
                obr_w = max(1, atak_przeciwnika - (1 if akcja=="blok" else 0) - (bonus_um_walka//3))
                self.player.zmien_potrzebe("wytrzymalosc", -obr_w);
                if self.player.wytrzymalosc < 4.0: self.player.zmien_potrzebe("komfort_psychiczny", -1.0)
            else: print(f"{przeciwnik_nazwa.capitalize()} chybia" + (" dzięki blokowi!" if akcja=="blok" else "!"))
            await self.player.uplyw_czasu(self, 0.2, "runda walki")
            if await self.sprawdz_stan_krytyczny("walka"): return
        if hp_przeciwnika > 0 and self.player.wytrzymalosc <=1.0:
            print(f"{przeciwnik_nazwa.capitalize()} powala Cię..."); self.player.zmien_potrzebe("komfort_psychiczny", -3.0)
            utr_zl = self.rzut_koscia(self.player.inventory["zloto"]//2 if self.player.inventory["zloto"] > 0 else 0)
            self.player.inventory["zloto"] = max(0, self.player.inventory["zloto"] - utr_zl)
            print(f"Gubisz {utr_zl} złota."); await self.player.uplyw_czasu(self, self.rzut_koscia(4), "dochodzenie do siebie")
            
    async def akcje_w_dziczy(self):
        while True:
            await asyncio.sleep(0.01); print(self.player)
            print(f"\nJesteś w: {self.player.lokacja_gracza}. Co robić?"); opcje = ["Ruszaj dalej", "Odpocznij", "Zjedz", "Napij się",
                f"Rozpal ogień (Drewno:{self.player.inventory['drewno']}, Ogień:{'Jest' if self.player.ma_ogien else 'Brak'})",
                f"Zbuduj schronienie (Drewno:{self.player.inventory['drewno']}, Schronienie:{'Jest' if self.player.ma_schronienie else 'Brak'})",
                "Przeszukaj okolicę", "Nic nie rób"]
            for i, op in enumerate(opcje): print(f"{i+1}. {op}")
            wyb = await async_input("> "); wyb = wyb.strip()
            if wyb == "1": return "kontynuuj"
            elif wyb == "2":
                jak_snu = 0;
                if self.player.ma_schronienie and self.player.ma_ogien: jak_snu=3
                elif self.player.ma_schronienie: jak_snu=2
                elif self.player.ma_ogien: jak_snu=1
                await self.player.odpocznij(self, self.rzut_koscia(4 if jak_snu > 0 else 3) + (2 if jak_snu > 0 else 1), jak_snu)
            elif wyb == "3": await self.player.jedz_z_ekwipunku(self)
            elif wyb == "4": await self.player.pij_z_ekwipunku(self)
            elif wyb == "5": await self.player.rozpal_ogien(self) if not self.player.ma_ogien else print("Ogień już płonie.")
            elif wyb == "6":
                if not self.player.ma_schronienie: await self.player.zbuduj_schronienie(self)
                else:
                    print("Masz schronienie.");
                    if self.player.inventory["drewno"] > 0 and (await async_input("Poprawić schronienie (t/n)? ")).lower().strip() == 't':
                        self.player.inventory["drewno"]-=1; self.player.zmien_potrzebe("komfort_psychiczny",0.5); await self.player.uplyw_czasu(self, 0.5, "poprawa schronienia"); print("Poprawiono.")
            elif wyb == "7":
                ob_d = OBSZARY_DZICZY.get(self.player.lokacja_gracza)
                if ob_d: await self.przeszukaj_obszar_dokladnie(ob_d, "akcja_gracza")
                else: print("Nieznane miejsce..."); await self.player.uplyw_czasu(self, 1, "bezowocne poszukiwania")
            elif wyb == "8": print("Czekasz chwilę..."); await self.player.uplyw_czasu(self, 1, "oczekiwanie")
            else: print("Nieznana komenda.")
            if await self.sprawdz_stan_krytyczny("po_akcji_w_dziczy"): return "koniec_gry"
            
    async def sprawdz_stan_krytyczny(self, kontekst=""):
        kryt = False; wiad = ""; eps = 0.01
        w_k = self.player.wytrzymalosc <= 1.0 + eps; gp_k = self.player.glod_pragnienie <= 1.0 + eps; kp_k = self.player.komfort_psychiczny <= 1.0 + eps
        w_n = self.player.wytrzymalosc <= 2.0 + eps; gp_n = self.player.glod_pragnienie <= 2.0 + eps; kp_n = self.player.komfort_psychiczny <= 2.0 + eps
        if w_k and gp_k and kp_k: kryt=True; wiad="Jesteś na skraju..."
        elif w_k and (gp_n or kp_n): kryt=True; wiad="Padłeś z wyczerpania..."
        elif gp_k and (w_n or kp_n): kryt=True; wiad="Głód i pragnienie odebrały siły..."
        elif kp_k and (w_n or gp_n): kryt=True; wiad="Duch złamany..."
        if kryt:
            print(f"\n--- KONIEC GRY ({kontekst}) ---"); print(wiad)
            print(f"Twoja próba inicjacji dobiegła końca po {int(self.player.dni_w_podrozy)} dniach na {self.player.poziom} poziomie."); return True
        return False
        
    async def start_gry(self):
        print("+" + "-"*70 + "+\n| Witaj w 'Słowiańska Dzicz' (X wiek) |\n" + "+" + "-"*70 + "+")
        print("\nW twojej osadzie, 'Ukrytej Dolinie', panuje stary zwyczaj.")
        print("Gdy młody człowiek osiąga wiek dojrzały, nie przechodzi próby w wiosce,")
        print("lecz jest zabierany w głąb dziczy i pozostawiany sam sobie.")
        print("To nie jest kara, a inicjacja. Twoim zadaniem jest przetrwać,")
        print("zdobyć wiedzę o świecie i siłę, by stać się pełnoprawnym członkiem społeczności,")
        print("który może ją wspierać. Twoja podróż właśnie się rozpoczyna.")
        print("\nPowodzenia, wędrowcze!")
        await async_input("\nNaciśnij Enter, aby rozpocząć...")
        
        if self.player.lokacja_gracza not in self.wioski_info: self.wioski_info[self.player.lokacja_gracza] = Village(self.player.lokacja_gracza)
        if self.player.lokacja_gracza not in self.odkryte_wioski_lista_nazw: self.odkryte_wioski_lista_nazw.append(self.player.lokacja_gracza)

        status_petli = "kontynuuj_glowna_petle"
        while status_petli != "koniec_gry":
            if status_petli == "przeladuj_petle_wioski":
                self.nazwa_aktualnej_wioski = self.player.lokacja_gracza
                status_petli = await self.petla_wioski()
            elif status_petli == "rozpocznij_eksploracje_do_celu":
                if self.cel_podrozy_nazwa_global:
                    status_petli = await self.petla_eksploracji(self.cel_podrozy_nazwa_global, self.czy_daleka_podroz_global)
                    self.cel_podrozy_nazwa_global = None; self.czy_daleka_podroz_global = False
                    if status_petli == "znaleziono_wioske": status_petli = "kontynuuj_glowna_petle"
                else: print("Błąd: Cel podróży nie ustawiony."); status_petli = "kontynuuj_glowna_petle"
            elif self.player.lokacja_gracza == "Dzicz" or status_petli == "rozpocznij_eksploracje" or status_petli == "kontynuuj_eksploracje":
                 status_petli = await self.petla_eksploracji(self.cel_podrozy_nazwa_global, self.czy_daleka_podroz_global)
                 if status_petli == "znaleziono_wioske": status_petli = "kontynuuj_glowna_petle"
            elif self.player.lokacja_gracza != "Dzicz":
                 wynik_wioski = await self.petla_wioski()
                 if wynik_wioski == "rozpocznij_eksploracje": self.player.lokacja_gracza = "Dzicz"; self.cel_podrozy_nazwa_global = None; status_petli = "kontynuuj_glowna_petle"
                 elif wynik_wioski == "rozpocznij_eksploracje_do_celu": status_petli = "rozpocznij_eksploracje_do_celu"
                 elif wynik_wioski == "koniec_gry": status_petli = "koniec_gry"
                 elif wynik_wioski == "przeladuj_petle_wioski": status_petli = "przeladuj_petle_wioski"
                 else: status_petli = "kontynuuj_glowna_petle"
            elif status_petli == "kontynuuj_glowna_petle": pass
            else:
                print(f"Nieznany status pętli: {status_petli}. Zakończenie gry.")
                status_petli = "koniec_gry"
            await asyncio.sleep(0.01)

        print("\n--- OSTATECZNY STAN POSTACI ---"); print(self.player)

# --- Główny Punkt Wejścia (dla Pyodide) ---
async def run_game_async_entry_point():
    """Asynchroniczny punkt wejścia do gry, wywoływany z JavaScript."""
    random.seed()
    game = Game()
    globals()["game"] = game
    await game.start_gry()

# Lokalny test (poza Pyodide)
# if __name__ == "__main__":
#     def mock_js_print(s): print(s, end='')
#     async def mock_js_input(prompt=""): return input(prompt)
#     js_print_function = mock_js_print
#     js_request_input_function = mock_js_input
#     asyncio.run(run_game_async_entry_point())
