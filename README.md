# Tableau de Bord d'Analyse des Ventes

Une application web moderne pour analyser et visualiser les données de ventes à partir de fichiers CSV. Cette application offre des visualisations interactives et des analyses détaillées pour mieux comprendre les tendances de ventes.

## 🚀 Fonctionnalités

### 📊 Visualisations
- Graphique des ventes journalières
- Distribution des ventes par type de forfait
- Analyse horaire des ventes
- Distribution des tickets vendus
- Tendances mensuelles
- Analyse par jour de la semaine
- Top 5 des meilleures journées

### 🔍 Filtres Dynamiques
- Filtrage par date
- Filtrage par type de forfait
- Filtrage par plage de prix

### 📈 Statistiques Avancées
- Croissance mensuelle des ventes
- Heures de pointe
- Performance par type de forfait
- Moyenne des ventes quotidiennes
- Valeur moyenne des tickets
- Nombre de clients uniques

## 🛠️ Technologies Utilisées

### Backend
- Python 3.11
- Flask 3.0.0
- Pandas 2.1.3
- Flask-CORS 4.0.0

### Frontend
- React 17
- Chart.js
- Tailwind CSS

## 📋 Prérequis
- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Navigateur web moderne

## 🔧 Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_REPO]
```

2. Installez les dépendances Python :
```bash
pip install -r requirements.txt
```

3. Lancez l'application :
```bash
python app.py
```

4. Ouvrez votre navigateur et accédez à :
```
http://localhost:5000
```

## 📁 Structure des Fichiers CSV
L'application attend des fichiers CSV avec la structure suivante :
- Date : Date de la vente
- Time : Heure de la vente
- Username : Identifiant de l'utilisateur
- Profile : Type de forfait (ex: 1HEURE, 24HEURES, 1SEMAINE)
- Comment : Référence de la vente
- Price : Prix en XOF

## 💡 Utilisation

1. **Upload de Fichier**
   - Cliquez sur le bouton de téléchargement
   - Sélectionnez votre fichier CSV

2. **Filtrage des Données**
   - Utilisez les filtres de date pour sélectionner une période spécifique
   - Filtrez par type de forfait
   - Définissez une plage de prix

3. **Analyse des Données**
   - Consultez les différents graphiques et visualisations
   - Analysez les tendances et patterns
   - Exportez les données si nécessaire

## 🔒 Sécurité
- Les fichiers uploadés sont stockés de manière sécurisée
- Validation des fichiers CSV
- Nettoyage des données avant traitement

## 🤝 Contribution
Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 License
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs
- [Sanlalex] - Développement initial

## 📧 Contact
Pour toute question ou suggestion, n'hésitez pas à nous contacter :
+226 73 38 39 40
