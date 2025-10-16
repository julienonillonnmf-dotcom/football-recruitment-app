# streamlit_app.py
"""
Application Streamlit - Système de Recrutement Football
Version COMPLÈTE avec Mode ULTRA et visualisations avancées
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

# Imports des modules
from football_recruitment_app import FootballRecruitmentAnalyzer
from recommendation_system import PlayerRecommendationSystem
from advanced_visualizations import AdvancedPlayerVisualizations

# 🎨 CONFIGURATION PAGE
st.set_page_config(
    page_title="⚽ Football Recruitment Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CSS PERSONNALISÉ
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    h1 {
        color: #ff4b4b;
        padding-bottom: 10px;
        border-bottom: 3px solid #ff4b4b;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff4b4b;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 🔧 INITIALISATION
@st.cache_resource
def init_analyzer():
    """Initialise l'analyseur (en cache)"""
    return FootballRecruitmentAnalyzer()

@st.cache_resource
def init_recommender():
    """Initialise le système de recommandation (en cache)"""
    return PlayerRecommendationSystem()

@st.cache_resource
def init_visualizer():
    """Initialise le système de visualisation (en cache)"""
    return AdvancedPlayerVisualizations()

# Initialiser dans session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = init_analyzer()
    st.session_state.data_loaded = False
    st.session_state.recommender = None
    st.session_state.player_stats = None
    st.session_state.visualizer = init_visualizer()

analyzer = st.session_state.analyzer

# 📊 HEADER
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <h1 style='text-align: center;'>
            ⚽ Football Recruitment Pro
        </h1>
        <p style='text-align: center; color: gray; font-size: 14px;'>
            Analyse avancée et recrutement intelligent avec IA & Machine Learning
        </p>
    """, unsafe_allow_html=True)

st.markdown("---")

# 🎛️ SIDEBAR - CONFIGURATION
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Choix de la compétition
    competitions = {
        "La Liga 2020/21": (11, 90),
        "Premier League 2020/21": (9, 42),
        "UEFA Euro 2020": (55, 43),
        "Champions League 2020/21": (16, 41),
        "World Cup 2022": (43, 106),
        "Ligue 1 2020/21": (7, 33),
        "Serie A 2020/21": (12, 27),
        "Bundesliga 2020/21": (8, 28),
        "World Cup 2018": (43, 3),
        "FA Women's Super League 2020/21": (37, 42),
    }
    
    competition_choice = st.selectbox(
        "🏆 Compétition",
        options=list(competitions.keys()),
        help="Sélectionnez la compétition à analyser"
    )
    
    competition_id, season_id = competitions[competition_choice]
    
    # 🆕 MODE ULTRA
    st.markdown("---")
    st.markdown("### 🚀 Mode Extraction")
    
    ultra_mode = st.checkbox(
        "⚡ **Activer Mode ULTRA**",
        value=False,
        help="Active l'extraction de 100+ métriques (plus long mais plus complet)"
    )
    
    if ultra_mode:
        st.info("🔥 Mode ULTRA activé : 100+ métriques seront extraites")
        st.warning("⏳ Temps de chargement : ~30-60 secondes")
    else:
        st.info("⚡ Mode Normal : 40 métriques (rapide)")
    
    st.markdown("---")
    
    # Bouton de chargement
    load_button = st.button("📥 Charger les Données", type="primary", use_container_width=True)
    
    if load_button:
        with st.spinner(f"{'🚀 Chargement ULTRA' if ultra_mode else '📊 Chargement'} des données..."):
            try:
                if ultra_mode:
                    df = analyzer.load_statsbomb_data_ultra(competition_id, season_id)
                else:
                    df = analyzer.load_statsbomb_data(competition_id, season_id)
                
                if not df.empty:
                    st.session_state.player_stats = df
                    st.session_state.data_loaded = True
                    st.success(f"✅ {len(df)} joueurs chargés!")
                    st.rerun()
                else:
                    st.error("❌ Aucune donnée chargée")
                    
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    
    # Infos sur les données
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown("### 📊 Données Chargées")
        df = st.session_state.player_stats
        st.metric("Joueurs", len(df))
        st.metric("Features", len(df.columns))
        st.metric("Matchs", df['matches_played'].sum() if 'matches_played' in df.columns else 0)
        
        # Bouton pour réinitialiser
        if st.button("🔄 Recharger", use_container_width=True):
            st.session_state.data_loaded = False
            st.session_state.player_stats = None
            st.session_state.recommender = None
            st.rerun()

# 📊 CONTENU PRINCIPAL
if not st.session_state.data_loaded:
    # 🎯 PAGE D'ACCUEIL
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2>👈 Commencez par charger des données</h2>
            <p style='font-size: 18px; color: gray;'>
                Sélectionnez une compétition dans la barre latérale et cliquez sur "Charger les Données"
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Fonctionnalités
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='metric-card'>
                <h3>📊 Analyse Avancée</h3>
                <p>Statistiques détaillées avec 40-100+ métriques par joueur</p>
                <ul style='text-align: left; margin-top: 10px;'>
                    <li>Mode Normal : 40 métriques</li>
                    <li>Mode ULTRA : 100+ métriques</li>
                    <li>Données StatsBomb</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='metric-card'>
                <h3>🤖 IA & Machine Learning</h3>
                <p>Recommandations intelligentes basées sur le ML</p>
                <ul style='text-align: left; margin-top: 10px;'>
                    <li>Recherche de similaires</li>
                    <li>Recommandations par rôle</li>
                    <li>Prédictions de performance</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class='metric-card'>
                <h3>📈 Visualisations</h3>
                <p>Graphiques interactifs et profils détaillés</p>
                <ul style='text-align: left; margin-top: 10px;'>
                    <li>Profils complets 6-en-1</li>
                    <li>Heatmaps de position</li>
                    <li>Comparaisons multi-joueurs</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Guide rapide
    with st.expander("📖 Guide de démarrage rapide"):
        st.markdown("""
        ### Comment utiliser l'application ?
        
        1. **Sélectionnez une compétition** dans la barre latérale
        2. **Choisissez le mode** : Normal (rapide) ou ULTRA (complet)
        3. **Cliquez sur "Charger les Données"**
        4. **Explorez les 5 onglets** :
           - 📊 Vue d'ensemble : Top joueurs et statistiques globales
           - 🔍 Recherche Similaires : Trouvez des profils comparables
           - 🎯 Recommandations IA : Suggestions intelligentes
           - 👤 Profil Détaillé : Analyse complète d'un joueur
           - 📋 Export : Téléchargez vos données
        """)
    
    st.stop()

# 📊 DONNÉES CHARGÉES - AFFICHAGE PRINCIPAL
df = st.session_state.player_stats

# 🎯 TABS PRINCIPALES
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Vue d'ensemble",
    "🔍 Recherche Similaires",
    "🎯 Recommandations IA",
    "👤 Profil Joueur Détaillé",
    "📋 Rapports & Export"
])

# ============================================
# TAB 1 : VUE D'ENSEMBLE
# ============================================
with tab1:
    st.header("📊 Vue d'Ensemble de la Compétition")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Joueurs",
            len(df),
            help="Nombre total de joueurs analysés"
        )
    
    with col2:
        total_goals = df['goals'].sum() if 'goals' in df.columns else 0
        st.metric(
            "⚽ Buts Totaux",
            int(total_goals),
            help="Total des buts marqués"
        )
    
    with col3:
        avg_pass_rate = df['pass_completion_rate'].mean() if 'pass_completion_rate' in df.columns else 0
        st.metric(
            "🎯 Taux Passe Moyen",
            f"{avg_pass_rate:.1f}%",
            help="Précision moyenne des passes"
        )
    
    with col4:
        features_count = len(df.columns)
        mode = "ULTRA 🚀" if features_count > 50 else "Normal ⚡"
        st.metric(
            "📊 Mode",
            mode,
            f"{features_count} features"
        )
    
    st.markdown("---")
    
    # Graphiques TOP JOUEURS
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥇 Top 10 Buteurs")
        if 'goals_per_90' in df.columns:
            top_scorers = df.nlargest(10, 'goals_per_90')[['player', 'team', 'goals_per_90', 'matches_played']]
            
            fig = px.bar(
                top_scorers,
                x='goals_per_90',
                y='player',
                orientation='h',
                title='Buts par 90 minutes',
                color='goals_per_90',
                color_continuous_scale='Reds',
                text='goals_per_90',
                hover_data=['team', 'matches_played']
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(showlegend=False, height=400, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de buts non disponibles")
    
    with col2:
        st.subheader("🎯 Top 10 Passeurs")
        if 'assists_per_90' in df.columns:
            top_assists = df.nlargest(10, 'assists_per_90')[['player', 'team', 'assists_per_90', 'matches_played']]
            
            fig = px.bar(
                top_assists,
                x='assists_per_90',
                y='player',
                orientation='h',
                title='Assists par 90 minutes',
                color='assists_per_90',
                color_continuous_scale='Blues',
                text='assists_per_90',
                hover_data=['team', 'matches_played']
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(showlegend=False, height=400, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données d'assists non disponibles")
    
    # Graphiques additionnels
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribution xG")
        if 'xG_per_90' in df.columns:
            fig = px.histogram(
                df[df['xG_per_90'] > 0],
                x='xG_per_90',
                nbins=30,
                title='Distribution des Expected Goals par 90min',
                labels={'xG_per_90': 'xG/90', 'count': 'Nombre de joueurs'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données xG non disponibles")
    
    with col2:
        st.subheader("🎯 Précision des passes")
        if 'pass_completion_rate' in df.columns:
            fig = px.box(
                df[df['pass_completion_rate'] > 0],
                y='pass_completion_rate',
                title='Distribution du taux de réussite des passes',
                labels={'pass_completion_rate': 'Taux de réussite (%)'},
                color_discrete_sequence=['#4ECDC4']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de passes non disponibles")
    
    # Scatter plot interactif
    st.markdown("---")
    st.subheader("🎨 Analyse Comparative Interactive")
    
    col1, col2, col3 = st.columns(3)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    with col1:
        x_axis = st.selectbox(
            "Axe X",
            options=numeric_cols,
            index=numeric_cols.index('goals_per_90') if 'goals_per_90' in numeric_cols else 0
        )
    
    with col2:
        y_axis = st.selectbox(
            "Axe Y",
            options=numeric_cols,
            index=numeric_cols.index('assists_per_90') if 'assists_per_90' in numeric_cols else 1
        )
    
    with col3:
        size_by = st.selectbox(
            "Taille des bulles",
            options=['matches_played'] + numeric_cols,
            index=0
        )
    
    # Créer le scatter plot
    if x_axis and y_axis:
        plot_df = df[[x_axis, y_axis, size_by, 'player', 'team']].dropna()
        
        fig = px.scatter(
            plot_df,
            x=x_axis,
            y=y_axis,
            size=size_by,
            hover_data=['player', 'team'],
            title=f'{y_axis} vs {x_axis}',
            color=y_axis,
            color_continuous_scale='Viridis',
            size_max=20
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau complet
    st.markdown("---")
    st.subheader("📋 Tableau Complet des Joueurs")
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_player = st.text_input("🔍 Rechercher un joueur", "")
    
    with col2:
        if 'team' in df.columns:
            teams = ['Toutes'] + sorted(df['team'].unique().tolist())
            team_filter = st.selectbox("👕 Équipe", teams)
        else:
            team_filter = 'Toutes'
    
    with col3:
        min_matches = st.slider(
            "Matchs minimum",
            0,
            int(df['matches_played'].max()) if 'matches_played' in df.columns else 10,
            5
        )
    
    with col4:
        available_sort_cols = [col for col in ['goals_per_90', 'assists_per_90', 'xG_per_90', 'passes_per_90', 'tackles_per_90'] if col in df.columns]
        if available_sort_cols:
            sort_by = st.selectbox("Trier par", available_sort_cols)
        else:
            sort_by = df.columns[0]
    
    # Filtrer données
    filtered_df = df.copy()
    
    if search_player:
        filtered_df = filtered_df[filtered_df['player'].str.contains(search_player, case=False, na=False)]
    
    if team_filter != 'Toutes' and 'team' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['team'] == team_filter]
    
    if 'matches_played' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['matches_played'] >= min_matches]
    
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(sort_by, ascending=False)
    
    # Colonnes à afficher
    display_cols = ['player', 'team', 'matches_played']
    available_stats = ['goals_per_90', 'assists_per_90', 'xG_per_90', 'passes_per_90', 
                       'pass_completion_rate', 'tackles_per_90', 'dribbles_per_90',
                       'shots_per_90', 'key_passes_per_90', 'interceptions_per_90']
    display_cols.extend([col for col in available_stats if col in filtered_df.columns])
    
    st.info(f"📊 {len(filtered_df)} joueurs correspondent aux filtres")
    
    st.dataframe(
        filtered_df[display_cols].head(100),
        use_container_width=True,
        height=400
    )

# ============================================
# TAB 2 : RECHERCHE SIMILAIRES
# ============================================
with tab2:
    st.header("🔍 Recherche de Joueurs Similaires")
    
    st.markdown("""
        Trouvez des joueurs avec un profil statistique similaire en utilisant la similarité cosinus
        sur les métriques clés de performance.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_player = st.selectbox(
            "👤 Sélectionnez un joueur de référence",
            options=sorted(df['player'].unique()),
            help="Choisissez le joueur de référence pour la comparaison"
        )
    
    with col2:
        position_filter = st.selectbox(
            "⚽ Filtrer par position",
            ['all', 'forward', 'midfielder', 'defender'],
            format_func=lambda x: {
                'all': '🌐 Toutes positions',
                'forward': '⚡ Attaquant',
                'midfielder': '🎯 Milieu',
                'defender': '🛡️ Défenseur'
            }[x]
        )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        top_n = st.slider("Nombre de résultats", 5, 20, 10)
    
    if st.button("🔎 Trouver des joueurs similaires", type="primary", use_container_width=True):
        with st.spinner("🔍 Recherche en cours..."):
            try:
                similar = analyzer.find_similar_players(
                    target_player=selected_player,
                    top_n=top_n,
                    position=position_filter
                )
                
                if not similar.empty:
                    st.success(f"✅ {len(similar)} joueurs similaires trouvés!")
                    
                    # Afficher le joueur de référence
                    st.markdown("---")
                    ref_player = df[df['player'] == selected_player].iloc[0]
                    
                    st.markdown(f"### 📌 Joueur de référence : **{selected_player}**")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Équipe", ref_player['team'])
                    with col2:
                        st.metric("Matchs", int(ref_player['matches_played']) if 'matches_played' in ref_player.index else 'N/A')
                    with col3:
                        st.metric("Buts/90", f"{ref_player['goals_per_90']:.2f}" if 'goals_per_90' in ref_player.index else 'N/A')
                    with col4:
                        st.metric("Assists/90", f"{ref_player['assists_per_90']:.2f}" if 'assists_per_90' in ref_player.index else 'N/A')
                    
                    st.markdown("---")
                    st.subheader(f"🎯 Joueurs similaires à {selected_player}")
                    
                    # Graphique de similarité
                    fig = px.bar(
                        similar,
                        x='similarity_score',
                        y='player',
                        orientation='h',
                        title='Score de Similarité (%)',
                        color='similarity_score',
                        color_continuous_scale='Viridis',
                        text='similarity_score',
                        hover_data=['team', 'matches_played']
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tableau détaillé
                    st.markdown("### 📊 Comparaison Détaillée")
                    
                    # Sélectionner colonnes pertinentes
                    compare_cols = ['player', 'team', 'similarity_score', 'matches_played']
                    stat_cols = ['goals_per_90', 'assists_per_90', 'passes_per_90', 'tackles_per_90', 'dribbles_per_90']
                    compare_cols.extend([col for col in stat_cols if col in similar.columns])
                    
                    st.dataframe(
                        similar[compare_cols].style.background_gradient(subset=['similarity_score'], cmap='RdYlGn'),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Comparaison radar
                    if len(similar) >= 3:
                        st.markdown("---")
                        st.subheader("📊 Comparaison Radar - Top 3")
                        
                        # Sélectionner les 3 premiers + le joueur de référence
                        top_3_similar = similar.head(3)
                        players_to_compare = [selected_player] + top_3_similar['player'].tolist()[:3]
                        
                        try:
                            fig_comparison = st.session_state.visualizer.create_comparison_chart(
                                df,
                                players_to_compare,
                                metrics=['goals_per_90', 'assists_per_90', 'passes_per_90', 
                                        'tackles_per_90', 'dribbles_per_90']
                            )
                            st.pyplot(fig_comparison)
                        except Exception as e:
                            st.warning(f"Impossible de créer le graphique de comparaison: {e}")
                
                else:
                    st.warning("Aucun joueur similaire trouvé avec ces critères")
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
                import traceback
                with st.expander("Détails de l'erreur"):
                    st.code(traceback.format_exc())

# ============================================
# TAB 3 : RECOMMANDATIONS IA
# ============================================
with tab3:
    st.header("🤖 Recommandations Intelligentes (IA)")
    
    st.markdown("""
        Système de recommandation basé sur le Machine Learning utilisant :
        - **K-Nearest Neighbors** pour la recherche de profils similaires
        - **Random Forest** pour la prédiction de performance
        - **Cosine Similarity** pour le matching de profils
    """)
    
    # Entraîner le modèle si pas déjà fait
    if st.session_state.recommender is None:
        with st.spinner("🧠 Entraînement du modèle IA..."):
            try:
                recommender = init_recommender()
                features = analyzer.select_features('all')
                recommender.fit(df, features)
                st.session_state.recommender = recommender
                st.success("✅ Modèle IA entraîné avec succès!")
            except Exception as e:
                st.error(f"❌ Erreur entraînement: {e}")
                st.stop()
    
    recommender = st.session_state.recommender
    
    st.markdown("---")
    
    # Options de recommandation
    reco_type = st.radio(
        "🎯 Type de recommandation",
        ["Par Profil Personnalisé", "Par Rôle Tactique", "Remplacement de Joueur"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if reco_type == "Par Profil Personnalisé":
        st.subheader("🎯 Définissez votre profil idéal")
        
        st.markdown("Ajustez les curseurs pour définir le profil recherché")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**⚽ Attaque**")
            goals_target = st.slider("Buts/90", 0.0, 2.0, 0.5, 0.1)
            shots_target = st.slider("Tirs/90", 0.0, 10.0, 3.0, 0.5)
            xg_target = st.slider("xG/90", 0.0, 1.5, 0.4, 0.1)
        
        with col2:
            st.markdown("**🎯 Création**")
            assists_target = st.slider("Assists/90", 0.0, 1.0, 0.3, 0.1)
            passes_target = st.slider("Passes/90", 0.0, 100.0, 50.0, 5.0)
            pass_rate_target = st.slider("Taux Passe %", 0.0, 100.0, 85.0, 5.0)
        
        with col3:
            st.markdown("**🛡️ Défense**")
            tackles_target = st.slider("Tacles/90", 0.0, 10.0, 2.0, 0.5)
            interceptions_target = st.slider("Interceptions/90", 0.0, 5.0, 1.0, 0.5)
            dribbles_target = st.slider("Dribbles/90", 0.0, 10.0, 2.0, 0.5)
        
        profile = {
            'goals_per_90': goals_target,
            'shots_per_90': shots_target,
            'xG_per_90': xg_target,
            'assists_per_90': assists_target,
            'passes_per_90': passes_target,
            'pass_completion_rate': pass_rate_target,
            'tackles_per_90': tackles_target,
            'interceptions_per_90': interceptions_target,
            'dribbles_per_90': dribbles_target
        }
        
        # Filtres additionnels
        st.markdown("---")
        st.markdown("**Filtres additionnels**")
        
        col1, col2 = st.columns(2)
        with col1:
            use_filters = st.checkbox("Activer les filtres")
        with col2:
            results_count = st.slider("Nombre de résultats", 5, 20, 10)
        
        filters = None
        if use_filters:
            col1, col2 = st.columns(2)
            with col1:
                min_matches_filter = st.number_input("Matchs minimum", 0, 50, 5)
            with col2:
                if 'age' in df.columns:
                    max_age_filter = st.number_input("Âge maximum", 18, 40, 30)
                    filters = {'min_matches': min_matches_filter, 'max_age': max_age_filter}
                else:
                    filters = {'min_matches': min_matches_filter}
        
        if st.button("🎯 Trouver les joueurs correspondants", type="primary", use_container_width=True):
            with st.spinner("🤖 Recherche IA en cours..."):
                results = recommender.recommend_by_profile(profile, df, top_n=results_count, filters=filters)
                
                if not results.empty:
                    st.success(f"✅ {len(results)} joueurs trouvés!")
                    
                    # Graphique
                    fig = px.bar(
                        results.head(15),
                        x='match_score',
                        y='player',
                        orientation='h',
                        title='Score de Correspondance au Profil (%)',
                        color='match_score',
                        color_continuous_scale='RdYlGn',
                        text='match_score',
                        hover_data=['team', 'matches_played']
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tableau
                    st.dataframe(
                        results.style.background_gradient(subset=['match_score'], cmap='RdYlGn'),
                        use_container_width=True,
                        height=400
                    )
                else:
                    st.warning("Aucun joueur ne correspond à ce profil")
    
    elif reco_type == "Par Rôle Tactique":
        st.subheader("⚽ Sélectionnez un rôle tactique")
        
        st.markdown("Le système recommandera les joueurs les plus adaptés au rôle sélectionné")
        
        roles = {
            'box_to_box': {
                'name': '🏃 Box-to-Box',
                'desc': 'Milieu complet qui couvre tout le terrain',
                'stats': '50 passes/90 · 85% précision · 2.5 tacles · 0.15 buts'
            },
            'playmaker': {
                'name': '🎯 Playmaker',
                'desc': 'Créateur de jeu, distribution et passes clés',
                'stats': '70 passes/90 · 90% précision · 3 passes clés · 0.3 assists'
            },
            'target_man': {
                'name': '🎯 Pivot',
                'desc': 'Attaquant de surface, finition',
                'stats': '0.6 buts/90 · 3.5 tirs · 45% précision tirs'
            },
            'winger': {
                'name': '⚡ Ailier',
                'desc': 'Vitesse, dribbles et percussion',
                'stats': '0.4 buts · 0.4 assists · 4 dribbles · 60% réussite'
            },
            'ball_winner': {
                'name': '🛡️ Récupérateur',
                'desc': 'Milieu défensif, récupération de balle',
                'stats': '4 tacles/90 · 2.5 interceptions'
            },
            'sweeper': {
                'name': '🧹 Libéro',
                'desc': 'Défenseur relanceur',
                'stats': '60 passes/90 · 88% précision · 3 dégagements · 2 interceptions'
            }
        }
        
        # Afficher les rôles sous forme de cartes
        cols = st.columns(3)
        role_choice = None
        
        for idx, (role_key, role_info) in enumerate(roles.items()):
            col = cols[idx % 3]
            with col:
                with st.container():
                    st.markdown(f"""
                        <div class='stat-box'>
                            <h4>{role_info['name']}</h4>
                            <p style='font-size: 14px;'>{role_info['desc']}</p>
                            <p style='font-size: 12px; color: gray; margin-top: 10px;'>{role_info['stats']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Sélectionner", key=f"role_{role_key}", use_container_width=True):
                        role_choice = role_key
        
        if role_choice is None:
            role_choice = st.selectbox(
                "Ou sélectionnez via le menu",
                options=list(roles.keys()),
                format_func=lambda x: roles[x]['name']
            )
        
        results_count = st.slider("Nombre de résultats", 5, 20, 10, key='role_results')
        
        if st.button("🔎 Trouver des joueurs pour ce rôle", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Recherche de {roles[role_choice]['name']}..."):
                results = recommender.recommend_by_role(role_choice, df, top_n=results_count)
                
                if not results.empty:
                    st.success(f"✅ {len(results)} joueurs trouvés pour le rôle {roles[role_choice]['name']}!")
                    
                    # Info sur le rôle
                    st.info(f"**{roles[role_choice]['name']}** : {roles[role_choice]['desc']}")
                    
                    # Graphique
                    fig = px.bar(
                        results.head(15),
                        x='match_score',
                        y='player',
                        orientation='h',
                        title=f'Meilleurs joueurs pour : {roles[role_choice]["name"]}',
                        color='match_score',
                        color_continuous_scale='Plasma',
                        text='match_score',
                        hover_data=['team', 'matches_played']
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tableau
                    st.dataframe(
                        results.style.background_gradient(subset=['match_score'], cmap='Plasma'),
                        use_container_width=True,
                        height=400
                    )
                else:
                    st.warning(f"Aucun joueur trouvé pour le rôle {roles[role_choice]['name']}")
    
    else:  # Remplacement
        st.subheader("🔄 Trouver un remplaçant")
        
        st.markdown("""
            Trouvez le meilleur remplaçant pour un joueur qui quitte votre effectif.
            Vous pouvez également demander un profil amélioré (upgrade) ou similaire.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            departing = st.selectbox(
                "👤 Joueur à remplacer",
                options=sorted(df['player'].unique())
            )
            
            # Afficher les stats du joueur sortant
            if departing:
                departing_data = df[df['player'] == departing].iloc[0]
                st.markdown("**Stats du joueur sortant:**")
                
                stats_to_show = {
                    'goals_per_90': 'Buts/90',
                    'assists_per_90': 'Assists/90',
                    'passes_per_90': 'Passes/90',
                    'tackles_per_90': 'Tacles/90'
                }
                
                for col_name, label in stats_to_show.items():
                    if col_name in departing_data.index:
                        st.metric(label, f"{departing_data[col_name]:.2f}")
        
        with col2:
            upgrade = st.slider(
                "⚡ Facteur d'amélioration",
                0.8, 1.5, 1.0, 0.1,
                help="1.0 = profil identique\n>1.0 = meilleur joueur\n<1.0 = profil inférieur"
            )
            
            if upgrade > 1.0:
                st.info(f"🔥 Recherche d'un joueur {(upgrade-1)*100:.0f}% meilleur")
            elif upgrade < 1.0:
                st.info(f"💰 Recherche d'un profil {(1-upgrade)*100:.0f}% moins performant")
            else:
                st.info("🎯 Recherche d'un profil identique")
            
            results_count = st.slider("Nombre de résultats", 5, 20, 10, key='replacement_results')
        
        if st.button("🔍 Trouver des remplaçants", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Recherche de remplaçants pour {departing}..."):
                results = recommender.recommend_replacement(
                    departing, df, top_n=results_count, upgrade_factor=upgrade
                )
                
                if not results.empty:
                    st.success(f"✅ {len(results)} remplaçants potentiels trouvés!")
                    
                    # Graphique
                    fig = px.bar(
                        results.head(15),
                        x='match_score',
                        y='player',
                        orientation='h',
                        title=f'Remplaçants pour {departing} (facteur {upgrade}x)',
                        color='match_score',
                        color_continuous_scale='Turbo',
                        text='match_score',
                        hover_data=['team', 'matches_played']
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparaison avec le joueur sortant
                    st.markdown("---")
                    st.subheader("📊 Comparaison avec le joueur sortant")
                    
                    # Top 3 remplaçants
                    top_3 = results.head(3)
                    
                    comparison_metrics = ['goals_per_90', 'assists_per_90', 'passes_per_90', 'tackles_per_90']
                    available_metrics = [m for m in comparison_metrics if m in df.columns]
                    
                    if available_metrics:
                        # Créer graphique de comparaison
                        comparison_data = []
                        
                        # Données du joueur sortant
                        for metric in available_metrics:
                            if metric in departing_data.index:
                                comparison_data.append({
                                    'Joueur': departing,
                                    'Métrique': metric,
                                    'Valeur': float(departing_data[metric]),
                                    'Type': 'Sortant'
                                })
                        
                        # Données des remplaçants
                        for _, player_row in top_3.iterrows():
                            for metric in available_metrics:
                                if metric in player_row.index:
                                    comparison_data.append({
                                        'Joueur': player_row['player'],
                                        'Métrique': metric,
                                        'Valeur': float(player_row[metric]),
                                        'Type': 'Remplaçant'
                                    })
                        
                        comp_df = pd.DataFrame(comparison_data)
                        
                        fig = px.bar(
                            comp_df,
                            x='Métrique',
                            y='Valeur',
                            color='Joueur',
                            barmode='group',
                            title='Comparaison des Statistiques Clés'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Tableau complet
                    st.dataframe(
                        results.style.background_gradient(subset=['match_score'], cmap='Turbo'),
                        use_container_width=True,
                        height=400
                    )
                else:
                    st.warning(f"Aucun remplaçant trouvé pour {departing}")

# ============================================
# TAB 4 : PROFIL JOUEUR DÉTAILLÉ
# ============================================
with tab4:
    st.header("👤 Profil Joueur Détaillé")
    
    st.markdown("""
        Analyse complète d'un joueur avec visualisations avancées :
        radar chart, heatmap, comparaisons et statistiques détaillées.
    """)
    
    st.markdown("---")
    
    player_profile = st.selectbox(
        "🔍 Sélectionnez un joueur",
        options=sorted(df['player'].unique()),
        key='profile_player'
    )
    
    if not player_profile:
        st.info("Sélectionnez un joueur pour voir son profil détaillé")
        st.stop()
    
    player_data = df[df['player'] == player_profile].iloc[0]
    
    # Infos de base - Header
    st.markdown(f"## 📋 {player_profile}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 👕 Équipe")
        st.markdown(f"**{player_data['team']}**")
    
    with col2:
        if 'matches_played' in player_data.index:
            st.markdown("### ⚽ Matchs")
            st.markdown(f"**{int(player_data['matches_played'])}**")
    
    with col3:
        if 'goals' in player_data.index:
            st.markdown("### 🎯 Buts")
            st.markdown(f"**{int(player_data['goals'])}**")
    
    with col4:
        if 'assists' in player_data.index:
            st.markdown("### 🅰️ Assists")
            st.markdown(f"**{int(player_data['assists'])}**")
    
    st.markdown("---")
    
    # 🆕 PROFIL VISUEL COMPLET
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🎨 Profil Visuel Complet (6 graphiques)")
    
    with col2:
        generate_profile = st.button(
            "🎨 Générer Profil",
            type="primary",
            use_container_width=True
        )
    
    if generate_profile:
        with st.spinner("🎨 Création du profil détaillé (6 visualisations)..."):
            try:
                viz = st.session_state.visualizer
                
                fig = viz.create_complete_player_profile(
                    player_data=player_data,
                    league_data=df,
                    player_name=player_profile
                )
                
                st.pyplot(fig)
                st.success("✅ Profil visuel généré avec succès!")
                
                # Bouton de téléchargement
                st.download_button(
                    label="💾 Télécharger le profil (PNG)",
                    data="PNG not available in this format",
                    file_name=f"profil_{player_profile.replace(' ', '_')}.png",
                    mime="image/png",
                    help="Fonction de téléchargement à implémenter",
                    disabled=True
                )
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération du profil: {e}")
                with st.expander("🔍 Détails de l'erreur"):
                    import traceback
                    st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Stats détaillées par catégorie avec graphiques
    st.subheader("📊 Statistiques Détaillées par Catégorie")
    
    tab_att, tab_crea, tab_def, tab_phys = st.tabs([
        "⚽ Attaque",
        "🎯 Création",
        "🛡️ Défense",
        "🏃 Physique & Mobilité"
    ])
    
    with tab_att:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📈 Métriques")
            
            attack_metrics = [
                ('goals_per_90', 'Buts/90', '⚽'),
                ('xG_per_90', 'xG/90', '📊'),
                ('shots_per_90', 'Tirs/90', '🎯'),
                ('shots_on_target', 'Tirs cadrés', '🎯'),
                ('shot_accuracy', 'Précision (%)', '📈'),
                ('big_chances', 'Grosses occasions', '🔥'),
                ('shots_from_outside_box', 'Tirs extérieur', '💥'),
            ]
            
            for col_name, label, icon in attack_metrics:
                if col_name in player_data.index:
                    value = player_data[col_name]
                    if pd.notna(value):
                        st.metric(f"{icon} {label}", f"{float(value):.2f}")
        
        with col2:
            # Graphique de comparaison avec la ligue
            if 'goals_per_90' in player_data.index and 'goals_per_90' in df.columns:
                st.markdown("#### 📊 Position dans la ligue")
                
                metrics_to_plot = ['goals_per_90', 'xG_per_90', 'shots_per_90']
                available = [m for m in metrics_to_plot if m in player_data.index and m in df.columns]
                
                if available:
                    percentiles = []
                    labels = []
                    
                    for metric in available:
                        player_val = float(player_data[metric])
                        league_vals = df[metric].dropna()
                        
                        if len(league_vals) > 0:
                            perc = (league_vals < player_val).sum() / len(league_vals) * 100
                            percentiles.append(perc)
                            labels.append(metric.replace('_per_90', '/90').replace('_', ' ').title())
                    
                    if percentiles:
                        fig = go.Figure(data=[
                            go.Bar(
                                x=percentiles,
                                y=labels,
                                orientation='h',
                                marker=dict(
                                    color=percentiles,
                                    colorscale='RdYlGn',
                                    showscale=True
                                ),
                                text=[f"{p:.0f}%" for p in percentiles],
                                textposition='outside'
                            )
                        ])
                        
                        fig.update_layout(
                            title="Percentile vs Ligue",
                            xaxis_title="Percentile (%)",
                            height=300,
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
    
    with tab_crea:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📈 Métriques")
            
            creation_metrics = [
                ('assists_per_90', 'Assists/90', '🅰️'),
                ('xA_total', 'xA total', '📊'),
                ('key_passes_per_90', 'Passes clés/90', '🔑'),
                ('passes_per_90', 'Passes/90', '⚽'),
                ('pass_completion_rate', 'Taux passe (%)', '🎯'),
                ('progressive_passes', 'Passes prog.', '↗️'),
                ('crosses', 'Centres', '✈️'),
                ('through_balls', 'Passes en prof.', '🎯'),
            ]
            
            for col_name, label, icon in creation_metrics:
                if col_name in player_data.index:
                    value = player_data[col_name]
                    if pd.notna(value):
                        st.metric(f"{icon} {label}", f"{float(value):.2f}")
        
        with col2:
            # Graphique des types de passes
            if 'crosses' in player_data.index or 'through_balls' in player_data.index:
                st.markdown("#### 📊 Types de passes")
                
                pass_types = []
                pass_values = []
                
                type_map = {
                    'crosses': 'Centres',
                    'through_balls': 'En profondeur',
                    'progressive_passes': 'Progressives',
                    'long_passes': 'Longues',
                    'short_passes': 'Courtes'
                }
                
                for col, label in type_map.items():
                    if col in player_data.index:
                        val = player_data[col]
                        if pd.notna(val) and float(val) > 0:
                            pass_types.append(label)
                            pass_values.append(float(val))
                
                if pass_types:
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=pass_types,
                            values=pass_values,
                            hole=0.4,
                            marker=dict(colors=px.colors.qualitative.Set3)
                        )
                    ])
                    
                    fig.update_layout(
                        title="Distribution des Types de Passes",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab_def:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📈 Métriques")
            
            defense_metrics = [
                ('tackles_per_90', 'Tacles/90', '🛡️'),
                ('interceptions_per_90', 'Interceptions/90', '✋'),
                ('clearances_per_90', 'Dégagements/90', '⚽'),
                ('ball_recoveries', 'Récupérations', '🔄'),
                ('duels_won', 'Duels gagnés', '⚔️'),
                ('aerial_duels_won', 'Duels aériens', '🎈'),
                ('blocks', 'Blocages', '🚫'),
                ('errors', 'Erreurs', '❌'),
            ]
            
            for col_name, label, icon in defense_metrics:
                if col_name in player_data.index:
                    value = player_data[col_name]
                    if pd.notna(value):
                        st.metric(f"{icon} {label}", f"{float(value):.2f}")
        
        with col2:
            # Graphique récupérations par zone
            if 'ball_recoveries_defensive_third' in player_data.index:
                st.markdown("#### 📊 Récupérations par zone")
                
                zones = ['Défensif', 'Milieu', 'Offensif']
                values = []
                
                zone_cols = [
                    'ball_recoveries_defensive_third',
                    'ball_recoveries_middle_third',
                    'ball_recoveries_attacking_third'
                ]
                
                for col in zone_cols:
                    if col in player_data.index:
                        val = player_data[col]
                        values.append(float(val) if pd.notna(val) else 0)
                    else:
                        values.append(0)
                
                if sum(values) > 0:
                    fig = go.Figure(data=[
                        go.Bar(
                            x=zones,
                            y=values,
                            marker=dict(
                                color=['#e74c3c', '#f39c12', '#2ecc71']
                            ),
                            text=values,
                            textposition='outside'
                        )
                    ])
                    
                    fig.update_layout(
                        title="Récupérations de balle par zone",
                        yaxis_title="Nombre",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab_phys:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📈 Métriques")
            
            physical_metrics = [
                ('dribbles_per_90', 'Dribbles/90', '🏃'),
                ('dribbles_completed', 'Dribbles réussis', '✅'),
                ('dribble_success_rate', 'Taux réussite (%)', '📈'),
                ('carries', 'Courses balle au pied', '🏃'),
                ('carry_distance', 'Distance (m)', '📏'),
                ('progressive_carries', 'Carries progressifs', '↗️'),
                ('touches', 'Touches totales', '⚽'),
                ('touches_in_box', 'Touches dans surface', '🎯'),
            ]
            
            for col_name, label, icon in physical_metrics:
                if col_name in player_data.index:
                    value = player_data[col_name]
                    if pd.notna(value):
                        if 'distance' in col_name:
                            st.metric(f"{icon} {label}", f"{float(value):.0f}")
                        else:
                            st.metric(f"{icon} {label}", f"{float(value):.2f}")
        
        with col2:
            # Heatmap simplifié
            if any(f'zone_{z}' in player_data.index for z in ['att_left', 'att_center', 'att_right']):
                st.markdown("#### 🗺️ Heatmap d'activité")
                
                zones_data = []
                zone_names = ['att_left', 'att_center', 'att_right',
                             'mid_left', 'mid_center', 'mid_right',
                             'def_left', 'def_center', 'def_right']
                
                for zone in zone_names:
                    col_name = f'zone_{zone}'
                    if col_name in player_data.index:
                        val = player_data[col_name]
                        zones_data.append(float(val) if pd.notna(val) else 0)
                    else:
                        zones_data.append(0)
                
                if len(zones_data) == 9:
                    heatmap = np.array(zones_data).reshape(3, 3)
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=heatmap,
                        x=['Gauche', 'Centre', 'Droit'],
                        y=['Attaque', 'Milieu', 'Défense'],
                        colorscale='YlOrRd',
                        text=heatmap,
                        texttemplate='%{text:.0f}',
                        textfont={"size": 14}
                    ))
                    
                    fig.update_layout(
                        title="Zones d'activité sur le terrain",
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # Section comparaison avec d'autres joueurs
    st.markdown("---")
    st.subheader("🔀 Comparer avec d'autres joueurs")
    
    compare_players = st.multiselect(
        "Sélectionnez des joueurs à comparer",
        options=[p for p in sorted(df['player'].unique()) if p != player_profile],
        max_selections=3
    )
    
    if compare_players:
        players_to_compare = [player_profile] + compare_players
        
        try:
            viz = st.session_state.visualizer
            fig_comparison = viz.create_comparison_chart(
                df,
                players_to_compare,
                metrics=['goals_per_90', 'assists_per_90', 'passes_per_90',
                        'tackles_per_90', 'dribbles_per_90', 'xG_per_90']
            )
            st.pyplot(fig_comparison)
        except Exception as e:
            st.warning(f"Impossible de créer le graphique de comparaison: {e}")

# ============================================
# TAB 5 : RAPPORTS & EXPORT
# ============================================
with tab5:
    st.header("📋 Rapports & Export")
    
    st.markdown("""
        Exportez les données analysées dans différents formats pour vos propres analyses
        ou rapports de scouting.
    """)
    
    # Export CSV
    st.markdown("---")
    st.subheader("💾 Export CSV")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📥 Export complet**")
        st.markdown("Téléchargez toutes les données de la compétition")
        
        if st.button("📥 Télécharger CSV Complet", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Télécharger le fichier CSV",
                data=csv,
                file_name=f"football_data_{competition_choice.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        st.markdown("**🎯 Export sélectif**")
        st.markdown("Sélectionnez des joueurs spécifiques")
        
        selected_players_export = st.multiselect(
            "Joueurs à exporter",
            options=df['player'].unique(),
            help="Sélectionnez un ou plusieurs joueurs"
        )
        
        if selected_players_export:
            filtered_export = df[df['player'].isin(selected_players_export)]
            csv = filtered_export.to_csv(index=False)
            st.download_button(
                label=f"⬇️ Télécharger {len(selected_players_export)} joueur(s)",
                data=csv,
                file_name=f"selection_{len(selected_players_export)}_joueurs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Statistiques d'export
    st.subheader("📊 Résumé des Données")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Joueurs", len(df))
    with col2:
        st.metric("📈 Features", len(df.columns))
    with col3:
        st.metric("🏆 Compétition", competition_choice.split()[0])
    with col4:
        st.metric("📅 Date Export", datetime.now().strftime("%d/%m/%Y"))
    
    # Aperçu des colonnes disponibles
    st.markdown("---")
    st.subheader("📋 Colonnes Disponibles dans l'Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Métriques Principales**")
        main_cols = [col for col in df.columns if any(x in col for x in ['goals', 'assists', 'xG', 'passes', 'tackles'])]
        for col in main_cols[:15]:
            st.text(f"• {col}")
    
    with col2:
        st.markdown("**📊 Métriques Avancées**")
        if len(df.columns) > 50:
            st.success("🚀 Mode ULTRA - 100+ métriques disponibles")
            advanced_cols = [col for col in df.columns if any(x in col for x in ['progressive', 'carry', 'pressure', 'zone'])]
            for col in advanced_cols[:15]:
                st.text(f"• {col}")
        else:
            st.info("⚡ Mode Normal - 40 métriques disponibles")
    
    # Guide d'utilisation des données
    st.markdown("---")
    with st.expander("📖 Guide d'utilisation des données exportées"):
        st.markdown("""
        ### Comment utiliser les données exportées ?
        
        **Format CSV** :
        - Compatible avec Excel, Google Sheets, Python, R
        - Séparateur : virgule (,)
        - Encodage : UTF-8
        
        **Colonnes clés** :
        - `player` : Nom du joueur
        - `team` : Équipe
        - `matches_played` : Nombre de matchs
        - `*_per_90` : Métriques normalisées par 90 minutes
        - `xG`, `xA` : Expected Goals/Assists
        
        **Analyses suggérées** :
        1. Filtrer par position ou rôle
        2. Comparer avec des benchmarks
        3. Créer des visualisations personnalisées
        4. Intégrer dans vos outils de scouting
        
        **Outils recommandés** :
        - Excel/Google Sheets : Analyse basique
        - Python (Pandas) : Analyse avancée
        - Tableau/Power BI : Visualisations
        - R : Modélisation statistique
        """)

# 🎯 FOOTER
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p style='font-size: 16px;'>⚽ <strong>Football Recruitment Pro</strong> | 💻 Propulsé par StatsBomb & Machine Learning</p>
        <p style='font-size: 12px;'>Données : StatsBomb Open Data | Analyse : scikit-learn + Pandas | Visualisations : Plotly + Matplotlib</p>
        <p style='font-size: 11px; margin-top: 10px;'>
            Mode Normal : 40 features | Mode ULTRA : 100+ features | 
            ML : K-NN, Random Forest, Cosine Similarity
        </p>
    </div>
""", unsafe_allow_html=True)
