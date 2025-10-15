# ⚽ Football Recruitment Analyzer

Application d'analyse de recrutement football avec Machine Learning utilisant les données StatsBomb.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://votre-app.streamlit.app)

## 🎯 Fonctionnalités

- **Analyse de données** : Visualisation complète des statistiques de joueurs
- **Recherche de joueurs similaires** : Algorithme de similarité cosinus pour trouver des profils similaires
- **Clustering** : Regroupement automatique de joueurs par profils
- **Profils détaillés** : Rapports de scouting complets avec visualisations radar

## 📊 Sources de données

- **StatsBomb Open Data** : Données événementielles gratuites
- Métriques incluses : xG, passes, tirs, dribbles, statistiques défensives, etc.

## 🚀 Installation locale

```bash
# Cloner le repository
git clone https://github.com/votre-username/football-recruitment-app.git
cd football-recruitment-app

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run streamlit_app.py
```

L'application sera accessible sur `http://localhost:8501`

## 📦 Technologies utilisées

- **Python 3.9+**
- **Streamlit** : Interface utilisateur
- **scikit-learn** : Machine Learning
- **StatsBombPy** : Accès aux données
- **Plotly** : Visualisations interactives
- **Pandas** : Manipulation de données

## 📖 Utilisation

1. **Charger les données** : Sélectionnez une compétition dans la barre latérale
2. **Explorer** : Naviguez entre les différents onglets
3. **Analyser** : Utilisez les outils de recherche et clustering
4. **Exporter** : Visualisez et comparez les profils de joueurs

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📝 Licence

MIT License

## 🙏 Crédits

- **StatsBomb** pour les données gratuites
- **Streamlit** pour la plateforme de déploiement
- La communauté football analytics

## 📧 Contact

Pour toute question : [votre-email@example.com]

---

Développé avec ❤️ et ⚽ par [Votre Nom]
