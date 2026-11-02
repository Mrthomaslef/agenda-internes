#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de l'application web (PWA) autonome pour les Internes du Service de Radiologie B
Hôpital Cochin (AP-HP) — Semestre Hiver 2026–2027 (Pr A. Feydy)
Répertoire : /Users/thomaslefevre/Documents/Agendainterventionnel/agenda-internes/
Aucune donnée patient n'est incluse ni autorisée dans cette application.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import stat

from build_internes_data import (
    BASE_DIR,
    CLOUD_PROP_KEY,
    DATA_FILE,
    ICON_FILE,
    INDEX_FILE,
    INTERNES_SHEET_ID,
    LAUNCHER_FILE,
    MANIFEST_FILE,
    SW_FILE,
    WEBHOOK_URL,
    assert_zero_patient_data,
    build_full_dataset,
    push_to_prod_github,
    sync_initial_state_to_cloud,
)


def js_json(obj) -> str:
    return (
        json.dumps(obj, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />
  <meta name="apple-mobile-web-app-title" content="Planning Radio B" />
  <meta name="application-name" content="Planning Radio B — Cochin" />
  <meta name="theme-color" content="#F8FAFC" />
  <link rel="manifest" href="manifest.json?v=3" />
  <link rel="icon" type="image/svg+xml" href="icon.svg?v=3" />
  <link rel="apple-touch-icon" href="icon.svg?v=3" />
  <title>Radio B Cochin — Planning Internes & Chefs</title>
  <style>
    :root {
      --bg: #F8FAFC;
      --bg-card: #FFFFFF;
      --bg-elevated: #F1F5F9;
      --border: #E2E8F0;
      --text: #0F172A;
      --text-muted: #64748B;
      --primary: #0284C7;
      --primary-dark: #0369A1;
      --tdm: #D97706;
      --irm: #7C3AED;
      --echo: #0D9488;
      --gestes: #E11D48;
      --cs: #2563EB;
      --off: #64748B;
      --vac: #16A34A;
      --rg: #DC2626;
      --safe-top: env(safe-area-inset-top, 0px);
      --safe-bottom: env(safe-area-inset-bottom, 0px);
    }

    * {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    html, body {
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.4;
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* En-tête épuré */
    .app-header {
      position: sticky;
      top: 0;
      z-index: 100;
      padding: calc(var(--safe-top) + 10px) 16px 10px;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
    }

    .header-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      max-width: 1120px;
      margin: 0 auto;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .brand-logo {
      width: 34px;
      height: 34px;
      border-radius: 9px;
      background: var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 13px;
      color: #fff;
      flex-shrink: 0;
    }

    .brand-title {
      font-size: 15px;
      font-weight: 800;
      color: #0F172A;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .brand-sub {
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .btn {
      border: 1px solid #CBD5E1;
      background: #FFFFFF;
      color: #0F172A;
      padding: 8px 13px;
      border-radius: 9px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      text-decoration: none;
      transition: background 0.15s ease, border-color 0.15s ease;
    }

    .btn:hover {
      background: #F1F5F9;
      border-color: #94A3B8;
    }

    .btn-sm {
      padding: 5px 10px;
      font-size: 12px;
      border-radius: 7px;
    }

    .btn-primary {
      background: var(--primary);
      border-color: var(--primary);
      color: #FFFFFF;
      font-weight: 700;
    }
    .btn-primary:hover {
      background: var(--primary-dark);
      border-color: var(--primary-dark);
      color: #FFFFFF;
    }

    /* Barre de sélection simple (2 listes déroulantes ou boutons clairs) */
    .selector-bar {
      max-width: 1120px;
      margin: 10px auto 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }

    .person-chips {
      display: flex;
      align-items: center;
      gap: 5px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: none;
      flex: 1;
    }
    .person-chips::-webkit-scrollbar { display: none; }

    .chip {
      border: 1px solid #CBD5E1;
      background: #FFFFFF;
      color: #334155;
      padding: 5px 11px;
      border-radius: 999px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .chip:hover {
      background: #F1F5F9;
    }

    .chip .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .chip.active {
      background: #E0F2FE;
      color: #0369A1;
      border-color: #0284C7;
      font-weight: 700;
    }

    /* Conteneur principal */
    .container {
      max-width: 1120px;
      margin: 0 auto;
      padding: 12px 16px calc(var(--safe-bottom) + 80px);
    }

    /* Bandeau résumé compact */
    .summary-strip {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 14px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    .summary-left {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .avatar-sm {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 12px;
      color: #fff;
      flex-shrink: 0;
    }

    .summary-title {
      font-size: 14px;
      font-weight: 800;
      color: #0F172A;
    }

    .summary-sub {
      font-size: 12.5px;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .summary-stats {
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 12.5px;
      color: var(--text-muted);
      flex-wrap: wrap;
    }

    .summary-stats strong {
      color: #0F172A;
      font-weight: 800;
    }

    /* Onglets principaux courts et lisibles */
    .main-tabs {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 4px;
      background: #E2E8F0;
      padding: 4px;
      border-radius: 11px;
      margin-bottom: 12px;
    }

    .tab-btn {
      border: none;
      background: transparent;
      color: #475569;
      padding: 8px 6px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease;
    }

    .tab-btn.active {
      background: #FFFFFF;
      color: #0F172A;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }

    /* Barre d'outils du planning */
    .planning-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }

    .segmented {
      display: inline-flex;
      background: #E2E8F0;
      border-radius: 9px;
      padding: 3px;
      gap: 2px;
    }

    .seg-btn {
      border: none;
      background: transparent;
      color: #475569;
      padding: 6px 11px;
      border-radius: 7px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
    }

    .seg-btn.active {
      background: #FFFFFF;
      color: #0F172A;
      font-weight: 700;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
    }

    .date-nav {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .date-label {
      font-size: 13.5px;
      font-weight: 800;
      min-width: 150px;
      text-align: center;
    }

    /* Jours de la semaine : Lun-Ven en grand + Sam/Dim en petit avec juste les gardes */
    .day-strip {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr)) repeat(2, minmax(0, 0.74fr));
      gap: 5px;
      margin-bottom: 10px;
      align-items: stretch;
    }

    .day-pill {
      padding: 6px 4px;
      border-radius: 9px;
      background: #FFFFFF;
      border: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 700;
      text-align: center;
      min-width: 0;
    }

    .day-pill .dp-top {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      white-space: nowrap;
      line-height: 1.15;
    }

    .day-pill .dp-dow {
      font-weight: 800;
      color: #0F172A;
    }

    .day-pill .dp-date {
      font-weight: 700;
      color: #475569;
      font-size: 11px;
    }

    .day-pill .dp-sub {
      font-size: 9.5px;
      font-weight: 700;
      color: #64748B;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      line-height: 1.1;
    }

    .day-pill.weekend-pill {
      padding: 4px 2px;
      background: #FFF5F5;
      border: 1px dashed #FCA5A5;
      border-radius: 8px;
    }

    .day-pill.weekend-pill .dp-dow {
      font-size: 9.5px;
      color: #991B1B;
      text-transform: uppercase;
    }

    .day-pill.weekend-pill .dp-date {
      font-size: 9px;
      color: #B91C1C;
    }

    .day-pill.weekend-pill .dp-garde {
      font-size: 9.5px;
      font-weight: 800;
      color: #B91C1C;
      background: #FEE2E2;
      border-radius: 4px;
      padding: 1px 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
      line-height: 1.15;
    }

    .day-pill.active {
      background: #E0F2FE;
      border-color: var(--primary);
      border-style: solid;
      color: #0369A1;
      box-shadow: 0 0 0 1px var(--primary);
    }

    .day-pill.active .dp-dow,
    .day-pill.active .dp-date {
      color: #0369A1;
    }

    /* Bandeau compact Samedi & Dimanche (Gardes uniquement) */
    .weekend-gardes-compact {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 6px;
      padding: 7px 10px;
      background: #FFF5F5;
      border-top: 1px dashed #FCA5A5;
    }

    .weekend-garde-mini {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      padding: 4px 8px;
      border-radius: 7px;
      background: #FFFFFF;
      border: 1px solid #FECACA;
      font-size: 11px;
      cursor: pointer;
      min-width: 0;
    }

    .weekend-garde-mini .wg-day {
      font-weight: 800;
      color: #7F1D1D;
      font-size: 10.5px;
      white-space: nowrap;
    }

    .weekend-garde-mini .wg-doc {
      font-weight: 800;
      color: #B91C1C;
      background: #FEE2E2;
      padding: 1px 6px;
      border-radius: 5px;
      font-size: 10.5px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* Grille 5 colonnes Lun-Ven pour Mon Planning */
    .perso-week-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
    }

    /* Badges de postes */
    .poste-pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      border: 1px solid transparent;
      white-space: nowrap;
    }

    .poste-tdm { background: #FEF3C7; color: #B45309; border-color: #FCD34D; }
    .poste-tdm-sau { background: #FEF3C7; color: #B45309; border-color: #FCD34D; }
    .poste-achard { background: #FFEDD5; color: #C2410C; border-color: #FDBA74; }
    .poste-tdm-ollier { background: #E0F2FE; color: #0369A1; border-color: #7DD3FC; }
    .poste-irm { background: #F3E8FF; color: #6D28D9; border-color: #D8B4FE; }
    .poste-echo { background: #CCFBF1; color: #0F766E; border-color: #5EEAD4; }
    .poste-gestes { background: #FFE4E6; color: #BE123C; border-color: #FDA4AF; }
    .poste-cs { background: #DBEAFE; color: #1D4ED8; border-color: #93C5FD; }
    .poste-off { background: #F1F5F9; color: #475569; border-color: #CBD5E1; }
    .poste-vac { background: #DCFCE7; color: #15803D; border-color: #86EFAC; }
    .poste-rg { background: #FEE2E2; color: #B91C1C; border-color: #FCA5A5; }
    .poste-closed {
      background: #FEF2F2;
      color: #B91C1C;
      border: 1px dashed #EF4444;
      font-weight: 700;
    }

    .tag-sm {
      display: inline-block;
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 800;
      background: #EDE9FE;
      color: #6D28D9;
      text-transform: uppercase;
    }

    .tag-dj {
      display: inline-block;
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 800;
      background: #DCFCE7;
      color: #15803D;
      border: 1px solid #86EFAC;
      text-transform: uppercase;
    }

    .pres-type-switcher {
      display: inline-flex;
      background: #F1F5F9;
      border: 1px solid #CBD5E1;
      border-radius: 7px;
      padding: 2px;
      gap: 2px;
      margin-top: 4px;
    }

    .pres-type-btn {
      border: none;
      background: transparent;
      color: #475569;
      padding: 3px 7px;
      border-radius: 5px;
      font-size: 10.5px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.12s ease;
    }

    .pres-type-btn:hover {
      background: #E2E8F0;
      color: #0F172A;
    }

    .pres-type-btn.active-cas {
      background: #F3E8FF;
      color: #6D28D9;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
    }

    .pres-type-btn.active-biblio {
      background: #FEF3C7;
      color: #B45309;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
    }

    .pres-type-btn.active-cours {
      background: #DBEAFE;
      color: #1D4ED8;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
    }

    .tag-binome {
      display: inline-block;
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 700;
      background: #FEF3C7;
      color: #B45309;
    }

    /* Cartes & Tableaux */
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 12px;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 10px;
      flex-wrap: wrap;
    }

    .card-title {
      font-size: 14px;
      font-weight: 800;
      color: #0F172A;
    }

    .week-table-wrap {
      overflow-x: auto;
      border-radius: 10px;
      border: 1px solid var(--border);
    }

    table.planning-table {
      width: 100%;
      border-collapse: collapse;
      min-width: 640px;
      background: #FFFFFF;
    }

    table.planning-table.week-5col {
      table-layout: fixed;
      min-width: 0;
      width: 100%;
    }

    table.planning-table.week-5col th.col-poste {
      width: 140px;
      vertical-align: middle;
    }

    table.planning-table.week-5col th.th-day-col {
      padding: 4px;
      background: #F1F5F9;
      vertical-align: middle;
      text-transform: none;
    }

    table.planning-table.week-5col th.th-day-col .day-pill {
      width: 100%;
      height: 100%;
      margin: 0;
      box-sizing: border-box;
      transition: all 0.12s ease;
    }

    table.planning-table.week-5col th.th-day-col .day-pill:hover {
      border-color: var(--primary);
      background: #F0F9FF;
    }

    table.planning-table.week-5col th.th-day-col .day-pill.active:hover {
      background: #E0F2FE;
    }

    .weekend-garde-mini:hover {
      border-color: #F87171;
      background: #FFF1F2;
    }

    .weekend-garde-mini.active {
      background: #E0F2FE;
      border-color: var(--primary);
      box-shadow: 0 0 0 1px var(--primary);
    }

    table.planning-table th,
    table.planning-table td {
      border-bottom: 1px solid var(--border);
      border-right: 1px solid var(--border);
      padding: 7px 9px;
      text-align: left;
      vertical-align: top;
      font-size: 12px;
    }

    table.planning-table th {
      background: #F8FAFC;
      color: #475569;
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
    }

    table.planning-table tr.period-divider td {
      background: #F1F5F9;
      color: #0F172A;
      font-weight: 800;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      padding: 5px 10px;
    }

    .interne-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 7px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 600;
      margin: 2px 3px 2px 0;
      background: #F8FAFC;
      color: #0F172A;
      border: 1px solid #CBD5E1;
      cursor: pointer;
    }
    .interne-badge:hover {
      background: #E2E8F0;
    }

    .interne-badge.highlight-me {
      background: #E0F2FE;
      color: #0369A1;
      border-color: var(--primary);
      font-weight: 800;
    }

    /* Grille mois */
    .month-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
    }

    /* ADAPTATION MOBILE : Semaine Lun-Ven entière à l'écran + Sam/Dim en petit avec juste les gardes */
    @media (max-width: 768px) {
      .container {
        padding: 8px 6px calc(var(--safe-bottom) + 74px);
      }
      .top-header {
        padding: 8px 10px;
      }
      .brand-title {
        font-size: 13.5px;
      }
      .brand-sub {
        display: none;
      }
      .brand > div:not(.brand-logo) {
        display: none;
      }
      .header-actions {
        gap: 5px;
        min-width: 0;
      }
      .header-actions .btn {
        padding: 6px 8px;
        font-size: 11.5px;
        white-space: nowrap;
      }
      .summary-strip {
        padding: 8px 10px;
        gap: 8px;
      }
      .main-tabs {
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 2px;
        padding: 3px;
      }
      .tab-btn {
        font-size: 11px;
        padding: 6px 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .planning-toolbar {
        gap: 5px;
      }
      .seg-btn {
        padding: 5px 7px;
        font-size: 11px;
      }
      .date-label {
        font-size: 12px;
        min-width: 115px;
      }
      .day-strip {
        grid-template-columns: repeat(5, minmax(0, 1fr)) repeat(2, minmax(0, 0.72fr));
        gap: 3px;
        margin-bottom: 8px;
      }
      .day-pill {
        padding: 4px 2px;
        border-radius: 7px;
        font-size: 10.5px;
      }
      .day-pill .dp-top {
        flex-direction: column;
        gap: 0px;
      }
      .day-pill .dp-dow {
        font-size: 10px;
      }
      .day-pill .dp-date {
        font-size: 9.5px;
      }
      .day-pill .dp-sub {
        font-size: 8px;
      }
      .day-pill.weekend-pill {
        padding: 3px 1px;
      }
      .day-pill.weekend-pill .dp-dow {
        font-size: 8.5px;
      }
      .day-pill.weekend-pill .dp-date {
        font-size: 8px;
      }
      .day-pill.weekend-pill .dp-garde {
        font-size: 8px;
        padding: 1px 2px;
      }
      table.planning-table.week-5col th.col-poste {
        width: 54px;
      }
      table.planning-table.week-5col th.th-day-col {
        padding: 2px 1.5px;
      }
      table.planning-table.week-5col th,
      table.planning-table.week-5col td {
        padding: 4px 2px;
        font-size: 9.5px;
        word-break: normal;
        overflow-wrap: anywhere;
        hyphens: auto;
      }
      table.planning-table.week-5col th {
        font-size: 9.5px;
        text-align: center;
      }
      table.planning-table.week-5col tr.period-divider td {
        font-size: 9.5px;
        padding: 4px 6px;
      }
      table.planning-table.week-5col .poste-pill {
        font-size: 8.5px;
        padding: 2px 3.5px;
        white-space: normal;
        line-height: 1.1;
      }
      table.planning-table.week-5col .poste-horaire-sub {
        font-size: 7.5px !important;
        line-height: 1.05;
      }
      /* Prénoms toujours sur une seule ligne : badge pleine largeur, tags masqués */
      table.planning-table.week-5col .interne-badge {
        display: flex;
        font-size: 8.5px;
        padding: 2px 2px;
        gap: 2px;
        margin: 0 0 2px 0;
        max-width: 100%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.15;
        letter-spacing: -0.01em;
      }
      table.planning-table.week-5col .interne-badge > span:first-of-type:not(.drag-grip),
      table.planning-table.week-5col .interne-badge .drag-grip + span {
        width: 4px !important;
        height: 4px !important;
        flex-shrink: 0;
      }
      table.planning-table.week-5col .interne-badge .tag-sm,
      table.planning-table.week-5col .interne-badge .tag-dj,
      table.planning-table.week-5col .interne-badge .tag-binome,
      table.planning-table.week-5col .interne-badge .drag-grip {
        display: none;
      }
      table.planning-table.week-5col .garde-dr {
        display: none;
      }
      table.planning-table.week-5col .garde-name {
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 8.5px;
      }
      .perso-week-grid {
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 3px;
      }
      .perso-week-grid .perso-day-card {
        padding: 5px 3px !important;
        border-radius: 8px !important;
      }
      .perso-week-grid .perso-day-card .poste-pill {
        font-size: 8.5px !important;
        padding: 2px 3px !important;
        white-space: normal !important;
        line-height: 1.1 !important;
      }
      .weekend-gardes-compact {
        padding: 5px 6px;
        gap: 4px;
      }
      .weekend-garde-mini {
        padding: 3px 6px;
        font-size: 9.5px;
      }
      .weekend-garde-mini .wg-day,
      .weekend-garde-mini .wg-doc {
        font-size: 9.5px;
      }
      .month-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    .month-cell {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 8px;
      min-height: 92px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      cursor: pointer;
    }

    .month-cell:hover {
      border-color: var(--primary);
    }

    .month-cell.today {
      border-color: var(--primary);
      background: #F0F9FF;
    }

    /* Modales */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.45);
      backdrop-filter: blur(3px);
      z-index: 300;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }

    .modal-backdrop.open {
      display: flex;
    }

    .modal-box {
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 14px;
      width: 100%;
      max-width: 480px;
      max-height: 90vh;
      overflow-y: auto;
      padding: 16px;
      box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
    }

    .action-choice-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .choice-btn {
      border: 1px solid var(--border);
      background: #F8FAFC;
      border-radius: 10px;
      padding: 12px 10px;
      text-align: left;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .choice-btn:hover {
      background: #E0F2FE;
      border-color: var(--primary);
    }

    .choice-btn strong {
      display: block;
      font-size: 13px;
      color: #0F172A;
      margin-bottom: 2px;
    }

    .choice-btn span {
      font-size: 11.5px;
      color: var(--text-muted);
    }

    .form-group {
      margin-bottom: 10px;
    }

    .form-group label {
      display: block;
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 4px;
    }

    .form-control {
      width: 100%;
      padding: 8px 10px;
      border-radius: 8px;
      border: 1px solid #CBD5E1;
      background: #F8FAFC;
      color: #0F172A;
      font-size: 13px;
      font-family: inherit;
    }

    .note-box {
      padding: 8px 11px;
      border-radius: 8px;
      font-size: 12px;
      margin-bottom: 10px;
      background: #F1F5F9;
      color: #334155;
      border: 1px solid #CBD5E1;
    }

    .toast {
      position: fixed;
      bottom: calc(var(--safe-bottom) + 18px);
      left: 50%;
      transform: translateX(-50%);
      background: #0F172A;
      color: #FFFFFF;
      font-weight: 700;
      font-size: 12.5px;
      padding: 8px 16px;
      border-radius: 999px;
      z-index: 400;
      display: none;
    }

    /* Mode Chef de Planning & Drag and Drop */
    .btn-chef-lock {
      border-color: #CBD5E1;
      background: #F8FAFC;
      color: #334155;
    }
    .btn-chef-lock.unlocked {
      background: #FEF3C7;
      border-color: #F59E0B;
      color: #92400E;
      font-weight: 800;
      box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2);
    }

    .chef-mode-banner {
      background: linear-gradient(90deg, #FEF3C7 0%, #FFFBEB 100%);
      border: 1.5px solid #F59E0B;
      border-radius: 12px;
      padding: 10px 14px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    .chef-mode-title {
      font-size: 13.5px;
      font-weight: 800;
      color: #92400E;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .chef-mode-sub {
      font-size: 12px;
      color: #B45309;
      margin-top: 2px;
    }

    .chef-mode-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .interne-badge.draggable-interne {
      cursor: grab;
      border: 1.5px solid #94A3B8;
      background: #FFFFFF;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
      user-select: none;
      -webkit-user-select: none;
      transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
    }
    .interne-badge.draggable-interne:hover {
      border-color: var(--primary);
      background: #F0F9FF;
      transform: translateY(-1px);
      box-shadow: 0 3px 6px rgba(2, 132, 199, 0.16);
    }
    .interne-badge.draggable-interne:active {
      cursor: grabbing;
    }
    .interne-badge.dragging {
      opacity: 0.45;
      transform: scale(0.96);
      border-style: dashed;
    }
    .interne-badge.selected-for-move {
      background: #FEF3C7 !important;
      border: 2px solid #D97706 !important;
      color: #92400E !important;
      box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.28);
      font-weight: 800;
    }

    .drag-grip {
      font-size: 11px;
      color: #64748B;
      margin-right: 1px;
      letter-spacing: -1px;
      font-weight: 900;
    }

    td.drop-zone-cell {
      transition: background 0.12s ease, outline 0.12s ease;
      position: relative;
      min-height: 38px;
    }
    td.drop-zone-cell.drag-over {
      background: #E0F2FE !important;
      outline: 2px dashed #0284C7;
      outline-offset: -2px;
    }
    td.drop-zone-cell.tap-target-ready {
      cursor: pointer;
    }
    td.drop-zone-cell.tap-target-ready:hover {
      background: #FEF3C7 !important;
      outline: 1.5px dashed #D97706;
      outline-offset: -2px;
    }

    /* Pastilles de notification & Espace Chef simplifié */
    .notif-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      border-radius: 999px;
      background: #DC2626;
      color: #FFFFFF;
      font-size: 10.5px;
      font-weight: 800;
      line-height: 1;
      margin-left: 4px;
    }

    .notif-badge.warn {
      background: #D97706;
    }

    .chef-simple-panel {
      background: #FFFFFF;
      border: 1.5px solid #CBD5E1;
      border-left: 4px solid #0284C7;
      border-radius: 12px;
      padding: 10px 14px;
      margin-bottom: 12px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    .chef-simple-panel.unlocked {
      border-left-color: #D97706;
    }

    .chef-simple-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }

    .chef-simple-title {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      font-size: 13.5px;
      font-weight: 800;
      color: #0F172A;
    }

    .chef-simple-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .chef-simple-empty {
      font-size: 12px;
      color: #15803D;
      font-weight: 600;
      margin-top: 6px;
      padding-top: 6px;
      border-top: 1px solid #F1F5F9;
    }

    .chef-simple-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid #E2E8F0;
    }

    .chef-simple-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
      padding: 7px 10px;
      border-radius: 8px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      font-size: 12px;
    }

    .chef-simple-row-left {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      color: #1E293B;
      line-height: 1.35;
    }

    .chef-row-tag {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 5px;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      white-space: nowrap;
    }
    .chef-row-tag.warn {
      background: #FEF3C7;
      color: #92400E;
      border: 1px solid #FDE68A;
    }
    .chef-row-tag.info {
      background: #E0F2FE;
      color: #0369A1;
      border: 1px solid #BAE6FD;
    }
    .chef-row-tag.danger {
      background: #FEE2E2;
      color: #B91C1C;
      border: 1px solid #FECACA;
    }

    .chef-decision-btns {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 5px;
    }

    .btn-approve {
      background: #16A34A;
      border: 1px solid #15803D;
      color: #FFFFFF;
      font-weight: 700;
      font-size: 11px;
      padding: 4px 9px;
      border-radius: 6px;
      cursor: pointer;
    }\n    .btn-approve:hover {
      background: #15803D;
      border-color: #166534;
      color: #FFFFFF;
    }

    .btn-reject {
      background: #FEF2F2;
      border: 1px solid #FCA5A5;
      color: #B91C1C;
      font-weight: 700;
      font-size: 11px;
      padding: 4px 9px;
      border-radius: 6px;
      cursor: pointer;
    }
    .btn-reject:hover {
      background: #FEE2E2;
      border-color: #F87171;
      color: #991B1B;
    }

    .btn-decide {
      background: #EFF6FF;
      border: 1px solid #93C5FD;
      color: #1D4ED8;
      font-weight: 700;
      font-size: 11px;
      padding: 4px 8px;
      border-radius: 6px;
      cursor: pointer;
    }
    .btn-decide:hover {
      background: #DBEAFE;
      border-color: #3B82F6;
    }

    .day-pill.blocking-day {
      border-color: #DC2626 !important;
      background: #FEF2F2;
    }

    td.cell-blocking-alert {
      background: #FEF2F2 !important;
      outline: 1.5px dashed #DC2626;
      outline-offset: -2px;
    }

    td.cell-mandatory-vacation {
      background: #FFF5F5;
      box-shadow: inset 3px 0 0 #FCA5A5;
    }

    .poste-pill.poste-mandatory-slot {
      box-shadow: 0 0 0 1.5px #FCA5A5;
      background: #FFF1F2;
      color: #9F1239;
      border-color: #FECDD3;
    }

    .mandatory-dot {
      display: inline-block;
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: #F87171;
      flex-shrink: 0;
    }

    .status-pill-pending {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 800;
      background: #FEF3C7;
      color: #92400E;
      border: 1px solid #FCD34D;
      white-space: nowrap;
    }
    .status-pill-approved {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 800;
      background: #DCFCE7;
      color: #166534;
      border: 1px solid #86EFAC;
      white-space: nowrap;
    }
    .status-pill-rejected {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 800;
      background: #F1F5F9;
      color: #64748B;
      border: 1px solid #CBD5E1;
      text-decoration: line-through;
      white-space: nowrap;
    }

    .week-status-strip {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
      padding: 6px 12px;
      border-radius: 9px;
      margin-bottom: 8px;
      font-size: 11.5px;
      font-weight: 700;
      border: 1px solid #CBD5E1;
      background: #F8FAFC;
      color: #334155;
    }

    .week-status-strip.locked {
      background: #F0FDF4;
      border-color: #86EFAC;
      color: #166534;
    }

    .btn-fix-week {
      background: #16A34A;
      border: 1px solid #15803D;
      color: #FFFFFF;
      font-weight: 700;
      font-size: 11.5px;
      padding: 4px 10px;
      border-radius: 7px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .btn-fix-week:hover {
      background: #15803D;
      border-color: #166534;
      color: #FFFFFF;
    }

    .btn-unfix-week {
      background: #FFFFFF;
      border: 1px solid #F59E0B;
      color: #B45309;
      font-weight: 700;
      font-size: 11px;
      padding: 4px 9px;
      border-radius: 7px;
      cursor: pointer;
    }
    .btn-unfix-week:hover {
      background: #FEF3C7;
    }

    /* Résumé Off & Vacations en Mode Chef */
    .chef-offvac-section {
      margin-top: 9px;
      padding-top: 9px;
      border-top: 1px solid #E2E8F0;
    }

    .chef-offvac-bar-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 7px;
      font-size: 11.5px;
      color: #334155;
    }

    .chef-offvac-grid {
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 6px;
    }

    .chef-offvac-card {
      background: #F8FAFC;
      border: 1px solid #CBD5E1;
      border-radius: 9px;
      padding: 6px 8px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      cursor: pointer;
      transition: border-color 0.12s ease, background 0.12s ease, box-shadow 0.12s ease;
      min-width: 0;
    }

    .chef-offvac-card:hover {
      border-color: var(--primary);
      background: #F0F9FF;
      box-shadow: 0 2px 5px rgba(2, 132, 199, 0.1);
    }

    .chef-offvac-card.warn-quota {
      border-color: #F59E0B;
      background: #FFFBEB;
    }

    .chef-offvac-card.danger-quota {
      border-color: #EF4444;
      background: #FEF2F2;
    }

    .chef-offvac-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 4px;
      min-width: 0;
    }

    .chef-offvac-name {
      display: flex;
      align-items: center;
      gap: 5px;
      font-weight: 800;
      font-size: 12px;
      color: #0F172A;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .chef-offvac-badges {
      display: flex;
      align-items: center;
      gap: 4px;
      flex-wrap: wrap;
    }

    .offvac-pill {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 1.5px 6px;
      border-radius: 5px;
      font-size: 10.5px;
      font-weight: 800;
      white-space: nowrap;
    }

    .offvac-pill.off-ok {
      background: #DCFCE7;
      color: #166534;
      border: 1px solid #86EFAC;
    }

    .offvac-pill.off-warn {
      background: #FEF3C7;
      color: #92400E;
      border: 1px solid #FCD34D;
    }

    .offvac-pill.off-danger {
      background: #FEE2E2;
      color: #991B1B;
      border: 1px solid #FCA5A5;
    }

    .offvac-pill.vac-count {
      background: #E0F2FE;
      color: #0369A1;
      border: 1px solid #BAE6FD;
    }

    .offvac-pill.conges-count {
      background: #F3E8FF;
      color: #6D28D9;
      border: 1px solid #D8B4FE;
    }

    .chef-offvac-slots {
      font-size: 10px;
      color: #475569;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .chef-offvac-sem {
      font-size: 10px;
      color: #64748B;
      border-top: 1px dashed #E2E8F0;
      padding-top: 3px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 4px;
      flex-wrap: wrap;
    }

    .chef-offvac-sem strong {
      color: #1E293B;
      font-weight: 800;
    }

    @media (max-width: 960px) {
      .chef-offvac-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
    }

    @media (max-width: 560px) {
      .chef-offvac-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }
  </style>
</head>
<body>

  <header class="app-header">
    <div class="header-top">
      <div class="brand">
        <div class="brand-logo">RB</div>
        <div>
          <div class="brand-title">Radio B Cochin</div>
          <div class="brand-sub">Hiver 2026–2027 • Sans donnée patient</div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn btn-sm btn-chef-lock" onclick="toggleChefPlanningMode()" id="chefModeBtn" title="Accéder à l'Espace Chef">
          <span id="chefModeBtnText">🔒 Espace Chef</span>
        </button>
        <button class="btn btn-sm" onclick="syncWithCloud(true)" id="syncBtn">
          <span id="syncStatusText">Synchroniser</span>
        </button>
        <button class="btn btn-primary" onclick="openQuickAddModal()">
          + Ajouter
        </button>
      </div>
    </div>

    <!-- Sélection rapide de la personne -->
    <div class="selector-bar" id="interneSelectorBar"></div>
  </header>

  <main class="container">
    <!-- Bandeau Espace Chef (affiché uniquement dans l'Espace Chef) -->
    <div id="chefPlanningBanner" style="display:none;"></div>

    <!-- Bandeau résumé sur 1 ligne -->
    <section class="summary-strip" id="personalBanner"></section>

    <!-- 5 Onglets au texte court et sans icône -->
    <nav class="main-tabs">
      <button class="tab-btn active" data-tab="planning" id="tabBtnPlanning" onclick="switchTab('planning')">Planning</button>
      <button class="tab-btn" data-tab="vacances" id="tabBtnVacances" onclick="switchTab('vacances')">Congés</button>
      <button class="tab-btn" data-tab="presentations" onclick="switchTab('presentations')">Cours & Cas</button>
      <button class="tab-btn" data-tab="reunions" onclick="switchTab('reunions')">Réunions</button>
      <button class="tab-btn" data-tab="annuaire" onclick="switchTab('annuaire')">Annuaire</button>
    </nav>

    <!-- Contenu de l'onglet -->
    <div id="tabContent"></div>
  </main>

  <!-- Modal : Déverrouillage Espace Chef (code cocochin) -->
  <div class="modal-backdrop" id="modalChefAuth">
    <div class="modal-box" style="max-width:390px;">
      <div class="card-header">
        <div class="card-title">🔓 Espace Chef</div>
        <button class="btn btn-sm" onclick="closeModal('modalChefAuth')">Fermer</button>
      </div>
      <div class="note-box">
        Entrez le code Chef pour valider les modifications, fixer la semaine ou déplacer un interne.
      </div>
      <div class="form-group">
        <label>Code Chef</label>
        <input
          type="password"
          id="chefCodeInput"
          class="form-control"
          placeholder="Code espace chef..."
          autocomplete="off"
          onkeydown="if(event.key==='Enter') submitChefAuth()"
        />
      </div>
      <div id="chefCodeError" class="note-box" style="display:none; background:#FEE2E2; border-color:#FCA5A5; color:#B91C1C; font-weight:700;">
        Code incorrect. Veuillez réessayer.
      </div>
      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:12px;">
        <button class="btn" onclick="closeModal('modalChefAuth')">Annuler</button>
        <button class="btn btn-primary" onclick="submitChefAuth()">Déverrouiller</button>
      </div>
    </div>
  </div>

  <!-- Menu unique "+ Ajouter" regroupant toutes les actions -->
  <div class="modal-backdrop" id="modalQuickAdd">
    <div class="modal-box">
      <div class="card-header">
        <div class="card-title">Que souhaitez-vous ajouter ?</div>
        <button class="btn btn-sm" onclick="closeModal('modalQuickAdd')">Fermer</button>
      </div>
      <div class="action-choice-grid">
        <button class="choice-btn" onclick="closeModal('modalQuickAdd'); openAbsenceModal();">
          <strong>Poser un congé / RG</strong>
          <span>Congés annuels, formation ou repos de garde</span>
        </button>
        <button class="choice-btn" onclick="closeModal('modalQuickAdd'); openNextPresentationModal();">
          <strong>S'inscrire à un cours</strong>
          <span>Cas du mardi ou biblio du vendredi</span>
        </button>
        <button class="choice-btn" onclick="closeModal('modalQuickAdd'); openQuickVacationPicker();">
          <strong>Échanger un poste</strong>
          <span>Modifier une demi-journée du planning</span>
        </button>
        <button class="choice-btn" onclick="closeModal('modalQuickAdd'); openMeetingModal();">
          <strong>Ajouter une réunion</strong>
          <span>Staff ou information du service</span>
        </button>
        <button class="choice-btn" onclick="closeModal('modalQuickAdd'); openPhoneContactModal();">
          <strong>Ajouter un numéro à l'annuaire</strong>
          <span>Poste interne Cochin, DECT ou secrétariat</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Modal : Poser un congé / RG -->
  <div class="modal-backdrop" id="modalAbsence">
    <div class="modal-box">
      <div class="card-header">
        <div class="card-title">Poser un congé ou repos de garde</div>
        <button class="btn btn-sm" onclick="closeModal('modalAbsence')">Fermer</button>
      </div>
      <div class="note-box">
        Règle : max 2 internes absents en même temps. Éviter mardi/vendredi pour les jours isolés.
      </div>
      <div class="form-group">
        <label>Interne</label>
        <select id="absInterneSelect" class="form-control" onchange="previewAbsenceRuleWarning()"></select>
      </div>
      <div class="form-group">
        <label>Motif</label>
        <select id="absTypeSelect" class="form-control" onchange="previewAbsenceRuleWarning()">
          <option value="CA 1">Congés Annuels (CA 1)</option>
          <option value="CA 2">Congés Annuels (CA 2)</option>
          <option value="CF">Congé Formation / Congrès (CF)</option>
          <option value="Repos de garde">Repos de garde (RG)</option>
          <option value="Autre">Autre absence</option>
        </select>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Début</label>
          <input type="date" id="absStartDate" class="form-control" min="2026-11-02" max="2027-05-02" onchange="previewAbsenceRuleWarning()" />
        </div>
        <div class="form-group">
          <label>Fin (incluse)</label>
          <input type="date" id="absEndDate" class="form-control" min="2026-11-02" max="2027-05-02" onchange="previewAbsenceRuleWarning()" />
        </div>
      </div>
      <div class="form-group">
        <label>Note (optionnel)</label>
        <input type="text" id="absComment" class="form-control" placeholder="Ex: Garde du dimanche, JFR..." />
      </div>
      <div id="absRuleWarning" class="note-box" style="display:none;"></div>
      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:12px;">
        <button class="btn" onclick="closeModal('modalAbsence')">Annuler</button>
        <button class="btn btn-primary" onclick="saveAbsenceForm()">Soumettre la demande</button>
      </div>
    </div>
  </div>

  <!-- Modal : Cas / Biblio / Cours -->
  <div class="modal-backdrop" id="modalPresentation">
    <div class="modal-box">
      <div class="card-header">
        <div class="card-title" id="presModalTitle">Modifier</div>
        <button class="btn btn-sm" onclick="closeModal('modalPresentation')">Fermer</button>
      </div>
      <input type="hidden" id="presIdInput" />
      <div class="form-group">
        <label>Date</label>
        <select id="presDateSelect" class="form-control" onchange="onPresDateChange(this.value)"></select>
      </div>
      <div class="form-group" id="presInterneGroup">
        <label>Interne</label>
        <select id="presInterneSelect" class="form-control"></select>
      </div>
      <div class="form-group" id="presChefGroup" style="display:none;">
        <label>Chef / Intervenant</label>
        <input type="text" id="presChefInput" class="form-control" placeholder="Ex: Dr T. Lefèvre" />
      </div>
      <div class="form-group">
        <label id="presSujetLabel">Sujet</label>
        <input type="text" id="presSujetInput" class="form-control" placeholder="Sujet..." />
      </div>
      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:12px;">
        <button class="btn" onclick="closeModal('modalPresentation')">Annuler</button>
        <button class="btn btn-primary" onclick="savePresentationForm()">Enregistrer</button>
      </div>
    </div>
  </div>

  <!-- Modal : Modifier / Échanger un poste -->
  <div class="modal-backdrop" id="modalVacationEdit">
    <div class="modal-box">
      <div class="card-header">
        <div class="card-title">Modifier un poste</div>
        <button class="btn btn-sm" onclick="closeModal('modalVacationEdit')">Fermer</button>
      </div>
      <div class="note-box">
        Règles : <strong>Pas le même poste toute la journée (Matin ≠ Après-midi)</strong> • <strong>Max 1 IRM d'après-midi / semaine</strong> (sauf exception) • 2 demi-offs max / semaine • Pas de demi-off mardi PM ni vendredi PM.
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Date</label>
          <input type="date" id="vacEditDate" class="form-control" onchange="refreshVacationModalFields()" />
        </div>
        <div class="form-group">
          <label>Interne</label>
          <select id="vacEditInterneId" class="form-control" onchange="refreshVacationModalFields()"></select>
        </div>
      </div>
      <input type="hidden" id="vacEditHeader" />
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Matin</label>
          <select id="vacEditAm" class="form-control" onchange="refreshVacationModalSummary()"></select>
        </div>
        <div class="form-group">
          <label>Après-midi</label>
          <select id="vacEditPm" class="form-control" onchange="refreshVacationModalSummary()"></select>
        </div>
      </div>
      <div id="vacEditLiveSummary" class="note-box" style="margin-bottom:10px; background:#F8FAFC; border-color:#CBD5E1;"></div>
      <div class="form-group">
        <label>Note</label>
        <input type="text" id="vacEditNote" class="form-control" placeholder="Ex: Échange avec Noé..." />
      </div>
      <div style="display:flex; justify-content:space-between; gap:8px; margin-top:12px;">
        <button class="btn btn-sm" onclick="resetSingleVacation()">Par défaut</button>
        <div style="display:flex; gap:8px;">
          <button class="btn" onclick="closeModal('modalVacationEdit')">Annuler</button>
          <button class="btn btn-primary" onclick="saveSingleVacation()">Valider</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal : Ajouter une réunion -->
  <div class="modal-backdrop" id="modalMeeting">
    <div class="modal-box">
      <div class="card-header">
        <div class="card-title">Nouvelle réunion</div>
        <button class="btn btn-sm" onclick="closeModal('modalMeeting')">Fermer</button>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Type</label>
          <select id="meetCategory" class="form-control" onchange="onMeetCategoryChange(this.value)">
            <option value="Bone Club">Bone Club</option>
            <option value="CRA">CRA (Anapath)</option>
            <option value="Autre">Autre réunion</option>
          </select>
        </div>
        <div class="form-group">
          <label>Date</label>
          <input type="date" id="meetDate" class="form-control" value="2026-11-25" />
        </div>
        <div class="form-group">
          <label>Horaire</label>
          <input type="text" id="meetHoraire" class="form-control" placeholder="18h00 – 20h00" />
        </div>
      </div>
      <div class="form-group">
        <label>Titre / Session</label>
        <input type="text" id="meetTitle" class="form-control" placeholder="Ex: Bone Club Cochin — Session..." />
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Modération / Intervenants</label>
          <input type="text" id="meetSender" class="form-control" value="Pr J-L. Drapé & Pr A. Feydy" />
        </div>
        <div class="form-group">
          <label>Salle</label>
          <input type="text" id="meetLocation" class="form-control" value="Amphithéâtre Luton (Cochin)" />
        </div>
      </div>
      <div class="form-group">
        <label>Détails</label>
        <textarea id="meetDesc" class="form-control" rows="2"></textarea>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:12px;">
        <button class="btn" onclick="closeModal('modalMeeting')">Annuler</button>
        <button class="btn btn-primary" onclick="saveMeetingForm()">Enregistrer</button>
      </div>
    </div>
  </div>

  <!-- Modal : Ajouter un numéro -->
  <div class="modal-backdrop" id="modalPhoneContact">
    <div class="modal-box">
      <div class="card-header">
        <div class="card-title">Nouveau numéro Cochin</div>
        <button class="btn btn-sm" onclick="closeModal('modalPhoneContact')">Fermer</button>
      </div>
      <div class="form-group">
        <label>Catégorie</label>
        <select id="phoneCatInput" class="form-control">
          <option value="Radiologie B — Secrétariats & Consoles">Radio B — Secrétariats & Consoles</option>
          <option value="Radiologie B — Équipe Médicale (Chefs & Seniors)">Radio B — Médecins</option>
          <option value="Services Partenaires (Ortho, Rhumato, Anesth, Anapath)">Services (Ortho, Rhumato, Anesth)</option>
          <option value="Laboratoires, Pharmacie & Administration (DAM)">Labos & Administration</option>
        </select>
      </div>
      <div class="form-group">
        <label>Nom / Console</label>
        <input type="text" id="phoneNameInput" class="form-control" placeholder="Ex: Console IRM 3T" />
      </div>
      <div class="form-group">
        <label>Précision</label>
        <input type="text" id="phoneRoleInput" class="form-control" placeholder="Ex: Manipulateurs IRM" />
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Poste à 5 chiffres / DECT</label>
          <input type="text" id="phonePosteInput" class="form-control" placeholder="Ex: 12483" />
        </div>
        <div class="form-group">
          <label>Ligne directe</label>
          <input type="text" id="phoneNumInput" class="form-control" placeholder="01 58 41 24 83" />
        </div>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Localisation</label>
          <input type="text" id="phoneBldgInput" class="form-control" placeholder="Bâtiment Ollier" />
        </div>
        <div class="form-group">
          <label>Fax (optionnel)</label>
          <input type="text" id="phoneFaxInput" class="form-control" />
        </div>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:12px;">
        <button class="btn" onclick="closeModal('modalPhoneContact')">Annuler</button>
        <button class="btn btn-primary" onclick="savePhoneContactForm()">Enregistrer</button>
      </div>
    </div>
  </div>

  <div class="toast" id="toastBox">Enregistré</div>

  <script>
    const INITIAL_DATA = __INITIAL_DATA_JSON__;
    const WEBHOOK_URL = __WEBHOOK_URL_JSON__;
    const INTERNES_SHEET_ID = __INTERNES_SHEET_ID_JSON__;
    const CLOUD_PROP_KEY = __CLOUD_PROP_KEY_JSON__;
    const LOCAL_STORAGE_KEY = "cochin_internes_app_state_v2";
    const SELECTED_INTERNE_KEY = "cochin_internes_selected_id_v1";
    const CHEF_MODE_STORAGE_KEY = "cochin_chef_planning_unlocked_v1";
    const CHEF_SECRET_CODE = "cocochin";

    let STATE = loadInitialState();
    let currentTab = "planning";
    let selectedInterneId = localStorage.getItem(SELECTED_INTERNE_KEY) || "gabriel";
    let planningScope = (selectedInterneId === "all") ? "internes" : (selectedInterneId === "all_chefs" ? "chefs" : "perso"); // 'internes' | 'perso' | 'chefs' | 'combined'
    let planningMode = "week";      // 'day' | 'week' | 'month'
    let currentDateIso = "2026-11-02";
    let presFilter = "cas_mardi"; // 'cas_mardi' | 'biblio_vendredi' | 'cours_internes'
    let reunionsFilter = "bone_cra"; // 'bone_cra' | 'staffs_hebdo'
    let annuaireSearch = "";
    let annuaireCategory = "all";
    let vacFilter = "all"; // 'all' | 'conges' | 'rg' | 'gardes'
    let showStatsTable = false;
    let showChefOffVacSummary = true;
    let isChefPlanningMode = sessionStorage.getItem(CHEF_MODE_STORAGE_KEY) === "1";
    let activeDragPayload = null;
    let selectedForMove = null; // { dIso, periodKey, interneId, fromPoste }
    let chefHistoryStack = [];
    let pendingChefActionCallback = null;

    function mergePresentationsList(baseList, savedList) {
      const rgSet = new Set(
        ((INITIAL_DATA && INITIAL_DATA.absences) || [])
          .filter(a => a && a.type === "Repos de garde")
          .map(a => a.date + "__" + a.interneId)
      );
      const map = {};
      (baseList || []).forEach(p => { if (p && p.id) map[p.id] = Object.assign({}, p); });
      (savedList || []).forEach(p => {
        if (!p || !p.id || !map[p.id]) return;
        const baseP = map[p.id];
        if (baseP.type === "cours_internes") {
          if (p.userEditedCours) {
            if (p.chefIntervenant !== undefined) baseP.chefIntervenant = p.chefIntervenant;
            if (p.coursChef !== undefined) baseP.coursChef = p.coursChef;
            if (p.sujet !== undefined) baseP.sujet = p.sujet;
            baseP.pasDeCours = (baseP.coursChef === "Pas de cours" || baseP.sujet === "Pas de cours");
            baseP.userEditedCours = true;
          }
          return;
        }
        if (p.sujet && p.sujet !== "Dossier ostéo-articulaire inaugural (choix libre)") {
          baseP.sujet = p.sujet;
        }
        if (p.userEditedPres && !(p.interneId && rgSet.has(baseP.date + "__" + p.interneId) && !p.sujet)) {
          if (p.interneId) baseP.interneId = p.interneId;
          if (p.interneName) baseP.interneName = p.interneName;
          baseP.userEditedPres = true;
        }
      });
      return Object.values(map).sort((a, b) => a.date.localeCompare(b.date) || a.type.localeCompare(b.type));
    }

    function mergeMeetingsList(baseList, savedList) {
      const obsoleteTitles = new Set(["Bone Club — Novembre", "Bone Club — Janvier", "Confrontation Radio-Anatomo-Pathologique (Janvier)", "BONE CLUB Cochin — Session de Décembre"]);
      const legacyRemovedIds = new Set([
        "reunion-2026-11-02-cafe",
        "reunion-2026-11-02-formation",
        "reunion-2026-11-04-accueil",
        "reunion-2026-11-09-externes",
        "reunion-2026-11-19-ecos",
        "reunion-2026-11-24-dmu",
        "reunion-2026-12-02-boneclub",
        "reunion-2026-12-18-vaccin",
        "reunion-2026-12-21-noel",
        "reunion-2027-02-26-seminaire-cochin"
      ]);
      const map = {};
      (baseList || []).forEach(m => { if (m && m.id) map[m.id] = Object.assign({}, m); });
      (savedList || []).forEach(m => {
        if (!m || !m.id || obsoleteTitles.has(m.title) || legacyRemovedIds.has(m.id)) return;
        if (!map[m.id]) map[m.id] = m;
      });
      return Object.values(map).sort((a, b) => a.date.localeCompare(b.date));
    }

    function normalizeAbsencesList(list) {
      return (list || []).map(a => {
        if (!a) return a;
        const copy = Object.assign({}, a);
        if (!copy.status) copy.status = (copy.type === "Repos de garde" && copy.isOfficialGardeRg) ? "approved" : "pending";
        return copy;
      });
    }

    let localMutationSeq = 0;

    function mergeAbsencesList(baseList, savedList, deletedIds) {
      const delSet = new Set(deletedIds || []);
      const mapByPair = {};
      normalizeAbsencesList(baseList || []).forEach(a => {
        if (!a || !a.date || !a.interneId || delSet.has(a.id)) return;
        mapByPair[a.date + "__" + a.interneId] = Object.assign({}, a);
      });
      normalizeAbsencesList(savedList || []).forEach(a => {
        if (!a || !a.date || !a.interneId || delSet.has(a.id)) return;
        const k = a.date + "__" + a.interneId;
        const existing = mapByPair[k];
        if (existing && existing.isOfficialGardeRg) {
          // Conserver le Repos de garde officiel (sauf si son statut a été explicitement modifié en rejected)
          if (a.status === "rejected") {
            existing.status = "rejected";
            existing.validatedBy = a.validatedBy || "Chef";
            existing.validatedAt = a.validatedAt || new Date().toISOString();
          } else if (a.status === "approved" && a.validatedAt) {
            existing.status = "approved";
            existing.validatedBy = a.validatedBy || "Chef";
            existing.validatedAt = a.validatedAt;
          }
          return;
        }
        if (existing) {
          // Une validation ou un refus par le Chef ("approved" / "rejected") prime toujours sur un statut "pending"
          const exDecided = existing.status === "approved" || existing.status === "rejected";
          const inDecided = a.status === "approved" || a.status === "rejected";
          if (exDecided && !inDecided) {
            return;
          }
          if (exDecided && inDecided && existing.validatedAt && a.validatedAt && existing.validatedAt > a.validatedAt) {
            return;
          }
        }
        mapByPair[k] = Object.assign({}, existing || {}, a);
      });
      return Object.values(mapByPair).sort((a, b) => a.date.localeCompare(b.date) || a.interneId.localeCompare(b.interneId));
    }

    function markChefValidationStamp() {
      const nowIso = new Date().toISOString();
      STATE.chefValidatedAt = nowIso;
      STATE.chefRevision = (Number(STATE.chefRevision) || 0) + 1;
      return nowIso;
    }

    function loadInitialState() {
      const base = JSON.parse(JSON.stringify(INITIAL_DATA));
      base.deletedAbsenceIds = Array.isArray(base.deletedAbsenceIds) ? base.deletedAbsenceIds : [];
      base.deletedCustomKeys = Array.isArray(base.deletedCustomKeys) ? base.deletedCustomKeys : [];
      base.deletedCustomAt = Object.assign({}, base.deletedCustomAt || {});
      base.absences = mergeAbsencesList(base.absences, [], base.deletedAbsenceIds);
      base.interneGardes = Object.assign({}, base.interneGardes || {});
      base.customVacations = Object.assign({}, base.customVacations || {});
      base.chefDecisions = Object.assign({}, base.chefDecisions || {});
      base.lockedWeeks = Object.assign({}, base.lockedWeeks || {});
      base.chefValidatedAt = base.chefValidatedAt || null;
      base.chefRevision = Number(base.chefRevision) || 0;
      try {
        const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
        if (raw) {
          const saved = JSON.parse(raw);
          if (Array.isArray(saved.deletedAbsenceIds)) {
            saved.deletedAbsenceIds.forEach(id => {
              if (id && !base.deletedAbsenceIds.includes(id)) base.deletedAbsenceIds.push(id);
            });
          }
          if (saved.deletedCustomAt && typeof saved.deletedCustomAt === "object") {
            base.deletedCustomAt = Object.assign({}, base.deletedCustomAt || {}, saved.deletedCustomAt);
          }
          if (Array.isArray(saved.deletedCustomKeys)) {
            saved.deletedCustomKeys.forEach(k => {
              if (k && !base.deletedCustomKeys.includes(k)) base.deletedCustomKeys.push(k);
            });
          }
          if (Array.isArray(saved.absences)) {
            base.absences = mergeAbsencesList(base.absences, saved.absences, base.deletedAbsenceIds);
          }
          if (saved.interneGardes && typeof saved.interneGardes === "object") {
            base.interneGardes = Object.assign({}, base.interneGardes, saved.interneGardes);
          }
          if (saved.customVacations) {
            Object.keys(saved.customVacations).forEach(cKey => {
              if (base.deletedCustomKeys.includes(cKey)) return;
              const sv = saved.customVacations[cKey];
              const bv = base.customVacations[cKey];
              if (!bv) {
                base.customVacations[cKey] = sv;
              } else if (bv.status === "approved" && sv.status !== "approved") {
                // Conserver la version validée par le chef
              } else if (sv.validatedAt && bv.validatedAt && sv.validatedAt < bv.validatedAt) {
                // Conserver la version plus récente
              } else {
                base.customVacations[cKey] = sv;
              }
            });
          }
          base.deletedCustomKeys.forEach(cKey => {
            delete base.customVacations[cKey];
          });
          if (saved.chefDecisions) base.chefDecisions = Object.assign({}, base.chefDecisions || {}, saved.chefDecisions);
          if (saved.lockedWeeks) base.lockedWeeks = Object.assign({}, base.lockedWeeks || {}, saved.lockedWeeks);
          if (saved.chefValidatedAt && (!base.chefValidatedAt || saved.chefValidatedAt > base.chefValidatedAt)) {
            base.chefValidatedAt = saved.chefValidatedAt;
          }
          if (Number(saved.chefRevision) > base.chefRevision) {
            base.chefRevision = Number(saved.chefRevision);
          }
          if (Array.isArray(saved.presentations) && saved.presentations.length > 0) {
            base.presentations = mergePresentationsList(base.presentations, saved.presentations);
          }
          if (Array.isArray(saved.meetings) && saved.meetings.length > 0) {
            base.meetings = mergeMeetingsList(base.meetings, saved.meetings);
          }
          if (Array.isArray(saved.phoneDirectory) && saved.phoneDirectory.length > 0) {
            const map = {};
            (base.phoneDirectory || []).forEach(c => { map[c.id] = c; });
            saved.phoneDirectory.forEach(c => { if (c && c.id) map[c.id] = c; });
            base.phoneDirectory = Object.values(map);
          }
        }
      } catch (e) {}
      recomputeScheduleInPlace(base);
      return base;
    }

    function saveStateLocal() {
      localMutationSeq++;
      recomputeScheduleInPlace(STATE);
      try {
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify({
          updatedAt: new Date().toISOString(),
          chefValidatedAt: STATE.chefValidatedAt || null,
          chefRevision: Number(STATE.chefRevision) || 0,
          deletedAbsenceIds: STATE.deletedAbsenceIds || [],
          deletedCustomKeys: STATE.deletedCustomKeys || [],
          deletedCustomAt: STATE.deletedCustomAt || {},
          absences: STATE.absences,
          interneGardes: STATE.interneGardes || {},
          customVacations: STATE.customVacations || {},
          chefDecisions: STATE.chefDecisions || {},
          lockedWeeks: STATE.lockedWeeks || {},
          presentations: STATE.presentations,
          meetings: STATE.meetings,
          phoneDirectory: STATE.phoneDirectory || []
        }));
      } catch (e) {}
    }

    function showToast(msg) {
      const el = document.getElementById("toastBox");
      el.textContent = msg;
      el.style.display = "block";
      clearTimeout(window.__toastTimer);
      window.__toastTimer = setTimeout(() => { el.style.display = "none"; }, 2500);
    }

    function getInterneById(iid) {
      return STATE.internes.find(x => x.id === iid) || STATE.internes[0];
    }

    function getInterneGardeInfo(iso) {
      if (!STATE.interneGardes || !STATE.interneGardes[iso]) return null;
      return STATE.interneGardes[iso];
    }

    function renderInterneGardeCellHtml(iso, compact = false) {
      const g = getInterneGardeInfo(iso);
      if (!g || !g.nom) return `<span style="color:#CBD5E1">—</span>`;
      if (g.isRadioB && g.interneId) {
        const iObj = getInterneById(g.interneId);
        const isMe = (selectedInterneId !== "all" && g.interneId === selectedInterneId) ? "highlight-me" : "";
        const rgTag = g.rgIsWorkingDay ? `<span class="tag-binome" title="Repos de garde le lendemain (${formatDateFr(g.rgDate)})">RG J+1</span>` : "";
        if (compact) {
          return `<span style="display:inline-flex; align-items:center; gap:4px; font-weight:800; color:${iObj.color};">
            <span style="width:6px;height:6px;border-radius:50%;background:${iObj.color};display:inline-block;"></span>
            ${iObj.shortName}
          </span>`;
        }
        return `<span class="interne-badge ${isMe}" onclick="selectInterne('${iObj.id}')" title="Garde d'interne : ${iObj.fullName}${g.rgDate ? ' • Repos de garde le ' + formatDateFr(g.rgDate) : ''}">
          <span style="width:6px;height:6px;border-radius:50%;background:${iObj.color};display:inline-block;"></span>
          <strong>🌙 ${iObj.shortName}</strong>
          ${rgTag}
        </span>`;
      }
      return `<span style="font-size:11px; font-weight:600; color:#475569;" title="Interne de garde Cochin (hors Radio B) : ${g.nom}">🌙 ${g.nom}</span>`;
    }

    function getPosteClass(poste) {
      const p = String(poste || "").toUpperCase();
      if (p.includes("FERMÉ") || p.includes("FERME") || p.includes("MAINTENANCE")) return "poste-closed";
      if (p.includes("VACANCES") || p.includes("CA") || p.includes("CF")) return "poste-vac";
      if (p === "RG" || p.includes("REPOS") || p.includes("GARDE") || p.includes("FÉRIÉ")) return "poste-rg";
      if (p.includes("LIBRE")) return "poste-off";
      if (p.includes("FORMATION") || p.includes("ACCUEIL")) return "poste-cs";
      if (p.includes("IRM")) return "poste-irm";
      if (p.includes("ECHO") || p.includes("ÉCHO")) return "poste-echo";
      if (p.includes("ACHARD")) return "poste-achard";
      if (p.includes("OLLIER DIAG") || p.includes("OLLIER 3") || p === "TDM OLLIER" || p === "SCAN OLLIER") return "poste-tdm-ollier";
      if (p.includes("SAU") || p.includes("OLLIER 4")) return "poste-tdm-sau";
      if (p.includes("GESTES") || p.includes("ALLURA")) return "poste-gestes";
      if (p.includes("LECTURE") || p.includes("CS") || p.includes("CONSULT")) return "poste-cs";
      return "poste-tdm";
    }

    function getPosteHoraire(poste, periodKey) {
      const p = String(poste || "").toUpperCase();
      if (p.includes("FORMATION") || p.includes("ACCUEIL")) return "08h15 – 12h00";
      if (p.includes("IRM")) {
        return periodKey === "am" ? "dès 07h45" : (periodKey === "pm" ? "13h30 – 18h30" : "dès 07h45");
      }
      if (p.includes("ECHO") || p.includes("ÉCHO") || p.includes("GESTES")) {
        return periodKey === "am" ? "dès 09h00" : (periodKey === "pm" ? "13h30 – 18h00" : "dès 09h00");
      }
      if (p.includes("SAU") || p.includes("OLLIER 4")) {
        return periodKey === "am" ? "08h00 – 13h00" : (periodKey === "pm" ? "fin à 18h30" : "08h00 – 18h30");
      }
      return "";
    }

    function getPosteWithTimeLabel(poste, periodKey) {
      let shortName = poste === "1/2 journée libre" ? "Demi-off" : (poste === "FORMATION / ACCUEIL" ? "Accueil & Formation" : poste);
      if (shortName === "TDM OLLIER DIAG") shortName = "SCAN OLLIER";
      if (shortName === "IRM" && periodKey === "pm") shortName = "IRM PM";
      const p = String(poste || "").toUpperCase();
      let h = "";
      if (p.includes("FORMATION") || p.includes("ACCUEIL")) h = "08h15–12h00";
      else if (p.includes("IRM")) h = periodKey === "am" ? "7h45" : (periodKey === "pm" ? "13h30–18h30" : "");
      else if (p.includes("ECHO") || p.includes("ÉCHO") || p.includes("GESTES")) h = periodKey === "am" ? "9h00" : "";
      else if (p.includes("SAU") || p.includes("OLLIER 4")) h = periodKey === "am" ? "dès 8h00" : (periodKey === "pm" ? "fin 18h30" : "8h00–18h30");
      return h ? `${shortName} <span style="opacity:0.85; font-weight:600; font-size:10px;">(${h})</span>` : shortName;
    }

    function renderPosteCellLabel(poste, periodKey) {
      let shortName = poste === "1/2 journée libre" ? "Demi-off" : poste;
      if (shortName === "FORMATION / ACCUEIL") shortName = "ACCUEIL / FORM.";
      if (shortName === "TDM OLLIER DIAG" || shortName === "TDM OLLIER" || shortName === "TDM OLLIER 3") shortName = "SCAN OLLIER";
      if (shortName === "TDM OLLIER 4 (SAU)") shortName = "TDM SAU";
      if (shortName === "TDM ACHARD 1") shortName = "SCAN ACHARD";
      if (shortName === "CONSULT / LECTURE") shortName = "CS / LECT.";
      if (shortName === "IRM" && periodKey === "pm") shortName = "IRM PM";
      if (isChefPlanningMode) {
        return `<span class="poste-pill ${getPosteClass(poste)}">${shortName.replace("/", "/<wbr>")}</span>`;
      }
      const p = String(poste || "").toUpperCase();
      let h = "";
      if (p.includes("FORMATION") || p.includes("ACCUEIL")) h = "08h15–12h00";
      else if (p.includes("IRM")) h = periodKey === "am" ? "07h45" : "13h30–18h30";
      else if (p.includes("ECHO") || p.includes("ÉCHO")) h = periodKey === "am" ? "09h00" : "13h30–18h00";
      else if (p.includes("GESTES")) h = periodKey === "am" ? "09h00" : "13h30–18h00";
      else if (p.includes("SAU") || p.includes("OLLIER 4")) h = periodKey === "am" ? "08h00–18h30" : "fin 18h30";
      else if (p.includes("LECTURE") || p.includes("CONSULT")) h = periodKey === "pm" ? "Mar : Pr Drapé • Ven : CS" : "";
      return `<div style="display:flex; flex-direction:column; align-items:flex-start; gap:1px;">
        <span class="poste-pill ${getPosteClass(poste)}">${shortName.replace("/", "/<wbr>")}</span>
        ${h ? `<span class="poste-horaire-sub" style="font-size:9.5px; font-weight:700; color:var(--text-muted); padding-left:1px;">🕒 ${h}</span>` : ""}
      </div>`;
    }

    const MANDATORY_WEEKLY_POSTES_MAP = {
      "1_am": ["ECHO"],
      "1_pm": ["IRM"],
      "2_am": ["GESTES (C)", "IRM 3T", "IRM 1,5T"],
      "2_pm": ["LECTURE/CS"],
      "3_am": ["IRM 3T", "IRM 1,5T"],
      "3_pm": ["GESTES (C)", "IRM", "SCAN ACHARD", "ECHO"],
      "4_am": ["ECHO", "GESTES (C)"],
      "4_pm": ["IRM"],
      "5_am": ["IRM 3T"],
      "5_pm": []
    };

    const CHEF_TO_INTERNE_POSTE_MAP = {
      "TDM OLLIER 4 (SAU)": "TDM SAU",
      "TDM OLLIER 4": "TDM SAU",
      "ECHO": "ECHO",
      "GESTES (C)": "GESTES (C)",
      "POSTE C": "GESTES (C)",
      "TDM ACHARD 1": "SCAN ACHARD",
      "TDM OLLIER 3": "TDM OLLIER DIAG",
      "IRM 3T": "IRM 3T",
      "IRM 1,5T": "IRM 1,5T",
      "IRM": "IRM",
      "ALLURA": "ALLURA"
    };

    function getOpenMandatoryPostesForHalfDay(iso, halfKey, stRef) {
      stRef = stRef || STATE;
      if (!iso || !stRef) return new Set();
      if (iso === "2026-11-02" && halfKey === "am") return new Set(["FORMATION / ACCUEIL"]);
      const dObj = stRef.schedule ? stRef.schedule[iso] : null;
      if (dObj && dObj.holiday) return new Set();
      const [yy, mm, dd] = iso.split("-").map(Number);
      const jsDay = new Date(yy, mm - 1, dd).getDay();
      if (jsDay < 1 || jsDay > 5) return new Set();
      const noInterneTheveninNov = (halfKey === "am" && jsDay === 3 && iso.startsWith("2026-11"));
      const baseReq = new Set(MANDATORY_WEEKLY_POSTES_MAP[`${jsDay}_${halfKey}`] || []);
      if (noInterneTheveninNov) baseReq.delete("ECHO");
      const chDay = (stRef.chefsPlanning || {})[iso];
      if (!chDay || !Array.isArray(chDay[halfKey])) {
        baseReq.add("TDM SAU");
        return baseReq;
      }
      const openPostes = new Set();
      chDay[halfKey].forEach(entry => {
        const docVal = String(entry.doc || "").trim();
        const pChef = String(entry.poste || "").trim();
        const isClosed = Boolean(entry.closed) || docVal.toUpperCase().startsWith("FERM") || docVal.toUpperCase() === "MAINTENANCE";
        if (isClosed) return;
        if (CHEF_TO_INTERNE_POSTE_MAP[pChef]) {
          openPostes.add(CHEF_TO_INTERNE_POSTE_MAP[pChef]);
        } else if (pChef === "CONSULTATION" && halfKey === "pm" && (jsDay === 2 || jsDay === 5)) {
          openPostes.add("LECTURE/CS");
        }
      });
      const res = new Set(["TDM SAU"]);
      baseReq.forEach(p => {
        if (openPostes.has(p)) res.add(p);
      });
      return res;
    }

    function isMandatoryVacationSlot(iso, halfKey, posteName, stRef) {
      if (!posteName || !iso || !halfKey) return false;
      const reqSet = getOpenMandatoryPostesForHalfDay(iso, halfKey, stRef);
      return reqSet.has(posteName);
    }

    function recomputeScheduleInPlace(st) {
      st = st || STATE;
      if (!st) return;
      // Utiliser baseSchedule (pré-équilibré autour des Repos de garde officiels, avec preRgAm/preRgPm en cas d'annulation)
      const baseSched = INITIAL_DATA.baseSchedule || INITIAL_DATA.schedule;
      const absLookup = {};
      (st.absences || []).forEach(a => {
        if (!a || !a.date || !a.interneId) return;
        if (a.status === "rejected") return; // Les vacances refusées par le chef ne bloquent plus le planning
        absLookup[a.date + "__" + a.interneId] = {
          type: a.type || "CA 1",
          status: a.status || "pending",
          comment: a.comment || "",
          id: a.id
        };
      });
      const custom = st.customVacations || {};
      const lockedWeeks = st.lockedWeeks || {};
      const seniorIds = ["gabriel", "marwane", "milan", "nathanael", "oussama"];
      const phDocTokens = new Set([
        "FEYDY", "DRAPE", "DRAPÉ", "MIHOUBI", "MD", "AL", "LAPORTE",
        "AC", "COSTEA", "YANG", "RUBINI", "SEROR", "MOUTOUNET", "HAMMOUD"
      ]);
      const chefToInterneMap = {
        "TDM OLLIER 4 (SAU)": "TDM SAU",
        "TDM OLLIER 4": "TDM SAU",
        "ECHO": "ECHO",
        "GESTES (C)": "GESTES (C)",
        "POSTE C": "GESTES (C)",
        "TDM ACHARD 1": "SCAN ACHARD",
        "TDM OLLIER 3": "TDM OLLIER DIAG",
        "IRM 3T": "IRM 3T",
        "IRM 1,5T": "IRM 1,5T",
        "IRM": "IRM",
        "ALLURA": "ALLURA"
      };
      const mandatoryWeeklyPostes = {
        "1_am": ["ECHO"],
        "1_pm": ["IRM"],
        "2_am": ["GESTES (C)", "IRM 3T"],
        "2_pm": ["LECTURE/CS"],
        "3_am": ["IRM 3T", "IRM 1,5T"],
        "3_pm": ["GESTES (C)", "IRM", "SCAN ACHARD", "ECHO"],
        "4_am": ["ECHO", "GESTES (C)"],
        "4_pm": ["IRM"],
        "5_am": ["IRM 3T"],
        "5_pm": []
      };
      const fixedOffHalfDays = {
        oussama: "1_am", // Lundi matin
        gabriel: "2_am", // Mardi matin
        marwane: "4_am"  // Jeudi matin
      };
      function isProtectedFixedOff(iid, dIso, halfKey) {
        if (!dIso || dIso < "2026-11-09") return false;
        const target = fixedOffHalfDays[iid];
        if (!target) return false;
        const [yyF, mmF, ddF] = dIso.split("-").map(Number);
        const jsDayF = new Date(yyF, mmF - 1, ddF).getDay();
        return `${jsDayF}_${halfKey}` === target;
      }
      function getPhInternePostesForHalfDay(iso, halfKey, jsDay) {
        const noInterneTheveninNov = (halfKey === "am" && jsDay === 3 && iso.startsWith("2026-11"));
        const baseReq = new Set(mandatoryWeeklyPostes[`${jsDay}_${halfKey}`] || []);
        if (noInterneTheveninNov) baseReq.delete("ECHO");
        const chDay = (st.chefsPlanning || {})[iso];
        if (!chDay || !Array.isArray(chDay[halfKey])) return baseReq;
        const openPostes = new Set();
        chDay[halfKey].forEach(entry => {
          const docVal = String(entry.doc || "").trim();
          const pChef = String(entry.poste || "").trim();
          const isClosed = Boolean(entry.closed) || docVal.toUpperCase().startsWith("FERM") || docVal.toUpperCase() === "MAINTENANCE";
          if (isClosed) return;
          if (chefToInterneMap[pChef]) {
            openPostes.add(chefToInterneMap[pChef]);
          } else if (pChef === "CONSULTATION" && halfKey === "pm" && (jsDay === 2 || jsDay === 5)) {
            openPostes.add("LECTURE/CS");
          }
        });
        const phSet = new Set();
        baseReq.forEach(p => {
          if (openPostes.has(p)) phSet.add(p);
        });
        return phSet;
      }

      // 1. Appliquer customVacations et absences jour par jour
      const weeksMap = {};
      Object.keys(baseSched).sort().forEach(iso => {
        const dayObj = JSON.parse(JSON.stringify(baseSched[iso]));
        const [yy, mm, dd] = iso.split("-").map(Number);
        const dt = new Date(yy, mm - 1, dd);
        const jsDay = dt.getDay(); // 1=Mon, 2=Tue, ..., 5=Fri
        const monIso = getMondayOfWeek(iso);
        if (!weeksMap[monIso]) weeksMap[monIso] = [];
        weeksMap[monIso].push(iso);

        if (!dayObj.holiday && dayObj.byInterne) {
          Object.keys(dayObj.byInterne).forEach(iid => {
            const intObj = st.internes.find(x => x.id === iid);
            const origSlot = dayObj.byInterne[iid] || {};
            const cKey = iso + "__" + iid;
            let am = origSlot.am;
            let pm = origSlot.pm;
            let noteAm = origSlot.noteAm || "";
            let notePm = origSlot.notePm || "";
            let note = origSlot.note || noteAm || notePm || "";
            let absStatus = null;
            const isSocle = Boolean(origSlot.isSocle || (intObj && intObj.isSocle));

            // Si un Repos de garde officiel avait été pré-intégré mais a été supprimé/refusé, restaurer le poste pré-RG
            if (!absLookup[cKey] && origSlot.am === "RG" && origSlot.preRgAm) {
              am = origSlot.preRgAm;
              pm = origSlot.preRgPm || origSlot.preRgAm;
              note = "";
              noteAm = "";
              notePm = "";
            }

            if (custom[cKey]) {
              const [yyC, mmC, ddC] = iso.split("-").map(Number);
              const jsDayC = new Date(yyC, mmC - 1, ddC).getDay();
              if (custom[cKey].am) am = custom[cKey].am;
              if (custom[cKey].pm && !((jsDayC === 2 || jsDayC === 5) && custom[cKey].pm === "1/2 journée libre")) {
                pm = custom[cKey].pm;
              }
              if (custom[cKey].note !== undefined) {
                note = custom[cKey].note;
                noteAm = custom[cKey].note;
              }
            }

            if (absLookup[cKey]) {
              const absInfo = absLookup[cKey];
              const at = absInfo.type;
              const badge = (at.toLowerCase().includes("garde") || at.toUpperCase() === "RG") ? "RG" : "VACANCES";
              am = badge;
              pm = badge;
              absStatus = absInfo.status || "pending";
              const noteTxt = (badge === "RG" && absInfo.comment) ? absInfo.comment : at;
              note = noteTxt;
              noteAm = noteTxt;
              notePm = noteTxt;
            }

            dayObj.byInterne[iid] = { am, pm, note, noteAm, notePm, isSocle, absStatus };
          });

          // Garantie impérative : il doit TOUJOURS y avoir au moins un interne senior au Scanner du SAU (TDM SAU) Matin & Après-midi
          // (hors matinée d'accueil et formation obligatoire du 02/11/2026)
          // en prélevant d'abord sur une vacation non obligatoire (hors 13 vacations prioritaires)
          const baseSauDonors = ["ALLURA", "TDM OLLIER DIAG", "IRM 1,5T", "SCAN ACHARD", "GESTES (C)", "ECHO", "IRM 3T", "IRM"];
          ["am", "pm"].forEach(hSau => {
            if (iso === "2026-11-02" && hSau === "am") return;
            const hasSauSenior = seniorIds.some(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId][hSau] === "TDM SAU");
            if (!hasSauSenior) {
              const nkSau = hSau === "am" ? "noteAm" : "notePm";
              const phSauSet = getPhInternePostesForHalfDay(iso, hSau, jsDay);
              const sauDonorOrder = [
                ...baseSauDonors.filter(d => !phSauSet.has(d)),
                ...baseSauDonors.filter(d => phSauSet.has(d)),
                "1/2 journée libre"
              ];
              let replacedSau = false;
              for (const allowCustomOverride of [false, true]) {
                for (const donorP of sauDonorOrder) {
                  for (const sId of seniorIds) {
                    const cKeySau = iso + "__" + sId;
                    if (!allowCustomOverride && custom[cKeySau] && custom[cKeySau][hSau]) continue;
                    const sl = dayObj.byInterne[sId];
                    if (sl && sl[hSau] === donorP) {
                      sl[hSau] = "TDM SAU";
                      sl[nkSau] = "Remplacement TDM SAU (permanence obligatoire)";
                      if (!sl.note) sl.note = sl[nkSau];
                      replacedSau = true;
                      break;
                    }
                  }
                  if (replacedSau) break;
                }
                if (replacedSau) break;
              }
            }
          });

          // Si un Repos de garde (RG) supplémentaire est posé un Mardi ou Vendredi, couvrir automatiquement LECTURE/CS
          // en prélevant d'abord sur une vacation non obligatoire
          if (jsDay === 2) {
            const hasTueCs = seniorIds.some(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId].pm === "LECTURE/CS");
            const anyRgToday = seniorIds.some(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId].pm === "RG");
            const anyVacToday = seniorIds.some(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId].pm === "VACANCES");
            if (!hasTueCs && anyRgToday && !anyVacToday) {
              const phTuePm = getPhInternePostesForHalfDay(iso, "pm", jsDay);
              const tueDonors = ["GESTES (C)", "ECHO", "SCAN ACHARD"];
              const orderedTueDonors = [...tueDonors.filter(d => !phTuePm.has(d)), ...tueDonors.filter(d => phTuePm.has(d))];
              for (const donorP of orderedTueDonors) {
                let rep = false;
                for (const sId of seniorIds) {
                  if (custom[iso + "__" + sId] && custom[iso + "__" + sId].pm) continue;
                  const sl = dayObj.byInterne[sId];
                  if (sl && sl.pm === donorP) {
                    sl.pm = "LECTURE/CS";
                    sl.notePm = "Relecture avec Pr Drapé (systématique)";
                    if (!sl.note) sl.note = sl.notePm;
                    rep = true;
                    break;
                  }
                }
                if (rep) break;
              }
            }
          }
          if (jsDay === 5) {
            const hasFriCs = seniorIds.some(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId].pm === "LECTURE/CS");
            const anyRgToday = seniorIds.some(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId].pm === "RG");
            if (!hasFriCs && anyRgToday) {
              const phFriPm = getPhInternePostesForHalfDay(iso, "pm", jsDay);
              for (const donorP of ["GESTES (C)", "IRM", "SCAN ACHARD"]) {
                if (phFriPm.has(donorP)) continue;
                let rep = false;
                for (const sId of seniorIds) {
                  if (custom[iso + "__" + sId] && custom[iso + "__" + sId].pm) continue;
                  const sl = dayObj.byInterne[sId];
                  if (sl && sl.pm === donorP) {
                    sl.pm = "LECTURE/CS";
                    sl.notePm = "Consultation Internes (Vendredi PM)";
                    if (!sl.note) sl.note = sl.notePm;
                    rep = true;
                    break;
                  }
                }
                if (rep) break;
              }
            }
          }
        }
        st.schedule[iso] = dayObj;
      });

      // 2. Garantie hebdomadaire :
      //    - Couverture stricte du TDM SAU permanent et des 13 vacations obligatoires prioritaires
      //    - Pose des 2 demi-offs en fonction (avec demi-journée fixe pour Oussama Lundi AM, Gabriel Mardi AM, Marwane Jeudi AM)
      //    - Équilibrage automatique sur les semaines suivantes (carryOverOffs) si < 2 demi-offs possibles sur une semaine chargée
      const nonMandatoryPriority = [
        "ALLURA",
        "GESTES (C)",
        "ECHO",
        "IRM 1,5T",
        "SCAN ACHARD",
        "TDM OLLIER DIAG",
        "IRM 3T",
        "IRM",
        "LECTURE/CS"
      ];
      const nonActivePostes = ["1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"];
      const carryOverOffs = {};
      const totalAmOffs = {};
      const totalPmOffs = {};
      (st.internes || []).forEach(intObj => {
        carryOverOffs[intObj.id] = 0;
        totalAmOffs[intObj.id] = 0;
        totalPmOffs[intObj.id] = 0;
      });

      Object.keys(weeksMap).sort().forEach(monIso => {
        const isWeekLocked = Boolean(lockedWeeks[monIso] && lockedWeeks[monIso].locked);
        const activeIsos = weeksMap[monIso].filter(dIso => st.schedule[dIso] && !st.schedule[dIso].holiday && st.schedule[dIso].byInterne);
        const countWeekHalfOffsJs = (interneId, halfKey) => {
          let cnt = 0;
          activeIsos.forEach(dChk => {
            const sl = st.schedule[dChk] && st.schedule[dChk].byInterne && st.schedule[dChk].byInterne[interneId];
            if (sl && sl[halfKey] === "1/2 journée libre") cnt++;
          });
          return cnt;
        };

        // 2A. Couverture des vacations obligatoires (TDM SAU + 13 vacations) sur chaque jour de la semaine
        activeIsos.forEach(iso => {
          const dayObj = st.schedule[iso];
          const [yy, mm, dd] = iso.split("-").map(Number);
          const jsDay = new Date(yy, mm - 1, dd).getDay();
          ["am", "pm"].forEach(h => {
            if (iso === "2026-11-02" && h === "am") return;
            const nk = h === "am" ? "noteAm" : "notePm";
            const phSet = getPhInternePostesForHalfDay(iso, h, jsDay);
            const hasSeniorSau = seniorIds.some(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId][h] === "TDM SAU");
            if (!hasSeniorSau) {
              const finalSauDonors = [
                ...nonMandatoryPriority.filter(d => !phSet.has(d)),
                "1/2 journée libre",
                ...nonMandatoryPriority.filter(d => phSet.has(d))
              ];
              const orderedSeniors = [
                ...seniorIds.filter(sId => !isProtectedFixedOff(sId, iso, h)),
                ...seniorIds.filter(sId => isProtectedFixedOff(sId, iso, h))
              ];
              let replaced = false;
              for (const allowCustomOverride of [false, true]) {
                for (const donorP of finalSauDonors) {
                  for (const sId of orderedSeniors) {
                    const cKeySau = iso + "__" + sId;
                    if (!allowCustomOverride && custom[cKeySau] && custom[cKeySau][h]) continue;
                    const sl = dayObj.byInterne[sId];
                    if (sl && sl[h] === donorP) {
                      sl[h] = "TDM SAU";
                      sl[nk] = "Remplacement TDM SAU (permanence obligatoire)";
                      if (!sl.note) sl.note = sl[nk];
                      replaced = true;
                      break;
                    }
                  }
                  if (replaced) break;
                }
                if (replaced) break;
              }
            }

            if (!isWeekLocked && !(iso === "2026-11-02" && h === "am")) {
              Array.from(phSet).sort().forEach(phPoste => {
                const allIds = Object.keys(dayObj.byInterne);
                const isCovered = allIds.some(anyId => dayObj.byInterne[anyId] && dayObj.byInterne[anyId][h] === phPoste);
                if (isCovered) return;
                let reassignedPh = false;
                const candIids = phPoste !== "TDM SAU" ? [...seniorIds, "noe"] : [...seniorIds];
                // A) Prélever sur une vacation non obligatoire
                for (const donorP of nonMandatoryPriority) {
                  if (phSet.has(donorP)) continue;
                  for (const candId of candIids) {
                    if (custom[iso + "__" + candId] && custom[iso + "__" + candId][h]) continue;
                    const sl = dayObj.byInterne[candId];
                    if (sl && sl[h] === donorP) {
                      sl[h] = phPoste;
                      sl[nk] = `Vacation obligatoire (${phPoste})`;
                      if (!sl.note) sl.note = sl[nk];
                      reassignedPh = true;
                      break;
                    }
                  }
                  if (reassignedPh) break;
                }
                // B) Binôme au TDM SAU
                if (!reassignedPh && phPoste !== "TDM SAU") {
                  const sauSeniors = seniorIds.filter(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId][h] === "TDM SAU");
                  if (sauSeniors.length >= 2) {
                    const donorSid = sauSeniors[sauSeniors.length - 1];
                    dayObj.byInterne[donorSid][h] = phPoste;
                    dayObj.byInterne[donorSid][nk] = `Vacation obligatoire (${phPoste})`;
                    reassignedPh = true;
                  } else if (sauSeniors.length >= 1 && dayObj.byInterne.noe && dayObj.byInterne.noe[h] === "TDM SAU") {
                    if (["ECHO", "IRM 3T", "IRM 1,5T", "IRM", "TDM OLLIER DIAG"].includes(phPoste)) {
                      dayObj.byInterne.noe[h] = phPoste;
                      dayObj.byInterne.noe[nk] = `Vacation obligatoire (${phPoste})`;
                      reassignedPh = true;
                    }
                  }
                }
                // C) Demi-off disponible (en sollicitant d'abord un interne ayant >1 off sur cette période AM/PM ou 2 offs le même jour)
                if (!reassignedPh) {
                  const otherH = h === "am" ? "pm" : "am";
                  const orderedOffCands = candIids
                    .filter(cid => dayObj.byInterne[cid] && dayObj.byInterne[cid][h] === "1/2 journée libre")
                    .sort((a, b) => {
                      const pa = isProtectedFixedOff(a, iso, h) ? 1 : 0;
                      const pb = isProtectedFixedOff(b, iso, h) ? 1 : 0;
                      if (pa !== pb) return pa - pb;
                      const sa = dayObj.byInterne[a][otherH] === "1/2 journée libre" ? 0 : 1;
                      const sb = dayObj.byInterne[b][otherH] === "1/2 journée libre" ? 0 : 1;
                      if (sa !== sb) return sa - sb;
                      const diffA = countWeekHalfOffsJs(a, h) - countWeekHalfOffsJs(a, otherH);
                      const diffB = countWeekHalfOffsJs(b, h) - countWeekHalfOffsJs(b, otherH);
                      return diffB - diffA;
                    });
                  for (const candId of orderedOffCands) {
                    if (custom[iso + "__" + candId] && custom[iso + "__" + candId][h]) continue;
                    const sl = dayObj.byInterne[candId];
                    if (sl && sl[h] === "1/2 journée libre") {
                      sl[h] = phPoste;
                      sl[nk] = `Vacation obligatoire (${phPoste})`;
                      if (!sl.note) sl.note = sl[nk];
                      reassignedPh = true;
                      break;
                    }
                  }
                }
              });
            }
          });
        });

        // 2B. Ajustement des demi-offs (en alternant Matin / Après-midi : 1 AM + 1 PM par semaine) et équilibrage multi-semaines
        if (!isWeekLocked) {
          (st.internes || []).forEach(intObj => {
            const iid = intObj.id;
            let vacHalfDays = 0;
            let offCnt = 0;
            activeIsos.forEach(dIso => {
              const slot = st.schedule[dIso].byInterne[iid];
              if (!slot) return;
              ["am", "pm"].forEach(h => {
                if (slot[h] === "VACANCES" || slot[h] === "RG") vacHalfDays++;
                else if (slot[h] === "1/2 journée libre") offCnt++;
              });
            });
            if (vacHalfDays >= 6) return;
            const targetOffs = Math.min(3, 2 + (carryOverOffs[iid] || 0));

            while (offCnt < targetOffs) {
              let freed = false;
              const isRattrapage = offCnt >= 2;
              const wAm = countWeekHalfOffsJs(iid, "am");
              const wPm = countWeekHalfOffsJs(iid, "pm");
              let preferredH = "pm";
              if (wAm < wPm) preferredH = "am";
              else if (wPm < wAm) preferredH = "pm";
              else if ((totalAmOffs[iid] || 0) + wAm < (totalPmOffs[iid] || 0) + wPm) preferredH = "am";
              else if ((totalPmOffs[iid] || 0) + wPm < (totalAmOffs[iid] || 0) + wAm) preferredH = "pm";
              else preferredH = fixedOffHalfDays[iid] ? "am" : "pm";

              const rawCands = [];
              for (let i = activeIsos.length - 1; i >= 0; i--) {
                const dIso = activeIsos[i];
                if (dIso === "2026-11-02") continue;
                const [yy, mm, dd] = dIso.split("-").map(Number);
                const jsDay = new Date(yy, mm - 1, dd).getDay();
                for (const h of ["pm", "am"]) {
                  if (h === "pm" && jsDay === 2) continue;
                  const slChk = st.schedule[dIso].byInterne[iid];
                  if (!slChk || nonActivePostes.includes(slChk[h])) continue;
                  rawCands.push([dIso, h, jsDay]);
                }
              }

              const slotCandidates = rawCands.slice().sort((a, b) => {
                const friA = (a[2] === 5 && a[1] === "pm") ? 1 : 0;
                const friB = (b[2] === 5 && b[1] === "pm") ? 1 : 0;
                if (friA !== friB) return friA - friB;
                const othA = a[1] === "am" ? "pm" : "am";
                const othB = b[1] === "am" ? "pm" : "am";
                const sameDayA = st.schedule[a[0]].byInterne[iid][othA] === "1/2 journée libre" ? 1 : 0;
                const sameDayB = st.schedule[b[0]].byInterne[iid][othB] === "1/2 journée libre" ? 1 : 0;
                if (sameDayA !== sameDayB) return sameDayA - sameDayB;
                const prefA = a[1] === preferredH ? 0 : 1;
                const prefB = b[1] === preferredH ? 0 : 1;
                if (prefA !== prefB) return prefA - prefB;
                const fixA = isProtectedFixedOff(iid, a[0], a[1]) ? 0 : 1;
                const fixB = isProtectedFixedOff(iid, b[0], b[1]) ? 0 : 1;
                return fixA - fixB;
              });

              for (const [dIso, h, jsDay] of slotCandidates) {
                const cKey = dIso + "__" + iid;
                if (custom[cKey] && custom[cKey][h]) continue;
                const phSet = getPhInternePostesForHalfDay(dIso, h, jsDay);
                const byInt = st.schedule[dIso].byInterne;
                const slot = byInt[iid];
                if (!slot || nonActivePostes.includes(slot[h])) continue;

                // Passe 1 : libérer directement une vacation non obligatoire
                for (const candPoste of nonMandatoryPriority) {
                  if (phSet.has(candPoste)) continue;
                  if (slot[h] === candPoste) {
                    const nk = h === "am" ? "noteAm" : "notePm";
                    slot[h] = "1/2 journée libre";
                    slot[nk] = isRattrapage
                      ? "Demi-off de rattrapage (équilibrage semaine précédente)"
                      : (isProtectedFixedOff(iid, dIso, h) ? "Demi-journée off fixe hebdomadaire" : "Demi-off hebdomadaire (hors vacations obligatoires)");
                    if (!slot.note) slot.note = slot[nk];
                    offCnt++;
                    freed = true;
                    break;
                  }
                }
                if (freed) break;

                // Passe 2 : échanger sur la même demi-journée avec un co-interne senior occupant une vacation non obligatoire
                if (seniorIds.includes(iid)) {
                  for (const candNonMand of nonMandatoryPriority) {
                    if (phSet.has(candNonMand)) continue;
                    for (const otherId of seniorIds) {
                      if (otherId === iid) continue;
                      if (custom[dIso + "__" + otherId] && custom[dIso + "__" + otherId][h]) continue;
                      if (byInt[otherId] && byInt[otherId][h] === candNonMand) {
                        const nk = h === "am" ? "noteAm" : "notePm";
                        byInt[otherId][h] = slot[h];
                        slot[h] = "1/2 journée libre";
                        slot[nk] = isRattrapage
                          ? "Demi-off de rattrapage (équilibrage semaine précédente)"
                          : (isProtectedFixedOff(iid, dIso, h) ? "Demi-journée off fixe hebdomadaire" : "Demi-off hebdomadaire (équilibré)");
                        if (!slot.note) slot.note = slot[nk];
                        offCnt++;
                        freed = true;
                        break;
                      }
                    }
                    if (freed) break;
                  }
                }
                if (freed) break;
              }
              if (!freed) break;
            }

            totalAmOffs[iid] = (totalAmOffs[iid] || 0) + countWeekHalfOffsJs(iid, "am");
            totalPmOffs[iid] = (totalPmOffs[iid] || 0) + countWeekHalfOffsJs(iid, "pm");
            carryOverOffs[iid] = Math.max(0, (carryOverOffs[iid] || 0) + (2 - offCnt));
          });

          // 2B-bis. Quotas hebdomadaires (TDM SAU & IRM d'après-midi max 1/sem) + Règle Matin != Après-midi :
          //   - 2 TDM SAU / semaine pour les 5 internes seniors (3 uniquement à titre exceptionnel en cas de congés/RG)
          //   - 3 TDM SAU / semaine pour Noé (Phase Socle), plus uniquement exceptionnellement
          //   - Maximum 1 IRM d'après-midi ("IRM" en PM) par semaine par interne (sauf exception)
          //   - Interdiction pour un interne de faire le même poste toute la journée (am !== pm)
          const countWeekSauJs = (interneId) => {
            let cnt = 0;
            activeIsos.forEach(dChk => {
              const sl = st.schedule[dChk] && st.schedule[dChk].byInterne && st.schedule[dChk].byInterne[interneId];
              if (!sl) return;
              if (sl.am === "TDM SAU") cnt++;
              if (sl.pm === "TDM SAU") cnt++;
            });
            return cnt;
          };

          const countWeekIrmPmJs = (interneId) => {
            let cnt = 0;
            activeIsos.forEach(dChk => {
              const sl = st.schedule[dChk] && st.schedule[dChk].byInterne && st.schedule[dChk].byInterne[interneId];
              if (sl && sl.pm === "IRM") cnt++;
            });
            return cnt;
          };

          const isSamePosteDayJs = (pAm, pPm) => {
            if (!pAm || !pPm || nonActivePostes.includes(pAm) || nonActivePostes.includes(pPm)) return false;
            return pAm === pPm;
          };

          for (let iter = 0; iter < 25; iter++) {
            const sauCounts = {};
            seniorIds.forEach(sId => { sauCounts[sId] = countWeekSauJs(sId); });
            const overSids = seniorIds.filter(sId => sauCounts[sId] > 2).sort((a, b) => sauCounts[b] - sauCounts[a]);
            if (!overSids.length) break;
            let swappedSau = false;

            for (const overSid of overSids) {
              let underSids = seniorIds.filter(sId => sauCounts[sId] < 2).sort((a, b) => sauCounts[a] - sauCounts[b]);
              if (sauCounts[overSid] > 3) {
                underSids = [...underSids, ...seniorIds.filter(sId => sauCounts[sId] === 2)];
              }
              // 1. Échange direct sur la même demi-journée
              for (const underSid of underSids) {
                for (const dIso of activeIsos) {
                  if (dIso === "2026-11-02") continue;
                  const byInt = st.schedule[dIso].byInterne;
                  for (const h of ["am", "pm"]) {
                    const otherH = h === "am" ? "pm" : "am";
                    if (custom[dIso + "__" + overSid] && custom[dIso + "__" + overSid][h]) continue;
                    if (custom[dIso + "__" + underSid] && custom[dIso + "__" + underSid][h]) continue;
                    if (!byInt[overSid] || byInt[overSid][h] !== "TDM SAU") continue;
                    const otherP = byInt[underSid] ? byInt[underSid][h] : "";
                    if (!otherP || nonActivePostes.includes(otherP) || otherP === "TDM SAU") continue;
                    if (isSamePosteDayJs(otherP, byInt[overSid][otherH]) || isSamePosteDayJs("TDM SAU", byInt[underSid][otherH])) continue;
                    if (h === "pm" && otherP === "IRM" && countWeekIrmPmJs(overSid) >= 1) continue;
                    const nk = h === "am" ? "noteAm" : "notePm";
                    const otherNote = byInt[underSid][nk] || "";
                    byInt[overSid][h] = otherP;
                    byInt[overSid][nk] = otherNote;
                    byInt[underSid][h] = "TDM SAU";
                    byInt[underSid][nk] = "";
                    swappedSau = true;
                    break;
                  }
                  if (swappedSau) break;
                }
                if (swappedSau) break;
              }
              if (swappedSau) break;

              // 2. Échange en 2 étapes via un senior intermédiaire (midSid)
              for (const underSid of underSids) {
                for (const midSid of seniorIds) {
                  if (midSid === overSid || midSid === underSid) continue;
                  let step1 = null;
                  for (const dIso of activeIsos) {
                    if (dIso === "2026-11-02") continue;
                    const byInt = st.schedule[dIso].byInterne;
                    for (const h of ["am", "pm"]) {
                      const otherH = h === "am" ? "pm" : "am";
                      if (custom[dIso + "__" + overSid] && custom[dIso + "__" + overSid][h]) continue;
                      if (custom[dIso + "__" + midSid] && custom[dIso + "__" + midSid][h]) continue;
                      if (byInt[overSid] && byInt[overSid][h] === "TDM SAU" && byInt[midSid] && !nonActivePostes.includes(byInt[midSid][h]) && byInt[midSid][h] !== "TDM SAU") {
                        const pMid = byInt[midSid][h];
                        if (isSamePosteDayJs(pMid, byInt[overSid][otherH]) || isSamePosteDayJs("TDM SAU", byInt[midSid][otherH])) continue;
                        if (h === "pm" && pMid === "IRM" && countWeekIrmPmJs(overSid) >= 1) continue;
                        step1 = [dIso, h];
                        break;
                      }
                    }
                    if (step1) break;
                  }
                  if (!step1) continue;
                  let step2 = null;
                  for (const dIso of activeIsos) {
                    if (dIso === "2026-11-02") continue;
                    const byInt = st.schedule[dIso].byInterne;
                    for (const h of ["am", "pm"]) {
                      if (dIso === step1[0] && h === step1[1]) continue;
                      const otherH = h === "am" ? "pm" : "am";
                      if (custom[dIso + "__" + midSid] && custom[dIso + "__" + midSid][h]) continue;
                      if (custom[dIso + "__" + underSid] && custom[dIso + "__" + underSid][h]) continue;
                      if (byInt[midSid] && byInt[midSid][h] === "TDM SAU" && byInt[underSid] && !nonActivePostes.includes(byInt[underSid][h]) && byInt[underSid][h] !== "TDM SAU") {
                        const pUnd = byInt[underSid][h];
                        if (isSamePosteDayJs(pUnd, byInt[midSid][otherH]) || isSamePosteDayJs("TDM SAU", byInt[underSid][otherH])) continue;
                        if (h === "pm" && pUnd === "IRM" && countWeekIrmPmJs(midSid) >= 1) continue;
                        step2 = [dIso, h];
                        break;
                      }
                    }
                    if (step2) break;
                  }
                  if (step1 && step2) {
                    const [d1, h1] = step1;
                    const nk1 = h1 === "am" ? "noteAm" : "notePm";
                    const by1 = st.schedule[d1].byInterne;
                    const p1 = by1[midSid][h1], n1 = by1[midSid][nk1] || "";
                    by1[overSid][h1] = p1;
                    by1[overSid][nk1] = n1;
                    by1[midSid][h1] = "TDM SAU";
                    by1[midSid][nk1] = "";

                    const [d2, h2] = step2;
                    const nk2 = h2 === "am" ? "noteAm" : "notePm";
                    const by2 = st.schedule[d2].byInterne;
                    const p2 = by2[underSid][h2], n2 = by2[underSid][nk2] || "";
                    by2[midSid][h2] = p2;
                    by2[midSid][nk2] = n2;
                    by2[underSid][h2] = "TDM SAU";
                    by2[underSid][nk2] = "";
                    swappedSau = true;
                    break;
                  }
                }
                if (swappedSau) break;
              }
              if (swappedSau) break;
            }
            if (!swappedSau) break;
          }

          // 2B-ter. Règle des IRM d'après-midi : maximum 1 IRM PM par semaine par interne (sauf exception)
          const allIidsJs = (st.internes || []).map(x => x.id);
          for (let iterIrm = 0; iterIrm < 20; iterIrm++) {
            const irmCounts = {};
            allIidsJs.forEach(id => { irmCounts[id] = countWeekIrmPmJs(id); });
            const overIrmIds = allIidsJs.filter(id => irmCounts[id] > 1);
            if (!overIrmIds.length) break;
            let swappedIrm = false;
            for (const overId of overIrmIds) {
              const zeroIrmIds = allIidsJs.filter(id => irmCounts[id] === 0 && id !== overId);
              for (const dIso of activeIsos) {
                if (dIso === "2026-11-02") continue;
                if (custom[dIso + "__" + overId] && custom[dIso + "__" + overId].pm) continue;
                const byInt = st.schedule[dIso].byInterne;
                if (!byInt[overId] || byInt[overId].pm !== "IRM") continue;
                for (const candId of zeroIrmIds) {
                  if (custom[dIso + "__" + candId] && custom[dIso + "__" + candId].pm) continue;
                  if (!byInt[candId]) continue;
                  const candPm = byInt[candId].pm;
                  if (!candPm || nonActivePostes.includes(candPm) || candPm === "IRM") continue;
                  if (candPm === "TDM SAU" && (candId === "noe" || overId === "noe" || countWeekSauJs(overId) >= 2)) continue;
                  if (isSamePosteDayJs(byInt[overId].am, candPm) || isSamePosteDayJs(byInt[candId].am, "IRM")) continue;
                  const nOver = byInt[overId].notePm || "";
                  const nCand = byInt[candId].notePm || "";
                  byInt[overId].pm = candPm;
                  byInt[overId].notePm = nCand;
                  byInt[candId].pm = "IRM";
                  byInt[candId].notePm = nOver;
                  swappedIrm = true;
                  break;
                }
                if (swappedIrm) break;
              }
              if (swappedIrm) break;
            }
            if (!swappedIrm) break;
          }

          // 2B-quater. Règle stricte : un interne ne peut pas faire le même poste toute la journée (am !== pm)
          for (let iterSame = 0; iterSame < 25; iterSame++) {
            let fixedSame = false;
            for (const dIso of activeIsos) {
              const byInt = st.schedule[dIso].byInterne;
              for (const iid of allIidsJs) {
                const sl = byInt[iid];
                if (!sl || !isSamePosteDayJs(sl.am, sl.pm)) continue;
                for (const h of ["pm", "am"]) {
                  if (dIso === "2026-11-02" && h === "am") continue;
                  if (custom[dIso + "__" + iid] && custom[dIso + "__" + iid][h]) continue;
                  const otherH = h === "am" ? "pm" : "am";
                  const curP = sl[h];
                  const swapPool = seniorIds.includes(iid) ? seniorIds : allIidsJs;
                  for (const otherId of swapPool) {
                    if (otherId === iid) continue;
                    if (custom[dIso + "__" + otherId] && custom[dIso + "__" + otherId][h]) continue;
                    const oSl = byInt[otherId];
                    if (!oSl) continue;
                    const candP = oSl[h];
                    if (!candP || nonActivePostes.includes(candP) || candP === curP) continue;
                    if ((curP === "TDM SAU" || candP === "TDM SAU") && (iid === "noe" || otherId === "noe")) continue;
                    if (isSamePosteDayJs(candP, sl[otherH]) || isSamePosteDayJs(curP, oSl[otherH])) continue;
                    if (h === "pm" && candP === "IRM" && countWeekIrmPmJs(iid) >= 1) continue;
                    if (h === "pm" && curP === "IRM" && countWeekIrmPmJs(otherId) >= 1) continue;
                    const nk = h === "am" ? "noteAm" : "notePm";
                    const n1 = sl[nk] || "";
                    const n2 = oSl[nk] || "";
                    sl[h] = candP;
                    sl[nk] = n2;
                    oSl[h] = curP;
                    oSl[nk] = n1;
                    fixedSame = true;
                    break;
                  }
                  if (fixedSame) break;
                }
                if (fixedSame) break;
              }
              if (fixedSame) break;
            }
            if (!fixedSame) break;
          }
        }

        // 2C. Mise à jour des notes de binôme de Noé (Phase Socle)
        activeIsos.forEach(iso => {
          const dayObj = st.schedule[iso];
          const [yy, mm, dd] = iso.split("-").map(Number);
          const jsDay = new Date(yy, mm - 1, dd).getDay();
          ["am", "pm"].forEach(h => {
            const nk = h === "am" ? "noteAm" : "notePm";
            if (!dayObj.byInterne.noe) return;
            const noeSlot = dayObj.byInterne.noe;
            const noeP = noeSlot[h];
            if (!noeP || nonActivePostes.includes(noeP)) return;
            if (noeP === "TDM SAU") {
              const sauPartners = seniorIds
                .filter(sId => dayObj.byInterne[sId] && dayObj.byInterne[sId][h] === "TDM SAU")
                .map(sId => {
                  const iObj = (st.internes || []).find(x => x.id === sId);
                  return iObj ? iObj.shortName : sId;
                });
              if (sauPartners.length > 0) {
                const pStr = sauPartners.join(" & ");
                if (h === "am" && (jsDay === 2 || jsDay === 4)) {
                  noeSlot[nk] = `Avec Dr Macil HAMADOUCHE (MH) • Binôme SAU avec ${pStr}`;
                } else {
                  noeSlot[nk] = `Posté Socle Urgences • Binôme SAU avec ${pStr}`;
                }
              }
            }
          });
          if (dayObj.byInterne.noe) {
            const noeSlot = dayObj.byInterne.noe;
            if (iso !== "2026-11-02" && !nonActivePostes.includes(noeSlot.am) && !nonActivePostes.includes(noeSlot.pm)) {
              noeSlot.note = [noeSlot.noteAm, noeSlot.notePm].filter(Boolean).join(" • ");
            }
          }
        });
      });

      // 3. Reconstruire dayObj.am, dayObj.pm et dayObj.slots
      Object.keys(st.schedule).forEach(iso => {
        const dayObj = st.schedule[iso];
        if (!dayObj || dayObj.holiday || !dayObj.byInterne) return;
        const amCounts = {};
        const pmCounts = {};
        Object.keys(dayObj.byInterne).forEach(iid => {
          const sl = dayObj.byInterne[iid];
          if (sl.am && !["1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"].includes(sl.am)) {
            amCounts[sl.am] = (amCounts[sl.am] || 0) + 1;
          }
          if (sl.pm && !["1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"].includes(sl.pm)) {
            pmCounts[sl.pm] = (pmCounts[sl.pm] || 0) + 1;
          }
        });
        dayObj.am = [];
        dayObj.pm = [];
        Object.keys(dayObj.byInterne).forEach(iid => {
          const intObj = st.internes.find(x => x.id === iid);
          const slot = dayObj.byInterne[iid];
          const isSocle = Boolean(slot.isSocle || (intObj && intObj.isSocle));
          dayObj.am.push({
            poste: slot.am,
            interneId: iid,
            interne: intObj ? intObj.shortName : iid,
            isSocle,
            binome: isSocle && (amCounts[slot.am] > 1),
            note: slot.noteAm || "",
            absStatus: slot.absStatus || null
          });
          dayObj.pm.push({
            poste: slot.pm,
            interneId: iid,
            interne: intObj ? intObj.shortName : iid,
            isSocle,
            binome: isSocle && (pmCounts[slot.pm] > 1),
            note: slot.notePm || "",
            absStatus: slot.absStatus || null
          });
        });
        (dayObj.closedAm || []).forEach(cl => {
          dayObj.am.push({
            poste: cl.poste,
            interneId: null,
            interne: cl.reason || cl.status || "FERMÉ",
            closed: true,
            reason: cl.reason || cl.status || "FERMÉ"
          });
        });
        (dayObj.closedPm || []).forEach(cl => {
          dayObj.pm.push({
            poste: cl.poste,
            interneId: null,
            interne: cl.reason || cl.status || "FERMÉ",
            closed: true,
            reason: cl.reason || cl.status || "FERMÉ"
          });
        });
        dayObj.slots = dayObj.byInterne;
      });
    }

    function computeStatsByInterne(overrideSlot) {
      const stats = {};
      STATE.internes.forEach(i => {
        stats[i.id] = {
          activeHalfDays: 0,
          freeHalfDays: 0,
          freeAmHalfDays: 0,
          freePmHalfDays: 0,
          vacHalfDays: 0,
          rgHalfDays: 0,
          gardesCount: 0,
          gardesWeekendCount: 0,
          casMardi: 0,
          biblioVendredi: 0,
          coursInternes: 0,
          byModality: { TDM_SAU: 0, SCAN_ACHARD: 0, TDM_OLLIER: 0, TDM: 0, IRM_AM: 0, IRM_PM: 0, IRM: 0, ECHO: 0, RI_GESTES: 0, LECTURE_CS: 0 }
        };
      });

      Object.keys(STATE.interneGardes || {}).forEach(gIso => {
        const g = STATE.interneGardes[gIso];
        if (g && g.interneId && stats[g.interneId]) {
          stats[g.interneId].gardesCount++;
          const [yy, mm, dd] = gIso.split("-").map(Number);
          const wd = new Date(yy, mm - 1, dd).getDay();
          if (wd === 0 || wd === 6) {
            stats[g.interneId].gardesWeekendCount++;
          }
        }
      });

      Object.keys(STATE.schedule).forEach(iso => {
        const d = STATE.schedule[iso];
        if (!d || d.holiday || !d.byInterne) return;
        Object.keys(d.byInterne).forEach(iid => {
          if (!stats[iid]) return;
          const isOver = Boolean(overrideSlot && overrideSlot.iso === iso && overrideSlot.iid === iid);
          const slots = isOver
            ? [["am", overrideSlot.am], ["pm", overrideSlot.pm]]
            : [["am", d.byInterne[iid].am], ["pm", d.byInterne[iid].pm]];
          slots.forEach(([hKey, p]) => {
            const up = String(p || "").toUpperCase();
            if (up.includes("LIBRE")) {
              stats[iid].freeHalfDays++;
              if (hKey === "am") stats[iid].freeAmHalfDays++;
              else stats[iid].freePmHalfDays++;
            } else if (up === "VACANCES") {
              stats[iid].vacHalfDays++;
            } else if (up === "RG") {
              stats[iid].rgHalfDays++;
            } else if (up !== "FÉRIÉ" && !up.includes("FORMATION")) {
              stats[iid].activeHalfDays++;
              if (up.includes("IRM")) {
                stats[iid].byModality.IRM++;
                if (hKey === "pm") stats[iid].byModality.IRM_PM++;
                else stats[iid].byModality.IRM_AM++;
              }
              else if (up.includes("ECHO")) stats[iid].byModality.ECHO++;
              else if (up.includes("ACHARD")) stats[iid].byModality.SCAN_ACHARD++;
              else if (up.includes("OLLIER DIAG") || up.includes("OLLIER 3") || up === "TDM OLLIER" || up === "SCAN OLLIER") {
                stats[iid].byModality.TDM_OLLIER++;
                stats[iid].byModality.TDM++;
              }
              else if (up.includes("SAU") || up.includes("OLLIER 4")) {
                stats[iid].byModality.TDM_SAU++;
                stats[iid].byModality.TDM++;
              }
              else if (up.includes("GESTES") || up.includes("ALLURA")) stats[iid].byModality.RI_GESTES++;
              else if (up.includes("LECTURE") || up.includes("CS")) stats[iid].byModality.LECTURE_CS++;
              else stats[iid].byModality.TDM++;
            }
          });
        });
      });

      (STATE.presentations || []).forEach(pr => {
        if (pr.interneId && stats[pr.interneId]) {
          if (pr.type === "cas_mardi") stats[pr.interneId].casMardi++;
          if (pr.type === "biblio_vendredi") stats[pr.interneId].biblioVendredi++;
          if (pr.type === "cours_internes") stats[pr.interneId].coursInternes++;
        }
      });

      return stats;
    }

    function computeWeekStatsByInterne(monIso, overrideSlot) {
      const targetMon = monIso || getMondayOfWeek(currentDateIso);
      const dayLabels = ["Lun", "Mar", "Mer", "Jeu", "Ven"];
      const weekStats = {};
      STATE.internes.forEach(i => {
        weekStats[i.id] = {
          weekVac: 0,
          weekOff: 0,
          weekOffSlots: [],
          weekSau: 0,
          weekAchard: 0,
          weekOllier: 0,
          weekIrmAm: 0,
          weekIrmPm: 0,
          sauTarget: i.isSocle ? 3 : 2,
          weekCongesHalf: 0,
          weekRgHalf: 0
        };
      });

      for (let off = 0; off < 5; off++) {
        const dIso = addDaysIso(targetMon, off);
        const dObj = STATE.schedule[dIso];
        if (!dObj || dObj.holiday || !dObj.byInterne) continue;
        STATE.internes.forEach(i => {
          const iid = i.id;
          const isOver = Boolean(overrideSlot && overrideSlot.iso === dIso && overrideSlot.iid === iid);
          const rawSlot = dObj.byInterne[iid];
          if (!rawSlot && !isOver) return;
          const am = isOver ? overrideSlot.am : rawSlot.am;
          const pm = isOver ? overrideSlot.pm : rawSlot.pm;
          [["am", am, "Mat"], ["pm", pm, "PM"]].forEach(([hKey, pVal, hShort]) => {
            const up = String(pVal || "").toUpperCase();
            if (up.includes("LIBRE")) {
              weekStats[iid].weekOff++;
              weekStats[iid].weekOffSlots.push(`${dayLabels[off]} ${hShort}`);
            } else if (up === "VACANCES") {
              weekStats[iid].weekCongesHalf++;
            } else if (up === "RG") {
              weekStats[iid].weekRgHalf++;
            } else if (up !== "FÉRIÉ") {
              weekStats[iid].weekVac++;
              if (up.includes("SAU") || up.includes("OLLIER 4")) weekStats[iid].weekSau++;
              else if (up.includes("ACHARD")) weekStats[iid].weekAchard++;
              else if (up.includes("OLLIER DIAG") || up.includes("OLLIER 3") || up === "TDM OLLIER") weekStats[iid].weekOllier++;
              else if (up.includes("IRM")) {
                if (hKey === "pm") weekStats[iid].weekIrmPm++;
                else weekStats[iid].weekIrmAm++;
              }
            }
          });
        });
      }

      return weekStats;
    }

    function toggleChefOffVacSummary() {
      showChefOffVacSummary = !showChefOffVacSummary;
      renderChefModeUI();
    }

    function renderChefOffVacSummaryHtml(monIso) {
      const targetMon = monIso || getMondayOfWeek(currentDateIso);
      const weekStats = computeWeekStatsByInterne(targetMon);

      let cardsHtml = "";
      STATE.internes.forEach(i => {
        const w = weekStats[i.id] || { weekVac: 0, weekOff: 0, weekOffSlots: [], weekSau: 0, weekIrmPm: 0, sauTarget: i.isSocle ? 3 : 2, weekCongesHalf: 0, weekRgHalf: 0 };
        const absHalf = w.weekCongesHalf + w.weekRgHalf;
        const isFullWeekAbs = absHalf >= 8;

        let offPillClass = "off-ok";
        let cardQuotaClass = "";
        if (w.weekOff > 2) {
          offPillClass = "off-danger";
          cardQuotaClass = "danger-quota";
        } else if (w.weekOff < 2 && absHalf < 6) {
          offPillClass = "off-warn";
          cardQuotaClass = "warn-quota";
        }
        const sauPillClass = w.weekSau > w.sauTarget ? "off-warn" : "off-ok";
        const irmPmPillClass = w.weekIrmPm > 1 ? "off-warn" : "off-ok";

        const slotParts = [];
        if (w.weekOffSlots.length > 0) slotParts.push(`Off : ${w.weekOffSlots.join(" • ")}`);
        if (w.weekCongesHalf > 0) slotParts.push(`${w.weekCongesHalf / 2}j Congé`);
        if (w.weekRgHalf > 0) slotParts.push(`${w.weekRgHalf / 2}j RG`);
        const offSlotsLabel = slotParts.length > 0
          ? slotParts.join(" • ")
          : (isFullWeekAbs ? "En congés / RG" : "⚠️ 0 demi-off");

        cardsHtml += `
          <div class="chef-offvac-card ${cardQuotaClass}" onclick="openVacationEditModal('${currentDateIso}', '${i.id}')" title="Modifier les postes de ${i.fullName}">
            <div class="chef-offvac-top">
              <div class="chef-offvac-name">
                <span style="width:7px;height:7px;border-radius:50%;background:${i.color};display:inline-block;flex-shrink:0;"></span>
                <span>${i.shortName}</span>
              </div>
              <div class="chef-offvac-badges">
                <span class="offvac-pill ${offPillClass}">${w.weekOff}/2 Off</span>
                <span class="offvac-pill ${sauPillClass}" title="Quota Scanner SAU : ${w.sauTarget} / semaine (plus exceptionnellement)">${w.weekSau}/${w.sauTarget} SAU</span>
                <span class="offvac-pill ${irmPmPillClass}" title="Quota IRM d'après-midi : max 1 / semaine (sauf exception)">${w.weekIrmPm}/1 IRM PM</span>
                <span class="offvac-pill vac-count">${w.weekVac}v</span>
              </div>
            </div>
            <div class="chef-offvac-slots" title="${offSlotsLabel}">${offSlotsLabel}</div>
          </div>
        `;
      });

      return `
        <div class="chef-offvac-section">
          <div class="chef-offvac-grid">${cardsHtml}</div>
        </div>
      `;
    }

    function formatDateFr(iso, withYear = false) {
      if (!iso) return "";
      const [y, m, d] = iso.split("-").map(Number);
      const dt = new Date(y, m - 1, d);
      const days = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"];
      const months = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];
      return `${days[dt.getDay()]} ${d} ${months[m - 1]}${withYear ? " " + y : ""}`;
    }

    function formatShortDayHeader(iso) {
      if (!iso) return "";
      const [y, m, d] = iso.split("-").map(Number);
      const dt = new Date(y, m - 1, d);
      const days = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"];
      const dd = String(d).padStart(2, "0");
      const mm = String(m).padStart(2, "0");
      return `${days[dt.getDay()]} ${dd}/${mm}`;
    }

    function getMondayOfWeek(iso) {
      const [y, m, d] = iso.split("-").map(Number);
      const dt = new Date(y, m - 1, d, 12, 0, 0);
      const day = dt.getDay();
      const diff = (day === 0 ? -6 : 1 - day);
      dt.setDate(dt.getDate() + diff);
      const yy = dt.getFullYear();
      const mm = String(dt.getMonth() + 1).padStart(2, "0");
      const dd = String(dt.getDate()).padStart(2, "0");
      return `${yy}-${mm}-${dd}`;
    }

    function addDaysIso(iso, delta) {
      const [y, m, d] = iso.split("-").map(Number);
      const dt = new Date(y, m - 1, d);
      dt.setDate(dt.getDate() + delta);
      const yy = dt.getFullYear();
      const mm = String(dt.getMonth() + 1).padStart(2, "0");
      const dd = String(dt.getDate()).padStart(2, "0");
      return `${yy}-${mm}-${dd}`;
    }

    function isChefId(id) {
      return String(id || "").startsWith("chef_");
    }

    function getChefById(cid) {
      const list = STATE.chefs || [];
      return list.find(c => c.id === cid) || list[0] || {
        id: "chef_tl", code: "TL", prenom: "Thomas", nom: "LEFÈVRE",
        fullName: "Dr Thomas LEFÈVRE", shortName: "Dr T. Lefèvre",
        initials: "TL", color: "#0284C7", role: "Chef de Clinique"
      };
    }

    function doesDocMatchChef(docStr, chef) {
      if (!docStr || !chef) return false;
      const up = String(docStr).toUpperCase();
      const code = String(chef.code || "").toUpperCase();
      const nom = String(chef.nom || "").toUpperCase();
      const re = new RegExp("(^|[^A-Z])" + code + "([^A-Z]|$)");
      if (re.test(up)) return true;
      if (nom && up.includes(nom)) return true;
      if (code === "MIHOUBI" && (up.includes("MD") || up.includes("MIHOUBI"))) return true;
      return false;
    }

    function getChefSlotsForDate(iso, chef) {
      const ch = (STATE.chefsPlanning && STATE.chefsPlanning[iso]) ? STATE.chefsPlanning[iso] : { am: [], pm: [] };
      const am = (ch.am || []).filter(x => doesDocMatchChef(x.doc, chef)).map(x => x.poste);
      const pm = (ch.pm || []).filter(x => doesDocMatchChef(x.doc, chef)).map(x => x.poste);
      const g = (STATE.chefsGardes && STATE.chefsGardes[iso]) ? STATE.chefsGardes[iso] : null;
      let isGarde = false;
      if (g && Array.isArray(g.noms)) {
        const matches = chef.gardeMatch || [chef.nom];
        isGarde = g.noms.some(n => matches.some(m => String(n).toUpperCase().includes(String(m).toUpperCase())));
      }
      return { am, pm, isGarde, gardeNature: g ? g.nature : "" };
    }

    function computeChefStats(chef) {
      let totalHalfDays = 0;
      let gardesCount = 0;
      let coursMardiCount = 0;
      Object.keys(STATE.chefsPlanning || {}).forEach(iso => {
        const sl = getChefSlotsForDate(iso, chef);
        if (sl.am.length > 0) totalHalfDays++;
        if (sl.pm.length > 0) totalHalfDays++;
      });
      Object.keys(STATE.chefsGardes || {}).forEach(iso => {
        const g = STATE.chefsGardes[iso];
        if (g && Array.isArray(g.noms)) {
          const matches = chef.gardeMatch || [chef.nom];
          if (g.noms.some(n => matches.some(m => String(n).toUpperCase().includes(String(m).toUpperCase())))) {
            gardesCount++;
          }
        }
      });
      (STATE.presentations || []).forEach(p => {
        if (p.chefIntervenant && String(p.chefIntervenant).toUpperCase().includes(String(chef.nom).toUpperCase())) {
          coursMardiCount++;
        }
      });
      return { totalHalfDays, gardesCount, coursMardiCount };
    }

    /* =========================================================================
     * DÉTECTION DES JOURS QUI BLOQUENT & VALIDATION DES VACANCES (ESPACE CHEF)
     * ========================================================================= */
    function groupAbsenceRequests(absList) {
      const sorted = (absList || []).slice().sort((a, b) => {
        if (a.interneId !== b.interneId) return a.interneId.localeCompare(b.interneId);
        return a.date.localeCompare(b.date);
      });
      const groups = [];
      sorted.forEach(a => {
        if (!a || !a.date || !a.interneId) return;
        const st = a.status || "pending";
        const last = groups.length ? groups[groups.length - 1] : null;
        if (
          last &&
          last.interneId === a.interneId &&
          last.type === a.type &&
          last.status === st &&
          addDaysIso(last.endDate, 1) === a.date
        ) {
          last.endDate = a.date;
          last.dates.push(a.date);
          last.ids.push(a.id);
          const [yy, mm, dd] = a.date.split("-").map(Number);
          const jsDay = new Date(yy, mm - 1, dd).getDay();
          if (jsDay >= 1 && jsDay <= 5) last.weekdaysCount++;
        } else {
          const [yy, mm, dd] = a.date.split("-").map(Number);
          const jsDay = new Date(yy, mm - 1, dd).getDay();
          groups.push({
            groupId: `grp-${a.interneId}-${a.date}`,
            interneId: a.interneId,
            interneName: a.interneName || getInterneById(a.interneId).fullName,
            type: a.type || "CA 1",
            status: st,
            comment: a.comment || "",
            startDate: a.date,
            endDate: a.date,
            dates: [a.date],
            ids: [a.id],
            weekdaysCount: (jsDay >= 1 && jsDay <= 5) ? 1 : 0
          });
        }
      });
      return groups.sort((a, b) => a.startDate.localeCompare(b.startDate));
    }

    function computeBlockingDays(st) {
      const stateRef = st || STATE;
      const sched = stateRef.schedule || {};
      const decisions = stateRef.chefDecisions || {};
      const seniorIds = ["gabriel", "marwane", "milan", "nathanael", "oussama"];
      const allInterneIds = ["gabriel", "noe", "marwane", "milan", "nathanael", "oussama"];
      const donorPriority = ["TDM OLLIER DIAG", "SCAN ACHARD", "ECHO", "IRM 1,5T", "IRM", "IRM 3T", "ALLURA", "GESTES (C)", "LECTURE/CS", "1/2 journée libre"];

      const issues = [];
      const byDate = {};

      function addIssue(issue) {
        if (decisions[issue.id] && decisions[issue.id].resolved) return;
        issues.push(issue);
        if (!byDate[issue.date]) byDate[issue.date] = [];
        byDate[issue.date].push(issue);
      }

      // Pré-calcul des groupes d'absences pour repérer les mardis/vendredis isolés
      const activeAbs = (stateRef.absences || []).filter(a => a && a.status !== "rejected");
      const groups = groupAbsenceRequests(activeAbs);
      const isolatedGroupByDateAndInt = {};
      groups.forEach(g => {
        if (g.weekdaysCount > 0 && g.weekdaysCount <= 2 && g.type !== "Repos de garde") {
          g.dates.forEach(dIso => {
            const [yy, mm, dd] = dIso.split("-").map(Number);
            const jsDay = new Date(yy, mm - 1, dd).getDay();
            if (jsDay === 2 || jsDay === 5) {
              isolatedGroupByDateAndInt[dIso + "__" + g.interneId] = g;
            }
          });
        }
      });

      Object.keys(sched).sort().forEach(iso => {
        const dayObj = sched[iso];
        if (!dayObj || dayObj.holiday || !dayObj.byInterne) return;
        const [yy, mm, dd] = iso.split("-").map(Number);
        const jsDay = new Date(yy, mm - 1, dd).getDay();
        const isFirstMonday = (iso === "2026-11-02");

        // 1. Vérifier couverture obligatoire TDM SAU (Urgences) par au moins un interne hors socle (Noé étant toujours en binôme)
        if (!isFirstMonday) {
          ["am", "pm"].forEach(periodKey => {
            const pLabel = periodKey === "am" ? "Matin (08h00–13h00)" : "Après-midi (13h00–18h30)";
            const hasSau = seniorIds.some(iid => dayObj.byInterne[iid] && dayObj.byInterne[iid][periodKey] === "TDM SAU");
            if (!hasSau) {
              const absentInternes = seniorIds
                .filter(iid => dayObj.byInterne[iid] && (dayObj.byInterne[iid][periodKey] === "VACANCES" || dayObj.byInterne[iid][periodKey] === "RG"))
                .map(iid => getInterneById(iid).shortName);

              // Candidats disponibles ce jour/période pour reprendre TDM SAU
              const candidates = [];
              donorPriority.forEach(candPoste => {
                seniorIds.forEach(iid => {
                  const sl = dayObj.byInterne[iid];
                  if (!sl || sl[periodKey] !== candPoste) return;
                  if (jsDay === 2 && periodKey === "pm" && candPoste === "LECTURE/CS") return;
                  candidates.push({
                    interneId: iid,
                    shortName: getInterneById(iid).shortName,
                    currentPoste: candPoste
                  });
                });
              });

              addIssue({
                id: `block-sau-${iso}-${periodKey}`,
                date: iso,
                periodKey,
                poste: "TDM SAU",
                severity: "critical",
                category: "tdm_sau",
                title: `TDM SAU (${periodKey === "am" ? "Matin" : "PM"}) non couvert`,
                detail: `Aucun interne posté sur TDM SAU — Urgences obligatoires (${pLabel}).${absentInternes.length ? ` Absent(s) : ${absentInternes.join(", ")}.` : ""}`,
                candidates: candidates.slice(0, 4)
              });
            }
          });
        }

        // 2. Vérifier couverture obligatoire Mardi PM : Relecture avec Pr Drapé (LECTURE/CS)
        if (jsDay === 2) {
          const hasTueCs = Object.keys(dayObj.byInterne).some(iid => dayObj.byInterne[iid] && dayObj.byInterne[iid].pm === "LECTURE/CS");
          if (!hasTueCs) {
            const candidates = [];
            donorPriority.forEach(candPoste => {
              seniorIds.forEach(iid => {
                const sl = dayObj.byInterne[iid];
                if (sl && sl.pm === candPoste) {
                  candidates.push({
                    interneId: iid,
                    shortName: getInterneById(iid).shortName,
                    currentPoste: candPoste
                  });
                }
              });
            });
            addIssue({
              id: `block-drape-${iso}-pm`,
              date: iso,
              periodKey: "pm",
              poste: "LECTURE/CS",
              severity: "critical",
              category: "relecture_drape",
              title: `Relecture Pr Drapé (Mardi PM) non couverte`,
              detail: `Aucun interne affecté en LECTURE/CS le mardi après-midi pour la relecture systématique avec Pr Drapé.`,
              candidates: candidates.slice(0, 3)
            });
          }
        }

        // 3. Vérifier si > 2 internes absents simultanément ce jour
        const absentIds = Object.keys(dayObj.byInterne).filter(iid => {
          const sl = dayObj.byInterne[iid];
          return sl && (sl.am === "VACANCES" || sl.pm === "VACANCES" || sl.am === "RG" || sl.pm === "RG");
        });
        if (absentIds.length > 2) {
          const names = absentIds.map(iid => getInterneById(iid).shortName).join(", ");
          addIssue({
            id: `block-quota-abs-${iso}`,
            date: iso,
            periodKey: "full",
            poste: "VACANCES",
            severity: "critical",
            category: "over_quota_abs",
            title: `${absentIds.length} internes absents simultanément (max 2 autorisés)`,
            detail: `Absents le ${formatDateFr(iso)} : ${names}. Règle du service : 2 internes absents maximum en même temps.`,
            absentIds,
            candidates: []
          });
        }

        // 4. Vérifier si un interne prévu pour présenter un Cas / Biblio / Cours 12h30 est absent ce jour-là
        const dayPres = (stateRef.presentations || []).filter(p => p.date === iso);
        dayPres.forEach(pr => {
          if (pr.interneId && absentIds.includes(pr.interneId)) {
            const targetMs = new Date(iso + "T12:00:00").getTime();
            function minPresGapDays(candId) {
              let best = 999;
              (stateRef.presentations || []).forEach(otherP => {
                if (!otherP || otherP.id === pr.id || otherP.interneId !== candId) return;
                if (otherP.type !== "cas_mardi" && otherP.type !== "biblio_vendredi") return;
                const diff = Math.round(Math.abs(new Date(otherP.date + "T12:00:00").getTime() - targetMs) / 86400000);
                if (diff < best) best = diff;
              });
              return best;
            }
            const presentCands = allInterneIds
              .filter(iid => !absentIds.includes(iid))
              .sort((a, b) => minPresGapDays(b) - minPresGapDays(a))
              .map(iid => ({
                interneId: iid,
                shortName: getInterneById(iid).shortName
              }));
            addIssue({
              id: `block-pres-${iso}-${pr.id}`,
              date: iso,
              periodKey: "am",
              poste: "COURS",
              severity: "warning",
              category: "pres_absent",
              presId: pr.id,
              title: `Intervenant absent pour ${pr.typeLabel || "Séance 12h30"} (${pr.interneName})`,
              detail: `${pr.interneName} est en congé/RG le ${formatDateFr(iso)} alors qu'il/elle est programmé(e) pour ${pr.typeLabel || "la séance de 12h30"}.`,
              candidates: presentCands.slice(0, 3)
            });
          }
        });

        // 5. Vérifier congé isolé posé un Mardi ou Vendredi (règle : éviter Mardi/Vendredi hors semaine complète)
        Object.keys(dayObj.byInterne).forEach(iid => {
          const grp = isolatedGroupByDateAndInt[iso + "__" + iid];
          if (grp) {
            const iName = getInterneById(iid).shortName;
            addIssue({
              id: `block-isoday-${iso}-${iid}`,
              date: iso,
              periodKey: "full",
              poste: "VACANCES",
              severity: "warning",
              category: "isolated_tue_fri",
              interneId: iid,
              groupId: grp.groupId,
              title: `Congé isolé un ${jsDay === 2 ? "Mardi" : "Vendredi"} (${iName})`,
              detail: `${iName} a posé un congé court (${grp.weekdaysCount} j.) incluant un ${jsDay === 2 ? "mardi" : "vendredi"}. Arbitrage chef requis.`,
              candidates: []
            });
          }
        });
      });

      return { issues, byDate };
    }

    /* =========================================================================
     * MODE CHEF DE PLANNING (CODE: cocochin) & DRAG-AND-DROP DES INTERNES
     * ========================================================================= */
    function requireChefUnlockThen(actionFn) {
      if (isChefPlanningMode) {
        actionFn();
        return;
      }
      pendingChefActionCallback = actionFn;
      const inp = document.getElementById("chefCodeInput");
      const err = document.getElementById("chefCodeError");
      if (inp) inp.value = "";
      if (err) err.style.display = "none";
      document.getElementById("modalChefAuth").classList.add("open");
      setTimeout(() => { if (inp) inp.focus(); }, 60);
    }

    function openChefSpacePanel() {
      if (isChefPlanningMode) {
        if (currentTab !== "planning") switchTab("planning");
        const banner = document.getElementById("chefPlanningBanner");
        if (banner) banner.scrollIntoView({ behavior: "smooth", block: "nearest" });
      } else {
        toggleChefPlanningMode();
      }
    }

    function toggleChefPlanningMode() {
      if (isChefPlanningMode) {
        isChefPlanningMode = false;
        selectedForMove = null;
        activeDragPayload = null;
        pendingChefActionCallback = null;
        sessionStorage.removeItem(CHEF_MODE_STORAGE_KEY);
        renderAll();
        showToast("🔒 Espace Chef verrouillé");
      } else {
        pendingChefActionCallback = null;
        const inp = document.getElementById("chefCodeInput");
        const err = document.getElementById("chefCodeError");
        if (inp) inp.value = "";
        if (err) err.style.display = "none";
        document.getElementById("modalChefAuth").classList.add("open");
        setTimeout(() => { if (inp) inp.focus(); }, 60);
      }
    }

    function submitChefAuth() {
      const inp = document.getElementById("chefCodeInput");
      const err = document.getElementById("chefCodeError");
      const val = String((inp && inp.value) || "").trim().toLowerCase();
      if (val === CHEF_SECRET_CODE) {
        isChefPlanningMode = true;
        selectedForMove = null;
        sessionStorage.setItem(CHEF_MODE_STORAGE_KEY, "1");
        closeModal("modalChefAuth");
        if (typeof pendingChefActionCallback === "function") {
          const cb = pendingChefActionCallback;
          pendingChefActionCallback = null;
          cb();
          return;
        }
        currentTab = "planning";
        selectedInterneId = "all";
        localStorage.setItem(SELECTED_INTERNE_KEY, selectedInterneId);
        if (planningScope !== "combined") {
          planningScope = "internes";
        }
        if (planningMode === "month") {
          planningMode = "week";
        }
        document.querySelectorAll(".tab-btn").forEach(b => {
          b.classList.toggle("active", b.getAttribute("data-tab") === "planning");
        });
        renderAll();
        showToast("🔓 Espace Chef activé");
      } else {
        if (err) err.style.display = "block";
        if (inp) inp.select();
      }
    }

    function approveAbsenceGroup(groupId) {
      requireChefUnlockThen(() => {
        const groups = groupAbsenceRequests(STATE.absences || []);
        const g = groups.find(x => x.groupId === groupId);
        if (!g) return;
        const nowIso = markChefValidationStamp();
        const idSet = new Set(g.ids);
        (STATE.absences || []).forEach(a => {
          if (idSet.has(a.id)) {
            a.status = "approved";
            a.validatedBy = "Chef";
            a.validatedAt = nowIso;
          }
        });
        saveStateLocal();
        renderAll();
        showToast(`✓ Congés validés pour ${g.interneName} (${g.dates.length} j.)`);
        pushStateToCloud({
          isChefValidation: true,
          syncAbsenceSheet: true,
          addedDates: g.dates,
          interneName: g.interneName,
          absType: g.type
        });
      });
    }

    function rejectAbsenceGroup(groupId) {
      requireChefUnlockThen(() => {
        const groups = groupAbsenceRequests(STATE.absences || []);
        const g = groups.find(x => x.groupId === groupId);
        if (!g) return;
        const nowIso = markChefValidationStamp();
        const idSet = new Set(g.ids);
        (STATE.absences || []).forEach(a => {
          if (idSet.has(a.id)) {
            a.status = "rejected";
            a.validatedBy = "Chef";
            a.validatedAt = nowIso;
          }
        });
        saveStateLocal();
        renderAll();
        showToast(`✕ Congés refusés pour ${g.interneName} — planning restauré`);
        pushStateToCloud({
          isChefValidation: true,
          syncAbsenceSheet: true,
          removedDates: g.dates,
          interneName: g.interneName
        });
      });
    }

    function setSingleAbsenceStatus(absId, newStatus) {
      requireChefUnlockThen(() => {
        const target = (STATE.absences || []).find(a => a.id === absId);
        if (!target) return;
        const nowIso = markChefValidationStamp();
        target.status = newStatus;
        target.validatedBy = "Chef";
        target.validatedAt = nowIso;
        saveStateLocal();
        renderAll();
        showToast(newStatus === "approved" ? "✓ Journée de congé validée par le chef" : "✕ Journée de congé refusée (poste restauré)");
        pushStateToCloud({
          isChefValidation: true,
          syncAbsenceSheet: true,
          addedDates: newStatus === "approved" ? [target.date] : [],
          removedDates: newStatus === "rejected" ? [target.date] : [],
          interneName: target.interneName,
          absType: target.type
        });
      });
    }

    function getPendingVacationModifs(st) {
      const stateRef = st || STATE;
      const custom = stateRef.customVacations || {};
      const list = [];
      Object.keys(custom).sort().forEach(cKey => {
        const entry = custom[cKey];
        if (!entry || entry.status !== "pending") return;
        const [dIso, iid] = cKey.split("__");
        if (!dIso || !iid) return;
        const iObj = getInterneById(iid);
        list.push({
          key: cKey,
          date: dIso,
          interneId: iid,
          interneName: iObj.shortName,
          fullName: iObj.fullName,
          color: iObj.color,
          am: entry.am,
          pm: entry.pm,
          prevAm: entry.prevAm || "",
          prevPm: entry.prevPm || "",
          note: entry.note || ""
        });
      });
      return list;
    }

    function approveVacationModif(cKey) {
      requireChefUnlockThen(() => {
        if (STATE.customVacations && STATE.customVacations[cKey]) {
          const nowIso = markChefValidationStamp();
          STATE.customVacations[cKey].status = "approved";
          STATE.customVacations[cKey].validatedBy = "Chef";
          STATE.customVacations[cKey].validatedAt = nowIso;
          if (Array.isArray(STATE.deletedCustomKeys)) {
            STATE.deletedCustomKeys = STATE.deletedCustomKeys.filter(k => k !== cKey);
          }
          saveStateLocal();
          renderAll();
          showToast("✓ Modification de poste validée");
          pushStateToCloud({ isChefValidation: true });
        }
      });
    }

    function rejectVacationModif(cKey) {
      requireChefUnlockThen(() => {
        if (STATE.customVacations && STATE.customVacations[cKey]) {
          const rejIso = markChefValidationStamp();
          delete STATE.customVacations[cKey];
          tombstoneCustomKey(cKey, rejIso);
          saveStateLocal();
          renderAll();
          showToast("✕ Modification annulée — poste initial rétabli");
          pushStateToCloud({ isChefValidation: true });
        }
      });
    }

    function approveAllPendingAbsences() {
      requireChefUnlockThen(() => {
        const nowIso = markChefValidationStamp();
        let count = 0;
        let absApprovedCount = 0;
        (STATE.absences || []).forEach(a => {
          if ((a.status || "pending") === "pending") {
            a.status = "approved";
            a.validatedBy = "Chef";
            a.validatedAt = nowIso;
            count++;
            absApprovedCount++;
          }
        });
        Object.keys(STATE.customVacations || {}).forEach(cKey => {
          const entry = STATE.customVacations[cKey];
          if (entry && entry.status === "pending") {
            entry.status = "approved";
            entry.validatedBy = "Chef";
            entry.validatedAt = nowIso;
            count++;
          }
        });
        saveStateLocal();
        renderAll();
        showToast(`✓ ${count} modification(s) validée(s)`);
        pushStateToCloud({ isChefValidation: true, syncAbsenceSheet: absApprovedCount > 0 });
      });
    }

    function applyChefBlockingDecision(issueId, dIso, periodKey, candidateInterneId, targetPoste, presId) {
      requireChefUnlockThen(() => {
        pushChefHistorySnapshot();
        const nowIso = markChefValidationStamp();
        if (presId) {
          const pr = (STATE.presentations || []).find(p => p.id === presId);
          const iObj = getInterneById(candidateInterneId);
          if (pr && iObj) {
            pr.interneId = iObj.id;
            pr.interneName = iObj.shortName;
            pr.userEditedPres = true;
          }
          if (!STATE.chefDecisions) STATE.chefDecisions = {};
          STATE.chefDecisions[issueId] = {
            resolved: true,
            note: `Séance reprise par ${iObj ? iObj.shortName : candidateInterneId}`,
            decidedAt: nowIso
          };
          saveStateLocal();
          renderAll();
          showToast(`✓ ${iObj.shortName} reprend la séance du ${formatDateFr(dIso)}`);
          pushStateToCloud({ isChefValidation: true, syncStaffSheet: true });
          return;
        }
        const iObj = getInterneById(candidateInterneId);
        applyInterneSlotChange(dIso, periodKey, candidateInterneId, targetPoste, `Remplacement ${targetPoste}`);
        if (!STATE.chefDecisions) STATE.chefDecisions = {};
        STATE.chefDecisions[issueId] = {
          resolved: true,
          note: `${iObj.shortName} affecté sur ${targetPoste}`,
          decidedAt: nowIso
        };
        currentDateIso = dIso;
        saveStateLocal();
        renderAll();
        showToast(`✓ ${iObj.shortName} affecté sur ${targetPoste} (${formatDateFr(dIso)} ${periodKey === "am" ? "Matin" : "PM"})`);
        pushStateToCloud({ isChefValidation: true });
      });
    }

    function acknowledgeBlockingIssue(issueId, noteText) {
      requireChefUnlockThen(() => {
        const nowIso = markChefValidationStamp();
        if (!STATE.chefDecisions) STATE.chefDecisions = {};
        STATE.chefDecisions[issueId] = {
          resolved: true,
          note: noteText || "Validé en l'état par le chef",
          decidedAt: nowIso
        };
        saveStateLocal();
        renderAll();
        showToast("✓ Conflit marqué comme géré");
        pushStateToCloud({ isChefValidation: true });
      });
    }

    function resetAllChefDecisions() {
      requireChefUnlockThen(() => {
        markChefValidationStamp();
        STATE.chefDecisions = {};
        saveStateLocal();
        renderAll();
        showToast("Alertes réinitialisées");
        pushStateToCloud({ isChefValidation: true, replaceChefDecisions: true });
      });
    }

    function openBlockingDayInPlanning(dIso) {
      currentDateIso = dIso;
      currentTab = "planning";
      if (planningScope === "chefs" || planningScope === "perso") {
        planningScope = "internes";
      }
      selectedInterneId = "all";
      localStorage.setItem(SELECTED_INTERNE_KEY, selectedInterneId);
      planningMode = "week";
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-tab") === "planning");
      });
      renderAll();
    }

    function renderChefModeUI() {
      const btn = document.getElementById("chefModeBtn");
      const btnTxt = document.getElementById("chefModeBtnText");
      const banner = document.getElementById("chefPlanningBanner");
      const tabBtnPlanning = document.getElementById("tabBtnPlanning");
      const tabBtnVacances = document.getElementById("tabBtnVacances");

      const monIso = getMondayOfWeek(currentDateIso);
      const friIso = addDaysIso(monIso, 4);
      const weekDaysSet = new Set([0, 1, 2, 3, 4].map(off => addDaysIso(monIso, off)));

      const blocking = computeBlockingDays(STATE);
      const weekIssues = blocking.issues.filter(iss => weekDaysSet.has(iss.date) && iss.severity === "critical");
      const allGroups = groupAbsenceRequests((STATE.absences || []).filter(a => a && a.status !== "rejected"));
      const pendingGroups = allGroups.filter(g => g.status === "pending");
      const pendingModifs = getPendingVacationModifs(STATE);
      const pendingCount = pendingGroups.length + pendingModifs.length;
      const totalNotifs = weekIssues.length + pendingCount;

      if (btn && btnTxt) {
        const badgeHtml = (isChefPlanningMode && totalNotifs > 0)
          ? `<span class="notif-badge ${weekIssues.length === 0 ? 'warn' : ''}">${totalNotifs}</span>`
          : "";
        if (isChefPlanningMode) {
          btn.classList.add("unlocked");
          btnTxt.innerHTML = `🔓 Mode Chef ${badgeHtml}`;
        } else {
          btn.classList.remove("unlocked");
          btnTxt.innerHTML = `🔒 Espace Chef`;
        }
      }

      if (tabBtnPlanning) tabBtnPlanning.innerHTML = `Planning`;
      if (tabBtnVacances) {
        tabBtnVacances.innerHTML = (isChefPlanningMode && pendingGroups.length > 0)
          ? `Congés <span class="notif-badge warn">${pendingGroups.length}</span>`
          : `Congés`;
      }

      if (!banner) return;

      if (!isChefPlanningMode) {
        banner.style.display = "none";
        banner.innerHTML = "";
        return;
      }

      const weekLock = getWeekLockInfo(monIso);

      // Lignes d'actions rapides : uniquement les demandes en attente + créneaux critiques non couverts de la semaine
      const rows = [];

      pendingGroups.forEach(g => {
        const iObj = getInterneById(g.interneId);
        const periodLabel = g.startDate === g.endDate
          ? formatDateFr(g.startDate)
          : `${formatDateFr(g.startDate)} → ${formatDateFr(g.endDate)} (${g.dates.length} j.)`;
        rows.push(`
          <div class="chef-simple-row">
            <div class="chef-simple-row-left">
              <span class="chef-row-tag warn">Congé</span>
              <strong>${iObj.shortName}</strong>
              <span class="poste-pill poste-vac">${g.type}</span>
              <span>${periodLabel}</span>
              ${g.comment ? `<span style="color:#64748B;">• ${g.comment}</span>` : ""}
            </div>
            <div class="chef-decision-btns">
              <button class="btn-approve" onclick="approveAbsenceGroup('${g.groupId}')">✓ Valider</button>
              <button class="btn-reject" onclick="rejectAbsenceGroup('${g.groupId}')">✕ Refuser</button>
              <button class="btn btn-sm" style="padding:3px 8px; font-size:11px;" onclick="openBlockingDayInPlanning('${g.startDate}')">Voir</button>
            </div>
          </div>
        `);
      });

      pendingModifs.forEach(m => {
        const changes = [];
        if (m.prevAm && m.prevAm !== m.am) changes.push(`Matin : ${m.prevAm} → <strong>${m.am}</strong>`);
        else if (m.am) changes.push(`Matin : <strong>${m.am}</strong>`);
        if (m.prevPm && m.prevPm !== m.pm) changes.push(`PM : ${m.prevPm} → <strong>${m.pm}</strong>`);
        else if (m.pm) changes.push(`PM : <strong>${m.pm}</strong>`);
        rows.push(`
          <div class="chef-simple-row">
            <div class="chef-simple-row-left">
              <span class="chef-row-tag info">Poste</span>
              <strong>${m.interneName}</strong>
              <span>• ${formatDateFr(m.date)} : ${changes.join(" • ")}</span>
            </div>
            <div class="chef-decision-btns">
              <button class="btn-approve" onclick="approveVacationModif('${m.key}')">✓ Valider</button>
              <button class="btn-reject" onclick="rejectVacationModif('${m.key}')">✕ Rétablir</button>
              <button class="btn btn-sm" style="padding:3px 8px; font-size:11px;" onclick="openBlockingDayInPlanning('${m.date}')">Voir</button>
            </div>
          </div>
        `);
      });

      weekIssues.forEach(iss => {
        const candBtns = (iss.candidates || []).slice(0, 3).map(c => {
          const pEsc = String(iss.poste || "").replace(/'/g, "\\'");
          const prArg = iss.presId ? `'${iss.presId}'` : `null`;
          return `<button class="btn-decide" onclick="applyChefBlockingDecision('${iss.id}', '${iss.date}', '${iss.periodKey}', '${c.interneId}', '${pEsc}', ${prArg})">⚡ ${c.shortName}</button>`;
        }).join("");
        rows.push(`
          <div class="chef-simple-row">
            <div class="chef-simple-row-left">
              <span class="chef-row-tag danger">À couvrir</span>
              <strong>${formatDateFr(iss.date)}</strong>
              <span>• ${iss.title}</span>
            </div>
            <div class="chef-decision-btns">
              ${candBtns}
              <button class="btn btn-sm" style="padding:3px 8px; font-size:11px;" onclick="acknowledgeBlockingIssue('${iss.id}', 'Maintenu')">Ignorer</button>
            </div>
          </div>
        `);
      });

      const weekBtnHtml = weekLock
        ? `<span class="status-pill-approved">📌 Semaine fixée</span>
           <button class="btn-unfix-week" onclick="unfixWeekPlanning('${monIso}')">Débloquer</button>`
        : `<button class="btn-fix-week" onclick="validateAndFixWeekPlanning('${monIso}')">📌 Fixer la semaine (${formatShortDayHeader(monIso)}–${formatShortDayHeader(friIso)})</button>`;

      const subHintHtml = selectedForMove
        ? `<span class="poste-pill poste-tdm">Sélectionné : ${getInterneById(selectedForMove.interneId).shortName} (${formatShortDayHeader(selectedForMove.dIso)} ${selectedForMove.periodKey === 'am' ? 'Matin' : 'PM'})</span>
           <span style="font-size:11.5px; color:#92400E; font-weight:600;">Cliquez sur un interne pour échanger ou une case pour déplacer</span>
           <button class="btn btn-sm" style="padding:3px 8px; font-size:11px;" onclick="openVacationEditModal('${selectedForMove.dIso}', '${selectedForMove.interneId}')">✎ Liste des postes</button>
           <button class="btn btn-sm" style="padding:3px 8px; font-size:11px;" onclick="cancelSelectedForMove()">Annuler</button>`
        : `<span style="font-size:11.5px; color:#64748B; font-weight:600;">Cliquez sur 2 internes pour les échanger, sur une case vide pour déplacer, ou sur un prénom ci-dessous pour modifier sa journée</span>`;

      banner.style.display = "block";
      banner.innerHTML = `
        <div class="chef-simple-panel unlocked">
          <div class="chef-simple-header">
            <div class="chef-simple-title">
              <span>🔓 Organisation du Planning</span>
              ${subHintHtml}
            </div>
            <div class="chef-simple-actions">
              ${weekBtnHtml}
              ${pendingCount > 1 ? `<button class="btn-approve" onclick="approveAllPendingAbsences()">✓ Tout valider (${pendingCount})</button>` : ""}
              ${chefHistoryStack.length > 0 ? `<button class="btn btn-sm" onclick="undoLastChefMove()">↩ Annuler</button>` : ""}
              <button class="btn btn-sm" onclick="resetCurrentWeekVacations()" title="Réinitialiser la semaine par défaut">Réinit. sem.</button>
              <button class="btn btn-sm" onclick="toggleChefPlanningMode()">Quitter</button>
            </div>
          </div>
          ${rows.length > 0 ? `<div class="chef-simple-list">${rows.join("")}</div>` : ""}
          ${renderChefOffVacSummaryHtml(monIso)}
        </div>
      `;
    }

    function isWeekLocked(monIso) {
      const m = monIso || getMondayOfWeek(currentDateIso);
      return Boolean(STATE.lockedWeeks && STATE.lockedWeeks[m] && STATE.lockedWeeks[m].locked);
    }

    function getWeekLockInfo(monIso) {
      const m = monIso || getMondayOfWeek(currentDateIso);
      return (STATE.lockedWeeks && STATE.lockedWeeks[m] && STATE.lockedWeeks[m].locked)
        ? STATE.lockedWeeks[m]
        : null;
    }

    function validateAndFixWeekPlanning(monIso) {
      requireChefUnlockThen(() => {
        const targetMon = monIso || getMondayOfWeek(currentDateIso);
        const days = [0, 1, 2, 3, 4].map(off => addDaysIso(targetMon, off));
        pushChefHistorySnapshot();
        const nowIso = markChefValidationStamp();

        recomputeScheduleInPlace(STATE);
        if (!STATE.customVacations) STATE.customVacations = {};

        days.forEach(dIso => {
          const dObj = STATE.schedule[dIso];
          if (!dObj || dObj.holiday || !dObj.byInterne) return;
          STATE.internes.forEach(i => {
            const curSlot = dObj.byInterne[i.id];
            if (!curSlot) return;
            const cKey = dIso + "__" + i.id;
            STATE.customVacations[cKey] = {
              am: curSlot.am,
              pm: curSlot.pm,
              note: curSlot.note || "",
              status: "approved",
              validatedBy: "Chef",
              validatedAt: nowIso
            };
            if (Array.isArray(STATE.deletedCustomKeys)) {
              STATE.deletedCustomKeys = STATE.deletedCustomKeys.filter(k => k !== cKey);
            }
          });
        });

        let approvedAbs = 0;
        (STATE.absences || []).forEach(a => {
          if (a && days.includes(a.date) && a.status === "pending") {
            a.status = "approved";
            a.validatedBy = "Chef";
            a.validatedAt = nowIso;
            approvedAbs++;
          }
        });

        const blocking = computeBlockingDays(STATE);
        if (!STATE.chefDecisions) STATE.chefDecisions = {};
        blocking.issues.forEach(iss => {
          if (days.includes(iss.date)) {
            STATE.chefDecisions[iss.id] = {
              resolved: true,
              resolvedAt: nowIso,
              decidedAt: nowIso,
              status: "validated_week",
              note: "Planning de la semaine validé et fixé par le Chef"
            };
          }
        });

        if (!STATE.lockedWeeks) STATE.lockedWeeks = {};
        STATE.lockedWeeks[targetMon] = {
          locked: true,
          validatedAt: nowIso,
          validatedBy: isChefId(selectedInterneId) ? getChefById(selectedInterneId).fullName : "Chef de clinique"
        };

        selectedForMove = null;
        saveStateLocal();
        renderAll();
        const friIso = addDaysIso(targetMon, 4);
        showToast(`📌 Semaine du ${formatDateFr(targetMon)} au ${formatDateFr(friIso)} fixée`);
        pushStateToCloud({ isChefValidation: true, syncAbsenceSheet: approvedAbs > 0 });
      });
    }

    function unfixWeekPlanning(monIso) {
      requireChefUnlockThen(() => {
        const targetMon = monIso || getMondayOfWeek(currentDateIso);
        const nowIso = markChefValidationStamp();
        if (!STATE.lockedWeeks) STATE.lockedWeeks = {};
        STATE.lockedWeeks[targetMon] = {
          locked: false,
          unlockedAt: nowIso
        };
        saveStateLocal();
        renderAll();
        showToast(`🔓 Semaine du ${formatDateFr(targetMon)} débloquée`);
        pushStateToCloud({ isChefValidation: true });
      });
    }

    function cancelSelectedForMove() {
      selectedForMove = null;
      renderAll();
    }

    function pushChefHistorySnapshot() {
      chefHistoryStack.push(JSON.parse(JSON.stringify(STATE.customVacations || {})));
      if (chefHistoryStack.length > 30) chefHistoryStack.shift();
    }

    function undoLastChefMove() {
      if (!chefHistoryStack.length) return;
      const undoIso = markChefValidationStamp();
      const prevCustom = chefHistoryStack.pop() || {};
      const curCustom = STATE.customVacations || {};
      Object.keys(curCustom).forEach(k => {
        if (!prevCustom[k]) tombstoneCustomKey(k, undoIso);
      });
      // Ré-horodater les versions restaurées pour qu'elles priment sur la version annulée lors de la fusion cloud
      Object.keys(prevCustom).forEach(k => {
        if (JSON.stringify(prevCustom[k]) !== JSON.stringify(curCustom[k])) {
          prevCustom[k] = Object.assign({}, prevCustom[k], { updatedAt: undoIso });
          if (prevCustom[k].validatedAt) prevCustom[k].validatedAt = undoIso;
          if (Array.isArray(STATE.deletedCustomKeys)) STATE.deletedCustomKeys = STATE.deletedCustomKeys.filter(x => x !== k);
        }
      });
      STATE.customVacations = prevCustom;
      selectedForMove = null;
      saveStateLocal();
      renderAll();
      showToast("Modification annulée");
      pushStateToCloud({ isChefValidation: true, replaceCustomVacations: true });
    }

    function resetCurrentWeekVacations() {
      const monIso = getMondayOfWeek(currentDateIso);
      const days = [0, 1, 2, 3, 4].map(off => addDaysIso(monIso, off));
      if (!STATE.customVacations) return;
      pushChefHistorySnapshot();
      const nowIso = markChefValidationStamp();
      if (!Array.isArray(STATE.deletedCustomKeys)) STATE.deletedCustomKeys = [];
      days.forEach(dIso => {
        STATE.internes.forEach(i => {
          const cKey = dIso + "__" + i.id;
          delete STATE.customVacations[cKey];
          tombstoneCustomKey(cKey, nowIso);
        });
      });
      if (STATE.lockedWeeks && STATE.lockedWeeks[monIso]) {
        STATE.lockedWeeks[monIso] = { locked: false, unlockedAt: nowIso };
      }
      selectedForMove = null;
      saveStateLocal();
      renderAll();
      showToast("Semaine réinitialisée par défaut");
      pushStateToCloud({ isChefValidation: true, replaceCustomVacations: true });
    }

    function applyInterneSlotChange(dIso, periodKey, interneId, newPoste, customNote) {
      const dObj = STATE.schedule[dIso];
      if (!dObj || !dObj.byInterne || !dObj.byInterne[interneId]) return;
      const curSlot = dObj.byInterne[interneId];
      if (!STATE.customVacations) STATE.customVacations = {};
      const nowIso = markChefValidationStamp();
      const cKey = dIso + "__" + interneId;
      const existing = STATE.customVacations[cKey] || {
        am: curSlot.am,
        pm: curSlot.pm,
        note: curSlot.note || "",
        status: "approved"
      };
      existing[periodKey] = newPoste;
      existing.status = "approved";
      existing.validatedBy = "Chef";
      existing.validatedAt = nowIso;
      if (customNote !== undefined) existing.note = customNote;
      STATE.customVacations[cKey] = existing;
      if (Array.isArray(STATE.deletedCustomKeys)) {
        STATE.deletedCustomKeys = STATE.deletedCustomKeys.filter(k => k !== cKey);
      }
    }

    function executeChefMoveOrSwap(source, target) {
      // source: { dIso, periodKey, interneId, fromPoste }
      // target: { dIso, periodKey, toPoste, targetInterneId (optional) }
      if (!source || !target) return;

      const srcInterne = getInterneById(source.interneId);
      const nonActList = ["1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"];

      // Si on dépose directement sur un autre interne (ou si on échange deux internes, même jour ou autre jour)
      if (target.targetInterneId && (target.targetInterneId !== source.interneId || target.dIso !== source.dIso || target.periodKey !== source.periodKey)) {
        const tgtInterne = getInterneById(target.targetInterneId);
        const srcDayObj = STATE.schedule[source.dIso];
        const tgtDayObj = STATE.schedule[target.dIso];
        const srcPoste = srcDayObj && srcDayObj.byInterne && srcDayObj.byInterne[source.interneId]
          ? srcDayObj.byInterne[source.interneId][source.periodKey]
          : source.fromPoste;
        const tgtPoste = tgtDayObj && tgtDayObj.byInterne && tgtDayObj.byInterne[target.targetInterneId]
          ? tgtDayObj.byInterne[target.targetInterneId][target.periodKey]
          : target.toPoste;

        const [yyS, mmS, ddS] = source.dIso.split("-").map(Number);
        const jsDayS = new Date(yyS, mmS - 1, ddS).getDay();
        const [yyT, mmT, ddT] = target.dIso.split("-").map(Number);
        const jsDayT = new Date(yyT, mmT - 1, ddT).getDay();
        if ((source.periodKey === "pm" && (jsDayS === 2 || jsDayS === 5) && tgtPoste === "1/2 journée libre") ||
            (target.periodKey === "pm" && (jsDayT === 2 || jsDayT === 5) && srcPoste === "1/2 journée libre")) {
          showToast("Règle du service : pas de demi-off le mardi après-midi ni le vendredi après-midi.");
          selectedForMove = null;
          renderAll();
          return;
        }

        // Vérifier qu'aucun des deux internes ne se retrouve avec le même poste toute la journée (Matin == Après-midi)
        if (!(source.interneId === target.targetInterneId && source.dIso === target.dIso)) {
          const srcOtherPeriod = source.periodKey === "am" ? "pm" : "am";
          const tgtOtherPeriod = target.periodKey === "am" ? "pm" : "am";
          const srcOtherPoste = srcDayObj && srcDayObj.byInterne && srcDayObj.byInterne[source.interneId]
            ? srcDayObj.byInterne[source.interneId][srcOtherPeriod]
            : "";
          const tgtOtherPoste = tgtDayObj && tgtDayObj.byInterne && tgtDayObj.byInterne[target.targetInterneId]
            ? tgtDayObj.byInterne[target.targetInterneId][tgtOtherPeriod]
            : "";
          if (!nonActList.includes(tgtPoste) && tgtPoste === srcOtherPoste) {
            showToast(`⛔ Règle : ${srcInterne.shortName} ne peut pas faire le même poste toute la journée (${tgtPoste}).`);
            selectedForMove = null;
            renderAll();
            return;
          }
          if (!nonActList.includes(srcPoste) && srcPoste === tgtOtherPoste) {
            showToast(`⛔ Règle : ${tgtInterne.shortName} ne peut pas faire le même poste toute la journée (${srcPoste}).`);
            selectedForMove = null;
            renderAll();
            return;
          }
        }

        pushChefHistorySnapshot();
        applyInterneSlotChange(source.dIso, source.periodKey, source.interneId, tgtPoste);
        applyInterneSlotChange(target.dIso, target.periodKey, target.targetInterneId, srcPoste);
        selectedForMove = null;
        saveStateLocal();
        renderAll();
        showToast(`🔄 Échange : ${srcInterne.shortName} (${tgtPoste}) ↔ ${tgtInterne.shortName} (${srcPoste})`);
        pushStateToCloud({ isChefValidation: true });
        return;
      }

      if (source.dIso !== target.dIso || source.periodKey !== target.periodKey) {
        showToast("Pour changer de poste vers une case vide, déposez sur le même jour/demi-journée (ou sur un interne pour échanger).");
        return;
      }

      // Déplacement vers une ligne de poste
      if (!target.toPoste || target.toPoste === source.fromPoste) {
        selectedForMove = null;
        renderAll();
        return;
      }

      const [yyM, mmM, ddM] = source.dIso.split("-").map(Number);
      const jsDayM = new Date(yyM, mmM - 1, ddM).getDay();
      if (source.periodKey === "pm" && (jsDayM === 2 || jsDayM === 5) && target.toPoste === "1/2 journée libre") {
        showToast("Règle du service : pas de demi-off le mardi après-midi ni le vendredi après-midi.");
        selectedForMove = null;
        renderAll();
        return;
      }

      const daySlotsMove = (STATE.schedule[source.dIso] && STATE.schedule[source.dIso].byInterne) || {};
      const otherPeriodMove = source.periodKey === "am" ? "pm" : "am";
      const myOtherPoste = daySlotsMove[source.interneId] ? daySlotsMove[source.interneId][otherPeriodMove] : "";
      if (!nonActList.includes(target.toPoste) && target.toPoste === myOtherPoste) {
        showToast(`⛔ Règle : ${srcInterne.shortName} ne peut pas faire le même poste toute la journée (${target.toPoste}).`);
        selectedForMove = null;
        renderAll();
        return;
      }

      pushChefHistorySnapshot();
      const seniorListMove = ["gabriel", "marwane", "milan", "nathanael", "oussama"];
      if (source.fromPoste === "TDM SAU" && target.toPoste !== "TDM SAU" && seniorListMove.includes(source.interneId)) {
        const otherSauSeniors = seniorListMove.filter(sId => sId !== source.interneId && daySlotsMove[sId] && daySlotsMove[sId][source.periodKey] === "TDM SAU");
        if (otherSauSeniors.length === 0) {
          const swapSenior = seniorListMove.find(sId => sId !== source.interneId && daySlotsMove[sId] && daySlotsMove[sId][source.periodKey] === target.toPoste);
          if (swapSenior) {
            applyInterneSlotChange(source.dIso, source.periodKey, swapSenior, "TDM SAU");
          }
        }
      }
      applyInterneSlotChange(source.dIso, source.periodKey, source.interneId, target.toPoste);
      selectedForMove = null;
      saveStateLocal();
      renderAll();
      showToast(`✅ ${srcInterne.shortName} déplacé sur ${target.toPoste} (${source.periodKey === 'am' ? 'Matin' : 'PM'})`);
      pushStateToCloud({ isChefValidation: true });
    }

    function onInterneDragStart(ev, dIso, periodKey, interneId, fromPoste) {
      if (!isChefPlanningMode) return;
      activeDragPayload = { dIso, periodKey, interneId, fromPoste };
      if (ev.dataTransfer) {
        ev.dataTransfer.effectAllowed = "move";
        ev.dataTransfer.setData("text/plain", JSON.stringify(activeDragPayload));
      }
      setTimeout(() => {
        if (ev.target && ev.target.classList) ev.target.classList.add("dragging");
      }, 0);
    }

    function onInterneDragEnd(ev) {
      if (ev.target && ev.target.classList) ev.target.classList.remove("dragging");
      document.querySelectorAll(".drag-over").forEach(el => el.classList.remove("drag-over"));
    }

    function onCellDragOver(ev, dIso, periodKey) {
      if (!isChefPlanningMode || !activeDragPayload) return;
      ev.preventDefault();
      if (ev.dataTransfer) ev.dataTransfer.dropEffect = "move";
      const td = ev.currentTarget;
      if (td && !td.classList.contains("drag-over")) {
        td.classList.add("drag-over");
      }
    }

    function onCellDragLeave(ev) {
      const td = ev.currentTarget;
      if (td) td.classList.remove("drag-over");
    }

    function onCellDrop(ev, dIso, periodKey, toPoste) {
      if (!isChefPlanningMode) return;
      ev.preventDefault();
      ev.stopPropagation();
      const td = ev.currentTarget;
      if (td) td.classList.remove("drag-over");

      let payload = activeDragPayload;
      if (!payload && ev.dataTransfer) {
        try { payload = JSON.parse(ev.dataTransfer.getData("text/plain")); } catch (e) {}
      }
      activeDragPayload = null;
      if (!payload) return;

      executeChefMoveOrSwap(payload, { dIso, periodKey, toPoste });
    }

    function onBadgeDrop(ev, dIso, periodKey, targetInterneId, toPoste) {
      if (!isChefPlanningMode) return;
      ev.preventDefault();
      ev.stopPropagation();
      document.querySelectorAll(".drag-over").forEach(el => el.classList.remove("drag-over"));

      let payload = activeDragPayload;
      if (!payload && ev.dataTransfer) {
        try { payload = JSON.parse(ev.dataTransfer.getData("text/plain")); } catch (e) {}
      }
      activeDragPayload = null;
      if (!payload) return;

      executeChefMoveOrSwap(payload, { dIso, periodKey, toPoste, targetInterneId });
    }

    function onInterneBadgeClick(ev, dIso, periodKey, interneId, posteName) {
      ev.stopPropagation();
      if (!isChefPlanningMode) {
        openVacationEditModal(dIso, interneId);
        return;
      }
      // En mode Chef de Planning : clic 1 sélectionne l'interne, clic 2 sur un autre interne les échange
      if (!selectedForMove) {
        selectedForMove = { dIso, periodKey, interneId, fromPoste: posteName };
        renderAll();
        return;
      }
      if (selectedForMove.interneId === interneId && selectedForMove.dIso === dIso && selectedForMove.periodKey === periodKey) {
        selectedForMove = null;
        renderAll();
        return;
      }
      executeChefMoveOrSwap(selectedForMove, {
        dIso,
        periodKey,
        toPoste: posteName,
        targetInterneId: interneId
      });
    }

    function onChefCellClick(ev, dIso, periodKey, toPoste) {
      if (!isChefPlanningMode || !selectedForMove) return;
      ev.stopPropagation();
      executeChefMoveOrSwap(selectedForMove, { dIso, periodKey, toPoste });
    }

    // Barre de sélection simplifiée (masquée en Mode Chef pour garder toute la place au planning)
    function renderInterneSelector() {
      const bar = document.getElementById("interneSelectorBar");
      if (!bar) return;
      if (isChefPlanningMode) {
        bar.style.display = "none";
        bar.innerHTML = "";
        return;
      }
      bar.style.display = "flex";
      const inChefSpace = (selectedInterneId === "all_chefs" || isChefId(selectedInterneId));

      let html = `
        <div class="segmented">
          <button class="seg-btn ${!inChefSpace ? 'active' : ''}" onclick="switchRoleSpace('internes')">Internes</button>
          <button class="seg-btn ${inChefSpace ? 'active' : ''}" onclick="switchRoleSpace('chefs')">Chefs</button>
        </div>
        <div class="person-chips">
      `;

      if (!inChefSpace) {
        html += `<button class="chip ${selectedInterneId === 'all' ? 'active' : ''}" onclick="selectInterne('all')">Tous</button>`;
        STATE.internes.forEach(i => {
          const active = (selectedInterneId === i.id) ? "active" : "";
          const isDJ = Boolean(i.isDJ || i.id === "oussama");
          html += `
            <button class="chip ${active}" onclick="selectInterne('${i.id}')">
              <span class="dot" style="background:${i.color}"></span>
              <span>${i.shortName}</span>
              ${i.isSocle ? `<span class="tag-sm">Socle</span>` : ""}
              ${isDJ ? `<span class="tag-dj">DJ</span>` : ""}
            </button>
          `;
        });
      } else {
        html += `<button class="chip ${selectedInterneId === 'all_chefs' ? 'active' : ''}" onclick="selectInterne('all_chefs')">Tous</button>`;
        (STATE.chefs || []).forEach(c => {
          const active = (selectedInterneId === c.id) ? "active" : "";
          html += `
            <button class="chip ${active}" onclick="selectInterne('${c.id}')">
              <span class="dot" style="background:${c.color}"></span>
              <span>${c.code} · ${c.nom}</span>
            </button>
          `;
        });
      }

      html += `</div>`;
      bar.innerHTML = html;
    }

    function switchRoleSpace(space) {
      if (space === "chefs") {
        if (!isChefId(selectedInterneId) && selectedInterneId !== "all_chefs") {
          selectedInterneId = "chef_tl";
        }
        planningScope = (selectedInterneId === "all_chefs") ? "chefs" : "perso";
      } else {
        if (isChefId(selectedInterneId) || selectedInterneId === "all_chefs") {
          selectedInterneId = "gabriel";
        }
        planningScope = (selectedInterneId === "all") ? "internes" : "perso";
      }
      localStorage.setItem(SELECTED_INTERNE_KEY, selectedInterneId);
      renderAll();
    }

    function selectInterne(iid) {
      selectedInterneId = iid;
      if (iid === "all_chefs") {
        planningScope = "chefs";
      } else if (isChefId(iid)) {
        planningScope = "perso";
      } else if (iid === "all") {
        planningScope = "internes";
      } else {
        planningScope = "perso";
      }
      localStorage.setItem(SELECTED_INTERNE_KEY, iid);
      renderAll();
    }

    // Bandeau résumé épuré sur une seule barre lisible (masqué en Mode Chef)
    function renderPersonalBanner() {
      const el = document.getElementById("personalBanner");
      if (!el) return;
      if (isChefPlanningMode) {
        el.style.display = "none";
        el.innerHTML = "";
        return;
      }
      el.style.display = "flex";

      if (selectedInterneId === "all_chefs") {
        el.innerHTML = `
          <div class="summary-left">
            <div class="avatar-sm" style="background:#0284C7">CH</div>
            <div>
              <div class="summary-title">Équipe Chefs & Seniors</div>
              <div class="summary-sub">${(STATE.chefs || []).length} médecins • Vacations, gardes et fermetures</div>
            </div>
          </div>
          <div class="summary-stats">
            <span><strong>6</strong> Internes / DJ</span>
            <span><strong>${STATE.presentations.filter(p => p.type === 'cas_mardi').length}</strong> Mardis</span>
          </div>
        `;
        return;
      }

      if (isChefId(selectedInterneId)) {
        const chef = getChefById(selectedInterneId);
        const cStats = computeChefStats(chef);
        const todaySlots = getChefSlotsForDate(currentDateIso, chef);
        const todayAmTxt = todaySlots.am.length ? todaySlots.am.join(" + ") : "Libre";
        const todayPmTxt = todaySlots.pm.length ? todaySlots.pm.join(" + ") : "Libre";
        const todayAmHtml = todaySlots.am.length ? todaySlots.am.map(p => getPosteWithTimeLabel(p, "am")).join(" + ") : "Libre";
        const todayPmHtml = todaySlots.pm.length ? todaySlots.pm.map(p => getPosteWithTimeLabel(p, "pm")).join(" + ") : "Libre";

        el.innerHTML = `
          <div class="summary-left">
            <div class="avatar-sm" style="background:${chef.color}">${chef.initials}</div>
            <div>
              <div class="summary-title">${chef.fullName}</div>
              <div class="summary-sub">
                <span>${formatDateFr(currentDateIso)} :</span>
                <span class="poste-pill ${getPosteClass(todayAmTxt)}">Matin : ${todayAmHtml}</span>
                <span class="poste-pill ${getPosteClass(todayPmTxt)}">PM : ${todayPmHtml}</span>
                ${todaySlots.isGarde ? `<span class="poste-pill poste-rg">Garde</span>` : ""}
              </div>
            </div>
          </div>
          <div class="summary-stats">
            <span>Poste <strong>${chef.posteTel || "12483"}</strong></span>
            <span><strong>${cStats.totalHalfDays}</strong> vac.</span>
            <span><strong>${cStats.gardesCount}</strong> gardes</span>
            ${chef.code === "TL" ? `<a class="btn btn-sm" href="https://mrthomaslef.github.io/agenda-cochin/" target="_blank" rel="noopener">App RI</a>` : ""}
          </div>
        `;
        return;
      }

      const statsAll = computeStatsByInterne();

      if (selectedInterneId === "all") {
        const mainCounts = ["gabriel", "noe", "marwane", "milan", "nathanael", "oussama"].map(id => statsAll[id].activeHalfDays);
        const avgVac = Math.round(mainCounts.reduce((a, b) => a + b, 0) / mainCounts.length);
        el.innerHTML = `
          <div class="summary-left">
            <div class="avatar-sm" style="background:#0284C7">6</div>
            <div>
              <div class="summary-title">Tous les internes & DJ (6)</div>
              <div class="summary-sub">2 SAU / sem. par interne (3 pour Noé en binôme) • Plus exceptionnellement • Scanners séparés (SAU, Achard, Ollier)</div>
            </div>
          </div>
          <div class="summary-stats">
            <span>Moyenne : <strong>${avgVac}</strong> postes</span>
            <span>SAU : <strong>2/sem. (Noé 3)</strong></span>
            <span>Demi-offs : <strong>2 / sem.</strong></span>
          </div>
        `;
        return;
      }

      const me = getInterneById(selectedInterneId);
      const isDJ = Boolean(me.isDJ || me.id === "oussama");
      const st = statsAll[me.id];
      const daySched = (STATE.schedule[currentDateIso] && STATE.schedule[currentDateIso].byInterne)
        ? STATE.schedule[currentDateIso].byInterne[me.id]
        : null;

      const todayAm = daySched ? daySched.am : "—";
      const todayPm = daySched ? daySched.pm : "—";
      const isTodayAmMand = isMandatoryVacationSlot(currentDateIso, "am", todayAm);
      const isTodayPmMand = isMandatoryVacationSlot(currentDateIso, "pm", todayPm);
      const gIntToday = getInterneGardeInfo(currentDateIso);
      const isMeGardeToday = Boolean(gIntToday && gIntToday.interneId === me.id);

      el.innerHTML = `
        <div class="summary-left">
          <div class="avatar-sm" style="background:${me.color}">${me.initials}</div>
          <div>
            <div class="summary-title">
              ${me.fullName}
              ${me.isSocle ? `<span class="tag-sm">Socle</span>` : ""}
              ${isDJ ? `<span class="tag-dj">Docteur Junior (DJ)</span>` : ""}
              ${isMeGardeToday ? `<span class="poste-pill poste-rg" style="font-size:10px; padding:1px 6px;">🌙 Garde ce soir</span>` : ""}
            </div>
            <div class="summary-sub">
              <span>${formatDateFr(currentDateIso)} :</span>
              <span class="poste-pill ${getPosteClass(todayAm)} ${isTodayAmMand ? 'poste-mandatory-slot' : ''}">${isTodayAmMand ? '<span class="mandatory-dot"></span> ' : ''}Matin : ${getPosteWithTimeLabel(todayAm, "am")}</span>
              <span class="poste-pill ${getPosteClass(todayPm)} ${isTodayPmMand ? 'poste-mandatory-slot' : ''}">${isTodayPmMand ? '<span class="mandatory-dot"></span> ' : ''}PM : ${getPosteWithTimeLabel(todayPm, "pm")}</span>
              ${daySched && daySched.note ? `<span class="tag-binome">${daySched.note}</span>` : ""}
            </div>
          </div>
        </div>
        <div class="summary-stats">
          <span><strong>${st.activeHalfDays}</strong> postes</span>
          <span><strong>${st.freeHalfDays}</strong> demi-offs (${st.freeAmHalfDays || 0} Mat / ${st.freePmHalfDays || 0} PM)</span>
          <span><strong>${st.gardesCount || 0}</strong> gardes (${Math.round((st.rgHalfDays || 0) / 2)} RG)</span>
          <span><strong>${Math.round(st.vacHalfDays / 2)}j</strong> congés</span>
          <span><strong>${st.casMardi + st.biblioVendredi + (st.coursInternes || 0)}</strong> cours</span>
        </div>
      `;
    }

    function switchTab(tab) {
      currentTab = tab;
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-tab") === tab);
      });
      renderTabContent();
    }

    function renderAll() {
      renderChefModeUI();
      renderInterneSelector();
      renderPersonalBanner();
      renderTabContent();
    }

    function renderTabContent() {
      const container = document.getElementById("tabContent");
      if (currentTab === "planning") {
        container.innerHTML = renderPlanningTab();
      } else if (currentTab === "vacances") {
        container.innerHTML = renderVacancesTab();
      } else if (currentTab === "presentations") {
        container.innerHTML = renderPresentationsTab();
      } else if (currentTab === "reunions") {
        container.innerHTML = renderReunionsTab();
      } else if (currentTab === "annuaire") {
        container.innerHTML = renderAnnuaireTab();
      }
    }

    /* =========================================================================
     * BOUTON UNIQUE "+ AJOUTER"
     * ========================================================================= */
    function openQuickAddModal() {
      document.getElementById("modalQuickAdd").classList.add("open");
    }

    function openNextPresentationModal() {
      const upcoming = (STATE.presentations || []).find(p => p.date >= currentDateIso) || (STATE.presentations || [])[0];
      if (upcoming) openPresentationModal(upcoming.id);
    }

    function openQuickVacationPicker() {
      const iid = (!isChefId(selectedInterneId) && selectedInterneId !== "all" && selectedInterneId !== "all_chefs")
        ? selectedInterneId
        : "gabriel";
      openVacationEditModal(currentDateIso, iid);
    }

    /* =========================================================================
     * ONGLET 1 : PLANNING
     * ========================================================================= */
    function renderWeekendGardesCompactBar(monIso) {
      const satIso = addDaysIso(monIso, 5);
      const sunIso = addDaysIso(monIso, 6);
      const [sy, sm, sd] = satIso.split("-").map(Number);
      const [uy, um, ud] = sunIso.split("-").map(Number);
      const gSat = (STATE.chefsGardes && STATE.chefsGardes[satIso] && STATE.chefsGardes[satIso].noms)
        ? `Dr ${STATE.chefsGardes[satIso].noms.join(", ")}`
        : "—";
      const gSun = (STATE.chefsGardes && STATE.chefsGardes[sunIso] && STATE.chefsGardes[sunIso].noms)
        ? `Dr ${STATE.chefsGardes[sunIso].noms.join(", ")}`
        : "—";
      const gIntSat = getInterneGardeInfo(satIso);
      const gIntSun = getInterneGardeInfo(sunIso);
      const intSatLabel = gIntSat
        ? (gIntSat.isRadioB && gIntSat.interneId
          ? `🌙 Int: <strong>${getInterneById(gIntSat.interneId).shortName}</strong>`
          : `🌙 Int: ${gIntSat.rawLabel || "Radio A"}`)
        : "";
      const intSunLabel = gIntSun
        ? (gIntSun.isRadioB && gIntSun.interneId
          ? `🌙 Int: <strong>${getInterneById(gIntSun.interneId).shortName}</strong> (RG lun.)`
          : `🌙 Int: ${gIntSun.rawLabel || "Radio A"}`)
        : "";
      return `
        <div class="weekend-gardes-compact">
          <div class="weekend-garde-mini" onclick="setCurrentDate('${satIso}'); setPlanningMode('day');">
            <span class="wg-day">Sam. ${String(sd).padStart(2, "0")}/${String(sm).padStart(2, "0")} <span style="font-weight:600; color:#991B1B;">(Garde)</span></span>
            <span class="wg-doc">🚨 ${gSat}${intSatLabel ? ` <span style="color:#475569; font-weight:600; margin-left:6px;">• ${intSatLabel}</span>` : ""}</span>
          </div>
          <div class="weekend-garde-mini" onclick="setCurrentDate('${sunIso}'); setPlanningMode('day');">
            <span class="wg-day">Dim. ${String(ud).padStart(2, "0")}/${String(um).padStart(2, "0")} <span style="font-weight:600; color:#991B1B;">(Garde)</span></span>
            <span class="wg-doc">🚨 ${gSun}${intSunLabel ? ` <span style="color:#475569; font-weight:600; margin-left:6px;">• ${intSunLabel}</span>` : ""}</span>
          </div>
        </div>
      `;
    }

    function renderPlanningTab() {
      const monIso = getMondayOfWeek(currentDateIso);
      const friIso = addDaysIso(monIso, 4);
      const inChefSpace = Boolean(isChefPlanningMode);
      const blocking = inChefSpace ? computeBlockingDays(STATE) : { byDate: {}, list: [] };

      let headerLabel = "";
      if (planningMode === "day") {
        headerLabel = formatDateFr(currentDateIso, true);
      } else if (planningMode === "week") {
        headerLabel = `${formatDateFr(monIso)} – ${formatDateFr(friIso)}`;
      } else {
        const [y, m] = currentDateIso.split("-").map(Number);
        const mNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];
        headerLabel = `${mNames[m - 1]} ${y}`;
      }

      const dNames = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
      let dayStripHtml = `<div class="day-strip">`;
      // Lundi à Vendredi (5 jours principaux)
      for (let offset = 0; offset < 5; offset++) {
        const dIso = addDaysIso(monIso, offset);
        const [yy, mm, dd] = dIso.split("-").map(Number);
        const isAct = (dIso === currentDateIso) ? "active" : "";
        const dayIssues = inChefSpace ? (blocking.byDate[dIso] || []).filter(x => x.severity === "critical") : [];
        const isBlock = dayIssues.length > 0 ? "blocking-day" : "";
        const g = (STATE.chefsGardes && STATE.chefsGardes[dIso] && STATE.chefsGardes[dIso].noms)
          ? STATE.chefsGardes[dIso].noms.join("/")
          : "";
        const gInt = getInterneGardeInfo(dIso);
        const gIntLabel = (gInt && gInt.isRadioB && gInt.interneId)
          ? `🌙 ${getInterneById(gInt.interneId).shortName}`
          : (gInt && gInt.rawLabel ? `🌙 ${gInt.rawLabel.split(" ")[0]}` : "");
        const gardeSubLabel = [g ? `Dr ${g}` : "", gIntLabel].filter(Boolean).join(" • ");
        dayStripHtml += `
          <div class="day-pill ${isAct} ${isBlock}" onclick="setCurrentDate('${dIso}')" title="${dayIssues.length ? dayIssues.map(x => x.title).join(' • ') : gardeSubLabel}">
            <div class="dp-top">
              <span class="dp-dow">${dNames[offset]}${dayIssues.length ? ' •' : ''}</span>
              <span class="dp-date">${String(dd).padStart(2, "0")}/${String(mm).padStart(2, "0")}</span>
            </div>
            ${dayIssues.length
              ? `<div class="dp-sub" style="color:${isAct ? '#FDE68A' : '#DC2626'}; font-weight:800;">À couvrir (${dayIssues.length})</div>`
              : (gardeSubLabel ? `<div class="dp-sub">${gardeSubLabel}</div>` : ``)}
          </div>
        `;
      }
      // Samedi et Dimanche en petit avec juste les gardes
      for (let offset = 5; offset < 7; offset++) {
        const dIso = addDaysIso(monIso, offset);
        const [yy, mm, dd] = dIso.split("-").map(Number);
        const isAct = (dIso === currentDateIso) ? "active" : "";
        const g = (STATE.chefsGardes && STATE.chefsGardes[dIso] && STATE.chefsGardes[dIso].noms)
          ? STATE.chefsGardes[dIso].noms.join("/")
          : "—";
        const gInt = getInterneGardeInfo(dIso);
        const gIntShort = (gInt && gInt.isRadioB && gInt.interneId)
          ? getInterneById(gInt.interneId).shortName
          : (gInt && gInt.rawLabel ? gInt.rawLabel.split(" ")[0] : "");
        dayStripHtml += `
          <div class="day-pill weekend-pill ${isAct}" onclick="setCurrentDate('${dIso}')" title="Garde ${dNames[offset]} ${dd}/${mm} : Dr ${g}${gIntShort ? ' • Int: ' + gIntShort : ''}">
            <div class="dp-top">
              <span class="dp-dow">${dNames[offset]}</span>
              <span class="dp-date">${String(dd).padStart(2, "0")}/${String(mm).padStart(2, "0")}</span>
            </div>
            <div class="dp-garde">🚨 ${g}${gIntShort ? ` • 🌙 ${gIntShort}` : ""}</div>
          </div>
        `;
      }
      dayStripHtml += `</div>`;

      const horairesStripHtml = isChefPlanningMode ? "" : `
        <div style="display:flex; flex-wrap:wrap; align-items:center; gap:5px; margin-bottom:8px; font-size:11px;">
          <span style="font-weight:700; color:var(--text-muted); margin-right:2px;">🕒 Horaires :</span>
          <span class="poste-pill poste-irm">IRM : 07h45</span>
          <span class="poste-pill poste-tdm">TDM SAU : 08h00 – 18h30</span>
          <span class="poste-pill poste-echo">Écho : 09h00</span>
          <span class="poste-pill poste-gestes">Poste C : 09h00</span>
          <span class="poste-pill poste-cs">Consult. Internes : Mar PM (Relecture Pr Drapé) & Ven PM</span>
          <span class="poste-pill poste-mandatory-slot" title="Vacations obligatoires prioritaires (TDM SAU permanent + Écho lun. AM, IRM lun. PM, Poste C & IRM 3T/1,5T mar. AM, Relecture mar. PM, IRM 3T/1,5T mer. AM, Poste C/IRM/Achard/Écho mer. PM, Écho & Poste C jeu. AM, IRM jeu. PM, IRM 3T ven. AM)"><span class="mandatory-dot"></span> Vacation obligatoire</span>
        </div>
      `;

      const weekLock = getWeekLockInfo(monIso);
      let weekValidationStripHtml = "";
      if (planningMode !== "month" && weekLock && !inChefSpace) {
        weekValidationStripHtml = `
          <div class="week-status-strip locked">
            <div>
              <strong>📌 Planning de la semaine (${formatDateFr(monIso)} – ${formatDateFr(friIso)}) validé & fixé</strong>
            </div>
            <div style="display:flex; gap:6px; align-items:center;">
              <span class="status-pill-approved">✓ Semaine fixée</span>
            </div>
          </div>
        `;
      }

      let bodyHtml = "";
      if (planningScope === "chefs" && !isChefPlanningMode) {
        bodyHtml = renderChefsPlanningView(monIso);
      } else if (planningScope === "combined") {
        bodyHtml = renderCombinedChefsInternesView(monIso);
      } else if (planningScope === "perso" && isChefId(selectedInterneId) && !isChefPlanningMode) {
        bodyHtml = renderSingleChefPersoView(monIso, getChefById(selectedInterneId));
      } else if (planningMode === "day") {
        bodyHtml = renderDayPlanningView(currentDateIso);
      } else if (planningMode === "week" || isChefPlanningMode) {
        bodyHtml = renderWeekPlanningView(monIso);
      } else {
        bodyHtml = renderMonthPlanningView(currentDateIso);
      }

      const toolbarScopeHtml = isChefPlanningMode
        ? `<div class="segmented">
             <button class="seg-btn ${planningScope !== 'combined' ? 'active' : ''}" onclick="setPlanningScope('internes')">Internes seuls</button>
             <button class="seg-btn ${planningScope === 'combined' ? 'active' : ''}" onclick="setPlanningScope('combined')">Avec les Chefs</button>
           </div>`
        : `<div class="segmented">
             <button class="seg-btn ${planningScope === 'internes' ? 'active' : ''}" onclick="setPlanningScope('internes')">Internes</button>
             <button class="seg-btn ${planningScope === 'chefs' ? 'active' : ''}" onclick="setPlanningScope('chefs')">Chefs</button>
             <button class="seg-btn ${planningScope === 'combined' ? 'active' : ''}" onclick="setPlanningScope('combined')">Croisé</button>
             <button class="seg-btn ${planningScope === 'perso' ? 'active' : ''}" onclick="setPlanningScope('perso')">Mon planning</button>
           </div>`;

      const toolbarModeHtml = isChefPlanningMode
        ? `<div class="segmented">
             <button class="seg-btn ${planningMode !== 'day' ? 'active' : ''}" onclick="setPlanningMode('week')">Semaine</button>
             <button class="seg-btn ${planningMode === 'day' ? 'active' : ''}" onclick="setPlanningMode('day')">Jour</button>
           </div>`
        : `<div class="segmented">
             <button class="seg-btn ${planningMode === 'day' ? 'active' : ''}" onclick="setPlanningMode('day')">Jour</button>
             <button class="seg-btn ${planningMode === 'week' ? 'active' : ''}" onclick="setPlanningMode('week')">Semaine</button>
             <button class="seg-btn ${planningMode === 'month' ? 'active' : ''}" onclick="setPlanningMode('month')">Mois</button>
           </div>`;

      return `
        <div class="planning-toolbar">
          ${toolbarScopeHtml}

          <div class="date-nav">
            <button class="btn btn-sm" onclick="shiftPlanningDate(-1)">◀ Préc.</button>
            <div class="date-label">${headerLabel}</div>
            <button class="btn btn-sm" onclick="shiftPlanningDate(1)">Suiv. ▶</button>
          </div>

          ${toolbarModeHtml}
        </div>

        ${(isChefPlanningMode && planningMode !== 'day') ? '' : dayStripHtml}
        ${weekValidationStripHtml}
        ${horairesStripHtml}
        ${bodyHtml}
        ${renderBalanceSummaryCard()}
      `;
    }

    function setPlanningScope(sc) {
      planningScope = sc;
      if (sc === "perso") {
        if (selectedInterneId === "all") selectedInterneId = "gabriel";
        if (selectedInterneId === "all_chefs") selectedInterneId = "chef_tl";
      } else if (sc === "internes") {
        selectedInterneId = "all";
      } else if (sc === "chefs") {
        selectedInterneId = "all_chefs";
      }
      localStorage.setItem(SELECTED_INTERNE_KEY, selectedInterneId);
      renderAll();
    }

    function setPlanningMode(md) {
      planningMode = md;
      renderTabContent();
    }

    function setCurrentDate(iso) {
      currentDateIso = iso;
      renderAll();
    }

    function shiftPlanningDate(dir) {
      if (planningMode === "day") {
        currentDateIso = addDaysIso(currentDateIso, dir);
      } else if (planningMode === "week") {
        currentDateIso = addDaysIso(currentDateIso, dir * 7);
      } else {
        const [y, m] = currentDateIso.split("-").map(Number);
        const dt = new Date(y, m - 1 + dir, 2, 12, 0, 0);
        const yy = dt.getFullYear();
        const mm = String(dt.getMonth() + 1).padStart(2, "0");
        const dd = String(dt.getDate()).padStart(2, "0");
        currentDateIso = `${yy}-${mm}-${dd}`;
      }
      renderAll();
    }

    function renderSingleChefPersoView(monIso, chef) {
      if (planningMode === "month") {
        const ym = currentDateIso.slice(0, 7);
        const allDates = Object.keys(STATE.chefsPlanning || {}).filter(k => k.startsWith(ym)).sort();
        let cells = "";
        allDates.forEach(dIso => {
          const sl = getChefSlotsForDate(dIso, chef);
          cells += `
            <div class="month-cell ${dIso === currentDateIso ? 'today' : ''}" onclick="setCurrentDate('${dIso}'); setPlanningMode('day');">
              <div style="display:flex; justify-content:space-between; font-weight:800; font-size:12px;">
                <span>${formatDateFr(dIso)}</span>
                ${sl.isGarde ? '<span class="tag-sm">Garde</span>' : ''}
              </div>
              <div style="font-size:10px; color:var(--text-muted);">Matin</div>
              ${sl.am.length ? sl.am.map(p => `<span class="poste-pill ${getPosteClass(p)}" style="font-size:10px; padding:2px 6px;">${getPosteWithTimeLabel(p, "am")}</span>`).join(" ") : `<span style="font-size:10.5px; color:var(--text-muted);">—</span>`}
              <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Après-midi</div>
              ${sl.pm.length ? sl.pm.map(p => `<span class="poste-pill ${getPosteClass(p)}" style="font-size:10px; padding:2px 6px;">${getPosteWithTimeLabel(p, "pm")}</span>`).join(" ") : `<span style="font-size:10.5px; color:var(--text-muted);">—</span>`}
            </div>
          `;
        });
        return `
          <div class="card">
            <div class="card-header">
              <div class="card-title">Mois — ${chef.fullName}</div>
            </div>
            <div class="month-grid">${cells}</div>
          </div>
        `;
      }

      const days = [0, 1, 2, 3, 4].map(off => addDaysIso(monIso, off));
      let cardsHtml = `
        <div class="card" style="padding:12px 10px 0; overflow:hidden;">
          <div class="card-header" style="padding:0 4px;">
            <div class="card-title">Semaine (Lun–Ven) — ${chef.fullName}</div>
          </div>
          <div class="perso-week-grid" style="margin-bottom:10px;">
      `;
      days.forEach(dIso => {
        const sl = getChefSlotsForDate(dIso, chef);
        const intDay = STATE.schedule[dIso] || { am: [], pm: [] };

        function findMatchingInternes(chefPostes, intPeriodList) {
          const out = [];
          (chefPostes || []).forEach(cp => {
            const pUp = cp.toUpperCase();
            (intPeriodList || []).forEach(it => {
              if (it.closed) return;
              const iUp = String(it.poste || "").toUpperCase();
              if (
                (pUp.includes("ACHARD") && iUp.includes("ACHARD")) ||
                (pUp.includes("GESTES") && iUp.includes("GESTES")) ||
                (pUp.includes("SAU") && iUp.includes("SAU")) ||
                (pUp.includes("OLLIER 3") && iUp.includes("OLLIER DIAG")) ||
                (pUp.includes("IRM") && iUp.includes("IRM")) ||
                (pUp.includes("ECHO") && iUp.includes("ECHO")) ||
                (pUp.includes("ALLURA") && iUp.includes("ALLURA")) ||
                (pUp.includes("CONSULT") && iUp.includes("LECTURE"))
              ) {
                const tag = `${it.interne}`;
                if (!out.includes(tag)) out.push(tag);
              }
            });
          });
          return out;
        }
        const intAm = findMatchingInternes(sl.am, intDay.am);
        const intPm = findMatchingInternes(sl.pm, intDay.pm);

        cardsHtml += `
          <div class="card perso-day-card" style="margin:0; padding:8px 6px; background:#F8FAFC;">
            <div style="font-weight:800; font-size:11.5px; margin-bottom:6px; color:${chef.color}; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:2px;">
              <span>${formatShortDayHeader(dIso)}</span>
              ${sl.isGarde ? `<span class="poste-pill poste-rg" style="font-size:9px; padding:1px 4px;">Garde</span>` : ``}
            </div>
            <div style="margin-bottom:6px;">
              <div style="font-size:9px; color:var(--text-muted); font-weight:700;">MATIN</div>
              <div style="margin-top:2px; display:flex; flex-wrap:wrap; gap:3px;">
                ${sl.am.length ? sl.am.map(p => `<span class="poste-pill ${getPosteClass(p)}">${getPosteWithTimeLabel(p, "am")}</span>`).join("") : `<span class="poste-pill poste-off">Libre</span>`}
              </div>
              ${intAm.length ? `<div style="font-size:9.5px; color:#0284C7; margin-top:3px;">Int: <strong>${intAm.join(", ")}</strong></div>` : ``}
            </div>
            <div>
              <div style="font-size:9px; color:var(--text-muted); font-weight:700;">APRÈS-MIDI</div>
              <div style="margin-top:2px; display:flex; flex-wrap:wrap; gap:3px;">
                ${sl.pm.length ? sl.pm.map(p => `<span class="poste-pill ${getPosteClass(p)}">${getPosteWithTimeLabel(p, "pm")}</span>`).join("") : `<span class="poste-pill poste-off">Libre</span>`}
              </div>
              ${intPm.length ? `<div style="font-size:9.5px; color:#7C3AED; margin-top:3px;">Int: <strong>${intPm.join(", ")}</strong></div>` : ``}
            </div>
          </div>
        `;
      });
      cardsHtml += `</div>${renderWeekendGardesCompactBar(monIso)}</div>`;
      return cardsHtml;
    }

    function renderCombinedChefsInternesView(monIso) {
      const days = [0, 1, 2, 3, 4].map(off => addDaysIso(monIso, off));
      const sectors = [
        { label: "FORMATION / ACCUEIL", chefMatch: [], intMatch: ["FORMATION / ACCUEIL"], defaultPosteAm: "FORMATION / ACCUEIL", defaultPostePm: "FORMATION / ACCUEIL", onlyIfPresent: true },
        { label: "ECHO", chefMatch: ["ECHO"], intMatch: ["ECHO"], defaultPosteAm: "ECHO", defaultPostePm: "ECHO" },
        { label: "GESTES (C)", chefMatch: ["GESTES"], intMatch: ["GESTES (C)"], defaultPosteAm: "GESTES (C)", defaultPostePm: "GESTES (C)" },
        { label: "TDM SAU", chefMatch: ["SAU", "OLLIER 4"], intMatch: ["TDM SAU"], defaultPosteAm: "TDM SAU", defaultPostePm: "TDM SAU" },
        { label: "SCAN ACHARD", chefMatch: ["ACHARD"], intMatch: ["SCAN ACHARD"], defaultPosteAm: "SCAN ACHARD", defaultPostePm: "SCAN ACHARD" },
        { label: "TDM OLLIER", chefMatch: ["OLLIER 3"], intMatch: ["TDM OLLIER DIAG"], defaultPosteAm: "TDM OLLIER DIAG", defaultPostePm: "TDM OLLIER DIAG" },
        { label: "ALLURA", chefMatch: ["ALLURA"], intMatch: ["ALLURA"], defaultPosteAm: "ALLURA", defaultPostePm: "ALLURA" },
        { label: "IRM", chefMatch: ["IRM"], intMatch: ["IRM 3T", "IRM 1,5T", "IRM"], defaultPosteAm: "IRM 3T", defaultPostePm: "IRM" },
        { label: "CONSULT / LECTURE", chefMatch: ["CONSULT", "UCSA"], intMatch: ["LECTURE/CS"], defaultPosteAm: "LECTURE/CS", defaultPostePm: "LECTURE/CS" },
        { label: "DEMI-OFF", chefMatch: ["LIBRE"], intMatch: ["1/2 journée libre"], defaultPosteAm: "1/2 journée libre", defaultPostePm: "1/2 journée libre" },
        { label: "REPOS DE GARDE (RG)", chefMatch: [], intMatch: ["RG"], defaultPosteAm: "RG", defaultPostePm: "RG", onlyIfPresent: true }
      ];

      function buildCombinedPeriodRows(periodKey) {
        let rows = "";
        sectors.forEach(sec => {
          if (sec.onlyIfPresent) {
            const hasAny = days.some(dIso => {
              const intDay = (STATE.schedule && STATE.schedule[dIso]) ? (STATE.schedule[dIso][periodKey] || []) : [];
              return intDay.some(x => sec.intMatch.includes(x.poste));
            });
            if (!hasAny) return;
          }
          const targetPoste = periodKey === "am" ? sec.defaultPosteAm : sec.defaultPostePm;
          const escPoste = targetPoste.replace(/'/g, "\\'");
          rows += `<tr><td>${renderPosteCellLabel(sec.label, periodKey)}</td>`;
          days.forEach(dIso => {
            const chDay = (STATE.chefsPlanning && STATE.chefsPlanning[dIso]) ? (STATE.chefsPlanning[dIso][periodKey] || []) : [];
            const intDay = (STATE.schedule && STATE.schedule[dIso]) ? (STATE.schedule[dIso][periodKey] || []) : [];

            const matchedChefs = chDay.filter(x => sec.chefMatch.some(m => String(x.poste || "").toUpperCase().includes(m)));
            const matchedInts = intDay.filter(x => {
              if (!sec.intMatch.includes(x.poste)) return false;
              if (!x.closed && selectedInterneId !== "all" && !isChefId(selectedInterneId) && selectedInterneId !== "all_chefs" && x.interneId !== selectedInterneId) {
                return false;
              }
              return true;
            });

            let cellHtml = "";
            if (matchedChefs.length > 0) {
              cellHtml += `<div style="margin-bottom:2px;">` + matchedChefs.map(c => {
                const isClosedDoc = (c.doc === "FERMÉ" || c.doc === "MAINTENANCE" || c.closed);
                if (isClosedDoc) {
                  return `<span class="poste-pill poste-closed" style="margin:1px; font-size:9px;">Fermé</span>`;
                }
                return `<span style="display:inline-block; font-size:9.5px; font-weight:700; color:#0369A1; background:#E0F2FE; border-radius:4px; padding:1px 4px; margin:1px;">${c.doc}</span>`;
              }).join("") + `</div>`;
            }
            if (matchedInts.length > 0) {
              cellHtml += `<div>` + matchedInts.map(m => {
                if (m.closed) {
                  return `<span class="poste-pill poste-closed" style="margin:1px; font-size:9px;">${m.reason || 'Fermé'}</span>`;
                }
                const iObj = getInterneById(m.interneId);
                const isSelectedMove = isChefPlanningMode && selectedForMove && selectedForMove.interneId === m.interneId && selectedForMove.dIso === dIso && selectedForMove.periodKey === periodKey;
                const dragClass = isChefPlanningMode ? `draggable-interne ${isSelectedMove ? 'selected-for-move' : ''}` : "";
                const mPosteEsc = String(m.poste || targetPoste).replace(/'/g, "\\'");
                const dragAttrs = isChefPlanningMode
                  ? `draggable="true" ondragstart="onInterneDragStart(event, '${dIso}', '${periodKey}', '${m.interneId}', '${mPosteEsc}')" ondragend="onInterneDragEnd(event)" ondragover="onCellDragOver(event, '${dIso}', '${periodKey}')" ondrop="onBadgeDrop(event, '${dIso}', '${periodKey}', '${m.interneId}', '${mPosteEsc}')"`
                  : "";
                return `<span class="interne-badge ${dragClass}" ${dragAttrs} onclick="onInterneBadgeClick(event, '${dIso}', '${periodKey}', '${m.interneId}', '${mPosteEsc}')" style="margin:1px;">
                  ${isChefPlanningMode ? `<span class="drag-grip">⋮⋮</span>` : ""}
                  <span style="width:6px;height:6px;border-radius:50%;background:${iObj.color};display:inline-block;"></span>
                  ${iObj.shortName}
                </span>`;
              }).join("") + `</div>`;
            }
            const isMandatorySec = sec.intMatch.some(p => isMandatoryVacationSlot(dIso, periodKey, p));
            const canDrop = isChefPlanningMode;
            const isTapTarget = canDrop && selectedForMove && selectedForMove.dIso === dIso && selectedForMove.periodKey === periodKey;
            const tdClass = [
              canDrop ? "drop-zone-cell" : "",
              isTapTarget ? "tap-target-ready" : "",
              isMandatorySec ? "cell-mandatory-vacation" : ""
            ].filter(Boolean).join(" ");
            const tdAttrs = canDrop
              ? `ondragover="onCellDragOver(event, '${dIso}', '${periodKey}')" ondragleave="onCellDragLeave(event)" ondrop="onCellDrop(event, '${dIso}', '${periodKey}', '${escPoste}')" onclick="onChefCellClick(event, '${dIso}', '${periodKey}', '${escPoste}')"`
              : "";
            rows += `<td class="${tdClass}" ${tdAttrs} ${isMandatorySec ? 'title="Vacation obligatoire prioritaire"' : ''}>${cellHtml || '<span style="color:#CBD5E1">—</span>'}</td>`;
          });
          rows += `</tr>`;
        });
        return rows;
      }

      let intGardeRowHtml = `<tr><td><span class="poste-pill poste-rg">GARDE INTERNE</span></td>`;
      days.forEach(dIso => {
        intGardeRowHtml += `<td>${renderInterneGardeCellHtml(dIso)}</td>`;
      });
      intGardeRowHtml += `</tr>`;

      let gardeRowHtml = `<tr><td><span class="poste-pill poste-rg">GARDE SENIOR</span></td>`;
      days.forEach(dIso => {
        const g = STATE.chefsGardes ? STATE.chefsGardes[dIso] : null;
        gardeRowHtml += `<td>${g && g.noms ? `<span class="garde-name" style="font-weight:700; color:#B91C1C;" title="Dr ${g.noms.join(", ")}"><span class="garde-dr">Dr </span>${g.noms.join(", ")}</span>` : '—'}</td>`;
      });
      gardeRowHtml += `</tr>`;

      return `
        <div class="card" style="padding:0; overflow:hidden;">
          <div class="week-table-wrap" style="border:none; border-radius:0;">
            <table class="planning-table week-5col">
              <thead>
                <tr>
                  <th class="col-poste">POSTE</th>
                  ${days.map(d => `<th>${formatShortDayHeader(d)}</th>`).join("")}
                </tr>
              </thead>
              <tbody>
                <tr class="period-divider"><td colspan="6">MATIN — IRM 07h45 • TDM SAU 08h00 • Écho & Poste C 09h00</td></tr>
                ${buildCombinedPeriodRows("am")}
                <tr class="period-divider"><td colspan="6">APRÈS-MIDI — TDM SAU fin 18h30</td></tr>
                ${buildCombinedPeriodRows("pm")}
                <tr class="period-divider"><td colspan="6">GARDES (LUN–VEN)</td></tr>
                ${intGardeRowHtml}
                ${gardeRowHtml}
              </tbody>
            </table>
          </div>
          ${renderWeekendGardesCompactBar(monIso)}
        </div>
      `;
    }

    function renderWeekPlanningView(monIso) {
      const days = [0, 1, 2, 3, 4].map(off => addDaysIso(monIso, off));
      const postesAm = ["FORMATION / ACCUEIL", "ECHO", "GESTES (C)", "TDM SAU", "SCAN ACHARD", "TDM OLLIER DIAG", "IRM 3T", "IRM 1,5T", "LECTURE/CS", "1/2 journée libre", "RG", "VACANCES"];
      const postesPm = ["GESTES (C)", "TDM SAU", "SCAN ACHARD", "TDM OLLIER DIAG", "IRM", "ECHO", "ALLURA", "LECTURE/CS", "1/2 journée libre", "RG", "VACANCES"];
      const inChefSpace = (selectedInterneId === "all_chefs" || isChefId(selectedInterneId) || isChefPlanningMode);
      const blocking = inChefSpace ? computeBlockingDays(STATE) : { byDate: {}, list: [] };

      const isSingleInterneSelected = !isChefId(selectedInterneId) && selectedInterneId !== "all" && selectedInterneId !== "all_chefs";
      if (planningScope === "perso" || (isSingleInterneSelected && !isChefPlanningMode)) {
        const me = getInterneById(selectedInterneId === "all" ? "gabriel" : selectedInterneId);
        let cardsHtml = `
          <div class="card" style="padding:12px 10px 0; overflow:hidden;">
            <div class="card-header" style="padding:0 4px;">
              <div class="card-title">Semaine (Lun–Ven) — ${me.fullName}</div>
              <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                <span style="font-size:11px; color:var(--text-muted);">Touchez un jour pour modifier</span>
                <button class="btn btn-sm" onclick="selectInterne('all')">Voir tous les internes</button>
              </div>
            </div>
            <div class="perso-week-grid" style="margin-bottom:10px;">
        `;
        days.forEach(dIso => {
          const dObj = STATE.schedule[dIso] || {};
          const slot = (dObj.byInterne && dObj.byInterne[me.id]) ? dObj.byInterne[me.id] : { am: "—", pm: "—", note: "" };
          const isAmMand = isMandatoryVacationSlot(dIso, "am", slot.am);
          const isPmMand = isMandatoryVacationSlot(dIso, "pm", slot.pm);
          const presList = STATE.presentations.filter(p => p.date === dIso && (p.interneId === me.id || (p.interneName && p.interneName.toLowerCase().includes(me.shortName.toLowerCase()))));
          const gInt = getInterneGardeInfo(dIso);
          const isMeOnGarde = Boolean(gInt && gInt.interneId === me.id);
          cardsHtml += `
            <div class="card perso-day-card" style="margin:0; padding:8px 6px; background:${isMeOnGarde ? '#FEF2F2' : '#F8FAFC'}; border-color:${isMeOnGarde ? '#FCA5A5' : 'var(--border)'}; cursor:pointer;" onclick="openVacationEditModal('${dIso}', '${me.id}')">
              <div style="font-weight:800; font-size:11.5px; margin-bottom:6px; color:var(--primary); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:2px;">
                <span>${formatShortDayHeader(dIso)}</span>
                ${isMeOnGarde ? `<span class="poste-pill poste-rg" style="font-size:9px; padding:1px 5px;">🌙 Garde ce soir</span>` : ""}
              </div>
              <div style="margin-bottom:5px; ${isAmMand ? 'background:#FFF5F5; border-left:2.5px solid #FCA5A5; padding:2px 4px; border-radius:5px;' : ''}">
                <div style="font-size:8.5px; color:${isAmMand ? '#9F1239' : 'var(--text-muted)'}; font-weight:700; display:flex; align-items:center; gap:3px;">MATIN ${isAmMand ? '<span class="mandatory-dot" title="Vacation obligatoire"></span>' : ''}</div>
                <span class="poste-pill ${getPosteClass(slot.am)} ${isAmMand ? 'poste-mandatory-slot' : ''}" style="margin-top:2px;">${getPosteWithTimeLabel(slot.am, "am")}</span>
              </div>
              <div style="${isPmMand ? 'background:#FFF5F5; border-left:2.5px solid #FCA5A5; padding:2px 4px; border-radius:5px;' : ''}">
                <div style="font-size:8.5px; color:${isPmMand ? '#9F1239' : 'var(--text-muted)'}; font-weight:700; display:flex; align-items:center; gap:3px;">APRÈS-MIDI ${isPmMand ? '<span class="mandatory-dot" title="Vacation obligatoire"></span>' : ''}</div>
                <span class="poste-pill ${getPosteClass(slot.pm)} ${isPmMand ? 'poste-mandatory-slot' : ''}" style="margin-top:2px;">${getPosteWithTimeLabel(slot.pm, "pm")}</span>
              </div>
              ${slot.note ? `<div style="font-size:9.5px; color:#0369A1; font-weight:700; margin-top:4px;">${slot.note}</div>` : ''}
              ${isMeOnGarde ? `<div style="font-size:9.5px; color:#991B1B; font-weight:800; margin-top:4px;">🌙 Garde Radio (RG demain)</div>` : ''}
              ${presList.map(p => `<div style="font-size:9.5px; color:#6D28D9; font-weight:700; margin-top:3px;">12h30: ${p.typeLabel || 'Cours'}</div>`).join("")}
            </div>
          `;
        });
        cardsHtml += `</div>${renderWeekendGardesCompactBar(monIso)}</div>`;
        return cardsHtml;
      }

      function renderPeriodRows(postesList, periodKey) {
        let rowsHtml = "";
        postesList.forEach(posteName => {
          const hasAny = days.some(dIso => {
            const dObj = STATE.schedule[dIso];
            if (!dObj || !dObj[periodKey]) return false;
            return dObj[periodKey].some(x => x.poste === posteName);
          });
          if (!hasAny && posteName === "FORMATION / ACCUEIL") return;
          if (periodKey === "am" && posteName === "LECTURE/CS" && !hasAny && !isChefPlanningMode) return;
          if (!isChefPlanningMode && !hasAny && (posteName === "RG" || posteName === "VACANCES")) return;

          const escPoste = posteName.replace(/'/g, "\\'");
          const canClickPosteTarget = isChefPlanningMode && selectedForMove && selectedForMove.periodKey === periodKey;
          const posteTdAttr = canClickPosteTarget
            ? `class="tap-target-ready" style="cursor:pointer;" title="Déplacer vers ${posteName}" onclick="onChefCellClick(event, '${selectedForMove.dIso}', '${periodKey}', '${escPoste}')"`
            : "";
          rowsHtml += `<tr><td ${posteTdAttr}>${renderPosteCellLabel(posteName, periodKey)}</td>`;
          days.forEach(dIso => {
            const dObj = STATE.schedule[dIso];
            if (!dObj) {
              rowsHtml += `<td>—</td>`;
              return;
            }
            if (dObj.holiday) {
              rowsHtml += `<td><span class="poste-pill poste-rg">Férié</span></td>`;
              return;
            }
            const matches = (dObj[periodKey] || []).filter(x => x.poste === posteName);
            const isMandatoryCell = isMandatoryVacationSlot(dIso, periodKey, posteName);
            const cellIssue = inChefSpace ? (blocking.byDate[dIso] || []).find(iss => iss.periodKey === periodKey && iss.poste === posteName) : null;
            const canDrop = isChefPlanningMode;
            const isTapTarget = canDrop && selectedForMove && selectedForMove.dIso === dIso && selectedForMove.periodKey === periodKey;
            const tdClass = [
              canDrop ? "drop-zone-cell" : "",
              isTapTarget ? "tap-target-ready" : "",
              cellIssue ? "cell-blocking-alert" : (isMandatoryCell ? "cell-mandatory-vacation" : "")
            ].filter(Boolean).join(" ");
            const tdAttrs = canDrop
              ? `ondragover="onCellDragOver(event, '${dIso}', '${periodKey}')" ondragleave="onCellDragLeave(event)" ondrop="onCellDrop(event, '${dIso}', '${periodKey}', '${escPoste}')" onclick="onChefCellClick(event, '${dIso}', '${periodKey}', '${escPoste}')"`
              : "";
            const mandatoryTitleAttr = isMandatoryCell ? `title="Vacation obligatoire prioritaire (${posteName})"` : "";

            const issueBannerHtml = cellIssue
              ? `<div style="margin-top:2px;"><span class="poste-pill poste-rg" style="font-size:9px; background:#DC2626; color:#FFF;">À couvrir</span></div>`
              : "";

            if (matches.length === 0) {
              rowsHtml += `<td class="${tdClass}" ${tdAttrs} ${mandatoryTitleAttr} style="color:#CBD5E1">${cellIssue ? issueBannerHtml : '—'}</td>`;
            } else {
              const [yy, mm, dd] = dIso.split("-").map(Number);
              const jsDay = new Date(yy, mm - 1, dd).getDay();
              const badges = matches.map(m => {
                if (m.closed) {
                  return `<span class="poste-pill poste-closed">${m.reason === "MAINTENANCE" ? "Maint." : "Fermé"}</span>`;
                }
                const iObj = getInterneById(m.interneId);
                const isMe = (selectedInterneId !== "all" && m.interneId === selectedInterneId) ? "highlight-me" : "";
                const isSelectedMove = isChefPlanningMode && selectedForMove && selectedForMove.interneId === m.interneId && selectedForMove.dIso === dIso && selectedForMove.periodKey === periodKey;
                const dragClass = isChefPlanningMode ? `draggable-interne ${isSelectedMove ? 'selected-for-move' : ''}` : "";
                const socleHtml = (!isChefPlanningMode && iObj.isSocle) ? `<span class="tag-sm">Socle</span>` : "";
                const djHtml = (!isChefPlanningMode && (iObj.isDJ || iObj.id === "oussama")) ? `<span class="tag-dj">DJ</span>` : "";
                let binomeHtml = "";
                if (!isChefPlanningMode) {
                  if (posteName === "LECTURE/CS" && periodKey === "pm" && jsDay === 2) {
                    binomeHtml = `<span class="tag-binome">Relecture Pr Drapé</span>`;
                  } else if (posteName === "LECTURE/CS" && periodKey === "pm" && jsDay === 5) {
                    binomeHtml = `<span class="tag-binome">Consult.</span>`;
                  } else if (m.note && m.note.includes("Macil")) {
                    binomeHtml = `<span class="tag-binome">${m.binome ? 'Binôme • +Macil' : '+Macil'}</span>`;
                  } else if (m.binome) {
                    binomeHtml = `<span class="tag-binome">Binôme</span>`;
                  }
                }
                let vacStatusHtml = "";
                if (inChefSpace && (posteName === "VACANCES" || posteName === "RG")) {
                  if (m.absStatus === "pending") {
                    vacStatusHtml = `<span class="status-pill-pending" style="font-size:8.5px; padding:1px 4px;">À valider</span>`;
                  }
                }
                const dragAttrs = isChefPlanningMode
                  ? `draggable="true" ondragstart="onInterneDragStart(event, '${dIso}', '${periodKey}', '${m.interneId}', '${escPoste}')" ondragend="onInterneDragEnd(event)" ondragover="onCellDragOver(event, '${dIso}', '${periodKey}')" ondrop="onBadgeDrop(event, '${dIso}', '${periodKey}', '${m.interneId}', '${escPoste}')"`
                  : "";
                return `<span class="interne-badge ${isMe} ${dragClass}" ${dragAttrs} onclick="onInterneBadgeClick(event, '${dIso}', '${periodKey}', '${m.interneId}', '${escPoste}')">
                  ${isChefPlanningMode ? `<span class="drag-grip">⋮⋮</span>` : ""}
                  <span style="width:6px;height:6px;border-radius:50%;background:${iObj.color};display:inline-block;"></span>
                  ${iObj.shortName}
                  ${socleHtml}
                  ${djHtml}
                  ${binomeHtml}
                  ${vacStatusHtml}
                </span>`;
              }).join(" ");
              rowsHtml += `<td class="${tdClass}" ${tdAttrs} ${mandatoryTitleAttr}>${badges}${issueBannerHtml}</td>`;
            }
          });
          rowsHtml += `</tr>`;
        });
        return rowsHtml;
      }

      let staffRowHtml = `<tr><td><span class="poste-pill poste-irm">COURS</span></td>`;
      days.forEach(dIso => {
        const pres = STATE.presentations.filter(p => p.date === dIso);
        const meets = STATE.meetings.filter(m => m.date === dIso);
        let cell = "";
        pres.forEach(p => {
          if (p.type === "cours_internes") {
            if (p.pasDeCours) return;
            const shortChef = (p.chefIntervenant || "").replace(/^(Dr|Pr)\s+/i, "");
            cell += `<div style="font-size:9.5px; margin-bottom:2px; padding:2px 4px; border-radius:4px; background:#DBEAFE; cursor:pointer; line-height:1.15;" onclick="openPresentationModal('${p.id}')">
              <strong style="color:#1D4ED8">Cours :</strong> ${shortChef ? shortChef + " — " : ""}${p.coursChef || p.sujet || ""}
            </div>`;
            return;
          }
          const presBlock = inChefSpace ? (blocking.byDate[dIso] || []).find(iss => iss.category === "pres_absent" && iss.presId === p.id) : null;
          const bg = presBlock ? "#FEE2E2" : "#F3E8FF";
          const fg = presBlock ? "#991B1B" : "#6D28D9";
          const lbl = p.type === "cas_mardi" ? "Cas" : "Biblio";
          cell += `<div style="font-size:9.5px; margin-bottom:2px; padding:2px 4px; border-radius:4px; background:${bg}; cursor:pointer; line-height:1.15; ${presBlock ? 'border:1px solid #EF4444;' : ''}" onclick="openPresentationModal('${p.id}')">
            <strong style="color:${fg}">${lbl} :</strong> ${p.interneName} ${presBlock ? '<span style="color:#DC2626; font-weight:800;">(Absent)</span>' : ''}
          </div>`;
        });
        meets.forEach(m => {
          cell += `<div style="font-size:9.5px; margin-bottom:2px; padding:2px 4px; border-radius:4px; background:#DCFCE7; line-height:1.15;">
            <strong style="color:#15803D">${m.horaire} :</strong> ${m.title}
          </div>`;
        });
        staffRowHtml += `<td>${cell || '<span style="color:#CBD5E1">—</span>'}</td>`;
      });
      staffRowHtml += `</tr>`;

      let intGardeRowHtml = `<tr><td><span class="poste-pill poste-rg">GARDE INTERNE</span></td>`;
      days.forEach(dIso => {
        intGardeRowHtml += `<td>${renderInterneGardeCellHtml(dIso)}</td>`;
      });
      intGardeRowHtml += `</tr>`;

      let gardeRowHtml = `<tr><td><span class="poste-pill poste-rg">GARDE SENIOR</span></td>`;
      days.forEach(dIso => {
        const g = STATE.chefsGardes ? STATE.chefsGardes[dIso] : null;
        gardeRowHtml += `<td>${g && g.noms ? `<span class="garde-name" style="font-weight:700; color:#B91C1C;" title="Dr ${g.noms.join(", ")}"><span class="garde-dr">Dr </span>${g.noms.join(", ")}</span>` : '—'}</td>`;
      });
      gardeRowHtml += `</tr>`;

      return `
        <div class="card" style="padding:0; overflow:hidden;">
          <div class="week-table-wrap" style="border:none; border-radius:0;">
            <table class="planning-table week-5col">
              <thead>
                <tr>
                  <th class="col-poste">POSTE</th>
                  ${days.map(d => {
                    const dIss = inChefSpace ? (blocking.byDate[d] || []) : [];
                    return `<th style="${dIss.length ? 'background:#FEF2F2; color:#991B1B;' : ''}">
                      ${formatShortDayHeader(d)}
                    </th>`;
                  }).join("")}
                </tr>
              </thead>
              <tbody>
                <tr class="period-divider"><td colspan="6">MATIN — IRM 07h45 • TDM SAU 08h00 • Écho & Poste C 09h00</td></tr>
                ${renderPeriodRows(postesAm, "am")}
                <tr class="period-divider"><td colspan="6">COURS & RÉUNIONS (12h30)</td></tr>
                ${staffRowHtml}
                <tr class="period-divider"><td colspan="6">APRÈS-MIDI — TDM SAU fin 18h30</td></tr>
                ${renderPeriodRows(postesPm, "pm")}
                <tr class="period-divider"><td colspan="6">GARDES (LUN–VEN)</td></tr>
                ${intGardeRowHtml}
                ${gardeRowHtml}
              </tbody>
            </table>
          </div>
          ${renderWeekendGardesCompactBar(monIso)}
        </div>
      `;
    }

    function renderDayPlanningView(iso) {
      const dObj = STATE.schedule[iso];
      const gSenior = STATE.chefsGardes ? STATE.chefsGardes[iso] : null;
      const gInt = getInterneGardeInfo(iso);
      const gIntBadge = gInt
        ? (gInt.isRadioB && gInt.interneId
          ? `<span class="poste-pill poste-rg">🌙 Garde Interne : ${getInterneById(gInt.interneId).fullName}</span>`
          : `<span class="poste-pill poste-off">🌙 Garde Interne : ${gInt.rawLabel || "Radio A"}</span>`)
        : "";
      if (!dObj) {
        return `
          <div class="card">
            <div class="card-header">
              <div class="card-title">${formatDateFr(iso, true)} — Week-end / Garde</div>
              <div style="display:flex; gap:6px; flex-wrap:wrap;">
                ${gIntBadge}
                ${gSenior && gSenior.noms ? `<span class="poste-pill poste-rg">🚨 Garde Senior : Dr ${gSenior.noms.join(", ")}</span>` : ''}
              </div>
            </div>
            <div style="font-size:13px; color:var(--text-muted);">
              ${gSenior && gSenior.noms
                ? `Médecin senior de garde ce jour : <strong style="color:#B91C1C;">Dr ${gSenior.noms.join(", ")}</strong> (${gSenior.nature || "Garde Week-end"}).`
                : `Aucune vacation ordinaire programmée pour le ${formatDateFr(iso, true)}.`}
              ${gInt ? `<div style="margin-top:6px;">Interne de garde : <strong>${gInt.isRadioB && gInt.interneId ? getInterneById(gInt.interneId).fullName + " (Radio B — repos de garde le lendemain)" : (gInt.rawLabel + " (Radio A / Hors service)")}</strong>.</div>` : ""}
            </div>
          </div>
        `;
      }
      const chDay = (STATE.chefsPlanning && STATE.chefsPlanning[iso]) ? STATE.chefsPlanning[iso] : { am: [], pm: [] };
      const isSingleInterneSelected = !isChefId(selectedInterneId) && selectedInterneId !== "all" && selectedInterneId !== "all_chefs";

      let rows = "";
      STATE.internes.forEach(i => {
        if ((planningScope === "perso" || (isSingleInterneSelected && !isChefPlanningMode)) && isSingleInterneSelected && i.id !== selectedInterneId) return;
        const slot = (dObj.byInterne && dObj.byInterne[i.id]) ? dObj.byInterne[i.id] : null;
        if (!slot) return;
        const amEsc = String(slot.am || "").replace(/'/g, "\\'");
        const pmEsc = String(slot.pm || "").replace(/'/g, "\\'");
        const isSelAm = isChefPlanningMode && selectedForMove && selectedForMove.interneId === i.id && selectedForMove.dIso === iso && selectedForMove.periodKey === "am";
        const isSelPm = isChefPlanningMode && selectedForMove && selectedForMove.interneId === i.id && selectedForMove.dIso === iso && selectedForMove.periodKey === "pm";
        const isAmMand = isMandatoryVacationSlot(iso, "am", slot.am);
        const isPmMand = isMandatoryVacationSlot(iso, "pm", slot.pm);
        const isDJ = Boolean(i.isDJ || i.id === "oussama");
        const isOnGardeTonight = Boolean(gInt && gInt.interneId === i.id);

        const amDragAttrs = isChefPlanningMode
          ? `draggable="true" ondragstart="onInterneDragStart(event, '${iso}', 'am', '${i.id}', '${amEsc}')" ondragend="onInterneDragEnd(event)" ondragover="onCellDragOver(event, '${iso}', 'am')" ondrop="onBadgeDrop(event, '${iso}', 'am', '${i.id}', '${amEsc}')" onclick="onInterneBadgeClick(event, '${iso}', 'am', '${i.id}', '${amEsc}')"`
          : "";
        const pmDragAttrs = isChefPlanningMode
          ? `draggable="true" ondragstart="onInterneDragStart(event, '${iso}', 'pm', '${i.id}', '${pmEsc}')" ondragend="onInterneDragEnd(event)" ondragover="onCellDragOver(event, '${iso}', 'pm')" ondrop="onBadgeDrop(event, '${iso}', 'pm', '${i.id}', '${pmEsc}')" onclick="onInterneBadgeClick(event, '${iso}', 'pm', '${i.id}', '${pmEsc}')"`
          : "";

        rows += `
          <tr onclick="openVacationEditModal('${iso}', '${i.id}')" style="cursor:pointer;">
            <td>
              <div style="display:flex; align-items:center; gap:7px; font-weight:700; flex-wrap:wrap;">
                <span style="width:8px;height:8px;border-radius:50%;background:${i.color};display:inline-block;"></span>
                ${i.shortName}
                ${i.isSocle ? `<span class="tag-sm">Socle</span>` : ""}
                ${isDJ ? `<span class="tag-dj">DJ</span>` : ""}
                ${isOnGardeTonight ? `<span class="poste-pill poste-rg" style="font-size:9px; padding:1px 5px;">🌙 Garde ce soir</span>` : ""}
              </div>
            </td>
            <td class="${[isChefPlanningMode ? 'drop-zone-cell' : '', isAmMand ? 'cell-mandatory-vacation' : ''].filter(Boolean).join(' ')}" ${amDragAttrs} ${isAmMand ? 'title="Vacation obligatoire prioritaire"' : ''}>
              <span class="poste-pill ${getPosteClass(slot.am)} ${isAmMand ? 'poste-mandatory-slot' : ''} ${isChefPlanningMode ? 'draggable-interne' : ''} ${isSelAm ? 'selected-for-move' : ''}">
                ${isChefPlanningMode ? `<span class="drag-grip">⋮⋮</span>` : ""}
                ${isAmMand ? `<span class="mandatory-dot"></span>` : ""}
                ${getPosteWithTimeLabel(slot.am, "am")}
              </span>
            </td>
            <td class="${[isChefPlanningMode ? 'drop-zone-cell' : '', isPmMand ? 'cell-mandatory-vacation' : ''].filter(Boolean).join(' ')}" ${pmDragAttrs} ${isPmMand ? 'title="Vacation obligatoire prioritaire"' : ''}>
              <span class="poste-pill ${getPosteClass(slot.pm)} ${isPmMand ? 'poste-mandatory-slot' : ''} ${isChefPlanningMode ? 'draggable-interne' : ''} ${isSelPm ? 'selected-for-move' : ''}">
                ${isChefPlanningMode ? `<span class="drag-grip">⋮⋮</span>` : ""}
                ${isPmMand ? `<span class="mandatory-dot"></span>` : ""}
                ${getPosteWithTimeLabel(slot.pm, "pm")}
              </span>
            </td>
            <td style="color:var(--text-muted); font-size:12px;">${slot.note || (isOnGardeTonight ? "🌙 Garde ce soir (RG demain)" : "—")}</td>
          </tr>
        `;
      });

      return `
        <div class="card">
          <div class="card-header">
            <div class="card-title">${formatDateFr(iso, true)}${isSingleInterneSelected ? ` — ${getInterneById(selectedInterneId).fullName}` : ''}</div>
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              ${isSingleInterneSelected ? `<button class="btn btn-sm" onclick="selectInterne('all')">Voir tous les internes</button>` : ''}
              ${gIntBadge}
              ${gSenior && gSenior.noms ? `<span class="poste-pill poste-rg">Garde Senior : Dr ${gSenior.noms.join(", ")}</span>` : ''}
            </div>
          </div>
          <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px;">
            <div>
              <div style="font-size:12px; font-weight:800; margin-bottom:6px;">${isChefPlanningMode ? "Internes & DJ (glissez-déposez un créneau sur un autre interne pour échanger)" : (isSingleInterneSelected ? `Planning de ${getInterneById(selectedInterneId).shortName} (cliquez pour modifier)` : "Internes & DJ (cliquez pour modifier)")}</div>
              <div class="week-table-wrap">
                <table class="planning-table" style="min-width:280px;">
                  <thead>
                    <tr>
                      <th>Interne / DJ</th>
                      <th>Matin</th>
                      <th>Après-midi</th>
                      <th>Note</th>
                    </tr>
                  </thead>
                  <tbody>${rows}</tbody>
                </table>
              </div>
            </div>
            ${!isSingleInterneSelected ? `
            <div>
              <div style="font-size:12px; font-weight:800; margin-bottom:6px;">Chefs & Seniors</div>
              <div class="card" style="margin:0; background:#F8FAFC;">
                <div style="font-size:11px; font-weight:700; color:var(--text-muted); margin-bottom:4px;">MATIN (IRM 7h45 • TDM SAU 8h • Écho/Poste C 9h)</div>
                ${(chDay.am || []).map(x => {
                  const isCl = (x.doc === "FERMÉ" || x.doc === "MAINTENANCE" || x.closed);
                  return `<div style="font-size:12px; margin-bottom:3px;"><strong>${getPosteWithTimeLabel(x.poste, "am")}</strong> : ${isCl ? `<span class="poste-pill poste-closed">${x.doc}</span>` : `<span style="color:#0284C7; font-weight:700;">${x.doc}</span>`}</div>`;
                }).join("") || '—'}
                <div style="font-size:11px; font-weight:700; color:var(--text-muted); margin:10px 0 4px;">APRÈS-MIDI (TDM SAU fin 18h30)</div>
                ${(chDay.pm || []).map(x => {
                  const isCl = (x.doc === "FERMÉ" || x.doc === "MAINTENANCE" || x.closed);
                  return `<div style="font-size:12px; margin-bottom:3px;"><strong>${getPosteWithTimeLabel(x.poste, "pm")}</strong> : ${isCl ? `<span class="poste-pill poste-closed">${x.doc}</span>` : `<span style="color:#6D28D9; font-weight:700;">${x.doc}</span>`}</div>`;
                }).join("") || '—'}
              </div>
            </div>
            ` : ''}
          </div>
        </div>
      `;
    }

    function renderMonthPlanningView(iso) {
      if (isChefId(selectedInterneId)) {
        return renderSingleChefPersoView(getMondayOfWeek(iso), getChefById(selectedInterneId));
      }
      const ym = iso.slice(0, 7);
      const daysInMonth = Object.keys(STATE.schedule).filter(k => k.startsWith(ym)).sort();
      const targetId = (selectedInterneId === "all" || selectedInterneId === "all_chefs") ? "gabriel" : selectedInterneId;
      const targetInterne = getInterneById(targetId);

      let cells = "";
      daysInMonth.forEach(dIso => {
        const dObj = STATE.schedule[dIso];
        const slot = (dObj.byInterne && dObj.byInterne[targetId]) ? dObj.byInterne[targetId] : null;
        const isAmMand = slot ? isMandatoryVacationSlot(dIso, "am", slot.am) : false;
        const isPmMand = slot ? isMandatoryVacationSlot(dIso, "pm", slot.pm) : false;
        const gInt = getInterneGardeInfo(dIso);
        const isMeOnGarde = Boolean(gInt && gInt.interneId === targetId);
        cells += `
          <div class="month-cell ${dIso === currentDateIso ? 'today' : ''}" style="${isMeOnGarde ? 'background:#FEF2F2; border-color:#FCA5A5;' : ''}" onclick="setCurrentDate('${dIso}'); setPlanningMode('day');">
            <div style="display:flex; justify-content:space-between; align-items:center; font-weight:800; font-size:12px;">
              <span>${formatDateFr(dIso)}</span>
              ${isMeOnGarde ? `<span class="poste-pill poste-rg" style="font-size:9px; padding:1px 4px;">🌙 Garde</span>` : ""}
            </div>
            ${dObj.holiday ? `<span class="poste-pill poste-rg">Férié</span>` : (slot ? `
              <span class="poste-pill ${getPosteClass(slot.am)} ${isAmMand ? 'poste-mandatory-slot' : ''}" style="font-size:10.5px; padding:2px 6px;">${isAmMand ? '<span class="mandatory-dot"></span> ' : ''}M: ${getPosteWithTimeLabel(slot.am, "am")}</span>
              <span class="poste-pill ${getPosteClass(slot.pm)} ${isPmMand ? 'poste-mandatory-slot' : ''}" style="font-size:10.5px; padding:2px 6px;">${isPmMand ? '<span class="mandatory-dot"></span> ' : ''}PM: ${getPosteWithTimeLabel(slot.pm, "pm")}</span>
            ` : `—`)}
          </div>
        `;
      });

      return `
        <div class="card">
          <div class="card-header">
            <div class="card-title">Mois — ${targetInterne.fullName}</div>
          </div>
          <div class="month-grid">${cells}</div>
        </div>
      `;
    }

    function renderChefsPlanningView(monIso) {
      const days = [0, 1, 2, 3, 4].map(off => addDaysIso(monIso, off));
      const chefPostesAm = ["ECHO", "GESTES (C)", "TDM OLLIER 4 (SAU)", "TDM OLLIER 3", "TDM ACHARD 1", "IRM 3T", "IRM 1,5T", "CONSULTATION", "UCSA", "STAFF", "1/2 journée libre"];
      const chefPostesPm = ["GESTES (C)", "TDM OLLIER 4 (SAU)", "TDM OLLIER 3", "TDM ACHARD 1", "IRM", "ECHO", "ALLURA", "CONSULTATION", "UCSA", "STAFF", "1/2 journée libre"];

      const activeChef = isChefId(selectedInterneId) ? getChefById(selectedInterneId) : null;

      function renderChefRows(postesList, periodKey) {
        let rows = "";
        postesList.forEach(pName => {
          const hasAny = days.some(dIso => {
            const ch = STATE.chefsPlanning ? STATE.chefsPlanning[dIso] : null;
            return ch && ch[periodKey] && ch[periodKey].some(x => x.poste === pName);
          });
          if (!hasAny) return;
          rows += `<tr><td>${renderPosteCellLabel(pName, periodKey)}</td>`;
          days.forEach(dIso => {
            const ch = STATE.chefsPlanning ? STATE.chefsPlanning[dIso] : null;
            const matches = (ch && ch[periodKey]) ? ch[periodKey].filter(x => x.poste === pName) : [];
            if (!matches.length) {
              rows += `<td style="color:#CBD5E1">—</td>`;
            } else {
              const badges = matches.map(m => {
                if (m.doc === "FERMÉ" || m.doc === "MAINTENANCE" || m.closed) {
                  return `<span class="poste-pill poste-closed">${m.doc === "MAINTENANCE" ? "Maint." : "Fermé"}</span>`;
                }
                const isHighlighted = activeChef && doesDocMatchChef(m.doc, activeChef);
                return `<span class="interne-badge ${isHighlighted ? 'highlight-me' : ''}" onclick="selectChefByDocString('${m.doc.replace(/'/g, "\\'")}')">
                  <strong>${m.doc}</strong>
                </span>`;
              }).join(" ");
              rows += `<td>${badges}</td>`;
            }
          });
          rows += `</tr>`;
        });
        return rows;
      }

      let gardeRowHtml = `<tr><td><span class="poste-pill poste-rg">GARDE</span></td>`;
      days.forEach(dIso => {
        const g = STATE.chefsGardes ? STATE.chefsGardes[dIso] : null;
        gardeRowHtml += `<td>${g && g.noms ? `<span class="garde-name" style="font-weight:700; color:#B91C1C;" title="Dr ${g.noms.join(", ")}"><span class="garde-dr">Dr </span>${g.noms.join(", ")}</span>` : '—'}</td>`;
      });
      gardeRowHtml += `</tr>`;

      return `
        <div class="card" style="padding:0; overflow:hidden;">
          <div class="week-table-wrap" style="border:none; border-radius:0;">
            <table class="planning-table week-5col">
              <thead>
                <tr>
                  <th class="col-poste">POSTE</th>
                  ${days.map(d => `<th>${formatShortDayHeader(d)}</th>`).join("")}
                </tr>
              </thead>
              <tbody>
                <tr class="period-divider"><td colspan="6">MATIN — IRM 07h45 • TDM SAU 08h00 • Écho & Poste C 09h00</td></tr>
                ${renderChefRows(chefPostesAm, "am")}
                <tr class="period-divider"><td colspan="6">APRÈS-MIDI — TDM SAU fin 18h30</td></tr>
                ${renderChefRows(chefPostesPm, "pm")}
                <tr class="period-divider"><td colspan="6">GARDE SENIOR (LUN–VEN)</td></tr>
                ${gardeRowHtml}
              </tbody>
            </table>
          </div>
          ${renderWeekendGardesCompactBar(monIso)}
        </div>
      `;
    }

    function selectChefByDocString(docStr) {
      const found = (STATE.chefs || []).find(c => doesDocMatchChef(docStr, c));
      if (found) selectInterne(found.id);
    }

    function toggleStatsTable() {
      showStatsTable = !showStatsTable;
      renderAll();
    }

    function renderBalanceSummaryCard() {
      const isSingleInterneSelected = !isChefId(selectedInterneId) && selectedInterneId !== "all" && selectedInterneId !== "all_chefs";
      if (!showStatsTable) {
        return `
          <div style="text-align:center; margin-top:8px;">
            <button class="btn btn-sm" onclick="toggleStatsTable()">${isSingleInterneSelected ? `Afficher le décompte des postes (${getInterneById(selectedInterneId).shortName})` : 'Afficher le décompte des postes par interne'}</button>
          </div>
        `;
      }

      const monIso = getMondayOfWeek(currentDateIso);
      const weekStatsAll = computeWeekStatsByInterne(monIso);
      const statsAll = computeStatsByInterne();
      let rows = "";
      STATE.internes.forEach(i => {
        if (isSingleInterneSelected && !isChefPlanningMode && i.id !== selectedInterneId) return;
        const s = statsAll[i.id];
        const w = weekStatsAll[i.id] || { weekVac: 0, weekOff: 0, weekOffSlots: [], weekSau: 0, weekIrmPm: 0, sauTarget: (i.isSocle || i.id === "noe") ? 3 : 2 };
        const isDJ = Boolean(i.isDJ || i.id === "oussama");
        const offClass = w.weekOff > 2 ? "off-danger" : (w.weekOff < 2 ? "off-warn" : "off-ok");
        const sauTarget = w.sauTarget || ((i.isSocle || i.id === "noe") ? 3 : 2);
        const sauClass = w.weekSau > sauTarget ? "off-warn" : (w.weekSau === sauTarget ? "off-ok" : "vac-count");
        const irmPmClass = (w.weekIrmPm || 0) > 1 ? "off-warn" : ((w.weekIrmPm || 0) === 1 ? "off-ok" : "vac-count");
        rows += `
          <tr>
            <td style="font-weight:700;">
              <span style="width:7px;height:7px;border-radius:50%;background:${i.color};display:inline-block;margin-right:4px;"></span>
              ${i.shortName}
              ${i.isSocle ? `<span class="tag-sm">Socle</span>` : ""}
              ${isDJ ? `<span class="tag-dj">DJ</span>` : ""}
            </td>
            <td>
              <span class="offvac-pill ${offClass}">${w.weekOff}/2 Off</span>
              ${w.weekOffSlots.length ? `<div style="font-size:10px; color:#64748B; margin-top:2px;">${w.weekOffSlots.join(" • ")}</div>` : ""}
            </td>
            <td><span class="offvac-pill ${sauClass}">${w.weekSau}/${sauTarget} SAU</span></td>
            <td><span class="offvac-pill ${irmPmClass}">${w.weekIrmPm || 0}/1 IRM PM</span></td>
            <td><span class="offvac-pill vac-count">${w.weekVac} vac.</span></td>
            <td><strong>${s.activeHalfDays}</strong></td>
            <td><strong>${s.freeHalfDays}</strong> <span style="font-size:10px; color:var(--text-muted);">(${s.freeAmHalfDays || 0}M/${s.freePmHalfDays || 0}PM)</span></td>
            <td><strong>${s.byModality.TDM_SAU || 0}</strong></td>
            <td>${s.byModality.SCAN_ACHARD || 0}</td>
            <td>${s.byModality.TDM_OLLIER || 0}</td>
            <td>${s.byModality.IRM_AM || 0}</td>
            <td><strong>${s.byModality.IRM_PM || 0}</strong></td>
            <td>${s.byModality.ECHO}</td>
            <td>${s.byModality.RI_GESTES}</td>
            <td>${s.byModality.LECTURE_CS}</td>
            <td><strong>${s.gardesCount || 0}</strong>${s.gardesWeekendCount ? ` <span style="font-size:10px; color:var(--text-muted);">(${s.gardesWeekendCount} WE/Fér.)</span>` : ""}</td>
            <td>${Math.round((s.rgHalfDays || 0) / 2)} j.</td>
            <td>${Math.round(s.vacHalfDays / 2)} j.</td>
            <td>${s.casMardi} / ${s.biblioVendredi}${s.coursInternes ? ` / ${s.coursInternes}` : ""}</td>
          </tr>
        `;
      });

      return `
        <div class="card">
          <div class="card-header">
            <div class="card-title">Répartition des Offs, Scanners (SAU / Achard / Ollier), IRM (Matin / PM), Vacations & Gardes</div>
            <button class="btn btn-sm" onclick="toggleStatsTable()">Masquer</button>
          </div>
          <div class="week-table-wrap">
            <table class="planning-table">
              <thead>
                <tr>
                  <th>Interne / DJ</th>
                  <th>Offs (Sem.)</th>
                  <th>SAU (Sem.)</th>
                  <th>IRM PM (Sem.)</th>
                  <th>Vac. (Sem.)</th>
                  <th>Total Vac. (Semestre)</th>
                  <th>Total Demi-offs</th>
                  <th>Scan SAU</th>
                  <th>Scan Achard</th>
                  <th>Scan Ollier</th>
                  <th>IRM Mat.</th>
                  <th>IRM PM</th>
                  <th>Écho</th>
                  <th>Gestes</th>
                  <th>CS</th>
                  <th>Gardes</th>
                  <th>RG</th>
                  <th>Congés</th>
                  <th>Cas / Biblio / Cours</th>
                </tr>
              </thead>
              <tbody>${rows}</tbody>
            </table>
          </div>
        </div>
      `;
    }

    /* =========================================================================
     * ONGLET 2 : CONGÉS & RG
     * ========================================================================= */
    function setVacFilter(f) {
      vacFilter = f;
      renderTabContent();
    }

    function renderVacancesTab() {
      const absences = (STATE.absences || []).slice().sort((a, b) => a.date.localeCompare(b.date));
      const inChefSpace = (selectedInterneId === "all_chefs" || isChefId(selectedInterneId) || isChefPlanningMode);
      const byInterneFiltered = (selectedInterneId === "all" || inChefSpace)
        ? absences
        : absences.filter(a => a.interneId === selectedInterneId);

      const congesOnly = byInterneFiltered.filter(a => !String(a.type || "").toLowerCase().includes("garde"));
      const rgOnly = byInterneFiltered.filter(a => String(a.type || "").toLowerCase().includes("garde"));

      const gardesEntries = Object.keys(STATE.interneGardes || {})
        .sort()
        .map(d => Object.assign({ date: d }, STATE.interneGardes[d]))
        .filter(g => g.isRadioB && g.interneId && (selectedInterneId === "all" || inChefSpace || g.interneId === selectedInterneId));

      const filtered = vacFilter === "conges"
        ? congesOnly
        : (vacFilter === "rg" ? rgOnly : byInterneFiltered);

      const countByDate = {};
      absences.forEach(a => {
        if (a.status === "rejected") return;
        if (a.type !== "Repos de garde") {
          countByDate[a.date] = (countByDate[a.date] || 0) + 1;
        }
      });

      if (vacFilter === "gardes_cal") {
        let gRows = "";
        gardesEntries.forEach(g => {
          const iObj = getInterneById(g.interneId);
          const rgDate = g.rgDate || addDaysIso(g.date, 1);
          const rgWorking = Boolean(STATE.schedule && STATE.schedule[rgDate] && !STATE.schedule[rgDate].holiday);
          gRows += `
            <tr>
              <td style="font-weight:700;">${formatDateFr(g.date, true)}</td>
              <td>
                <span class="interne-badge" onclick="setCurrentDate('${g.date}'); switchTab('planning');">
                  <span style="width:7px;height:7px;border-radius:50%;background:${iObj.color};display:inline-block;"></span>
                  ${iObj.fullName}
                </span>
              </td>
              <td><span class="poste-pill ${g.isWeekendOrHoliday ? 'poste-rg' : 'poste-irm'}">${g.isWeekendOrHoliday ? 'Garde WE / Férié' : 'Garde Semaine'}</span></td>
              <td style="font-weight:700;">${formatDateFr(rgDate, true)}</td>
              <td>${rgWorking ? `<span class="poste-pill poste-rg">✓ RG posé sur le planning</span>` : `<span class="poste-pill poste-off">Week-end / Férié (hors vac.)</span>`}</td>
            </tr>
          `;
        });
        return `
          <div class="card">
            <div class="card-header">
              <div>
                <div class="card-title">Congés, Repos de garde & Planning des Gardes Internes (Hiver 2026–2027)</div>
                <div style="font-size:12px; color:var(--text-muted);">68 gardes Radio B sur le semestre • Repos de garde automatique le lendemain</div>
              </div>
              <div style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
                <div class="segmented">
                  <button class="seg-btn ${vacFilter === 'all' ? 'active' : ''}" onclick="setVacFilter('all')">Tous (${byInterneFiltered.length})</button>
                  <button class="seg-btn ${vacFilter === 'conges' ? 'active' : ''}" onclick="setVacFilter('conges')">Congés (${congesOnly.length})</button>
                  <button class="seg-btn ${vacFilter === 'rg' ? 'active' : ''}" onclick="setVacFilter('rg')">Repos de garde (${rgOnly.length})</button>
                  <button class="seg-btn ${vacFilter === 'gardes_cal' ? 'active' : ''}" onclick="setVacFilter('gardes_cal')">🌙 Gardes (${gardesEntries.length})</button>
                </div>
                <button class="btn btn-sm btn-primary" onclick="openAbsenceModal()">+ Poser un congé</button>
              </div>
            </div>
            <div class="week-table-wrap">
              <table class="planning-table">
                <thead>
                  <tr>
                    <th>Date de Garde</th>
                    <th>Interne / DJ (Radio B)</th>
                    <th>Nature</th>
                    <th>Lendemain (Repos de garde)</th>
                    <th>Impact Planning</th>
                  </tr>
                </thead>
                <tbody>${gRows || `<tr><td colspan="5" style="text-align:center; padding:18px;">Aucune garde enregistrée.</td></tr>`}</tbody>
              </table>
            </div>
          </div>
        `;
      }

      const colSpanCount = inChefSpace ? 7 : 6;
      let rowsHtml = "";
      if (filtered.length === 0) {
        rowsHtml = `<tr><td colspan="${colSpanCount}" style="text-align:center; padding:18px; color:var(--text-muted);">Aucun congé ou repos de garde enregistré dans ce filtre. Utilisez le bouton "+ Poser un congé".</td></tr>`;
      } else {
        filtered.forEach(a => {
          const iObj = getInterneById(a.interneId);
          const isRg = String(a.type || "").toLowerCase().includes("garde");
          const simCount = countByDate[a.date] || 1;
          const isOverLimit = !isRg && simCount > 2;
          const st = a.status || "pending";
          const statusHtml = st === "approved"
            ? `<span class="status-pill-approved">✓ Validé</span>`
            : (st === "rejected"
              ? `<span class="status-pill-rejected">✕ Refusé</span>`
              : `<span class="status-pill-pending">À valider</span>`);

          rowsHtml += `
            <tr style="${st === 'rejected' ? 'opacity:0.55; text-decoration:line-through;' : ''}">
              <td style="font-weight:700;">${formatDateFr(a.date, true)}</td>
              <td>${iObj.shortName}</td>
              <td><span class="poste-pill ${isRg ? 'poste-rg' : 'poste-vac'}">${a.type}</span></td>
              <td style="color:var(--text-muted);">${a.comment || "—"}</td>
              <td>
                ${isRg
                  ? `<span class="poste-pill poste-rg">Lendemain de garde</span>`
                  : (isOverLimit
                    ? `<span class="poste-pill poste-rg">${simCount} absents (max 2)</span>`
                    : `<span class="poste-pill poste-vac">Quota OK (${simCount}/2)</span>`)}
              </td>
              ${inChefSpace ? `<td>${statusHtml}</td>` : ""}
              <td>
                <div style="display:flex; gap:4px; flex-wrap:wrap;">
                  ${inChefSpace && st !== "approved" ? `<button class="btn-approve" onclick="setSingleAbsenceStatus('${a.id}', 'approved')">✓ Valider</button>` : ""}
                  ${inChefSpace && st !== "rejected" ? `<button class="btn-reject" onclick="setSingleAbsenceStatus('${a.id}', 'rejected')">✕ Refuser</button>` : ""}
                  <button class="btn btn-sm" onclick="deleteAbsence('${a.id}')" style="color:#64748B;">Suppr.</button>
                </div>
              </td>
            </tr>
          `;
        });
      }

      return `
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Congés & Repos de garde</div>
              <div style="font-size:12px; color:var(--text-muted);">Max 2 internes en congés simultanément • Repos de garde automatiques le lendemain des gardes (${rgOnly.length} j. ouvrés)</div>
            </div>
            <div style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;">
              <div class="segmented">
                <button class="seg-btn ${vacFilter === 'all' ? 'active' : ''}" onclick="setVacFilter('all')">Tous (${byInterneFiltered.length})</button>
                <button class="seg-btn ${vacFilter === 'conges' ? 'active' : ''}" onclick="setVacFilter('conges')">Congés (${congesOnly.length})</button>
                <button class="seg-btn ${vacFilter === 'rg' ? 'active' : ''}" onclick="setVacFilter('rg')">Repos de garde (${rgOnly.length})</button>
                <button class="seg-btn ${vacFilter === 'gardes_cal' ? 'active' : ''}" onclick="setVacFilter('gardes_cal')">🌙 Gardes (${gardesEntries.length})</button>
              </div>
              <button class="btn btn-sm btn-primary" onclick="openAbsenceModal()">+ Poser un congé</button>
            </div>
          </div>

          <div class="week-table-wrap">
            <table class="planning-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Interne</th>
                  <th>Type</th>
                  <th>Note</th>
                  <th>Quota / Motif</th>
                  ${inChefSpace ? `<th>Statut</th>` : ""}
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>${rowsHtml}</tbody>
            </table>
          </div>
        </div>
      `;
    }

    function previewAbsenceRuleWarning() {
      const warnEl = document.getElementById("absRuleWarning");
      if (!warnEl) return;
      const iid = document.getElementById("absInterneSelect") ? document.getElementById("absInterneSelect").value : "gabriel";
      const type = document.getElementById("absTypeSelect") ? document.getElementById("absTypeSelect").value : "CA 1";
      const startIso = document.getElementById("absStartDate") ? document.getElementById("absStartDate").value : "";
      const endIso = (document.getElementById("absEndDate") && document.getElementById("absEndDate").value) || startIso;
      if (!startIso || endIso < startIso) {
        warnEl.style.display = "none";
        return;
      }

      const warnings = [];
      let cur = startIso;
      let weekdays = 0;
      const tueFriDates = [];
      while (cur <= endIso) {
        const [yy, mm, dd] = cur.split("-").map(Number);
        const jsDay = new Date(yy, mm - 1, dd).getDay();
        if (jsDay >= 1 && jsDay <= 5) {
          weekdays++;
          if (jsDay === 2 || jsDay === 5) tueFriDates.push(formatDateFr(cur));
          const otherAbs = (STATE.absences || []).filter(a => a.date === cur && a.interneId !== iid && a.status !== "rejected");
          if (otherAbs.length >= 2) {
            warnings.push(`🚨 <strong>${formatDateFr(cur)}</strong> : déjà ${otherAbs.length} internes absents (${otherAbs.map(x => getInterneById(x.interneId).shortName).join(", ")}) — dépasse la limite de 2.`);
          }
          const baseSched = INITIAL_DATA.baseSchedule || INITIAL_DATA.schedule;
          const dOrig = baseSched[cur];
          if (dOrig && dOrig.byInterne && dOrig.byInterne[iid]) {
            const sl = dOrig.byInterne[iid];
            if (sl.am === "TDM SAU" || sl.pm === "TDM SAU") {
              warnings.push(`⚠️ <strong>${formatDateFr(cur)}</strong> : vous êtes prévu(e) sur <strong>TDM SAU</strong> (Urgences).`);
            }
          }
        }
        cur = addDaysIso(cur, 1);
      }
      if (weekdays > 0 && weekdays <= 2 && tueFriDates.length > 0 && type !== "Repos de garde") {
        warnings.push(`⚠️ Congé isolé un Mardi/Vendredi (${tueFriDates.join(", ")}).`);
      }

      if (warnings.length > 0) {
        warnEl.style.display = "block";
        warnEl.innerHTML = warnings.join("<br>");
      } else {
        warnEl.style.display = "none";
      }
    }

    function openAbsenceModal(defaultInterneId) {
      const sel = document.getElementById("absInterneSelect");
      const target = defaultInterneId || ((!isChefId(selectedInterneId) && selectedInterneId !== "all" && selectedInterneId !== "all_chefs") ? selectedInterneId : "gabriel");
      sel.innerHTML = STATE.internes.map(i => `<option value="${i.id}" ${i.id === target ? 'selected' : ''}>${i.fullName}</option>`).join("");
      document.getElementById("absStartDate").value = currentDateIso;
      document.getElementById("absEndDate").value = currentDateIso;
      document.getElementById("absComment").value = "";
      previewAbsenceRuleWarning();
      document.getElementById("modalAbsence").classList.add("open");
    }

    function saveAbsenceForm() {
      const iid = document.getElementById("absInterneSelect").value;
      const iObj = getInterneById(iid);
      const type = document.getElementById("absTypeSelect").value;
      const startIso = document.getElementById("absStartDate").value;
      const endIso = document.getElementById("absEndDate").value || startIso;
      const comment = document.getElementById("absComment").value.trim();

      if (!startIso || endIso < startIso) {
        alert("Vérifiez les dates.");
        return;
      }

      const initialStatus = isChefPlanningMode ? "approved" : "pending";

      let cur = startIso;
      const addedDates = [];
      while (cur <= endIso) {
        const id = `abs-${iid}-${cur}`;
        STATE.absences = (STATE.absences || []).filter(x => x.id !== id);
        STATE.absences.push({
          id,
          date: cur,
          interneId: iid,
          interneName: iObj.fullName,
          type,
          status: initialStatus,
          comment,
          createdAt: new Date().toISOString()
        });
        addedDates.push(cur);
        cur = addDaysIso(cur, 1);
      }

      saveStateLocal();
      closeModal("modalAbsence");
      renderAll();
      showToast(`Congé enregistré (${addedDates.length} j.)`);
      pushStateToCloud({ syncAbsenceSheet: true, addedDates, interneName: iObj.fullName, absType: type });
    }

    function deleteAbsence(absId) {
      const target = (STATE.absences || []).find(x => x.id === absId);
      STATE.absences = (STATE.absences || []).filter(x => x.id !== absId);
      saveStateLocal();
      renderAll();
      showToast("Congé supprimé");
      pushStateToCloud({ syncAbsenceSheet: true, deletedAbsence: target });
    }

    /* =========================================================================
     * ONGLET 3 : 3 PAGES SÉPARÉES (CAS DES INTERNES / BIBLIO / COURS DES INTERNES)
     * ========================================================================= */
    function getPresTypeMeta(p) {
      if (p.type === "cas_mardi") {
        return { modalLabel: "Cas des internes", typeLabel: "Cas des internes" };
      }
      if (p.type === "cours_internes") {
        return { modalLabel: "Cours des internes (Chef)", typeLabel: "Cours des internes" };
      }
      return { modalLabel: "Biblio", typeLabel: "Biblio" };
    }

    function renderPresentationsTab() {
      if (presFilter !== "cas_mardi" && presFilter !== "biblio_vendredi" && presFilter !== "cours_internes") {
        presFilter = "cas_mardi";
      }
      const list = (STATE.presentations || [])
        .filter(p => p.type === presFilter)
        .slice()
        .sort((a, b) => a.date.localeCompare(b.date));

      const pageTabsHtml = `
        <div class="main-tabs" style="grid-template-columns:repeat(3, 1fr); margin-bottom:10px;">
          <button class="tab-btn ${presFilter === 'cas_mardi' ? 'active' : ''}" onclick="setPresFilter('cas_mardi')">Cas des internes</button>
          <button class="tab-btn ${presFilter === 'biblio_vendredi' ? 'active' : ''}" onclick="setPresFilter('biblio_vendredi')">Biblio</button>
          <button class="tab-btn ${presFilter === 'cours_internes' ? 'active' : ''}" onclick="setPresFilter('cours_internes')">Cours des internes</button>
        </div>
      `;

      if (presFilter === "cours_internes") {
        let rowsHtml = "";
        list.forEach(p => {
          const isPasDeCours = Boolean(p.pasDeCours || p.coursChef === "Pas de cours" || p.sujet === "Pas de cours");
          const chefTxt = isPasDeCours ? "—" : (p.chefIntervenant || "—");
          const coursTxt = isPasDeCours
            ? `<span style="color:var(--text-muted);">Pas de cours</span>`
            : `<strong>${p.coursChef || p.sujet || "—"}</strong>`;

          rowsHtml += `
            <tr style="${isPasDeCours ? 'opacity:0.6;' : ''}">
              <td style="font-weight:700; white-space:nowrap;">${formatDateFr(p.date)}</td>
              <td style="font-weight:600; color:#0284C7; white-space:nowrap;">${chefTxt}</td>
              <td>${coursTxt}</td>
              <td style="width:1%; white-space:nowrap;">
                <button class="btn btn-sm" onclick="openPresentationModal('${p.id}')">Modifier</button>
              </td>
            </tr>
          `;
        });

        return `
          ${pageTabsHtml}
          <div class="card">
            <div class="card-header">
              <div class="card-title">Cours des internes (faits par les chefs)</div>
            </div>
            <div class="week-table-wrap">
              <table class="planning-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Chef</th>
                    <th>Cours</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>${rowsHtml}</tbody>
              </table>
            </div>
          </div>
        `;
      }

      const pageTitle = presFilter === "cas_mardi" ? "Cas des internes" : "Biblio";
      let rowsHtml = "";
      list.forEach(p => {
        const iObj = getInterneById(p.interneId);
        const isMe = (selectedInterneId !== "all" && !isChefId(selectedInterneId) && p.interneId === selectedInterneId);

        rowsHtml += `
          <tr style="${isMe ? 'background:#EFF6FF;' : ''}">
            <td style="font-weight:700; white-space:nowrap;">${formatDateFr(p.date)}</td>
            <td style="white-space:nowrap;">
              <span class="interne-badge ${isMe ? 'highlight-me' : ''}" onclick="openPresentationModal('${p.id}')">
                <span style="width:7px;height:7px;border-radius:50%;background:${iObj.color};display:inline-block;"></span>
                ${p.interneName || iObj.shortName}
              </span>
            </td>
            <td onclick="openPresentationModal('${p.id}')" style="cursor:pointer;">
              ${p.sujet
                ? `<strong>${p.sujet}</strong>`
                : `<span style="color:#94A3B8;">—</span>`}
            </td>
            <td style="width:1%; white-space:nowrap;">
              <button class="btn btn-sm" onclick="openPresentationModal('${p.id}')">Modifier</button>
            </td>
          </tr>
        `;
      });

      return `
        ${pageTabsHtml}
        <div class="card">
          <div class="card-header">
            <div class="card-title">${pageTitle}</div>
          </div>
          <div class="week-table-wrap">
            <table class="planning-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Interne</th>
                  <th>Sujet</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>${rowsHtml}</tbody>
            </table>
          </div>
        </div>
      `;
    }

    function setPresFilter(f) {
      presFilter = f;
      renderAll();
    }

    function openPresentationModal(presId) {
      const allList = (STATE.presentations || []).slice().sort((a, b) => a.date.localeCompare(b.date));
      const p = allList.find(x => x.id === presId) || allList[0];
      if (!p) return;

      const sameTypeList = allList.filter(x => x.type === p.type);
      const dateSel = document.getElementById("presDateSelect");
      dateSel.innerHTML = sameTypeList.map(item => {
        const who = item.type === "cours_internes" ? (item.chefIntervenant || "—") : (item.interneName || "");
        const lbl = `${formatDateFr(item.date)} — ${who}`;
        return `<option value="${item.id}" ${item.id === p.id ? 'selected' : ''}>${lbl}</option>`;
      }).join("");

      populatePresentationModalFields(p);
      document.getElementById("modalPresentation").classList.add("open");
    }

    function onPresDateChange(presId) {
      const p = (STATE.presentations || []).find(x => x.id === presId);
      if (p) populatePresentationModalFields(p);
    }

    function populatePresentationModalFields(p) {
      const meta = getPresTypeMeta(p);
      document.getElementById("presIdInput").value = p.id;
      document.getElementById("presModalTitle").textContent = `${meta.modalLabel} — ${formatDateFr(p.date)}`;

      const isCours = (p.type === "cours_internes");
      const intGroup = document.getElementById("presInterneGroup");
      const chefGroup = document.getElementById("presChefGroup");
      const sujetLabel = document.getElementById("presSujetLabel");

      if (intGroup) intGroup.style.display = isCours ? "none" : "block";
      if (chefGroup) chefGroup.style.display = isCours ? "block" : "none";
      if (sujetLabel) sujetLabel.textContent = isCours ? "Cours" : "Sujet";

      if (isCours) {
        document.getElementById("presChefInput").value = p.chefIntervenant || "";
        document.getElementById("presSujetInput").value = p.coursChef || p.sujet || "";
      } else {
        const sel = document.getElementById("presInterneSelect");
        sel.innerHTML = STATE.internes.map(i => `<option value="${i.id}" ${i.id === p.interneId ? 'selected' : ''}>${i.shortName}</option>`).join("");
        document.getElementById("presSujetInput").value = p.sujet || "";
      }
    }

    function savePresentationForm() {
      const pid = document.getElementById("presIdInput").value;
      const p = (STATE.presentations || []).find(x => x.id === pid);
      if (!p) return;

      const sujet = document.getElementById("presSujetInput").value.trim();

      if (p.type === "cours_internes") {
        const chefRaw = document.getElementById("presChefInput").value.trim();
        p.chefIntervenant = chefRaw;
        p.coursChef = sujet;
        p.sujet = sujet;
        p.pasDeCours = (sujet.toLowerCase() === "pas de cours");
        p.userEditedCours = true;
      } else {
        const iid = document.getElementById("presInterneSelect").value;
        const iObj = getInterneById(iid);
        p.interneId = iid;
        p.interneName = iObj.shortName;
        p.sujet = sujet;
        p.userEditedPres = true;
      }

      saveStateLocal();
      closeModal("modalPresentation");
      renderAll();
      showToast("Enregistré");
      pushStateToCloud({ syncStaffSheet: true });
    }

    /* =========================================================================
     * ONGLET 4 : RÉUNIONS (BONE CLUB & CRA / STAFFS MÉDICO-HEBDOMADAIRES)
     * ========================================================================= */
    function setReunionsFilter(f) {
      reunionsFilter = f;
      renderTabContent();
    }

    function renderReunionsTab() {
      const meets = (STATE.meetings || []).slice().sort((a, b) => a.date.localeCompare(b.date));
      const recurring = STATE.recurringStaffs || [];

      const pageTabsHtml = `
        <div class="main-tabs" style="grid-template-columns:repeat(2, 1fr); margin-bottom:10px;">
          <button class="tab-btn ${reunionsFilter === 'bone_cra' ? 'active' : ''}" onclick="setReunionsFilter('bone_cra')">Bone Club & CRA</button>
          <button class="tab-btn ${reunionsFilter === 'staffs_hebdo' ? 'active' : ''}" onclick="setReunionsFilter('staffs_hebdo')">Staffs médico-hebdomadaires</button>
        </div>
      `;

      if (reunionsFilter === "staffs_hebdo") {
        let staffRowsHtml = "";
        recurring.forEach(r => {
          (r.items || []).forEach((it, idx) => {
            const isAm = String(it.horaire || "").toLowerCase().includes("matin");
            staffRowsHtml += `
              <tr>
                <td style="font-weight:800; color:var(--primary); white-space:nowrap;">${idx === 0 ? r.day : ""}</td>
                <td style="white-space:nowrap;">
                  <span class="poste-pill ${isAm ? 'poste-irm' : 'poste-echo'}">${it.horaire}</span>
                </td>
                <td><strong>${it.title}</strong></td>
                <td style="font-weight:600; color:#334155; white-space:nowrap;">${it.referent || "—"}</td>
              </tr>
            `;
          });
        });

        return `
          ${pageTabsHtml}
          <div class="card">
            <div class="card-header">
              <div class="card-title">Staffs médico-hebdomadaires — Radiologie B</div>
            </div>
            <div class="week-table-wrap">
              <table class="planning-table">
                <thead>
                  <tr>
                    <th style="width:110px;">Jour</th>
                    <th style="width:120px;">Créneau</th>
                    <th>Staff médico-hebdomadaire</th>
                    <th style="width:200px;">Référent Radio B</th>
                  </tr>
                </thead>
                <tbody>${staffRowsHtml}</tbody>
              </table>
            </div>
          </div>
        `;
      }

      const boneClubList = meets.filter(m =>
        m.category === "Bone Club" || String(m.title || "").toLowerCase().includes("bone club")
      );
      const craList = meets.filter(m =>
        m.category === "CRA" ||
        String(m.title || "").toLowerCase().includes("cra") ||
        String(m.title || "").toLowerCase().includes("anapath") ||
        String(m.title || "").toLowerCase().includes("anatomo")
      );
      const otherList = meets.filter(m => !boneClubList.includes(m) && !craList.includes(m));

      const boneRowsHtml = boneClubList.map(m => `
        <tr>
          <td style="font-weight:700; white-space:nowrap;">${formatDateFr(m.date, true)}</td>
          <td style="white-space:nowrap;"><span class="poste-pill poste-irm">${m.horaire}</span></td>
          <td><strong>${m.title}</strong></td>
          <td style="color:#475569; font-size:12px;">${m.sender || "Pr J-L. Drapé & Pr A. Feydy"}</td>
          <td style="color:var(--text-muted); font-size:12px; white-space:nowrap;">${m.location || "Amphithéâtre Luton"}</td>
        </tr>
      `).join("");

      const craRowsHtml = craList.map(m => `
        <tr>
          <td style="font-weight:700; white-space:nowrap;">${formatDateFr(m.date, true)}</td>
          <td style="white-space:nowrap;"><span class="poste-pill poste-gestes">${m.horaire}</span></td>
          <td><strong>${m.title}</strong></td>
          <td style="color:#475569; font-size:12px;">${m.sender || "Radio B & Anapath"}</td>
          <td style="color:var(--text-muted); font-size:12px; white-space:nowrap;">${m.location || "Salle Staff Albarran -1"}</td>
        </tr>
      `).join("");

      const otherCardHtml = otherList.length ? `
        <div class="card">
          <div class="card-header">
            <div class="card-title">Autres réunions</div>
          </div>
          <div class="week-table-wrap">
            <table class="planning-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Horaire</th>
                  <th>Réunion</th>
                  <th>Intervenants</th>
                  <th>Lieu</th>
                </tr>
              </thead>
              <tbody>
                ${otherList.map(m => `
                  <tr>
                    <td style="font-weight:700; white-space:nowrap;">${formatDateFr(m.date, true)}</td>
                    <td style="white-space:nowrap;"><span class="poste-pill poste-echo">${m.horaire}</span></td>
                    <td><strong>${m.title}</strong></td>
                    <td style="color:#475569; font-size:12px;">${m.sender || "—"}</td>
                    <td style="color:var(--text-muted); font-size:12px;">${m.location || "—"}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
      ` : "";

      return `
        ${pageTabsHtml}
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Bone Club Cochin</div>
              <div style="font-size:11.5px; color:var(--text-muted);">Mercredi 18h00 – 20h00 • Amphithéâtre Luton (RDC UFR Médecine Site Cochin)</div>
            </div>
            <button class="btn btn-sm btn-primary" onclick="openMeetingModal('Bone Club')">+ Réunion</button>
          </div>
          <div class="week-table-wrap">
            <table class="planning-table">
              <thead>
                <tr>
                  <th style="width:130px;">Date</th>
                  <th style="width:125px;">Horaire</th>
                  <th>Session</th>
                  <th>Modération</th>
                  <th style="width:180px;">Lieu</th>
                </tr>
              </thead>
              <tbody>${boneRowsHtml}</tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">CRA — Confrontations Radio-Anatomo-Pathologiques</div>
              <div style="font-size:11.5px; color:var(--text-muted);">Vendredi 14h00 / 14h15 – 16h00 • Salle de Staff Radio B (Pavillon Albarran -1)</div>
            </div>
            <button class="btn btn-sm" onclick="openMeetingModal('CRA')">+ CRA</button>
          </div>
          <div class="week-table-wrap">
            <table class="planning-table">
              <thead>
                <tr>
                  <th style="width:130px;">Date</th>
                  <th style="width:125px;">Horaire</th>
                  <th>Session</th>
                  <th>Intervenants</th>
                  <th style="width:180px;">Lieu</th>
                </tr>
              </thead>
              <tbody>${craRowsHtml}</tbody>
            </table>
          </div>
        </div>
        ${otherCardHtml}
      `;
    }

    function onMeetCategoryChange(cat) {
      if (cat === "Bone Club") {
        document.getElementById("meetHoraire").value = "18h00 – 20h00";
        document.getElementById("meetSender").value = "Pr J-L. Drapé & Pr A. Feydy";
        document.getElementById("meetLocation").value = "Amphithéâtre Luton (Cochin)";
      } else if (cat === "CRA") {
        document.getElementById("meetHoraire").value = "14h15 – 16h00";
        document.getElementById("meetSender").value = "Radio B & Anapath";
        document.getElementById("meetLocation").value = "Salle de Staff Radio B (Albarran -1)";
      } else {
        document.getElementById("meetHoraire").value = "17h00 – 18h00";
        document.getElementById("meetSender").value = "Service de Radiologie B";
        document.getElementById("meetLocation").value = "Salle de Staff Radio B (Albarran -1)";
      }
    }

    function openMeetingModal(defaultCat) {
      const cat = defaultCat || "Bone Club";
      const catEl = document.getElementById("meetCategory");
      if (catEl) catEl.value = cat;
      document.getElementById("meetDate").value = currentDateIso;
      document.getElementById("meetTitle").value = "";
      document.getElementById("meetDesc").value = "";
      onMeetCategoryChange(cat);
      document.getElementById("modalMeeting").classList.add("open");
    }

    function saveMeetingForm() {
      const category = document.getElementById("meetCategory") ? document.getElementById("meetCategory").value : "Bone Club";
      const date = document.getElementById("meetDate").value;
      const horaire = document.getElementById("meetHoraire").value.trim() || "18h00 – 20h00";
      const title = document.getElementById("meetTitle").value.trim();
      const sender = document.getElementById("meetSender").value.trim() || "Service de Radiologie B";
      const location = document.getElementById("meetLocation").value.trim() || "Salle de Staff Radio B";
      const description = document.getElementById("meetDesc").value.trim();

      if (!date || !title) {
        alert("Indiquez la date et le titre.");
        return;
      }

      STATE.meetings.push({
        id: "reunion-" + Date.now(),
        date,
        horaire,
        title,
        category,
        sender,
        location,
        description,
        mandatory: true
      });

      saveStateLocal();
      closeModal("modalMeeting");
      renderAll();
      showToast("Réunion ajoutée");
      pushStateToCloud({});
    }

    /* =========================================================================
     * ONGLET 5 : ANNUAIRE COCHIN
     * ========================================================================= */
    function renderAnnuaireTab() {
      const list = (STATE.phoneDirectory || []).slice();
      const q = (annuaireSearch || "").toLowerCase().trim();
      const categories = [
        "Radiologie B — Secrétariats & Consoles",
        "Radiologie B — Équipe Médicale (Chefs & Seniors)",
        "Services Partenaires (Ortho, Rhumato, Anesth, Anapath)",
        "Laboratoires, Pharmacie & Administration (DAM)"
      ];

      const filtered = list.filter(c => {
        if (annuaireCategory !== "all" && c.category !== annuaireCategory) return false;
        if (!q) return true;
        const blob = `${c.name || ""} ${c.role || ""} ${c.poste || ""} ${c.phone || ""} ${c.building || ""} ${c.category || ""}`.toLowerCase();
        return blob.includes(q);
      });

      let groupsHtml = "";
      categories.forEach(cat => {
        const items = filtered.filter(x => x.category === cat);
        if (items.length === 0) return;

        let rows = items.map(c => {
          const telHref = (c.phone || "").replace(/[^0-9+]/g, "");
          return `
            <tr>
              <td>
                <div style="font-weight:700; color:#0F172A;">${c.name}</div>
                <div style="font-size:11px; color:var(--text-muted);">${c.role || ""}</div>
              </td>
              <td><span class="poste-pill poste-irm">${c.poste || "—"}</span></td>
              <td>
                ${c.phone
                  ? `<a href="tel:${telHref}" class="poste-pill poste-echo" style="text-decoration:none;">${c.phone}</a>`
                  : "—"}
              </td>
              <td style="font-size:12px; color:#475569;">${c.building || "Cochin"}</td>
            </tr>
          `;
        }).join("");

        groupsHtml += `
          <div class="card" style="margin-bottom:10px;">
            <div class="card-header">
              <div class="card-title">${cat}</div>
            </div>
            <div class="week-table-wrap">
              <table class="planning-table" style="min-width:480px;">
                <thead>
                  <tr>
                    <th>Contact</th>
                    <th style="width:130px;">Poste / DECT</th>
                    <th style="width:150px;">Ligne directe</th>
                    <th style="width:150px;">Lieu</th>
                  </tr>
                </thead>
                <tbody>${rows}</tbody>
              </table>
            </div>
          </div>
        `;
      });

      if (!groupsHtml) {
        groupsHtml = `<div class="card" style="text-align:center; color:var(--text-muted); padding:20px;">Aucun numéro trouvé.</div>`;
      }

      return `
        <div class="card">
          <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
            <input
              type="text"
              class="form-control"
              style="flex:1; min-width:200px;"
              placeholder="Rechercher un nom, poste (ex: 12483), console, service..."
              value="${annuaireSearch.replace(/"/g, '&quot;')}"
              oninput="onAnnuaireSearch(this.value)"
            />
            <div class="segmented" style="flex-wrap:wrap;">
              <button class="seg-btn ${annuaireCategory === 'all' ? 'active' : ''}" onclick="setAnnuaireCategory('all')">Tous</button>
              <button class="seg-btn ${annuaireCategory === 'Radiologie B — Secrétariats & Consoles' ? 'active' : ''}" onclick="setAnnuaireCategory('Radiologie B — Secrétariats & Consoles')">Consoles</button>
              <button class="seg-btn ${annuaireCategory === 'Radiologie B — Équipe Médicale (Chefs & Seniors)' ? 'active' : ''}" onclick="setAnnuaireCategory('Radiologie B — Équipe Médicale (Chefs & Seniors)')">Médecins</button>
              <button class="seg-btn ${annuaireCategory === 'Services Partenaires (Ortho, Rhumato, Anesth, Anapath)' ? 'active' : ''}" onclick="setAnnuaireCategory('Services Partenaires (Ortho, Rhumato, Anesth, Anapath)')">Services</button>
            </div>
            <button class="btn btn-sm btn-primary" onclick="openPhoneContactModal()">+ Numéro</button>
          </div>
        </div>
        ${groupsHtml}
      `;
    }

    function onAnnuaireSearch(val) {
      annuaireSearch = val;
      renderTabContent();
      const inputs = document.querySelectorAll('input[oninput*="onAnnuaireSearch"]');
      if (inputs.length) {
        const inp = inputs[0];
        inp.focus();
        inp.setSelectionRange(inp.value.length, inp.value.length);
      }
    }

    function setAnnuaireCategory(cat) {
      annuaireCategory = cat;
      renderTabContent();
    }

    function openPhoneContactModal() {
      document.getElementById("phoneNameInput").value = "";
      document.getElementById("phoneRoleInput").value = "";
      document.getElementById("phonePosteInput").value = "";
      document.getElementById("phoneNumInput").value = "01 58 41 ";
      document.getElementById("phoneBldgInput").value = "Bâtiment Ollier";
      document.getElementById("phoneFaxInput").value = "";
      document.getElementById("modalPhoneContact").classList.add("open");
    }

    function savePhoneContactForm() {
      const category = document.getElementById("phoneCatInput").value;
      const name = document.getElementById("phoneNameInput").value.trim();
      const role = document.getElementById("phoneRoleInput").value.trim();
      const poste = document.getElementById("phonePosteInput").value.trim();
      const phone = document.getElementById("phoneNumInput").value.trim();
      const building = document.getElementById("phoneBldgInput").value.trim() || "Hôpital Cochin";
      const fax = document.getElementById("phoneFaxInput").value.trim();

      if (!name || (!poste && !phone)) {
        alert("Indiquez le nom et le numéro.");
        return;
      }

      if (!STATE.phoneDirectory) STATE.phoneDirectory = [];
      STATE.phoneDirectory.unshift({
        id: "tel-custom-" + Date.now(),
        category,
        name,
        role,
        poste,
        phone,
        fax,
        building
      });

      saveStateLocal();
      closeModal("modalPhoneContact");
      renderAll();
      showToast("Numéro ajouté");
      pushStateToCloud({});
    }

    /* =========================================================================
     * MODIFICATION D'UNE VACATION D'INTERNE
     * ========================================================================= */
    function openVacationEditModal(iso, iid) {
      const targetIso = STATE.schedule[iso] ? iso : "2026-11-02";
      const targetIid = getInterneById(iid).id;
      const monIso = getMondayOfWeek(targetIso);

      if (isWeekLocked(monIso) && !isChefPlanningMode) {
        showToast("🔒 Ce planning hebdomadaire est validé et fixé par le Chef. Déverrouillez avec le code Chef pour modifier.");
        requireChefUnlockThen(() => openVacationEditModal(targetIso, targetIid));
        return;
      }

      document.getElementById("vacEditDate").value = targetIso;
      const intSelect = document.getElementById("vacEditInterneId");
      intSelect.innerHTML = STATE.internes.map(i => `<option value="${i.id}" ${i.id === targetIid ? 'selected' : ''}>${i.fullName}</option>`).join("");

      refreshVacationModalFields();
      document.getElementById("modalVacationEdit").classList.add("open");
    }

    function refreshVacationModalFields() {
      const iso = document.getElementById("vacEditDate").value;
      const iid = document.getElementById("vacEditInterneId").value;
      const iObj = getInterneById(iid);
      const dObj = STATE.schedule[iso];
      const slot = (dObj && dObj.byInterne && dObj.byInterne[iid]) ? dObj.byInterne[iid] : { am: "TDM SAU", pm: "TDM SAU", note: "" };

      document.getElementById("vacEditHeader").value = `${iObj.fullName} — ${formatDateFr(iso, true)}`;
      const options = STATE.postesMeta.map(p => p.code);
      document.getElementById("vacEditAm").innerHTML = options.map(c => `<option value="${c}" ${c === slot.am ? 'selected' : ''}>${c}</option>`).join("");
      document.getElementById("vacEditPm").innerHTML = options.map(c => `<option value="${c}" ${c === slot.pm ? 'selected' : ''}>${c}</option>`).join("");
      document.getElementById("vacEditNote").value = slot.note || "";
      refreshVacationModalSummary();
    }

    function refreshVacationModalSummary() {
      const box = document.getElementById("vacEditLiveSummary");
      if (!box) return;
      const iso = document.getElementById("vacEditDate").value;
      const iid = document.getElementById("vacEditInterneId").value;
      const am = document.getElementById("vacEditAm").value;
      const pm = document.getElementById("vacEditPm").value;
      if (!iso || !iid) {
        box.style.display = "none";
        return;
      }
      const iObj = getInterneById(iid);
      const monIso = getMondayOfWeek(iso);
      const friIso = addDaysIso(monIso, 4);
      const overrideSlot = { iso, iid, am, pm };
      const weekStats = computeWeekStatsByInterne(monIso, overrideSlot);
      const semStats = computeStatsByInterne(overrideSlot);
      const w = weekStats[iid] || { weekVac: 0, weekOff: 0, weekOffSlots: [], weekCongesHalf: 0, weekRgHalf: 0, weekSau: 0, sauTarget: (iObj.isSocle || iid === "noe") ? 3 : 2 };
      const s = semStats[iid] || { activeHalfDays: 0, freeHalfDays: 0, vacHalfDays: 0, rgHalfDays: 0, byModality: {} };

      const [yy, mm, dd] = iso.split("-").map(Number);
      const jsDay = new Date(yy, mm - 1, dd).getDay();
      const nonActList = ["1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"];
      const samePosteAllDay = Boolean(am && pm && !nonActList.includes(am) && !nonActList.includes(pm) && am === pm);
      const forbiddenPmOff = (jsDay === 2 || jsDay === 5) && pm === "1/2 journée libre";
      const overOffQuota = w.weekOff > 2;
      const offPillClass = overOffQuota ? "off-danger" : (w.weekOff < 2 ? "off-warn" : "off-ok");
      const sauTarget = w.sauTarget || ((iObj.isSocle || iid === "noe") ? 3 : 2);
      const sauPillClass = w.weekSau > sauTarget ? "off-warn" : (w.weekSau === sauTarget ? "off-ok" : "vac-count");
      const irmPmPillClass = (w.weekIrmPm || 0) > 1 ? "off-warn" : ((w.weekIrmPm || 0) === 1 ? "off-ok" : "vac-count");

      const otherChips = STATE.internes.map(other => {
        const ow = weekStats[other.id] || { weekVac: 0, weekOff: 0, weekSau: 0, weekIrmPm: 0, sauTarget: (other.isSocle || other.id === "noe") ? 3 : 2 };
        const os = semStats[other.id] || { activeHalfDays: 0, freeHalfDays: 0 };
        const isCur = other.id === iid;
        const oSauTarget = ow.sauTarget || ((other.isSocle || other.id === "noe") ? 3 : 2);
        return `<span onclick="document.getElementById('vacEditInterneId').value='${other.id}'; refreshVacationModalFields();" style="display:inline-flex; align-items:center; gap:3px; padding:2px 6px; border-radius:6px; font-size:10.5px; cursor:pointer; border:1px solid ${isCur ? '#0284C7' : '#CBD5E1'}; background:${isCur ? '#E0F2FE' : '#FFFFFF'}; font-weight:${isCur ? '800' : '600'};" title="Semestre : ${os.activeHalfDays} vac • ${os.freeHalfDays} off">
          <span style="width:6px;height:6px;border-radius:50%;background:${other.color};display:inline-block;"></span>
          ${other.shortName}: <strong>${ow.weekOff}/2 off</strong> • <strong>${ow.weekSau}/${oSauTarget} SAU</strong> • <strong>${ow.weekIrmPm || 0}/1 IRM PM</strong> • ${ow.weekVac}v
        </span>`;
      }).join(" ");

      box.style.display = "block";
      box.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; gap:6px; flex-wrap:wrap; margin-bottom:4px;">
          <strong style="color:#0F172A; font-size:12px;">📊 Bilan ${iObj.shortName} (${formatShortDayHeader(monIso)}–${formatShortDayHeader(friIso)})</strong>
          <div style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
            <span class="offvac-pill ${offPillClass}">${w.weekOff}/2 Off</span>
            <span class="offvac-pill ${sauPillClass}">${w.weekSau}/${sauTarget} SAU</span>
            <span class="offvac-pill ${irmPmPillClass}">${w.weekIrmPm || 0}/1 IRM PM</span>
            <span class="offvac-pill vac-count">${w.weekVac} Vac. sem.</span>
            ${w.weekCongesHalf > 0 ? `<span class="offvac-pill conges-count">${w.weekCongesHalf / 2}j Cong.</span>` : ""}
            ${w.weekRgHalf > 0 ? `<span class="offvac-pill off-danger">${w.weekRgHalf / 2}j RG</span>` : ""}
          </div>
        </div>
        <div style="font-size:11px; color:#334155; margin-bottom:3px;">
          <strong>Créneaux Off cette semaine :</strong> ${w.weekOffSlots.length ? w.weekOffSlots.join(" • ") : "Aucun demi-off"}
        </div>
        <div style="font-size:11px; color:#475569; margin-bottom:6px;">
          <strong>Cumul Semestre :</strong> <strong>${s.activeHalfDays}</strong> vac. (SAU: <strong>${(s.byModality && s.byModality.TDM_SAU) || 0}</strong> • Achard: <strong>${(s.byModality && s.byModality.SCAN_ACHARD) || 0}</strong> • Ollier: <strong>${(s.byModality && s.byModality.TDM_OLLIER) || 0}</strong> • IRM Mat: <strong>${(s.byModality && s.byModality.IRM_AM) || 0}</strong> • IRM PM: <strong>${(s.byModality && s.byModality.IRM_PM) || 0}</strong>) • <strong>${s.freeHalfDays}</strong> demi-offs
        </div>
        ${samePosteAllDay ? `<div style="font-size:11px; color:#B91C1C; font-weight:800; margin-bottom:5px;">⛔ Règle du service : un interne ne peut pas faire le même poste toute la journée (${am} matin et après-midi).</div>` : ""}
        ${forbiddenPmOff ? `<div style="font-size:11px; color:#B91C1C; font-weight:800; margin-bottom:5px;">⛔ Règle du service : pas de demi-off le mardi après-midi ni le vendredi après-midi.</div>` : ""}
        ${overOffQuota ? `<div style="font-size:11px; color:#B91C1C; font-weight:800; margin-bottom:5px;">⚠️ Attention : ${w.weekOff} demi-offs sur cette semaine (max 2 autorisés).</div>` : ""}
        ${(w.weekIrmPm || 0) > 1 ? `<div style="font-size:11px; color:#B45309; font-weight:800; margin-bottom:5px;">⚠️ Quota IRM d'après-midi dépassé : ${w.weekIrmPm}/1 IRM PM cette semaine (acceptable uniquement à titre exceptionnel).</div>` : ""}
        ${w.weekSau > sauTarget ? `<div style="font-size:11px; color:#B45309; font-weight:800; margin-bottom:5px;">⚠️ Quota SAU dépassé : ${w.weekSau}/${sauTarget} TDM SAU cette semaine (acceptable uniquement à titre exceptionnel).</div>` : ""}
        <div style="border-top:1px dashed #CBD5E1; padding-top:5px; margin-top:4px;">
          <div style="font-size:10px; font-weight:700; color:#64748B; margin-bottom:3px;">COMPARATIF DES 6 INTERNES (SEMAINE & SEMESTRE) :</div>
          <div style="display:flex; flex-wrap:wrap; gap:4px;">${otherChips}</div>
        </div>
      `;
    }

    function saveSingleVacation() {
      const iso = document.getElementById("vacEditDate").value;
      const iid = document.getElementById("vacEditInterneId").value;
      const am = document.getElementById("vacEditAm").value;
      const pm = document.getElementById("vacEditPm").value;
      const note = document.getElementById("vacEditNote").value.trim();

      const monIso = getMondayOfWeek(iso);
      if (isWeekLocked(monIso) && !isChefPlanningMode) {
        alert("Ce planning hebdomadaire a été validé et fixé par le Chef. Déverrouillez l'Espace Chef pour le modifier.");
        return;
      }

      // Vérification stricte : un interne ne peut pas faire le même poste toute la journée (Matin == Après-midi)
      const nonActSave = ["1/2 journée libre", "RG", "VACANCES", "FÉRIÉ", "FORMATION / ACCUEIL"];
      if (am && pm && !nonActSave.includes(am) && !nonActSave.includes(pm) && am === pm) {
        alert(`Règle du service : un interne ne peut pas faire le même poste toute la journée (${am} matin et après-midi).`);
        return;
      }

      // Vérification stricte : pas de demi-off le mardi après-midi ni le vendredi après-midi
      const [yyV, mmV, ddV] = iso.split("-").map(Number);
      const jsDayV = new Date(yyV, mmV - 1, ddV).getDay();
      if ((jsDayV === 2 || jsDayV === 5) && pm === "1/2 journée libre") {
        alert("Règle du service : pas de demi-off le mardi après-midi ni le vendredi après-midi pour les internes.");
        return;
      }

      // Vérification stricte : maximum 2 demi-offs ('1/2 journée libre') par semaine par interne + max 1 IRM PM / semaine (sauf exception)
      let weekDemiOffs = 0;
      let weekIrmPmCnt = 0;
      for (let d = 0; d < 5; d++) {
        const curIso = addDaysIso(monIso, d);
        if (curIso === iso) {
          if (am === "1/2 journée libre") weekDemiOffs++;
          if (pm === "1/2 journée libre") weekDemiOffs++;
          if (pm === "IRM") weekIrmPmCnt++;
        } else {
          const dayObj = STATE.schedule[curIso];
          if (dayObj && !dayObj.holiday && dayObj.byInterne && dayObj.byInterne[iid]) {
            if (dayObj.byInterne[iid].am === "1/2 journée libre") weekDemiOffs++;
            if (dayObj.byInterne[iid].pm === "1/2 journée libre") weekDemiOffs++;
            if (dayObj.byInterne[iid].pm === "IRM") weekIrmPmCnt++;
          }
        }
      }
      if (weekDemiOffs > 2) {
        alert(`Règle du service : 2 demi-offs par semaine maximum par interne (${weekDemiOffs} demi-offs sur cette semaine).`);
        return;
      }
      if (weekIrmPmCnt > 1 && pm === "IRM") {
        const okIrm = confirm(`Règle du service : un interne ne peut pas avoir plus d'une IRM d'après-midi par semaine (${weekIrmPmCnt} IRM PM sur cette semaine). Confirmer cette affectation à titre exceptionnel ?`);
        if (!okIrm) return;
      }

      if (!STATE.customVacations) STATE.customVacations = {};
      const seniorListVac = ["gabriel", "marwane", "milan", "nathanael", "oussama"];
      const daySlotsVac = (STATE.schedule[iso] && STATE.schedule[iso].byInterne) || {};
      const prevSlot = daySlotsVac[iid] || {};
      const prevAm = prevSlot.am || "";
      const prevPm = prevSlot.pm || "";
      if (seniorListVac.includes(iid) && daySlotsVac[iid]) {
        [["am", am], ["pm", pm]].forEach(([pKey, newVal]) => {
          if (daySlotsVac[iid][pKey] === "TDM SAU" && newVal !== "TDM SAU") {
            const otherSau = seniorListVac.filter(sId => sId !== iid && daySlotsVac[sId] && daySlotsVac[sId][pKey] === "TDM SAU");
            if (otherSau.length === 0) {
              const swapCand = seniorListVac.find(sId => sId !== iid && daySlotsVac[sId] && daySlotsVac[sId][pKey] === newVal);
              if (swapCand) {
                applyInterneSlotChange(iso, pKey, swapCand, "TDM SAU");
              }
            }
          }
        });
      }
      const nowIso = isChefPlanningMode ? markChefValidationStamp() : new Date().toISOString();
      const cKey = iso + "__" + iid;
      STATE.customVacations[cKey] = {
        am,
        pm,
        note,
        prevAm,
        prevPm,
        status: isChefPlanningMode ? "approved" : "pending",
        validatedBy: isChefPlanningMode ? "Chef" : undefined,
        validatedAt: isChefPlanningMode ? nowIso : undefined,
        updatedAt: nowIso
      };
      if (Array.isArray(STATE.deletedCustomKeys)) {
        STATE.deletedCustomKeys = STATE.deletedCustomKeys.filter(k => k !== cKey);
      }

      saveStateLocal();
      closeModal("modalVacationEdit");
      renderAll();
      showToast(isChefPlanningMode ? "✓ Poste validé par le Chef" : "Poste mis à jour (en attente de validation)");
      pushStateToCloud({ isChefValidation: Boolean(isChefPlanningMode) });
    }

    function resetSingleVacation() {
      const iso = document.getElementById("vacEditDate").value;
      const iid = document.getElementById("vacEditInterneId").value;
      const monIso = getMondayOfWeek(iso);
      if (isWeekLocked(monIso) && !isChefPlanningMode) {
        alert("Ce planning hebdomadaire a été validé et fixé par le Chef. Déverrouillez l'Espace Chef pour le réinitialiser.");
        return;
      }
      const cKey = iso + "__" + iid;
      const resetIso = isChefPlanningMode ? markChefValidationStamp() : new Date().toISOString();
      if (STATE.customVacations) delete STATE.customVacations[cKey];
      tombstoneCustomKey(cKey, resetIso);
      saveStateLocal();
      closeModal("modalVacationEdit");
      renderAll();
      showToast("Poste réinitialisé");
      pushStateToCloud({ isChefValidation: Boolean(isChefPlanningMode) });
    }

    function closeModal(id) {
      document.getElementById(id).classList.remove("open");
    }

    /* =========================================================================
     * SYNCHRONISATION CLOUD & GOOGLE SHEET (PRIORITÉ IMPÉRATIVE ESPACE CHEF)
     * ========================================================================= */
    let cloudPushPromise = Promise.resolve();
    let isCloudPushInFlight = false;
    const PENDING_PUSH_KEY = "cochin_internes_pending_push_v1";

    // File d'attente PERSISTANTE (localStorage) des envois non confirmés par le cloud :
    // une validation du Chef n'est jamais perdue (réseau hôpital instable, onglet fermé, etc.).
    function readPendingPushes() {
      try {
        const v = JSON.parse(localStorage.getItem(PENDING_PUSH_KEY) || "[]");
        return Array.isArray(v) ? v : [];
      } catch (e) { return []; }
    }
    function writePendingPushes(list) {
      try {
        if (list && list.length) localStorage.setItem(PENDING_PUSH_KEY, JSON.stringify(list.slice(-40)));
        else localStorage.removeItem(PENDING_PUSH_KEY);
      } catch (e) {}
    }
    function hasPendingPushes() {
      return readPendingPushes().length > 0;
    }
    function pushHasSheetOps(e) {
      return Boolean(e && (e.syncAbsenceSheet || e.syncStaffSheet || Array.isArray(e.addedDates) || Array.isArray(e.removedDates)));
    }

    function tombstoneCustomKey(cKey, nowIso) {
      if (!Array.isArray(STATE.deletedCustomKeys)) STATE.deletedCustomKeys = [];
      if (!STATE.deletedCustomKeys.includes(cKey)) STATE.deletedCustomKeys.push(cKey);
      if (!STATE.deletedCustomAt || typeof STATE.deletedCustomAt !== "object") STATE.deletedCustomAt = {};
      STATE.deletedCustomAt[cKey] = nowIso || new Date().toISOString();
    }

    function updateSyncBadge(text) {
      const statusEl = document.getElementById("syncStatusText");
      if (statusEl) statusEl.textContent = text;
    }

    function pushStateToCloud(opts = {}) {
      const entry = Object.assign({}, opts, {
        isChefValidation: Boolean(opts.isChefValidation || isChefPlanningMode),
        _pid: Date.now() + "_" + Math.random().toString(36).slice(2, 8)
      });
      const list = readPendingPushes();
      list.push(entry);
      writePendingPushes(list);
      return enqueuePush(entry);
    }

    function enqueuePush(entry) {
      cloudPushPromise = cloudPushPromise
        .catch(() => {})
        .then(() => _executePushStateToCloud(entry));
      return cloudPushPromise;
    }

    // Rejoue les envois en attente (au démarrage, au retour du réseau, avant chaque synchronisation)
    async function flushPendingPushes() {
      let guard = 0;
      while (hasPendingPushes() && guard < 40) {
        guard++;
        const first = readPendingPushes()[0];
        const ok = await enqueuePush(first);
        if (!ok) return false;
      }
      return !hasPendingPushes();
    }

    async function _executePushStateToCloud(entry = {}) {
      const stillPending = readPendingPushes();
      if (entry._pid && !stillPending.some(e => e._pid === entry._pid)) {
        // Déjà couvert par un envoi complet plus récent
        return true;
      }
      updateSyncBadge("Sync...");
      isCloudPushInFlight = true;

      // Un envoi transmet l'état COMPLET : il couvre toutes les modifications en attente sans opération Google Sheet
      const coveredPids = stillPending
        .filter(e => e._pid === entry._pid || !pushHasSheetOps(e))
        .map(e => e._pid);
      const isChefVal = Boolean(entry.isChefValidation || isChefPlanningMode ||
        stillPending.some(e => coveredPids.includes(e._pid) && e.isChefValidation));

      const nowIso = new Date().toISOString();
      if (isChefVal && !STATE.chefValidatedAt) {
        STATE.chefValidatedAt = nowIso;
      }

      const compact = {
        updatedAt: nowIso,
        chefValidatedAt: STATE.chefValidatedAt || null,
        chefRevision: Number(STATE.chefRevision) || 0,
        deletedAbsenceIds: STATE.deletedAbsenceIds || [],
        deletedCustomKeys: STATE.deletedCustomKeys || [],
        deletedCustomAt: STATE.deletedCustomAt || {},
        absences: STATE.absences || [],
        interneGardes: STATE.interneGardes || {},
        customVacations: STATE.customVacations || {},
        chefDecisions: STATE.chefDecisions || {},
        lockedWeeks: STATE.lockedWeeks || {},
        presentations: STATE.presentations || [],
        meetings: STATE.meetings || [],
        phoneDirectory: STATE.phoneDirectory || []
      };

      const syncPayload = Object.assign({}, entry, { isChefValidation: isChefVal });
      delete syncPayload._pid;

      const evalCode = `
        var lock = LockService.getScriptLock();
        var gotLock = false;
        try { gotLock = lock.tryLock(25000); } catch (lockErr) { gotLock = false; }
        if (!gotLock) return { status: 'busy' };
        try {
        var props = PropertiesService.getScriptProperties();
        var rawExisting = props.getProperty('${CLOUD_PROP_KEY}');
        var existing = null;
        try { existing = rawExisting ? JSON.parse(rawExisting) : null; } catch (e) { existing = null; }
        var incoming = ${JSON.stringify(compact)};
        var syncOpts = ${JSON.stringify(syncPayload)};

        // Horodatage d'une entrée (validation chef, décision, demande) : la plus récente gagne
        function stampOf(o) {
          if (!o || typeof o !== 'object') return '';
          var best = '';
          ['validatedAt', 'decidedAt', 'resolvedAt', 'unlockedAt', 'updatedAt', 'createdAt'].forEach(function(f) {
            var v = o[f] ? String(o[f]) : '';
            if (v > best) best = v;
          });
          return best;
        }
        function mergeByStamp(exMap, inMap) {
          var out = Object.assign({}, exMap || {});
          Object.keys(inMap || {}).forEach(function(k) {
            var inc = inMap[k];
            if (!inc) return;
            var ex = out[k];
            if (ex && stampOf(ex) > stampOf(inc)) return;
            out[k] = inc;
          });
          return out;
        }

        if (existing && typeof existing === 'object') {
          var isChef = Boolean(syncOpts.isChefValidation);

          // 1. Suppressions d'absences (union)
          var delSet = {};
          (existing.deletedAbsenceIds || []).forEach(function(id) { if (id) delSet[id] = true; });
          (incoming.deletedAbsenceIds || []).forEach(function(id) { if (id) delSet[id] = true; });
          incoming.deletedAbsenceIds = Object.keys(delSet);

          // 2. Postes modifiés (customVacations) : fusion entrée par entrée, la plus récente gagne.
          //    Un appareil non à jour ne peut JAMAIS écraser une validation plus récente de l'autre chef.
          var mergedCustom = Object.assign({}, existing.customVacations || {});
          var inCustom = incoming.customVacations || {};
          Object.keys(inCustom).forEach(function(k) {
            var incV = inCustom[k];
            var exV = mergedCustom[k];
            if (!incV) return;
            if (!exV) { mergedCustom[k] = incV; return; }
            if (!isChef && exV.status === 'approved' && incV.status !== 'approved') return;
            if (stampOf(exV) > stampOf(incV)) return;
            mergedCustom[k] = incV;
          });

          // Tombstones horodatés : une suppression n'efface que les versions antérieures
          var delAt = Object.assign({}, existing.deletedCustomAt || {});
          Object.keys(incoming.deletedCustomAt || {}).forEach(function(k) {
            var v = String(incoming.deletedCustomAt[k] || '');
            if (!delAt[k] || v > String(delAt[k])) delAt[k] = v;
          });
          var delCustomSet = {};
          (existing.deletedCustomKeys || []).forEach(function(k) { if (k) delCustomSet[k] = true; });
          (incoming.deletedCustomKeys || []).forEach(function(k) { if (k) delCustomSet[k] = true; });
          Object.keys(delCustomSet).forEach(function(k) {
            var entryV = mergedCustom[k];
            if (!entryV) return;
            var keep = delAt[k] ? (stampOf(entryV) > String(delAt[k])) : Boolean(inCustom[k]);
            if (keep) {
              delete delCustomSet[k];
            } else {
              delete mergedCustom[k];
            }
          });
          incoming.customVacations = mergedCustom;
          incoming.deletedCustomKeys = Object.keys(delCustomSet);
          var keptDelAt = {};
          incoming.deletedCustomKeys.forEach(function(k) { if (delAt[k]) keptDelAt[k] = delAt[k]; });
          incoming.deletedCustomAt = keptDelAt;

          // 3. Décisions du Chef et semaines fixées : fusion par horodatage
          if (isChef && syncOpts.replaceChefDecisions) {
            incoming.chefDecisions = Object.assign({}, incoming.chefDecisions || {});
          } else {
            incoming.chefDecisions = mergeByStamp(existing.chefDecisions, isChef ? incoming.chefDecisions : {});
          }
          incoming.lockedWeeks = mergeByStamp(existing.lockedWeeks, isChef ? incoming.lockedWeeks : {});

          if (existing.chefValidatedAt && (!incoming.chefValidatedAt || existing.chefValidatedAt > incoming.chefValidatedAt)) {
            incoming.chefValidatedAt = existing.chefValidatedAt;
          }
          if (isChef) {
            incoming.chefRevision = Math.max((Number(existing.chefRevision) || 0) + 1, Number(incoming.chefRevision) || 1);
          } else {
            incoming.chefRevision = Math.max(Number(existing.chefRevision) || 0, Number(incoming.chefRevision) || 0);
          }

          // 4. Absences : une décision du Chef (approved / rejected) n'est jamais remplacée par une version plus ancienne
          var absByKey = {};
          (existing.absences || []).forEach(function(a) {
            if (!a || !a.date || !a.interneId || delSet[a.id]) return;
            absByKey[a.date + '__' + a.interneId] = a;
          });
          (incoming.absences || []).forEach(function(a) {
            if (!a || !a.date || !a.interneId || delSet[a.id]) return;
            var k = a.date + '__' + a.interneId;
            var ex = absByKey[k];
            if (!ex) { absByKey[k] = a; return; }
            var exDecided = (ex.status === 'approved' || ex.status === 'rejected');
            var inDecided = (a.status === 'approved' || a.status === 'rejected');
            if (exDecided && !inDecided) return;
            if (stampOf(ex) > stampOf(a)) return;
            absByKey[k] = Object.assign({}, ex, a);
          });
          incoming.absences = Object.keys(absByKey).sort().map(function(k) { return absByKey[k]; });
        }

        props.setProperty('${CLOUD_PROP_KEY}', JSON.stringify(incoming));

        if (syncOpts.syncAbsenceSheet) {
          try {
            var ssInt = SpreadsheetApp.openById('${INTERNES_SHEET_ID}');
            var shAbs = ssInt.getSheetByName('Planning Absence');
            if (shAbs) {
              var data = shAbs.getDataRange().getDisplayValues();
              var colMap = { 'Repos de garde': 2, 'CA 1': 3, 'CA 2': 4, 'CF': 5, 'Autre': 6 };
              var rowByDate = {};
              for (var r = 1; r < data.length; r++) {
                var dStr = String(data[r][0] || '').trim();
                if (dStr) rowByDate[dStr] = r + 1;
              }
              function isoToSheetDate(iso) {
                var p = String(iso || '').split('-');
                if (p.length !== 3) return '';
                return p[2] + '/' + p[1] + '/' + p[0].slice(2);
              }
              if (Array.isArray(syncOpts.addedDates) && syncOpts.interneName) {
                var cIdx = colMap[syncOpts.absType] || 3;
                syncOpts.addedDates.forEach(function(iso) {
                  var k = isoToSheetDate(iso);
                  if (rowByDate[k]) {
                    var cell = shAbs.getRange(rowByDate[k], cIdx);
                    var curVal = String(cell.getDisplayValue() || '').trim();
                    if (curVal.indexOf(syncOpts.interneName) === -1) {
                      cell.setValue(curVal ? (curVal + ' / ' + syncOpts.interneName) : syncOpts.interneName);
                    }
                  }
                });
              }
              if (Array.isArray(syncOpts.removedDates) && syncOpts.interneName) {
                var shortToken = String(syncOpts.interneName).split(' ')[0].toLowerCase();
                syncOpts.removedDates.forEach(function(iso) {
                  var k = isoToSheetDate(iso);
                  var rIdx = rowByDate[k];
                  if (!rIdx) return;
                  for (var c = 2; c <= 6; c++) {
                    var cell = shAbs.getRange(rIdx, c);
                    var curVal = String(cell.getDisplayValue() || '').trim();
                    if (!curVal) continue;
                    var parts = curVal.split('/').map(function(tok) { return String(tok || '').trim(); }).filter(function(tok) {
                      if (!tok) return false;
                      var low = tok.toLowerCase();
                      return low.indexOf(shortToken) === -1 && low !== String(syncOpts.interneName).toLowerCase();
                    });
                    var nextVal = parts.join(' / ');
                    if (nextVal !== curVal) cell.setValue(nextVal);
                  }
                });
              }
              SpreadsheetApp.flush();
            }
          } catch (sheetErr) {}
        }
        return {
          status: 'saved',
          updatedAt: incoming.updatedAt,
          chefRevision: incoming.chefRevision,
          chefValidatedAt: incoming.chefValidatedAt
        };
        } finally {
          try { lock.releaseLock(); } catch (relErr) {}
        }
      `;

      const bodyStr = JSON.stringify({ eval_code: evalCode });
      let pushedOk = false;
      for (let attempt = 0; attempt < 3 && !pushedOk; attempt++) {
        try {
          // ⚠️ Pas de keepalive au-delà de ~60 Ko : les navigateurs rejettent sinon la requête (limite 64 Ko)
          const resp = await fetch(WEBHOOK_URL, {
            method: "POST",
            keepalive: bodyStr.length < 60000,
            headers: { "Content-Type": "text/plain;charset=utf-8" },
            body: bodyStr
          });
          if (resp.ok) {
            const resJson = await resp.json().catch(() => null);
            if (resJson && resJson.status === "ok" && resJson.evalResult && resJson.evalResult.status === "saved") {
              pushedOk = true;
              break;
            }
          }
        } catch (err) {}
        if (attempt < 2) await new Promise(r => setTimeout(r, 1200 * (attempt + 1)));
      }
      isCloudPushInFlight = false;
      if (pushedOk) {
        writePendingPushes(readPendingPushes().filter(e => !coveredPids.includes(e._pid)));
        updateSyncBadge("Synchronisé ✓");
      } else {
        updateSyncBadge("⚠️ Non envoyé");
        if (isChefVal) {
          showToast("⚠️ Modification enregistrée sur cet appareil, pas encore sur le cloud — renvoi automatique");
        }
      }
      return pushedOk;
    }

    let isSyncRunning = false;
    async function syncWithCloud(manual = false) {
      if (isSyncRunning) return;
      isSyncRunning = true;
      try {
        await _syncWithCloudInner(manual);
      } finally {
        isSyncRunning = false;
      }
    }

    async function _syncWithCloudInner(manual = false) {
      if (isCloudPushInFlight) {
        try { await cloudPushPromise; } catch (e) {}
      }
      // Sécurité Espace Chef : tant que des modifications locales n'ont pas été confirmées par le cloud,
      // on les renvoie d'abord et on n'applique JAMAIS l'état distant par-dessus (pas de perte de validation).
      if (hasPendingPushes()) {
        const flushed = await flushPendingPushes();
        if (!flushed) {
          updateSyncBadge("⚠️ Non envoyé");
          if (manual) showToast("⚠️ Cloud injoignable : vos modifications restent enregistrées sur cet appareil");
          return;
        }
      }
      const seqBeforeFetch = localMutationSeq;
      const statusEl = document.getElementById("syncStatusText");
      if (statusEl) statusEl.textContent = "Sync...";
      const evalCode = `
        var props = PropertiesService.getScriptProperties();
        var raw = props.getProperty('${CLOUD_PROP_KEY}');
        var cloudState = raw ? JSON.parse(raw) : null;
        var sheetAbs = [];
        try {
          var ssInt = SpreadsheetApp.openById('${INTERNES_SHEET_ID}');
          var shAbs = ssInt.getSheetByName('Planning Absence');
          if (shAbs) {
            var rows = shAbs.getDataRange().getDisplayValues();
            for (var r = 1; r < rows.length; r++) {
              var dStr = String(rows[r][0] || '').trim();
              if (!dStr) continue;
              var cols = [
                { idx: 1, type: 'Repos de garde' },
                { idx: 2, type: 'CA 1' },
                { idx: 3, type: 'CA 2' },
                { idx: 4, type: 'CF' },
                { idx: 5, type: 'Autre' }
              ];
              for (var c = 0; c < cols.length; c++) {
                var val = String(rows[r][cols[c].idx] || '').trim();
                if (val) {
                  sheetAbs.push({ dateStr: dStr, name: val, type: cols[c].type });
                }
              }
            }
          }
        } catch (e) {}
        return { cloudState: cloudState, sheetAbs: sheetAbs };
      `;
      try {
        const resp = await fetch(WEBHOOK_URL, {
          method: "POST",
          headers: { "Content-Type": "text/plain;charset=utf-8" },
          body: JSON.stringify({ eval_code: evalCode })
        });
        const res = await resp.json();
        // Si l'utilisateur (ou le Chef) a effectué une modification locale pendant la requête, ne pas l'écraser
        if (localMutationSeq !== seqBeforeFetch || isCloudPushInFlight) {
          if (statusEl) statusEl.textContent = "Synchronisé";
          return;
        }
        if (res && res.evalResult) {
          const remote = res.evalResult.cloudState;
          if (remote) {
            // 1. Synchroniser deletedAbsenceIds & deletedCustomKeys
            const delAbsSet = new Set([
              ...(STATE.deletedAbsenceIds || []),
              ...(Array.isArray(remote.deletedAbsenceIds) ? remote.deletedAbsenceIds : [])
            ]);
            STATE.deletedAbsenceIds = Array.from(delAbsSet);

            const delCustomSet = new Set([
              ...(STATE.deletedCustomKeys || []),
              ...(Array.isArray(remote.deletedCustomKeys) ? remote.deletedCustomKeys : [])
            ]);
            if (remote.customVacations && typeof remote.customVacations === "object") {
              Object.keys(remote.customVacations).forEach(k => {
                if (remote.customVacations[k]) delCustomSet.delete(k);
              });
            }
            STATE.deletedCustomKeys = Array.from(delCustomSet);
            STATE.deletedCustomAt = Object.assign({}, STATE.deletedCustomAt || {}, remote.deletedCustomAt || {});

            // 2. Synchroniser les absences en donnant priorité absolue aux décisions du Chef ("approved" / "rejected")
            if (Array.isArray(remote.absences)) {
              STATE.absences = mergeAbsencesList(STATE.absences || [], remote.absences, STATE.deletedAbsenceIds);
            }

            // 3. Synchroniser customVacations (les validations et suppressions du Chef dans le cloud sont impératives)
            if (remote.customVacations && typeof remote.customVacations === "object") {
              const nextCustom = Object.assign({}, remote.customVacations);
              Object.keys(STATE.customVacations || {}).forEach(cKey => {
                if (delCustomSet.has(cKey)) return;
                const localEntry = STATE.customVacations[cKey];
                const remEntry = nextCustom[cKey];
                if (!remEntry) {
                  // Conserver uniquement une demande locale très récente non encore présente sur le cloud
                  if (localEntry && localEntry.status === "pending" && (!remote.chefValidatedAt || (localEntry.updatedAt && localEntry.updatedAt > remote.chefValidatedAt))) {
                    nextCustom[cKey] = localEntry;
                  }
                } else if (localEntry && localEntry.status === "approved" && remEntry.status !== "approved") {
                  nextCustom[cKey] = localEntry;
                } else if (localEntry && remEntry && localEntry.validatedAt && remEntry.validatedAt && localEntry.validatedAt > remEntry.validatedAt) {
                  nextCustom[cKey] = localEntry;
                }
              });
              delCustomSet.forEach(cKey => { delete nextCustom[cKey]; });
              STATE.customVacations = nextCustom;
            }

            // 4. Synchroniser chefDecisions et lockedWeeks depuis le cloud
            if (remote.chefDecisions && typeof remote.chefDecisions === "object") {
              STATE.chefDecisions = Object.assign({}, remote.chefDecisions);
            }
            if (remote.lockedWeeks && typeof remote.lockedWeeks === "object") {
              const mergedLocks = Object.assign({}, STATE.lockedWeeks || {}, remote.lockedWeeks);
              STATE.lockedWeeks = mergedLocks;
            }
            if (remote.interneGardes && typeof remote.interneGardes === "object") {
              STATE.interneGardes = Object.assign({}, STATE.interneGardes || {}, remote.interneGardes);
            }
            if (remote.chefValidatedAt) {
              STATE.chefValidatedAt = remote.chefValidatedAt;
            }
            if (Number(remote.chefRevision) > (Number(STATE.chefRevision) || 0)) {
              STATE.chefRevision = Number(remote.chefRevision);
            }

            if (Array.isArray(remote.presentations) && remote.presentations.length > 0) {
              STATE.presentations = mergePresentationsList(INITIAL_DATA.presentations, remote.presentations);
            }
            if (Array.isArray(remote.meetings) && remote.meetings.length > 0) {
              STATE.meetings = mergeMeetingsList(INITIAL_DATA.meetings, remote.meetings);
            }
            if (Array.isArray(remote.phoneDirectory) && remote.phoneDirectory.length > 0) {
              const map = {};
              (STATE.phoneDirectory || []).forEach(c => { map[c.id] = c; });
              remote.phoneDirectory.forEach(c => { if (c && c.id) map[c.id] = c; });
              STATE.phoneDirectory = Object.values(map);
            }
          }
          const sheetAbs = res.evalResult.sheetAbs || [];
          const delSetSheet = new Set(STATE.deletedAbsenceIds || []);
          sheetAbs.forEach(sa => {
            const parts = sa.dateStr.split("/");
            if (parts.length === 3) {
              const yr = parts[2].length === 2 ? "20" + parts[2] : parts[2];
              const iso = `${yr}-${parts[1].padStart(2, "0")}-${parts[0].padStart(2, "0")}`;
              const low = sa.name.toLowerCase();
              const matched = STATE.internes.find(i => low.includes(i.prenom.toLowerCase()) || low.includes(i.nom.toLowerCase()));
              if (matched) {
                const id = `abs-${matched.id}-${iso}`;
                if (delSetSheet.has(id)) return;
                if (!STATE.absences.some(x => x.id === id || (x.date === iso && x.interneId === matched.id))) {
                  STATE.absences.push({
                    id,
                    date: iso,
                    interneId: matched.id,
                    interneName: matched.fullName,
                    type: sa.type,
                    status: "pending",
                    comment: "Google Sheet"
                  });
                }
              }
            }
          });
          recomputeScheduleInPlace(STATE);
          try {
            localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify({
              updatedAt: new Date().toISOString(),
              chefValidatedAt: STATE.chefValidatedAt || null,
              chefRevision: Number(STATE.chefRevision) || 0,
              deletedAbsenceIds: STATE.deletedAbsenceIds || [],
              deletedCustomKeys: STATE.deletedCustomKeys || [],
              deletedCustomAt: STATE.deletedCustomAt || {},
              absences: STATE.absences,
              interneGardes: STATE.interneGardes || {},
              customVacations: STATE.customVacations || {},
              chefDecisions: STATE.chefDecisions || {},
              lockedWeeks: STATE.lockedWeeks || {},
              presentations: STATE.presentations,
              meetings: STATE.meetings,
              phoneDirectory: STATE.phoneDirectory || []
            }));
          } catch (e) {}
          renderAll();
        }
        if (statusEl) statusEl.textContent = "Synchronisé";
        if (manual) showToast("Synchronisé");
      } catch (e) {
        if (statusEl) statusEl.textContent = "Hors-ligne";
      }
    }

    // Synchronisation automatique multi-onglets et multi-appareils
    window.addEventListener("storage", (ev) => {
      if (ev.key === LOCAL_STORAGE_KEY && ev.newValue) {
        STATE = loadInitialState();
        renderAll();
      }
    });

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") {
        syncWithCloud(false);
      }
    });

    window.addEventListener("focus", () => {
      syncWithCloud(false);
    });

    window.addEventListener("online", () => {
      syncWithCloud(false);
    });

    // Avertir avant de fermer l'onglet si un envoi est en cours ou en attente
    window.addEventListener("beforeunload", (ev) => {
      if (isCloudPushInFlight) {
        ev.preventDefault();
        ev.returnValue = "";
      }
    });

    window.addEventListener("DOMContentLoaded", () => {
      renderAll();
      syncWithCloud(false);
      setInterval(() => {
        if (document.visibilityState === "visible" && !isCloudPushInFlight) {
          syncWithCloud(false);
        }
      }, 25000);
      if (hasPendingPushes()) updateSyncBadge("⚠️ Non envoyé");
    });
  </script>
</body>
</html>
"""


def generate_pwa_files(dataset: dict):
    html_out = (
        HTML_TEMPLATE
        .replace("__INITIAL_DATA_JSON__", js_json(dataset))
        .replace("__WEBHOOK_URL_JSON__", js_json(WEBHOOK_URL))
        .replace("__INTERNES_SHEET_ID_JSON__", js_json(INTERNES_SHEET_ID))
        .replace("__CLOUD_PROP_KEY_JSON__", js_json(CLOUD_PROP_KEY))
    )

    assert_zero_patient_data(html_out)

    INDEX_FILE.write_text(html_out, encoding="utf-8")

    manifest = {
        "name": "Radio B Cochin — Planning Internes & Chefs",
        "short_name": "Radio B Cochin",
        "description": "Planning des internes et chefs de Radiologie B à Cochin.",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#F8FAFC",
        "theme_color": "#F8FAFC",
        "icons": [
            {
                "src": "icon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            }
        ],
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    sw_version = dataset.get("updatedAt", "v5")
    sw_code = f"""const CACHE_NAME = 'cochin-internes-{sw_version}';
const ASSETS = ['./index.html', './manifest.json', './icon.svg'];
self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
}});
self.addEventListener('activate', e => {{
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
}});
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
}});
"""
    SW_FILE.write_text(sw_code, encoding="utf-8")

    svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="56" fill="#0284C7"/>
  <text x="128" y="148" text-anchor="middle" fill="#FFFFFF" font-family="-apple-system, sans-serif" font-weight="800" font-size="84">RB</text>
</svg>
"""
    ICON_FILE.write_text(svg_icon, encoding="utf-8")

    launcher_code = """#!/bin/zsh
cd "$(dirname "$0")"
open "https://mrthomaslef.github.io/agenda-internes/"
"""
    LAUNCHER_FILE.write_text(launcher_code, encoding="utf-8")
    LAUNCHER_FILE.chmod(LAUNCHER_FILE.stat().st_mode | stat.S_IEXEC)


if __name__ == "__main__":
    dataset = build_full_dataset()
    DATA_FILE.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    generate_pwa_files(dataset)
    print(f"Generated {INDEX_FILE} ({INDEX_FILE.stat().st_size} bytes) successfully with ZERO patient data!")
    try:
        res = sync_initial_state_to_cloud(dataset)
        print("Synced initial state to cloud:", res)
    except Exception as exc:
        print("Cloud sync warning:", exc)
    try:
        prod_res = push_to_prod_github()
        print("Pushed to GitHub Pages prod (https://mrthomaslef.github.io/agenda-internes/):", prod_res)
    except Exception as exc:
        print("GitHub Pages prod push warning:", exc)
