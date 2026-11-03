/**
 * ============================================================================
 * GÉNÉRATEUR DU GOOGLE DOC OFFICIEL — RÈGLES DE RÉPARTITION DES INTERNES
 * Service de Radiologie B — Hôpital Cochin (AP-HP) — Semestre Hiver 2026–2027
 * ============================================================================
 *
 * COMMENT EXÉCUTER CE SCRIPT (1 CLIC) :
 * 1. Ouvrez votre projet Google Apps Script (ou depuis le Google Sheet via Extensions > Apps Script).
 * 2. Collez cette fonction `creerGoogleDocReglesInternes` et cliquez sur "▷ Exécuter".
 * 3. Acceptez l'autorisation Google Docs (`https://www.googleapis.com/auth/documents`) si demandée.
 * 4. Le Google Doc complet et mis en forme est immédiatement créé dans votre Google Drive
 *    et son URL directe s'affiche dans le journal d'exécution !
 */
function creerGoogleDocReglesInternes() {
  var doc = DocumentApp.create("Règles de Répartition du Planning des Internes — Radiologie B Cochin (Hiver 2026–2027)");
  var body = doc.getBody();
  body.clear();

  // Marges du document
  body.setMarginTop(36);
  body.setMarginBottom(36);
  body.setMarginLeft(45);
  body.setMarginRight(45);

  function addTitle(text, subtitle) {
    var p = body.appendParagraph(text);
    p.setHeading(DocumentApp.ParagraphHeading.TITLE);
    p.setForegroundColor("#0F172A");
    p.setFontFamily("Arial");
    p.setFontSize(18);
    p.setBold(true);
    p.setSpacingAfter(4);

    var sub = body.appendParagraph(subtitle);
    sub.setForegroundColor("#475569");
    sub.setFontFamily("Arial");
    sub.setFontSize(10.5);
    sub.setItalic(true);
    sub.setSpacingAfter(14);
    body.appendHorizontalRule();
  }

  function addH1(text) {
    var p = body.appendParagraph(text);
    p.setHeading(DocumentApp.ParagraphHeading.HEADING1);
    p.setForegroundColor("#1E3A8A");
    p.setFontFamily("Arial");
    p.setFontSize(13.5);
    p.setBold(true);
    p.setSpacingBefore(14);
    p.setSpacingAfter(6);
  }

  function addH2(text) {
    var p = body.appendParagraph(text);
    p.setHeading(DocumentApp.ParagraphHeading.HEADING2);
    p.setForegroundColor("#0F172A");
    p.setFontFamily("Arial");
    p.setFontSize(11);
    p.setBold(true);
    p.setSpacingBefore(8);
    p.setSpacingAfter(4);
  }

  function addPara(text) {
    var p = body.appendParagraph(text);
    p.setForegroundColor("#1E293B");
    p.setFontFamily("Arial");
    p.setFontSize(10);
    p.setSpacingAfter(6);
    return p;
  }

  function addBullet(boldPrefix, restText, nesting) {
    var item = body.appendListItem(boldPrefix + restText);
    item.setGlyphType(DocumentApp.GlyphType.BULLET);
    item.setNestingLevel(nesting || 0);
    item.setFontFamily("Arial");
    item.setFontSize(10);
    item.setForegroundColor("#1E293B");
    item.setSpacingAfter(3);
    if (boldPrefix && boldPrefix.length > 0) {
      item.editAsText().setBold(0, boldPrefix.length - 1, true);
    }
    return item;
  }

  function addStyledTable(headers, rows) {
    var data = [headers].concat(rows);
    var table = body.appendTable(data);
    table.setBorderColor("#CBD5E1");
    table.setBorderWidth(1);
    for (var r = 0; r < table.getNumRows(); r++) {
      var row = table.getRow(r);
      var isHeader = (r === 0);
      var bg = isHeader ? "#1E3A8A" : (r % 2 === 1 ? "#FFFFFF" : "#F8FAFC");
      var fg = isHeader ? "#FFFFFF" : "#1E293B";
      for (var c = 0; c < row.getNumCells(); c++) {
        var cell = row.getCell(c);
        cell.setBackgroundColor(bg);
        cell.setPaddingTop(5);
        cell.setPaddingBottom(5);
        cell.setPaddingLeft(6);
        cell.setPaddingRight(6);
        var txt = cell.editAsText();
        txt.setFontFamily("Arial");
        txt.setFontSize(isHeader ? 9 : 8.5);
        txt.setForegroundColor(fg);
        txt.setBold(isHeader || c === 0);
      }
    }
    body.appendParagraph("").setSpacingAfter(4);
  }

  addTitle(
    "Règles Officielles de Répartition des Internes sur le Planning",
    "Service de Radiologie B — Hôpital Cochin (AP-HP) • Chef de Service : Pr Antoine FEYDY\nSemestre d'Hiver 2026–2027 (du lundi 2 novembre 2026 au vendredi 30 avril 2027 — 26 semaines)"
  );

  // SECTION 1
  addH1("1. Effectif des Internes du Semestre Hiver 2026–2027");
  addPara("Le service accueille 6 internes répartis en deux groupes fonctionnels :");
  addBullet("5 Internes « Seniors » (hors Phase Socle) ", "en rotation équilibrée sur les postes diagnostiques, d'urgences et interventionnels :", 0);
  addBullet("Gabriel COTTIN (GC) : ", "Interne DES Radiologie", 1);
  addBullet("Marwane HAMMAMI (MH) : ", "Interne DES Radiologie", 1);
  addBullet("Milan KORSEC (MK) : ", "Interne DES Radiologie", 1);
  addBullet("Nathanaël SEBBAN (NS) : ", "Interne DES Radiologie", 1);
  addBullet("Oussama TALIB (OT) : ", "Docteur Junior (DJ) — Radiologie", 1);
  addBullet("1 Interne en Phase Socle (1er semestre) ", "avec maquette pédagogique dédiée :", 0);
  addBullet("Noé GRANDVAL (NG) : ", "Interne DES Radiologie (Phase Socle)", 1);

  // SECTION 2
  addH1("2. Postes, Vacations et Horaires Officiels");
  addH2("2.1. Séparation stricte des 3 Scanners du service");
  addBullet("TDM SAU (TDM Ollier 4 — Scanner des Urgences) : ", "08h00 – 18h30 (Matin : 08h00 – 13h00 • Après-midi : 13h30 – 18h30).", 0);
  addBullet("SCAN ACHARD (TDM Achard 1 — Diagnostique & Interventionnel) : ", "08h30 – 18h30 (Matin : 08h30 – 13h00 • Après-midi : 13h30 – 18h30).", 0);
  addBullet("TDM OLLIER DIAG (TDM Ollier 3 — Diagnostique ostéo-articulaire) : ", "08h30 – 18h00 (Matin : 08h30 – 13h00 • Après-midi : 13h30 – 18h00).", 0);

  addH2("2.2. Séparation des IRM du matin et de l'après-midi");
  addBullet("IRM Matin (IRM 3T et IRM 1,5T) : ", "début dès 07h45 (07h45 – 13h00).", 0);
  addBullet("IRM Après-midi (IRM) : ", "début dès 13h00 (vacation comptabilisée séparément des IRM du matin).", 0);

  addH2("2.3. Échographie et Radiologie Interventionnelle");
  addBullet("ÉCHOGRAPHIE (ECHO) : ", "Matin dès 09h00 • Après-midi dès 14h00.", 0);
  addBullet("POSTE C / GESTES INTERVENTIONNELS (GESTES (C)) : ", "Matin dès 09h00 • Après-midi dès 14h00.", 0);
  addBullet("SALLE ALLURA (ALLURA — Vasculaire / Os) : ", "Matin 08h30 – 13h00 • Après-midi dès 14h00.", 0);

  addH2("2.4. Séparation des Consultations et de la Lecture / Relecture");
  addBullet("CONSULTATION INTERNES (CONSULTATION) : ", "14h00 – 15h00, ouverte aux internes uniquement le Mardi après-midi et le Vendredi après-midi.", 0);
  addBullet("LECTURE / RELECTURE (LECTURE) : ", "14h00 – 16h00, ouverte le Mardi après-midi (Relecture systématique avec le Pr Jean-Luc DRAPÉ, sauf en décembre après la 1re semaine : pas de relecture les mardis 08/12, 15/12, 22/12 et 29/12/2026) et le Vendredi après-midi.", 0);

  // SECTION 3
  addH1("3. Règles Fondamentales de Répartition Quotidienne");
  addBullet("1. Interdiction absolue de faire le même poste toute la journée (Matin ≠ Après-midi) : ", "un interne ne peut jamais être affecté au même poste actif le matin et l'après-midi d'une même journée, ni cumuler une IRM le matin (3T / 1,5T) et une IRM l'après-midi le même jour.", 0);
  addBullet("2. Zéro doublon sur les postes diagnostiques et interventionnels : ", "hors TDM SAU (binôme Socle + Senior), un même poste ouvert n'est jamais attribué en doublon à deux internes sur la même demi-journée.", 0);
  addBullet("3. Gestion automatique des vacations fermées (FERMÉ / MAINTENANCE) : ", "toute vacation fermée dans le planning des Chefs (ex. IRM du vendredi après-midi fermée 1 semaine sur 2 les semaines impaires) est affichée et l'interne est réaffecté sur une vacation ouverte prioritaire.", 0);
  addBullet("4. Règles spécifiques Échographie du Mercredi matin (Dr Fabrice THÉVENIN) & Relecture du Mardi PM (Pr Jean-Luc DRAPÉ) : ", "aucun interne en Échographie le mercredi matin sur le mois de Novembre 2026 (obligatoire à partir de Décembre 2026) ; pas de relecture IRM avec le Pr Drapé le mardi après-midi en Décembre 2026 sauf la première semaine (maintenue le 01/12/2026, suspendue les 08/12, 15/12, 22/12 et 29/12/2026).", 0);
  addBullet("5. Journée inaugurale du Lundi 2 novembre 2026 : ", "Matin (08h15 – 12h00) réservé à l'accueil et la formation obligatoire (FORMATION / ACCUEIL) ; Après-midi calé sur la trame de référence du Dr Hippolyte MONNIER (Gabriel et Noé en TDM Ollier 3, Marwane en IRM avec Pr Feydy, Milan en Écho avec Dr Monnier, Nathanaël au TDM SAU, Oussama en demi-off).", 0);

  // SECTION 4
  addH1("4. Hiérarchie de Couverture : Permanence SAU & 13 Vacations Obligatoires (PH / PU-PH)");
  addPara("Toute vacation ouverte assurée par un PH ou PU-PH (Pr Feydy, Pr Drapé, Dr Mihoubi Bouvier, Dr Laporte, Dr Costea, Dr Yang, Dr Moutounet, Dr Rubini, Dr Seror, Dr Hammoud) doit impérativement être couverte par un interne, quitte à laisser sans interne une vacation d'Assistant Spécialiste (Dr Hamadouche) ou de Chef de Clinique (Dr Lefèvre, Dr Monnier, Dr Lusi, Dr Allel, Dr Talabard).");
  addBullet("Permanence obligatoire au TDM SAU : ", "couverte 100 % des demi-journées ouvrées par un interne senior, sauf le mardi matin où Noé GRANDVAL (Phase Socle) assure le TDM SAU en solo sous la supervision directe du Dr Macil HAMADOUCHE (MH).", 0);

  addStyledTable(
    ["Jour", "Vacations Obligatoires — Matin (AM)", "Vacations Obligatoires — Après-midi (PM)"],
    [
      ["Lundi", "• ECHO (+ Permanence TDM SAU)", "• IRM (+ Permanence TDM SAU)"],
      ["Mardi", "• GESTES (C)\n• IRM 3T\n• IRM 1,5T\n• TDM SAU (Noé solo avec Dr M. Hamadouche)", "• LECTURE (Relecture Pr Drapé systématique, sauf déc. après S1)\n• Permanence TDM SAU"],
      ["Mercredi", "• IRM 3T\n• IRM 1,5T\n• TDM OLLIER DIAG\n• ECHO (à partir de décembre 2026)\n• Permanence TDM SAU", "• GESTES (C)\n• IRM\n• SCAN ACHARD\n• ECHO\n• Permanence TDM SAU"],
      ["Jeudi", "• ECHO\n• GESTES (C)\n• Permanence TDM SAU", "• IRM (+ Permanence TDM SAU)"],
      ["Vendredi", "• IRM 3T (+ Permanence TDM SAU)", "• Permanence TDM SAU (+ CONSULTATION)"]
    ]
  );

  // SECTION 5
  addH1("5. Quotas Hebdomadaires et Équilibrage Semestriel par Poste");
  addBullet("Quota de Scanner des Urgences (TDM SAU) : ", "2 TDM SAU / semaine pour chacun des 5 internes seniors (en privilégiant 1 Matin + 1 Après-midi ; 3 uniquement à titre exceptionnel en cas de congés/RG multiples) et 3 TDM SAU / semaine pour Noé (Phase Socle).", 0);
  addBullet("Quota d'IRM d'Après-midi (IRM) : ", "maximum 1 IRM d'après-midi par semaine et par interne (2e uniquement à titre exceptionnel pour remplacement congés/RG).", 0);
  addBullet("Quota de Poste C / Radiologie Interventionnelle (GESTES (C) / ALLURA) : ", "1 à 2 par semaine pour les seniors (~27 à 30 sur le semestre, équilibrés Matin/PM) ; limité à max 1 / semaine pour Noé (15 sur le semestre).", 0);
  addBullet("Quota de Consultations (CONSULTATION) et Lectures (LECTURE) : ", "maximum 1 CONSULTATION par semaine par interne (cible : 8 à 9 consultations par senior sur le semestre, et 3 consultations pour Noé uniquement sur Mars–Avril 2027) ; 7 à 8 LECTURE par interne sur le semestre.", 0);
  addBullet("Équilibrage diagnostique global : ", "lissage multi-passes entre internes pour l'Échographie (~25 à 27), l'IRM Matin 3T/1,5T (~23 à 25), l'IRM Après-midi (~13 à 15) et les Scanners diagnostiques (SCAN ACHARD et TDM OLLIER DIAG).", 0);

  // SECTION 6
  addH1("6. Règles Spécifiques à l'Interne en Phase Socle (Noé GRANDVAL)");
  addBullet("1er mois (Novembre 2026, S1 à S4) : ", "TDM SAU le lundi matin (binôme), mardi matin (solo avec Dr M. Hamadouche) et jeudi matin (binôme avec Dr M. Hamadouche) ; ECHO le mercredi PM (avec Dr Mihoubi) ; IRM 3T le vendredi matin ; demi-offs fixes le mercredi matin et le jeudi après-midi.", 0);
  addBullet("Du 2e au 6e mois (Décembre 2026 à Avril 2027) : ", "TDM SAU le mardi matin (solo avec Dr M. Hamadouche) + 2 TDM SAU en binôme tournants chaque semaine, complétés par ses vacations propres d'IRM 3T, IRM 1,5T, ECHO, TDM OLLIER DIAG, SCAN ACHARD, GESTES (C) et LECTURE.", 0);
  addBullet("Mars – Avril 2027 (dès le 01/03/2027) : ", "intégration au tour de CONSULTATION (3 consultations sur les 2 derniers mois).", 0);

  // SECTION 7
  addH1("7. Règles des Demi-Journées Libres (« Demi-Offs »)");
  addBullet("Quota hebdomadaire : ", "2 demi-offs (1/2 journée libre) maximum par semaine et par interne (ramené à 0 si l'interne a ≥ 6 demi-journées de congés ou RG dans la semaine).", 0);
  addBullet("Interdictions strictes : ", "jamais de demi-off le Mardi après-midi ni le Vendredi après-midi ; jamais 2 demi-offs sur la même journée (Matin + Après-midi le même jour interdits).", 0);
  addBullet("Alternance Matin / Après-midi : ", "1 demi-off Matin + 1 demi-off Après-midi chaque semaine (~25 Matins et ~25 Après-midis sur le semestre).", 0);
  addBullet("Demi-journées off fixes protégées (dès la semaine 2, 09/11/2026) : ", "Lundi matin pour Oussama TALIB, Mardi matin pour Gabriel COTTIN, Jeudi matin pour Marwane HAMMAMI.", 0);

  // SECTION 8
  addH1("8. Gardes, Repos de Garde (RG) et Congés (CA / CF)");
  addBullet("Repos de Garde (RG) : ", "journée complète de RG automatique le lendemain ouvré de chaque garde (avec maintien des 2 demi-offs hebdomadaires et couverture garantie du TDM SAU et des vacations obligatoires).", 0);
  addBullet("Congés (CA / CF) : ", "maximum 2 internes en congés simultanément ; validation obligatoire dans l'Espace Chef avec alertes automatiques en cas de conflit.", 0);
  addBullet("Jours fériés Hiver 2026–2027 : ", "11/11/2026 (Armistice), 25/12/2026 (Noël), 01/01/2027 (Jour de l'An), 29/03/2027 (Lundi de Pâques).", 0);

  // SECTION 9
  addH1("9. Enseignement, Staffs et Présentations Pédagogiques");
  addBullet("Cas cliniques (Mardi 12h30, dès le 10/11/2026) & Bibliographie (Vendredi, dès le 13/11/2026) : ", "attribués uniquement aux internes présents ; décalage de 3 semaines entre Cas et Biblio ; espacement minimal garanti de 18 à 24 jours (2,5 à 3,5 semaines) entre deux présentations quelconques et de 35 à 42 jours (5 à 6 semaines) entre deux Cas ou deux Biblios.", 0);
  addBullet("Cours des Chefs (Mardi 13h00 – 14h00, dès le 03/11/2026) : ", "programme officiel de 25 cours d'Imagerie Ostéo-Articulaire coordonné par le Dr Fadila MIHOUBI BOUVIER.", 0);
  addBullet("Réunions obligatoires du service : ", "Bone Club Cochin (Mercredis 18h00 – 20h00, Amphi Luton) et CRA Confrontations Radio-Anapath (Vendredis 14h00 – 16h00, Salle de Staff Radio B).", 0);

  // SECTION 10
  addH1("10. Bilan Chiffré de la Répartition sur le Semestre (Hiver 2026–2027)");
  addStyledTable(
    ["Interne", "Statut", "TDM SAU (M/PM)", "Demi-Offs (M/PM)", "IRM 3T", "IRM 1,5T", "IRM PM", "Écho", "Poste C (+Allura)", "Achard", "Ollier", "CS", "Lect.", "RG", "CA"],
    [
      ["Gabriel COTTIN", "Senior", "47 (22M/25P)", "50 (25M/25P)", "12", "11", "15", "26", "28 (+1)", "19", "7", "8", "7", "12", "8"],
      ["Marwane HAMMAMI", "Senior", "43 (18M/25P)", "48 (25M/23P)", "13", "12", "13", "26", "28 (+1)", "19", "6", "9", "7", "16", "10"],
      ["Milan KORSEC", "Senior", "44 (20M/24P)", "49 (27M/22P)", "12", "11", "14", "25", "27", "17", "6", "9", "7", "20", "10"],
      ["Nathanaël SEBBAN", "Senior", "48 (19M/29P)", "51 (26M/25P)", "13", "11", "14", "26", "29", "18", "7", "9", "7", "16", "2"],
      ["Oussama TALIB", "DJ (Senior)", "43 (20M/23P)", "48 (25M/23P)", "13", "11", "14", "25", "30", "17", "7", "9", "8", "16", "10"],
      ["Noé GRANDVAL", "Phase Socle", "76 (43M/33P)", "51 (26M/25P)", "12", "11", "15", "27", "15", "25", "8", "3", "8", "0", "0"]
    ]
  );

  doc.saveAndClose();
  Logger.log("Google Doc créé avec succès : " + doc.getUrl());
  return { id: doc.getId(), url: doc.getUrl(), name: doc.getName() };
}
