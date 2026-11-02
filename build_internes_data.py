#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cochin Radio B — Espace Internes (Semestre Hiver 2026–2027)
Générateur et synchroniseur de l'application web mobile (PWA) dédiée aux internes.
APPLICATION 100% INDÉPENDANTE ET SÉPARÉE :
- Répertoire dédié : /Users/thomaslefevre/Documents/planning-interne/
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
    {"code": "TDM SAU", "label": "Scanner SAU (TDM SAU — Ollier 4)", "cat": "tdm_sau", "color": "#D97706", "horaire": "08h00 – 18h30", "horaireAm": "08h00 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "SCAN ACHARD", "label": "Scanner Achard (TDM Achard 1)", "cat": "scan_achard", "color": "#DB2777", "horaire": "08h30 – 18h30", "horaireAm": "08h30 – 13h00", "horairePm": "13h30 – 18h30"},
    {"code": "TDM OLLIER DIAG", "label": "Scanner Ollier (TDM Ollier 3 Diag)", "cat": "tdm_ollier", "color": "#0284C7", "horaire": "08h30 – 18h00", "horaireAm": "08h30 – 13h00", "horairePm": "13h30 – 18h00"},
    {"code": "IRM 3T", "label": "IRM 3T (dès 07h45)", "cat": "irm", "color": "#7C3AED", "horaire": "Dès 07h45", "horaireAm": "07h45 – 13h00", "horairePm": "Dès 13h00"},
    {"code": "IRM 1,5T", "label": "IRM 1,5T (dès 07h45)", "cat": "irm", "color": "#6D28D9", "horaire": "Dès 07h45", "horaireAm": "07h45 – 13h00", "horairePm": "Dès 13h00"},
    {"code": "IRM", "label": "IRM Après-midi (dès 13h00)", "cat": "irm", "color": "#7C3AED", "horaire": "Dès 13h00", "horaireAm": "07h45 – 13h00", "horairePm": "Dès 13h00"},
    {"code": "ECHO", "label": "Échographie Ostéo-Articulaire (Matin 09h00 • PM 14h00)", "cat": "echo", "color": "#0D9488", "horaire": "Matin 09h00 • PM 14h00", "horaireAm": "Dès 09h00", "horairePm": "Dès 14h00"},
    {"code": "GESTES (C)", "label": "Poste C / Gestes Interventionnels (Matin 09h00 • PM 14h00)", "cat": "gestes", "color": "#E11D48", "horaire": "Matin 09h00 • PM 14h00", "horaireAm": "Dès 09h00", "horairePm": "Dès 14h00"},
    {"code": "ALLURA", "label": "Salle Allura (Vasculaire / Os)", "cat": "gestes", "color": "#BE123C", "horaire": "Dès 14h00", "horaireAm": "08h30 – 13h00", "horairePm": "Dès 14h00"},
    {"code": "CONSULTATION", "label": "Consultation Internes (14h00 – 15h00 • Mardi PM & Vendredi PM)", "cat": "cs", "color": "#2563EB", "horaire": "14h00 – 15h00 (Mardi PM & Vendredi PM)", "horaireAm": "—", "horairePm": "14h00 – 15h00"},
    {"code": "LECTURE", "label": "Lecture / Relecture (14h00 – 16h00 • Mardi PM : Pr Drapé & Vendredi PM)", "cat": "lecture", "color": "#4F46E5", "horaire": "14h00 – 16h00 (Mardi PM : Relecture Pr Drapé)", "horaireAm": "—", "horairePm": "14h00 – 16h00"},
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

# Planning officiel des cours hebdomadaires du mardi (13h00 – 14h00) envoyé par Dr Fadila Mihoubi Bouvier (V3 + erratum WhatsApp)
FADILA_COURS_SCHEDULE = {
    "2026-11-03": ("Pr Jean-Luc DRAPÉ", "Mesures EOS Rachis"),
    "2026-11-10": ("Dr Amandine LAPORTE", "Consultation pré-interventionnelle"),
    "2026-11-17": ("Dr Fadila MIHOUBI BOUVIER", "Produits de contraste"),
    "2026-11-24": ("Dr Wassef KHALED", "IRM Fat Sat"),
    "2026-12-01": ("Dr Éric PESSIS", "Ménisques 1"),
    "2026-12-08": ("Dr Éric PESSIS", "Ménisques 2"),
    "2026-12-15": ("Dr Wassef KHALED", "Artéfacts IRM"),
    "2026-12-22": ("—", "Pas de cours"),
    "2026-12-29": ("—", "Pas de cours"),
    "2027-01-05": ("Pr Antoine FEYDY", "Rhumatisme axial"),
    "2027-01-12": ("Pr Jean-Luc DRAPÉ", "Optimisation séquences IRM"),
    "2027-01-19": ("Pr Jean-Luc DRAPÉ", "Ligament scapho-lunaire"),
    "2027-01-26": ("Dr Wassef KHALED", "Douleur du bord ulnaire"),
    "2027-02-02": ("Dr Hippolyte MONNIER", "Statique du pied"),
    "2027-02-09": ("Dr Macil HAMADOUCHE", "Sacro-iliaques : variantes"),
    "2027-02-16": ("Dr Étienne PLUOT", "Instabilité de l'épaule"),
    "2027-02-23": ("Dr Amandine LAPORTE", "Don't touch lesion"),
    "2027-03-02": ("Dr Wassef KHALED", "MODIC ou SPD"),
    "2027-03-09": ("Dr Éric PESSIS", "Artéfacts et prothèses"),
    "2027-03-16": ("Dr Marie-Pauline TALABARD", "Ablation percutanée OS"),
    "2027-03-23": ("Dr Thomas LEFÈVRE", "Lésions d'aspect kystique"),
    "2027-03-30": ("Dr Fadila MIHOUBI BOUVIER", "Lésion de surface"),
    "2027-04-06": ("Dr Wassef KHALED", "Tumeurs des tissus mous"),
    "2027-04-13": ("Dr Yazid ALLEL", "PTH"),
    "2027-04-20": ("Dr S. YANG", "Diagnostic d'un hypersignal musculaire"),
    "2027-04-27": ("Dr Stéphano LUSI", "Tumeurs cartilagineuses"),
}

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
      - R0 (Gabriel en S1) : Lundi PM = TDM OLLIER DIAG (Scanner Ollier 3)
      - R1 (Marwane en S1) : Lundi PM = IRM (avec Pr A. Feydy)
      - R2 (Milan en S1)   : Lundi PM = ECHO (US avec Dr H. Monnier)
      - R3 (Nathanaël en S1): Lundi PM = TDM SAU (au U le 02/11 PM, puis demi-off les lundis suivants)
      - R4 (Oussama en S1) : Lundi PM = GESTES (C) (ou 1/2 journée libre si Poste C fermé)
    - Séparation stricte des 3 scanners :
      * TDM SAU (Scanner des Urgences — Ollier 4)
      * SCAN ACHARD (Scanner Achard 1 — Diagnostique & Interventionnel)
      * TDM OLLIER DIAG (Scanner Ollier 3 — Diagnostique ostéo-articulaire)
    - Quota hebdomadaire de TDM SAU :
      * 2 TDM SAU par semaine pour chacun des 5 internes seniors (Gabriel, Marwane, Milan, Nathanaël, Oussama),
        et 3 uniquement à titre exceptionnel (en cas de congés / RG multiples la même semaine).
      * 3 TDM SAU par semaine pour Noé GRANDVAL ('noe', Phase Socle, toujours en binôme avec un co-interne senior,
        sauf exceptionnellement le mardi matin où Noé est posté en solo au TDM SAU avec Dr Macil HAMADOUCHE).
    - 2 demi-offs ('1/2 journée libre') par semaine chacun :
      * Consultation ('CONSULTATION') et Lecture ('LECTURE') pour les internes le Mardi après-midi et le Vendredi après-midi.
      * Relecture avec Pr Jean-Luc DRAPÉ le Mardi après-midi SYSTÉMATIQUE sur le créneau LECTURE.
    """
    weekly_roles = {
        0: {  # LUNDI (calé sur la base du Dr H. Monnier du 02/11 après-midi : TDM3, IRM, US/ECHO, U/TDM SAU, GESTES C)
            "am": {
                0: "1/2 journée libre",
                1: "1/2 journée libre",
                2: "GESTES (C)",
                3: "ECHO",
                4: "TDM SAU",
                "socle": "TDM SAU",  # TDM SAU n°1 de Noé (en binôme)
            },
            "pm": {
                0: "TDM OLLIER DIAG",  # S1: Gabriel en Scanner Ollier 3 (TDM3)
                1: "IRM",              # S1: Marwane en IRM (avec Pr A. Feydy)
                2: "ECHO",             # S1: Milan en US / Écho (avec Dr H. Monnier)
                3: "1/2 journée libre",# S1: Nathanaël au U le 02/11 PM, puis demi-off les lundis suivants
                4: "GESTES (C)",       # S1: Oussama (Poste C fermé le 02/11 PM -> 1/2 journée libre)
                "socle": "TDM OLLIER DIAG",  # Scanner Ollier 3 (TDM3)
            },
        },
        1: {  # MARDI (Staff Cas Clinique + Cours Chef à 12h30 • Mardi AM : Noé au TDM SAU solo avec Dr Macil Hamadouche • Mardi PM : pas de demi-off, Relecture systématique avec Pr Drapé)
            "am": {
                0: "1/2 journée libre",  # Demi-off matin fixe de Gabriel dès S1
                1: "IRM 3T",
                2: "IRM 1,5T",
                3: "GESTES (C)",
                4: "SCAN ACHARD",
                "socle_w1_3": "TDM SAU",  # TDM SAU de Noé en solo avec Dr Macil HAMADOUCHE (MH) le mardi matin
                "socle_after": "TDM SAU",
            },
            "pm": {
                0: "SCAN ACHARD",
                1: "ECHO",
                2: "GESTES (C)",
                3: "LECTURE",  # Relecture avec Pr Drapé (systématique)
                4: "TDM SAU",
                "socle": "CONSULTATION",  # Consultation Internes (Mardi PM) ou Scanner Achard
            },
        },
        2: {  # MERCREDI
            "am": {
                0: "IRM 1,5T",
                1: "IRM 3T",
                2: "1/2 journée libre",  # Demi-off matin de Milan
                3: "TDM OLLIER DIAG",
                4: "TDM SAU",
                "socle": "1/2 journée libre",  # Demi-off matin de Noé
            },
            "pm": {
                0: "TDM SAU",
                1: "1/2 journée libre",  # Demi-off après-midi de Marwane
                2: "SCAN ACHARD",
                3: "GESTES (C)",
                4: "IRM",
                "socle": "ECHO",  # Posté en Écho le mercredi après-midi (avec Dr Mihoubi)
            },
        },
        3: {  # JEUDI
            "am": {
                0: "ECHO",
                1: "1/2 journée libre",  # Demi-off matin fixe de Marwane
                2: "TDM SAU",
                3: "GESTES (C)",
                4: "1/2 journée libre",  # Demi-off matin d'Oussama en S1 (Lundi matin occupé par Formation/Accueil)
                "socle": "TDM SAU",  # TDM SAU n°3 de Noé avec Dr Macil HAMADOUCHE (MH) en binôme
            },
            "pm": {
                0: "1/2 journée libre",  # Demi-off après-midi de Gabriel
                1: "IRM",
                2: "1/2 journée libre",  # Demi-off après-midi de Milan
                3: "1/2 journée libre",  # Demi-off après-midi de Nathanaël (Écho fermée le jeudi PM)
                4: "TDM SAU",
                "socle": "1/2 journée libre",  # Demi-off après-midi de Noé
            },
        },
        4: {  # VENDREDI (Biblio du vendredi • Vendredi PM : pas de demi-off, Consultation Internes & Lecture)
            "am": {
                0: "GESTES (C)",
                1: "ECHO",
                2: "IRM 1,5T",
                3: "1/2 journée libre",  # Demi-off matin de Nathanaël
                4: "TDM SAU",
                "socle": "IRM 3T",  # Posté en IRM 3T le vendredi matin
            },
            "pm": {
                0: "IRM",
                1: "TDM SAU",
                2: "SCAN ACHARD",
                3: "CONSULTATION",  # Consultation Internes du vendredi après-midi (avec Dr Macil HAMADOUCHE / Internes)
                4: "GESTES (C)",
                "socle": "CONSULTATION",  # Consultation Internes / Lecture / Scanner Achard le vendredi après-midi (TDM SAU en S1)
            },
        },
    }
    return weekly_roles


# Liste des identifiants / noms de PH et PU-PH dans le planning des chefs :
# Toute vacation ouverte occupée par un PH / PU-PH doit impérativement avoir un interne,
# quitte à laisser une vacation d'Assistant Spécialiste (MH) ou de Chef de Clinique (TL, HM, SL, YA, MP) sans interne.
PH_DOC_TOKENS = {
    "FEYDY",
    "DRAPE",
    "DRAPÉ",
    "MIHOUBI",
    "MD",
    "AL",
    "LAPORTE",
    "AC",
    "COSTEA",
    "YANG",
    "RUBINI",
    "SEROR",
    "MOUTOUNET",
    "HAMMOUD",
}

MANDATORY_WEEKLY_POSTES = {
    (0, "am"): {"ECHO"},
    (0, "pm"): {"IRM"},
    (1, "am"): {"GESTES (C)", "IRM 3T", "IRM 1,5T"},
    (1, "pm"): {"LECTURE"},
    (2, "am"): {"IRM 3T", "IRM 1,5T", "TDM OLLIER DIAG", "ECHO"},
    (2, "pm"): {"GESTES (C)", "IRM", "SCAN ACHARD", "ECHO"},
    (3, "am"): {"ECHO", "GESTES (C)"},
    (3, "pm"): {"IRM"},
    (4, "am"): {"IRM 3T"},
    (4, "pm"): set(),
}


def is_ph_doc(doc_str: str) -> bool:
    if not doc_str:
        return False
    up = doc_str.upper()
    for sep in ("/", ",", "-", "(", ")", " "):
        up = up.replace(sep, " ")
    tokens = set(up.split())
    return bool(tokens & PH_DOC_TOKENS)


def get_ph_interne_postes_for_halfday(chefs_day: dict, half: str, wd: int | None = None, day_iso: str = "") -> set[str]:
    """
    Retourne l'ensemble des postes d'internes obligatoires (les vacations prioritaires)
    réellement OUVERTS sur la demi-journée donnée :
    - Lundi matin : ECHO
    - Lundi après-midi : IRM
    - Mardi matin : GESTES (C), IRM 3T, IRM 1,5T
    - Mardi après-midi : LECTURE (Relecture Pr Drapé)
    - Mercredi matin : IRM 3T, IRM 1,5T, TDM OLLIER DIAG (+ ECHO à partir de décembre)
    - Mercredi après-midi : GESTES (C), IRM, SCAN ACHARD, ECHO
    - Jeudi matin : ECHO, GESTES (C)
    - Jeudi après-midi : IRM
    - Vendredi matin : IRM 3T
    - Vendredi après-midi : (uniquement TDM SAU géré séparément)
    """
    if wd is None and day_iso:
        try:
            wd = datetime.date.fromisoformat(day_iso).weekday()
        except Exception:
            wd = None
    no_interne_thevenin_nov = (half == "am" and wd == 2 and day_iso.startswith("2026-11"))
    mandatory_for_slot = set(MANDATORY_WEEKLY_POSTES.get((wd, half), set()))
    if no_interne_thevenin_nov:
        mandatory_for_slot.discard("ECHO")
    if not chefs_day:
        return mandatory_for_slot

    open_set = get_open_interne_postes_for_halfday(chefs_day, half, wd)
    closed_codes = {c["poste"] for c in get_closed_vacations_for_halfday(chefs_day, half, wd)}
    return {p for p in mandatory_for_slot if p in open_set and p not in closed_codes}


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
                interne_poste = "CONSULTATION"
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
    Note : 'CONSULTATION' et 'LECTURE' sont ouverts aux internes le mardi après-midi (wd=1, half='pm')
    et le vendredi après-midi (wd=4, half='pm').
    """
    if not chefs_day:
        base = {"TDM SAU", "ECHO", "GESTES (C)", "SCAN ACHARD", "IRM 3T", "IRM 1,5T", "IRM", "TDM OLLIER DIAG", "ALLURA"}
        if half == "pm" and wd in (1, 4):
            base.add("CONSULTATION")
            base.add("LECTURE")
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
                open_set.add("CONSULTATION")
                open_set.add("LECTURE")
    if half == "pm" and wd in (1, 4):
        open_set.add("LECTURE")
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
    - PRIORITÉ STRICTE AUX VACATIONS DE PH / PU-PH : Sur toutes les vacations de PH il y a un interne,
      quitte à ne pas mettre d'interne avec un Assistant Spécialiste (MH) ou un Chef de Clinique (TL, HM, SL, YA, MP).
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
        #      Les demi-journées fixes préférées des demandeurs (dans la mesure du possible) + 1 autre demi-journée off libre :
        #        * Oussama : demi-journée off fixe le LUNDI MATIN (0, 'am')
        #        * Gabriel : demi-journée off fixe le MARDI MATIN (1, 'am')
        #        * Marwane : demi-journée off fixe le JEUDI MATIN (3, 'am')
        FIXED_OFF_HALFDAYS_FROM_W2 = {
            "oussama": (0, "am"),
            "gabriel": (1, "am"),
            "marwane": (3, "am"),
        }

        if week_idx == 0:
            for idx, iid in enumerate(senior_interne_ids):
                role_idx = (idx + week_idx) % 5
                post_am = day_roles["am"][role_idx]
                post_pm = day_roles["pm"][role_idx]
                if wd == 1 and post_pm == "LECTURE":
                    note_pm = "Relecture avec Pr Drapé (systématique)"
                elif wd == 1 and post_pm == "CONSULTATION":
                    note_pm = "Consultation Internes (Mardi PM)"
                elif wd == 4 and post_pm == "CONSULTATION":
                    note_pm = "Consultation Internes (Vendredi PM)"
                elif wd == 4 and post_pm == "LECTURE":
                    note_pm = "Lecture (Vendredi PM)"
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
            # Rotation sur 4 semaines garantissant systématiquement 1 demi-off MATIN + 1 demi-off APRÈS-MIDI
            # pour chacun des 5 internes seniors (sur 2 jours différents), tout en variant les créneaux :
            mod4 = week_idx % 4
            if mod4 == 1:
                weekly_offs_by_interne = {
                    "oussama": {(0, "am"), (3, "pm")},    # Lundi AM (fixe) + Jeudi PM
                    "gabriel": {(1, "am"), (0, "pm")},    # Mardi AM (fixe) + Lundi PM
                    "marwane": {(3, "am"), (0, "pm")},    # Jeudi AM (fixe) + Lundi PM
                    "milan": {(0, "am"), (2, "pm")},      # Lundi AM + Mercredi PM
                    "nathanael": {(4, "am"), (3, "pm")},  # Vendredi AM + Jeudi PM
                }
            elif mod4 == 2:
                weekly_offs_by_interne = {
                    "oussama": {(0, "am"), (2, "pm")},    # Lundi AM (fixe) + Mercredi PM
                    "gabriel": {(1, "am"), (3, "pm")},    # Mardi AM (fixe) + Jeudi PM
                    "marwane": {(3, "am"), (0, "pm")},    # Jeudi AM (fixe) + Lundi PM
                    "milan": {(4, "am"), (0, "pm")},      # Vendredi AM + Lundi PM
                    "nathanael": {(0, "am"), (3, "pm")},  # Lundi AM + Jeudi PM
                }
            elif mod4 == 3:
                weekly_offs_by_interne = {
                    "oussama": {(0, "am"), (3, "pm")},    # Lundi AM (fixe) + Jeudi PM
                    "gabriel": {(1, "am"), (0, "pm")},    # Mardi AM (fixe) + Lundi PM
                    "marwane": {(3, "am"), (2, "pm")},    # Jeudi AM (fixe) + Mercredi PM
                    "milan": {(0, "am"), (3, "pm")},      # Lundi AM + Jeudi PM
                    "nathanael": {(4, "am"), (0, "pm")},  # Vendredi AM + Lundi PM
                }
            else:
                weekly_offs_by_interne = {
                    "oussama": {(0, "am"), (3, "pm")},    # Lundi AM (fixe) + Jeudi PM
                    "gabriel": {(1, "am"), (2, "pm")},    # Mardi AM (fixe) + Mercredi PM
                    "marwane": {(3, "am"), (0, "pm")},    # Jeudi AM (fixe) + Lundi PM
                    "milan": {(2, "am"), (0, "pm")},      # Mercredi AM + Lundi PM
                    "nathanael": {(0, "am"), (3, "pm")},  # Lundi AM + Jeudi PM
                }

            am_pools_w2 = {
                0: [  # Lundi AM (3 seniors actifs : 2 demi-offs dont Oussama fixe) — Obligatoires : TDM SAU, ECHO (+ GESTES C)
                    "TDM SAU",
                    "ECHO",
                    "GESTES (C)",
                ],
                1: [  # Mardi AM (4 seniors actifs : Gabriel demi-off fixe, Noé au TDM SAU solo avec Dr Macil Hamadouche) — Obligatoires : GESTES (C), IRM 3T, IRM 1,5T (+ SCAN ACHARD, ECHO)
                    "GESTES (C)",
                    "IRM 3T",
                    "IRM 1,5T",
                    "SCAN ACHARD",
                    "ECHO",
                ],
                2: [  # Mercredi AM (4 ou 5 seniors actifs) — Obligatoires : TDM SAU, IRM 3T, IRM 1,5T (+ TDM OLLIER DIAG, GESTES C)
                    "TDM SAU",
                    "IRM 3T",
                    "IRM 1,5T",
                    "TDM OLLIER DIAG",
                    "GESTES (C)",
                ],
                3: [  # Jeudi AM (4 seniors actifs : Marwane demi-off fixe) — Obligatoires : TDM SAU, ECHO, GESTES (C) (+ SCAN ACHARD)
                    "TDM SAU",
                    "ECHO",
                    "GESTES (C)",
                    "SCAN ACHARD",
                ],
                4: [  # Vendredi AM (4 ou 5 seniors actifs, Noé en IRM 3T) — Obligatoires : TDM SAU, IRM 3T (+ ECHO, GESTES C, IRM 1,5T)
                    "TDM SAU",
                    "ECHO",
                    "GESTES (C)",
                    "IRM 1,5T",
                    "IRM 3T",
                ],
            }
            pm_pools_w2 = {
                0: [  # Lundi PM (3 seniors actifs : 2 demi-offs) — Obligatoires : TDM SAU, IRM (+ TDM OLLIER DIAG, ECHO, GESTES C)
                    "TDM SAU",
                    "IRM",
                    "TDM OLLIER DIAG",
                    "ECHO",
                    "GESTES (C)",
                ],
                1: [  # Mardi PM (5 seniors actifs, 0 off) — Obligatoires : TDM SAU, LECTURE (+ CONSULTATION, SCAN ACHARD, ECHO, GESTES C)
                    "LECTURE",
                    "TDM SAU",
                    "CONSULTATION",
                    "SCAN ACHARD",
                    "ECHO",
                    "GESTES (C)",
                ],
                2: [  # Mercredi PM (4 seniors actifs + Noé en ECHO) — Obligatoires : TDM SAU, GESTES (C), IRM, SCAN ACHARD, ECHO
                    "TDM SAU",
                    "GESTES (C)",
                    "IRM",
                    "SCAN ACHARD",
                ],
                3: [  # Jeudi PM (3 seniors actifs : 2 demi-offs + Noé demi-off) — Obligatoires : TDM SAU, IRM (+ SCAN ACHARD, ALLURA)
                    "TDM SAU",
                    "IRM",
                    "SCAN ACHARD",
                    "ALLURA",
                ],
                4: [  # Vendredi PM (5 seniors actifs, 0 off) — Obligatoire : TDM SAU (+ CONSULTATION, LECTURE, SCAN ACHARD, IRM, GESTES C)
                    "TDM SAU",
                    "CONSULTATION",
                    "SCAN ACHARD",
                    "GESTES (C)",
                    "IRM",
                    "LECTURE",
                ],
            }

            for iid in senior_interne_ids:
                by_interne[iid] = {"am": "", "pm": "", "note": "", "noteAm": "", "notePm": ""}

            # Attribution Matin (AM)
            active_am_seniors = []
            for iid in senior_interne_ids:
                if (wd, "am") in weekly_offs_by_interne[iid]:
                    is_fixed = FIXED_OFF_HALFDAYS_FROM_W2.get(iid) == (wd, "am")
                    lbl_am = "Demi-journée off fixe hebdomadaire" if is_fixed else "Demi-off hebdomadaire"
                    by_interne[iid]["am"] = "1/2 journée libre"
                    by_interne[iid]["noteAm"] = lbl_am
                else:
                    active_am_seniors.append(iid)

            pool_am = am_pools_w2[wd]
            used_am_turn = set()
            for idx_a, iid in enumerate(active_am_seniors):
                rot_am = [pool_am[(idx_a + week_idx + (week_idx // 2) + wd * 2 + k) % len(pool_am)] for k in range(len(pool_am))]
                chosen_am = next((p for p in rot_am if p not in used_am_turn), rot_am[0])
                used_am_turn.add(chosen_am)
                by_interne[iid]["am"] = chosen_am

            # Attribution Après-midi (PM)
            active_pm_seniors = []
            for iid in senior_interne_ids:
                if (wd, "pm") in weekly_offs_by_interne[iid]:
                    is_fixed = FIXED_OFF_HALFDAYS_FROM_W2.get(iid) == (wd, "pm")
                    lbl_pm = "Demi-journée off fixe hebdomadaire" if is_fixed else "Demi-off hebdomadaire"
                    by_interne[iid]["pm"] = "1/2 journée libre"
                    by_interne[iid]["notePm"] = lbl_pm
                else:
                    active_pm_seniors.append(iid)

            pool_pm = pm_pools_w2[wd]
            used_pm_turn = set()
            for idx_p, iid in enumerate(active_pm_seniors):
                rot_pm = [pool_pm[(idx_p + week_idx + (week_idx // 2) + wd * 2 + 1 + k) % len(pool_pm)] for k in range(len(pool_pm))]
                chosen_pm = next((p for p in rot_pm if p not in used_pm_turn), rot_pm[0])
                used_pm_turn.add(chosen_pm)
                by_interne[iid]["pm"] = chosen_pm
                if wd == 1 and chosen_pm == "LECTURE":
                    by_interne[iid]["notePm"] = "Relecture avec Pr Drapé (systématique)"
                elif wd == 1 and chosen_pm == "CONSULTATION":
                    by_interne[iid]["notePm"] = "Consultation Internes (Mardi PM)"
                elif wd == 4 and chosen_pm == "CONSULTATION":
                    by_interne[iid]["notePm"] = "Consultation Internes (Vendredi PM)"
                elif wd == 4 and chosen_pm == "LECTURE":
                    by_interne[iid]["notePm"] = "Lecture (Vendredi PM)"

            for iid in senior_interne_ids:
                if not by_interne[iid]["note"]:
                    by_interne[iid]["note"] = by_interne[iid]["noteAm"] or by_interne[iid]["notePm"]

        # 2. Attribution pour Noé (Phase Socle — 3 TDM SAU / semaine, dont le mardi matin en solo avec Dr Macil Hamadouche)
        #    - 1er mois (Novembre, week_idx < 4) :
        #      * S1 (week_idx == 0, lundi matin = Formation) : Mardi AM (solo avec Dr M. Hamadouche), Jeudi AM, Vendredi PM.
        #      * S2 à S4 (1 <= week_idx < 4) : Lundi AM, Mardi AM (solo avec Dr M. Hamadouche) et Jeudi AM (avec Dr M. Hamadouche).
        #    - À partir du 2e mois (Décembre à Avril, week_idx >= 4) :
        #      * Toujours au TDM SAU le mardi matin (solo avec Dr M. Hamadouche) + 2 autres TDM SAU en binôme qui varient chaque semaine.
        if week_idx < 4:
            if wd == 0:
                noe_am = "TDM SAU"
                noe_note_am = "Posté Socle Urgences (1er mois)"
                if week_idx % 3 == 0:
                    noe_pm = "TDM OLLIER DIAG"
                    noe_note_pm = "Scanner Ollier 3 (TDM3)"
                elif week_idx % 3 == 1:
                    noe_pm = "ECHO"
                    noe_note_pm = "Échographie (Phase Socle)"
                else:
                    noe_pm = "GESTES (C)"
                    noe_note_pm = "Salle C — Gestes (Phase Socle)"
            elif wd == 1:
                noe_am = "TDM SAU"
                noe_note_am = "Avec Dr Macil HAMADOUCHE (MH) — Solo SAU (exceptionnellement sans doublure)"
                noe_pm = "SCAN ACHARD" if (week_idx % 2 == 0) else "ECHO"
                noe_note_pm = "Scanner Achard 1" if noe_pm == "SCAN ACHARD" else "Échographie"
            elif wd == 2:
                noe_am = "1/2 journée libre"
                noe_note_am = "Demi-off hebdomadaire"
                noe_pm = "ECHO"
                noe_note_pm = "Échographie (avec Dr Mihoubi)"
            elif wd == 3:
                noe_am = "TDM SAU"
                noe_note_am = "Avec Dr Macil HAMADOUCHE (MH) — Posté Socle Urgences"
                noe_pm = "1/2 journée libre"
                noe_note_pm = "Demi-off hebdomadaire"
            else:  # wd == 4 (Vendredi)
                noe_am = "IRM 3T"
                noe_note_am = "IRM 3T (Vendredi matin)"
                if week_idx == 0:
                    noe_pm = "TDM SAU"
                    noe_note_pm = "Posté Socle Urgences"
                else:
                    noe_pm = "SCAN ACHARD" if (week_idx % 2 == 1) else "LECTURE"
                    noe_note_pm = "Scanner Achard 1" if noe_pm == "SCAN ACHARD" else "Lecture (Vendredi PM)"
        else:
            is_noe_cs_months = iso >= "2027-03-01"
            rot_noe = (week_idx - 4) % 5
            if rot_noe == 0:
                # SAU : Mar AM (solo MH), Lun PM, Ven PM (1 AM + 2 PM) • Offs : Mer AM, Jeu PM
                noe_week_plan = {
                    0: ("ECHO", "TDM SAU"),
                    1: ("TDM SAU", "CONSULTATION" if is_noe_cs_months else "SCAN ACHARD"),
                    2: ("1/2 journée libre", "TDM OLLIER DIAG"),
                    3: ("GESTES (C)", "1/2 journée libre"),
                    4: ("IRM 3T", "TDM SAU"),
                }
            elif rot_noe == 1:
                # SAU : Mar AM (solo MH), Mer PM, Ven PM (1 AM + 2 PM) • Offs : Lun AM, Jeu PM
                noe_week_plan = {
                    0: ("1/2 journée libre", "TDM OLLIER DIAG"),
                    1: ("TDM SAU", "ECHO"),
                    2: ("IRM 3T", "TDM SAU"),
                    3: ("ECHO", "1/2 journée libre"),
                    4: ("GESTES (C)", "TDM SAU"),
                }
            elif rot_noe == 2:
                # SAU : Mar AM (solo MH), Mer PM, Jeu PM (1 AM + 2 PM) • Offs : Lun PM, Jeu AM
                noe_week_plan = {
                    0: ("GESTES (C)", "1/2 journée libre"),
                    1: ("TDM SAU", "ECHO"),
                    2: ("TDM OLLIER DIAG", "TDM SAU"),
                    3: ("1/2 journée libre", "TDM SAU"),
                    4: ("IRM 3T", "LECTURE"),
                }
            elif rot_noe == 3:
                # SAU : Mar AM (solo MH), Mer PM, Ven AM (2 AM + 1 PM) • Offs : Mer AM, Lun PM
                noe_week_plan = {
                    0: ("GESTES (C)", "1/2 journée libre"),
                    1: ("TDM SAU", "LECTURE"),
                    2: ("1/2 journée libre", "TDM SAU"),
                    3: ("ECHO", "SCAN ACHARD"),
                    4: ("TDM SAU", "IRM" if (week_idx % 2 == 0) else ("CONSULTATION" if is_noe_cs_months else "LECTURE")),
                }
            else:  # rot_noe == 4
                # SAU : Mar AM (solo MH), Lun PM, Jeu PM (1 AM + 2 PM) • Offs : Mer PM, Ven AM
                noe_week_plan = {
                    0: ("ECHO", "TDM SAU"),
                    1: ("TDM SAU", "SCAN ACHARD"),
                    2: ("IRM 1,5T", "1/2 journée libre"),
                    3: ("GESTES (C)", "TDM SAU"),
                    4: ("1/2 journée libre", "CONSULTATION" if is_noe_cs_months else "LECTURE"),
                }
            noe_am, noe_pm = noe_week_plan[wd]

            def _noe_slot_note(poste_code: str, weekday_i: int, half_s: str) -> str:
                if poste_code == "TDM SAU":
                    if weekday_i == 1 and half_s == "am":
                        return "Avec Dr Macil HAMADOUCHE (MH) — Solo SAU (exceptionnellement sans doublure)"
                    return "Posté Socle Urgences"
                if poste_code == "1/2 journée libre":
                    return "Demi-off hebdomadaire"
                if poste_code == "LECTURE":
                    return "Relecture avec Pr Drapé" if weekday_i == 1 else "Lecture (Vendredi PM)"
                if poste_code == "CONSULTATION":
                    return "Consultation Internes (Mardi PM)" if weekday_i == 1 else "Consultation Internes (Vendredi PM)"
                return f"Phase Socle ({poste_code})"

            noe_note_am = _noe_slot_note(noe_am, wd, "am")
            noe_note_pm = _noe_slot_note(noe_pm, wd, "pm")

        by_interne["noe"] = {
            "am": noe_am,
            "pm": noe_pm,
            "note": noe_note_am or noe_note_pm,
            "noteAm": noe_note_am,
            "notePm": noe_note_pm,
        }

        def is_protected_fixed_off(interne_id: str, day_iso_str: str, half_k: str | None = None) -> bool:
            w_i = (datetime.date.fromisoformat(day_iso_str) - start_date).days // 7
            if w_i < 1:
                return False
            wd_i = datetime.date.fromisoformat(day_iso_str).weekday()
            fixed_slot = FIXED_OFF_HALFDAYS_FROM_W2.get(interne_id)
            if not fixed_slot:
                return False
            if half_k is None:
                return fixed_slot[0] == wd_i
            return fixed_slot == (wd_i, half_k)

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
        #       (sauf le mardi matin où Noé assure le TDM SAU en solo avec Dr Macil Hamadouche)
        #       et de la Relecture avec Pr Drapé le Mardi après-midi (wd == 1)
        #       Priorité : prélever d'abord sur une vacation non obligatoire (hors 13 vacations prioritaires)
        for h_sau in ("am", "pm"):
            is_tue_am_noe_solo = (wd == 1 and h_sau == "am" and by_interne["noe"]["am"] == "TDM SAU")
            has_sau = is_tue_am_noe_solo or any(
                by_interne[iid][h_sau] == "TDM SAU"
                for iid in senior_interne_ids
            )
            if not has_sau:
                nk_sau = "noteAm" if h_sau == "am" else "notePm"
                ph_sau_set = get_ph_interne_postes_for_halfday(chefs_day, h_sau, wd, iso)
                all_donors = ["ALLURA", "GESTES (C)", "ECHO", "IRM 1,5T", "SCAN ACHARD", "TDM OLLIER DIAG", "IRM 3T", "IRM", "CONSULTATION", "LECTURE"]
                donor_order = [d for d in all_donors if d not in ph_sau_set] + [d for d in all_donors if d in ph_sau_set]
                for donor_poste in donor_order:
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
                by_interne[iid]["pm"] == "LECTURE"
                for iid in senior_interne_ids
            )
            if not has_tue_cs:
                ph_tue_pm = get_ph_interne_postes_for_halfday(chefs_day, "pm", wd, iso)
                tue_donors = ["GESTES (C)", "ECHO", "SCAN ACHARD", "CONSULTATION"]
                tue_donor_order = [d for d in tue_donors if d not in ph_tue_pm] + [d for d in tue_donors if d in ph_tue_pm]
                for donor_poste in tue_donor_order:
                    replaced = False
                    for iid in senior_interne_ids:
                        if by_interne[iid]["pm"] == donor_poste:
                            by_interne[iid]["pm"] = "LECTURE"
                            by_interne[iid]["notePm"] = "Relecture avec Pr Drapé (systématique)"
                            if not by_interne[iid]["note"]:
                                by_interne[iid]["note"] = "Relecture avec Pr Drapé (systématique)"
                            replaced = True
                            break
                    if replaced:
                        break

        # 4. Gestion des vacations FERMÉES / MAINTENANCE et garantie zéro doublon hors TDM SAU
        for half, closed_map, open_set in [("am", closed_am_codes, open_am_codes), ("pm", closed_pm_codes, open_pm_codes)]:
            note_key = "noteAm" if half == "am" else "notePm"
            is_no_off_halfday = (half == "pm" and wd in (1, 4))
            ph_half_set = get_ph_interne_postes_for_halfday(chefs_day, half, wd, iso)
            used_by_seniors = set()
            for iid in senior_interne_ids:
                p = by_interne[iid][half]
                if p not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL") and p not in closed_map:
                    used_by_seniors.add(p)

            base_fallbacks = ["TDM OLLIER DIAG", "SCAN ACHARD", "GESTES (C)", "IRM", "IRM 3T", "IRM 1,5T", "ECHO", "ALLURA"]
            if half == "pm" and wd in (1, 4):
                base_fallbacks = ["CONSULTATION", "LECTURE"] + base_fallbacks
            no_interne_thevenin_nov = (half == "am" and wd == 2 and iso.startswith("2026-11"))
            if no_interne_thevenin_nov:
                base_fallbacks = [c for c in base_fallbacks if c != "ECHO"]
            fallback_candidates = [c for c in base_fallbacks if c in ph_half_set] + [c for c in base_fallbacks if c not in ph_half_set]

            for iid in senior_interne_ids:
                p = by_interne[iid][half]
                if p == "ECHO" and no_interne_thevenin_nov:
                    reassigned = None
                    for cand in fallback_candidates:
                        if cand in open_set and cand not in closed_map and cand not in used_by_seniors and cand != by_interne["noe"][half]:
                            reassigned = cand
                            break
                    if not reassigned:
                        reassigned = "1/2 journée libre"
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
                            if "CONSULTATION" in open_set and "CONSULTATION" not in closed_map and "CONSULTATION" not in used_by_seniors:
                                reassigned = "CONSULTATION"
                                used_by_seniors.add("CONSULTATION")
                            else:
                                reassigned = "LECTURE"
                                used_by_seniors.add("LECTURE")
                        else:
                            reassigned = "1/2 journée libre"
                    else:
                        used_by_seniors.add(reassigned)
                    by_interne[iid][half] = reassigned
                    if is_no_off_halfday and reassigned in ("LECTURE", "CONSULTATION"):
                        if reassigned == "CONSULTATION":
                            re_lbl = "Consultation Internes (Mardi PM)" if wd == 1 else "Consultation Internes (Vendredi PM)"
                        else:
                            re_lbl = "Relecture Pr Drapé" if wd == 1 else "Lecture"
                        by_interne[iid][note_key] = f"{p} {status_lbl.lower()} → {re_lbl}"
                    else:
                        by_interne[iid][note_key] = f"{p} {status_lbl.lower()}"
                    if not by_interne[iid]["note"]:
                        by_interne[iid]["note"] = by_interne[iid][note_key]

            noe_p = by_interne["noe"][half]
            if noe_p not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"):
                if noe_p in closed_map or (noe_p != "TDM SAU" and noe_p in used_by_seniors):
                    noe_cands = ["TDM OLLIER DIAG", "SCAN ACHARD", "ECHO", "IRM 1,5T", "IRM 3T", "IRM", "GESTES (C)"]
                    if half == "pm" and wd in (1, 4):
                        noe_cands = (["CONSULTATION", "LECTURE"] if iso >= "2027-03-01" else ["LECTURE"]) + noe_cands
                    if no_interne_thevenin_nov:
                        noe_cands = [c for c in noe_cands if c != "ECHO"]
                    reassigned_noe = None
                    for cand in noe_cands:
                        if cand in open_set and cand not in closed_map and cand not in used_by_seniors:
                            reassigned_noe = cand
                            break
                    if reassigned_noe:
                        by_interne["noe"][half] = reassigned_noe
                        if reassigned_noe == "CONSULTATION":
                            by_interne["noe"][note_key] = "Consultation Internes (Mardi PM)" if wd == 1 else "Consultation Internes (Vendredi PM)"
                        elif reassigned_noe == "LECTURE":
                            by_interne["noe"][note_key] = "Relecture avec Pr Drapé" if wd == 1 else "Lecture (Vendredi PM)"
                        else:
                            by_interne["noe"][note_key] = f"Phase Socle ({reassigned_noe})"
                    elif noe_p in closed_map:
                        status_lbl = closed_map[noe_p]
                        by_interne["noe"][half] = "TDM SAU"
                        by_interne["noe"][note_key] = f"{noe_p} {status_lbl.lower()} → TDM SAU"
                    else:
                        by_interne["noe"][half] = "TDM SAU"
                        by_interne["noe"][note_key] = "Posté Socle Urgences"
                    if not by_interne["noe"]["note"]:
                        by_interne["noe"]["note"] = by_interne["noe"][note_key]

        schedule[iso] = {
            "holiday": None,
            "am": [],
            "pm": [],
            "closedAm": closed_am,
            "closedPm": closed_pm,
            "byInterne": by_interne,
        }
        cur += datetime.timedelta(days=1)

    # 5. Couverture stricte des 13 vacations obligatoires + TDM SAU permanent,
    #    pose des demi-journées off en fonction (variées entre Matin et Après-midi : 1 AM + 1 PM par semaine),
    #    et équilibrage automatique sur les semaines suivantes si un interne n'a pas pu avoir ses 2 demi-offs.
    def get_available_open_postes(day_iso: str, half_key: str) -> list[str]:
        day_obj = schedule[day_iso]
        ch_day = (chefs_planning or {}).get(day_iso, {})
        dt_obj = datetime.date.fromisoformat(day_iso)
        wd_cur = dt_obj.weekday()
        open_set = get_open_interne_postes_for_halfday(ch_day, half_key, wd_cur)
        ph_set = get_ph_interne_postes_for_halfday(ch_day, half_key, wd_cur, day_iso)
        closed_codes = {c["poste"] for c in (day_obj["closedAm"] if half_key == "am" else day_obj["closedPm"])}
        used = {
            st[half_key]
            for st in day_obj["byInterne"].values()
            if st[half_key] not in ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ")
        }
        base_cands = ["TDM OLLIER DIAG", "SCAN ACHARD", "GESTES (C)", "IRM", "IRM 3T", "IRM 1,5T", "ECHO", "ALLURA"]
        if half_key == "pm" and wd_cur in (1, 4):
            base_cands = ["CONSULTATION", "LECTURE"] + base_cands
        if half_key == "am" and wd_cur == 2 and day_iso.startswith("2026-11"):
            base_cands = [c for c in base_cands if c != "ECHO"]
        candidates = [c for c in base_cands if c in ph_set] + [c for c in base_cands if c not in ph_set]
        return [c for c in candidates if c in open_set and c not in closed_codes and c not in used]

    all_interne_ids = [x["id"] for x in INTERNES_LIST]
    non_active_codes = ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL")
    non_mandatory_priority = [
        "ALLURA",
        "GESTES (C)",
        "ECHO",
        "IRM 1,5T",
        "SCAN ACHARD",
        "TDM OLLIER DIAG",
        "IRM 3T",
        "IRM",
        "CONSULTATION",
        "LECTURE",
    ]

    # Suivi du solde de demi-offs à reporter sur les semaines suivantes (carry-over)
    carry_over_offs: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    # Suivi cumulé des demi-offs Matin (AM) vs Après-midi (PM) sur le semestre pour varier au maximum
    total_am_offs_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_pm_offs_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    # Suivi cumulé des IRM d'après-midi sur le semestre pour équilibrer entre internes
    total_irm_pm_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    # Suivi cumulé des TDM SAU Matin (AM) vs Après-midi (PM) sur le semestre pour équilibrer dans la mesure du possible
    total_sau_am_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_sau_pm_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    # Suivi cumulé des vacations de Poste C (GESTES (C) / RI) Matin (AM) et Après-midi (PM) sur le semestre pour équilibrer entre internes
    total_gestes_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_ri_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_gestes_am_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_gestes_pm_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    # Suivi cumulé des Consultations (CONSULTATION : Mardi PM / Vendredi PM) et des Lectures (LECTURE) sur le semestre
    total_cs_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_cs_tue_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_cs_fri_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_lecture_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    # Suivi cumulé des vacations d'Échographie (ECHO) et d'IRM (Matin / PM) ainsi que Scanners diagnostiques sur le semestre
    total_echo_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_echo_am_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_echo_pm_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_irm_am_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_achard_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}
    total_ollier_counts: dict[str, int] = {iid: 0 for iid in all_interne_ids}

    for w_idx, iso_list in sorted(weeks_map.items()):
        active_isos = [d_iso for d_iso in iso_list if not schedule[d_iso].get("holiday")]

        def count_week_half_offs(interne_id: str, half_k: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                if schedule[d_chk]["byInterne"][interne_id][half_k] == "1/2 journée libre"
            )

        # Objectif de demi-offs pour la semaine = 2 maximum par interne (0 si >= 6 demi-journées de congés/RG)
        target_offs_for_week: dict[str, int] = {}
        vac_halfdays_by_interne: dict[str, int] = {}
        for iid in all_interne_ids:
            v_cnt = 0
            for d_iso in active_isos:
                st = schedule[d_iso]["byInterne"][iid]
                for h in ("am", "pm"):
                    if st[h] in ("VACANCES", "RG"):
                        v_cnt += 1
            vac_halfdays_by_interne[iid] = v_cnt
            if v_cnt >= 6:
                target_offs_for_week[iid] = 0
            else:
                target_offs_for_week[iid] = 2

        # 5A. Garantir d'abord que toutes les vacations obligatoires (TDM SAU + les 13 vacations listées) sont pourvues
        for d_iso in active_isos:
            wd_cur = datetime.date.fromisoformat(d_iso).weekday()
            ch_day = (chefs_planning or {}).get(d_iso, {})
            by_int = schedule[d_iso]["byInterne"]
            for h in ("am", "pm"):
                if d_iso == "2026-11-02" and h == "am":
                    continue
                nk = "noteAm" if h == "am" else "notePm"
                ph_set = get_ph_interne_postes_for_halfday(ch_day, h, wd_cur, d_iso)

                # 1) Toujours au moins un interne senior au TDM SAU (hors 02/11 matin = Formation/Accueil,
                #    et hors mardi matin où Noé est posté en solo au TDM SAU avec Dr Macil Hamadouche)
                is_tue_am_noe_solo = (wd_cur == 1 and h == "am" and by_int["noe"]["am"] not in ("RG", "VACANCES", "FÉRIÉ"))
                if is_tue_am_noe_solo:
                    by_int["noe"]["am"] = "TDM SAU"
                    by_int["noe"]["noteAm"] = "Avec Dr Macil HAMADOUCHE (MH) — Solo SAU (exceptionnellement sans doublure)"
                has_senior_sau = is_tue_am_noe_solo or any(by_int[s_id][h] == "TDM SAU" for s_id in senior_interne_ids)
                if not has_senior_sau:
                    sau_donors = (
                        [p for p in non_mandatory_priority if p not in ph_set]
                        + ["1/2 journée libre"]
                        + [p for p in non_mandatory_priority if p in ph_set]
                    )
                    for donor_p in sau_donors:
                        replaced_s = False
                        ordered_sids = (
                            [s_id for s_id in senior_interne_ids if not is_protected_fixed_off(s_id, d_iso, h)]
                            + [s_id for s_id in senior_interne_ids if is_protected_fixed_off(s_id, d_iso, h)]
                        )
                        for s_id in ordered_sids:
                            if by_int[s_id][h] == donor_p:
                                by_int[s_id][h] = "TDM SAU"
                                by_int[s_id][nk] = "Permanence Scanner SAU obligatoire"
                                replaced_s = True
                                break
                        if replaced_s:
                            break

                # 2) Couvrir chacune des 13 vacations obligatoires ouvertes sur cette demi-journée (hors 02/11 matin = Formation/Accueil)
                if not (d_iso == "2026-11-02" and h == "am"):
                    for ph_poste in sorted(ph_set):
                        is_covered = any(by_int[any_id][h] == ph_poste for any_id in by_int)
                        if is_covered:
                            continue

                        reassigned_ph = False
                        # A) Prélever un interne actuellement sur une vacation non obligatoire sur la même demi-journée
                        for donor_p in non_mandatory_priority:
                            if donor_p in ph_set:
                                continue
                            candidate_iids = list(senior_interne_ids) + (["noe"] if ph_poste != "TDM SAU" else [])
                            for cand_iid in candidate_iids:
                                if by_int[cand_iid][h] == donor_p:
                                    by_int[cand_iid][h] = ph_poste
                                    by_int[cand_iid][nk] = f"Vacation obligatoire ({ph_poste})"
                                    if not by_int[cand_iid].get("note"):
                                        by_int[cand_iid]["note"] = by_int[cand_iid][nk]
                                    reassigned_ph = True
                                    break
                            if reassigned_ph:
                                break

                        # B) S'il y a >= 2 seniors au TDM SAU (ou Noé au TDM SAU avec un senior hors mardi matin solo), l'un d'eux prend la vacation obligatoire
                        if not reassigned_ph and ph_poste != "TDM SAU":
                            sau_seniors = [s_id for s_id in senior_interne_ids if by_int[s_id][h] == "TDM SAU"]
                            if len(sau_seniors) >= 2:
                                donor_sid = sau_seniors[-1]
                                by_int[donor_sid][h] = ph_poste
                                by_int[donor_sid][nk] = f"Vacation obligatoire ({ph_poste})"
                                reassigned_ph = True
                            elif len(sau_seniors) >= 1 and by_int["noe"][h] == "TDM SAU" and not (wd_cur == 1 and h == "am"):
                                if ph_poste in ("ECHO", "IRM 3T", "IRM 1,5T", "IRM", "TDM OLLIER DIAG"):
                                    by_int["noe"][h] = ph_poste
                                    by_int["noe"][nk] = f"Vacation obligatoire ({ph_poste})"
                                    reassigned_ph = True
                                else:
                                    # Échanger avec un senior sur ECHO / IRM pour que le senior prenne GESTES (C) / SCAN ACHARD / LECTURE/CS
                                    for swap_sid in senior_interne_ids:
                                        if by_int[swap_sid][h] in ("ECHO", "IRM", "IRM 3T"):
                                            noe_new_p = by_int[swap_sid][h]
                                            by_int[swap_sid][h] = ph_poste
                                            by_int[swap_sid][nk] = f"Vacation obligatoire ({ph_poste})"
                                            by_int["noe"][h] = noe_new_p
                                            by_int["noe"][nk] = f"Vacation obligatoire ({noe_new_p})"
                                            reassigned_ph = True
                                            break

                        # C) Si aucun poste non obligatoire n'est disponible sur cette demi-journée, solliciter un interne en demi-off
                        #    en sollicitant en priorité un interne qui a déjà >1 off sur cette période (AM/PM) ou un double off le même jour
                        if not reassigned_ph:
                            other_h_ph = "pm" if h == "am" else "am"
                            base_off_cands = ["noe"] + senior_interne_ids if ph_poste != "TDM SAU" else list(senior_interne_ids)
                            off_candidates = sorted(
                                [cid for cid in base_off_cands if by_int[cid][h] == "1/2 journée libre"],
                                key=lambda cid: (
                                    1 if is_protected_fixed_off(cid, d_iso, h) else 0,
                                    0 if by_int[cid][other_h_ph] == "1/2 journée libre" else 1,
                                    -(count_week_half_offs(cid, h) - count_week_half_offs(cid, other_h_ph)),
                                    -(
                                        (total_am_offs_counts[cid] - total_pm_offs_counts[cid])
                                        if h == "am"
                                        else (total_pm_offs_counts[cid] - total_am_offs_counts[cid])
                                    ),
                                ),
                            )
                            for cand_iid in off_candidates:
                                by_int[cand_iid][h] = ph_poste
                                by_int[cand_iid][nk] = f"Vacation obligatoire ({ph_poste})"
                                if not by_int[cand_iid].get("note"):
                                    by_int[cand_iid]["note"] = by_int[cand_iid][nk]
                                reassigned_ph = True
                                break

        def assign_active_poste_on_slot(interne_id: str, d_iso: str, h: str) -> bool:
            """Remplace un demi-off en excès sur (d_iso, h) par une vacation active ouverte (ou via binôme Socle)."""
            st = schedule[d_iso]["byInterne"][interne_id]
            other_h = "pm" if h == "am" else "am"
            other_p = st[other_h]
            avail = [p for p in get_available_open_postes(d_iso, h) if p != other_p] or get_available_open_postes(d_iso, h)
            nk = "noteAm" if h == "am" else "notePm"
            if avail:
                st[h] = avail[0]
                st[nk] = f"Phase Socle ({avail[0]})" if interne_id == "noe" else ""
                return True
            if interne_id != "noe":
                noe_st = schedule[d_iso]["byInterne"]["noe"]
                noe_p = noe_st[h]
                other_h_n = "pm" if h == "am" else "am"
                if noe_p not in non_active_codes and noe_p != "TDM SAU" and noe_p != other_p:
                    # Noé bascule au TDM SAU (si < 3) ou en binôme sur ECHO / SCAN ACHARD / TDM OLLIER DIAG
                    noe_sau_w = sum(
                        1
                        for d_chk in active_isos
                        for h_chk in ("am", "pm")
                        if schedule[d_chk]["byInterne"]["noe"][h_chk] == "TDM SAU"
                    )
                    if noe_sau_w < 3 and noe_st[other_h_n] != "TDM SAU":
                        st[h] = noe_p
                        st[nk] = ""
                        noe_st[h] = "TDM SAU"
                        noe_st[nk] = "Posté Socle Urgences"
                        return True
                    ch_day = (chefs_planning or {}).get(d_iso, {})
                    wd_cur = datetime.date.fromisoformat(d_iso).weekday()
                    open_set = get_open_interne_postes_for_halfday(ch_day, h, wd_cur)
                    closed_codes = {c["poste"] for c in (schedule[d_iso]["closedAm"] if h == "am" else schedule[d_iso]["closedPm"])}
                    for bin_p in ("TDM OLLIER DIAG", "SCAN ACHARD", "ECHO"):
                        if bin_p in open_set and bin_p not in closed_codes and bin_p != noe_p and bin_p != noe_st[other_h_n]:
                            st[h] = noe_p
                            st[nk] = ""
                            noe_st[h] = bin_p
                            noe_st[nk] = f"Phase Socle ({bin_p})"
                            return True
            return False

        def reduce_excess_offs_for_week():
            while True:
                off_counts = {
                    iid: count_week_half_offs(iid, "am") + count_week_half_offs(iid, "pm")
                    for iid in all_interne_ids
                }
                over_iids = [iid for iid, cnt in off_counts.items() if cnt > min(2, target_offs_for_week[iid])]
                if not over_iids:
                    break
                fixed = False
                for iid in over_iids:
                    w_am = count_week_half_offs(iid, "am")
                    w_pm = count_week_half_offs(iid, "pm")
                    off_slots = [
                        (d_iso, h)
                        for d_iso in active_isos
                        if d_iso != "2026-11-02"
                        for h in ("am", "pm")
                        if schedule[d_iso]["byInterne"][iid][h] == "1/2 journée libre"
                    ]
                    # Retirer en priorité :
                    # 1. Un demi-off non protégé
                    # 2. Un demi-off situé un jour où l'interne a déjà l'autre demi-journée en off (même jour AM+PM)
                    # 3. Un demi-off de la période (AM ou PM) qui est en excès sur la semaine (ou sur le cumul du semestre)
                    off_slots.sort(
                        key=lambda s: (
                            1 if is_protected_fixed_off(iid, s[0], s[1]) else 0,
                            0 if schedule[s[0]]["byInterne"][iid]["pm" if s[1] == "am" else "am"] == "1/2 journée libre" else 1,
                            0 if (s[1] == "am" and w_am > w_pm) or (s[1] == "pm" and w_pm > w_am) else (
                                0 if w_am == w_pm and (
                                    (s[1] == "am" and total_am_offs_counts[iid] >= total_pm_offs_counts[iid])
                                    or (s[1] == "pm" and total_pm_offs_counts[iid] > total_am_offs_counts[iid])
                                ) else 1
                            ),
                        )
                    )
                    for allow_protected in (False, True):
                        for d_iso, h in off_slots:
                            if not allow_protected and is_protected_fixed_off(iid, d_iso, h):
                                continue
                            if assign_active_poste_on_slot(iid, d_iso, h):
                                fixed = True
                                break
                        if fixed:
                            break
                    if fixed:
                        break
                if not fixed:
                    break

        # 5B. Ajuster les demi-offs de la semaine selon target_offs_for_week (max 2 demi-offs / semaine par interne)
        #     1) Réduction si un interne dépasse sa cible hebdomadaire (jamais > 2 demi-offs)
        reduce_excess_offs_for_week()

        #     2) Attribution des demi-offs manquants (jusqu'à 2 maximum par semaine)
        #        en privilégiant systématiquement l'alternance Matin / Après-midi (1 AM + 1 PM par semaine)
        #        et en évitant 2 demi-offs le même jour.
        for iid in all_interne_ids:
            if vac_halfdays_by_interne[iid] >= 6:
                continue
            target_cnt = min(2, target_offs_for_week[iid])
            off_cnt = count_week_half_offs(iid, "am") + count_week_half_offs(iid, "pm")

            while off_cnt < target_cnt:
                freed = False
                w_am = count_week_half_offs(iid, "am")
                w_pm = count_week_half_offs(iid, "pm")
                if w_am < w_pm:
                    preferred_h = "am"
                elif w_pm < w_am:
                    preferred_h = "pm"
                else:
                    if total_am_offs_counts[iid] + w_am < total_pm_offs_counts[iid] + w_pm:
                        preferred_h = "am"
                    elif total_pm_offs_counts[iid] + w_pm < total_am_offs_counts[iid] + w_am:
                        preferred_h = "pm"
                    else:
                        preferred_h = "am" if iid in FIXED_OFF_HALFDAYS_FROM_W2 else "pm"

                raw_slots: list[tuple[str, str]] = []
                for d_iso in reversed(active_isos):
                    if d_iso == "2026-11-02":
                        continue
                    wd_cand = datetime.date.fromisoformat(d_iso).weekday()
                    for h in ("pm", "am"):
                        if h == "pm" and wd_cand in (1, 4):
                            continue
                        if iid == "noe" and wd_cand == 1 and h == "am":
                            continue
                        if schedule[d_iso]["byInterne"][iid][h] in non_active_codes:
                            continue
                        raw_slots.append((d_iso, h))

                # Trier les créneaux candidats pour :
                # 1. Éviter de poser 2 demi-offs le même jour (AM + PM sur le même jour)
                # 2. Privilégier la demi-journée (AM ou PM) manquante pour avoir 1 AM + 1 PM
                # 3. Pour Noé, éviter d'écraser ses créneaux TDM SAU de la semaine tant qu'un autre poste est libérable
                # 4. Privilégier la demi-journée fixe demandée si c'est le matin
                slot_candidates = sorted(
                    raw_slots,
                    key=lambda s: (
                        1 if schedule[s[0]]["byInterne"][iid]["pm" if s[1] == "am" else "am"] == "1/2 journée libre" else 0,
                        0 if s[1] == preferred_h else 1,
                        1 if (iid == "noe" and schedule[s[0]]["byInterne"]["noe"][s[1]] == "TDM SAU") else 0,
                        0 if is_protected_fixed_off(iid, s[0], s[1]) else 1,
                    ),
                )

                # Pour chaque créneau candidat (dans l'ordre de priorité : hors Mar/Ven PM, jour différent,
                # demi-journée AM/PM manquante, demi-journée fixe), tenter :
                # - Passe 1 : libérer directement une vacation non obligatoire occupée par l'interne
                # - Passe 2 : échanger sur la même demi-journée avec un co-interne qui occupe une vacation non obligatoire
                # - Passe 3 : relais avec un co-interne en demi-off sur (d_iso, h) qui occupe un poste non obligatoire un autre jour de la semaine
                cand_list = list(non_mandatory_priority) + (["TDM SAU"] if iid == "noe" else [])
                for d_iso, h in slot_candidates:
                    wd_cur = datetime.date.fromisoformat(d_iso).weekday()
                    ch_day = (chefs_planning or {}).get(d_iso, {})
                    ph_set = get_ph_interne_postes_for_halfday(ch_day, h, wd_cur, d_iso)
                    by_int = schedule[d_iso]["byInterne"]
                    st = by_int[iid]
                    my_p = st[h]
                    if my_p in non_active_codes:
                        continue

                    # Passe 1 : libération directe si le poste de l'interne est non obligatoire
                    for cand_poste in cand_list:
                        if iid == "noe" and cand_poste == "TDM SAU" and wd_cur == 1 and h == "am":
                            continue
                        if cand_poste in ph_set and not (iid == "noe" and cand_poste == "TDM SAU"):
                            continue
                        if my_p == cand_poste:
                            nk = "noteAm" if h == "am" else "notePm"
                            st[h] = "1/2 journée libre"
                            if is_protected_fixed_off(iid, d_iso, h):
                                st[nk] = "Demi-journée off fixe hebdomadaire"
                            else:
                                st[nk] = "Demi-off hebdomadaire (hors vacations obligatoires)"
                            if not st.get("note"):
                                st["note"] = st[nk]
                            off_cnt += 1
                            freed = True
                            break
                    if freed:
                        break

                    # Passe 2 : échange sur la même demi-journée avec un co-interne occupant un poste non obligatoire
                    swap_partners = (
                        list(senior_interne_ids) + (["noe"] if my_p != "TDM SAU" else [])
                        if iid in senior_interne_ids
                        else [s_id for s_id in senior_interne_ids if my_p != "TDM SAU"]
                    )
                    for cand_non_mand in non_mandatory_priority:
                        if cand_non_mand in ph_set:
                            continue
                        for other_id in swap_partners:
                            if other_id == iid:
                                continue
                            if by_int[other_id][h] == cand_non_mand:
                                nk = "noteAm" if h == "am" else "notePm"
                                by_int[other_id][h] = my_p
                                st[h] = "1/2 journée libre"
                                if is_protected_fixed_off(iid, d_iso, h):
                                    st[nk] = "Demi-journée off fixe hebdomadaire"
                                else:
                                    st[nk] = "Demi-off hebdomadaire (équilibré)"
                                if not st.get("note"):
                                    st["note"] = st[nk]
                                off_cnt += 1
                                freed = True
                                break
                        if freed:
                            break
                    if freed:
                        break

                    # Passe 3 : relais avec un co-interne en demi-off sur (d_iso, h) qui occupe une vacation non obligatoire
                    #           sur un autre créneau (d_alt, h_alt) de la même semaine
                    for other_id in swap_partners:
                        if other_id == iid:
                            continue
                        if is_protected_fixed_off(other_id, d_iso, h):
                            continue
                        if by_int[other_id][h] != "1/2 journée libre":
                            continue
                        other_h_cur = "pm" if h == "am" else "am"
                        if by_int[other_id][other_h_cur] == my_p:
                            continue
                        for d_alt in active_isos:
                            if d_alt in ("2026-11-02", d_iso):
                                continue
                            wd_alt = datetime.date.fromisoformat(d_alt).weekday()
                            ch_alt = (chefs_planning or {}).get(d_alt, {})
                            for h_alt in ("am", "pm"):
                                if h_alt == "pm" and wd_alt in (1, 4):
                                    continue
                                if other_id == "noe" and wd_alt == 1 and h_alt == "am":
                                    continue
                                other_h_alt = "pm" if h_alt == "am" else "am"
                                if schedule[d_alt]["byInterne"][other_id][other_h_alt] == "1/2 journée libre":
                                    continue
                                p_alt = schedule[d_alt]["byInterne"][other_id][h_alt]
                                if p_alt in non_active_codes or p_alt == "TDM SAU":
                                    continue
                                ph_alt = get_ph_interne_postes_for_halfday(ch_alt, h_alt, wd_alt, d_alt)
                                if p_alt in ph_alt:
                                    continue
                                nk = "noteAm" if h == "am" else "notePm"
                                nk_alt = "noteAm" if h_alt == "am" else "notePm"
                                schedule[d_alt]["byInterne"][other_id][h_alt] = "1/2 journée libre"
                                schedule[d_alt]["byInterne"][other_id][nk_alt] = "Demi-off hebdomadaire (équilibré)"
                                by_int[other_id][h] = my_p
                                by_int[other_id][nk] = ""
                                st[h] = "1/2 journée libre"
                                st[nk] = (
                                    "Demi-journée off fixe hebdomadaire"
                                    if is_protected_fixed_off(iid, d_iso, h)
                                    else "Demi-off hebdomadaire (équilibré)"
                                )
                                if not st.get("note"):
                                    st["note"] = st[nk]
                                off_cnt += 1
                                freed = True
                                break
                            if freed:
                                break
                        if freed:
                            break
                    if freed:
                        break
                if not freed:
                    break

        #     3) Second passage de réduction si des postes se sont libérés en 5B-2 pour un interne ayant > target_offs_for_week
        reduce_excess_offs_for_week()

        #     4) Rééquilibrage hebdomadaire Matin / Après-midi (1 AM + 1 PM par semaine et éviter AM+PM le même jour) :
        #        Si un interne a 2 demi-offs le matin (2 AM, 0 PM) ou 2 l'après-midi (0 AM, 2 PM) ou AM+PM le même jour,
        #        basculer l'un des demi-offs vers l'autre demi-journée (ou un autre jour) en préservant les vacations obligatoires.
        for _ in range(20):
            rebalanced_off = False
            for iid in all_interne_ids:
                w_am = count_week_half_offs(iid, "am")
                w_pm = count_week_half_offs(iid, "pm")
                if w_am + w_pm < 2:
                    continue

                # Cas A : L'interne a 2 demi-offs sur la MÊME journée (am == off et pm == off le même jour)
                same_day_isos = [
                    d_iso for d_iso in active_isos
                    if d_iso != "2026-11-02"
                    and schedule[d_iso]["byInterne"][iid]["am"] == "1/2 journée libre"
                    and schedule[d_iso]["byInterne"][iid]["pm"] == "1/2 journée libre"
                ]
                for d_same in same_day_isos:
                    # Déplacer l'une des deux demi-journées (en gardant 1 AM + 1 PM si w_am == w_pm)
                    move_halves = ["am", "pm"] if w_am >= w_pm else ["pm", "am"]
                    for h_move in move_halves:
                        if is_protected_fixed_off(iid, d_same, h_move):
                            continue
                        target_h = h_move if (w_am == w_pm) else ("pm" if w_am > w_pm else "am")
                        dest_candidates = sorted(
                            [d for d in active_isos if d not in ("2026-11-02", d_same)],
                            key=lambda d: 1 if (iid == "noe" and schedule[d]["byInterne"]["noe"][target_h] == "TDM SAU") else 0,
                        )
                        for d_dest in dest_candidates:
                            wd_dest = datetime.date.fromisoformat(d_dest).weekday()
                            if target_h == "pm" and wd_dest in (1, 4):
                                continue
                            if iid == "noe" and wd_dest == 1 and target_h == "am":
                                continue
                            other_dest_h = "am" if target_h == "pm" else "pm"
                            if schedule[d_dest]["byInterne"][iid][other_dest_h] == "1/2 journée libre":
                                continue
                            dest_p = schedule[d_dest]["byInterne"][iid][target_h]
                            if dest_p in non_active_codes:
                                continue
                            ch_dest = (chefs_planning or {}).get(d_dest, {})
                            ph_dest = get_ph_interne_postes_for_halfday(ch_dest, target_h, wd_dest, d_dest)
                            can_free_dest = (dest_p != "TDM SAU" and dest_p not in ph_dest) or (
                                iid == "noe" and dest_p == "TDM SAU" and not (wd_dest == 1 and target_h == "am")
                            )
                            swap_partner_dest = None
                            if not can_free_dest and iid in senior_interne_ids:
                                for o_id in senior_interne_ids:
                                    if o_id == iid:
                                        continue
                                    o_p = schedule[d_dest]["byInterne"][o_id][target_h]
                                    if o_p not in non_active_codes and o_p != "TDM SAU" and o_p not in ph_dest:
                                        swap_partner_dest = o_id
                                        break
                            if (can_free_dest or swap_partner_dest) and assign_active_poste_on_slot(iid, d_same, h_move):
                                nk_dest = "noteAm" if target_h == "am" else "notePm"
                                if swap_partner_dest:
                                    schedule[d_dest]["byInterne"][swap_partner_dest][target_h] = dest_p
                                schedule[d_dest]["byInterne"][iid][target_h] = "1/2 journée libre"
                                schedule[d_dest]["byInterne"][iid][nk_dest] = "Demi-off hebdomadaire (équilibré)"
                                rebalanced_off = True
                                break
                            # Sinon, si h_move == target_h, échanger le demi-off entre d_same et d_dest avec un co-interne
                            if not rebalanced_off and h_move == target_h and iid in senior_interne_ids:
                                for o_id in senior_interne_ids:
                                    if o_id == iid:
                                        continue
                                    if is_protected_fixed_off(o_id, d_dest, target_h):
                                        continue
                                    if schedule[d_dest]["byInterne"][o_id][target_h] != "1/2 journée libre":
                                        continue
                                    if schedule[d_same]["byInterne"][o_id][other_dest_h] == "1/2 journée libre":
                                        continue
                                    o_same_p = schedule[d_same]["byInterne"][o_id][h_move]
                                    if o_same_p in non_active_codes:
                                        continue
                                    nk_t = "noteAm" if target_h == "am" else "notePm"
                                    schedule[d_same]["byInterne"][iid][h_move] = o_same_p
                                    schedule[d_same]["byInterne"][iid][nk_t] = ""
                                    schedule[d_same]["byInterne"][o_id][h_move] = "1/2 journée libre"
                                    schedule[d_same]["byInterne"][o_id][nk_t] = "Demi-off hebdomadaire (équilibré)"
                                    schedule[d_dest]["byInterne"][o_id][target_h] = dest_p
                                    schedule[d_dest]["byInterne"][o_id][nk_t] = ""
                                    schedule[d_dest]["byInterne"][iid][target_h] = "1/2 journée libre"
                                    schedule[d_dest]["byInterne"][iid][nk_t] = "Demi-off hebdomadaire (équilibré)"
                                    rebalanced_off = True
                                    break
                        if rebalanced_off:
                            break
                    if rebalanced_off:
                        break
                if rebalanced_off:
                    break

                # Cas B : L'interne a un déséquilibre Matin / Après-midi (ex: 2 AM + 0 PM ou 0 AM + 2 PM, ou 3 offs mal répartis)
                need_am_to_pm = (w_am - w_pm >= 2) or (w_am - w_pm == 1 and total_am_offs_counts[iid] > total_pm_offs_counts[iid])
                need_pm_to_am = (w_pm - w_am >= 2) or (w_pm - w_am == 1 and total_pm_offs_counts[iid] > total_am_offs_counts[iid])
                if not (need_am_to_pm or need_pm_to_am):
                    continue
                from_h = "am" if need_am_to_pm else "pm"
                to_h = "pm" if need_am_to_pm else "am"
                other_to_h = from_h

                from_days = [
                    d_iso for d_iso in active_isos
                    if d_iso != "2026-11-02"
                    and schedule[d_iso]["byInterne"][iid][from_h] == "1/2 journée libre"
                ]
                from_days.sort(key=lambda d: 1 if is_protected_fixed_off(iid, d, from_h) else 0)

                to_days = [
                    d_iso for d_iso in active_isos
                    if d_iso != "2026-11-02"
                    and schedule[d_iso]["byInterne"][iid][to_h] not in non_active_codes
                    and not (to_h == "pm" and datetime.date.fromisoformat(d_iso).weekday() in (1, 4))
                    and not (iid == "noe" and to_h == "am" and datetime.date.fromisoformat(d_iso).weekday() == 1)
                ]

                for allow_protected_from in (False, True):
                    for d_from in from_days:
                        if not allow_protected_from and is_protected_fixed_off(iid, d_from, from_h) and len(from_days) > 1:
                            continue
                        to_days_sorted = sorted(
                            to_days,
                            key=lambda d: (
                                1 if (d != d_from and schedule[d]["byInterne"][iid][other_to_h] == "1/2 journée libre") else 0,
                                1 if (iid == "noe" and schedule[d]["byInterne"]["noe"][to_h] == "TDM SAU") else 0,
                                0 if is_protected_fixed_off(iid, d, to_h) else 1,
                            ),
                        )
                        for d_to in to_days_sorted:
                            if d_to != d_from and schedule[d_to]["byInterne"][iid][other_to_h] == "1/2 journée libre":
                                continue
                            wd_to = datetime.date.fromisoformat(d_to).weekday()
                            ch_to = (chefs_planning or {}).get(d_to, {})
                            ph_to = get_ph_interne_postes_for_halfday(ch_to, to_h, wd_to, d_to)
                            cur_to_p = schedule[d_to]["byInterne"][iid][to_h]

                            can_free_to = (cur_to_p != "TDM SAU" and cur_to_p not in ph_to) or (
                                iid == "noe" and cur_to_p == "TDM SAU" and not (wd_to == 1 and to_h == "am")
                            )
                            swap_partner_to = None
                            if not can_free_to and iid in senior_interne_ids:
                                for o_id in senior_interne_ids:
                                    if o_id == iid:
                                        continue
                                    o_p = schedule[d_to]["byInterne"][o_id][to_h]
                                    if o_p not in non_active_codes and o_p != "TDM SAU" and o_p not in ph_to:
                                        swap_partner_to = o_id
                                        break

                            if can_free_to or swap_partner_to:
                                if assign_active_poste_on_slot(iid, d_from, from_h):
                                    nk_to = "noteAm" if to_h == "am" else "notePm"
                                    if swap_partner_to:
                                        schedule[d_to]["byInterne"][swap_partner_to][to_h] = cur_to_p
                                    schedule[d_to]["byInterne"][iid][to_h] = "1/2 journée libre"
                                    schedule[d_to]["byInterne"][iid][nk_to] = (
                                        "Demi-journée off fixe hebdomadaire"
                                        if is_protected_fixed_off(iid, d_to, to_h)
                                        else "Demi-off hebdomadaire (équilibré Matin/PM)"
                                    )
                                    if not schedule[d_to]["byInterne"][iid].get("note"):
                                        schedule[d_to]["byInterne"][iid]["note"] = schedule[d_to]["byInterne"][iid][nk_to]
                                    rebalanced_off = True
                                    break

                            # Sinon, relais en 2 étapes : un co-interne o_id en demi-off sur (d_to, to_h) décale son demi-off
                            # to_h vers un autre jour d_alt où o_id occupe un poste non obligatoire (ou échangeable),
                            # reprend cur_to_p sur (d_to, to_h), et libère (d_to, to_h) pour iid !
                            if not rebalanced_off and iid in senior_interne_ids:
                                for o_id in senior_interne_ids:
                                    if o_id == iid:
                                        continue
                                    if is_protected_fixed_off(o_id, d_to, to_h):
                                        continue
                                    if schedule[d_to]["byInterne"][o_id][to_h] != "1/2 journée libre":
                                        continue
                                    for d_alt in active_isos:
                                        if d_alt in ("2026-11-02", d_to):
                                            continue
                                        wd_alt = datetime.date.fromisoformat(d_alt).weekday()
                                        if to_h == "pm" and wd_alt in (1, 4):
                                            continue
                                        if schedule[d_alt]["byInterne"][o_id][other_to_h] == "1/2 journée libre":
                                            continue
                                        o_alt_p = schedule[d_alt]["byInterne"][o_id][to_h]
                                        if o_alt_p in non_active_codes:
                                            continue
                                        ch_alt = (chefs_planning or {}).get(d_alt, {})
                                        ph_alt = get_ph_interne_postes_for_halfday(ch_alt, to_h, wd_alt, d_alt)
                                        can_free_alt = o_alt_p != "TDM SAU" and o_alt_p not in ph_alt
                                        swap_partner_alt = None
                                        if not can_free_alt:
                                            for p3_id in senior_interne_ids:
                                                if p3_id in (iid, o_id):
                                                    continue
                                                p3_p = schedule[d_alt]["byInterne"][p3_id][to_h]
                                                if p3_p not in non_active_codes and p3_p != "TDM SAU" and p3_p not in ph_alt:
                                                    swap_partner_alt = p3_id
                                                    break
                                        if not (can_free_alt or swap_partner_alt):
                                            continue
                                        if assign_active_poste_on_slot(iid, d_from, from_h):
                                            nk_to = "noteAm" if to_h == "am" else "notePm"
                                            if swap_partner_alt:
                                                schedule[d_alt]["byInterne"][swap_partner_alt][to_h] = o_alt_p
                                            schedule[d_alt]["byInterne"][o_id][to_h] = "1/2 journée libre"
                                            schedule[d_alt]["byInterne"][o_id][nk_to] = "Demi-off hebdomadaire (équilibré Matin/PM)"
                                            schedule[d_to]["byInterne"][o_id][to_h] = cur_to_p
                                            schedule[d_to]["byInterne"][o_id][nk_to] = ""
                                            schedule[d_to]["byInterne"][iid][to_h] = "1/2 journée libre"
                                            schedule[d_to]["byInterne"][iid][nk_to] = "Demi-off hebdomadaire (équilibré Matin/PM)"
                                            rebalanced_off = True
                                            break
                                    if rebalanced_off:
                                        break

                            # Sinon, échange croisé avec un co-interne qui est en off sur (d_to, to_h) et actif sur (d_from, from_h)
                            if not rebalanced_off and iid in senior_interne_ids:
                                for o_id in senior_interne_ids:
                                    if o_id == iid:
                                        continue
                                    if is_protected_fixed_off(o_id, d_to, to_h):
                                        continue
                                    if schedule[d_to]["byInterne"][o_id][to_h] != "1/2 journée libre":
                                        continue
                                    if from_h == "pm" and datetime.date.fromisoformat(d_from).weekday() in (1, 4):
                                        continue
                                    o_from_p = schedule[d_from]["byInterne"][o_id][from_h]
                                    if o_from_p in non_active_codes:
                                        continue
                                    o_w_from = count_week_half_offs(o_id, from_h)
                                    o_w_to = count_week_half_offs(o_id, to_h)
                                    if o_w_to <= o_w_from:
                                        continue
                                    nk_from = "noteAm" if from_h == "am" else "notePm"
                                    nk_to = "noteAm" if to_h == "am" else "notePm"
                                    schedule[d_from]["byInterne"][iid][from_h] = o_from_p
                                    schedule[d_from]["byInterne"][iid][nk_from] = ""
                                    schedule[d_from]["byInterne"][o_id][from_h] = "1/2 journée libre"
                                    schedule[d_from]["byInterne"][o_id][nk_from] = "Demi-off hebdomadaire (équilibré Matin/PM)"

                                    schedule[d_to]["byInterne"][o_id][to_h] = cur_to_p
                                    schedule[d_to]["byInterne"][o_id][nk_to] = ""
                                    schedule[d_to]["byInterne"][iid][to_h] = "1/2 journée libre"
                                    schedule[d_to]["byInterne"][iid][nk_to] = "Demi-off hebdomadaire (équilibré Matin/PM)"
                                    rebalanced_off = True
                                    break
                            if rebalanced_off:
                                break
                        if rebalanced_off:
                            break
                    if rebalanced_off:
                        break
                if rebalanced_off:
                    break
            if not rebalanced_off:
                break

        # Mise à jour du compteur de report (carry-over) et du cumul AM/PM pour la semaine suivante :
        for iid in all_interne_ids:
            w_am_final = count_week_half_offs(iid, "am")
            w_pm_final = count_week_half_offs(iid, "pm")
            total_am_offs_counts[iid] += w_am_final
            total_pm_offs_counts[iid] += w_pm_final
            if vac_halfdays_by_interne[iid] >= 6:
                continue
            final_off_cnt = w_am_final + w_pm_final
            new_debt = carry_over_offs[iid] + (2 - final_off_cnt)
            carry_over_offs[iid] = max(0, new_debt)

        # 5B-bis. QUOTAS HEBDOMADAIRES & RÈGLES DE VARIÉTÉ DES POSTES :
        #   1. TDM SAU : 2 SAU/semaine pour chacun des 5 internes seniors, 3 SAU/semaine pour Noé (Phase Socle)
        #   2. IRM d'après-midi ("IRM" en PM) séparée des IRM du matin : max 1 IRM d'après-midi par semaine par interne (sauf exception)
        #   3. Variété sur la journée : un interne ne peut JAMAIS faire le même poste toute la journée (am != pm)
        def count_week_sau(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] == "TDM SAU"
            )

        def count_week_irm_pm(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                if schedule[d_chk]["byInterne"][interne_id]["pm"] == "IRM"
            )

        def is_same_poste_am_pm(p_am: str, p_pm: str, avoid_irm_both: bool = True) -> bool:
            if p_am in non_active_codes or p_pm in non_active_codes:
                return False
            if p_am == p_pm:
                return True
            if avoid_irm_both and ("IRM" in p_am and "IRM" in p_pm):
                return True
            return False

        def count_week_sau_half(interne_id: str, half_k: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                if schedule[d_chk]["byInterne"][interne_id][half_k] == "TDM SAU"
            )

        # A) Éviter les doublons de seniors au TDM SAU sur la même demi-journée
        #    (et retirer tout senior du TDM SAU le mardi matin où Noé est en solo avec Dr Macil Hamadouche)
        for d_iso in active_isos:
            wd_cur = datetime.date.fromisoformat(d_iso).weekday()
            for h in ("am", "pm"):
                if d_iso == "2026-11-02" and h == "am":
                    continue
                by_int = schedule[d_iso]["byInterne"]
                sau_sids = [s_id for s_id in senior_interne_ids if by_int[s_id][h] == "TDM SAU"]
                min_sau_sids = 0 if (wd_cur == 1 and h == "am" and by_int["noe"]["am"] == "TDM SAU") else 1
                while len(sau_sids) > min_sau_sids:
                    avail = get_available_open_postes(d_iso, h)
                    if not avail:
                        break
                    other_h_a = "pm" if h == "am" else "am"
                    sau_sids.sort(
                        key=lambda x: (
                            count_week_sau(x),
                            count_week_sau_half(x, h) - count_week_sau_half(x, other_h_a),
                            (total_sau_am_counts[x] - total_sau_pm_counts[x])
                            if h == "am"
                            else (total_sau_pm_counts[x] - total_sau_am_counts[x]),
                        ),
                        reverse=True,
                    )
                    move_sid = sau_sids[0]
                    other_h = "pm" if h == "am" else "am"
                    other_p = by_int[move_sid][other_h]
                    # Choisir un poste ouvert qui ne crée pas de doublon matin/après-midi ni >1 IRM PM/semaine
                    valid_avail = [
                        c for c in avail
                        if not is_same_poste_am_pm(c, other_p)
                        and not (h == "pm" and c == "IRM" and count_week_irm_pm(move_sid) >= 1)
                    ]
                    if not valid_avail:
                        valid_avail = [c for c in avail if c != other_p] or avail
                    nk = "noteAm" if h == "am" else "notePm"
                    by_int[move_sid][h] = valid_avail[0]
                    by_int[move_sid][nk] = ""
                    sau_sids.pop(0)

        # B) Équilibrer les TDM SAU entre les 5 internes seniors : cible = 2 TDM SAU / semaine (max 3 exceptionnellement)
        for _ in range(35):
            sau_counts = {s_id: count_week_sau(s_id) for s_id in senior_interne_ids}
            over_sids = [s_id for s_id, c in sau_counts.items() if c > 2]
            if not over_sids:
                break
            over_sids.sort(
                key=lambda x: (
                    sau_counts[x],
                    total_sau_am_counts[x] + total_sau_pm_counts[x],
                ),
                reverse=True,
            )
            swapped_sau = False

            for over_sid in over_sids:
                under_sids = sorted(
                    [s_id for s_id in senior_interne_ids if sau_counts[s_id] < 2],
                    key=lambda x: (
                        sau_counts[x],
                        total_sau_am_counts[x] + total_sau_pm_counts[x],
                    ),
                )
                if sau_counts[over_sid] > 3:
                    under_sids += sorted(
                        [s_id for s_id in senior_interne_ids if sau_counts[s_id] == 2],
                        key=lambda x: total_sau_am_counts[x] + total_sau_pm_counts[x],
                    )

                # 1. Échange direct sur la même demi-journée (en privilégiant la demi-journée qui équilibre AM/PM)
                for strict_mode in (True, False):
                    for under_sid in under_sids:
                        over_am = count_week_sau_half(over_sid, "am")
                        over_pm = count_week_sau_half(over_sid, "pm")
                        under_am = count_week_sau_half(under_sid, "am")
                        under_pm = count_week_sau_half(under_sid, "pm")
                        over_cum_diff = (total_sau_am_counts[over_sid] + over_am) - (total_sau_pm_counts[over_sid] + over_pm)
                        under_cum_diff = (total_sau_am_counts[under_sid] + under_am) - (total_sau_pm_counts[under_sid] + under_pm)
                        pref_halves = (
                            ("am", "pm")
                            if (over_am - over_pm, over_cum_diff) >= (under_am - under_pm, under_cum_diff)
                            else ("pm", "am")
                        )
                        for h in pref_halves:
                            for d_iso in active_isos:
                                if d_iso == "2026-11-02":
                                    continue
                                other_h = "pm" if h == "am" else "am"
                                by_int = schedule[d_iso]["byInterne"]
                                if by_int[over_sid][h] != "TDM SAU":
                                    continue
                                other_p = by_int[under_sid][h]
                                if other_p in non_active_codes or other_p == "TDM SAU":
                                    continue
                                if is_same_poste_am_pm(other_p, by_int[over_sid][other_h], avoid_irm_both=strict_mode):
                                    continue
                                if is_same_poste_am_pm("TDM SAU", by_int[under_sid][other_h], avoid_irm_both=strict_mode):
                                    continue
                                if strict_mode and h == "pm" and other_p == "IRM" and count_week_irm_pm(over_sid) >= 1:
                                    continue
                                nk = "noteAm" if h == "am" else "notePm"
                                other_note = by_int[under_sid].get(nk, "")
                                by_int[over_sid][h] = other_p
                                by_int[over_sid][nk] = other_note
                                by_int[under_sid][h] = "TDM SAU"
                                by_int[under_sid][nk] = ""
                                swapped_sau = True
                                break
                            if swapped_sau:
                                break
                        if swapped_sau:
                            break
                    if swapped_sau:
                        break
                if swapped_sau:
                    break

                # 2. Échange en 2 étapes via un senior intermédiaire (mid_sid)
                for strict_mode in (True, False):
                    for under_sid in under_sids:
                        for mid_sid in senior_interne_ids:
                            if mid_sid in (over_sid, under_sid):
                                continue
                            step1_slot = None
                            over_am = count_week_sau_half(over_sid, "am")
                            over_pm = count_week_sau_half(over_sid, "pm")
                            over_cum_diff = (total_sau_am_counts[over_sid] + over_am) - (total_sau_pm_counts[over_sid] + over_pm)
                            pref_h1 = ("am", "pm") if (over_am - over_pm, over_cum_diff) >= (0, 0) else ("pm", "am")
                            for h in pref_h1:
                                for d_iso in active_isos:
                                    if d_iso == "2026-11-02":
                                        continue
                                    other_h = "pm" if h == "am" else "am"
                                    by_int = schedule[d_iso]["byInterne"]
                                    p_mid = by_int[mid_sid][h]
                                    if by_int[over_sid][h] == "TDM SAU" and p_mid not in non_active_codes and p_mid != "TDM SAU":
                                        if is_same_poste_am_pm(p_mid, by_int[over_sid][other_h], avoid_irm_both=strict_mode):
                                            continue
                                        if is_same_poste_am_pm("TDM SAU", by_int[mid_sid][other_h], avoid_irm_both=strict_mode):
                                            continue
                                        if strict_mode and h == "pm" and p_mid == "IRM" and count_week_irm_pm(over_sid) >= 1:
                                            continue
                                        step1_slot = (d_iso, h)
                                        break
                                if step1_slot:
                                    break
                            if not step1_slot:
                                continue
                            step2_slot = None
                            under_am = count_week_sau_half(under_sid, "am")
                            under_pm = count_week_sau_half(under_sid, "pm")
                            under_cum_diff = (total_sau_am_counts[under_sid] + under_am) - (total_sau_pm_counts[under_sid] + under_pm)
                            pref_h2 = ("am", "pm") if (under_am - under_pm, under_cum_diff) <= (0, 0) else ("pm", "am")
                            for h in pref_h2:
                                for d_iso in active_isos:
                                    if d_iso == "2026-11-02":
                                        continue
                                    if (d_iso, h) == step1_slot:
                                        continue
                                    other_h = "pm" if h == "am" else "am"
                                    by_int = schedule[d_iso]["byInterne"]
                                    p_und = by_int[under_sid][h]
                                    if by_int[mid_sid][h] == "TDM SAU" and p_und not in non_active_codes and p_und != "TDM SAU":
                                        if is_same_poste_am_pm(p_und, by_int[mid_sid][other_h], avoid_irm_both=strict_mode):
                                            continue
                                        if is_same_poste_am_pm("TDM SAU", by_int[under_sid][other_h], avoid_irm_both=strict_mode):
                                            continue
                                        if strict_mode and h == "pm" and p_und == "IRM" and count_week_irm_pm(mid_sid) >= 1:
                                            continue
                                        step2_slot = (d_iso, h)
                                        break
                                if step2_slot:
                                    break
                            if step1_slot and step2_slot:
                                d1, h1 = step1_slot
                                nk1 = "noteAm" if h1 == "am" else "notePm"
                                by1 = schedule[d1]["byInterne"]
                                p1, n1 = by1[mid_sid][h1], by1[mid_sid].get(nk1, "")
                                by1[over_sid][h1] = p1
                                by1[over_sid][nk1] = n1
                                by1[mid_sid][h1] = "TDM SAU"
                                by1[mid_sid][nk1] = ""

                                d2, h2 = step2_slot
                                nk2 = "noteAm" if h2 == "am" else "notePm"
                                by2 = schedule[d2]["byInterne"]
                                p2, n2 = by2[under_sid][h2], by2[under_sid].get(nk2, "")
                                by2[mid_sid][h2] = p2
                                by2[mid_sid][nk2] = n2
                                by2[under_sid][h2] = "TDM SAU"
                                by2[under_sid][nk2] = ""
                                swapped_sau = True
                                break
                        if swapped_sau:
                            break
                    if swapped_sau:
                        break
                if swapped_sau:
                    break
            if not swapped_sau:
                break

        # C) Quota hebdomadaire de TDM SAU pour Noé (Phase Socle) : cible = 3 TDM SAU / semaine
        #    (dont systématiquement Mardi AM en solo avec Dr Macil Hamadouche, et jamais matin ET après-midi le même jour)
        if w_idx == 0:
            noe_pref_sau_slots = {(1, "am"), (3, "am"), (4, "pm")}
        elif w_idx < 4:
            noe_pref_sau_slots = {(0, "am"), (1, "am"), (3, "am")}
        else:
            rot_noe_w = (w_idx - 4) % 5
            noe_pref_sau_by_rot = {
                0: {(1, "am"), (0, "pm"), (4, "pm")},
                1: {(1, "am"), (2, "pm"), (4, "pm")},
                2: {(1, "am"), (2, "pm"), (3, "pm")},
                3: {(1, "am"), (2, "pm"), (4, "am")},
                4: {(1, "am"), (0, "pm"), (3, "pm")},
            }
            noe_pref_sau_slots = noe_pref_sau_by_rot[rot_noe_w]

        while count_week_sau("noe") > 3 or any(
            schedule[d]["byInterne"]["noe"]["am"] == "TDM SAU" and schedule[d]["byInterne"]["noe"]["pm"] == "TDM SAU"
            for d in active_isos
        ):
            noe_sau_slots = [
                (d_iso, h)
                for d_iso in active_isos
                for h in ("am", "pm")
                if schedule[d_iso]["byInterne"]["noe"][h] == "TDM SAU"
                and not (datetime.date.fromisoformat(d_iso).weekday() == 1 and h == "am")
            ]
            def noe_slot_drop_priority(slot: tuple[str, str]) -> int:
                d_s, h_s = slot
                wd_s = datetime.date.fromisoformat(d_s).weekday()
                other_h_s = "pm" if h_s == "am" else "am"
                if schedule[d_s]["byInterne"]["noe"][other_h_s] == "TDM SAU":
                    return -2 if (wd_s, h_s) not in noe_pref_sau_slots else -1
                if (wd_s, h_s) in noe_pref_sau_slots:
                    return 3
                return 0

            noe_sau_slots.sort(key=noe_slot_drop_priority)
            reduced_noe = False
            for d_iso, h in noe_sau_slots:
                other_h = "pm" if h == "am" else "am"
                other_p_noe = schedule[d_iso]["byInterne"]["noe"][other_h]
                avail = get_available_open_postes(d_iso, h)
                avail_filtered = [
                    p for p in avail
                    if not is_same_poste_am_pm(p, other_p_noe)
                    and not (h == "pm" and p == "IRM" and count_week_irm_pm("noe") >= 1)
                ]
                if not avail_filtered:
                    avail_filtered = [p for p in avail if p != other_p_noe]
                avail_sorted = sorted(
                    avail_filtered,
                    key=lambda p: 0 if p == "TDM OLLIER DIAG" else (1 if p == "SCAN ACHARD" else 2),
                )
                if avail_sorted:
                    nk = "noteAm" if h == "am" else "notePm"
                    new_p = avail_sorted[0]
                    schedule[d_iso]["byInterne"]["noe"][h] = new_p
                    schedule[d_iso]["byInterne"]["noe"][nk] = f"Phase Socle ({new_p})"
                    reduced_noe = True
                    break
                wd_s = datetime.date.fromisoformat(d_iso).weekday()
                if h == "pm" and wd_s in (1, 4):
                    nk = "noteAm" if h == "am" else "notePm"
                    by_int = schedule[d_iso]["byInterne"]
                    swapped_achard = False
                    used_pm_s = {by_int[k_id][h] for k_id in all_interne_ids}
                    target_cs_lec = "CONSULTATION" if ("CONSULTATION" not in used_pm_s and d_iso >= "2027-03-01") else "LECTURE"
                    target_note_s = (
                        ("Consultation Internes (Mardi PM)" if wd_s == 1 else "Consultation Internes (Vendredi PM)")
                        if target_cs_lec == "CONSULTATION"
                        else ("Relecture avec Pr Drapé" if wd_s == 1 else "Lecture (Vendredi PM)")
                    )
                    for s_id in senior_interne_ids:
                        if by_int[s_id][h] == "SCAN ACHARD" and other_p_noe != "SCAN ACHARD" and by_int[s_id]["am"] != target_cs_lec:
                            by_int["noe"][h] = "SCAN ACHARD"
                            by_int["noe"][nk] = "Scanner Achard 1"
                            by_int[s_id][h] = target_cs_lec
                            by_int[s_id][nk] = target_note_s
                            swapped_achard = True
                            break
                    if not swapped_achard and other_p_noe != target_cs_lec:
                        by_int["noe"][h] = target_cs_lec
                        by_int["noe"][nk] = target_note_s
                        swapped_achard = True
                    if swapped_achard:
                        reduced_noe = True
                        break
                # Si les 5 seniors occupent tous les postes ouverts sur cette demi-journée, Noé (Phase Socle)
                # va en binôme sur un poste diagnostique ouvert (SCAN ACHARD, TDM OLLIER DIAG, ECHO) différent de son autre demi-journée
                ch_day_s = (chefs_planning or {}).get(d_iso, {})
                open_set_s = get_open_interne_postes_for_halfday(ch_day_s, h, wd_s)
                closed_s = {c["poste"] for c in (schedule[d_iso]["closedAm"] if h == "am" else schedule[d_iso]["closedPm"])}
                binome_cands = ["SCAN ACHARD", "TDM OLLIER DIAG", "ECHO", "IRM 1,5T", "IRM 3T", "IRM"]
                if h == "am" and wd_s == 2 and d_iso.startswith("2026-11"):
                    binome_cands = [c for c in binome_cands if c != "ECHO"]
                binome_valid = [
                    c for c in binome_cands
                    if c in open_set_s and c not in closed_s
                    and not is_same_poste_am_pm(c, other_p_noe)
                    and not (h == "pm" and c == "IRM" and count_week_irm_pm("noe") >= 1)
                ]
                if not binome_valid:
                    binome_valid = [c for c in binome_cands if c in open_set_s and c not in closed_s and c != other_p_noe]
                if binome_valid:
                    nk = "noteAm" if h == "am" else "notePm"
                    new_p = binome_valid[0]
                    schedule[d_iso]["byInterne"]["noe"][h] = new_p
                    schedule[d_iso]["byInterne"]["noe"][nk] = f"Phase Socle ({new_p})"
                    reduced_noe = True
                    break
            if not reduced_noe:
                break

        noe_active_halfdays = sum(
            1
            for d_iso in active_isos
            for h in ("am", "pm")
            if schedule[d_iso]["byInterne"]["noe"][h] not in non_active_codes
        )
        noe_target_sau = min(3, noe_active_halfdays)
        while count_week_sau("noe") < noe_target_sau:
            added_noe = False
            sau_am_cnt = sum(1 for d_c in active_isos if schedule[d_c]["byInterne"]["noe"]["am"] == "TDM SAU")
            sau_pm_cnt = sum(1 for d_c in active_isos if schedule[d_c]["byInterne"]["noe"]["pm"] == "TDM SAU")
            add_candidates: list[tuple[str, str]] = [
                (d_iso, h)
                for d_iso in active_isos
                if d_iso != "2026-11-02"
                for h in ("am", "pm")
            ]
            add_candidates.sort(
                key=lambda s: (
                    0 if (datetime.date.fromisoformat(s[0]).weekday(), s[1]) in noe_pref_sau_slots else 1,
                    0 if (w_idx >= 4 and ((s[1] == "pm" and sau_pm_cnt < 2) or (s[1] == "am" and sau_am_cnt == 0))) else 1,
                    (datetime.date.fromisoformat(s[0]).weekday() * 2 + (0 if s[1] == "am" else 1) + w_idx * 3) % 10,
                )
            )
            for d_iso, h in add_candidates:
                wd_cur = datetime.date.fromisoformat(d_iso).weekday()
                ch_day = (chefs_planning or {}).get(d_iso, {})
                by_int = schedule[d_iso]["byInterne"]
                other_h = "pm" if h == "am" else "am"
                noe_p = by_int["noe"][h]
                if noe_p in non_active_codes or noe_p == "TDM SAU":
                    continue
                if by_int["noe"][other_h] == "TDM SAU":
                    continue
                if not (wd_cur == 1 and h == "am") and not any(by_int[s_id][h] == "TDM SAU" for s_id in senior_interne_ids):
                    continue
                ph_set = get_ph_interne_postes_for_halfday(ch_day, h, wd_cur, d_iso)
                if noe_p in ph_set:
                    # Si un autre interne couvre déjà noe_p ou si un poste ouvert permet à un senior de reprendre noe_p, autoriser
                    other_covers = any(by_int[s_id][h] == noe_p for s_id in senior_interne_ids)
                    if not other_covers:
                        continue
                nk = "noteAm" if h == "am" else "notePm"
                by_int["noe"][h] = "TDM SAU"
                by_int["noe"][nk] = (
                    "Avec Dr Macil HAMADOUCHE (MH) — Solo SAU (exceptionnellement sans doublure)"
                    if (wd_cur == 1 and h == "am")
                    else "Posté Socle Urgences"
                )
                added_noe = True
                break
            if not added_noe:
                break

        # D) RÈGLE DES IRM D'APRÈS-MIDI ("IRM" en PM) :
        #    - Les IRM d'après-midi sont séparées des IRM du matin (IRM 3T / IRM 1,5T)
        #    - Maximum 1 IRM d'après-midi par semaine par interne (sauf exception en cas d'absences/RG multiples)
        for _ in range(30):
            irm_pm_counts = {iid: count_week_irm_pm(iid) for iid in all_interne_ids}
            over_irm = [iid for iid, c in irm_pm_counts.items() if c > 1]
            if not over_irm:
                break
            over_irm.sort(key=lambda x: (irm_pm_counts[x], total_irm_pm_counts[x]), reverse=True)
            fixed_irm = False

            for over_id in over_irm:
                irm_days = [
                    d_iso for d_iso in active_isos
                    if schedule[d_iso]["byInterne"][over_id]["pm"] == "IRM" and d_iso != "2026-11-02"
                ]
                # Déplacer en priorité un jour où l'interne faisait déjà une IRM le matin
                irm_days.sort(key=lambda d: 0 if "IRM" in schedule[d]["byInterne"][over_id]["am"] else 1)

                for d_iso in irm_days:
                    by_int = schedule[d_iso]["byInterne"]
                    wd_cur = datetime.date.fromisoformat(d_iso).weekday()
                    ch_day = (chefs_planning or {}).get(d_iso, {})
                    ph_pm = get_ph_interne_postes_for_halfday(ch_day, "pm", wd_cur, d_iso)

                    # Cas 1 : si "IRM" n'est pas obligatoire ce jour-là (ex: Vendredi PM), remplacer par un poste ouvert
                    if "IRM" not in ph_pm:
                        avail = [
                            c for c in get_available_open_postes(d_iso, "pm")
                            if c != "IRM" and not is_same_poste_am_pm(by_int[over_id]["am"], c)
                        ]
                        if avail:
                            by_int[over_id]["pm"] = avail[0]
                            by_int[over_id]["notePm"] = ""
                            fixed_irm = True
                            break

                    # Cas 2 : Échange direct le même après-midi avec un interne ayant 0 IRM PM cette semaine
                    zero_irm_cands = sorted(
                        [iid for iid in all_interne_ids if irm_pm_counts[iid] == 0 and iid != over_id],
                        key=lambda x: (0 if x in senior_interne_ids else 1, total_irm_pm_counts[x]),
                    )
                    for strict_irm in (True, False):
                        for cand_id in zero_irm_cands:
                            cand_pm = by_int[cand_id]["pm"]
                            if cand_pm in non_active_codes or cand_pm == "IRM":
                                continue
                            if cand_pm == "TDM SAU":
                                if cand_id == "noe" or over_id == "noe":
                                    continue
                                if count_week_sau(over_id) >= 2:
                                    continue
                            if is_same_poste_am_pm(by_int[over_id]["am"], cand_pm, avoid_irm_both=strict_irm):
                                continue
                            if is_same_poste_am_pm(by_int[cand_id]["am"], "IRM", avoid_irm_both=strict_irm):
                                continue
                            cand_note = by_int[cand_id].get("notePm", "")
                            over_note = by_int[over_id].get("notePm", "")
                            by_int[over_id]["pm"] = cand_pm
                            by_int[over_id]["notePm"] = cand_note
                            by_int[cand_id]["pm"] = "IRM"
                            by_int[cand_id]["notePm"] = over_note
                            fixed_irm = True
                            break
                        if fixed_irm:
                            break
                    if fixed_irm:
                        break
                if fixed_irm:
                    break
            if not fixed_irm:
                break

        # E) RÈGLE STRICTE : UN INTERNE NE PEUT PAS FAIRE LE MÊME POSTE TOUTE LA JOURNÉE (am != pm)
        #    Résolution multi-passes des conflits matin == après-midi (et IRM matin + IRM après-midi)
        for pass_num in range(45):
            avoid_irm_both_flag = (pass_num < 30)
            resolved_conflict = False
            for d_iso in active_isos:
                by_int = schedule[d_iso]["byInterne"]
                wd_cur = datetime.date.fromisoformat(d_iso).weekday()
                ch_day = (chefs_planning or {}).get(d_iso, {})

                for iid in all_interne_ids:
                    p_am = by_int[iid]["am"]
                    p_pm = by_int[iid]["pm"]
                    if not is_same_poste_am_pm(p_am, p_pm, avoid_irm_both=avoid_irm_both_flag):
                        continue

                    # Tester une réaffectation ou un échange sur PM puis sur AM
                    for h in ("pm", "am"):
                        if d_iso == "2026-11-02" and h == "am":
                            continue
                        if iid == "noe" and wd_cur == 1 and h == "am":
                            continue
                        other_h = "am" if h == "pm" else "pm"
                        cur_p = by_int[iid][h]
                        other_p = by_int[iid][other_h]
                        nk = "noteAm" if h == "am" else "notePm"
                        ph_req = get_ph_interne_postes_for_halfday(ch_day, h, wd_cur, d_iso)

                        # 1. Si le poste actuel n'est pas obligatoire (ou est doublonné), prendre un poste ouvert disponible
                        if cur_p == "TDM SAU":
                            is_duplicated_post = (
                                iid in senior_interne_ids
                                and sum(1 for s_id in senior_interne_ids if by_int[s_id][h] == "TDM SAU") > 1
                            )
                        else:
                            is_duplicated_post = sum(1 for k_id in all_interne_ids if by_int[k_id][h] == cur_p) > 1
                        if (cur_p != "TDM SAU" and cur_p not in ph_req) or is_duplicated_post:
                            avail = [
                                c for c in get_available_open_postes(d_iso, h)
                                if not is_same_poste_am_pm(c, other_p, avoid_irm_both=avoid_irm_both_flag)
                                and not (h == "pm" and c == "IRM" and count_week_irm_pm(iid) >= 1)
                            ]
                            if avail:
                                by_int[iid][h] = avail[0]
                                by_int[iid][nk] = f"Phase Socle ({avail[0]})" if iid == "noe" else ""
                                resolved_conflict = True
                                break

                        # 2. Échange sur la même demi-journée avec un co-interne
                        if d_iso == "2026-11-02" and h == "pm":
                            continue
                        swap_cands = senior_interne_ids if iid in senior_interne_ids else all_interne_ids
                        for other_id in swap_cands:
                            if other_id == iid:
                                continue
                            if other_id == "noe" and wd_cur == 1 and h == "am":
                                continue
                            cand_p = by_int[other_id][h]
                            if cand_p in non_active_codes or cand_p == cur_p:
                                continue
                            # Préserver les quotas de TDM SAU
                            if cur_p == "TDM SAU" or cand_p == "TDM SAU":
                                if "noe" in (iid, other_id):
                                    continue
                                # Si l'un des deux prend TDM SAU en plus, vérifier qu'on peut rééquilibrer avec un 2e échange dans la semaine
                                giver_id = iid if cur_p == "TDM SAU" else other_id
                                taker_id = other_id if cur_p == "TDM SAU" else iid
                                if count_week_sau(taker_id) >= 2:
                                    # Chercher un autre créneau de la semaine où taker_id est au TDM SAU et giver_id sur un autre poste
                                    comp_slot = None
                                    for d2 in active_isos:
                                        if d2 == "2026-11-02":
                                            continue
                                        for h2 in ("am", "pm"):
                                            if (d2, h2) == (d_iso, h):
                                                continue
                                            by2 = schedule[d2]["byInterne"]
                                            if by2[taker_id][h2] == "TDM SAU" and by2[giver_id][h2] not in non_active_codes and by2[giver_id][h2] != "TDM SAU":
                                                other_h2 = "am" if h2 == "pm" else "pm"
                                                p_giv2 = by2[giver_id][h2]
                                                if is_same_poste_am_pm(p_giv2, by2[taker_id][other_h2], avoid_irm_both=avoid_irm_both_flag):
                                                    continue
                                                if is_same_poste_am_pm("TDM SAU", by2[giver_id][other_h2], avoid_irm_both=avoid_irm_both_flag):
                                                    continue
                                                if h2 == "pm" and p_giv2 == "IRM" and count_week_irm_pm(taker_id) >= 1:
                                                    continue
                                                comp_slot = (d2, h2)
                                                break
                                        if comp_slot:
                                            break
                                    if not comp_slot:
                                        continue
                                    # Valider aussi le créneau (d_iso, h) avant d'appliquer le double échange
                                    if is_same_poste_am_pm(cand_p, other_p, avoid_irm_both=avoid_irm_both_flag):
                                        continue
                                    if is_same_poste_am_pm(cur_p, by_int[other_id][other_h], avoid_irm_both=avoid_irm_both_flag):
                                        continue
                                    if h == "pm" and cand_p == "IRM" and count_week_irm_pm(iid) >= 1:
                                        continue
                                    if h == "pm" and cur_p == "IRM" and count_week_irm_pm(other_id) >= 1:
                                        continue
                                    # Appliquer l'échange sur (d_iso, h) + compensation sur comp_slot
                                    n_iid = by_int[iid].get(nk, "")
                                    n_oth = by_int[other_id].get(nk, "")
                                    by_int[iid][h] = cand_p
                                    by_int[iid][nk] = n_oth
                                    by_int[other_id][h] = cur_p
                                    by_int[other_id][nk] = n_iid

                                    d2, h2 = comp_slot
                                    nk2 = "noteAm" if h2 == "am" else "notePm"
                                    by2 = schedule[d2]["byInterne"]
                                    p_g2, n_g2 = by2[giver_id][h2], by2[giver_id].get(nk2, "")
                                    by2[taker_id][h2] = p_g2
                                    by2[taker_id][nk2] = n_g2
                                    by2[giver_id][h2] = "TDM SAU"
                                    by2[giver_id][nk2] = ""
                                    resolved_conflict = True
                                    break

                            if is_same_poste_am_pm(cand_p, other_p, avoid_irm_both=avoid_irm_both_flag):
                                continue
                            if is_same_poste_am_pm(cur_p, by_int[other_id][other_h], avoid_irm_both=avoid_irm_both_flag):
                                continue
                            if h == "pm" and cand_p == "IRM" and cur_p != "IRM" and count_week_irm_pm(iid) >= 1:
                                continue
                            if h == "pm" and cur_p == "IRM" and cand_p != "IRM" and count_week_irm_pm(other_id) >= 1:
                                continue

                            n_iid = by_int[iid].get(nk, "")
                            n_oth = by_int[other_id].get(nk, "")
                            by_int[iid][h] = cand_p
                            by_int[iid][nk] = n_oth
                            by_int[other_id][h] = cur_p
                            by_int[other_id][nk] = n_iid
                            resolved_conflict = True
                            break
                        if resolved_conflict:
                            break

                        # 3. Pour un senior bloqué (hors TDM SAU), tenter un échange avec Noé si Noé est sur un poste diagnostique (hors TDM SAU)
                        if not resolved_conflict and iid in senior_interne_ids and cur_p != "TDM SAU":
                            noe_p = by_int["noe"][h]
                            if noe_p not in non_active_codes and noe_p != "TDM SAU" and noe_p != cur_p:
                                if (
                                    not is_same_poste_am_pm(noe_p, other_p, avoid_irm_both=avoid_irm_both_flag)
                                    and not is_same_poste_am_pm(cur_p, by_int["noe"][other_h], avoid_irm_both=avoid_irm_both_flag)
                                    and not (h == "pm" and noe_p == "IRM" and count_week_irm_pm(iid) >= 1)
                                    and not (h == "pm" and cur_p == "IRM" and count_week_irm_pm("noe") >= 1)
                                ):
                                    by_int[iid][h] = noe_p
                                    by_int[iid][nk] = ""
                                    by_int["noe"][h] = cur_p
                                    by_int["noe"][nk] = f"Phase Socle ({cur_p})"
                                    resolved_conflict = True
                                    break
                    if resolved_conflict:
                        break
                if resolved_conflict:
                    break
            if not resolved_conflict and pass_num >= 30:
                break

        # F) ÉQUILIBRAGE DES VACATIONS TDM SAU MATIN (AM) ET APRÈS-MIDI (PM) DANS LA LIMITE DU POSSIBLE :
        #    1. Sur chaque semaine : privilégier 1 SAU Matin + 1 SAU Après-midi (au lieu de 2 Matins ou 2 Après-midis)
        #    2. Sur le cumul du semestre : équilibrer l'écart (AM - PM) entre tous les internes seniors
        def can_swap_sau_on_slot(d_slot: str, h_slot: str, from_sid: str, to_sid: str, strict_irm: bool = True) -> bool:
            if d_slot == "2026-11-02":
                return False
            by_s = schedule[d_slot]["byInterne"]
            if by_s[from_sid][h_slot] != "TDM SAU":
                return False
            other_p_s = by_s[to_sid][h_slot]
            if other_p_s in non_active_codes or other_p_s == "TDM SAU":
                return False
            other_h_s = "pm" if h_slot == "am" else "am"
            if is_same_poste_am_pm(other_p_s, by_s[from_sid][other_h_s], avoid_irm_both=strict_irm):
                return False
            if is_same_poste_am_pm("TDM SAU", by_s[to_sid][other_h_s], avoid_irm_both=strict_irm):
                return False
            if h_slot == "pm" and other_p_s == "IRM" and count_week_irm_pm(from_sid) >= 1:
                return False
            return True

        def execute_sau_swap(d_slot: str, h_slot: str, from_sid: str, to_sid: str):
            by_s = schedule[d_slot]["byInterne"]
            nk_s = "noteAm" if h_slot == "am" else "notePm"
            p_other = by_s[to_sid][h_slot]
            n_other = by_s[to_sid].get(nk_s, "")
            by_s[from_sid][h_slot] = p_other
            by_s[from_sid][nk_s] = n_other
            by_s[to_sid][h_slot] = "TDM SAU"
            by_s[to_sid][nk_s] = ""

        def try_transfer_sau_half(h_slot: str, from_sid: str, to_sid: str, strict_irm: bool = True) -> bool:
            # 1. Échange direct sur un créneau h_slot de la semaine
            for d_slot in active_isos:
                if can_swap_sau_on_slot(d_slot, h_slot, from_sid, to_sid, strict_irm=strict_irm):
                    execute_sau_swap(d_slot, h_slot, from_sid, to_sid)
                    return True
            # 2. Échange en 2 étapes sur le même type de demi-journée h_slot via un senior intermédiaire mid_sid
            for mid_sid in senior_interne_ids:
                if mid_sid in (from_sid, to_sid):
                    continue
                for d1 in active_isos:
                    if not can_swap_sau_on_slot(d1, h_slot, from_sid, mid_sid, strict_irm=strict_irm):
                        continue
                    for d2 in active_isos:
                        if d2 == d1:
                            continue
                        if can_swap_sau_on_slot(d2, h_slot, mid_sid, to_sid, strict_irm=strict_irm):
                            execute_sau_swap(d1, h_slot, from_sid, mid_sid)
                            execute_sau_swap(d2, h_slot, mid_sid, to_sid)
                            return True
            return False

        def try_same_day_cross_swap(sid_am: str, sid_pm: str, strict_irm: bool = True) -> bool:
            for d_same in active_isos:
                if d_same == "2026-11-02":
                    continue
                by_s = schedule[d_same]["byInterne"]
                if by_s[sid_am]["am"] != "TDM SAU" or by_s[sid_pm]["pm"] != "TDM SAU":
                    continue
                p_am_other = by_s[sid_pm]["am"]
                p_pm_other = by_s[sid_am]["pm"]
                if p_am_other in non_active_codes or p_am_other == "TDM SAU":
                    continue
                if p_pm_other in non_active_codes or p_pm_other == "TDM SAU":
                    continue
                if is_same_poste_am_pm(p_am_other, "TDM SAU", avoid_irm_both=strict_irm):
                    continue
                if is_same_poste_am_pm("TDM SAU", p_pm_other, avoid_irm_both=strict_irm):
                    continue
                if p_pm_other == "IRM" and count_week_irm_pm(sid_pm) >= 1:
                    continue
                n_am_other = by_s[sid_pm].get("noteAm", "")
                n_pm_other = by_s[sid_am].get("notePm", "")
                by_s[sid_am]["am"] = p_am_other
                by_s[sid_am]["noteAm"] = n_am_other
                by_s[sid_pm]["am"] = "TDM SAU"
                by_s[sid_pm]["noteAm"] = ""
                by_s[sid_pm]["pm"] = p_pm_other
                by_s[sid_pm]["notePm"] = n_pm_other
                by_s[sid_am]["pm"] = "TDM SAU"
                by_s[sid_am]["notePm"] = ""
                return True
            return False

        for _ in range(40):
            swapped_am_pm_sau = False
            sorted_seniors_am = sorted(
                senior_interne_ids,
                key=lambda s: (
                    count_week_sau_half(s, "am") - count_week_sau_half(s, "pm"),
                    (total_sau_am_counts[s] + count_week_sau_half(s, "am")) - (total_sau_pm_counts[s] + count_week_sau_half(s, "pm")),
                ),
                reverse=True,
            )
            sorted_seniors_pm = list(reversed(sorted_seniors_am))

            for strict_irm in (True, False):
                for sid_a in sorted_seniors_am:
                    w_am_a = count_week_sau_half(sid_a, "am")
                    w_pm_a = count_week_sau_half(sid_a, "pm")
                    cum_diff_a = (total_sau_am_counts[sid_a] + w_am_a) - (total_sau_pm_counts[sid_a] + w_pm_a)
                    if w_am_a == 0:
                        continue
                    for sid_b in sorted_seniors_pm:
                        if sid_b == sid_a:
                            continue
                        w_am_b = count_week_sau_half(sid_b, "am")
                        w_pm_b = count_week_sau_half(sid_b, "pm")
                        cum_diff_b = (total_sau_am_counts[sid_b] + w_am_b) - (total_sau_pm_counts[sid_b] + w_pm_b)
                        if w_pm_b == 0:
                            continue
                        before_week_imb = abs(w_am_a - w_pm_a) + abs(w_am_b - w_pm_b)
                        after_week_imb = abs((w_am_a - 1) - (w_pm_a + 1)) + abs((w_am_b + 1) - (w_pm_b - 1))
                        before_cum_spread = (cum_diff_a ** 2) + (cum_diff_b ** 2)
                        after_cum_spread = ((cum_diff_a - 2) ** 2) + ((cum_diff_b + 2) ** 2)
                        if not (
                            (after_week_imb < before_week_imb and after_cum_spread <= before_cum_spread + 12)
                            or (after_week_imb == before_week_imb and after_cum_spread < before_cum_spread)
                        ):
                            continue

                        if try_same_day_cross_swap(sid_a, sid_b, strict_irm=strict_irm):
                            swapped_am_pm_sau = True
                            break

                        snap_week = {
                            d_s: {k_s: dict(v_s) for k_s, v_s in schedule[d_s]["byInterne"].items()}
                            for d_s in active_isos
                        }
                        if (
                            try_transfer_sau_half("am", sid_a, sid_b, strict_irm=strict_irm)
                            and try_transfer_sau_half("pm", sid_b, sid_a, strict_irm=strict_irm)
                        ):
                            swapped_am_pm_sau = True
                            break
                        else:
                            for d_s in active_isos:
                                schedule[d_s]["byInterne"] = snap_week[d_s]
                    if swapped_am_pm_sau:
                        break
                if swapped_am_pm_sau:
                    break

                # Échange simple d'1 demi-journée SAU entre un senior à 2 SAU et un senior à 1 SAU :
                # - soit pour résorber un 0M/2P + 1M/0P -> 0M/1P + 1M/1P (ou 2M/0P + 0M/1P -> 1M/0P + 1M/1P)
                # - soit pour équilibrer le cumul AM/PM (1M/1P + 0M/1P -> 0M/1P + 1M/1P)
                for sid_from in senior_interne_ids:
                    w_am_f = count_week_sau_half(sid_from, "am")
                    w_pm_f = count_week_sau_half(sid_from, "pm")
                    if w_am_f + w_pm_f != 2:
                        continue
                    for sid_to in senior_interne_ids:
                        if sid_to == sid_from:
                            continue
                        w_am_t = count_week_sau_half(sid_to, "am")
                        w_pm_t = count_week_sau_half(sid_to, "pm")
                        if w_am_t + w_pm_t != 1:
                            continue
                        # Cas 1 : sid_from est à 0M/2P et sid_to est à 1M/0P -> transférer 1 PM de sid_from vers sid_to
                        if w_am_f == 0 and w_pm_f == 2 and w_am_t == 1 and w_pm_t == 0:
                            if try_transfer_sau_half("pm", sid_from, sid_to, strict_irm=strict_irm):
                                swapped_am_pm_sau = True
                                break
                        # Cas 2 : sid_from est à 2M/0P et sid_to est à 0M/1P -> transférer 1 AM de sid_from vers sid_to
                        if w_am_f == 2 and w_pm_f == 0 and w_am_t == 0 and w_pm_t == 1:
                            if try_transfer_sau_half("am", sid_from, sid_to, strict_irm=strict_irm):
                                swapped_am_pm_sau = True
                                break
                        # Cas 3 : sid_from est à 1M/1P et sid_to est à 0M/1P -> transférer 1 AM de sid_from vers sid_to
                        if w_am_f == 1 and w_pm_f == 1 and w_am_t == 0 and w_pm_t == 1:
                            cum_am_f = total_sau_am_counts[sid_from] + w_am_f
                            cum_am_t = total_sau_am_counts[sid_to] + w_am_t
                            cum_pm_f = total_sau_pm_counts[sid_from] + w_pm_f
                            cum_pm_t = total_sau_pm_counts[sid_to] + w_pm_t
                            cum_diff_f = cum_am_f - cum_pm_f
                            cum_diff_t = cum_am_t - cum_pm_t
                            if (cum_am_f >= cum_am_t + 2 and cum_diff_f >= cum_diff_t + 2) or (
                                (cum_am_f + cum_pm_f) >= (cum_am_t + cum_pm_t) + 2 and cum_am_f >= cum_am_t + 1
                            ):
                                if try_transfer_sau_half("am", sid_from, sid_to, strict_irm=strict_irm):
                                    swapped_am_pm_sau = True
                                    break
                        # Cas 4 : sid_from est à 1M/1P et sid_to est à 1M/0P -> transférer 1 PM de sid_from vers sid_to
                        if w_am_f == 1 and w_pm_f == 1 and w_am_t == 1 and w_pm_t == 0:
                            cum_am_f = total_sau_am_counts[sid_from] + w_am_f
                            cum_am_t = total_sau_am_counts[sid_to] + w_am_t
                            cum_pm_f = total_sau_pm_counts[sid_from] + w_pm_f
                            cum_pm_t = total_sau_pm_counts[sid_to] + w_pm_t
                            cum_diff_f = cum_am_f - cum_pm_f
                            cum_diff_t = cum_am_t - cum_pm_t
                            if (cum_pm_f >= cum_pm_t + 2 and cum_diff_f <= cum_diff_t - 2) or (
                                (cum_am_f + cum_pm_f) >= (cum_am_t + cum_pm_t) + 2 and cum_pm_f >= cum_pm_t + 1
                            ):
                                if try_transfer_sau_half("pm", sid_from, sid_to, strict_irm=strict_irm):
                                    swapped_am_pm_sau = True
                                    break
                    if swapped_am_pm_sau:
                        break
                if swapped_am_pm_sau:
                    break
            if not swapped_am_pm_sau:
                break

        # G) ÉQUILIBRAGE DES VACATIONS DE POSTE C (GESTES (C) / RI) ENTRE LES INTERNES :
        #    1. Sur chaque semaine : éviter les semaines à 3 Postes C pour un même interne et limiter Noé (Socle) à max 1 Poste C / semaine
        #    2. Sur le cumul du semestre : équilibrer le total de Poste C (et l'équilibre Matin / Après-midi) entre les 5 internes seniors
        def count_week_gestes(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] == "GESTES (C)"
            )

        def count_week_ri(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] in ("GESTES (C)", "ALLURA")
            )

        def count_week_gestes_half(interne_id: str, half_k: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                if schedule[d_chk]["byInterne"][interne_id][half_k] == "GESTES (C)"
            )

        def can_swap_gestes_on_slot(d_slot: str, h_slot: str, from_sid: str, to_sid: str, strict_irm: bool = True) -> bool:
            if d_slot == "2026-11-02":
                return False
            by_s = schedule[d_slot]["byInterne"]
            if by_s[from_sid][h_slot] != "GESTES (C)":
                return False
            p_und = by_s[to_sid][h_slot]
            if p_und in non_active_codes or p_und in ("TDM SAU", "GESTES (C)", "ALLURA"):
                return False
            other_h_s = "pm" if h_slot == "am" else "am"
            if is_same_poste_am_pm(p_und, by_s[from_sid][other_h_s], avoid_irm_both=strict_irm):
                return False
            if is_same_poste_am_pm("GESTES (C)", by_s[to_sid][other_h_s], avoid_irm_both=strict_irm):
                return False
            if h_slot == "pm" and p_und == "IRM" and count_week_irm_pm(from_sid) >= 1:
                return False
            return True

        def execute_gestes_swap(d_slot: str, h_slot: str, from_sid: str, to_sid: str):
            by_s = schedule[d_slot]["byInterne"]
            nk_s = "noteAm" if h_slot == "am" else "notePm"
            p_und = by_s[to_sid][h_slot]
            n_over = by_s[from_sid].get(nk_s, "")
            n_und = by_s[to_sid].get(nk_s, "")
            by_s[from_sid][h_slot] = p_und
            by_s[from_sid][nk_s] = n_und
            by_s[to_sid][h_slot] = "GESTES (C)"
            by_s[to_sid][nk_s] = n_over

        # G-0) Si Noé (Phase Socle) a >= 2 GESTES (C) dans la même semaine (ou >14 sur le semestre quand un senior est à 0 sur la semaine),
        #      transférer 1 GESTES (C) vers un interne senior ayant <= 1 GESTES (C) cette semaine
        for _ in range(15):
            swapped_noe_g = False
            w_noe_g = count_week_gestes("noe")
            if w_noe_g >= 1:
                s_cands_g = sorted(
                    [s for s in senior_interne_ids if count_week_gestes(s) <= 1],
                    key=lambda s: (
                        count_week_gestes(s),
                        total_ri_counts[s] + count_week_ri(s),
                        total_gestes_counts[s] + count_week_gestes(s),
                    ),
                )
                for strict_irm in (True, False):
                    for sid_to in s_cands_g:
                        w_to_g = count_week_gestes(sid_to)
                        if not (w_noe_g >= 2 or (w_noe_g == 1 and w_to_g == 0 and total_gestes_counts["noe"] + w_noe_g > 14)):
                            continue
                        for h_g in ("pm", "am"):
                            for d_iso in active_isos:
                                if d_iso == "2026-11-02":
                                    continue
                                by_s = schedule[d_iso]["byInterne"]
                                if by_s["noe"][h_g] != "GESTES (C)":
                                    continue
                                p_sen = by_s[sid_to][h_g]
                                if p_sen not in ("ECHO", "SCAN ACHARD", "TDM OLLIER DIAG", "IRM 1,5T", "IRM 3T", "CONSULTATION", "LECTURE"):
                                    continue
                                other_h_g = "pm" if h_g == "am" else "am"
                                if is_same_poste_am_pm(p_sen, by_s["noe"][other_h_g], avoid_irm_both=strict_irm):
                                    continue
                                if is_same_poste_am_pm("GESTES (C)", by_s[sid_to][other_h_g], avoid_irm_both=strict_irm):
                                    continue
                                nk_g = "noteAm" if h_g == "am" else "notePm"
                                n_sen = by_s[sid_to].get(nk_g, "")
                                by_s["noe"][h_g] = p_sen
                                by_s["noe"][nk_g] = n_sen or f"Phase Socle ({p_sen})"
                                by_s[sid_to][h_g] = "GESTES (C)"
                                by_s[sid_to][nk_g] = ""
                                swapped_noe_g = True
                                break
                            if swapped_noe_g:
                                break
                        if swapped_noe_g:
                            break
                    if swapped_noe_g:
                        break
            if not swapped_noe_g:
                break

        # G-1) Équilibrer le nombre hebdomadaire et cumulé de GESTES (C) / RI entre les 5 internes seniors
        for _ in range(45):
            swapped_g = False
            s_sorted_g = sorted(
                senior_interne_ids,
                key=lambda s: (
                    1 if count_week_gestes(s) >= 2 else 0,
                    total_ri_counts[s] + count_week_ri(s),
                    total_gestes_counts[s] + count_week_gestes(s),
                    count_week_gestes(s),
                ),
                reverse=True,
            )
            for strict_irm in (True, False):
                for sid_over in s_sorted_g:
                    w_over = count_week_gestes(sid_over)
                    if w_over == 0:
                        continue
                    c_over = total_ri_counts[sid_over] + count_week_ri(sid_over)
                    for sid_under in reversed(s_sorted_g):
                        if sid_under == sid_over:
                            continue
                        w_under = count_week_gestes(sid_under)
                        c_under = total_ri_counts[sid_under] + count_week_ri(sid_under)
                        if not (
                            (w_over >= 2 and w_under == 0 and c_over >= c_under)
                            or (w_over >= 3 and w_under <= 1)
                            or (c_over >= c_under + 2 and w_under + 1 <= max(2, w_over))
                        ):
                            continue
                        over_am_diff = (total_gestes_am_counts[sid_over] + count_week_gestes_half(sid_over, "am")) - (
                            total_gestes_pm_counts[sid_over] + count_week_gestes_half(sid_over, "pm")
                        )
                        under_am_diff = (total_gestes_am_counts[sid_under] + count_week_gestes_half(sid_under, "am")) - (
                            total_gestes_pm_counts[sid_under] + count_week_gestes_half(sid_under, "pm")
                        )
                        pref_halves_g = ("am", "pm") if over_am_diff >= under_am_diff else ("pm", "am")
                        for h_g in pref_halves_g:
                            for d_iso in active_isos:
                                if can_swap_gestes_on_slot(d_iso, h_g, sid_over, sid_under, strict_irm=strict_irm):
                                    execute_gestes_swap(d_iso, h_g, sid_over, sid_under)
                                    swapped_g = True
                                    break
                            if swapped_g:
                                break
                        if swapped_g:
                            break
                    if swapped_g:
                        break
                if swapped_g:
                    break
            if not swapped_g:
                break

        # G-2) Équilibrer la répartition Matin (AM) vs Après-midi (PM) des GESTES (C) entre les seniors (sans modifier leur total hebdo)
        for _ in range(30):
            swapped_g_ampm = False
            s_am_sorted_g = sorted(
                senior_interne_ids,
                key=lambda s: (total_gestes_am_counts[s] + count_week_gestes_half(s, "am"))
                - (total_gestes_pm_counts[s] + count_week_gestes_half(s, "pm")),
                reverse=True,
            )
            for strict_irm in (True, False):
                for sid_a in s_am_sorted_g:
                    if count_week_gestes_half(sid_a, "am") == 0:
                        continue
                    diff_a = (total_gestes_am_counts[sid_a] + count_week_gestes_half(sid_a, "am")) - (
                        total_gestes_pm_counts[sid_a] + count_week_gestes_half(sid_a, "pm")
                    )
                    for sid_b in reversed(s_am_sorted_g):
                        if sid_b == sid_a:
                            continue
                        if count_week_gestes_half(sid_b, "pm") == 0:
                            continue
                        diff_b = (total_gestes_am_counts[sid_b] + count_week_gestes_half(sid_b, "am")) - (
                            total_gestes_pm_counts[sid_b] + count_week_gestes_half(sid_b, "pm")
                        )
                        if diff_a - diff_b < 3:
                            continue
                        d_am_g = next(
                            (d for d in active_isos if can_swap_gestes_on_slot(d, "am", sid_a, sid_b, strict_irm=strict_irm)),
                            None,
                        )
                        if not d_am_g:
                            continue
                        snap_g = {
                            d_s: {k_s: dict(v_s) for k_s, v_s in schedule[d_s]["byInterne"].items()}
                            for d_s in active_isos
                        }
                        execute_gestes_swap(d_am_g, "am", sid_a, sid_b)
                        d_pm_g = next(
                            (
                                d
                                for d in active_isos
                                if d != d_am_g and can_swap_gestes_on_slot(d, "pm", sid_b, sid_a, strict_irm=strict_irm)
                            ),
                            None,
                        )
                        if d_pm_g:
                            execute_gestes_swap(d_pm_g, "pm", sid_b, sid_a)
                            swapped_g_ampm = True
                            break
                        else:
                            for d_s in active_isos:
                                schedule[d_s]["byInterne"] = snap_g[d_s]
                    if swapped_g_ampm:
                        break
                if swapped_g_ampm:
                    break
            if not swapped_g_ampm:
                break

        # H) ÉQUILIBRAGE DES CONSULTATIONS (ET LECTURES) ENTRE LES INTERNES :
        #    1. Sur chaque semaine : maximum 1 Consultation par semaine par interne (jamais Mardi PM + Vendredi PM la même semaine)
        #    2. Sur le cumul du semestre : équilibrer le nombre total de Consultations (8 à 9 par interne)
        #    3. Équilibrer la répartition Mardi PM vs Vendredi PM des Consultations ainsi que le total de Lectures entre seniors
        def count_week_cs(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] == "CONSULTATION"
            )

        def count_week_cs_wd(interne_id: str, wd_target: int) -> int:
            return sum(
                1
                for d_chk in active_isos
                if datetime.date.fromisoformat(d_chk).weekday() == wd_target
                and schedule[d_chk]["byInterne"][interne_id]["pm"] == "CONSULTATION"
            )

        def count_week_lecture(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] == "LECTURE"
            )

        def format_pm_note_for_poste(d_slot: str, iid: str, p_code: str) -> str:
            wd_s = datetime.date.fromisoformat(d_slot).weekday()
            if p_code == "CONSULTATION":
                return "Consultation Internes (Mardi PM)" if wd_s == 1 else "Consultation Internes (Vendredi PM)"
            if p_code == "LECTURE":
                if wd_s == 1:
                    return "Relecture avec Pr Drapé" if iid == "noe" else "Relecture avec Pr Drapé (systématique)"
                return "Lecture (Vendredi PM)"
            if iid == "noe":
                return f"Phase Socle ({p_code})"
            return ""

        def can_swap_cs_on_slot(
            d_slot: str, from_id: str, to_id: str, allowed_other_postes: tuple[str, ...], strict_irm: bool = True
        ) -> bool:
            if d_slot == "2026-11-02":
                return False
            if to_id == "noe" and d_slot < "2027-03-01":
                return False
            wd_s = datetime.date.fromisoformat(d_slot).weekday()
            by_s = schedule[d_slot]["byInterne"]
            if by_s[from_id]["pm"] != "CONSULTATION":
                return False
            p_other = by_s[to_id]["pm"]
            if p_other not in allowed_other_postes:
                return False
            if wd_s == 1 and p_other == "LECTURE" and from_id == "noe":
                return False
            if "noe" in (from_id, to_id) and p_other != "LECTURE" and from_id != "noe":
                if any(by_s[s_id]["pm"] == p_other for s_id in senior_interne_ids if s_id != from_id):
                    return False
            if is_same_poste_am_pm(by_s[from_id]["am"], p_other, avoid_irm_both=strict_irm):
                return False
            if is_same_poste_am_pm(by_s[to_id]["am"], "CONSULTATION", avoid_irm_both=strict_irm):
                return False
            return True

        def execute_cs_swap(d_slot: str, from_id: str, to_id: str):
            by_s = schedule[d_slot]["byInterne"]
            p_other = by_s[to_id]["pm"]
            by_s[from_id]["pm"] = p_other
            by_s[from_id]["notePm"] = format_pm_note_for_poste(d_slot, from_id, p_other)
            by_s[to_id]["pm"] = "CONSULTATION"
            by_s[to_id]["notePm"] = format_pm_note_for_poste(d_slot, to_id, "CONSULTATION")

        # H-0) Avant le 01/03/2027, Noé ne fait aucune consultation : transférer toute CONSULTATION éventuelle de Noé vers un senior
        for d_iso in active_isos:
            if d_iso < "2027-03-01" and schedule[d_iso]["byInterne"]["noe"]["pm"] == "CONSULTATION":
                swapped_noe_cs = False
                cands_s = sorted(
                    [s for s in senior_interne_ids if count_week_cs(s) == 0],
                    key=lambda s: (total_cs_counts[s] + count_week_cs(s), -(total_lecture_counts[s] + count_week_lecture(s))),
                )
                for strict_irm in (True, False):
                    for allowed_postes in (("LECTURE",), ("LECTURE", "ECHO", "SCAN ACHARD", "TDM OLLIER DIAG")):
                        for u_sid in cands_s:
                            if can_swap_cs_on_slot(d_iso, "noe", u_sid, allowed_postes, strict_irm=strict_irm):
                                execute_cs_swap(d_iso, "noe", u_sid)
                                swapped_noe_cs = True
                                break
                        if swapped_noe_cs:
                            break
                        for mid_sid in senior_interne_ids:
                            if count_week_cs(mid_sid) != 1:
                                continue
                            if not can_swap_cs_on_slot(d_iso, "noe", mid_sid, allowed_postes, strict_irm=strict_irm):
                                continue
                            d2 = next(
                                (
                                    dt
                                    for dt in active_isos
                                    if dt != d_iso and schedule[dt]["byInterne"][mid_sid]["pm"] == "CONSULTATION"
                                ),
                                None,
                            )
                            if not d2:
                                continue
                            for u_sid in cands_s:
                                if can_swap_cs_on_slot(d2, mid_sid, u_sid, allowed_postes, strict_irm=strict_irm):
                                    execute_cs_swap(d2, mid_sid, u_sid)
                                    execute_cs_swap(d_iso, "noe", mid_sid)
                                    swapped_noe_cs = True
                                    break
                            if swapped_noe_cs:
                                break
                        if swapped_noe_cs:
                            break
                    if swapped_noe_cs:
                        break

        # H-1) Équilibrer le nombre hebdomadaire (max 1/semaine) et cumulé de CONSULTATION
        #      (cible : 9 pour chacun des 5 seniors, et 3 pour Noé sur les 2 derniers mois Mars-Avril)
        for _ in range(45):
            swapped_cs = False
            sorted_cs_iids = sorted(
                all_interne_ids,
                key=lambda i: (
                    1 if count_week_cs(i) >= 2 else 0,
                    (total_cs_counts[i] + count_week_cs(i)) - (3 if i == "noe" else 9),
                    1 if i == "noe" else 0,
                    count_week_cs(i),
                    -(total_lecture_counts[i] + count_week_lecture(i)),
                ),
                reverse=True,
            )
            for strict_irm in (True, False):
                for allowed_postes in (("LECTURE",), ("LECTURE", "ECHO", "SCAN ACHARD", "TDM OLLIER DIAG")):
                    for over_id in sorted_cs_iids:
                        w_over = count_week_cs(over_id)
                        if w_over == 0:
                            continue
                        c_over = total_cs_counts[over_id] + w_over
                        eff_over = c_over - (3 if over_id == "noe" else 9)
                        for under_id in reversed(sorted_cs_iids):
                            if under_id == over_id:
                                continue
                            w_under = count_week_cs(under_id)
                            c_under = total_cs_counts[under_id] + w_under
                            eff_under = c_under - (3 if under_id == "noe" else 9)
                            if under_id == "noe" and c_under >= 3:
                                continue
                            if not (
                                (w_over >= 2 and w_under == 0)
                                or (eff_over >= eff_under + 2 and w_under == 0)
                                or (
                                    over_id == "noe"
                                    and under_id in senior_interne_ids
                                    and c_over > 3
                                    and w_under == 0
                                )
                            ):
                                continue
                            pref_days = sorted(
                                active_isos,
                                key=lambda d: (
                                    total_cs_tue_counts[under_id] - total_cs_fri_counts[under_id]
                                    if datetime.date.fromisoformat(d).weekday() == 1
                                    else total_cs_fri_counts[under_id] - total_cs_tue_counts[under_id]
                                ),
                            )
                            for d_iso in pref_days:
                                if can_swap_cs_on_slot(d_iso, over_id, under_id, allowed_postes, strict_irm=strict_irm):
                                    execute_cs_swap(d_iso, over_id, under_id)
                                    swapped_cs = True
                                    break
                            if swapped_cs:
                                break
                            # Relais en 2 étapes via un interne intermédiaire mid_id (ayant 1 CS sur l'autre jour de CS de la semaine)
                            for mid_id in all_interne_ids:
                                if mid_id in (over_id, under_id) or count_week_cs(mid_id) != 1:
                                    continue
                                d1 = next(
                                    (d for d in pref_days if can_swap_cs_on_slot(d, over_id, mid_id, allowed_postes, strict_irm=strict_irm)),
                                    None,
                                )
                                if not d1:
                                    continue
                                d2 = next(
                                    (
                                        d
                                        for d in pref_days
                                        if d != d1 and can_swap_cs_on_slot(d, mid_id, under_id, allowed_postes, strict_irm=strict_irm)
                                    ),
                                    None,
                                )
                                if d2:
                                    execute_cs_swap(d1, over_id, mid_id)
                                    execute_cs_swap(d2, mid_id, under_id)
                                    swapped_cs = True
                                    break
                            if swapped_cs:
                                break
                        if swapped_cs:
                            break
                    if swapped_cs:
                        break
                if swapped_cs:
                    break
            if not swapped_cs:
                break

        # H-2) Équilibrer la répartition Mardi PM vs Vendredi PM des Consultations (sans dégrader l'écart global)
        allowed_tf_postes = ("LECTURE", "ECHO", "SCAN ACHARD", "TDM OLLIER DIAG")
        for _ in range(20):
            swapped_tf = False
            for d_iso in active_isos:
                wd_tf = datetime.date.fromisoformat(d_iso).weekday()
                if wd_tf not in (1, 4):
                    continue
                from_id = next((i for i in all_interne_ids if schedule[d_iso]["byInterne"][i]["pm"] == "CONSULTATION"), None)
                if not from_id:
                    continue
                w_from = count_week_cs(from_id)
                c_from = total_cs_counts[from_id] + w_from
                eff_from = c_from - (3 if from_id == "noe" else 9)
                from_wd_cnt = (total_cs_tue_counts[from_id] if wd_tf == 1 else total_cs_fri_counts[from_id]) + 1
                from_oth_cnt = total_cs_fri_counts[from_id] if wd_tf == 1 else total_cs_tue_counts[from_id]
                for to_id in all_interne_ids:
                    if to_id == from_id or count_week_cs(to_id) != 0:
                        continue
                    c_to = total_cs_counts[to_id]
                    eff_to = c_to - (3 if to_id == "noe" else 9)
                    if eff_from < eff_to + 1:
                        continue
                    if to_id == "noe" and (d_iso < "2027-03-01" or c_to >= 3):
                        continue
                    to_wd_cnt = total_cs_tue_counts[to_id] if wd_tf == 1 else total_cs_fri_counts[to_id]
                    to_oth_cnt = total_cs_fri_counts[to_id] if wd_tf == 1 else total_cs_tue_counts[to_id]
                    if (from_wd_cnt - from_oth_cnt) - (to_wd_cnt - to_oth_cnt) >= 2 and from_wd_cnt >= to_wd_cnt + 2:
                        if can_swap_cs_on_slot(d_iso, from_id, to_id, allowed_tf_postes, strict_irm=True):
                            execute_cs_swap(d_iso, from_id, to_id)
                            swapped_tf = True
                            break
                if swapped_tf:
                    break
            if not swapped_tf:
                break

        # H-3) Équilibrer les vacations de LECTURE entre les 5 internes seniors (hors CONSULTATION / TDM SAU / GESTES C / IRM)
        for _ in range(25):
            swapped_lec = False
            s_lec = sorted(
                senior_interne_ids,
                key=lambda s: (
                    1 if count_week_lecture(s) >= 2 else 0,
                    total_lecture_counts[s] + count_week_lecture(s),
                    count_week_lecture(s),
                ),
                reverse=True,
            )
            for over_s in s_lec:
                w_o = count_week_lecture(over_s)
                if w_o == 0:
                    continue
                c_o = total_lecture_counts[over_s] + w_o
                for under_s in reversed(s_lec):
                    if under_s == over_s:
                        continue
                    w_u = count_week_lecture(under_s)
                    c_u = total_lecture_counts[under_s] + w_u
                    if not ((w_o >= 2 and w_u == 0) or (c_o >= c_u + 2 and w_u == 0)):
                        continue
                    for d_iso in active_isos:
                        by_s = schedule[d_iso]["byInterne"]
                        if by_s[over_s]["pm"] != "LECTURE":
                            continue
                        p_u = by_s[under_s]["pm"]
                        if p_u not in ("ECHO", "SCAN ACHARD", "TDM OLLIER DIAG"):
                            continue
                        if is_same_poste_am_pm(by_s[over_s]["am"], p_u, avoid_irm_both=True):
                            continue
                        if is_same_poste_am_pm(by_s[under_s]["am"], "LECTURE", avoid_irm_both=True):
                            continue
                        by_s[over_s]["pm"] = p_u
                        by_s[over_s]["notePm"] = format_pm_note_for_poste(d_iso, over_s, p_u)
                        by_s[under_s]["pm"] = "LECTURE"
                        by_s[under_s]["notePm"] = format_pm_note_for_poste(d_iso, under_s, "LECTURE")
                        swapped_lec = True
                        break
                    if swapped_lec:
                        break
                if swapped_lec:
                    break
            if not swapped_lec:
                break

        # I) ÉQUILIBRAGE HEBDOMADAIRE ET CUMULÉ DES VACATIONS D'ÉCHOGRAPHIE (ECHO) ET D'IRM (IRM 3T / 1,5T / IRM PM)
        #    ainsi que des Scanners diagnostiques (SCAN ACHARD / TDM OLLIER DIAG) entre tous les internes :
        diag_balance_postes = ("ECHO", "IRM 3T", "IRM 1,5T", "IRM", "SCAN ACHARD", "TDM OLLIER DIAG")

        def count_week_echo(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] == "ECHO"
            )

        def count_week_echo_half(interne_id: str, half_k: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                if schedule[d_chk]["byInterne"][interne_id][half_k] == "ECHO"
            )

        def count_week_irm_am(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                if schedule[d_chk]["byInterne"][interne_id]["am"] in ("IRM 3T", "IRM 1,5T")
            )

        def count_week_achard(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] == "SCAN ACHARD"
            )

        def count_week_ollier(interne_id: str) -> int:
            return sum(
                1
                for d_chk in active_isos
                for h_chk in ("am", "pm")
                if schedule[d_chk]["byInterne"][interne_id][h_chk] == "TDM OLLIER DIAG"
            )

        def can_swap_diag_on_slot(d_slot: str, h_slot: str, i1: str, i2: str) -> bool:
            if d_slot == "2026-11-02":
                return False
            by_s = schedule[d_slot]["byInterne"]
            p1 = by_s[i1][h_slot]
            p2 = by_s[i2][h_slot]
            if p1 == p2 or p1 not in diag_balance_postes or p2 not in diag_balance_postes:
                return False
            if "noe" in (i1, i2):
                sen_id = i2 if i1 == "noe" else i1
                p_noe = p1 if i1 == "noe" else p2
                if any(by_s[s_other][h_slot] == p_noe for s_other in senior_interne_ids if s_other != sen_id):
                    return False
            other_h_s = "pm" if h_slot == "am" else "am"
            if is_same_poste_am_pm(p2, by_s[i1][other_h_s], avoid_irm_both=True):
                return False
            if is_same_poste_am_pm(p1, by_s[i2][other_h_s], avoid_irm_both=True):
                return False
            if h_slot == "pm":
                if p2 == "IRM" and p1 != "IRM" and count_week_irm_pm(i1) >= 1:
                    return False
                if p1 == "IRM" and p2 != "IRM" and count_week_irm_pm(i2) >= 1:
                    return False
            return True

        def execute_diag_swap(d_slot: str, h_slot: str, i1: str, i2: str):
            by_s = schedule[d_slot]["byInterne"]
            nk_s = "noteAm" if h_slot == "am" else "notePm"
            p1, p2 = by_s[i1][h_slot], by_s[i2][h_slot]
            by_s[i1][h_slot] = p2
            by_s[i1][nk_s] = f"Phase Socle ({p2})" if i1 == "noe" else ""
            by_s[i2][h_slot] = p1
            by_s[i2][nk_s] = f"Phase Socle ({p1})" if i2 == "noe" else ""

        def eval_week_cum_diag_score() -> float:
            w_echo = {i: count_week_echo(i) for i in all_interne_ids}
            w_echo_am = {i: count_week_echo_half(i, "am") for i in all_interne_ids}
            w_echo_pm = {i: count_week_echo_half(i, "pm") for i in all_interne_ids}
            w_irm_am = {i: count_week_irm_am(i) for i in all_interne_ids}
            w_irm_pm = {i: count_week_irm_pm(i) for i in all_interne_ids}
            w_ach = {i: count_week_achard(i) for i in all_interne_ids}
            w_oll = {i: count_week_ollier(i) for i in all_interne_ids}

            c_echo = [total_echo_counts[i] + w_echo[i] for i in all_interne_ids]
            c_echo_am = [total_echo_am_counts[i] + w_echo_am[i] for i in all_interne_ids]
            c_echo_pm = [total_echo_pm_counts[i] + w_echo_pm[i] for i in all_interne_ids]
            c_irm_am = [total_irm_am_counts[i] + w_irm_am[i] for i in all_interne_ids]
            c_irm_pm = [total_irm_pm_counts[i] + w_irm_pm[i] for i in all_interne_ids]
            c_irm_tot = [c_irm_am[k] + c_irm_pm[k] for k in range(len(all_interne_ids))]
            c_ach_sen = [total_achard_counts[s] + w_ach[s] for s in senior_interne_ids]
            c_oll_sen = [total_ollier_counts[s] + w_oll[s] for s in senior_interne_ids]

            def _var(vals: list[int | float]) -> float:
                mean_v = sum(vals) / len(vals)
                return sum((v - mean_v) ** 2 for v in vals)

            return (
                16.0 * _var(c_echo)
                + 16.0 * _var(c_irm_tot)
                + 10.0 * _var(c_irm_am)
                + 10.0 * _var(c_irm_pm)
                + 3.0 * _var(c_echo_am)
                + 3.0 * _var(c_echo_pm)
                + 4.0 * _var(c_ach_sen)
                + 4.0 * _var(c_oll_sen)
                + 4.0 * _var(list(w_echo.values()))
                + 4.0 * _var([w_irm_am[i] + w_irm_pm[i] for i in all_interne_ids])
            )

        for _ in range(60):
            improved_diag = False
            cur_diag_score = eval_week_cum_diag_score()
            for d_iso in active_isos:
                for h_d in ("am", "pm"):
                    for idx1 in range(len(all_interne_ids)):
                        for idx2 in range(idx1 + 1, len(all_interne_ids)):
                            i1, i2 = all_interne_ids[idx1], all_interne_ids[idx2]
                            if can_swap_diag_on_slot(d_iso, h_d, i1, i2):
                                execute_diag_swap(d_iso, h_d, i1, i2)
                                new_diag_score = eval_week_cum_diag_score()
                                if new_diag_score < cur_diag_score - 1e-6:
                                    cur_diag_score = new_diag_score
                                    improved_diag = True
                                else:
                                    execute_diag_swap(d_iso, h_d, i1, i2)
            if not improved_diag:
                break

        # Mettre à jour les compteurs cumulés d'IRM PM, de TDM SAU (AM/PM), de Poste C (GESTES (C) / RI), de Consultations / Lectures et d'Écho / IRM du semestre
        for iid in all_interne_ids:
            total_irm_pm_counts[iid] += count_week_irm_pm(iid)
            total_sau_am_counts[iid] += count_week_sau_half(iid, "am")
            total_sau_pm_counts[iid] += count_week_sau_half(iid, "pm")
            total_gestes_counts[iid] += count_week_gestes(iid)
            total_ri_counts[iid] += count_week_ri(iid)
            total_gestes_am_counts[iid] += count_week_gestes_half(iid, "am")
            total_gestes_pm_counts[iid] += count_week_gestes_half(iid, "pm")
            total_cs_counts[iid] += count_week_cs(iid)
            total_cs_tue_counts[iid] += count_week_cs_wd(iid, 1)
            total_cs_fri_counts[iid] += count_week_cs_wd(iid, 4)
            total_lecture_counts[iid] += count_week_lecture(iid)
            total_echo_counts[iid] += count_week_echo(iid)
            total_echo_am_counts[iid] += count_week_echo_half(iid, "am")
            total_echo_pm_counts[iid] += count_week_echo_half(iid, "pm")
            total_irm_am_counts[iid] += count_week_irm_am(iid)
            total_achard_counts[iid] += count_week_achard(iid)
            total_ollier_counts[iid] += count_week_ollier(iid)

        # 5C. Mise à jour des notes de binôme de Noé (Phase Socle) et des remplacements exceptionnels (TDM SAU / IRM PM)
        final_senior_sau = {s_id: count_week_sau(s_id) for s_id in senior_interne_ids}
        for s_id, s_cnt in final_senior_sau.items():
            if s_cnt > 2:
                seen_sau = 0
                for d_iso in active_isos:
                    for h in ("am", "pm"):
                        st_s = schedule[d_iso]["byInterne"][s_id]
                        if st_s[h] == "TDM SAU":
                            seen_sau += 1
                            if seen_sau > 2:
                                nk = "noteAm" if h == "am" else "notePm"
                                st_s[nk] = "3e TDM SAU exceptionnel (remplacement congés/RG)"
                                if not st_s.get("note"):
                                    st_s["note"] = st_s[nk]

        for iid in all_interne_ids:
            if count_week_irm_pm(iid) > 1:
                seen_irm_pm = 0
                for d_iso in active_isos:
                    st_i = schedule[d_iso]["byInterne"][iid]
                    if st_i["pm"] == "IRM":
                        seen_irm_pm += 1
                        if seen_irm_pm > 1:
                            st_i["notePm"] = "2e IRM d'après-midi exceptionnelle (remplacement congés/RG)"
                            if not st_i.get("note"):
                                st_i["note"] = st_i["notePm"]

        for d_iso in active_isos:
            wd_cur = datetime.date.fromisoformat(d_iso).weekday()
            by_int = schedule[d_iso]["byInterne"]
            for h in ("am", "pm"):
                nk = "noteAm" if h == "am" else "notePm"
                noe_st = by_int["noe"]
                noe_p = noe_st[h]
                if noe_p in non_active_codes:
                    continue
                if noe_p == "TDM SAU":
                    sau_partners = [interne_short_by_id[s_id] for s_id in senior_interne_ids if by_int[s_id][h] == "TDM SAU"]
                    partner_str = " & ".join(sau_partners)
                    if h == "am" and wd_cur == 1:
                        noe_st[nk] = (
                            f"Avec Dr Macil HAMADOUCHE (MH) • Binôme SAU avec {partner_str}"
                            if partner_str
                            else "Avec Dr Macil HAMADOUCHE (MH) — Solo SAU (exceptionnellement sans doublure)"
                        )
                    elif h == "am" and wd_cur == 3:
                        noe_st[nk] = f"Avec Dr Macil HAMADOUCHE (MH) • Binôme SAU avec {partner_str}" if partner_str else "Avec Dr Macil HAMADOUCHE (MH) — Posté Socle Urgences"
                    else:
                        noe_st[nk] = f"Posté Socle Urgences • Binôme SAU avec {partner_str}" if partner_str else "Posté Socle Urgences"

            if d_iso != "2026-11-02":
                notes_combined = [x for x in (by_int["noe"].get("noteAm", ""), by_int["noe"].get("notePm", "")) if x]
                by_int["noe"]["note"] = " • ".join(notes_combined)

    for d_iso, day_obj in schedule.items():
        if not day_obj.get("holiday"):
            wd_chk = datetime.date.fromisoformat(d_iso).weekday()
            ch_chk = (chefs_planning or {}).get(d_iso, {})
            # Vérifier qu'aucun interne ne fait le même poste actif toute la journée (am == pm)
            # et qu'aucun interne n'a de demi-off le mardi après-midi ni le vendredi après-midi
            for iid_chk, st_chk in day_obj["byInterne"].items():
                p_am_chk, p_pm_chk = st_chk["am"], st_chk["pm"]
                if p_am_chk not in non_active_codes and p_pm_chk not in non_active_codes and p_am_chk == p_pm_chk:
                    raise RuntimeError(f"ERREUR : L'interne {iid_chk} a le même poste toute la journée ({p_am_chk}) le {d_iso}")
                if wd_chk in (1, 4) and p_pm_chk == "1/2 journée libre":
                    raise RuntimeError(f"ERREUR : Demi-off interdit le {'mardi' if wd_chk == 1 else 'vendredi'} après-midi pour {iid_chk} le {d_iso}")
            for h_chk in ("am", "pm"):
                if d_iso == "2026-11-02" and h_chk == "am":
                    continue
                is_tue_am_noe_solo_chk = (wd_chk == 1 and h_chk == "am" and day_obj["byInterne"]["noe"]["am"] == "TDM SAU")
                if not is_tue_am_noe_solo_chk and not any(day_obj["byInterne"][s_id][h_chk] == "TDM SAU" for s_id in senior_interne_ids):
                    raise RuntimeError(f"ERREUR : Aucun interne senior au TDM SAU le {d_iso} ({h_chk})")
                ph_req = get_ph_interne_postes_for_halfday(ch_chk, h_chk, wd_chk, d_iso)
                present_cnt = sum(
                    1
                    for st in day_obj["byInterne"].values()
                    if st[h_chk] not in ("RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL")
                )
                if present_cnt >= 1 + len(ph_req):
                    for ph_p in ph_req:
                        if not any(day_obj["byInterne"][any_id][h_chk] == ph_p for any_id in day_obj["byInterne"]):
                            raise RuntimeError(f"ERREUR : Vacation obligatoire non couverte ({ph_p}) le {d_iso} ({h_chk})")
        rebuild_day_lists(day_obj)

    for w_chk_idx, iso_chk_list in sorted(weeks_map.items()):
        active_chk_isos = [d_iso for d_iso in iso_chk_list if not schedule[d_iso].get("holiday")]
        for iid_chk in all_interne_ids:
            w_off_cnt = sum(
                1
                for d_iso in active_chk_isos
                for h_chk in ("am", "pm")
                if schedule[d_iso]["byInterne"][iid_chk][h_chk] == "1/2 journée libre"
            )
            if w_off_cnt > 2:
                raise RuntimeError(
                    f"ERREUR : L'interne {iid_chk} a {w_off_cnt} demi-offs (> 2 autorisés) sur la semaine du {iso_chk_list[0]}"
                )

    return schedule


def build_initial_presentations(schedule: dict | None = None) -> list[dict]:
    """
    Génère le calendrier des 3 pages séparées du semestre Hiver 2026-2027 :
    1. Cas des internes (Mardis, à partir de la semaine du 09/11/2026, soit dès le mardi 10/11/2026) : type = 'cas_mardi'
    2. Biblio des internes (Vendredis, à partir de la semaine du 09/11/2026, soit dès le vendredi 13/11/2026) : type = 'biblio_vendredi'
    3. Cours des internes faits par les chefs (Mardis dès le 03/11/2026, planning officiel de Dr Fadila Mihoubi Bouvier) : type = 'cours_internes'

    Règle d'espacement strict des présentations des internes :
    - Décalage d'un demi-cycle (3 semaines) entre le tour de Cas du Mardi et le tour de Biblio du Vendredi.
    - Chaque interne alterne Cas et Biblio avec au moins 18 à 24 jours (2,5 à 3,5 semaines) d'écart
      entre deux présentations quelconques (Cas ou Biblio), et au moins 42 jours (6 semaines) d'écart
      entre deux Cas ou entre deux Biblios.
    """
    start_date = datetime.date(2026, 11, 2)
    internes_pres_start_date = datetime.date(2026, 11, 9)  # Début des présentations des internes en semaine 2
    end_date = datetime.date(2027, 4, 30)
    # Oussama (DJ) et les internes seniors passent en premier ; Noé (Phase Socle) passe en dernier du cycle de Cas
    rotation_ids = ["oussama", "gabriel", "marwane", "milan", "nathanael", "noe"]
    tue_counts = {k: 0 for k in rotation_ids}
    fri_counts = {k: 0 for k in rotation_ids}
    last_any_date: dict[str, datetime.date | None] = {k: None for k in rotation_ids}
    last_tue_date: dict[str, datetime.date | None] = {k: None for k in rotation_ids}
    last_fri_date: dict[str, datetime.date | None] = {k: None for k in rotation_ids}

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
            iid for iid in rotation_ids
            if day_by_int.get(iid, {}).get("am") not in ("RG", "VACANCES")
            and day_by_int.get(iid, {}).get("pm") not in ("RG", "VACANCES")
        ]
        pool = present_ids if present_ids else rotation_ids

        if wd == 1:  # MARDI : 1) Cas des internes (dès le 10/11/2026) + 2) Cours des internes (fait par le chef)
            chef_nom, chef_sujet = FADILA_COURS_SCHEDULE.get(iso, ("—", ""))
            pas_de_cours = (chef_sujet == "Pas de cours")

            if cur >= internes_pres_start_date and not pas_de_cours:
                def score_tue(x: str) -> tuple:
                    d_any = (cur - last_any_date[x]).days if last_any_date[x] else 999
                    d_tue = (cur - last_tue_date[x]).days if last_tue_date[x] else 999
                    return (
                        1 if d_any < 18 else 0,
                        1 if d_tue < 35 else 0,
                        tue_counts[x],
                        tue_counts[x] + fri_counts[x],
                        -min(d_any, 24),
                        -min(d_tue, 42),
                        (rotation_ids.index(x) - tuesday_idx) % len(rotation_ids),
                    )

                cands = sorted(pool, key=score_tue)
                assigned_id = cands[0]
                tue_counts[assigned_id] += 1
                last_any_date[assigned_id] = cur
                last_tue_date[assigned_id] = cur
                assigned_obj = next(x for x in INTERNES_LIST if x["id"] == assigned_id)
                items.append({
                    "id": f"cas-{iso}",
                    "date": iso,
                    "type": "cas_mardi",
                    "typeLabel": "Cas des internes",
                    "interneId": assigned_id,
                    "interneName": assigned_obj["shortName"],
                    "sujet": "",
                })
                tuesday_idx += 1

            items.append({
                "id": f"cours-{iso}",
                "date": iso,
                "type": "cours_internes",
                "typeLabel": "Cours des internes",
                "chefIntervenant": "" if pas_de_cours else chef_nom,
                "coursChef": chef_sujet,
                "sujet": chef_sujet,
                "pasDeCours": pas_de_cours,
            })

        elif wd == 4 and cur >= internes_pres_start_date:  # VENDREDI : Biblio des internes (dès le 13/11/2026)
            def score_fri(x: str) -> tuple:
                d_any = (cur - last_any_date[x]).days if last_any_date[x] else 999
                d_fri = (cur - last_fri_date[x]).days if last_fri_date[x] else 999
                return (
                    1 if d_any < 18 else 0,
                    1 if d_fri < 35 else 0,
                    fri_counts[x],
                    tue_counts[x] + fri_counts[x],
                    -min(d_any, 24),
                    -min(d_fri, 42),
                    (rotation_ids.index(x) - (friday_idx + 3)) % len(rotation_ids),
                )

            cands = sorted(pool, key=score_fri)
            assigned_id = cands[0]
            fri_counts[assigned_id] += 1
            last_any_date[assigned_id] = cur
            last_fri_date[assigned_id] = cur
            assigned_obj = next(x for x in INTERNES_LIST if x["id"] == assigned_id)
            items.append({
                "id": f"biblio-{iso}",
                "date": iso,
                "type": "biblio_vendredi",
                "typeLabel": "Biblio",
                "interneId": assigned_id,
                "interneName": assigned_obj["shortName"],
                "sujet": "",
            })
            friday_idx += 1

        cur += datetime.timedelta(days=1)

    items.sort(key=lambda x: (x["date"], x["type"]))
    return items


def build_service_meetings() -> list[dict]:
    """
    Calendrier simplifié des réunions majeures du service :
    - Bone Club Cochin (Mercredis 18h00 – 20h00, Amphithéâtre Luton)
    - CRA : Confrontations Radio-Anatomo-Pathologiques (Vendredis 14h00/14h15 – 16h00, Salle de Staff Radio B)
    """
    return [
        {
            "id": "reunion-2026-11-25-boneclub",
            "date": "2026-11-25",
            "horaire": "18h00 – 20h00",
            "title": "Bone Club Cochin — Novembre",
            "category": "Bone Club",
            "sender": "Pr J-L. Drapé & Pr A. Feydy",
            "location": "Amphithéâtre Luton (Cochin)",
            "description": "Session de Novembre — Dossiers d'imagerie ostéo-articulaire",
            "mandatory": True,
        },
        {
            "id": "reunion-2026-11-27-anapath",
            "date": "2026-11-27",
            "horaire": "14h00 – 16h00",
            "title": "CRA #1 — Confrontation Radio-Anapath (Novembre)",
            "category": "CRA",
            "sender": "Radio B & Anapath (Pr B. Terris, Dr F. Larousserie, Dr V. Audard)",
            "location": "Salle de Staff Radio B (Albarran -1)",
            "description": "Corrélation radio-histologique de l'appareil locomoteur",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-01-15-anapath",
            "date": "2027-01-15",
            "horaire": "14h15 – 16h00",
            "title": "CRA #2 — Confrontation Radio-Anapath (Janvier)",
            "category": "CRA",
            "sender": "Radio B & Anapath (Dr F. Larousserie, Dr V. Audard)",
            "location": "Salle de Staff Radio B (Albarran -1)",
            "description": "Corrélation radio-histologique de l'appareil locomoteur",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-01-20-boneclub",
            "date": "2027-01-20",
            "horaire": "18h00 – 20h00",
            "title": "Bone Club Cochin — Janvier",
            "category": "Bone Club",
            "sender": "Dr M. Lacroix & Pr J-L. Drapé",
            "location": "Amphithéâtre Luton (Cochin)",
            "description": "Modération : Dr M. Lacroix (HEGP) & Pr J-L. Drapé (Cochin)",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-03-24-boneclub",
            "date": "2027-03-24",
            "horaire": "18h00 – 20h00",
            "title": "Bone Club Cochin — Mars",
            "category": "Bone Club",
            "sender": "Pr É. Dion, Dr M. Crézé & Pr A. Feydy",
            "location": "Amphithéâtre Luton (Cochin)",
            "description": "Modération : Pr É. Dion, Dr M. Crézé & Pr A. Feydy",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-03-26-anapath",
            "date": "2027-03-26",
            "horaire": "14h15 – 16h00",
            "title": "CRA #3 — Confrontation Radio-Anapath (Mars)",
            "category": "CRA",
            "sender": "Radio B & Anapath (Dr F. Larousserie, Dr V. Audard)",
            "location": "Salle de Staff Radio B (Albarran -1)",
            "description": "Corrélation radio-histologique de l'appareil locomoteur",
            "mandatory": True,
        },
        {
            "id": "reunion-2027-05-14-anapath",
            "date": "2027-05-14",
            "horaire": "14h15 – 16h00",
            "title": "CRA #4 — Confrontation Radio-Anapath (Mai)",
            "category": "CRA",
            "sender": "Radio B & Anapath",
            "location": "Salle de Staff Radio B (Albarran -1)",
            "description": "Corrélation radio-histologique de l'appareil locomoteur",
            "mandatory": False,
        },
        {
            "id": "reunion-2027-05-26-boneclub",
            "date": "2027-05-26",
            "horaire": "18h00 – 20h00",
            "title": "Bone Club Cochin — Mai",
            "category": "Bone Club",
            "sender": "Pr A. Feydy & Dr M. Lacroix",
            "location": "Amphithéâtre Luton (Cochin)",
            "description": "Modération : Pr A. Feydy & Dr M. Lacroix",
            "mandatory": False,
        },
        {
            "id": "reunion-2027-06-18-anapath",
            "date": "2027-06-18",
            "horaire": "14h15 – 16h00",
            "title": "CRA #5 — Confrontation Radio-Anapath (Juin)",
            "category": "CRA",
            "sender": "Radio B & Anapath",
            "location": "Salle de Staff Radio B (Albarran -1)",
            "description": "Corrélation radio-histologique de l'appareil locomoteur",
            "mandatory": False,
        },
        {
            "id": "reunion-2027-06-30-boneclub",
            "date": "2027-06-30",
            "horaire": "18h00 – 20h00",
            "title": "Bone Club Cochin × APRAMEN — Juin",
            "category": "Bone Club",
            "sender": "Pr A. Feydy & Dr F. Paycha",
            "location": "Amphithéâtre Luton (Cochin)",
            "description": "Session jumelée annuelle Bone Club & APRAMEN (Pr A. Feydy & Dr F. Paycha)",
            "mandatory": False,
        },
    ]


def build_recurring_staffs() -> list[dict]:
    """Staffs médico-chirurgicaux et multidisciplinaires hebdomadaires du service de Radiologie B."""
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
                {"horaire": "Après-midi", "title": "Staff RCP Sarcomes des Tissus Mous", "referent": "Dr A. Laporte & Chefs"},
            ],
        },
        {
            "day": "Mercredi",
            "weekday": 2,
            "items": [
                {"horaire": "Après-midi", "title": "Staff Rachis / Rhumatologie Osseuse", "referent": "Dr Yang"},
            ],
        },
        {
            "day": "Vendredi",
            "weekday": 4,
            "items": [
                {"horaire": "Matin", "title": "Staff Prothèses & Imagerie Orthopédique", "referent": "Dr H. Guérini"},
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

    def _mon_of_iso(d_str: str) -> str:
        dt_d = datetime.date.fromisoformat(d_str)
        return (dt_d - datetime.timedelta(days=dt_d.weekday())).isoformat()

    schedule = json.loads(json.dumps(base_schedule))
    rg_by_week: dict[str, list[dict]] = {}
    for a in rg_absences:
        if a.get("date"):
            rg_by_week.setdefault(_mon_of_iso(a["date"]), []).append(a)
    active_by_week: dict[str, list[dict]] = {}
    for a in active_absences_for_sched:
        if a.get("date"):
            active_by_week.setdefault(_mon_of_iso(a["date"]), []).append(a)

    all_mons = sorted({_mon_of_iso(d_iso) for d_iso in base_schedule})
    for mon_iso in all_mons:
        if isinstance(locked_weeks.get(mon_iso), dict) and locked_weeks[mon_iso].get("locked"):
            continue
        w_rg = {(a.get("date"), a.get("interneId")): a.get("type") for a in rg_by_week.get(mon_iso, [])}
        w_act = {(a.get("date"), a.get("interneId")): a.get("type") for a in active_by_week.get(mon_iso, [])}
        if w_rg != w_act:
            isolated_abs = [a for a in rg_absences if _mon_of_iso(a["date"]) != mon_iso] + active_by_week.get(mon_iso, [])
            w_sched = generate_semester_schedule(isolated_abs, chefs_planning)
            for d_iso, d_val in w_sched.items():
                if _mon_of_iso(d_iso) == mon_iso and d_iso in schedule:
                    base_by_int = base_schedule.get(d_iso, {}).get("byInterne", {})
                    for iid, sl in d_val.get("byInterne", {}).items():
                        b_sl = base_by_int.get(iid, {})
                        if "preRgAm" in b_sl:
                            sl["preRgAm"] = b_sl["preRgAm"]
                        if "preRgPm" in b_sl:
                            sl["preRgPm"] = b_sl["preRgPm"]
                    schedule[d_iso] = d_val

    # Équilibrage global final des Consultations sur les semaines non verrouillées (après intégration des congés et customVacations)
    all_iids_global = [x["id"] for x in INTERNES_LIST]
    non_active_global = ("1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL")
    weeks_by_mon_global: dict[str, list[str]] = {}
    for d_iso in sorted(schedule.keys()):
        weeks_by_mon_global.setdefault(_mon_of_iso(d_iso), []).append(d_iso)
    unlocked_mons_global = [
        m for m in sorted(weeks_by_mon_global.keys())
        if not (isinstance(locked_weeks.get(m), dict) and locked_weeks[m].get("locked"))
    ]

    def _effective_slot_post(d_iso: str, iid: str, half: str) -> str:
        ck = f"{d_iso}__{iid}"
        cv = custom_vacations.get(ck)
        if isinstance(cv, dict) and cv.get(half):
            return cv[half]
        return schedule[d_iso]["byInterne"][iid][half]

    def _is_same_poste_day_global(p1: str, p2: str) -> bool:
        if not p1 or not p2 or p1 in non_active_global or p2 in non_active_global:
            return False
        if p1 == p2:
            return True
        if "IRM" in p1 and "IRM" in p2:
            return True
        return False

    def _format_pm_note_global(d_iso: str, iid: str, p_code: str) -> str:
        wd_d = datetime.date.fromisoformat(d_iso).weekday()
        if p_code == "CONSULTATION":
            return "Consultation Internes (Mardi PM)" if wd_d == 1 else "Consultation Internes (Vendredi PM)"
        if p_code == "LECTURE":
            if wd_d == 1:
                return "Relecture avec Pr Drapé" if iid == "noe" else "Relecture avec Pr Drapé (systématique)"
            return "Lecture (Vendredi PM)"
        if iid == "noe":
            return f"Phase Socle ({p_code})"
        return ""

    # Convertir une LECTURE du Vendredi PM en CONSULTATION si la CONSULTATION du Vendredi PM n'est pas couverte (ex: interne en VACANCES)
    for mon_iso in unlocked_mons_global:
        for d_iso in weeks_by_mon_global[mon_iso]:
            if schedule[d_iso].get("holiday"):
                continue
            if datetime.date.fromisoformat(d_iso).weekday() != 4:
                continue
            has_cs_fri = any(_effective_slot_post(d_iso, iid, "pm") == "CONSULTATION" for iid in all_iids_global)
            if not has_cs_fri:
                for iid in all_iids_global:
                    ck = f"{d_iso}__{iid}"
                    if isinstance(custom_vacations.get(ck), dict) and custom_vacations[ck].get("pm"):
                        continue
                    if _effective_slot_post(d_iso, iid, "pm") == "LECTURE" and not _is_same_poste_day_global(_effective_slot_post(d_iso, iid, "am"), "CONSULTATION"):
                        sl = schedule[d_iso]["byInterne"][iid]
                        sl["pm"] = "CONSULTATION"
                        sl["notePm"] = _format_pm_note_global(d_iso, iid, "CONSULTATION")
                        sl["note"] = " • ".join(x for x in (sl.get("noteAm", ""), sl.get("notePm", "")) if x)
                        rebuild_day_lists(schedule[d_iso])
                        break

    def _week_cs_cnt(mon_iso: str, iid: str) -> int:
        return sum(
            1
            for d_iso in weeks_by_mon_global[mon_iso]
            if not schedule[d_iso].get("holiday")
            for h in ("am", "pm")
            if _effective_slot_post(d_iso, iid, h) == "CONSULTATION"
        )

    def _total_cs_cnt(iid: str) -> int:
        return sum(
            1
            for d_iso, d_obj in schedule.items()
            if not d_obj.get("holiday")
            for h in ("am", "pm")
            if _effective_slot_post(d_iso, iid, h) == "CONSULTATION"
        )

    def _total_cs_wd_cnt(iid: str, wd_target: int) -> int:
        return sum(
            1
            for d_iso, d_obj in schedule.items()
            if not d_obj.get("holiday") and datetime.date.fromisoformat(d_iso).weekday() == wd_target
            for h in ("am", "pm")
            if _effective_slot_post(d_iso, iid, h) == "CONSULTATION"
        )

    def _can_swap_cs_global(d_iso: str, from_id: str, to_id: str, allowed_postes: tuple[str, ...]) -> bool:
        if d_iso == "2026-11-02" or schedule[d_iso].get("holiday"):
            return False
        if to_id == "noe" and d_iso < "2027-03-01":
            return False
        if isinstance(custom_vacations.get(f"{d_iso}__{from_id}"), dict) and custom_vacations[f"{d_iso}__{from_id}"].get("pm"):
            return False
        if isinstance(custom_vacations.get(f"{d_iso}__{to_id}"), dict) and custom_vacations[f"{d_iso}__{to_id}"].get("pm"):
            return False
        wd_d = datetime.date.fromisoformat(d_iso).weekday()
        if _effective_slot_post(d_iso, from_id, "pm") != "CONSULTATION":
            return False
        p_other = _effective_slot_post(d_iso, to_id, "pm")
        if p_other not in allowed_postes:
            return False
        if wd_d == 1 and p_other == "LECTURE" and from_id == "noe":
            return False
        if "noe" in (from_id, to_id) and p_other != "LECTURE" and from_id != "noe":
            if any(_effective_slot_post(d_iso, s_id, "pm") == p_other for s_id in all_iids_global if s_id not in ("noe", from_id)):
                return False
        if _is_same_poste_day_global(_effective_slot_post(d_iso, from_id, "am"), p_other):
            return False
        if _is_same_poste_day_global(_effective_slot_post(d_iso, to_id, "am"), "CONSULTATION"):
            return False
        return True

    def _exec_swap_cs_global(d_iso: str, from_id: str, to_id: str) -> None:
        by_s = schedule[d_iso]["byInterne"]
        p_other = by_s[to_id]["pm"]
        by_s[from_id]["pm"] = p_other
        by_s[from_id]["notePm"] = _format_pm_note_global(d_iso, from_id, p_other)
        by_s[from_id]["note"] = " • ".join(x for x in (by_s[from_id].get("noteAm", ""), by_s[from_id].get("notePm", "")) if x)
        by_s[to_id]["pm"] = "CONSULTATION"
        by_s[to_id]["notePm"] = _format_pm_note_global(d_iso, to_id, "CONSULTATION")
        by_s[to_id]["note"] = " • ".join(x for x in (by_s[to_id].get("noteAm", ""), by_s[to_id].get("notePm", "")) if x)
        rebuild_day_lists(schedule[d_iso])

    senior_iids_global = [x for x in all_iids_global if x != "noe"]

    # 0) Avant le 01/03/2027, transférer toute consultation de Noé vers un interne senior
    for mon_iso in unlocked_mons_global:
        for d_iso in weeks_by_mon_global[mon_iso]:
            if d_iso < "2027-03-01" and not schedule[d_iso].get("holiday") and _effective_slot_post(d_iso, "noe", "pm") == "CONSULTATION":
                sw_n = False
                cands_s = sorted([s for s in senior_iids_global if _week_cs_cnt(mon_iso, s) == 0], key=_total_cs_cnt)
                for allowed_list in (("LECTURE",), ("LECTURE", "ECHO", "SCAN ACHARD", "TDM OLLIER DIAG")):
                    for u_id in cands_s:
                        if _can_swap_cs_global(d_iso, "noe", u_id, allowed_list):
                            _exec_swap_cs_global(d_iso, "noe", u_id)
                            sw_n = True
                            break
                    if sw_n:
                        break
                    for mid_s in senior_iids_global:
                        if _week_cs_cnt(mon_iso, mid_s) != 1 or not _can_swap_cs_global(d_iso, "noe", mid_s, allowed_list):
                            continue
                        d2 = next(
                            (
                                dt
                                for dt in weeks_by_mon_global[mon_iso]
                                if dt != d_iso and not schedule[dt].get("holiday") and _effective_slot_post(dt, mid_s, "pm") == "CONSULTATION"
                            ),
                            None,
                        )
                        if not d2:
                            continue
                        for u_id in cands_s:
                            if _can_swap_cs_global(d2, mid_s, u_id, allowed_list):
                                _exec_swap_cs_global(d2, mid_s, u_id)
                                _exec_swap_cs_global(d_iso, "noe", mid_s)
                                sw_n = True
                                break
                        if sw_n:
                            break
                    if sw_n:
                        break

    # 1) Éliminer les semaines avec >= 2 consultations pour un même interne
    for mon_iso in unlocked_mons_global:
        for _ in range(10):
            sw = False
            for allowed_list in (("LECTURE",), ("LECTURE", "ECHO", "SCAN ACHARD", "TDM OLLIER DIAG")):
                for over_id in all_iids_global:
                    if _week_cs_cnt(mon_iso, over_id) < 2:
                        continue
                    under_cands = sorted(
                        [u for u in all_iids_global if u != over_id and _week_cs_cnt(mon_iso, u) == 0 and not (u == "noe" and mon_iso < "2027-03-01")],
                        key=lambda x: _total_cs_cnt(x) - (3 if x == "noe" else 9),
                    )
                    for under_id in under_cands:
                        for d_iso in weeks_by_mon_global[mon_iso]:
                            if _can_swap_cs_global(d_iso, over_id, under_id, allowed_list):
                                _exec_swap_cs_global(d_iso, over_id, under_id)
                                sw = True
                                break
                        if sw:
                            break
                    if sw:
                        break
                if sw:
                    break
            if not sw:
                break

    # 2) Égaliser le total de CONSULTATION sur le semestre (cible 9 pour chacun des 5 seniors, 3 pour Noé sur les 2 derniers mois)
    target_cs_global = {iid: (3 if iid == "noe" else 9) for iid in all_iids_global}
    for _ in range(80):
        swapped_g = False
        counts_g = {iid: _total_cs_cnt(iid) for iid in all_iids_global}
        eff_g = {iid: counts_g[iid] - target_cs_global[iid] for iid in all_iids_global}
        sorted_iids_g = sorted(
            all_iids_global,
            key=lambda x: (eff_g[x], 1 if x == "noe" else 0, counts_g[x]),
            reverse=True,
        )
        if eff_g[sorted_iids_g[0]] - eff_g[sorted_iids_g[-1]] <= 1 and counts_g["noe"] <= 3:
            break
        for allowed_list in (("LECTURE",), ("LECTURE", "ECHO", "SCAN ACHARD", "TDM OLLIER DIAG")):
            for over_id in sorted_iids_g:
                for under_id in reversed(sorted_iids_g):
                    if under_id == over_id:
                        continue
                    if under_id == "noe" and counts_g["noe"] >= 3:
                        continue
                    diff_eff = eff_g[over_id] - eff_g[under_id]
                    if not (diff_eff >= 2 or (over_id == "noe" and counts_g["noe"] > 3 and diff_eff >= 1)):
                        continue
                    for mon_iso in unlocked_mons_global:
                        if under_id == "noe" and mon_iso < "2027-03-01":
                            continue
                        if _week_cs_cnt(mon_iso, over_id) == 0 or _week_cs_cnt(mon_iso, under_id) > 0:
                            continue
                        for d_iso in weeks_by_mon_global[mon_iso]:
                            if _can_swap_cs_global(d_iso, over_id, under_id, allowed_list):
                                _exec_swap_cs_global(d_iso, over_id, under_id)
                                swapped_g = True
                                break
                        if swapped_g:
                            break
                    if swapped_g:
                        break
                if swapped_g:
                    break
            if swapped_g:
                break
        if not swapped_g:
            break

    # 3) Équilibrer Mardi PM vs Vendredi PM sans dégrader le total par interne
    for _ in range(40):
        swapped_tf = False
        tot_c = {iid: _total_cs_cnt(iid) for iid in all_iids_global}
        tue_c = {iid: _total_cs_wd_cnt(iid, 1) for iid in all_iids_global}
        fri_c = {iid: _total_cs_wd_cnt(iid, 4) for iid in all_iids_global}
        for allowed_list in (("LECTURE",), ("LECTURE", "ECHO", "SCAN ACHARD", "TDM OLLIER DIAG")):
            for over_tue_id in all_iids_global:
                if tue_c[over_tue_id] < fri_c[over_tue_id]:
                    continue
                for over_fri_id in all_iids_global:
                    if over_fri_id == over_tue_id or fri_c[over_fri_id] < tue_c[over_fri_id]:
                        continue
                    if (tue_c[over_tue_id] - fri_c[over_tue_id]) + (fri_c[over_fri_id] - tue_c[over_fri_id]) < 4:
                        continue
                    eff_tue = tot_c[over_tue_id] - target_cs_global[over_tue_id]
                    eff_fri = tot_c[over_fri_id] - target_cs_global[over_fri_id]
                    if abs(eff_tue - eff_fri) > 1:
                        continue
                    for mon_tue in unlocked_mons_global:
                        if over_fri_id == "noe" and mon_tue < "2027-03-01":
                            continue
                        if _week_cs_cnt(mon_tue, over_tue_id) == 0 or _week_cs_cnt(mon_tue, over_fri_id) > 0:
                            continue
                        tue_day = next(
                            (
                                d for d in weeks_by_mon_global[mon_tue]
                                if datetime.date.fromisoformat(d).weekday() == 1
                                and _can_swap_cs_global(d, over_tue_id, over_fri_id, allowed_list)
                            ),
                            None,
                        )
                        if not tue_day:
                            continue
                        for mon_fri in unlocked_mons_global:
                            if over_tue_id == "noe" and mon_fri < "2027-03-01":
                                continue
                            if mon_fri == mon_tue or _week_cs_cnt(mon_fri, over_fri_id) == 0 or _week_cs_cnt(mon_fri, over_tue_id) > 0:
                                continue
                            fri_day = next(
                                (
                                    d for d in weeks_by_mon_global[mon_fri]
                                    if datetime.date.fromisoformat(d).weekday() == 4
                                    and _can_swap_cs_global(d, over_fri_id, over_tue_id, allowed_list)
                                ),
                                None,
                            )
                            if not fri_day:
                                continue
                            _exec_swap_cs_global(tue_day, over_tue_id, over_fri_id)
                            _exec_swap_cs_global(fri_day, over_fri_id, over_tue_id)
                            swapped_tf = True
                            break
                        if swapped_tf:
                            break
                    if swapped_tf:
                        break
                if swapped_tf:
                    break
            if swapped_tf:
                break
        if not swapped_tf:
            break

    # 4) Équilibrage global des vacations d'ÉCHOGRAPHIE (ECHO) et d'IRM (IRM Matin / IRM PM / Total IRM)
    #    ainsi que des Scanners diagnostiques (SCAN ACHARD / TDM OLLIER DIAG) sur les semaines non verrouillées :
    diag_postes_global = ("ECHO", "IRM 3T", "IRM 1,5T", "IRM", "SCAN ACHARD", "TDM OLLIER DIAG")

    def _week_irm_pm_cnt_global(mon_iso: str, iid: str) -> int:
        return sum(
            1
            for d_iso in weeks_by_mon_global[mon_iso]
            if not schedule[d_iso].get("holiday") and _effective_slot_post(d_iso, iid, "pm") == "IRM"
        )

    def _can_swap_diag_global(d_iso: str, h_key: str, i1: str, i2: str) -> bool:
        if d_iso == "2026-11-02" or schedule[d_iso].get("holiday"):
            return False
        if isinstance(custom_vacations.get(f"{d_iso}__{i1}"), dict) and custom_vacations[f"{d_iso}__{i1}"].get(h_key):
            return False
        if isinstance(custom_vacations.get(f"{d_iso}__{i2}"), dict) and custom_vacations[f"{d_iso}__{i2}"].get(h_key):
            return False
        p1 = _effective_slot_post(d_iso, i1, h_key)
        p2 = _effective_slot_post(d_iso, i2, h_key)
        if p1 == p2 or p1 not in diag_postes_global or p2 not in diag_postes_global:
            return False
        if "noe" in (i1, i2):
            sen_id = i2 if i1 == "noe" else i1
            p_noe = p1 if i1 == "noe" else p2
            if any(_effective_slot_post(d_iso, s_other, h_key) == p_noe for s_other in senior_iids_global if s_other != sen_id):
                return False
        other_h = "pm" if h_key == "am" else "am"
        if _is_same_poste_day_global(p2, _effective_slot_post(d_iso, i1, other_h)):
            return False
        if _is_same_poste_day_global(p1, _effective_slot_post(d_iso, i2, other_h)):
            return False
        if h_key == "pm":
            mon_iso = _mon_of_iso(d_iso)
            if p2 == "IRM" and p1 != "IRM" and _week_irm_pm_cnt_global(mon_iso, i1) >= 1:
                return False
            if p1 == "IRM" and p2 != "IRM" and _week_irm_pm_cnt_global(mon_iso, i2) >= 1:
                return False
        return True

    def _exec_swap_diag_global(d_iso: str, h_key: str, i1: str, i2: str) -> None:
        by_s = schedule[d_iso]["byInterne"]
        nk = "noteAm" if h_key == "am" else "notePm"
        p1, p2 = by_s[i1][h_key], by_s[i2][h_key]
        by_s[i1][h_key] = p2
        by_s[i1][nk] = f"Phase Socle ({p2})" if i1 == "noe" else ""
        by_s[i1]["note"] = " • ".join(x for x in (by_s[i1].get("noteAm", ""), by_s[i1].get("notePm", "")) if x)
        by_s[i2][h_key] = p1
        by_s[i2][nk] = f"Phase Socle ({p1})" if i2 == "noe" else ""
        by_s[i2]["note"] = " • ".join(x for x in (by_s[i2].get("noteAm", ""), by_s[i2].get("notePm", "")) if x)

    def _eval_global_diag_score(phase_two: bool = False) -> float:
        echo_am = {i: 0 for i in all_iids_global}
        echo_pm = {i: 0 for i in all_iids_global}
        irm_am = {i: 0 for i in all_iids_global}
        irm_3t = {i: 0 for i in all_iids_global}
        irm_15t = {i: 0 for i in all_iids_global}
        irm_pm = {i: 0 for i in all_iids_global}
        achard = {i: 0 for i in all_iids_global}
        ollier = {i: 0 for i in all_iids_global}
        w_pen = 0.0
        for mon_iso, d_list in weeks_by_mon_global.items():
            we = {i: 0 for i in all_iids_global}
            wi = {i: 0 for i in all_iids_global}
            for d_iso in d_list:
                if schedule[d_iso].get("holiday"):
                    continue
                for h_k in ("am", "pm"):
                    for i in all_iids_global:
                        v = _effective_slot_post(d_iso, i, h_k)
                        if v == "ECHO":
                            if h_k == "am":
                                echo_am[i] += 1
                            else:
                                echo_pm[i] += 1
                            we[i] += 1
                        elif v in ("IRM 3T", "IRM 1,5T") and h_k == "am":
                            irm_am[i] += 1
                            if v == "IRM 3T":
                                irm_3t[i] += 1
                            else:
                                irm_15t[i] += 1
                            wi[i] += 1
                        elif v == "IRM" and h_k == "pm":
                            irm_pm[i] += 1
                            wi[i] += 1
                        elif v == "SCAN ACHARD":
                            achard[i] += 1
                        elif v == "TDM OLLIER DIAG":
                            ollier[i] += 1
            me = sum(we.values()) / len(all_iids_global)
            mi = sum(wi.values()) / len(all_iids_global)
            w_pen += sum((we[i] - me) ** 2 for i in all_iids_global) + sum((wi[i] - mi) ** 2 for i in all_iids_global)

        def _var_g(vals: list[int | float]) -> float:
            m = sum(vals) / len(vals)
            return sum((x - m) ** 2 for x in vals)

        echo_tot = [echo_am[i] + echo_pm[i] for i in all_iids_global]
        irm_tot = [irm_am[i] + irm_pm[i] for i in all_iids_global]
        if phase_two:
            return (
                80.0 * _var_g(echo_tot)
                + 80.0 * _var_g(irm_tot)
                + 25.0 * _var_g(list(irm_am.values()))
                + 25.0 * _var_g(list(irm_pm.values()))
                + 4.0 * _var_g(list(echo_am.values()))
                + 4.0 * _var_g(list(echo_pm.values()))
                + 3.0 * _var_g(list(irm_3t.values()))
                + 3.0 * _var_g(list(irm_15t.values()))
                + 12.0 * _var_g(list(achard.values()))
                + 12.0 * _var_g(list(ollier.values()))
                + 4.0 * _var_g([achard[i] + ollier[i] for i in all_iids_global])
                + 1.5 * w_pen
            )
        return (
            16.0 * _var_g(echo_tot)
            + 16.0 * _var_g(irm_tot)
            + 10.0 * _var_g(list(irm_am.values()))
            + 10.0 * _var_g(list(irm_pm.values()))
            + 3.0 * _var_g(list(echo_am.values()))
            + 3.0 * _var_g(list(echo_pm.values()))
            + 2.0 * _var_g(list(irm_3t.values()))
            + 2.0 * _var_g(list(irm_15t.values()))
            + 4.0 * _var_g([achard[s] for s in senior_iids_global])
            + 4.0 * _var_g([ollier[s] for s in senior_iids_global])
            + 1.5 * _var_g(list(achard.values()))
            + 1.5 * _var_g(list(ollier.values()))
            + 1.5 * w_pen
        )

    for _ in range(120):
        improved_g = False
        cur_score_g = _eval_global_diag_score(False)
        for mon_iso in unlocked_mons_global:
            for d_iso in weeks_by_mon_global[mon_iso]:
                if schedule[d_iso].get("holiday"):
                    continue
                for h_k in ("am", "pm"):
                    for idx1 in range(len(all_iids_global)):
                        for idx2 in range(idx1 + 1, len(all_iids_global)):
                            i1, i2 = all_iids_global[idx1], all_iids_global[idx2]
                            if _can_swap_diag_global(d_iso, h_k, i1, i2):
                                _exec_swap_diag_global(d_iso, h_k, i1, i2)
                                new_score_g = _eval_global_diag_score(False)
                                if new_score_g < cur_score_g - 1e-6:
                                    cur_score_g = new_score_g
                                    improved_g = True
                                else:
                                    _exec_swap_diag_global(d_iso, h_k, i1, i2)
        if not improved_g:
            break

    # 4bis) Équilibrage global des vacations de LECTURE et de SCAN ACHARD (notamment pour Noé) :
    def _total_lec_cnt(iid: str) -> int:
        return sum(
            1
            for d_iso, d_obj in schedule.items()
            if not d_obj.get("holiday")
            for h in ("am", "pm")
            if _effective_slot_post(d_iso, iid, h) == "LECTURE"
        )

    def _total_ach_cnt(iid: str) -> int:
        return sum(
            1
            for d_iso, d_obj in schedule.items()
            if not d_obj.get("holiday")
            for h in ("am", "pm")
            if _effective_slot_post(d_iso, iid, h) == "SCAN ACHARD"
        )

    def _week_lec_cnt(mon_iso: str, iid: str) -> int:
        return sum(
            1
            for d_iso in weeks_by_mon_global[mon_iso]
            if not schedule[d_iso].get("holiday")
            for h in ("am", "pm")
            if _effective_slot_post(d_iso, iid, h) == "LECTURE"
        )

    def _week_ach_cnt(mon_iso: str, iid: str) -> int:
        return sum(
            1
            for d_iso in weeks_by_mon_global[mon_iso]
            if not schedule[d_iso].get("holiday")
            for h in ("am", "pm")
            if _effective_slot_post(d_iso, iid, h) == "SCAN ACHARD"
        )

    # A) Transférer des vacations de SCAN ACHARD de Noé vers LECTURE (en échange avec un senior en LECTURE)
    for _ in range(15):
        lec_c = {i: _total_lec_cnt(i) for i in all_iids_global}
        ach_c = {i: _total_ach_cnt(i) for i in all_iids_global}
        if lec_c["noe"] >= 10:
            break
        best_cand = None
        best_score = -999999.0
        for mon_iso in unlocked_mons_global:
            if _week_lec_cnt(mon_iso, "noe") >= 1:
                continue
            noe_w_ach = _week_ach_cnt(mon_iso, "noe")
            for d_iso in weeks_by_mon_global[mon_iso]:
                if d_iso == "2026-11-02" or schedule[d_iso].get("holiday"):
                    continue
                if datetime.date.fromisoformat(d_iso).weekday() not in (1, 4):
                    continue
                if isinstance(custom_vacations.get(f"{d_iso}__noe"), dict) and custom_vacations[f"{d_iso}__noe"].get("pm"):
                    continue
                if _effective_slot_post(d_iso, "noe", "pm") != "SCAN ACHARD":
                    continue
                if _is_same_poste_day_global(_effective_slot_post(d_iso, "noe", "am"), "LECTURE"):
                    continue
                for s_id in senior_iids_global:
                    if isinstance(custom_vacations.get(f"{d_iso}__{s_id}"), dict) and custom_vacations[f"{d_iso}__{s_id}"].get("pm"):
                        continue
                    if _effective_slot_post(d_iso, s_id, "pm") != "LECTURE":
                        continue
                    if _is_same_poste_day_global(_effective_slot_post(d_iso, s_id, "am"), "SCAN ACHARD"):
                        continue
                    if any(_effective_slot_post(d_iso, o_id, "pm") == "SCAN ACHARD" for o_id in senior_iids_global if o_id != s_id):
                        continue
                    sc = 10.0 * lec_c[s_id] - 6.0 * ach_c[s_id] + 3.0 * noe_w_ach - 2.0 * _week_ach_cnt(mon_iso, s_id)
                    if sc > best_score:
                        best_score = sc
                        best_cand = (d_iso, s_id)
        if not best_cand:
            break
        d_sw, s_sw = best_cand
        by_s = schedule[d_sw]["byInterne"]
        by_s["noe"]["pm"] = "LECTURE"
        by_s["noe"]["notePm"] = _format_pm_note_global(d_sw, "noe", "LECTURE")
        by_s["noe"]["note"] = " • ".join(x for x in (by_s["noe"].get("noteAm", ""), by_s["noe"].get("notePm", "")) if x)
        by_s[s_sw]["pm"] = "SCAN ACHARD"
        by_s[s_sw]["notePm"] = _format_pm_note_global(d_sw, s_sw, "SCAN ACHARD")
        by_s[s_sw]["note"] = " • ".join(x for x in (by_s[s_sw].get("noteAm", ""), by_s[s_sw].get("notePm", "")) if x)

    # B) Égaliser les LECTURE entre tous les internes (cible ~8-9 chacun)
    for _ in range(30):
        lec_c = {i: _total_lec_cnt(i) for i in all_iids_global}
        ach_c = {i: _total_ach_cnt(i) for i in all_iids_global}
        swapped_l = False
        over_l = sorted([i for i in all_iids_global if lec_c[i] >= (10 if i == "noe" else 9)], key=lambda x: (-lec_c[x], ach_c[x]))
        under_l = sorted([i for i in all_iids_global if lec_c[i] <= 7], key=lambda x: (lec_c[x], -ach_c[x]))
        for o_id in over_l:
            for u_id in under_l:
                if lec_c[o_id] - lec_c[u_id] < 1 or (lec_c[o_id] - lec_c[u_id] == 1 and not (o_id != "noe" and lec_c[o_id] >= 9 and lec_c[u_id] <= 7)):
                    continue
                for donor_p in ("SCAN ACHARD", "ECHO", "TDM OLLIER DIAG"):
                    for mon_iso in unlocked_mons_global:
                        if _week_lec_cnt(mon_iso, u_id) >= 1:
                            continue
                        for d_iso in weeks_by_mon_global[mon_iso]:
                            if d_iso == "2026-11-02" or schedule[d_iso].get("holiday"):
                                continue
                            if datetime.date.fromisoformat(d_iso).weekday() not in (1, 4):
                                continue
                            if isinstance(custom_vacations.get(f"{d_iso}__{o_id}"), dict) and custom_vacations[f"{d_iso}__{o_id}"].get("pm"):
                                continue
                            if isinstance(custom_vacations.get(f"{d_iso}__{u_id}"), dict) and custom_vacations[f"{d_iso}__{u_id}"].get("pm"):
                                continue
                            if _effective_slot_post(d_iso, o_id, "pm") != "LECTURE" or _effective_slot_post(d_iso, u_id, "pm") != donor_p:
                                continue
                            if _is_same_poste_day_global(_effective_slot_post(d_iso, o_id, "am"), donor_p):
                                continue
                            if _is_same_poste_day_global(_effective_slot_post(d_iso, u_id, "am"), "LECTURE"):
                                continue
                            if "noe" in (o_id, u_id):
                                if any(_effective_slot_post(d_iso, k, "pm") == donor_p for k in all_iids_global if k not in (o_id, u_id)):
                                    continue
                            by_s = schedule[d_iso]["byInterne"]
                            by_s[o_id]["pm"] = donor_p
                            by_s[o_id]["notePm"] = _format_pm_note_global(d_iso, o_id, donor_p)
                            by_s[o_id]["note"] = " • ".join(x for x in (by_s[o_id].get("noteAm", ""), by_s[o_id].get("notePm", "")) if x)
                            by_s[u_id]["pm"] = "LECTURE"
                            by_s[u_id]["notePm"] = _format_pm_note_global(d_iso, u_id, "LECTURE")
                            by_s[u_id]["note"] = " • ".join(x for x in (by_s[u_id].get("noteAm", ""), by_s[u_id].get("notePm", "")) if x)
                            swapped_l = True
                            break
                        if swapped_l:
                            break
                    if swapped_l:
                        break
                if swapped_l:
                    break
            if swapped_l:
                break
        if not swapped_l:
            break

    # 4ter) Second passage d'équilibrage diagnostique intégrant le lissage SCAN ACHARD / TDM OLLIER DIAG :
    for _ in range(120):
        improved_g2 = False
        cur_score_g2 = _eval_global_diag_score(True)
        for mon_iso in unlocked_mons_global:
            for d_iso in weeks_by_mon_global[mon_iso]:
                if schedule[d_iso].get("holiday"):
                    continue
                for h_k in ("am", "pm"):
                    for idx1 in range(len(all_iids_global)):
                        for idx2 in range(idx1 + 1, len(all_iids_global)):
                            i1, i2 = all_iids_global[idx1], all_iids_global[idx2]
                            if _can_swap_diag_global(d_iso, h_k, i1, i2):
                                _exec_swap_diag_global(d_iso, h_k, i1, i2)
                                new_score_g2 = _eval_global_diag_score(True)
                                if new_score_g2 < cur_score_g2 - 1e-6:
                                    cur_score_g2 = new_score_g2
                                    improved_g2 = True
                                else:
                                    _exec_swap_diag_global(d_iso, h_k, i1, i2)
        if not improved_g2:
            break

    # 4ter-bis) Second passage LECTURE <-> SCAN ACHARD après le lissage diagnostique :
    for _ in range(15):
        lec_c = {i: _total_lec_cnt(i) for i in all_iids_global}
        ach_c = {i: _total_ach_cnt(i) for i in all_iids_global}
        if lec_c["noe"] >= 9:
            break
        best_cand = None
        best_score = -999999.0
        for mon_iso in unlocked_mons_global:
            if _week_lec_cnt(mon_iso, "noe") >= 1:
                continue
            noe_w_ach = _week_ach_cnt(mon_iso, "noe")
            for d_iso in weeks_by_mon_global[mon_iso]:
                if d_iso == "2026-11-02" or schedule[d_iso].get("holiday"):
                    continue
                if datetime.date.fromisoformat(d_iso).weekday() not in (1, 4):
                    continue
                if isinstance(custom_vacations.get(f"{d_iso}__noe"), dict) and custom_vacations[f"{d_iso}__noe"].get("pm"):
                    continue
                if _effective_slot_post(d_iso, "noe", "pm") != "SCAN ACHARD":
                    continue
                if _is_same_poste_day_global(_effective_slot_post(d_iso, "noe", "am"), "LECTURE"):
                    continue
                for s_id in senior_iids_global:
                    if isinstance(custom_vacations.get(f"{d_iso}__{s_id}"), dict) and custom_vacations[f"{d_iso}__{s_id}"].get("pm"):
                        continue
                    if _effective_slot_post(d_iso, s_id, "pm") != "LECTURE":
                        continue
                    if _is_same_poste_day_global(_effective_slot_post(d_iso, s_id, "am"), "SCAN ACHARD"):
                        continue
                    if any(_effective_slot_post(d_iso, o_id, "pm") == "SCAN ACHARD" for o_id in senior_iids_global if o_id != s_id):
                        continue
                    sc = 10.0 * lec_c[s_id] - 6.0 * ach_c[s_id] + 3.0 * noe_w_ach - 2.0 * _week_ach_cnt(mon_iso, s_id)
                    if sc > best_score:
                        best_score = sc
                        best_cand = (d_iso, s_id)
        if not best_cand:
            break
        d_sw, s_sw = best_cand
        by_s = schedule[d_sw]["byInterne"]
        by_s["noe"]["pm"] = "LECTURE"
        by_s["noe"]["notePm"] = _format_pm_note_global(d_sw, "noe", "LECTURE")
        by_s["noe"]["note"] = " • ".join(x for x in (by_s["noe"].get("noteAm", ""), by_s["noe"].get("notePm", "")) if x)
        by_s[s_sw]["pm"] = "SCAN ACHARD"
        by_s[s_sw]["notePm"] = _format_pm_note_global(d_sw, s_sw, "SCAN ACHARD")
        by_s[s_sw]["note"] = " • ".join(x for x in (by_s[s_sw].get("noteAm", ""), by_s[s_sw].get("notePm", "")) if x)

    for _ in range(30):
        lec_c = {i: _total_lec_cnt(i) for i in all_iids_global}
        ach_c = {i: _total_ach_cnt(i) for i in all_iids_global}
        swapped_l = False
        over_l = sorted([i for i in all_iids_global if lec_c[i] >= (10 if i == "noe" else 9)], key=lambda x: (-lec_c[x], ach_c[x]))
        under_l = sorted([i for i in all_iids_global if lec_c[i] <= 8], key=lambda x: (lec_c[x], -ach_c[x]))
        for o_id in over_l:
            for u_id in under_l:
                if lec_c[o_id] - lec_c[u_id] < 1 or (lec_c[o_id] - lec_c[u_id] == 1 and not (o_id != "noe" and lec_c[o_id] >= 9 and lec_c[u_id] <= 7)):
                    continue
                for donor_p in ("SCAN ACHARD", "ECHO", "TDM OLLIER DIAG"):
                    for mon_iso in unlocked_mons_global:
                        if _week_lec_cnt(mon_iso, u_id) >= 1:
                            continue
                        for d_iso in weeks_by_mon_global[mon_iso]:
                            if d_iso == "2026-11-02" or schedule[d_iso].get("holiday"):
                                continue
                            if datetime.date.fromisoformat(d_iso).weekday() not in (1, 4):
                                continue
                            if isinstance(custom_vacations.get(f"{d_iso}__{o_id}"), dict) and custom_vacations[f"{d_iso}__{o_id}"].get("pm"):
                                continue
                            if isinstance(custom_vacations.get(f"{d_iso}__{u_id}"), dict) and custom_vacations[f"{d_iso}__{u_id}"].get("pm"):
                                continue
                            if _effective_slot_post(d_iso, o_id, "pm") != "LECTURE" or _effective_slot_post(d_iso, u_id, "pm") != donor_p:
                                continue
                            if _is_same_poste_day_global(_effective_slot_post(d_iso, o_id, "am"), donor_p):
                                continue
                            if _is_same_poste_day_global(_effective_slot_post(d_iso, u_id, "am"), "LECTURE"):
                                continue
                            if "noe" in (o_id, u_id):
                                if any(_effective_slot_post(d_iso, k, "pm") == donor_p for k in all_iids_global if k not in (o_id, u_id)):
                                    continue
                            by_s = schedule[d_iso]["byInterne"]
                            by_s[o_id]["pm"] = donor_p
                            by_s[o_id]["notePm"] = _format_pm_note_global(d_iso, o_id, donor_p)
                            by_s[o_id]["note"] = " • ".join(x for x in (by_s[o_id].get("noteAm", ""), by_s[o_id].get("notePm", "")) if x)
                            by_s[u_id]["pm"] = "LECTURE"
                            by_s[u_id]["notePm"] = _format_pm_note_global(d_iso, u_id, "LECTURE")
                            by_s[u_id]["note"] = " • ".join(x for x in (by_s[u_id].get("noteAm", ""), by_s[u_id].get("notePm", "")) if x)
                            swapped_l = True
                            break
                        if swapped_l:
                            break
                    if swapped_l:
                        break
                if swapped_l:
                    break
            if swapped_l:
                break
        if not swapped_l:
            break

    # 4quater) Lissage fin GESTES (C) <-> SCAN ACHARD entre seniors lorsque l'écart combiné est >= 2 :
    for _ in range(10):
        gest_c = {
            s: sum(
                1
                for d_iso, d_obj in schedule.items()
                if not d_obj.get("holiday")
                for h_k in ("am", "pm")
                if _effective_slot_post(d_iso, s, h_k) in ("GESTES (C)", "ALLURA")
            )
            for s in senior_iids_global
        }
        ach_c = {s: _total_ach_cnt(s) for s in senior_iids_global}
        swapped_ga = False
        for over_g in sorted(senior_iids_global, key=lambda s: -gest_c[s]):
            for under_g in sorted(senior_iids_global, key=lambda s: gest_c[s]):
                if gest_c[over_g] - gest_c[under_g] < 2 or ach_c[under_g] - ach_c[over_g] < 2:
                    continue
                for mon_iso in unlocked_mons_global:
                    w_g_u = sum(
                        1
                        for d_iso in weeks_by_mon_global[mon_iso]
                        if not schedule[d_iso].get("holiday")
                        for h_k in ("am", "pm")
                        if _effective_slot_post(d_iso, under_g, h_k) in ("GESTES (C)", "ALLURA")
                    )
                    if w_g_u >= 2:
                        continue
                    for d_iso in weeks_by_mon_global[mon_iso]:
                        if d_iso == "2026-11-02" or schedule[d_iso].get("holiday"):
                            continue
                        for h_k in ("am", "pm"):
                            if isinstance(custom_vacations.get(f"{d_iso}__{over_g}"), dict) and custom_vacations[f"{d_iso}__{over_g}"].get(h_k):
                                continue
                            if isinstance(custom_vacations.get(f"{d_iso}__{under_g}"), dict) and custom_vacations[f"{d_iso}__{under_g}"].get(h_k):
                                continue
                            if _effective_slot_post(d_iso, over_g, h_k) != "GESTES (C)" or _effective_slot_post(d_iso, under_g, h_k) != "SCAN ACHARD":
                                continue
                            other_h = "pm" if h_k == "am" else "am"
                            if _is_same_poste_day_global(_effective_slot_post(d_iso, over_g, other_h), "SCAN ACHARD"):
                                continue
                            if _is_same_poste_day_global(_effective_slot_post(d_iso, under_g, other_h), "GESTES (C)"):
                                continue
                            by_s = schedule[d_iso]["byInterne"]
                            nk = "noteAm" if h_k == "am" else "notePm"
                            by_s[over_g][h_k] = "SCAN ACHARD"
                            by_s[over_g][nk] = ""
                            by_s[over_g]["note"] = " • ".join(x for x in (by_s[over_g].get("noteAm", ""), by_s[over_g].get("notePm", "")) if x)
                            by_s[under_g][h_k] = "GESTES (C)"
                            by_s[under_g][nk] = ""
                            by_s[under_g]["note"] = " • ".join(x for x in (by_s[under_g].get("noteAm", ""), by_s[under_g].get("notePm", "")) if x)
                            swapped_ga = True
                            break
                        if swapped_ga:
                            break
                    if swapped_ga:
                        break
                if swapped_ga:
                    break
            if swapped_ga:
                break
        if not swapped_ga:
            break

    for mon_iso in unlocked_mons_global:
        for d_iso in weeks_by_mon_global[mon_iso]:
            rebuild_day_lists(schedule[d_iso])

    presentations = build_initial_presentations(schedule)
    meetings = build_service_meetings()
    recurring_staffs = build_recurring_staffs()
    phone_directory = build_phone_directory()

    # Préserver les modifications manuelles de présentations (intervenant, sujet) depuis le cloud/fichier
    pres_map = {p["id"]: p for p in presentations if p.get("id")}
    for src in saved_sources:
        if isinstance(src, dict) and isinstance(src.get("presentations"), list):
            for sv in src["presentations"]:
                if isinstance(sv, dict) and sv.get("id") in pres_map:
                    bp = pres_map[sv["id"]]
                    if bp.get("type") == "cours_internes":
                        if sv.get("userEditedCours"):
                            if sv.get("chefIntervenant") is not None:
                                bp["chefIntervenant"] = sv["chefIntervenant"]
                            if sv.get("coursChef") is not None:
                                bp["coursChef"] = sv["coursChef"]
                            if sv.get("sujet") is not None:
                                bp["sujet"] = sv["sujet"]
                            bp["pasDeCours"] = bp.get("coursChef") == "Pas de cours" or bp.get("sujet") == "Pas de cours"
                            bp["userEditedCours"] = True
                    else:
                        suj = sv.get("sujet", "")
                        if suj and suj != "Dossier ostéo-articulaire inaugural (choix libre)":
                            bp["sujet"] = suj
                        elif sv.get("userEditedPres") and suj == "":
                            bp["sujet"] = ""
                        if sv.get("userEditedPres"):
                            if sv.get("isUserSwap") or sv.get("updatedAt") or (bp.get("date"), sv.get("interneId")) not in rg_pairs or suj:
                                if sv.get("interneId"):
                                    bp["interneId"] = sv["interneId"]
                                if sv.get("interneName"):
                                    bp["interneName"] = sv["interneName"]
                                bp["userEditedPres"] = True
                                if sv.get("isUserSwap"):
                                    bp["isUserSwap"] = True
                                if sv.get("updatedAt"):
                                    bp["updatedAt"] = sv["updatedAt"]
    presentations = sorted(pres_map.values(), key=lambda x: (x.get("date", ""), x.get("type", "")))

    return {
        "version": "2.0.0",
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
                "IRM": "IRM Matin (3T / 1,5T) : dès 07h45 • IRM Après-midi (séparée) : dès 13h00 (max 1/semaine par interne)",
                "ECHO": "Matin : dès 09h00 • Après-midi : dès 14h00",
                "GESTES_C": "Matin : dès 09h00 • Après-midi : dès 14h00",
                "TDM_SAU": "08h00 – 18h30 (Scanner des Urgences : début à 08h00, fin à 18h30)",
                "CONSULTATION": "Consultation Internes le Mardi après-midi et le Vendredi après-midi (14h00 – 15h00)",
                "LECTURE": "Lecture / Relecture le Mardi après-midi (Relecture systématique avec Pr Drapé) et le Vendredi après-midi (14h00 – 16h00)",
            },
            "rules": [
                "Interdiction de faire le même poste toute la journée : un interne ne peut jamais être affecté au même poste le matin et l'après-midi d'une même journée.",
                "IRM d'après-midi séparées des IRM du matin (3T / 1,5T) : un interne ne peut pas avoir plus d'une IRM d'après-midi par semaine (sauf exception en cas de congés / RG).",
                "Horaires des vacations : Matin — IRM à 07h45, Scanner des U (TDM SAU) de 08h00 à 18h30, Échographie (US) et Poste C (Gestes) à 09h00 • Après-midi — IRM à 13h00, Échographie (US) et Poste C (Gestes) à 14h00, Consultation (CS) de 14h00 à 15h00, Lecture / Relecture de 14h00 à 16h00.",
                "Séparation des vacations de Lecture (LECTURE : 14h00 – 16h00) et de Consultation d'internes (CONSULTATION : 14h00 – 15h00) : les consultations d'internes ont lieu le mardi après-midi et le vendredi après-midi, séparément des vacations de lecture/relecture.",
                "Séparation des 3 scanners du service : Scanner SAU (TDM Ollier 4 — Urgences), Scanner Achard (TDM Achard 1 — Diagnostique & Interventionnel) et Scanner Ollier (TDM Ollier 3 — Diagnostique).",
                "Quota hebdomadaire de Scanner SAU (TDM SAU) : 2 SAU par semaine pour chacun des 5 internes seniors (Gabriel, Marwane, Milan, Nathanaël, Oussama), et 3 SAU par semaine pour Noé (Phase Socle : imposé en solo sans doublure exceptionnellement chaque mardi matin avec Dr Macil HAMADOUCHE, + 2 créneaux en binôme avec un co-interne senior sur le reste de la semaine) — plus uniquement à titre exceptionnel (remplacement congés / RG).",
                "Permanence Scanner SAU (un interne senior matin et après-midi, sauf le mardi matin assuré en solo par Noé avec Dr Macil HAMADOUCHE) + vacations obligatoires prioritaires : Écho lundi matin, IRM lundi après-midi, Poste C, IRM 3T et IRM 1,5T mardi matin, Lecture/Relecture mardi après-midi, IRM 3T, IRM 1,5T et Scanner Ollier mercredi matin (+ Écho mercredi matin à partir de décembre), Poste C / IRM / Scanner Achard / Écho mercredi après-midi, Écho et Poste C jeudi matin, IRM jeudi après-midi, IRM 3T vendredi matin.",
                "Planning officiel des gardes des internes Hiver 2026–2027 intégré : Repos de garde (RG) systématique le lendemain de chaque garde (avec maintien des 2 demi-offs hebdomadaires et couverture garantie du TDM SAU et des vacations obligatoires).",
                "Maximum 2 demi-offs (1/2 journée libre) par semaine par interne (jamais plus de 2 demi-offs sur une même semaine, et jamais de demi-off le mardi après-midi ni le vendredi après-midi) : à partir du 09/11/2026, demi-journée off fixe pour les demandeurs dans la mesure du possible (Lundi matin pour Oussama, Mardi matin pour Gabriel, Jeudi matin pour Marwane) + 1 autre demi-journée off posée en fonction des vacations obligatoires.",
                "Présentations des internes (Cas du Mardi & Biblio du Vendredi) : début en semaine 2 (mardi 10/11/2026 pour les Cas, vendredi 13/11/2026 pour la Biblio) avec espacement garanti d'au moins 2,5 à 3,5 semaines (18 à 24 jours minimum) entre deux présentations d'un même interne et 6 semaines entre deux Cas ou deux Biblios.",
                "Pas plus de 2 internes absents (CA / CF) en même temps. Toutes les vacances sont validées par le Chef dans l'Espace Chef.",
                "Notification automatique dans l'Espace Chef lorsqu'un jour bloque (TDM SAU découvert, >2 absents, Relecture Mardi PM, cours/biblio sans interne) et qu'une décision doit être prise.",
                "Pas d'interne en Échographie avec le Dr Fabrice THÉVENIN sur le mois de novembre (mercredi matin), puis vacation obligatoire à partir de décembre.",
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
    var lock = LockService.getScriptLock();
    if (!lock.tryLock(30000)) return {{ status: 'busy' }};
    try {{
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
        if (baseP.type === 'cours_internes') {{
          if (sv.userEditedCours) {{
            var mergedCours = Object.assign({{}}, baseP);
            if (sv.chefIntervenant !== undefined) mergedCours.chefIntervenant = sv.chefIntervenant;
            if (sv.coursChef !== undefined) mergedCours.coursChef = sv.coursChef;
            if (sv.sujet !== undefined) mergedCours.sujet = sv.sujet;
            mergedCours.userEditedCours = true;
            if (sv.updatedAt) mergedCours.updatedAt = sv.updatedAt;
            return mergedCours;
          }}
          return baseP;
        }}
        var merged = Object.assign({{}}, baseP);
        if (sv.sujet && sv.sujet !== 'Dossier ostéo-articulaire inaugural (choix libre)') {{
          merged.sujet = sv.sujet;
        }} else if (sv.userEditedPres && sv.sujet === '') {{
          merged.sujet = '';
        }}
        if (sv.userEditedPres && (sv.isUserSwap || sv.updatedAt || !(sv.interneId && rgPairs[baseP.date + '__' + sv.interneId] && !sv.sujet))) {{
          if (sv.interneId) merged.interneId = sv.interneId;
          if (sv.interneName) merged.interneName = sv.interneName;
          merged.userEditedPres = true;
          if (sv.isUserSwap) merged.isUserSwap = true;
          if (sv.updatedAt) merged.updatedAt = sv.updatedAt;
        }}
        return merged;
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
    }} finally {{
      try {{ lock.releaseLock(); }} catch (relErr) {{}}
    }}
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
