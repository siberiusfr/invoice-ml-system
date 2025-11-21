# 🎉 BIENVENUE DANS VOTRE PROJET !

Vous avez maintenant tous les fichiers nécessaires pour démarrer votre système d'extraction automatique de factures.

## 📂 Structure du projet

```
invoice-ml-system/
├── 📄 README.md              # Documentation principale
├── 🚀 QUICKSTART.md          # Démarrage rapide
├── ⚙️ install.sh             # Installation automatique (Mac/Linux)
├── ⚙️ install.bat            # Installation automatique (Windows)
├── 🐳 docker-compose.yml     # Configuration Docker
├── 📦 requirements.txt       # Dépendances Python
│
├── 📁 api/                   # API REST (À venir)
├── 📁 config/                # Configuration
│   └── settings.example.yaml
├── 📁 data/                  # Vos données
│   ├── raw/invoices/         # ← Placez vos factures ici
│   ├── label-studio/         # Données Label Studio
│   ├── processed/            # Datasets préparés
│   └── models/               # Modèles entraînés
├── 📁 docs/                  # Documentation détaillée
│   ├── phase0-setup.md       # Guide d'installation
│   ├── phase1-labelling.md   # Guide d'annotation
│   └── troubleshooting.md    # Résolution de problèmes
├── 📁 label-studio/          # Templates Label Studio
├── 📁 scripts/               # Scripts d'automatisation
├── 📁 training/              # Scripts d'entraînement (À venir)
└── 📁 monitoring/            # Dashboard (À venir)
```

## 🚀 Démarrage RAPIDE (5 minutes)

### Option 1 : Installation automatique (Recommandé)

**Mac/Linux :**
```bash
./install.sh
```

**Windows :**
```cmd
install.bat
```

### Option 2 : Installation manuelle

```bash
# 1. Créer environnement Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Lancer Label Studio
docker-compose up -d

# 4. Configurer
cp config/settings.example.yaml config/settings.yaml
```

## 📚 Documentation

### Débutants - Lisez dans cet ordre :

1. **[README.md](README.md)** - Vue d'ensemble complète
2. **[docs/phase0-setup.md](docs/phase0-setup.md)** - Installation pas-à-pas
3. **[docs/phase1-labelling.md](docs/phase1-labelling.md)** - Comment annoter
4. **[docs/troubleshooting.md](docs/troubleshooting.md)** - En cas de problème

### Pressés - Démarrage rapide :

→ **[QUICKSTART.md](QUICKSTART.md)**

## ⏱️ Timeline du projet

| Phase | Description | Temps | Statut |
|-------|-------------|-------|--------|
| Phase 0 | Installation & Setup | 1-2h | 📦 À faire |
| Phase 1 | Annotation (100+ factures) | 15-20h | 📝 À faire |
| Phase 2 | Entraînement du modèle | 2-4h | 🤖 À venir |
| Phase 3 | API & Production | 4-6h | 🚀 À venir |

**Total estimé : 3-4 semaines à temps partiel**

## 🎯 Vos prochaines actions

### Aujourd'hui (1-2h)

- [ ] Lire le README.md
- [ ] Lancer `install.sh` ou `install.bat`
- [ ] Créer votre compte Label Studio (http://localhost:8080)
- [ ] Créer votre premier projet
- [ ] Copier quelques factures de test

### Cette semaine (5-10h)

- [ ] Annoter 30-50 premières factures
- [ ] Prendre le rythme
- [ ] Ajuster votre workflow

### Ce mois (20-30h)

- [ ] Terminer 100-150 annotations
- [ ] Exporter les données
- [ ] Entraîner le premier modèle
- [ ] Tester l'API

## 💡 Conseils pour réussir

### ✅ DO

- Commencez petit (10 factures pour tester)
- Annotez régulièrement (10-15 factures/jour)
- Sauvegardez vos annotations régulièrement
- Lisez la documentation

### ❌ DON'T

- Ne tentez pas de tout faire en une fois
- Ne négligez pas la qualité des annotations
- Ne sautez pas les étapes
- N'abandonnez pas après 20 factures !

## 🆘 Besoin d'aide ?

### En cas de problème

1. **Consultez [docs/troubleshooting.md](docs/troubleshooting.md)**
2. Vérifiez les logs : `docker-compose logs`
3. Lisez les messages d'erreur complets
4. Recherchez l'erreur sur Google/StackOverflow

### Pour des questions

- 📖 Relire la documentation
- 💬 GitHub Discussions (si configuré)
- 🐛 GitHub Issues pour les bugs

## 📊 Statistiques du projet

Une fois que vous aurez commencé :

```bash
# Voir vos progrès
python scripts/export_from_label_studio.py

# Résultat exemple :
📊 STATISTIQUES
  Factures annotées : 127
  
  Annotations par type :
    • montant_ttc           : 127 occurrences
    • numero_facture        : 125 occurrences
    ...
```

## 🎉 C'est parti !

Vous avez tout ce qu'il faut pour réussir.

**Première étape :** Lancer l'installation
```bash
# Mac/Linux
./install.sh

# Windows
install.bat
```

Puis suivez les instructions à l'écran.

---

**Bon courage et bon dev ! 💪🚀**

*P.S. : Annotez 10 factures par jour pendant 2 semaines = vous avez terminé !*
