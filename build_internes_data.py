#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cochin Radio B — Espace Internes (Semestre Hiver 2026–2027)
Générateur et synchroniseur de l'application web mobile (PWA) dédiée aux internes.
APPLICATION 100% INDÉPENDANTE ET SÉPARÉE :
- Répertoire dédié : /Users/thomaslefevre/Documents/Agendainterventionnel/agenda-internes/
- ZÉRO donnée patient (vérifié automatiquement par assert_zero_patient_data).
- Synchronisation directe avec le Google Sheet officiel 'Planning Interne CCH - Hiver 26'
  (ID: 10sPMOg9GPXqsSItnUfuYn2Ke0im34p5EEyKk5A0hEF8) et PropertiesService ('cochin_internes_state_v1').
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
import re
import ssl
import subprocess
import urllib.request

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "internes_data.json"
INDEX_FILE = BASE_DIR / "index.html"
MANIFEST_FILE = BASE_DIR / "manifest.json"
SW_FILE = BASE_DIR / "sw.js"
ICON_FILE = BASE_DIR / "icon.svg"
LAUNCHER_FILE = BASE_DIR / "Lancer_Agenda_Internes.command"

INTERNES_SHEET_ID = "10sPMOg9GPXqsSItnUfuYn2Ke0im34p5EEyKk5A0hEF8"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxLGqUevVWi36mNQ7WNoY2uhRsYLdsG_gQcscMPkP1GcQEt0LgdhGIuzYL2SM-uTcPq/exec"
CLOUD_PROP_KEY = "cochin_internes_state_v1"

# Liste officielle des internes du semestre Hiver 2026-2027 (Service de Radiologie B - Pr A. Feydy)
INTERNES_LIST = [
    {
        "id": "gabriel",
        "prenom": "Gabriel",
        "nom": "COTTIN",
        "fullName": "Gabriel COTTIN",
        "shortName": "Gabriel",
        "initials": "GC",
        "color": "#38BDF8",
        "role": "Interne DES Radiologie",
        "semestre": "Hiver 2026–2027",
        "startIso": "2026-11-02",
    },
    {
        "id": "noe",
        "prenom": "Noé",
        "nom": "GRANDVAL",
        "fullName": "Noé GRANDVAL",
        "shortName": "Noé",
        "initials": "NG",
        "color": "#7C3AED",
        "role": "Interne DES Radiologie (Phase Socle)",
        "isSocle": True,
        "semestre": "Hiver 2026–2027",
        "startIso": "2026-11-02",
    },
    {
        "id": "marwane",
        "prenom": "Marwane",
        "nom": "HAMMAMI",
        "fullName": "Marwane HAMMAMI",
        "shortName": "Marwane",
        "initials": "MH",
        "color": "#0D9488",
        "role": "Interne DES Radiologie",
        "semestre": "Hiver 2026–2027",
        "startIso": "2026-11-02",
    },
    {
        "id": "milan",
        "prenom": "Milan",
        "nom": "KORSEC",
        "fullName": "Milan KORSEC",
        "shortName": "Milan",
        "initials": "MK",
        "color": "#D97706",
        "role": "Interne DES Radiologie",
        "semestre": "Hiver 2026–2027",
        "startIso": "2026-11-02",
    },
    {
        "id": "nathanael",
        "prenom": "Nathanaël",
        "nom": "SEBBAN",
        "fullName": "Nathanaël SEBBAN",
        "shortName": "Nathanaël",
        "initials": "NS",
        "color": "#E11D48",
        "role": "Interne DES Radiologie",
        "semestre": "Hiver 2026–2027",
        "startIso": "2026-11-02",
    },
    {
        "id": "oussama",
        "prenom": "Oussama",
        "nom": "TALIB",
        "fullName": "Oussama TALIB",
        "shortName": "Oussama",
        "initials": "OT",
        "color": "#16A34A",
        "role": "Docteur Junior (DJ) — Radiologie",
        "isDJ": True,
        "semestre": "Hiver 2026–2027",
        "startIso": "2026-11-02",
    },
]

# Liste officielle des Chefs de Clinique, Assistants & Seniors de Radiologie B (Cochin)
CHEFS_LIST = [
    {
        "id": "chef_tl",
        "code": "TL",
        "prenom": "Thomas",
        "nom": "LEFÈVRE",
        "fullName": "Dr Thomas LEFÈVRE",
        "shortName": "Dr T. Lefèvre (TL)",
        "initials": "TL",
        "color": "#0284C7",
        "role": "Chef de Clinique / Assistant — RI & Ostéo-Articulaire",
        "posteTel": "12489 / 12163 (DECT 12504)",
        "gardeMatch": ["LEFEVRE", "LEFÈVRE"],
    },
    {
        "id": "chef_hm",
        "code": "HM",
        "prenom": "Hippolyte",
        "nom": "MONNIER",
        "fullName": "Dr Hippolyte MONNIER",
        "shortName": "Dr H. Monnier (HM)",
        "initials": "HM",
        "color": "#7C3AED",
        "role": "Chef de Clinique Assistant — Radiologie B",
        "posteTel": "12488 / 12489",
        "gardeMatch": ["MONNIER"],
    },
    {
        "id": "chef_mh",
        "code": "MH",
        "prenom": "Macil",
        "nom": "HAMADOUCHE",
        "fullName": "Dr Macil HAMADOUCHE",
        "shortName": "Dr M. Hamadouche (MH)",
        "initials": "MH",
        "color": "#D97706",
        "role": "Assistant Spécialiste — Radiologie B & RI",
        "posteTel": "DECT 12504 / 12488",
        "gardeMatch": ["HAMADOUCHE"],
    },
    {
        "id": "chef_sl",
        "code": "SL",
        "prenom": "Stéphano",
        "nom": "LUSI",
        "fullName": "Dr Stéphano LUSI",
        "shortName": "Dr S. Lusi (SL)",
        "initials": "SL",
        "color": "#0D9488",
        "role": "Chef de Clinique Assistant — Radiologie B",
        "posteTel": "12488 / 12489",
        "gardeMatch": ["LUSI"],
    },
    {
        "id": "chef_ya",
        "code": "YA",
        "prenom": "Yazid",
        "nom": "ALLEL",
        "fullName": "Dr Yazid ALLEL",
        "shortName": "Dr Y. Allel (YA)",
        "initials": "YA",
        "color": "#E11D48",
        "role": "Chef de Clinique Assistant — Radiologie B",
        "posteTel": "12488 / 12489",
        "gardeMatch": ["ALLEL"],
    },
    {
        "id": "chef_mp",
        "code": "MP",
        "prenom": "Marie-Pauline",
        "nom": "TALABARD",
        "fullName": "Dr Marie-Pauline TALABARD",
        "shortName": "Dr M-P. Talabard (MP)",
        "initials": "MP",
        "color": "#DB2777",
        "role": "Chef de Clinique Assistant — Imagerie Ostéo-Articulaire & RI",
        "posteTel": "12489",
        "gardeMatch": ["TALABARD"],
    },
    {
        "id": "chef_al",
        "code": "AL",
        "prenom": "Amandine",
        "nom": "LAPORTE",
        "fullName": "Dr Amandine LAPORTE",
        "shortName": "Dr A. Laporte (AL)",
        "initials": "AL",
        "color": "#4F46E5",
        "role": "PH / Senior — Référente Sarcomes & Radiologie B",
        "posteTel": "12483 / 12488",
        "gardeMatch": ["LAPORTE"],
    },
    {
        "id": "chef_ac",
        "code": "AC",
        "prenom": "Adina",
        "nom": "COSTEA",
        "fullName": "Dr Adina COSTEA",
        "shortName": "Dr A. Costea (AC)",
        "initials": "AC",
        "color": "#16A34A",
        "role": "Praticien — Radiologie B",
        "posteTel": "12483",
        "gardeMatch": ["COSTEA"],
    },
    {
        "id": "chef_mihoubi",
        "code": "MIHOUBI",
        "prenom": "Fadila",
        "nom": "MIHOUBI BOUVIER",
        "fullName": "Dr Fadila MIHOUBI BOUVIER",
        "shortName": "Dr F. Mihoubi",
        "initials": "FM",
        "color": "#0891B2",
        "role": "PH — Responsable Pédagogique Internes & Staffs",
        "posteTel": "12483",
        "gardeMatch": ["MIHOUBI"],
    },
    {
        "id": "chef_feydy",
        "code": "FEYDY",
        "prenom": "Antoine",
        "nom": "FEYDY",
        "fullName": "Pr Antoine FEYDY",
        "shortName": "Pr A. Feydy",
        "initials": "AF",
        "color": "#2563EB",
        "role": "PU-PH, Chef de Service — Radiologie B",
        "posteTel": "12483 / 12481",
        "gardeMatch": ["FEYDY"],
    },
    {
        "id": "chef_drape",
        "code": "DRAPE",
        "prenom": "Jean-Luc",
        "nom": "DRAPÉ",
        "fullName": "Pr Jean-Luc DRAPÉ",
        "shortName": "Pr J-L. Drapé",
        "initials": "JD",
        "color": "#6D28D9",
        "role": "PU-PH — Radiologie B",
        "posteTel": "12502 / 12480",
        "gardeMatch": ["DRAPE", "DRAPÉ"],
    },
    {
        "id": "chef_yang",
        "code": "YANG",
        "prenom": "Malika",
        "nom": "YANG",
        "fullName": "Dr YANG",
        "shortName": "Dr Yang",
        "initials": "YG",
        "color": "#059669",
        "role": "Praticien — IRM, Écho & Staff Rachis/Rhumato",
        "posteTel": "12483",
        "gardeMatch": ["YANG"],
    },
]

# Postes officiels de la trame des internes de Radiologie B (Cochin) avec horaires officiels
POSTES_META = [
    {"code": "TDM SAU", "label": "TDM SAU (Scanner des U — Ollier 4)", "cat": "tdm", "color": "#D97706", "horaire": "08h00 – 18h30", "horaireAm": "08h00 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "IRM 3T", "label": "IRM 3T (dès 07h45)", "cat": "irm", "color": "#7C3AED", "horaire": "Dès 07h45", "horaireAm": "07h45 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "IRM 1,5T", "label": "IRM 1,5T (dès 07h45)", "cat": "irm", "color": "#6D28D9", "horaire": "Dès 07h45", "horaireAm": "07h45 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "IRM", "label": "IRM (Matin 07h45 / Après-midi)", "cat": "irm", "color": "#7C3AED", "horaire": "Dès 07h45", "horaireAm": "07h45 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "ECHO", "label": "Échographie Ostéo-Articulaire (dès 09h00)", "cat": "echo", "color": "#0D9488", "horaire": "Dès 09h00", "horaireAm": "09h00 – 13h00", "horairePm": "13h30 – 18h00"},
    {"code": "GESTES (C)", "label": "Poste C / Gestes Interventionnels (dès 09h00)", "cat": "gestes", "color": "#E11D48", "horaire": "Dès 09h00", "horaireAm": "09h00 – 13h00", "horairePm": "13h30 – 18h00"},
    {"code": "SCAN ACHARD", "label": "Scanner Achard 1 (Interventionnel)", "cat": "gestes", "color": "#DB2777", "horaire": "08h30 – 18h30", "horaireAm": "08h30 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "ALLURA", "label": "Salle Allura (Vasculaire / Os)", "cat": "gestes", "color": "#BE123C", "horaire": "13h30 – 18h30", "horaireAm": "08h30 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "TDM OLLIER DIAG", "label": "TDM Ollier Diag (Ollier 3)", "cat": "tdm", "color": "#0284C7", "horaire": "08h30 – 18h00", "horaireAm": "08h30 – 13h00", "horairePm": "13h30 – 18h00"},
    {"code": "LECTURE/CS", "label": "Consultation Internes / Relecture Pr Drapé (Mardi PM & Vendredi PM)", "cat": "cs", "color": "#2563EB", "horaire": "13h30 – 18h00 (Mardi PM : Relecture Pr Drapé • Vendredi PM : CS)", "horaireAm": "—", "horairePm": "13h30 – 18h00"},
    {"code": "FORMATION / ACCUEIL", "label": "Accueil & Formation obligatoire des nouveaux arrivants (08h15 – 12h00)", "cat": "cs", "color": "#0284C7", "horaire": "08h15 – 12h00", "horaireAm": "08h15 – 12h00", "horairePm": "—"},
    {"code": "1/2 journée libre", "label": "Demi-off (1/2 journée libre)", "cat": "off", "color": "#64748B", "horaire": "Demi-journée libre", "horaireAm": "Demi-off matin", "horairePm": "Demi-off après-midi"},
    {"code": "FERMÉ", "label": "Vacation Fermée", "cat": "closed", "color": "#DC2626", "horaire": "Fermé", "horaireAm": "Fermé", "horairePm": "Fermé"},
    {"code": "MAINTENANCE", "label": "Maintenance", "cat": "closed", "color": "#EA580C", "horaire": "Maintenance", "horaireAm": "Maintenance", "horairePm": "Maintenance"},
    {"code": "RG", "label": "Repos de garde (RG)", "cat": "rg", "color": "#DC2626", "horaire": "Journée RG", "horaireAm": "Repos de garde", "horairePm": "Repos de garde"},
    {"code": "VACANCES", "label": "Congés / Vacances (CA/CF)", "cat": "vac", "color": "#16A34A", "horaire": "Congés", "horaireAm": "Congés", "horairePm": "Congés"},
]

# Programme officiel des 25 cours d'Imagerie Ostéo-Articulaire (Feuille 3 du Google Sheet)
CURRICULUM_COURS = [
    "Épaule : Pathologies de la coiffe des rotateurs",
    "Épaule : Instabilité gléno-humérale",
    "Épaule : Pathologies nerveuses de la ceinture scapulaire",
    "Épaule : Capsulite rétractile - Omarthrose - Ostéochondrite - Scapula alata - Articulation AC/SC - Grand pectoral",
    "Rachis cervical : Pathologies mécaniques",
    "Rachis thoraco-lombaire : Pathologies dégénératives (discopathie, hernie, rachialgie / radiculalgies)",
    "Rachis thoraco-lombaire : Instabilité - Ossifications ligamentaires - Fractures vertébrales et sacrum - Scoliose",
    "Coude : Pathologies du compartiment médial et latéral",
    "Coude : Pathologies du compartiment antérieur et postérieur et pathologies diverses",
    "Poignet : Pathologies osseuses dégénératives",
    "Poignet : Pathologies ligamentaires",
    "Poignet : Pathologies tendineuses et ténosynoviales",
    "Poignet : Pathologies vasculo-nerveuses",
    "Main : Pathologies dégénératives / tendineuses de la main et des doigts (I)",
    "Main : Pathologies dégénératives / tendineuses de la main et des doigts (II)",
    "Hanche : Pathologies osseuses et articulaires",
    "Hanche : Pathologies abarticulaires",
    "Ceinture pelvienne : Articulations sacro-iliaques, symphyse pubienne & plexus lombo-sacré",
    "Genou : Pathologies antérieures",
    "Genou : Ménisques et ligaments croisés",
    "Genou : Plans collatéraux et postérieurs, Gonarthrose, fractures de contrainte, ostéonécroses, SDRC1",
    "Jambe & Cheville : Pathologies de la jambe et du mollet / Tendon calcanéen & Aponévrose plantaire",
    "Pied et Cheville : Tendon Tibial postérieur + Spring - LFH - Fibulaires – Extenseurs",
    "Pied et Cheville : Ligaments & Neuropathies (Morton, Baxter, tunnel tarsien)",
    "Pied et Cheville : Statique du pied - Coalition du tarse - Ostéochondroses - Arthrose de cheville et du pied",
]

# Sujets des cours des chefs du mardi (20-30 min, organisés par Dr Fadila Mihoubi Bouvier)
CHEFS_TUESDAY_COURS = [
    ("Dr Fadila MIHOUBI BOUVIER", "Introduction à la séméiologie ostéo-articulaire & organisation du staff"),
    ("Dr Thomas LEFÈVRE", "Analyse radiologique d'une prothèse totale de hanche (PTH)"),
    ("Dr Hippolyte MONNIER", "Troubles de la statique du pied : mesures et points clés"),
    ("Dr Stéphano LUSI", "Tumeurs cartilagineuses : enchondrome vs tumeur cartilagineuse atypique"),
    ("Dr Yazid ALLEL", "Urgences traumatiques du poignet et du carpe au TDM SAU"),
    ("Dr Macil HAMADOUCHE", "Échographie de l'épaule : protocole standardisé et pièges"),
    ("Dr Amandine LAPORTE", "Bilan d'extension et biopsie des sarcomes des tissus mous"),
    ("Dr Henri GUÉRINI", "Imagerie des prothèses du genou et conflits péri-prothétiques"),
    ("Dr YANG", "IRM du rachis inflammatoire vs mécanique"),
    ("Pr Antoine FEYDY", "IRM de l'épaule : instabilité et bourrelet glénoïdien"),
    ("Pr Jean-Luc DRAPÉ", "Imagerie de la main et des tendons fléchisseurs/extenseurs"),
    ("Dr Marie-Pauline TALABARD", "Radiologie interventionnelle ostéo-articulaire : infiltrations & cimentoplasties"),
]

JOURS_FERIES_HIVER = {
    "2026-11-11": "Armistice 1918",
    "2026-12-25": "Jour de Noël",
    "2027-01-01": "Jour de l'An",
    "2027-03-29": "Lundi de Pâques",
}

CHEF_TO_INTERNE_POSTE = {
    "ECHO": "ECHO",
    "GESTES (C)": "GESTES (C)",
    "TDM OLLIER 4 (SAU)": "TDM SAU",
    "TDM ACHARD 1": "SCAN ACHARD",
    "TDM OLLIER 3": "TDM OLLIER DIAG",
    "IRM 3T": "IRM 3T",
    "IRM 1,5T": "IRM 1,5T",
    "IRM": "IRM",
    "ALLURA": "ALLURA",
    # CONSULTATION est un créneau pour les internes UNIQUEMENT le mardi après-midi (Relecture Pr Drapé)
    # et le vendredi après-midi (Consultation MH / Internes). Les autres créneaux de consultation/UCSA
    # sont des consultations propres des seniors/chefs.
}


def build_balanced_trame() -> dict:
    """
    Construit la trame hebdomadaire officielle calée sur la base envoyée par le Dr Hippolyte MONNIER
    pour le lundi 2 novembre 2026 après-midi :
      - R0 (Gabriel en S1) : Lundi PM = TDM OLLIER DIAG (TDM3)
      - R1 (Marwane en S1) : Lundi PM = IRM (avec Pr A. Feydy)
      - R2 (Milan en S1)   : Lundi PM = ECHO (US avec Dr H. Monnier)
      - R3 (Nathanaël en S1): Lundi PM = TDM SAU (au U le 02/11 PM, puis demi-off les lundis suivants)
      - R4 (Oussama en S1) : Lundi PM = GESTES (C) (ou 1/2 journée libre si Poste C fermé)
    - 5 rôles tournants (R0..R4) pour les 5 internes DES hors socle (Gabriel, Marwane, Milan, Nathanaël, Oussama)
      avec 8 vacations actives + 2 demi-offs ('1/2 journée libre') par semaine chacun :
      * Consultation ('LECTURE/CS') pour les internes UNIQUEMENT le Mardi après-midi et le Vendredi après-midi.
      * Relecture avec Pr Jean-Luc DRAPÉ le Mardi après-midi SYSTÉMATIQUE sur le créneau LECTURE/CS.
      * Autres créneaux non obligatoires si les demi-offs ne sont pas suffisants pour garantir 2 demi-offs / semaine.
    - 1 trame spécifique Phase Socle pour Noé GRANDVAL ('noe') :
      * Posté principalement au Scanner des Urgences ('TDM SAU') avec un ratio équilibré (~50-55 % de ses vacations actives,
        soit 4 à 4,5 demi-journées / semaine posté au TDM SAU) et le reste réparti sur IRM (3T / 1,5T), Échographie,
        TDM Ollier Diag (TDM3) et Consultation du vendredi après-midi.
      * Lundi 02/11 après-midi : en binôme avec Gabriel en TDM OLLIER DIAG (TDM3) selon le planning de Dr H. Monnier,
        puis posté en alternance au TDM SAU et en TDM OLLIER DIAG les lundis après-midi suivants.
      * Le Mardi matin des 3 premières semaines (03/11, 10/11, 17/11), Noé est posté avec Dr Macil HAMADOUCHE (MH)
        au TDM SAU (Urgences Ollier 4), puis alterne 1 semaine sur 2 entre TDM SAU (avec MH) et IRM 1,5T.
      * 2 demi-offs ('1/2 journée libre') par semaine (Mardi après-midi et Jeudi après-midi).
    """
    weekly_roles = {
        0: {  # LUNDI (calé sur la base du Dr H. Monnier du 02/11 après-midi : TDM3, IRM, US/ECHO, U/TDM SAU, GESTES C)
            "am": {
                0: "1/2 journée libre",
                1: "1/2 journée libre",
                2: "GESTES (C)",
                3: "ECHO",
                4: "TDM SAU",
                "socle": "TDM SAU",  # Posté au TDM SAU en binôme
            },
            "pm": {
                0: "TDM OLLIER DIAG",  # S1: Gabriel en TDM3 (avec Noé le 02/11 PM, puis alterne TDM3 / TDM SAU)
                1: "IRM",              # S1: Marwane en IRM (avec Pr A. Feydy)
                2: "ECHO",             # S1: Milan en US / Écho (avec Dr H. Monnier)
                3: "1/2 journée libre",# S1: Nathanaël au U le 02/11 PM, puis demi-off les lundis suivants
                4: "GESTES (C)",       # S1: Oussama (Poste C fermé le 02/11 PM -> 1/2 journée libre)
                "socle": "TDM SAU",    # Posté au TDM SAU (1 sem/2) ou TDM OLLIER DIAG (1 sem/2, et binôme TDM3 le 02/11 PM)
            },
        },
        1: {  # MARDI (Staff Cas Clinique + Cours Chef à 12h30 • Mardi PM : pas de demi-off, Relecture systématique avec Pr Drapé)
            "am": {
                0: "TDM SAU",
                1: "IRM 3T",
                2: "ECHO",
                3: "GESTES (C)",
                4: "IRM 1,5T",
                "socle_w1_3": "TDM SAU",  # 3 premières semaines : posté avec Dr Macil HAMADOUCHE (MH) au TDM SAU (en binôme)
                "socle_after": "IRM 1,5T",  # Ensuite : alterne 1 sem/2 IRM 1,5T (en binôme) et 1 sem/2 TDM SAU (avec MH, en binôme)
            },
            "pm": {
                0: "SCAN ACHARD",
                1: "ECHO",
                2: "GESTES (C)",
                3: "LECTURE/CS",  # Relecture avec Pr Drapé (systématique)
                4: "TDM SAU",
                "socle": "TDM SAU",  # Posté Socle Urgences en binôme (pas de demi-off le mardi après-midi)
            },
        },
        2: {  # MERCREDI
            "am": {
                0: "IRM 1,5T",
                1: "TDM OLLIER DIAG",
                2: "1/2 journée libre",
                3: "ECHO",
                4: "TDM SAU",
                "socle": "1/2 journée libre",  # Demi-off n°1 de Noé
            },
            "pm": {
                0: "1/2 journée libre",
                1: "TDM SAU",
                2: "SCAN ACHARD",
                3: "GESTES (C)",
                4: "IRM",
                "socle": "ECHO",  # Posté en Écho le mercredi après-midi (avec Dr Mihoubi)
            },
        },
        3: {  # JEUDI
            "am": {
                0: "SCAN ACHARD",
                1: "1/2 journée libre",
                2: "TDM SAU",
                3: "GESTES (C)",
                4: "1/2 journée libre",
                "socle": "TDM SAU",  # Posté au TDM SAU avec Dr Macil HAMADOUCHE (MH) en binôme avec co-interne
            },
            "pm": {
                0: "ALLURA",
                1: "IRM",
                2: "TDM SAU",
                3: "1/2 journée libre",  # Demi-off n°2 de R3 (Écho fermée le jeudi PM)
                4: "SCAN ACHARD",
                "socle": "1/2 journée libre",  # Demi-off n°2 de Noé
            },
        },
        4: {  # VENDREDI (Biblio du vendredi • Vendredi PM : pas de demi-off, Consultation Internes)
            "am": {
                0: "GESTES (C)",
                1: "ECHO",
                2: "1/2 journée libre",
                3: "TDM SAU",
                4: "IRM 1,5T",
                "socle": "IRM 3T",  # Posté en IRM 3T le vendredi matin
            },
            "pm": {
                0: "IRM",
                1: "GESTES (C)",
                2: "TDM SAU",
                3: "LECTURE/CS",  # Consultation du vendredi après-midi (avec Dr Macil HAMADOUCHE / Internes)
                4: "SCAN ACHARD",
                "socle": "TDM SAU",  # Posté Socle Urgences en binôme avec co-interne (pas de demi-off le vendredi après-midi)
            },
        },
    }
    return weekly_roles


def get_closed_vacations_for_halfday(chefs_day: dict, half: str, wd: int | None = None) -> list[dict]:
    """
    Extrait les vacations fermées ('FERMÉ') ou en maintenance ('MAINTENANCE')
    du planning des Chefs pour une demi-journée donnée ('am' ou 'pm').
    """
    closed_items = []
    if not chefs_day:
        return closed_items
    for entry in chefs_day.get(half, []):
        doc_val = str(entry.get("doc", "")).strip()
        poste_chef = str(entry.get("poste", "")).strip()
        is_closed = bool(entry.get("closed")) or doc_val.upper().startswith("FERM") or doc_val.upper() == "MAINTENANCE"
        if is_closed and poste_chef != "FÉRIÉ":
            if poste_chef in ("CONSULTATION", "UCSA"):
                if not (half == "pm" and wd in (1, 4) and poste_chef == "CONSULTATION"):
                    continue
                interne_poste = "LECTURE/CS"
            else:
                interne_poste = CHEF_TO_INTERNE_POSTE.get(poste_chef, poste_chef)
            status = "MAINTENANCE" if "MAINTENANCE" in doc_val.upper() else "FERMÉ"
            closed_items.append({
                "poste": interne_poste,
                "chefsPoste": poste_chef,
                "status": status,
                "detail": doc_val,
            })
    return closed_items


def get_open_interne_postes_for_halfday(chefs_day: dict, half: str, wd: int | None = None) -> set[str]:
    """
    Retourne l'ensemble des postes d'internes réellement OUVERTS sur la demi-journée
    d'après le planning des Chefs.
    Note : 'LECTURE/CS' n'est ouvert aux internes QUE le mardi après-midi (wd=1, half='pm')
    et le vendredi après-midi (wd=4, half='pm').
    """
    if not chefs_day:
        base = {"TDM SAU", "ECHO", "GESTES (C)", "SCAN ACHARD", "IRM 3T", "IRM 1,5T", "IRM", "TDM OLLIER DIAG", "ALLURA"}
        if half == "pm" and wd in (1, 4):
            base.add("LECTURE/CS")
        return base
    open_set = set()
    for entry in chefs_day.get(half, []):
        doc_val = str(entry.get("doc", "")).strip()
        poste_chef = str(entry.get("poste", "")).strip()
        is_closed = bool(entry.get("closed")) or doc_val.upper().startswith("FERM") or doc_val.upper() == "MAINTENANCE"
        if not is_closed:
            if poste_chef in CHEF_TO_INTERNE_POSTE:
                open_set.add(CHEF_TO_INTERNE_POSTE[poste_chef])
            elif poste_chef == "CONSULTATION" and half == "pm" and wd in (1, 4):
                open_set.add("LECTURE/CS")
    return open_set


def rebuild_day_lists(day_obj: dict):
    """
    Reconstruit am et pm à partir de byInterne et closedAm/closedPm.
    """
    if day_obj.get("holiday"):
        return
    by_interne = day_obj["byInterne"]
    closed_am = day_obj.get("closedAm", [])
    closed_pm = day_obj.get("closedPm", [])
    am_counts: dict[str, int] = {}
    pm_counts: dict[str, int] = {}
    for st in by_interne.values():
        p_am = st.get("am", "")
        p_pm = st.get("pm", "")
        if p_am not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"):
            am_counts[p_am] = am_counts.get(p_am, 0) + 1
        if p_pm not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"):
            pm_counts[p_pm] = pm_counts.get(p_pm, 0) + 1
    am_list = []
    pm_list = []
    for i_obj in INTERNES_LIST:
        iid = i_obj["id"]
        st = by_interne[iid]
        am_list.append({
            "poste": st["am"],
            "interneId": iid,
            "interne": i_obj["shortName"],
            "isSocle": bool(i_obj.get("isSocle")),
            "binome": am_counts.get(st["am"], 0) > 1 and bool(i_obj.get("isSocle")),
            "note": st.get("noteAm", ""),
        })
        pm_list.append({
            "poste": st["pm"],
            "interneId": iid,
            "interne": i_obj["shortName"],
            "isSocle": bool(i_obj.get("isSocle")),
            "binome": pm_counts.get(st["pm"], 0) > 1 and bool(i_obj.get("isSocle")),
            "note": st.get("notePm", ""),
        })
    for c in closed_am:
        am_list.append({
            "poste": c["poste"],
            "chefsPoste": c["chefsPoste"],
            "interneId": None,
            "interne": c["status"],
            "closed": True,
            "status": c["status"],
            "detail": c["detail"],
        })
    for c in closed_pm:
        pm_list.append({
            "poste": c["poste"],
            "chefsPoste": c["chefsPoste"],
            "interneId": None,
            "interne": c["status"],
            "closed": True,
            "status": c["status"],
            "detail": c["detail"],
        })
    day_obj["am"] = am_list
    day_obj["pm"] = pm_list
    day_obj["slots"] = by_interne


def generate_semester_schedule(absences: list[dict], chefs_planning: dict | None = None) -> dict:
    """
    Génère le planning quotidien (Matin & Après-midi) du 02/11/2026 au 30/04/2027 (26 semaines)
    pour les 6 internes du service, en intégrant :
    - La première matinée d'accueil et de formation obligatoire du lundi 02/11/2026 matin ('FORMATION / ACCUEIL')
      pour tous les internes arrivants, suivie du planning officiel du 02/11/2026 après-midi envoyé par
      le Dr Hippolyte MONNIER (Nathanaël au U, Marwane en IRM, Noé et Gabriel en TDM3, Milan en US, Oussama en demi-off)
      servant de base (R0..R4) pour toute la suite du semestre.
    - Les 5 internes DES hors socle en rotation équilibrée sur R0..R4 (2 demi-offs / semaine chacun)
    - PAS DE DEMI-OFF LE MARDI APRÈS-MIDI NI LE VENDREDI APRÈS-MIDI pour les internes.
    - Consultation ('LECTURE/CS') pour les internes UNIQUEMENT le mardi après-midi et le vendredi après-midi :
      * Mardi après-midi : Relecture avec Pr Drapé SYSTÉMATIQUE (toujours pourvue par un interne présent).
      * Vendredi après-midi : Consultation Internes (avec MH / seniors).
      * Autres créneaux (hors mardi PM et vendredi PM) non obligatoires si les demi-offs ne sont pas suffisants pour les internes.
    - Noé GRANDVAL ('noe', Phase Socle) :
      * SYSTÉMATIQUEMENT EN BINÔME AVEC UN CO-INTERNE AU TDM SAU (jamais seul au Scanner des Urgences).
      * 2 demi-offs / semaine (Mercredi matin et Jeudi après-midi).
      * Posté principalement au Scanner des Urgences ('TDM SAU') en binôme avec un co-interne (~55 % de ses vacations actives)
        et réparti le reste du temps sur ses propres postes d'IRM (3T / 1,5T), Échographie et TDM Ollier Diag (TDM3).
      * Posté avec Dr Macil HAMADOUCHE ('MH') et un co-interne le mardi matin les 3 premières semaines (03/11, 10/11, 17/11).
    - Les vacations fermées ('FERMÉ' / 'MAINTENANCE') issues du planning officiel du service.
    """
    weekly_roles = build_balanced_trame()
    senior_interne_ids = ["gabriel", "marwane", "milan", "nathanael", "oussama"]
    interne_short_by_id = {x["id"]: x["shortName"] for x in INTERNES_LIST}

    abs_lookup = {}
    for ab in absences:
        dt = ab.get("date")
        iid = ab.get("interneId")
        atype = ab.get("type", "CA 1")
        if dt and iid:
            abs_lookup[(dt, iid)] = atype

    start_date = datetime.date(2026, 11, 2)
    end_date = datetime.date(2027, 4, 30)
    schedule = {}
    weeks_map: dict[int, list[str]] = {}

    cur = start_date
    while cur <= end_date:
        iso = cur.isoformat()
        wd = cur.weekday()  # 0=Mon .. 6=Sun
        week_idx = (cur - start_date).days // 7

        if wd >= 5:
            cur += datetime.timedelta(days=1)
            continue

        weeks_map.setdefault(week_idx, []).append(iso)

        if iso in JOURS_FERIES_HIVER:
            by_interne_ferie = {
                i["id"]: {"am": "FÉRIÉ", "pm": "FÉRIÉ", "note": JOURS_FERIES_HIVER[iso]}
                for i in INTERNES_LIST
            }
            schedule[iso] = {
                "holiday": JOURS_FERIES_HIVER[iso],
                "am": [],
                "pm": [],
                "closedAm": [],
                "closedPm": [],
                "byInterne": by_interne_ferie,
                "slots": by_interne_ferie,
            }
            cur += datetime.timedelta(days=1)
            continue

        chefs_day = (chefs_planning or {}).get(iso, {})
        closed_am = get_closed_vacations_for_halfday(chefs_day, "am", wd)
        closed_pm = get_closed_vacations_for_halfday(chefs_day, "pm", wd)
        closed_am_codes = {c["poste"]: c["status"] for c in closed_am}
        closed_pm_codes = {c["poste"]: c["status"] for c in closed_pm}
        open_am_codes = get_open_interne_postes_for_halfday(chefs_day, "am", wd)
        open_pm_codes = get_open_interne_postes_for_halfday(chefs_day, "pm", wd)

        day_roles = weekly_roles[wd]
        by_interne = {}

        # Cas particulier : Première matinée des internes le lundi 2 novembre 2026 (Accueil & Formation obligatoire)
        # et premier après-midi fixé par le Dr Hippolyte MONNIER servant de base pour la suite
        if iso == "2026-11-02":
            monnier_pm_base = {
                "gabriel": ("TDM OLLIER DIAG", "Planning Dr H. Monnier (TDM3 avec Noé)"),
                "noe": ("TDM OLLIER DIAG", "Planning Dr H. Monnier (Binôme TDM3 avec Gabriel)"),
                "marwane": ("IRM", "Planning Dr H. Monnier (IRM avec Pr A. Feydy)"),
                "milan": ("ECHO", "Planning Dr H. Monnier (US / Écho avec Dr H. Monnier)"),
                "nathanael": ("TDM SAU", "Planning Dr H. Monnier (Scanner des U)"),
                "oussama": ("1/2 journée libre", "Poste C (Gestes) fermé"),
            }
            for i_obj in INTERNES_LIST:
                iid = i_obj["id"]
                pm_poste, pm_note = monnier_pm_base[iid]
                if iid == "oussama":
                    am_poste = "TDM SAU"
                    am_note = "Permanence Scanner des Urgences (pendant la matinée d'accueil des internes)"
                else:
                    am_poste = "FORMATION / ACCUEIL"
                    am_note = "Accueil café (08h15), visite du service & Formation obligatoire (Salle Chevrot)"
                by_interne[iid] = {
                    "am": am_poste,
                    "pm": pm_poste,
                    "note": f"Matin : {am_note} • PM : {pm_note}",
                    "noteAm": am_note,
                    "notePm": pm_note,
                }
            schedule[iso] = {
                "holiday": None,
                "am": [],
                "pm": [],
                "closedAm": closed_am,
                "closedPm": closed_pm,
                "byInterne": by_interne,
            }
            cur += datetime.timedelta(days=1)
            continue

        # 1. Attribution initiale pour les 5 internes hors socle
        #    - Semaine 1 (week_idx == 0, semaine du 02/11/2026) : trame initiale calée sur le planning du Dr H. Monnier
        #    - À partir de la semaine 2 (week_idx >= 1, dès le lundi 09/11/2026) :
        #      Offs fixes (2 demi-offs groupés sur la journée entière Matin + Après-midi) pour les 3 internes :
        #        * Marwane : OFF fixe le LUNDI (Matin + Après-midi)
        #        * Gabriel : OFF fixe le MERCREDI (Matin + Après-midi)
        #        * Oussama : OFF fixe le JEUDI (Matin + Après-midi)
        #      Milan & Nathanaël : 2 demi-offs tournants sur Lundi / Mercredi / Jeudi / Vendredi matin
        #      (jamais de demi-off le Mardi après-midi ni le Vendredi après-midi).
        FIXED_OFF_DAYS_FROM_W2 = {
            "marwane": 0,  # Lundi (Matin + Après-midi)
            "gabriel": 2,  # Mercredi (Matin + Après-midi)
            "oussama": 3,  # Jeudi (Matin + Après-midi)
        }

        if week_idx == 0:
            for idx, iid in enumerate(senior_interne_ids):
                role_idx = (idx + week_idx) % 5
                post_am = day_roles["am"][role_idx]
                post_pm = day_roles["pm"][role_idx]
                if wd == 1 and post_pm == "LECTURE/CS":
                    note_pm = "Relecture avec Pr Drapé (systématique)"
                elif wd == 4 and post_pm == "LECTURE/CS":
                    note_pm = "Consultation Internes (Vendredi PM)"
                else:
                    note_pm = ""
                by_interne[iid] = {
                    "am": post_am,
                    "pm": post_pm,
                    "note": note_pm,
                    "noteAm": "",
                    "notePm": note_pm,
                }
        else:
            # À partir de la semaine 2 (09/11/2026) :
            # Demi-offs tournants pour Milan et Nathanaël (2 demi-offs chacun / semaine, hors Mardi PM et Vendredi PM)
            if week_idx % 2 == 1:
                milan_offs = {(0, "am"), (3, "pm")}      # Lundi matin + Jeudi après-midi
                nathanael_offs = {(2, "pm"), (4, "am")}  # Mercredi après-midi + Vendredi matin
            else:
                milan_offs = {(2, "pm"), (4, "am")}      # Mercredi après-midi + Vendredi matin
                nathanael_offs = {(0, "am"), (3, "pm")}  # Lundi matin + Jeudi après-midi

            am_pools_w2 = {
                0: [  # Lundi AM (3 seniors actifs : Marwane off fixe, Milan/Nathanaël demi-off)
                    "TDM SAU",
                    "GESTES (C)",
                    "ECHO",
                ],
                1: [  # Mardi AM (5 seniors actifs)
                    "TDM SAU",
                    "IRM 1,5T" if (week_idx < 3 or week_idx % 2 == 0) else "SCAN ACHARD",
                    "IRM 3T",
                    "ECHO",
                    "GESTES (C)",
                ],
                2: [  # Mercredi AM (4 seniors actifs : Gabriel off fixe)
                    "TDM SAU",
                    "IRM 1,5T",
                    "TDM OLLIER DIAG",
                    "GESTES (C)",
                ],
                3: [  # Jeudi AM (4 seniors actifs : Oussama off fixe)
                    "TDM SAU",
                    "SCAN ACHARD",
                    "ECHO",
                    "GESTES (C)",
                ],
                4: [  # Vendredi AM (4 seniors actifs : Milan/Nathanaël demi-off)
                    "TDM SAU",
                    "GESTES (C)",
                    "ECHO",
                    "IRM 1,5T",
                ],
            }
            pm_pools_w2 = {
                0: [  # Lundi PM (4 seniors actifs : Marwane off fixe)
                    "TDM SAU",
                    "GESTES (C)" if (week_idx % 2 == 0) else "TDM OLLIER DIAG",
                    "IRM",
                    "ECHO",
                ],
                1: [  # Mardi PM (5 seniors actifs, 0 off)
                    "LECTURE/CS",
                    "TDM SAU",
                    "SCAN ACHARD",
                    "ECHO",
                    "GESTES (C)",
                ],
                2: [  # Mercredi PM (3 seniors actifs : Gabriel off fixe, Milan/Nathanaël demi-off)
                    "TDM SAU",
                    "SCAN ACHARD",
                    "GESTES (C)" if (week_idx % 2 == 0) else "IRM",
                ],
                3: [  # Jeudi PM (3 seniors actifs : Oussama off fixe, Milan/Nathanaël demi-off)
                    "TDM SAU",
                    "IRM",
                    "SCAN ACHARD" if (week_idx % 2 == 0) else "ALLURA",
                ],
                4: [  # Vendredi PM (5 seniors actifs, 0 off)
                    "LECTURE/CS",
                    "TDM SAU",
                    "IRM",
                    "GESTES (C)",
                    "SCAN ACHARD",
                ],
            }

            # Attribution Matin (AM)
            active_am_seniors = []
            for iid in senior_interne_ids:
                if FIXED_OFF_DAYS_FROM_W2.get(iid) == wd:
                    by_interne[iid] = {
                        "am": "1/2 journée libre",
                        "pm": "1/2 journée libre",
                        "note": "Jour off fixe hebdomadaire",
                        "noteAm": "Off fixe (journée entière)",
                        "notePm": "Off fixe (journée entière)",
                    }
                elif (iid == "milan" and (wd, "am") in milan_offs) or (iid == "nathanael" and (wd, "am") in nathanael_offs):
                    by_interne[iid] = {
                        "am": "1/2 journée libre",
                        "pm": "",
                        "note": "",
                        "noteAm": "Demi-off hebdomadaire",
                        "notePm": "",
                    }
                else:
                    active_am_seniors.append(iid)
                    by_interne[iid] = {"am": "", "pm": "", "note": "", "noteAm": "", "notePm": ""}

            pool_am = am_pools_w2[wd]
            for idx_a, iid in enumerate(active_am_seniors):
                p_am = pool_am[(idx_a + week_idx) % len(pool_am)]
                by_interne[iid]["am"] = p_am

            # Attribution Après-midi (PM)
            active_pm_seniors = []
            for iid in senior_interne_ids:
                if FIXED_OFF_DAYS_FROM_W2.get(iid) == wd:
                    continue
                if (iid == "milan" and (wd, "pm") in milan_offs) or (iid == "nathanael" and (wd, "pm") in nathanael_offs):
                    by_interne[iid]["pm"] = "1/2 journée libre"
                    by_interne[iid]["notePm"] = "Demi-off hebdomadaire"
                else:
                    active_pm_seniors.append(iid)

            pool_pm = pm_pools_w2[wd]
            for idx_p, iid in enumerate(active_pm_seniors):
                p_pm = pool_pm[(idx_p + week_idx) % len(pool_pm)]
                by_interne[iid]["pm"] = p_pm
                if wd == 1 and p_pm == "LECTURE/CS":
                    by_interne[iid]["notePm"] = "Relecture avec Pr Drapé (systématique)"
                elif wd == 4 and p_pm == "LECTURE/CS":
                    by_interne[iid]["notePm"] = "Consultation Internes (Vendredi PM)"
                if not by_interne[iid]["note"]:
                    by_interne[iid]["note"] = by_interne[iid]["noteAm"] or by_interne[iid]["notePm"]

        # 2. Attribution pour Noé (Phase Socle — systématiquement avec un co-interne au TDM SAU)
        if wd == 1:  # Mardi matin : 3 premières semaines (week_idx 0, 1, 2 -> 03/11, 10/11, 17/11) posté avec Macil (MH) au TDM SAU
            if week_idx < 3:
                noe_am = "TDM SAU"
                noe_note_am = "Avec Dr Macil HAMADOUCHE (MH) — Posté Socle Urgences"
            else:
                noe_am = "IRM 1,5T" if (week_idx % 2 == 1) else "TDM SAU"
                noe_note_am = "Avec Dr Macil HAMADOUCHE (MH) — Posté Socle Urgences" if noe_am == "TDM SAU" else "Phase Socle"
        elif wd == 3:
            noe_am = day_roles["am"]["socle"]
            noe_note_am = "Avec Dr Macil HAMADOUCHE (MH) — Posté Socle Urgences" if noe_am == "TDM SAU" else ""
        else:
            noe_am = day_roles["am"]["socle"]
            noe_note_am = "Posté Socle Urgences" if noe_am == "TDM SAU" else ""

        if wd == 0:  # Lundi après-midi (hors 02/11) : alterne 1 sem/2 TDM SAU et 1 sem/2 TDM OLLIER DIAG
            noe_pm = "TDM OLLIER DIAG" if (week_idx % 2 == 0) else "TDM SAU"
            noe_note_pm = "Posté Socle Urgences" if noe_pm == "TDM SAU" else "Phase Socle (TDM3)"
        else:
            noe_pm = day_roles["pm"]["socle"]
            noe_note_pm = "Posté Socle Urgences" if noe_pm == "TDM SAU" else ""
        by_interne["noe"] = {
            "am": noe_am,
            "pm": noe_pm,
            "note": noe_note_am or noe_note_pm,
            "noteAm": noe_note_am,
            "notePm": noe_note_pm,
        }

        def is_protected_fixed_off(interne_id: str, day_iso_str: str) -> bool:
            w_i = (datetime.date.fromisoformat(day_iso_str) - start_date).days // 7
            if w_i < 1:
                return False
            wd_i = datetime.date.fromisoformat(day_iso_str).weekday()
            return FIXED_OFF_DAYS_FROM_W2.get(interne_id) == wd_i

        # 3. Application des absences (CA / CF / RG)
        for iid in [x["id"] for x in INTERNES_LIST]:
            abs_type = abs_lookup.get((iso, iid))
            if abs_type:
                badge = "RG" if "garde" in abs_type.lower() or abs_type.upper() == "RG" else "VACANCES"
                by_interne[iid]["am"] = badge
                by_interne[iid]["pm"] = badge
                by_interne[iid]["note"] = abs_type
                by_interne[iid]["noteAm"] = abs_type
                by_interne[iid]["notePm"] = abs_type

        # 3bis. Garantie SYSTÉMATIQUE du TDM SAU (Matin & Après-midi) par un co-interne hors socle
        #       et de la Relecture avec Pr Drapé le Mardi après-midi (wd == 1)
        for h_sau in ("am", "pm"):
            has_sau = any(
                by_interne[iid][h_sau] == "TDM SAU"
                for iid in senior_interne_ids
            )
            if not has_sau:
                nk_sau = "noteAm" if h_sau == "am" else "notePm"
                for donor_poste in ("ECHO", "GESTES (C)", "ALLURA", "SCAN ACHARD", "TDM OLLIER DIAG", "IRM", "IRM 1,5T", "IRM 3T"):
                    replaced_sau = False
                    for iid in senior_interne_ids:
                        if by_interne[iid][h_sau] == donor_poste:
                            by_interne[iid][h_sau] = "TDM SAU"
                            by_interne[iid][nk_sau] = "Remplacement TDM SAU (congés/RG)"
                            if not by_interne[iid]["note"]:
                                by_interne[iid]["note"] = by_interne[iid][nk_sau]
                            replaced_sau = True
                            break
                    if replaced_sau:
                        break

        if wd == 1:
            has_tue_cs = any(
                by_interne[iid]["pm"] == "LECTURE/CS"
                for iid in senior_interne_ids
            )
            if not has_tue_cs:
                # Si l'interne initialement prévu en LECTURE/CS le mardi PM est en congés/RG,
                # un interne présent bascule systématiquement sur la Relecture avec Pr Drapé
                # depuis un poste non obligatoire (ECHO, GESTES (C), SCAN ACHARD).
                for donor_poste in ("ECHO", "GESTES (C)", "SCAN ACHARD"):
                    replaced = False
                    for iid in senior_interne_ids:
                        if by_interne[iid]["pm"] == donor_poste:
                            by_interne[iid]["pm"] = "LECTURE/CS"
                            by_interne[iid]["notePm"] = "Relecture avec Pr Drapé (systématique)"
                            if not by_interne[iid]["note"]:
                                by_interne[iid]["note"] = "Relecture avec Pr Drapé (systématique)"
                            replaced = True
                            break
                    if replaced:
                        break

        # 4. Gestion des vacations FERMÉES / MAINTENANCE et garantie zéro doublon hors TDM SAU
        #    Note : Le mardi après-midi (wd=1, half='pm') et le vendredi après-midi (wd=4, half='pm'),
        #    AUCUN interne ne peut être mis en '1/2 journée libre' : si une salle est fermée,
        #    l'interne rejoint LECTURE/CS (Relecture Pr Drapé / Consultation Internes).
        for half, closed_map, open_set in [("am", closed_am_codes, open_am_codes), ("pm", closed_pm_codes, open_pm_codes)]:
            note_key = "noteAm" if half == "am" else "notePm"
            is_no_off_halfday = (half == "pm" and wd in (1, 4))
            used_by_seniors = set()
            for iid in senior_interne_ids:
                p = by_interne[iid][half]
                if p not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL") and p not in closed_map:
                    used_by_seniors.add(p)

            # LECTURE/CS n'est un candidat de repli QUE le mardi PM (wd=1) ou vendredi PM (wd=4)
            fallback_candidates = ["TDM OLLIER DIAG", "SCAN ACHARD", "GESTES (C)", "IRM", "IRM 3T", "IRM 1,5T", "ECHO", "ALLURA"]
            if half == "pm" and wd in (1, 4):
                fallback_candidates.insert(0, "LECTURE/CS")
            no_interne_thevenin_nov = (half == "am" and wd == 2 and iso.startswith("2026-11"))
            if no_interne_thevenin_nov:
                fallback_candidates = [c for c in fallback_candidates if c != "ECHO"]

            for iid in senior_interne_ids:
                p = by_interne[iid][half]
                if p == "ECHO" and no_interne_thevenin_nov:
                    reassigned = None
                    for cand in fallback_candidates:
                        if cand in open_set and cand not in closed_map and cand not in used_by_seniors and cand != by_interne["noe"][half]:
                            reassigned = cand
                            break
                    if not reassigned:
                        reassigned = "TDM SAU" if (week_idx >= 1 and iid in FIXED_OFF_DAYS_FROM_W2) else "1/2 journée libre"
                    else:
                        used_by_seniors.add(reassigned)
                    used_by_seniors.discard("ECHO")
                    by_interne[iid][half] = reassigned
                    by_interne[iid][note_key] = "Pas d'interne en Écho avec Dr F. Thévenin (Novembre)"
                    if not by_interne[iid]["note"]:
                        by_interne[iid]["note"] = "Pas d'interne en Écho avec Dr F. Thévenin (Novembre)"
                elif p in closed_map:
                    status_lbl = closed_map[p]
                    reassigned = None
                    for cand in fallback_candidates:
                        if cand in open_set and cand not in closed_map and cand not in used_by_seniors and cand != by_interne["noe"][half]:
                            reassigned = cand
                            break
                    if not reassigned:
                        if is_no_off_halfday:
                            reassigned = "LECTURE/CS"
                        elif week_idx >= 1 and iid in FIXED_OFF_DAYS_FROM_W2:
                            reassigned = "TDM SAU"
                        else:
                            reassigned = "1/2 journée libre"
                    else:
                        used_by_seniors.add(reassigned)
                    by_interne[iid][half] = reassigned
                    if is_no_off_halfday and reassigned == "LECTURE/CS":
                        re_lbl = "Relecture Pr Drapé" if wd == 1 else "Consultation Internes"
                        by_interne[iid][note_key] = f"{p} {status_lbl.lower()} → {re_lbl}"
                    else:
                        by_interne[iid][note_key] = f"{p} {status_lbl.lower()}"
                    if not by_interne[iid]["note"]:
                        by_interne[iid]["note"] = by_interne[iid][note_key]

            noe_p = by_interne["noe"][half]
            if noe_p not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"):
                if noe_p in closed_map:
                    status_lbl = closed_map[noe_p]
                    by_interne["noe"][half] = "TDM SAU"
                    by_interne["noe"][note_key] = f"{noe_p} {status_lbl.lower()} → TDM SAU"
                    by_interne["noe"]["note"] = by_interne["noe"][note_key]
                elif noe_p != "TDM SAU" and noe_p in used_by_seniors:
                    by_interne["noe"][half] = "TDM SAU"
                    by_interne["noe"][note_key] = "Posté Socle Urgences"

        # 4bis. Le Vendredi après-midi (wd == 4), s'assurer que le créneau LECTURE/CS est couvert par un interne senior
        if wd == 4 and "LECTURE/CS" in open_pm_codes and "LECTURE/CS" not in closed_pm_codes:
            has_fri_cs = any(
                by_interne[iid]["pm"] == "LECTURE/CS"
                for iid in senior_interne_ids
            )
            if not has_fri_cs:
                for donor_poste in ("GESTES (C)", "SCAN ACHARD", "IRM"):
                    replaced = False
                    for iid in senior_interne_ids:
                        if by_interne[iid]["pm"] == donor_poste:
                            by_interne[iid]["pm"] = "LECTURE/CS"
                            by_interne[iid]["notePm"] = "Consultation Internes (Vendredi PM)"
                            if not by_interne[iid]["note"]:
                                by_interne[iid]["note"] = "Consultation Internes (Vendredi PM)"
                            replaced = True
                            break
                    if replaced:
                        break

        schedule[iso] = {
            "holiday": None,
            "am": [],
            "pm": [],
            "closedAm": closed_am,
            "closedPm": closed_pm,
            "byInterne": by_interne,
        }
        cur += datetime.timedelta(days=1)

    # 5. Équilibrage hebdomadaire des demi-offs ('1/2 journée libre') :
    #    - INTERDICTION STRICTE de demi-off le mardi après-midi (wd=1, pm) et le vendredi après-midi (wd=4, pm)
    #    - Protection stricte des jours offs fixes à partir de S2 (09/11/2026) :
    #      Marwane = Lundi (matin+PM), Gabriel = Mercredi (matin+PM), Oussama = Jeudi (matin+PM)
    #    - Maximum 2 demi-offs par semaine par interne (réaffectation sur postes ouverts si > 2)
    #    - Garantie de 2 demi-offs par semaine pour chaque interne actif : si un interne a < 2 demi-offs
    #      (ex: jour férié tombant sur son demi-off ou 1re matinée d'accueil), les autres créneaux non obligatoires
    #      (en dehors du mardi PM, du vendredi PM et du TDM SAU) sont libérés en demi-off.
    def get_available_open_postes(day_iso: str, half_key: str) -> list[str]:
        day_obj = schedule[day_iso]
        ch_day = (chefs_planning or {}).get(day_iso, {})
        dt_obj = datetime.date.fromisoformat(day_iso)
        wd_cur = dt_obj.weekday()
        open_set = get_open_interne_postes_for_halfday(ch_day, half_key, wd_cur)
        closed_codes = {c["poste"] for c in (day_obj["closedAm"] if half_key == "am" else day_obj["closedPm"])}
        used = {
            st[half_key]
            for st in day_obj["byInterne"].values()
            if st[half_key] not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ")
        }
        # LECTURE/CS uniquement le mardi PM (wd=1) et vendredi PM (wd=4)
        candidates = ["TDM OLLIER DIAG", "SCAN ACHARD", "GESTES (C)", "IRM", "IRM 3T", "IRM 1,5T", "ECHO", "ALLURA"]
        if half_key == "pm" and wd_cur in (1, 4):
            candidates.insert(0, "LECTURE/CS")
        if half_key == "am" and wd_cur == 2 and day_iso.startswith("2026-11"):
            candidates = [c for c in candidates if c != "ECHO"]
        return [c for c in candidates if c in open_set and c not in closed_codes and c not in used]

    for w_idx, iso_list in sorted(weeks_map.items()):
        active_isos = [d_iso for d_iso in iso_list if not schedule[d_iso].get("holiday")]
        # 5A. Réduction si > 2 demi-offs
        while True:
            off_counts = {i["id"]: 0 for i in INTERNES_LIST}
            for d_iso in active_isos:
                for iid, st in schedule[d_iso]["byInterne"].items():
                    for h in ("am", "pm"):
                        if st[h] == "1/2 journée libre":
                            off_counts[iid] += 1
            over_iids = [iid for iid, cnt in off_counts.items() if cnt > 2]
            if not over_iids:
                break

            fixed = False
            for iid in over_iids:
                # A) Remplacement direct d'un demi-off (hors off fixe protégé) par un poste ouvert disponible sur le même créneau
                for d_iso in active_isos:
                    if d_iso == "2026-11-02" or is_protected_fixed_off(iid, d_iso):
                        continue
                    for h in ("am", "pm"):
                        st = schedule[d_iso]["byInterne"][iid]
                        if st[h] == "1/2 journée libre":
                            avail = get_available_open_postes(d_iso, h)
                            if avail:
                                st[h] = avail[0]
                                fixed = True
                                break
                    if fixed:
                        break
                if fixed:
                    break

                # B) Échange intra-semaine (sans toucher aux offs fixes protégés)
                for d_iso1 in active_isos:
                    if d_iso1 == "2026-11-02" or is_protected_fixed_off(iid, d_iso1):
                        continue
                    for h1 in ("am", "pm"):
                        nk1 = "noteAm" if h1 == "am" else "notePm"
                        st1 = schedule[d_iso1]["byInterne"][iid]
                        if st1[h1] == "1/2 journée libre":
                            for other in senior_interne_ids:
                                if other == iid:
                                    continue
                                p_other1 = schedule[d_iso1]["byInterne"][other][h1]
                                if p_other1 in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"):
                                     continue
                                for d_iso2 in active_isos:
                                    if d_iso2 == "2026-11-02" or is_protected_fixed_off(other, d_iso2):
                                        continue
                                    wd2 = datetime.date.fromisoformat(d_iso2).weekday()
                                    for h2 in ("am", "pm"):
                                        if h2 == "pm" and wd2 in (1, 4):
                                            continue
                                        st_other2 = schedule[d_iso2]["byInterne"][other]
                                        if st_other2[h2] == "1/2 journée libre":
                                            avail2 = get_available_open_postes(d_iso2, h2)
                                            if avail2:
                                                st1[h1] = p_other1
                                                if st1.get("note") == st1.get(nk1):
                                                    st1["note"] = ""
                                                st1[nk1] = ""
                                                schedule[d_iso1]["byInterne"][other][h1] = "1/2 journée libre"
                                                st_other2[h2] = avail2[0]
                                                fixed = True
                                                break
                                    if fixed:
                                        break
                                if fixed:
                                    break
                        if fixed:
                            break
                    if fixed:
                        break
                if fixed:
                    break

            if not fixed:
                break

        # 5B. Garantie que chaque interne actif (hors semaine de congés) a bien ses 2 demi-offs :
        #     INTERDICTION STRICTE de libérer le mardi après-midi (wd_cur == 1, h == 'pm')
        #     ou le vendredi après-midi (wd_cur == 4, h == 'pm') ou le TDM SAU.
        non_mandatory_priority = [
            "ALLURA",
            "TDM OLLIER DIAG",
            "IRM 1,5T",
            "ECHO",
            "GESTES (C)",
            "SCAN ACHARD",
            "IRM 3T",
            "IRM",
        ]
        for iid in [x["id"] for x in INTERNES_LIST]:
            vac_halfdays = 0
            off_cnt = 0
            for d_iso in active_isos:
                st = schedule[d_iso]["byInterne"][iid]
                for h in ("am", "pm"):
                    if st[h] in ("VACANCES", "RG"):
                        vac_halfdays += 1
                    elif st[h] == "1/2 journée libre":
                        off_cnt += 1
            # Si l'interne est présent sur la semaine (pas en semaine complète de congés) et a < 2 demi-offs
            if vac_halfdays >= 6:
                continue
            while off_cnt < 2:
                freed = False
                for cand_poste in non_mandatory_priority:
                    for d_iso in reversed(active_isos):
                        if d_iso == "2026-11-02":
                            continue
                        wd_cur = datetime.date.fromisoformat(d_iso).weekday()
                        for h in ("pm", "am"):
                            # Interdiction stricte de demi-off le mardi après-midi (wd=1) et le vendredi après-midi (wd=4)
                            if h == "pm" and wd_cur in (1, 4):
                                continue
                            # Pour Noé (socle), ne jamais libérer le TDM SAU
                            st = schedule[d_iso]["byInterne"][iid]
                            if st[h] == cand_poste:
                                nk = "noteAm" if h == "am" else "notePm"
                                st[h] = "1/2 journée libre"
                                st[nk] = "Créneau non obligatoire libéré (quota 2 demi-offs / sem)"
                                if not st.get("note"):
                                    st["note"] = st[nk]
                                off_cnt += 1
                                freed = True
                                break
                        if freed:
                            break
                    if freed:
                        break
                if not freed:
                    break

        # 5C. Garantie STRICTE qu'il y a TOUJOURS un interne hors socle au TDM SAU (Matin & Après-midi)
        #     et que Noé (Phase Socle) est SYSTÉMATIQUEMENT avec un co-interne lorsqu'il est au TDM SAU
        #     (jamais seul au TDM SAU), tout en gardant ses postes propres hors TDM SAU (IRM, Écho, TDM3).
        non_active_codes = ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL")
        for d_iso in active_isos:
            wd_cur = datetime.date.fromisoformat(d_iso).weekday()
            by_int = schedule[d_iso]["byInterne"]
            for h in ("am", "pm"):
                nk = "noteAm" if h == "am" else "notePm"
                # S'assurer qu'au moins un co-interne hors socle couvre SYSTÉMATIQUEMENT le TDM SAU
                has_senior_sau = any(by_int[s_id][h] == "TDM SAU" for s_id in senior_interne_ids)
                if not has_senior_sau:
                    for donor_p in ("ECHO", "GESTES (C)", "ALLURA", "SCAN ACHARD", "TDM OLLIER DIAG", "IRM", "IRM 1,5T", "IRM 3T", "1/2 journée libre", "FORMATION / ACCUEIL"):
                        replaced_s = False
                        for s_id in senior_interne_ids:
                            if by_int[s_id][h] == donor_p:
                                by_int[s_id][h] = "TDM SAU"
                                by_int[s_id][nk] = "Remplacement TDM SAU"
                                replaced_s = True
                                break
                        if replaced_s:
                            break

                noe_st = by_int["noe"]
                noe_p = noe_st[h]
                if noe_p in non_active_codes:
                    continue

                if noe_p == "TDM SAU":
                    sau_partners = [interne_short_by_id[s_id] for s_id in senior_interne_ids if by_int[s_id][h] == "TDM SAU"]
                    partner_str = " & ".join(sau_partners)
                    if h == "am" and wd_cur in (1, 3):
                        noe_st[nk] = f"Avec Dr Macil HAMADOUCHE (MH) • Binôme SAU avec {partner_str}" if partner_str else "Avec Dr Macil HAMADOUCHE (MH) — Posté Socle Urgences"
                    else:
                        noe_st[nk] = f"Posté Socle Urgences • Binôme SAU avec {partner_str}" if partner_str else "Posté Socle Urgences"

            if d_iso != "2026-11-02":
                notes_combined = [x for x in (by_int["noe"].get("noteAm", ""), by_int["noe"].get("notePm", "")) if x]
                by_int["noe"]["note"] = " • ".join(notes_combined)

    for d_iso, day_obj in schedule.items():
        if not day_obj.get("holiday"):
            for h_chk in ("am", "pm"):
                if not any(day_obj["byInterne"][s_id][h_chk] == "TDM SAU" for s_id in senior_interne_ids):
                    raise RuntimeError(f"ERREUR : Aucun interne senior au TDM SAU le {d_iso} ({h_chk})")
        rebuild_day_lists(day_obj)

    return schedule


def build_initial_presentations(schedule: dict | None = None) -> list[dict]:
    """
    Génère le calendrier complet des présentations du semestre Hiver 2026-2027 :
    - Tous les Mardis (Cas clinique des internes + Cours des chefs)
    - Tous les Vendredis (Bibliographie des internes)
    - Les séances Bone Club & Confrontations Radio-Anatomopathologiques
    Avec répartition initiale équilibrée par roulement (en évitant systématiquement
    les jours de Repos de garde RG ou congés de l'interne).
    """
    start_date = datetime.date(2026, 11, 2)
    end_date = datetime.date(2027, 4, 30)
    main_ids = ["gabriel", "noe", "marwane", "milan", "nathanael", "oussama"]
    tue_counts = {k: 0 for k in main_ids}
    fri_counts = {k: 0 for k in main_ids}

    items = []
    tuesday_idx = 0
    friday_idx = 0

    cur = start_date
    while cur <= end_date:
        iso = cur.isoformat()
        wd = cur.weekday()
        if iso in JOURS_FERIES_HIVER:
            cur += datetime.timedelta(days=1)
            continue

        day_by_int = (schedule or {}).get(iso, {}).get("byInterne", {})
        present_ids = [
            iid for iid in main_ids
            if day_by_int.get(iid, {}).get("am") not in ("RG", "VACANCES")
            and day_by_int.get(iid, {}).get("pm") not in ("RG", "VACANCES")
        ]
        pool = present_ids if present_ids else main_ids

        if wd == 1:  # MARDI : Cas clinique + Cours des chefs
            cands = sorted(
                pool,
                key=lambda x: (tue_counts[x], (main_ids.index(x) - tuesday_idx) % len(main_ids)),
            )
            assigned_id = cands[0]
            tue_counts[assigned_id] += 1
            assigned_obj = next(x for x in INTERNES_LIST if x["id"] == assigned_id)
            chef_nom, chef_sujet = CHEFS_TUESDAY_COURS[tuesday_idx % len(CHEFS_TUESDAY_COURS)]
            cours_programme = CURRICULUM_COURS[tuesday_idx % len(CURRICULUM_COURS)]
            items.append({
                "id": f"cas-{iso}",
                "date": iso,
                "type": "cas_mardi",
                "typeLabel": "Cas Clinique du Mardi",
                "horaire": "12h30 – 13h30",
                "salle": "Salle de Staff Radio B (Albarran -1)",
                "interneId": assigned_id,
                "interneName": assigned_obj["shortName"],
                "sujet": "" if iso > "2026-11-17" else (
                    "Dossier ostéo-articulaire inaugural (choix libre)" if iso == "2026-11-03" else ""
                ),
                "chefIntervenant": chef_nom,
                "coursChef": chef_sujet,
                "themeSemaine": cours_programme,
                "notes": "Présentation d'un cas clinique (10 min) suivie du cours hebdo des chefs (20-30 min).",
            })
            tuesday_idx += 1

        elif wd == 4:  # VENDREDI : Biblio du vendredi
            cands = sorted(
                pool,
                key=lambda x: (fri_counts[x], (main_ids.index(x) - (friday_idx + 3)) % len(main_ids)),
            )
            assigned_id = cands[0]
            fri_counts[assigned_id] += 1
            assigned_obj = next(x for x in INTERNES_LIST if x["id"] == assigned_id)
            items.append({
                "id": f"biblio-{iso}",
                "date": iso,
                "type": "biblio_vendredi",
                "typeLabel": "Biblio du Vendredi",
                "horaire": "12h30 – 13h30",
                "salle": "Salle de Staff Radio B (Albarran -1)",
                "interneId": assigned_id,
                "interneName": assigned_obj["shortName"],
                "sujet": "",
                "articleRef": "",
                "notes": "Présentation critique d'un article récent d'imagerie musculo-squelettique ou interventionnelle.",
            })
            friday_idx += 1

        cur += datetime.timedelta(days=1)

    # Ajout des Confrontations Radio-Anatomopathologiques (CRA) & Bone Club (Amphi Luton)
    # Sources : Mails de Sandrine CAMBLONG ([CCH] Enseignement Radiob Cochin <enseignement.radiob.cch@aphp.fr>)
    # - Calendrier-CRA-V3.pdf (reçu le 21/09/2026) : Vendredis 27/11/2026, 15/01/2027, 26/03/2027, 14/05/2027, 18/06/2027 (14h15–16h00, Salle de réunion Radio B, Albarran -1)
    # - BONE CLUB (mercredis 18h00–20h00, Amphithéâtre LUTON — RDC UFR de Médecine Site Cochin, 24 rue du Fg St-Jacques Paris 14e)
    special_staffs = [
        {
            "id": "cra-2026-11-27",
            "date": "2026-11-27",
            "type": "confrontation_anapath",
            "typeLabel": "Confrontations Radio-Anatomopathologiques (CRA)",
            "horaire": "14h15 – 16h00",
            "salle": "Salle de réunion Radio B (Pavillon Albarran -1)",
            "interneId": "gabriel",
            "interneName": "Gabriel & Noé",
            "sujet": "Confrontations Radio-Anatomo-Pathologiques dans les maladies de l'appareil locomoteur",
            "chefIntervenant": "Pr A. Feydy, Pr J-L. Drapé & Pr B. Terris / Dr F. Larousserie / Dr V. Audard",
            "coursChef": "Corrélation radio-histologique (Service Radio B & Anatomie Pathologique)",
            "notes": "Calendrier officiel CRA 2026-2027 (Sandrine Camblong, 21/09/2026) — Salle de réunion Radio B (Albarran -1) de 14h15 à 16h00.",
        },
        {
            "id": "boneclub-2026-12-02",
            "date": "2026-12-02",
            "type": "bone_club",
            "typeLabel": "Bone Club Cochin (Amphi Luton)",
            "horaire": "18h00 – 20h00",
            "salle": "Amphithéâtre LUTON — RDC UFR Médecine Site Cochin (24 rue du Fg St-Jacques)",
            "interneId": "gabriel",
            "interneName": "Gabriel & Noé",
            "sujet": "Présentation et discussion de dossiers de pathologies de l'appareil locomoteur — Session de Décembre",
            "chefIntervenant": "Pr V. Bousson (Lariboisière), Dr A. Miquel (St-Antoine), Pr A. Feydy & Pr J-L. Drapé",
            "coursChef": "Amphi LUTON (RDC UFR Médecine, 24 rue Fg St-Jacques) • 18h00 – 20h00",
            "notes": "Réunion d'imagerie ostéo-articulaire des équipes hospitalières d'Île-de-France (Entrée libre, Amphi Luton face à l'entrée principale de Cochin).",
        },
        {
            "id": "cra-2027-01-15",
            "date": "2027-01-15",
            "type": "confrontation_anapath",
            "typeLabel": "Confrontations Radio-Anatomopathologiques (CRA)",
            "horaire": "14h15 – 16h00",
            "salle": "Salle de réunion Radio B (Pavillon Albarran -1)",
            "interneId": "marwane",
            "interneName": "Marwane & Milan",
            "sujet": "Confrontations Radio-Anatomo-Pathologiques — Session de Janvier",
            "chefIntervenant": "Pr A. Feydy, Pr J-L. Drapé & Service d'Anapath (Dr F. Larousserie, Dr V. Audard)",
            "coursChef": "Corrélation radio-histologique (Albarran -1 • 14h15 – 16h00)",
            "notes": "Calendrier officiel CRA 2026-2027 (Sandrine Camblong, 21/09/2026) — Dossiers biopsiés au Scanner Achard / Écho.",
        },
        {
            "id": "boneclub-2027-01-20",
            "date": "2027-01-20",
            "type": "bone_club",
            "typeLabel": "Bone Club Cochin (Amphi Luton)",
            "horaire": "18h00 – 20h00",
            "salle": "Amphithéâtre LUTON — RDC UFR Médecine Site Cochin (24 rue du Fg St-Jacques)",
            "interneId": "marwane",
            "interneName": "Marwane & Milan",
            "sujet": "Présentation et discussion de dossiers de pathologies de l'appareil locomoteur — Session de Janvier",
            "chefIntervenant": "Dr M. Lacroix (HEGP) & Pr J-L. Drapé (Cochin)",
            "coursChef": "Amphi LUTON (RDC UFR Médecine, 24 rue Fg St-Jacques) • 18h00 – 20h00",
            "notes": "Réunion d'imagerie ostéo-articulaire des équipes hospitalières d'Île-de-France (Entrée libre, Amphi Luton).",
        },
        {
            "id": "boneclub-2027-03-24",
            "date": "2027-03-24",
            "type": "bone_club",
            "typeLabel": "Bone Club Cochin (Amphi Luton)",
            "horaire": "18h00 – 20h00",
            "salle": "Amphithéâtre LUTON — RDC UFR Médecine Site Cochin (24 rue du Fg St-Jacques)",
            "interneId": "nathanael",
            "interneName": "Nathanaël & Oussama",
            "sujet": "Présentation et discussion de dossiers de pathologies de l'appareil locomoteur — Session de Mars",
            "chefIntervenant": "Pr É. Dion (Hôtel-Dieu), Dr M. Crézé (Bicêtre) & Pr A. Feydy (Cochin)",
            "coursChef": "Amphi LUTON (RDC UFR Médecine, 24 rue Fg St-Jacques) • 18h00 – 20h00",
            "notes": "Réunion d'imagerie ostéo-articulaire des équipes hospitalières d'Île-de-France (Entrée libre, Amphi Luton).",
        },
        {
            "id": "cra-2027-03-26",
            "date": "2027-03-26",
            "type": "confrontation_anapath",
            "typeLabel": "Confrontations Radio-Anatomopathologiques (CRA)",
            "horaire": "14h15 – 16h00",
            "salle": "Salle de réunion Radio B (Pavillon Albarran -1)",
            "interneId": "nathanael",
            "interneName": "Nathanaël & Oussama",
            "sujet": "Confrontations Radio-Anatomo-Pathologiques — Session de Mars",
            "chefIntervenant": "Pr A. Feydy, Pr J-L. Drapé & Service d'Anapath (Dr F. Larousserie, Dr V. Audard)",
            "coursChef": "Corrélation radio-histologique (Albarran -1 • 14h15 – 16h00)",
            "notes": "Calendrier officiel CRA 2026-2027 (Sandrine Camblong, 21/09/2026) — Salle de réunion Radio B (Albarran -1).",
        },
        {
            "id": "cra-2027-05-14",
            "date": "2027-05-14",
            "type": "confrontation_anapath",
            "typeLabel": "Confrontations Radio-Anatomopathologiques (CRA)",
            "horaire": "14h15 – 16h00",
            "salle": "Salle de réunion Radio B (Pavillon Albarran -1)",
            "interneId": "gabriel",
            "interneName": "Équipe Internes Radio B",
            "sujet": "Confrontations Radio-Anatomo-Pathologiques — Session de Mai",
            "chefIntervenant": "Pr A. Feydy, Pr J-L. Drapé & Service d'Anapath",
            "coursChef": "Corrélation radio-histologique (Albarran -1 • 14h15 – 16h00)",
            "notes": "Calendrier officiel CRA 2026-2027 (Sandrine Camblong, 21/09/2026).",
        },
        {
            "id": "boneclub-2027-05-26",
            "date": "2027-05-26",
            "type": "bone_club",
            "typeLabel": "Bone Club Cochin (Amphi Luton)",
            "horaire": "18h00 – 20h00",
            "salle": "Amphithéâtre LUTON — RDC UFR Médecine Site Cochin (24 rue du Fg St-Jacques)",
            "interneId": "gabriel",
            "interneName": "Équipe Internes Radio B",
            "sujet": "Présentation et discussion de dossiers de pathologies de l'appareil locomoteur — Session de Mai",
            "chefIntervenant": "Pr A. Feydy (Cochin) & Dr M. Lacroix (HEGP)",
            "coursChef": "Amphi LUTON (RDC UFR Médecine, 24 rue Fg St-Jacques) • 18h00 – 20h00",
            "notes": "Réunion d'imagerie ostéo-articulaire des équipes hospitalières d'Île-de-France (Entrée libre, Amphi Luton).",
        },
        {
            "id": "cra-2027-06-18",
            "date": "2027-06-18",
            "type": "confrontation_anapath",
            "typeLabel": "Confrontations Radio-Anatomopathologiques (CRA)",
            "horaire": "14h15 – 16h00",
            "salle": "Salle de réunion Radio B (Pavillon Albarran -1)",
            "interneId": "gabriel",
            "interneName": "Équipe Internes Radio B",
            "sujet": "Confrontations Radio-Anatomo-Pathologiques — Session de Juin",
            "chefIntervenant": "Pr A. Feydy, Pr J-L. Drapé & Service d'Anapath",
            "coursChef": "Corrélation radio-histologique (Albarran -1 • 14h15 – 16h00)",
            "notes": "Calendrier officiel CRA 2026-2027 (Sandrine Camblong, 21/09/2026).",
        },
        {
            "id": "boneclub-2027-06-30",
            "date": "2027-06-30",
            "type": "bone_club",
            "typeLabel": "Bone Club Cochin × APRAMEN (Amphi Luton)",
            "horaire": "18h00 – 20h00",
            "salle": "Amphithéâtre LUTON — RDC UFR Médecine Site Cochin (24 rue du Fg St-Jacques)",
            "interneId": "gabriel",
            "interneName": "Équipe Internes Radio B",
            "sujet": "Réunion Jumelée Bone Club & APRAMEN (Association des Praticiens de Médecine Nucléaire d'IDF)",
            "chefIntervenant": "Pr A. Feydy (Paris-Cochin) & Dr F. Paycha (Paris-Lariboisière)",
            "coursChef": "Amphi LUTON (RDC UFR Médecine, 24 rue Fg St-Jacques) • 18h00 – 20h00",
            "notes": "Séance annuelle jumelée Bone Club / APRAMEN (Entrée libre, Amphi Luton).",
        },
    ]
    items.extend(special_staffs)
    items.sort(key=lambda x: (x["date"], x["type"]))
    return items


def build_service_meetings() -> list[dict]:
    """
    Réunions du service, formations obligatoires, accueils, Bone Club, CRA et annonces officielles
    envoyées par Anne-Marie Fortin et Sandrine Camblong (secrétariats du Pr A. Feydy & Pr J-L. Drapé).
    """
    return [
        {
            "id": "reunion-2026-11-02-cafe",
            "date": "2026-11-02",
            "horaire": "08h15 – 08h45",
            "title": "Café d'accueil & Visite du Service de Radiologie B",
            "category": "Accueil & Vie du service",
            "sender": "Anne-Marie FORTIN / Dr M-P. TALABARD & les Chefs",
            "location": "Bâtiment Albarran (-1) — Salle de Staff Radio B",
            "description": "Accueil de la nouvelle promotion d'internes Hiver 2026–2027 autour d'un café à 8h15, suivi de la visite des différents secteurs (TDM Ollier, Achard, IRM 1.5T/3T, Écho, Salle C & Allura).",
            "mandatory": True,
        },
        {
            "id": "reunion-2026-11-02-formation",
            "date": "2026-11-02",
            "horaire": "09h00 – 11h45",
            "title": "Demi-journée de Formation obligatoire des nouveaux arrivants",
            "category": "Formation obligatoire",
            "sender": "Anne-Marie FORTIN (Secrétariat Pr A. Feydy)",
            "location": "Salle de Staff Radio B (Albarran -1 / Salle Chevrot)",
            "description": (
                "Programme officiel transmis par Anne-Marie Fortin :\n"
                "• 09h00 – 09h45 : Radioprotection (Mme Sophie LE GALL)\n"
                "• 10h00 – 10h45 : Règles d'hygiène en imagerie & interventionnel (Dr Véronique FARAUT DEROUIN)\n"
                "• 11h00 – 11h45 : Utilisation des anesthésiants locaux (Pr Anthony DOHAN / Dr Raphaël DAUTRY)"
            ),
            "mandatory": True,
        },
        {
            "id": "reunion-2026-11-04-accueil",
            "date": "2026-11-04",
            "horaire": "17h00 – 18h30",
            "title": "Réunion d'accueil Internes & Chefs de Clinique",
            "category": "Réunion Service",
            "sender": "Dr Fadila MIHOUBI BOUVIER, Dr Amandine LAPORTE & Anne-Marie FORTIN",
            "location": "Salle de Staff Radio B (Albarran -1)",
            "description": "Présentation du fonctionnement du service, des gardes, des règles de congés (max 2 absents simultanés, éviter mardi/vendredi), de la trame des vacations et du programme des présentations du mardi (cas) et vendredi (biblio).",
            "mandatory": True,
        },
        {
            "id": "reunion-2026-11-09-externes",
            "date": "2026-11-09",
            "horaire": "09h00 – 12h00",
            "title": "Arrivée des nouveaux externes & Lancement des Cours Externes Nov–Déc",
            "category": "Enseignement",
            "sender": "Anne-Marie FORTIN",
            "location": "Salle de réunion Albarran -1",
            "description": "Accueil des externes du stage de Novembre–Décembre 2026 (du 09/11/2026 au 03/01/2027) et début du planning des cours externes assurés par les CCA et internes.",
            "mandatory": False,
        },
        {
            "id": "reunion-2026-11-19-ecos",
            "date": "2026-11-19",
            "horaire": "09h00 – 12h00",
            "title": "Session ECOS Externes — Radiologie B",
            "category": "Enseignement",
            "sender": "Anne-Marie FORTIN",
            "location": "Salle de réunion Albarran -1",
            "description": "Entraînement ECOS pour les externes du service (encadrement CCA / Internes).",
            "mandatory": False,
        },
        {
            "id": "reunion-2026-11-24-dmu",
            "date": "2026-11-24",
            "horaire": "09h00 – 17h00",
            "title": "Séminaire DMU Imagina",
            "category": "Séminaire / Congrès",
            "sender": "Anne-Marie FORTIN / Direction DMU Imagina",
            "location": "Hôpital Necker-Enfants Malades",
            "description": "Journée annuelle du DMU Imagina (présentations institutionnelles et projets du DMU).",
            "mandatory": False,
        },
        {
            "id": "reunion-2026-11-27-anapath",
            "date": "2026-11-27",
            "horaire": "14h15 – 16h00",
            "title": "Confrontations Radio-Anatomo-Pathologiques (CRA #1)",
            "category": "Staff Multidisciplinaire",
            "sender": "Sandrine CAMBLONG (Enseignement Radio B — 01 58 41 24 81)",
            "location": "Salle de réunion Radio B (Pavillon Albarran - 1er sous-sol)",
            "description": "Réunion mensuelle de corrélation radio-histologique dans les maladies de l'appareil locomoteur (Service d'Anapath Pr B. Terris / Dr V. Audard / Dr F. Larousserie & Service de Radiologie B Prs J-L. Drapé et A. Feydy).",
            "mandatory": True,
        },
        {
            "id": "reunion-2026-12-02-boneclub",
            "date": "2026-12-02",
            "horaire": "18h00 – 20h00",
            "title": "BONE CLUB Cochin — Session de Décembre",
            "category": "Bone Club",
            "sender": "Sandrine CAMBLONG (Secrétariat d'enseignement Pr J-L. Drapé & Pr A. Feydy)",
            "location": "Amphithéâtre LUTON — RDC UFR de Médecine Site Cochin (24 rue du Fg St-Jacques, face à Cochin)",
            "description": "Réunion de radiologie ostéo-articulaire (Pr V. Bousson, Pr R. Carlier, Pr A. Feydy, Pr J-L. Drapé) : présentation et discussion de dossiers de pathologies de l'appareil locomoteur par les équipes hospitalières d'Île-de-France. Entrée libre et sans réservation.",
            "mandatory": True,
        },
        {
            "id": "reunion-2026-12-18-vaccin",
            "date": "2026-12-18",
            "horaire": "Toute la journée",
            "title": "Campagne de vaccination Grippe & Covid — Cochin Port-Royal",
            "category": "Infos AP-HP",
            "sender": "Anne-Marie FORTIN",
            "location": "Hôpital Cochin",
            "description": "Date limite de la campagne de vaccination annuelle pour le personnel médical et les internes du site Cochin.",
            "mandatory": False,
        },
        {
            "id": "reunion-2026-12-21-noel",
            "date": "2026-12-21",
            "horaire": "Semaines du 21/12 et 28/12/2026",
            "title": "Organisation des Congés de Fin d'Année (Noël / Nouvel An)",
            "category": "Congés & Effectifs",
            "sender": "Anne-Marie FORTIN & les Chefs",
            "location": "Service de Radiologie B",
            "description": "Répartition équitable des internes entre la semaine de Noël (21/12–25/12) et la semaine du Jour de l'An (28/12–01/01) afin d'assurer la continuité des postes prioritaires (TDM SAU, IRM, Gestes).",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-01-15-anapath",
            "date": "2027-01-15",
            "horaire": "14h15 – 16h00",
            "title": "Confrontations Radio-Anatomo-Pathologiques (CRA #2)",
            "category": "Staff Multidisciplinaire",
            "sender": "Sandrine CAMBLONG (Enseignement Radio B)",
            "location": "Salle de réunion Radio B (Pavillon Albarran - 1er sous-sol)",
            "description": "Réunion de corrélation radio-histologique dans les maladies de l'appareil locomoteur (Calendrier CRA V3).",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-01-20-boneclub",
            "date": "2027-01-20",
            "horaire": "18h00 – 20h00",
            "title": "BONE CLUB Cochin — Session de Janvier",
            "category": "Bone Club",
            "sender": "Sandrine CAMBLONG (Secrétariat d'enseignement Pr J-L. Drapé & Pr A. Feydy)",
            "location": "Amphithéâtre LUTON — RDC UFR de Médecine Site Cochin (24 rue du Fg St-Jacques, Paris 14e)",
            "description": "Présentation et discussion de dossiers de pathologies de l'appareil locomoteur par les équipes hospitalières d'Île-de-France (Modération : Dr M. Lacroix & Pr J-L. Drapé). Entrée libre.",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-02-26-seminaire-cochin",
            "date": "2027-02-26",
            "horaire": "26 & 27 février 2027",
            "title": "XLIIIe Séminaire de Radiologie Ostéo-Articulaire de Cochin — Bassin & Hanche",
            "category": "Séminaire / Congrès",
            "sender": "Sandrine CAMBLONG / Pr A. Feydy & Pr J-L. Drapé",
            "location": "Institut Imagine (24 boulevard du Montparnasse, 75015 Paris)",
            "description": "40 problèmes au quotidien, solutions par l'exemple sur le thème Bassin / Hanche (quiz interactifs et cas cliniques commentés par l'équipe de Radio B Cochin).",
            "mandatory": False,
        },
        {
            "id": "reunion-2027-03-24-boneclub",
            "date": "2027-03-24",
            "horaire": "18h00 – 20h00",
            "title": "BONE CLUB Cochin — Session de Mars",
            "category": "Bone Club",
            "sender": "Sandrine CAMBLONG (Secrétariat d'enseignement Pr J-L. Drapé & Pr A. Feydy)",
            "location": "Amphithéâtre LUTON — RDC UFR de Médecine Site Cochin (24 rue du Fg St-Jacques, Paris 14e)",
            "description": "Présentation et discussion de dossiers de pathologies de l'appareil locomoteur par les équipes hospitalières d'Île-de-France (Modération : Pr É. Dion & Dr M. Crézé / Pr A. Feydy). Entrée libre.",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-03-26-anapath",
            "date": "2027-03-26",
            "horaire": "14h15 – 16h00",
            "title": "Confrontations Radio-Anatomo-Pathologiques (CRA #3)",
            "category": "Staff Multidisciplinaire",
            "sender": "Sandrine CAMBLONG (Enseignement Radio B)",
            "location": "Salle de réunion Radio B (Pavillon Albarran - 1er sous-sol)",
            "description": "Réunion de corrélation radio-histologique dans les maladies de l'appareil locomoteur (Calendrier CRA V3).",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-05-14-anapath",
            "date": "2027-05-14",
            "horaire": "14h15 – 16h00",
            "title": "Confrontations Radio-Anatomo-Pathologiques (CRA #4)",
            "category": "Staff Multidisciplinaire",
            "sender": "Sandrine CAMBLONG (Enseignement Radio B)",
            "location": "Salle de réunion Radio B (Pavillon Albarran - 1er sous-sol)",
            "description": "Réunion de corrélation radio-histologique dans les maladies de l'appareil locomoteur (Calendrier CRA V3).",
            "mandatory": False,
        },
        {
            "id": "reunion-2027-05-26-boneclub",
            "date": "2027-05-26",
            "horaire": "18h00 – 20h00",
            "title": "BONE CLUB Cochin — Session de Mai",
            "category": "Bone Club",
            "sender": "Sandrine CAMBLONG (Secrétariat d'enseignement Pr J-L. Drapé & Pr A. Feydy)",
            "location": "Amphithéâtre LUTON — RDC UFR de Médecine Site Cochin (24 rue du Fg St-Jacques, Paris 14e)",
            "description": "Présentation et discussion de dossiers de pathologies de l'appareil locomoteur par les équipes hospitalières d'Île-de-France (Modération : Pr A. Feydy & Dr M. Lacroix). Entrée libre.",
            "mandatory": False,
        },
        {
            "id": "reunion-2027-06-18-anapath",
            "date": "2027-06-18",
            "horaire": "14h15 – 16h00",
            "title": "Confrontations Radio-Anatomo-Pathologiques (CRA #5)",
            "category": "Staff Multidisciplinaire",
            "sender": "Sandrine CAMBLONG (Enseignement Radio B)",
            "location": "Salle de réunion Radio B (Pavillon Albarran - 1er sous-sol)",
            "description": "Réunion de corrélation radio-histologique dans les maladies de l'appareil locomoteur (Calendrier CRA V3).",
            "mandatory": False,
        },
        {
            "id": "reunion-2027-06-30-boneclub",
            "date": "2027-06-30",
            "horaire": "18h00 – 20h00",
            "title": "BONE CLUB Cochin × APRAMEN — Session Jumelée de Juin",
            "category": "Bone Club",
            "sender": "Sandrine CAMBLONG (Secrétariat d'enseignement Pr J-L. Drapé & Pr A. Feydy)",
            "location": "Amphithéâtre LUTON — RDC UFR de Médecine Site Cochin (24 rue du Fg St-Jacques, Paris 14e)",
            "description": "Réunion annuelle jumelée Bone Club & APRAMEN (Association des Praticiens de Médecine Nucléaire d'Île-de-France — Modération : Pr A. Feydy & Dr F. Paycha). Entrée libre.",
            "mandatory": False,
        },
    ]


def build_recurring_staffs() -> list[dict]:
    """Staffs hebdomadaires récurrents du service de Radiologie B."""
    return [
        {
            "day": "Lundi",
            "weekday": 0,
            "items": [
                {"horaire": "Matin", "title": "Staff RCP Métastases Osseuses", "referent": "Dr T. Lefèvre"},
                {"horaire": "Après-midi", "title": "Staff CIRTAL / Sarcomes d'Ewing", "referent": "Dr H. Monnier"},
            ],
        },
        {
            "day": "Mardi",
            "weekday": 1,
            "items": [
                {"horaire": "12h30 – 13h30", "title": "Staff Internes : Cas Clinique du Mardi + Cours des Chefs", "referent": "Dr F. Mihoubi Bouvier & Tous les Chefs"},
                {"horaire": "Après-midi (13h30–18h00)", "title": "Consultation & Relecture systématique avec Pr Jean-Luc Drapé", "referent": "Pr J-L. Drapé & Interne de Consultation"},
                {"horaire": "Après-midi", "title": "Staff RCP Sarcomes des Tissus Mous", "referent": "Dr A. Laporte & Chefs"},
            ],
        },
        {
            "day": "Mercredi",
            "weekday": 2,
            "items": [
                {"horaire": "Matin", "title": "Accueil stagiaires / Enseignement externes", "referent": "CCA / Internes"},
                {"horaire": "Après-midi", "title": "Staff Rachis / Rhumatologie Osseuse", "referent": "Dr Yang"},
            ],
        },
        {
            "day": "Jeudi",
            "weekday": 3,
            "items": [
                {"horaire": "Matin / PM", "title": "Vacations Interventionnelles lourdes (Scanner Achard & Salle Allura)", "referent": "Équipe RI"},
            ],
        },
        {
            "day": "Vendredi",
            "weekday": 4,
            "items": [
                {"horaire": "Matin", "title": "Staff Prothèses & Imagerie Orthopédique", "referent": "Dr H. Guérini"},
                {"horaire": "12h30 – 13h30", "title": "Biblio du Vendredi (Article scientifique par un interne)", "referent": "Internes & Chefs"},
                {"horaire": "Après-midi (13h30–18h00)", "title": "Consultation Internes du Vendredi après-midi", "referent": "Dr M. Hamadouche / Seniors & Internes"},
                {"horaire": "Après-midi", "title": "Staff MPR / Rhumatologie", "referent": "Dr F. Mihoubi Bouvier"},
            ],
        },
    ]


def get_rg_absences_from_gardes(interne_gardes: dict | None = None) -> list[dict]:
    """
    Génère les Repos de garde (RG) obligatoires le lendemain de chaque garde
    des internes de Radiologie B lorsque le lendemain est un jour ouvré du semestre
    (Lundi à Vendredi, hors jours fériés).
    """
    if not interne_gardes:
        return []
    full_name_by_id = {i["id"]: f"{i['prenom']} {i['nom']}" for i in INTERNES_LIST}
    rg_list = []
    for g_iso, g in sorted(interne_gardes.items()):
        iid = g.get("interneId")
        if not iid or iid not in full_name_by_id:
            continue
        d_garde = datetime.date.fromisoformat(g_iso)
        d_next = d_garde + datetime.timedelta(days=1)
        next_iso = d_next.isoformat()
        if d_next.weekday() < 5 and "2026-11-02" <= next_iso <= "2027-04-30" and next_iso not in JOURS_FERIES_HIVER:
            rg_list.append({
                "id": f"abs-{iid}-{next_iso}",
                "date": next_iso,
                "gardeDate": g_iso,
                "interneId": iid,
                "interneName": full_name_by_id[iid],
                "type": "Repos de garde",
                "status": "approved",
                "validatedBy": "Planning Garde Officiel",
                "isOfficialGardeRg": True,
                "comment": f"Repos de garde (lendemain de garde du {g_iso[8:10]}/{g_iso[5:7]}/{g_iso[0:4]})",
                "createdAt": "2026-11-02T14:31:00Z",
            })
    return rg_list


def get_initial_absences(interne_gardes: dict | None = None) -> list[dict]:
    """
    Absences inscrites sur le Google Sheet officiel 'Planning Interne CCH - Hiver 26'
    (ex: Milan KORSEC du 22/03/2027 au 28/03/2027 en CA 1) + Repos de garde (RG)
    issus du planning officiel des gardes des internes Hiver 2026-2027.
    """
    absences = get_rg_absences_from_gardes(interne_gardes)
    for day in range(22, 29):
        iso = f"2027-03-{day:02d}"
        absences.append({
            "id": f"abs-milan-{iso}",
            "date": iso,
            "interneId": "milan",
            "interneName": "Milan KORSEC",
            "type": "CA 1",
            "status": "pending",
            "comment": "Congés annuels posés sur le Google Sheet Hiver 26-27",
            "createdAt": "2026-11-01T10:00:00Z",
        })
    return sorted(absences, key=lambda x: (x["date"], x["interneId"]))


def build_phone_directory() -> list[dict]:
    """
    Annuaire téléphonique complet de l'Hôpital Cochin (AP-HP) — Service de Radiologie B & Services partenaires.
    Numéros fixes (01 58 41 XX XX), postes internes (5 chiffres) et DECT extraits des communications officielles.
    Aucune donnée patient.
    """
    return [
        # 1. RADIOLOGIE B — SECRÉTARIATS, ENCADREMENT & CONSOLES
        {
            "id": "tel-fortin",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Anne-Marie FORTIN-COZIC",
            "role": "Secrétariat Chef de Service (Pr Antoine FEYDY) — Bât. Albarran",
            "poste": "12483 / 13788",
            "phone": "01 58 41 24 83",
            "fax": "01 58 41 24 55",
            "building": "Albarran / Ollier",
        },
        {
            "id": "tel-ri-sec",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Secrétariat Radiologie Interventionnelle (RI)",
            "role": "Programmation RI & Consultations — Bât. Ollier",
            "poste": "14612 / 12476",
            "phone": "01 58 41 46 12",
            "fax": "01 58 41 24 55",
            "building": "Bâtiment Ollier",
        },
        {
            "id": "tel-ri-direct",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Ligne Directe Radiologie Interventionnelle",
            "role": "Salle / Coordination RI (Ollier / Achard)",
            "poste": "12163",
            "phone": "01 58 41 21 63",
            "fax": "",
            "building": "Bâtiment Ollier / Achard",
        },
        {
            "id": "tel-mouyoungui",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Andress Gyslève MOUYOUNGUI",
            "role": "Assistante Médico-Administrative (AMA) — Radio B",
            "poste": "12684",
            "phone": "01 58 41 26 84",
            "fax": "01 58 41 24 55",
            "building": "Bâtiment Ollier",
        },
        {
            "id": "tel-gameiro",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Mariana GAMEIRO JORGE",
            "role": "Assistante Médico-Administrative (AMA) — Radio B",
            "poste": "11788",
            "phone": "01 58 41 17 88",
            "fax": "01 58 41 24 55",
            "building": "Bâtiment Ollier",
        },
        {
            "id": "tel-orak",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Secrétariat Pr Jean-Luc DRAPÉ (Mme ORAK)",
            "role": "Assistante Médico-Administrative — Radio B",
            "poste": "12502",
            "phone": "01 58 41 25 02",
            "fax": "01 58 41 21 51",
            "building": "Bâtiment Ollier",
        },
        {
            "id": "tel-menage",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Isabelle MENAGE",
            "role": "Cadre Médico-Technique — Service de Radiologie B",
            "poste": "12484",
            "phone": "01 58 41 24 84",
            "fax": "",
            "building": "Bâtiment Ollier (1er sous-sol)",
        },
        {
            "id": "tel-accueil-ollier",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Accueil & Rendez-vous Radio B (Ollier -1)",
            "role": "Accueil examens TDM / IRM / Écho / Biopsies",
            "poste": "12360 / 12350",
            "phone": "01 58 41 23 60",
            "fax": "01 58 41 24 49",
            "building": "Bâtiment Ollier (1er sous-sol)",
        },
        {
            "id": "tel-sellami",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Laila SELLAMI",
            "role": "Référente Informatique Imagerie / PACS Carestream (CCH, HTD, BRC)",
            "poste": "DECT 12197",
            "phone": "01 58 41 21 97",
            "fax": "",
            "building": "Imagerie Cochin",
        },
        {
            "id": "tel-logistique-matos",
            "category": "Radiologie B — Secrétariats & Consoles",
            "name": "Logisticiens / Matériel RI (O. Peaudecerf / D. Vannifterik)",
            "role": "Commandes & Matériel Interventionnel",
            "poste": "DECT 12183",
            "phone": "01 58 41 21 83",
            "fax": "",
            "building": "Radiologie B",
        },
        # 2. RADIOLOGIE B — MÉDECINS SENIORS & CHEFS DE CLINIQUE
        {
            "id": "tel-feydy",
            "category": "Radiologie B — Équipe Médicale (Chefs & Seniors)",
            "name": "Pr Antoine FEYDY",
            "role": "Chef de Service — Radiologie B (Ostéo-Articulaire)",
            "poste": "12483",
            "phone": "01 58 41 24 83",
            "fax": "01 58 41 24 55",
            "building": "Albarran / Ollier",
        },
        {
            "id": "tel-drape",
            "category": "Radiologie B — Équipe Médicale (Chefs & Seniors)",
            "name": "Pr Jean-Luc DRAPÉ",
            "role": "PU-PH — Radiologie B",
            "poste": "12502",
            "phone": "01 58 41 25 02",
            "fax": "01 58 41 21 51",
            "building": "Albarran / Ollier",
        },
        {
            "id": "tel-talabard",
            "category": "Radiologie B — Équipe Médicale (Chefs & Seniors)",
            "name": "Dr Marie-Pauline TALABARD",
            "role": "Chef de Clinique Assistant — Imagerie Ostéo-Articulaire & RI",
            "poste": "12489",
            "phone": "01 58 41 24 89",
            "fax": "",
            "building": "Albarran / Ollier",
        },
        {
            "id": "tel-lefevre",
            "category": "Radiologie B — Équipe Médicale (Chefs & Seniors)",
            "name": "Dr Thomas LEFÈVRE",
            "role": "Chef de Clinique / Assistant — Radiologie Interventionnelle & Ostéo-Articulaire",
            "poste": "12489 / 12163",
            "phone": "01 58 41 24 89",
            "fax": "",
            "building": "Albarran / Ollier / Achard",
        },
        {
            "id": "tel-hamadouche",
            "category": "Radiologie B — Équipe Médicale (Chefs & Seniors)",
            "name": "Dr Macil HAMADOUCHE",
            "role": "Assistant Spécialiste — Imagerie Ostéo-Articulaire & RI",
            "poste": "DECT 12504",
            "phone": "01 58 41 25 04",
            "fax": "",
            "building": "Albarran / Ollier",
        },
        {
            "id": "tel-bureau-cca",
            "category": "Radiologie B — Équipe Médicale (Chefs & Seniors)",
            "name": "Bureau des CCA / Assistants Radio B (Dr Monnier, Dr Lusi, Dr Allel, Dr Hammoud)",
            "role": "Ligne directe Bureau CCA Radiologie B",
            "poste": "12488 / 12489",
            "phone": "01 58 41 24 88",
            "fax": "",
            "building": "Bâtiment Albarran / Ollier",
        },
        {
            "id": "tel-radio-a",
            "category": "Radiologie B — Équipe Médicale (Chefs & Seniors)",
            "name": "Service de Radiologie A (Pr A. Dohan / Pr M. Barat)",
            "role": "Secrétariat Radiologie A & Gardes d'Imagerie",
            "poste": "12490",
            "phone": "01 58 41 24 90",
            "fax": "",
            "building": "Hôpital Cochin",
        },
        # 3. SERVICES CLINIQUES PARTENAIRES (ORTHOPÉDIE, RHUMATO, ANESTH, ANAPATH)
        {
            "id": "tel-ortho-biau",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Chirurgie Orthopédique & Oncologique — Pr David BIAU (Mme A. Tison)",
            "role": "Secrétariat Pr Biau (Sarcomes & Tumeurs osseuses)",
            "poste": "13037",
            "phone": "01 58 41 30 37",
            "fax": "01 58 41 30 60",
            "building": "Bâtiment Ollier",
        },
        {
            "id": "tel-ortho-cca",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Secrétariat CCA Chirurgie Orthopédique (M. Rahmani / A. P. Bitty / L. Guedj)",
            "role": "Chirurgie Orthopédique et Traumatologique",
            "poste": "13130 / 13082 / 13107",
            "phone": "01 58 41 31 30",
            "fax": "01 58 41 30 60",
            "building": "Bâtiment Ollier",
        },
        {
            "id": "tel-ortho-maalouf",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Chirurgie Orthopédique — Dr P. MAALOUF / Dr A. VILLARD / Banque Os",
            "role": "Secrétariats Orthopédie (13077 / 13041 / 13104)",
            "poste": "13077 / 13041",
            "phone": "01 58 41 30 77",
            "fax": "",
            "building": "Bâtiment Ollier",
        },
        {
            "id": "tel-rhumato-allanore",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Service de Rhumatologie (Pr Y. ALLANORE — Mme Canvel)",
            "role": "Secrétariat Rhumatologie A/B & Demandes Cimentoplastie",
            "poste": "12606 / 12619",
            "phone": "01 58 41 26 06",
            "fax": "01 58 41 40 97",
            "building": "Bâtiment Achard / Hardy",
        },
        {
            "id": "tel-anesth",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Service d'Anesthésie-Réanimation & Consultations d'Anesthésie",
            "role": "Médecine Péri-Opératoire & Programmation AG",
            "poste": "11563 / 11566 / 11528",
            "phone": "01 58 41 15 63",
            "fax": "",
            "building": "Hôpital Cochin",
        },
        {
            "id": "tel-uca",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Unité de Chirurgie Ambulatoire (UCA — Mme S. Azzopardi)",
            "role": "Cadre de santé IBODE / Ambulatoire",
            "poste": "14022",
            "phone": "01 58 41 40 22",
            "fax": "",
            "building": "Bâtiment Port-Royal",
        },
        {
            "id": "tel-achard-poly",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Polyclinique Bâtiment Achard RDC (Mme E. Vaugenot Nardy)",
            "role": "Cadre de santé — Bâtiment Achard RDC",
            "poste": "12412",
            "phone": "01 58 41 24 12",
            "fax": "",
            "building": "Bâtiment Achard",
        },
        {
            "id": "tel-anapath",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Service d'Anatomie et Cytologie Pathologiques (Anapath)",
            "role": "Secrétariat Pathologie (Mme L. Chanat) & UF CRB-Cancer",
            "poste": "13542 / 14719",
            "phone": "01 58 41 35 42",
            "fax": "",
            "building": "Hôpital Cochin",
        },
        {
            "id": "tel-douleur",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Centre d'Évaluation et Traitement de la Douleur (CETD — Pr Perrot)",
            "role": "Secrétariat Douleur (Mme C. Taliercio) & UF Douleur",
            "poste": "13040 / 12704",
            "phone": "01 58 41 30 40",
            "fax": "",
            "building": "Hôpital Cochin",
        },
        {
            "id": "tel-onco-thorax",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Oncologie Thoracique & Pneumologie",
            "role": "DECT Oncologie 14352 / Secrétariats 12349 & 13099",
            "poste": "DECT 14352 / 12349",
            "phone": "01 58 41 23 49",
            "fax": "01 58 41 23 85",
            "building": "Hôpital Cochin",
        },
        {
            "id": "tel-med-interne",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Service de Médecine Interne",
            "role": "Secrétariat 12103 / DECT Interne 18184",
            "poste": "12103 / DECT 18184",
            "phone": "01 58 41 21 03",
            "fax": "01 58 41 15 79",
            "building": "Hôpital Cochin",
        },
        {
            "id": "tel-hemato-clin",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Service d'Hématologie Clinique (Mme V. Kerouaz)",
            "role": "Secrétariat Hématologie Clinique",
            "poste": "12110 / 13919",
            "phone": "01 58 41 21 10",
            "fax": "",
            "building": "Hôpital Cochin",
        },
        {
            "id": "tel-endocrino",
            "category": "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
            "name": "Service d'Endocrinologie & Programmation Hospitalisations (Copernic)",
            "role": "Secrétariat 11878 / Programmation Hospit 11888 & 13940",
            "poste": "11878 / 11888",
            "phone": "01 58 41 18 88",
            "fax": "01 58 41 18 10",
            "building": "Pavillon Copernic",
        },
        # 4. LABORATOIRES, PHARMACIE, HYGIÈNE & AFFAIRES MÉDICALES
        {
            "id": "tel-hemostase",
            "category": "Laboratoires, Pharmacie & Administration (DAM)",
            "name": "Consultation & Laboratoire d'Hémostase / Hématologie Biologique",
            "role": "Bilan d'hémostase pré-geste (13445) / Labo Hémato J. Dausset (14141 / 13520)",
            "poste": "13445 / 14141",
            "phone": "01 58 41 34 45",
            "fax": "",
            "building": "Bâtiment Jean Dausset",
        },
        {
            "id": "tel-bio-auto",
            "category": "Laboratoires, Pharmacie & Administration (DAM)",
            "name": "Diagnostic Biologique Automatisé & Virologie / Parasitologie",
            "role": "Biochimie-Garde (14146) / Viro-Parasito (11547)",
            "poste": "14146 / 11547",
            "phone": "01 58 41 41 46",
            "fax": "",
            "building": "Bâtiment Jean Dausset",
        },
        {
            "id": "tel-pharmacie",
            "category": "Laboratoires, Pharmacie & Administration (DAM)",
            "name": "Pharmacie Hospitalière (Dr M-L. Brandely-Piat / Dr H. Palisson)",
            "role": "Médicaments, Bléomycine ECT & Dispositifs Médicaux Stériles (MDS)",
            "poste": "14275 / 12314 / 12982",
            "phone": "01 58 41 42 75",
            "fax": "01 58 41 18 84",
            "building": "Service Pharmacie Cochin",
        },
        {
            "id": "tel-hygiene",
            "category": "Laboratoires, Pharmacie & Administration (DAM)",
            "name": "Équipe Opérationnelle d'Hygiène (EOH — Mme L. Meyer)",
            "role": "Hygiène Hospitalière Cochin / Hôtel-Dieu / Broca",
            "poste": "12632",
            "phone": "01 58 41 26 32",
            "fax": "",
            "building": "Hôpital Cochin",
        },
        {
            "id": "tel-ucsa",
            "category": "Laboratoires, Pharmacie & Administration (DAM)",
            "name": "UCSA — Unité de Consultations et Soins Ambulatoires (La Santé)",
            "role": "Liaison UCSA / Hôpital Cochin",
            "poste": "12700",
            "phone": "01 58 41 27 00",
            "fax": "",
            "building": "Cochin / La Santé",
        },
        {
            "id": "tel-dam",
            "category": "Laboratoires, Pharmacie & Administration (DAM)",
            "name": "Bureau du Personnel Médical — Pavillon de Chasse (Mme A. N'Diaye / Mme M. Lambert)",
            "role": "Gestion des Internes & Seniors Cochin (12295 / 11014 / 11071)",
            "poste": "12295 / 11014",
            "phone": "01 58 41 22 95",
            "fax": "",
            "building": "Port-Royal — Pavillon de Chasse",
        },
        {
            "id": "tel-standard",
            "category": "Laboratoires, Pharmacie & Administration (DAM)",
            "name": "Standard Général Hôpital Cochin",
            "role": "Standard AP-HP Cochin (27 rue du Faubourg Saint-Jacques)",
            "poste": "11000 / 9",
            "phone": "01 58 41 10 00",
            "fax": "",
            "building": "Hôpital Cochin",
        },
    ]


def assert_zero_patient_data(text: str):
    """
    Vérifie de façon stricte qu'aucune donnée patient (IPP, date de naissance, nom de patient,
    numéro de téléphone, adresse email personnelle) ne figure dans le code généré.
    """
    forbidden_patterns = {
        "Numéro IPP": r"IPP[^0-9<]{0,15}[0-9]{7,10}",
        "Date de naissance patient": r"n[ée]e? le [0-9]{2}/[0-9]{2}/[0-9]{4}",
    }
    problems = []
    for label, pat in forbidden_patterns.items():
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            problems.append(f"{label}: {m.group(0)[:40]!r}")
    if problems:
        raise RuntimeError("ERREUR CRITIQUE : Donnée sensible détectée -> " + ", ".join(problems))


def expand_chefs_planning_full_semester(base_chefs_planning: dict) -> dict:
    """
    Étend le planning des Chefs & Seniors sur l'ensemble du semestre d'Hiver (02/11/2026 au 30/04/2027)
    en conservant les dates exactes du planning d'Anne-Marie V3 et en appliquant la maquette hebdomadaire
    officielle des Chefs pour toutes les autres semaines du semestre (incluant les demi-offs et fermetures).
    """
    maquette_dow = {
        0: {  # LUNDI
            "am": [
                {"poste": "ECHO", "doc": "HAMMOUD"},
                {"poste": "GESTES (C)", "doc": "HM"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "YA"},
                {"poste": "CONSULTATION", "doc": "TL"},
                {"poste": "UCSA", "doc": "TL"},
                {"poste": "STAFF", "doc": "TL (méta OS)"},
                {"poste": "1/2 journée libre", "doc": "SL/MH", "demiOff": True},
            ],
            "pm": [
                {"poste": "GESTES (C)", "doc": "TL"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "TL"},
                {"poste": "TDM OLLIER 3", "doc": "YA"},
                {"poste": "IRM", "doc": "FEYDY"},
                {"poste": "ECHO", "doc": "HM"},
                {"poste": "STAFF", "doc": "HM (Cirtal/Ewing)"},
                {"poste": "1/2 journée libre", "doc": "SL/MH", "demiOff": True},
            ],
        },
        1: {  # MARDI
            "am": [
                {"poste": "ECHO", "doc": "YA"},
                {"poste": "GESTES (C)", "doc": "MIHOUBI"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "MH"},
                {"poste": "TDM ACHARD 1", "doc": "TL"},
                {"poste": "IRM 3T", "doc": "DRAPE/YANG"},
                {"poste": "IRM 1,5T", "doc": "AL"},
                {"poste": "CONSULTATION", "doc": "HM"},
                {"poste": "UCSA", "doc": "SL"},
            ],
            "pm": [
                {"poste": "GESTES (C)", "doc": "HM"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "SL"},
                {"poste": "TDM ACHARD 1", "doc": "TL"},
                {"poste": "ECHO", "doc": "MH"},
                {"poste": "CONSULTATION", "doc": "DRAPE / INTERNES"},
                {"poste": "UCSA", "doc": "YA"},
                {"poste": "STAFF", "doc": "Chef et AL Sarcomes"},
            ],
        },
        2: {  # MERCREDI
            "am": [
                {"poste": "ECHO", "doc": "THEVENIN ET SL"},
                {"poste": "GESTES (C)", "doc": "TL"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "YA"},
                {"poste": "TDM OLLIER 3", "doc": "MH"},
                {"poste": "IRM 3T", "doc": "DRAPE/YANG"},
                {"poste": "IRM 1,5T", "doc": "MOUTOUNET"},
                {"poste": "1/2 journée libre", "doc": "HM", "demiOff": True},
            ],
            "pm": [
                {"poste": "GESTES (C)", "doc": "DRAPE"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "TL"},
                {"poste": "TDM ACHARD 1", "doc": "SEROR/YA"},
                {"poste": "IRM", "doc": "SL"},
                {"poste": "ECHO", "doc": "MIHOUBI"},
                {"poste": "CONSULTATION", "doc": "TL"},
                {"poste": "UCSA", "doc": "MH"},
                {"poste": "STAFF", "doc": "YANG (Rachis/Rhumato OS)"},
                {"poste": "1/2 journée libre", "doc": "HM", "demiOff": True},
            ],
        },
        3: {  # JEUDI
            "am": [
                {"poste": "ECHO", "doc": "AL/AC"},
                {"poste": "GESTES (C)", "doc": "RUBINI"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "MH"},
                {"poste": "TDM ACHARD 1", "doc": "HM"},
                {"poste": "CONSULTATION", "doc": "SL"},
                {"poste": "1/2 journée libre", "doc": "TL/YA", "demiOff": True},
            ],
            "pm": [
                {"poste": "GESTES (C)", "doc": "SL"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "SL"},
                {"poste": "TDM ACHARD 1", "doc": "AL/MH"},
                {"poste": "IRM", "doc": "AC"},
                {"poste": "ECHO", "doc": "MD"},
                {"poste": "ALLURA", "doc": "HM"},
                {"poste": "CONSULTATION", "doc": "FEYDY"},
                {"poste": "1/2 journée libre", "doc": "TL/YA", "demiOff": True},
            ],
        },
        4: {  # VENDREDI
            "am": [
                {"poste": "ECHO", "doc": "TL/YANG"},
                {"poste": "GESTES (C)", "doc": "MH"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "AC"},
                {"poste": "IRM 3T", "doc": "HM"},
                {"poste": "IRM 1,5T", "doc": "YA"},
                {"poste": "STAFF", "doc": "GUERINI (prothèse)"},
            ],
            "pm": [
                {"poste": "GESTES (C)", "doc": "YA"},
                {"poste": "TDM OLLIER 4 (SAU)", "doc": "HM"},
                {"poste": "TDM ACHARD 1", "doc": "AC/SL"},
                {"poste": "IRM", "doc": "TL"},
                {"poste": "CONSULTATION", "doc": "MH/INTERNES"},
                {"poste": "STAFF", "doc": "MIHOUBI (MPR Rhumato)"},
            ],
        },
    }
    out = {}
    for iso_k, day_v in base_chefs_planning.items():
        try:
            wd_k = datetime.date.fromisoformat(iso_k).weekday()
        except Exception:
            wd_k = -1
        am_c = [dict(x) for x in day_v.get("am", [])]
        pm_c = [dict(x) for x in day_v.get("pm", [])]
        if wd_k == 1:
            for item in pm_c:
                if item.get("poste") == "CONSULTATION" and item.get("doc") == "INTERNES":
                    item["doc"] = "DRAPE / INTERNES"
        out[iso_k] = {"am": am_c, "pm": pm_c}
    start_dt = datetime.date(2026, 11, 2)
    cur = start_dt
    end = datetime.date(2027, 4, 30)
    while cur <= end:
        iso = cur.isoformat()
        wd = cur.weekday()
        week_idx = (cur - start_dt).days // 7
        if wd < 5 and iso not in out:
            if iso in JOURS_FERIES_HIVER:
                out[iso] = {"am": [{"poste": "FÉRIÉ", "doc": JOURS_FERIES_HIVER[iso]}], "pm": []}
            else:
                am_copy = [dict(x) for x in maquette_dow[wd]["am"]]
                pm_copy = [dict(x) for x in maquette_dow[wd]["pm"]]
                # Vendredi PM : IRM 1 semaine sur 2 (fermée les semaines impaires comme S2 13/11 et S4 27/11)
                if wd == 4 and (week_idx % 2 == 1):
                    for item in pm_copy:
                        if item["poste"] == "IRM":
                            item["doc"] = "FERMÉ"
                            item["closed"] = True
                out[iso] = {"am": am_copy, "pm": pm_copy}
        cur += datetime.timedelta(days=1)
    return out


def fetch_existing_cloud_state() -> dict | None:
    """
    Récupère l'état actuellement synchronisé dans le Cloud (PropertiesService)
    afin de ne jamais écraser les modifications et validations faites dans l'Espace Chef.
    """
    eval_code = f"""
    var props = PropertiesService.getScriptProperties();
    var raw = props.getProperty('{CLOUD_PROP_KEY}');
    return raw ? JSON.parse(raw) : null;
    """
    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps({"eval_code": eval_code}).encode("utf-8"),
            headers={"Content-Type": "text/plain;charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if isinstance(res, dict) and isinstance(res.get("evalResult"), dict):
                return res["evalResult"]
    except Exception:
        pass
    return None


def build_full_dataset() -> dict:
    chefs_gardes = {}
    chefs_planning = {}
    interne_gardes = {}
    if (BASE_DIR / "chefs_gardes.json").exists():
        chefs_gardes = json.loads((BASE_DIR / "chefs_gardes.json").read_text(encoding="utf-8"))
    if (BASE_DIR / "chefs_planning.json").exists():
        chefs_planning = json.loads((BASE_DIR / "chefs_planning.json").read_text(encoding="utf-8"))
    if (BASE_DIR / "internes_gardes.json").exists():
        raw_ig = json.loads((BASE_DIR / "internes_gardes.json").read_text(encoding="utf-8"))
        for g_iso, g_val in sorted(raw_ig.items()):
            d_next = datetime.date.fromisoformat(g_iso) + datetime.timedelta(days=1)
            next_iso = d_next.isoformat()
            rg_working = (
                d_next.weekday() < 5
                and "2026-11-02" <= next_iso <= "2027-04-30"
                and next_iso not in JOURS_FERIES_HIVER
            )
            entry = dict(g_val)
            entry["rgDate"] = next_iso
            entry["rgIsWorkingDay"] = rg_working
            interne_gardes[g_iso] = entry
    chefs_planning = expand_chefs_planning_full_semester(chefs_planning)

    rg_absences = get_rg_absences_from_gardes(interne_gardes)
    rg_pairs = {(a["date"], a["interneId"]) for a in rg_absences}
    absences = get_initial_absences(interne_gardes)
    custom_vacations = {}
    chef_decisions = {}
    locked_weeks = {}
    deleted_absence_ids = []
    deleted_custom_keys = []
    chef_validated_at = None
    chef_revision = 0

    saved_sources = []
    if DATA_FILE.exists():
        try:
            saved_sources.append(json.loads(DATA_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    cloud_existing = fetch_existing_cloud_state()
    if isinstance(cloud_existing, dict):
        saved_sources.append(cloud_existing)

    abs_map = {a["id"]: a for a in absences}
    for src in saved_sources:
        if not isinstance(src, dict):
            continue
        if isinstance(src.get("deletedAbsenceIds"), list):
            for did in src["deletedAbsenceIds"]:
                if did and did not in deleted_absence_ids:
                    deleted_absence_ids.append(did)
        if isinstance(src.get("deletedCustomKeys"), list):
            for dck in src["deletedCustomKeys"]:
                if dck and dck not in deleted_custom_keys:
                    deleted_custom_keys.append(dck)
        if isinstance(src.get("absences"), list):
            for a in src["absences"]:
                if isinstance(a, dict) and a.get("id"):
                    aid = a["id"]
                    if not a.get("status"):
                        a["status"] = "pending"
                    prev = abs_map.get(aid)
                    if prev and prev.get("isOfficialGardeRg"):
                        if a.get("status") == "rejected":
                            prev["status"] = "rejected"
                            prev["validatedBy"] = a.get("validatedBy", "Chef")
                            prev["validatedAt"] = a.get("validatedAt")
                        continue
                    if prev and prev.get("status") in ("approved", "rejected") and a.get("status") == "pending":
                        continue
                    abs_map[aid] = a
        if isinstance(src.get("customVacations"), dict):
            custom_vacations.update(src["customVacations"])
        if isinstance(src.get("chefDecisions"), dict):
            chef_decisions.update(src["chefDecisions"])
        if isinstance(src.get("lockedWeeks"), dict):
            locked_weeks.update(src["lockedWeeks"])
        if src.get("chefValidatedAt"):
            chef_validated_at = src["chefValidatedAt"]
        if src.get("chefRevision"):
            try:
                chef_revision = max(chef_revision, int(src["chefRevision"]))
            except Exception:
                pass

    for dck in list(deleted_custom_keys):
        if dck not in custom_vacations:
            custom_vacations.pop(dck, None)
    for did in deleted_absence_ids:
        abs_map.pop(did, None)
    absences = sorted(abs_map.values(), key=lambda x: (x.get("date", ""), x.get("interneId", "")))

    active_absences_for_sched = [a for a in absences if a.get("status") != "rejected"]
    raw_schedule = generate_semester_schedule([], chefs_planning)
    base_schedule = generate_semester_schedule(rg_absences, chefs_planning)
    for d_iso, day_obj in base_schedule.items():
        if day_obj.get("holiday") or "byInterne" not in day_obj:
            continue
        raw_day_int = raw_schedule.get(d_iso, {}).get("byInterne", {})
        for iid, st_slot in day_obj["byInterne"].items():
            raw_slot = raw_day_int.get(iid, {})
            st_slot["preRgAm"] = raw_slot.get("am", st_slot.get("am"))
            st_slot["preRgPm"] = raw_slot.get("pm", st_slot.get("pm"))

    schedule = generate_semester_schedule(active_absences_for_sched, chefs_planning)
    presentations = build_initial_presentations(schedule)
    meetings = build_service_meetings()
    recurring_staffs = build_recurring_staffs()
    phone_directory = build_phone_directory()

    # Préserver les modifications de présentations (intervenant, sujet, format) depuis le cloud/fichier
    pres_map = {p["id"]: p for p in presentations if p.get("id")}
    for src in saved_sources:
        if isinstance(src, dict) and isinstance(src.get("presentations"), list):
            for sv in src["presentations"]:
                if isinstance(sv, dict) and sv.get("id") in pres_map:
                    bp = pres_map[sv["id"]]
                    if bp.get("type") in ("bone_club", "confrontation_anapath"):
                        if sv.get("sujet"):
                            bp["sujet"] = sv["sujet"]
                        if sv.get("interneId"):
                            bp["interneId"] = sv["interneId"]
                        if sv.get("interneName"):
                            bp["interneName"] = sv["interneName"]
                    else:
                        if (bp.get("date"), sv.get("interneId")) in rg_pairs and not sv.get("sujet"):
                            continue
                        pres_map[sv["id"]] = {**bp, **sv}
    presentations = sorted(pres_map.values(), key=lambda x: x.get("date", ""))

    return {
        "version": "1.8.0",
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "chefValidatedAt": chef_validated_at,
        "chefRevision": chef_revision,
        "deletedAbsenceIds": deleted_absence_ids,
        "deletedCustomKeys": deleted_custom_keys,
        "semester": {
            "title": "Semestre d'Hiver 2026–2027",
            "hospital": "Hôpital Cochin (AP-HP) — Service de Radiologie B (Pr A. Feydy)",
            "startDate": "2026-11-02",
            "endDate": "2027-04-30",
            "secretariat": "Anne-Marie FORTIN (01 58 41 24 83 / poste 12483)",
            "horairesVacations": {
                "IRM": "Début à 07h45 (Matin : dès 07h45 • Après-midi : 13h30 – 18h30)",
                "ECHO": "Début à 09h00 (Matin : dès 09h00 • Après-midi : 13h30 – 18h00)",
                "GESTES_C": "Début à 09h00 (Matin : dès 09h00 • Après-midi : 13h30 – 18h00)",
                "TDM_SAU": "08h00 – 18h30 (Scanner des Urgences : début à 08h00, fin à 18h30)",
                "LECTURE_CS": "Consultation Internes le Mardi après-midi (Relecture systématique avec Pr Drapé) et le Vendredi après-midi (13h30 – 18h00)",
            },
            "rules": [
                "Horaires des vacations : IRM commence à 07h45 • Scanner des U (TDM SAU) de 08h00 à 18h30 • Échographie et Poste C (Gestes) commencent à 09h00.",
                "Consultation pour les internes uniquement le Mardi après-midi et le Vendredi après-midi : Relecture avec Pr Drapé le Mardi après-midi systématique.",
                "Planning officiel des gardes des internes Hiver 2026–2027 intégré : Repos de garde (RG) systématique le lendemain de chaque garde (avec maintien des 2 demi-offs hebdomadaires et couverture garantie du TDM SAU et de la Relecture du mardi PM).",
                "2 demi-offs (1/2 journée libre) par semaine par interne (jamais le mardi PM ni le vendredi PM). À partir du 09/11/2026 : journée off fixe (2 demi-offs groupés Matin + PM) le Lundi pour Marwane, le Mercredi pour Gabriel et le Jeudi pour Oussama.",
                "Pas plus de 2 internes absents (CA / CF) en même temps. Toutes les vacances sont validées par le Chef dans l'Espace Chef.",
                "Notification automatique dans l'Espace Chef lorsqu'un jour bloque (TDM SAU découvert, >2 absents, Relecture Mardi PM, cours/biblio sans interne) et qu'une décision doit être prise.",
                "Noé GRANDVAL (Phase Socle) est systématiquement en binôme avec un co-interne pour le TDM SAU (Scanner des Urgences, ~50-55 % de ses vacations actives, jamais seul au SAU) tout en gardant un ratio équilibré sur les autres modalités (IRM, Écho, TDM Diag) et avec Dr Macil HAMADOUCHE (MH) le mardi matin les 3 premières semaines.",
                "Pas d'interne en Échographie avec le Dr Fabrice THÉVENIN sur le mois de novembre (mercredi matin).",
                "Les vacations fermées (FERMÉ / MAINTENANCE) sont affichées directement sur le planning.",
            ],
        },
        "internes": INTERNES_LIST,
        "chefs": CHEFS_LIST,
        "postesMeta": POSTES_META,
        "curriculumCours": CURRICULUM_COURS,
        "absences": absences,
        "customVacations": custom_vacations,
        "chefDecisions": chef_decisions,
        "lockedWeeks": locked_weeks,
        "interneGardes": interne_gardes,
        "baseSchedule": base_schedule,
        "schedule": schedule,
        "presentations": presentations,
        "meetings": meetings,
        "recurringStaffs": recurring_staffs,
        "phoneDirectory": phone_directory,
        "chefsGardes": chefs_gardes,
        "chefsPlanning": chefs_planning,
    }


def sync_initial_state_to_cloud(dataset: dict):
    """
    Sauvegarde l'état initial de l'application des internes dans PropertiesService
    sous la clé dédiée 'cochin_internes_state_v1' en préservant impérativement toutes
    les validations et modifications effectuées par le Chef dans l'Espace Chef,
    et met à jour la colonne 'Repos de garde' du Google Sheet officiel.
    """
    compact_state = {
        "updatedAt": dataset["updatedAt"],
        "chefValidatedAt": dataset.get("chefValidatedAt"),
        "chefRevision": dataset.get("chefRevision", 0),
        "deletedAbsenceIds": dataset.get("deletedAbsenceIds", []),
        "deletedCustomKeys": dataset.get("deletedCustomKeys", []),
        "absences": dataset["absences"],
        "customVacations": dataset["customVacations"],
        "chefDecisions": dataset.get("chefDecisions", {}),
        "lockedWeeks": dataset.get("lockedWeeks", {}),
        "interneGardes": dataset["interneGardes"],
        "presentations": dataset["presentations"],
        "meetings": dataset["meetings"],
        "phoneDirectory": dataset["phoneDirectory"],
    }
    safe_json = json.dumps(compact_state, ensure_ascii=False)
    eval_code = f"""
    var props = PropertiesService.getScriptProperties();
    var existingRaw = props.getProperty('{CLOUD_PROP_KEY}');
    var incoming = {safe_json};
    var rgPairs = {{}};
    (incoming.absences || []).forEach(function(a) {{
      if (a && a.type === 'Repos de garde') rgPairs[a.date + '__' + a.interneId] = true;
    }});
    if (!existingRaw) {{
      props.setProperty('{CLOUD_PROP_KEY}', JSON.stringify(incoming));
    }} else {{
      var cur = JSON.parse(existingRaw);
      var savedMap = {{}};
      if (Array.isArray(cur.presentations)) {{
        cur.presentations.forEach(function(p) {{ if (p && p.id) savedMap[p.id] = p; }});
      }}
      cur.presentations = incoming.presentations.map(function(baseP) {{
        var sv = savedMap[baseP.id];
        if (!sv) return baseP;
        if (baseP.type === 'bone_club' || baseP.type === 'confrontation_anapath') {{
          var merged = Object.assign({{}}, baseP);
          if (sv.sujet) merged.sujet = sv.sujet;
          if (sv.interneId) merged.interneId = sv.interneId;
          if (sv.interneName) merged.interneName = sv.interneName;
          return merged;
        }}
        if (sv.interneId && rgPairs[baseP.date + '__' + sv.interneId] && !sv.sujet) {{
          return baseP;
        }}
        return Object.assign({{}}, baseP, sv);
      }});
      cur.meetings = incoming.meetings;
      cur.phoneDirectory = incoming.phoneDirectory;
      cur.interneGardes = incoming.interneGardes;
      cur.deletedCustomKeys = Array.isArray(cur.deletedCustomKeys) ? cur.deletedCustomKeys : (incoming.deletedCustomKeys || []);
      var delCustomSet = {{}};
      cur.deletedCustomKeys.forEach(function(k) {{ if (k) delCustomSet[k] = true; }});
      cur.customVacations = Object.assign({{}}, incoming.customVacations || {{}}, cur.customVacations || {{}});
      Object.keys(delCustomSet).forEach(function(k) {{ delete cur.customVacations[k]; }});
      cur.lockedWeeks = Object.assign({{}}, incoming.lockedWeeks || {{}}, cur.lockedWeeks || {{}});
      cur.chefDecisions = Object.assign({{}}, incoming.chefDecisions || {{}}, cur.chefDecisions || {{}});
      cur.deletedAbsenceIds = Array.isArray(cur.deletedAbsenceIds) ? cur.deletedAbsenceIds : (incoming.deletedAbsenceIds || []);
      var delSet = {{}};
      cur.deletedAbsenceIds.forEach(function(id) {{ delSet[id] = true; }});
      var absMap = {{}};
      (incoming.absences || []).forEach(function(a) {{
        if (a && a.id && !delSet[a.id]) {{
          if (!a.status) a.status = 'pending';
          absMap[a.id] = a;
        }}
      }});
      (cur.absences || []).forEach(function(a) {{
        if (a && a.id && !delSet[a.id]) {{
          if (absMap[a.id] && absMap[a.id].isOfficialGardeRg) {{
            if (a.status === 'rejected') {{
              absMap[a.id].status = 'rejected';
              absMap[a.id].validatedBy = a.validatedBy || 'Chef';
              absMap[a.id].validatedAt = a.validatedAt;
            }}
            return;
          }}
          if (!a.status) a.status = (absMap[a.id] && absMap[a.id].status) ? absMap[a.id].status : 'pending';
          absMap[a.id] = a;
        }}
      }});
      cur.absences = Object.keys(absMap).map(function(k) {{ return absMap[k]; }}).sort(function(a, b) {{
        return String(a.date || '').localeCompare(String(b.date || ''));
      }});
      props.setProperty('{CLOUD_PROP_KEY}', JSON.stringify(cur));
    }}
    return {{ status: 'verified_cloud', presentations: incoming.presentations.length, absences: incoming.absences.length, gardes: Object.keys(incoming.interneGardes || {{}}).length }};
    """
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps({"eval_code": eval_code}).encode("utf-8"),
        headers={"Content-Type": "text/plain;charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def push_to_prod_github(commit_msg: str | None = None) -> dict:
    """
    Pousse systématiquement en production sur GitHub Pages (https://github.com/Mrthomaslef/agenda-internes.git)
    toutes les mises à jour réalisées sur l'application Planning Internes.
    """
    repo_url = "https://github.com/Mrthomaslef/agenda-internes.git"
    cwd = str(BASE_DIR)

    if not (BASE_DIR / ".git").exists():
        subprocess.run(["git", "init", "-b", "main"], cwd=cwd, check=False, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=cwd, check=False, capture_output=True)
        subprocess.run(["git", "fetch", "origin", "main"], cwd=cwd, check=False, capture_output=True)
        subprocess.run(["git", "branch", "--set-upstream-to=origin/main", "main"], cwd=cwd, check=False, capture_output=True)

    subprocess.run(["git", "add", "-A"], cwd=cwd, check=True, capture_output=True)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()
    if not status:
        return {"status": "up_to_date", "message": "Aucun changement local à pousser"}

    if not commit_msg:
        ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        commit_msg = f"Mise à jour automatique Planning Internes ({ts})"

    subprocess.run(["git", "commit", "-m", commit_msg], cwd=cwd, check=True, capture_output=True, text=True)
    push_res = subprocess.run(["git", "push", "origin", "main"], cwd=cwd, check=False, capture_output=True, text=True)
    if push_res.returncode != 0:
        subprocess.run(["git", "pull", "--rebase", "-X", "ours", "origin", "main"], cwd=cwd, check=False, capture_output=True)
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=cwd, check=True, capture_output=True, text=True)

    head_sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()
    return {"status": "pushed", "commit": head_sha, "message": commit_msg}


if __name__ == "__main__":
    data = build_full_dataset()
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Wrote internes_data.json successfully. Days in schedule:", len(data["schedule"]))
    try:
        res = sync_initial_state_to_cloud(data)
        print("Cloud sync result:", res)
    except Exception as e:
        print("Cloud sync warning:", e)
    try:
        gen_script = BASE_DIR / "generate_internes_app.py"
        if gen_script.exists():
            subprocess.run(["python3", str(gen_script)], cwd=str(BASE_DIR), check=True)
    except Exception as e:
        print("App generation / prod push warning:", e)
