# 📝 Phase 1 : Labelling (Annotation des factures)

Ce guide vous explique comment annoter efficacement vos factures pour entraîner un modèle performant.

## ⏱️ Temps estimé : 15-25 heures pour 100-150 factures

---

## 🎯 Objectifs de cette phase

- ✅ Comprendre les bonnes pratiques d'annotation
- ✅ Annoter 100-150 factures (minimum)
- ✅ Maintenir une qualité et cohérence élevées
- ✅ Exporter les données pour l'entraînement

---

## 📊 Combien de factures annoter ?

| Nombre | Qualité attendue | Usage |
|--------|------------------|-------|
| 50-100 | Prototype | Tester le concept |
| 100-200 | Bon | MVP fonctionnel |
| 200-500 | Très bon | Production |
| 500+ | Excellent | Système robuste |

**Recommandation pour démarrer : 100-150 factures**

---

## 🎨 Comprendre l'interface Label Studio

### Vue principale

```
┌─────────────────────────────────────────────────┐
│ [<] Invoice.pdf                         [>] │
├─────────────────────────────────────────────────┤
│                                                 │
│         [Image de la facture]                   │
│                                                 │
│                                                 │
├─────────────────────────────────────────────────┤
│ Labels:                                         │
│ ⬜ numero_facture                               │
│ ⬜ date_facture                                 │
│ ⬜ montant_ttc                                  │
│ ...                                             │
└─────────────────────────────────────────────────┘
```

### Raccourcis clavier essentiels

| Touche | Action |
|--------|--------|
| `1-9` | Sélectionner un label rapidement |
| `Ctrl + Enter` | Valider et passer à la suivante |
| `Ctrl + Z` | Annuler dernière action |
| `Delete` | Supprimer l'annotation sélectionnée |
| `Molette` | Zoomer / dézoomer |
| `Espace + Drag` | Déplacer l'image |

---

## 📐 Guide d'annotation par champ

### 1. numero_facture (Rouge 🔴)

**Quoi annoter :**
- Le numéro unique de la facture
- Généralement en haut de la facture
- Format : INV-2024-001, F2024-123, etc.

**Exemples :**
```
✅ BON : Encercler "INV-2024-001234"
✅ BON : Encercler "Facture N° 2024-001"
❌ MAUVAIS : Encercler juste "Facture N°" sans le numéro
❌ MAUVAIS : Encercler plusieurs numéros différents
```

**Astuces :**
- Si le label "Facture N°" est collé au numéro → inclure les deux
- Si séparés → seulement le numéro
- Si plusieurs numéros (commande ET facture) → prendre le numéro de facture

---

### 2. date_facture (Bleu clair 🔵)

**Quoi annoter :**
- La date d'émission de la facture
- Souvent près du numéro
- Format : 05/11/2024, 5 novembre 2024, etc.

**Exemples :**
```
✅ BON : "Date : 05/11/2024"
✅ BON : "Émise le 5 novembre 2024"
✅ BON : "05.11.2024"
❌ MAUVAIS : Date d'échéance (c'est différent)
❌ MAUVAIS : Date de livraison
```

**Astuces :**
- Prendre la date complète avec le label si proche
- Ne pas confondre avec "Date d'échéance" ou "Date de paiement"

---

### 3. montant_ht (Vert clair 🟢)

**Quoi annoter :**
- Montant hors taxes
- Souvent dans un tableau récapitulatif
- Label : "Total HT", "Sous-total", etc.

**Exemples :**
```
✅ BON : "Total HT : 100,00 €"
✅ BON : "Montant HT   100.00 EUR"
❌ MAUVAIS : Montant d'une ligne produit
❌ MAUVAIS : Acompte ou sous-total partiel
```

---

### 4. montant_tva (Rose 🌸)

**Quoi annoter :**
- Montant de la TVA
- Attention : le MONTANT pas le taux !
- Label : "TVA", "T.V.A", "VAT"

**Exemples :**
```
✅ BON : "TVA 20% : 20,00 €"
✅ BON : "T.V.A.     20.00"
❌ MAUVAIS : "20%" (c'est le taux, pas le montant)
```

**Astuces :**
- Si plusieurs taux de TVA → annoter chaque ligne
- Si TVA totale → annoter le total

---

### 5. montant_ttc (Jaune ⭐ - LE PLUS IMPORTANT)

**Quoi annoter :**
- Montant TOTAL à payer (Toutes Taxes Comprises)
- **C'EST LE CHAMP LE PLUS IMPORTANT !**
- Label : "Total TTC", "Net à payer", "Total"

**Exemples :**
```
✅ BON : "TOTAL TTC : 120,00 €"
✅ BON : "Net à payer   120.00 EUR"
✅ BON : "TOTAL         120,00"
❌ MAUVAIS : Total HT
❌ MAUVAIS : Montant déjà payé
```

**⚠️ TRÈS IMPORTANT :**
- C'est souvent en gras, en gros, en bas de facture
- Double-vérifiez : HT + TVA = TTC
- En cas de doute, c'est le montant le plus gros

---

### 6. nom_fournisseur (Violet 🟣)

**Quoi annoter :**
- Nom ou raison sociale du fournisseur
- En général en haut de la facture
- Peut être une entreprise ou un nom de personne

**Exemples :**
```
✅ BON : "ENTREPRISE ABC SAS"
✅ BON : "Jean Dupont - Consultant"
❌ MAUVAIS : Nom du client
```

---

### 7. adresse_fournisseur (Rose clair 🎀)

**Quoi annoter :**
- Adresse complète du fournisseur
- Rue, code postal, ville
- Peut être sur plusieurs lignes

**Exemples :**
```
✅ BON : Annoter le bloc complet
"123 Rue de Paris
75001 Paris
France"

❌ MAUVAIS : Seulement la rue
❌ MAUVAIS : Adresse du client
```

---

### 8. siret_fournisseur (Bleu 🔷)

**Quoi annoter :**
- Numéro SIRET (14 chiffres)
- Ou SIREN (9 chiffres)
- Généralement en bas ou en haut de facture

**Exemples :**
```
✅ BON : "SIRET : 123 456 789 00012"
✅ BON : "SIREN 123456789"
❌ MAUVAIS : Numéro de TVA intracommunautaire
```

---

### 9. ligne_produit (Jaune pâle 📄)

**Quoi annoter :**
- Chaque ligne de produit/service
- Description + quantité + prix

**Exemples :**
```
✅ BON : Annoter chaque ligne du tableau
"Produit A    x2    50,00€"
"Produit B    x1    30,00€"

❌ MAUVAIS : Annoter tout le tableau en une fois
```

**Astuce :**
- Une annotation par ligne
- Inclure toute la ligne (description → prix)

---

## 🎯 Workflow optimal d'annotation

### Méthode recommandée (10-15 min par facture)

**1. Survol rapide (30 sec)**
- Scanner visuellement la facture
- Repérer les zones principales

**2. Champs prioritaires (5 min)**
Dans l'ordre :
1. ⭐ montant_ttc (le plus important)
2. numero_facture
3. date_facture
4. montant_ht
5. montant_tva

**3. Informations fournisseur (3 min)**
6. nom_fournisseur
7. adresse_fournisseur
8. siret_fournisseur

**4. Lignes de produits (2-5 min)**
9. ligne_produit (chacune)

**5. Vérification (1 min)**
- Toutes les annotations sont complètes
- Pas de chevauchement
- Rectangles bien alignés

**6. Valider (Ctrl+Enter)**

---

## ✅ Bonnes pratiques

### DO ✅

1. **Soyez cohérent**
   - Annotez toujours de la même manière
   - Si "Date :" inclus la première fois → toujours l'inclure

2. **Rectangles précis**
   - Englobez TOUT le texte
   - Pas trop d'espace vide autour
   - Aligné sur le texte

3. **Zoom si nécessaire**
   - N'hésitez pas à zoomer pour les petits textes
   - Vérifiez que rien n'est coupé

4. **Prenez des pauses**
   - Pause de 5 min toutes les heures
   - Évite les erreurs de concentration

5. **Annotez par sessions**
   - 10-20 factures par session
   - Maintient la qualité

### DON'T ❌

1. **Pas de sélections approximatives**
   - ❌ Rectangle qui coupe le texte
   - ❌ Plusieurs champs en un

2. **Pas d'incohérences**
   - ❌ "Date :" inclus parfois, parfois non
   - ❌ Labels différents pour même info

3. **Pas de précipitation**
   - ❌ Annoter 50 factures d'affilée sans pause
   - ❌ Valider sans vérifier

4. **Pas d'oublis**
   - ❌ Oublier des champs
   - ❌ Sauter des lignes de produits

---

## 📊 Suivi de progression

### Template de suivi

Créez un fichier `progression.txt` :

```
OBJECTIF : 150 factures

Jour 1  : 10 factures (2h)     ▓░░░░░░░░░ 7%
Jour 2  : 15 factures (2h30)   ▓▓░░░░░░░░ 17%
Jour 3  : 12 factures (2h)     ▓▓▓░░░░░░░ 25%
...
```

### Rythme recommandé

| Planning | Factures/jour | Durée totale |
|----------|---------------|--------------|
| Intensif | 20-25 | 6-8 jours |
| Modéré | 10-15 | 10-15 jours |
| Relax | 5-10 | 15-30 jours |

**Astuce :** Visez 10-15 factures par jour = terminé en 2 semaines

---

## 🎨 Astuces pour accélérer

### 1. Organisation physique
- Écran large ou double écran
- Souris (plus rapide que trackpad)
- Clavier : utilisez les chiffres 1-9

### 2. Workflow optimisé
```
1. Ouvrir facture
2. Sélectionner label 1 (touche 1)
3. Tracer rectangle → Clic
4. Touche 2 → Rectangle → Clic
5. ...
6. Ctrl+Enter (suivante)
```

### 3. Batch par type
Annotez par lots de factures similaires :
- Même fournisseur → même mise en page
- Vous allez plus vite

### 4. Template mental
Créez-vous un "template mental" :
- Haut gauche : fournisseur
- Haut droite : numéro + date
- Milieu : lignes
- Bas : totaux

---

## 🔍 Contrôle qualité

### Auto-vérification (toutes les 10 factures)

Checklist :
- [ ] Tous les champs annotés ?
- [ ] Rectangles bien alignés ?
- [ ] Pas de chevauchements ?
- [ ] Cohérence avec les précédentes ?
- [ ] Montant TTC toujours annoté ?

### Revue par un tiers (optionnel mais recommandé)

Si possible, faites réviser 10% de vos annotations par quelqu'un d'autre.

---

## 📤 Exporter les données (après 100+ annotations)

### Via l'interface Label Studio

1. Aller dans votre projet
2. Cliquer sur "Export"
3. Choisir format "JSON"
4. Télécharger

### Via le script

```bash
python scripts/export_from_label_studio.py
```

Les données seront dans :
```
data/exports/export_YYYYMMDD_HHMMSS.json
```

---

## 🎉 Phase 1 terminée !

### ✅ Checklist finale

- [ ] 100+ factures annotées
- [ ] Qualité vérifiée (revue de 10%)
- [ ] Données exportées
- [ ] Sauvegarde faite

### 📊 Statistiques à vérifier

```bash
# Statistiques dans Label Studio
Projet → Vue d'ensemble
```

Vérifiez :
- Nombre de tâches complètes : 100+
- Taux de completion : 100%
- Nombre moyen d'annotations par facture : ~9-15

---

## 🚀 Prochaine étape

👉 **[Phase 2 : Training (Entraînement)](phase2-training.md)**

Vous allez enfin entraîner votre modèle ! 🤖

---

## 💡 Conseils motivationnels

**C'est long, mais ça vaut le coup !**

- ✅ Après 20 factures : Vous avez le rythme
- ✅ Après 50 factures : Vous êtes un pro
- ✅ Après 100 factures : Le modèle va bien fonctionner
- ✅ Après 150 factures : Vous allez avoir un système solide

**Musique ou podcast en fond** aide à tenir sur la durée 🎵

---

## 🆘 Problèmes courants

### "Je me trompe souvent"

**Solution :** Faites des pauses plus fréquentes. 10 factures, puis 5 min de pause.

### "C'est trop lent"

**Normal** au début. Vous allez accélérer :
- Facture 1-10 : 15-20 min/facture
- Facture 10-50 : 10-12 min/facture
- Facture 50+ : 8-10 min/facture

### "Toutes mes factures sont différentes"

**C'est bon signe !** Le modèle sera plus robuste. Continuez.

### "Je ne sais pas quoi annoter"

Consultez les exemples ci-dessus ou créez un document de référence avec des screenshots.

---

**Courage, vous allez y arriver ! 💪**
