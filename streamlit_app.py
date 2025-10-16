# streamlit_app.py
"""
Application Streamlit - Football Recruitment Pro
Version ULTRA : 100+ métriques disponibles
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tempfile
import os

# Imports des modules
from football_recruitment_app import FootballRecruitmentAnalyzer
from recommendation_system import PlayerRecommendationSystem
from advanced_visualizations import FootballVisualizer
from pdf_reports import ScoutingReportGenerator
from advanced_ml_system import AdvancedPlayerAnalyzer

# Configuration
st.set_page_config(
    page_title="Football Recruitment Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .ultra-badge {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.8em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialisation
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = FootballRecruitmentAnalyzer()
    st.session_state.data_loaded = False
    st.session_state.recommender = None
    st.session_state.advanced_analyzer = None
    st.session_state.advanced_trained = False
    st.session_state.ultra_mode = False

# Titre
st.markdown('<h1 class="main-header">⚽ Football Recruitment Pro</h1>', 
           unsafe_allow_html=True)

# Badge MODE ULTRA si activé
if st.session_state.get('ultra_mode', False):
    st.markdown('<div style="text-align: center;"><span class="ultra-badge">🚀 MODE ULTRA ACTIVÉ - 100+ MÉTRIQUES</span></div>', 
               unsafe_allow_html=True)

st.markdown("---")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Sélection compétition
    st.subheader("1. Données")
    
    competitions = {
        "La Liga 2020/21": (11, 90),
        "Premier League 2015/16": (2, 27),
        "UEFA Euro 2020": (55, 43),
        "Women's World Cup 2019": (72, 30)
    }
    
    selected_comp = st.selectbox("Compétition", list(competitions.keys()))
    
    # 🆕 NOUVEAU : Choix du mode ULTRA
    ultra_mode = st.checkbox(
        "🚀 Mode ULTRA (100+ métriques)", 
        value=st.session_state.get('ultra_mode', False),
        help="Active l'extraction de TOUTES les données disponibles. Plus lent mais beaucoup plus précis !"
    )
    
    if ultra_mode:
        st.info("""
        **Mode ULTRA activé** :
        - ✅ 100+ métriques au lieu de 35
        - ✅ Analyse tactique détaillée
        - ✅ Heatmaps de position
        - ✅ Profil de pressing
        - ⏳ Temps de chargement : ~30-60 sec
        """)
    
    if st.button("📥 Charger les données", type="primary"):
        comp_id, season_id = competitions[selected_comp]
        
        loading_text = "Chargement ULTRA..." if ultra_mode else "Chargement..."
        with st.spinner(loading_text):
            try:
                if ultra_mode:
                    # MODE ULTRA
                    df = st.session_state.analyzer.load_statsbomb_data_ultra(comp_id, season_id)
                    if not df.empty:
                        st.session_state.player_stats = df
                        st.session_state.data_loaded = True
                        st.session_state.ultra_mode = True
                        st.success(f"✅ {len(df)} joueurs chargés en MODE ULTRA!")
                        st.info(f"📊 {len(df.columns)} features disponibles (+{len(df.columns) - 35} vs mode normal)")
                else:
                    # MODE NORMAL
                    df = st.session_state.analyzer.load_statsbomb_data(comp_id, season_id)
                    if not df.empty:
                        st.session_state.player_stats = df
                        st.session_state.data_loaded = True
                        st.session_state.ultra_mode = False
                        st.success(f"✅ {len(df)} joueurs chargés!")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    # Entraînement ML basique
    if st.session_state.data_loaded:
        st.markdown("---")
        st.subheader("2. Machine Learning")
        
        if st.button("🎓 Entraîner le système de recommandation"):
            with st.spinner("Entraînement..."):
                try:
                    df = st.session_state.player_stats
                    recommender = PlayerRecommendationSystem()
                    
                    features = [
                        'goals_per_90', 'assists_per_90', 'passes_per_90',
                        'pass_completion_rate', 'tackles_per_90', 
                        'interceptions_per_90', 'dribbles_per_90'
                    ]
                    
                    # Filtrer les features qui existent
                    features = [f for f in features if f in df.columns]
                    
                    recommender.fit(df, features)
                    st.session_state.recommender = recommender
                    st.success("✅ Système prêt!")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        
        if st.session_state.recommender:
            st.info("🤖 Système ML actif")
        
        # ML Avancé
        st.markdown("---")
        st.subheader("3. ML Avancé 🧠")
        
        if st.button("🚀 Activer le système ML avancé"):
            with st.spinner("Entraînement ML avancé..."):
                try:
                    df = st.session_state.player_stats
                    advanced = AdvancedPlayerAnalyzer()
                    
                    base_features = [
                        'goals_per_90', 'assists_per_90', 'passes_per_90',
                        'pass_completion_rate', 'tackles_per_90', 
                        'interceptions_per_90', 'dribbles_per_90',
                        'shots_per_90', 'xG_per_90'
                    ]
                    
                    # Filtrer les features disponibles
                    base_features = [f for f in base_features if f in df.columns]
                    
                    success = advanced.fit(df, base_features)
                    
                    if success:
                        st.session_state.advanced_analyzer = advanced
                        st.session_state.advanced_trained = True
                        st.success("✅ ML avancé activé!")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        
        if st.session_state.advanced_trained:
            st.info("🧠 ML Avancé actif")
    
    st.markdown("---")
    st.subheader("4. Filtrage")
    position = st.selectbox(
        "Position",
        ["all", "forward", "midfielder", "defender"],
        format_func=lambda x: {
            "all": "Toutes",
            "forward": "Attaquant",
            "midfielder": "Milieu",
            "defender": "Défenseur"
        }[x]
    )

# ==================== CONTENU PRINCIPAL ====================

if not st.session_state.data_loaded:
    st.warning("⚠️ Veuillez charger des données via la sidebar")
    
    # Instructions
    st.markdown("""
    ### 📖 Guide de démarrage rapide
    
    1. **Sélectionnez une compétition** dans la sidebar
    2. **Choisissez le mode** :
       - ⚡ **Mode Normal** : Rapide, 35 métriques
       - 🚀 **Mode ULTRA** : Complet, 100+ métriques
    3. **Cliquez sur "Charger les données"**
    4. Explorez les onglets d'analyse !
    
    ### 🆕 Mode ULTRA
    Le Mode ULTRA exploite **100+ métriques** :
    - Heatmaps de position (9 zones)
    - Profil de pressing détaillé
    - Analyse de progression
    - Types de passes/tirs/duels
    - Distances parcourues ballon au pied
    - Et bien plus !
    """)
    st.stop()

df = st.session_state.player_stats

# Afficher le nombre de features
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.metric("📊 Features disponibles", len(df.columns))
with col2:
    mode_label = "ULTRA 🚀" if st.session_state.get('ultra_mode', False) else "Normal"
    st.metric("Mode", mode_label)
with col3:
    st.metric("Joueurs", len(df))

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Vue d'ensemble",
    "🔍 Joueurs similaires",
    "🎯 Clustering",
    "📈 Profils détaillés",
    "🧠 ML Avancé",
    "🤖 Recommandations",
    "📄 Export PDF"
])

# ==================== TAB 1: VUE D'ENSEMBLE ====================
with tab1:
    st.header("📊 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Joueurs", len(df))
    with col2:
        st.metric("Équipes", df['team'].nunique())
    with col3:
        if 'matches_played' in df.columns:
            st.metric("Matchs", int(df['matches_played'].sum()))
    with col4:
        if 'goals' in df.columns:
            st.metric("Buts", int(df['goals'].sum()))
    
    st.markdown("---")
    
    # Top scoreurs
    col1, col2 = st.columns(2)
    
    with col1:
        if 'goals_per_90' in df.columns:
            st.subheader("🥇 Top 10 Buteurs")
            top_scorers = df.nlargest(10, 'goals_per_90')[['player', 'team', 'goals_per_90']]
            
            fig = px.bar(
                top_scorers,
                x='goals_per_90',
                y='player',
                orientation='h',
                title='Buts par match',
                color='goals_per_90',
                color_continuous_scale='Blues'
            )
            st.caption("*Moyenne de buts par match")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'assists_per_90' in df.columns:
            st.subheader("🎯 Top 10 Passeurs")
            top_assists = df.nlargest(10, 'assists_per_90')[['player', 'team', 'assists_per_90']]
            
            fig = px.bar(
                top_assists,
                x='assists_per_90',
                y='player',
                orientation='h',
                title='Passes décisives par match',
                color='assists_per_90',
                color_continuous_scale='Greens'
            )
            st.caption("*Moyenne de passes décisives par match")
            st.plotly_chart(fig, use_container_width=True)
    
    # 🆕 NOUVEAU : Métriques ULTRA si disponibles
    if st.session_state.get('ultra_mode', False):
        st.markdown("---")
        st.subheader("🚀 Métriques ULTRA disponibles")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📍 Position**")
            if 'zone_att_left' in df.columns:
                st.success("✅ Heatmaps 9 zones")
            if 'touches_in_box' in df.columns:
                st.success("✅ Touches en surface")
        
        with col2:
            st.markdown("**💪 Pressing**")
            if 'pressures' in df.columns:
                st.success("✅ Pressions totales")
            if 'pressures_attacking_third' in df.columns:
                st.success("✅ Pressing haut")
        
        with col3:
            st.markdown("**🏃 Progression**")
            if 'progressive_passes' in df.columns:
                st.success("✅ Passes progressives")
            if 'carry_distance' in df.columns:
                st.success("✅ Distance de carry")

# ==================== TAB 2: JOUEURS SIMILAIRES ====================
with tab2:
    st.header("🔍 Recherche de joueurs similaires")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        target_player = st.selectbox("Joueur", sorted(df['player'].unique()))
    with col2:
        n_similar = st.slider("Nombre", 3, 20, 10)
    
    if st.button("🔎 Rechercher", type="primary"):
        with st.spinner("Recherche..."):
            try:
                similar = st.session_state.analyzer.find_similar_players(
                    target_player,
                    top_n=n_similar,
                    position=position
                )
                
                st.success(f"✅ Trouvé {len(similar)} joueurs similaires")
                
                # Graphique
                fig = px.bar(
                    similar,
                    x='similarity_score',
                    y='player',
                    orientation='h',
                    title='Score de similarité',
                    color='similarity_score',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau
                st.dataframe(similar, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

# ==================== TAB 3: CLUSTERING ====================
with tab3:
    st.header("🎯 Clustering de joueurs")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        n_clusters = st.slider("Clusters", 2, 10, 5)
        
        if st.button("🎲 Créer les clusters"):
            with st.spinner("Création..."):
                try:
                    clustered_df, kmeans = st.session_state.analyzer.cluster_players(
                        n_clusters=n_clusters,
                        position=position
                    )
                    st.session_state.clustered_df = clustered_df
                    st.success("✅ Clusters créés!")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
    
    if 'clustered_df' in st.session_state:
        clustered_df = st.session_state.clustered_df
        
        # Distribution
        cluster_counts = clustered_df['cluster'].value_counts()
        
        fig = px.bar(
            x=cluster_counts.index,
            y=cluster_counts.values,
            labels={'x': 'Cluster', 'y': 'Nombre'},
            title='Répartition des clusters',
            color=cluster_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Joueurs par cluster
        selected_cluster = st.selectbox("Cluster", sorted(clustered_df['cluster'].unique()))
        cluster_players = clustered_df[clustered_df['cluster'] == selected_cluster]
        st.dataframe(cluster_players[['player', 'team', 'matches_played']])

# ==================== TAB 4: PROFILS DÉTAILLÉS ====================
with tab4:
    st.header("📈 Profils détaillés")
    
    selected_player = st.selectbox(
        "Joueur",
        sorted(df['player'].unique()),
        key='profile_player'
    )
    
    if selected_player:
        report = st.session_state.analyzer.create_scouting_report(selected_player)
        
        if "error" not in report:
            # Informations
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Joueur", report["Informations"]["Joueur"])
            with col2:
                st.metric("Équipe", report["Informations"]["Équipe"])
            with col3:
                st.metric("Matchs", report["Informations"]["Matchs joués"])
            
            st.markdown("---")
            
            # Stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("⚽ Offensif")
                for k, v in report["Statistiques offensives"].items():
                    st.metric(k, v)
            
            with col2:
                st.subheader("🎨 Création")
                for k, v in report["Statistiques de création"].items():
                    st.metric(k, v)
            
            with col3:
                st.subheader("🛡️ Défensif")
                for k, v in report["Statistiques défensives"].items():
                    st.metric(k, v)
            
            # 🆕 NOUVEAU : Métriques ULTRA
            if st.session_state.get('ultra_mode', False):
                st.markdown("---")
                st.subheader("🚀 Métriques ULTRA")
                
                player_data = df[df['player'] == selected_player].iloc[0]
                
                # Heatmap de position
                if 'zone_att_left' in df.columns:
                    st.markdown("### 🗺️ Heatmap de position")
                    
                    zones = [
                        [player_data.get('zone_def_left', 0), 
                         player_data.get('zone_def_center', 0), 
                         player_data.get('zone_def_right', 0)],
                        [player_data.get('zone_mid_left', 0), 
                         player_data.get('zone_mid_center', 0), 
                         player_data.get('zone_mid_right', 0)],
                        [player_data.get('zone_att_left', 0), 
                         player_data.get('zone_att_center', 0), 
                         player_data.get('zone_att_right', 0)]
                    ]
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=zones,
                        x=['Gauche', 'Centre', 'Droite'],
                        y=['Défense', 'Milieu', 'Attaque'],
                        colorscale='Hot'
                    ))
                    
                    fig.update_layout(
                        title=f'Zones d\'activité - {selected_player}',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Profil de pressing
                if 'pressures' in df.columns:
                    st.markdown("### 💪 Profil de pressing")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Pressions totales",
                            int(player_data.get('pressures', 0))
                        )
                    
                    with col2:
                        st.metric(
                            "Pressions hautes",
                            int(player_data.get('pressures_attacking_third', 0))
                        )
                    
                    with col3:
                        pressing_score = (
                            player_data.get('pressures_attacking_third', 0) * 1.5 +
                            player_data.get('ball_recoveries_offensive_third', 0) * 2.0
                        )
                        
                        if pressing_score > 50:
                            st.success("🔥 Presseur intensif")
                        elif pressing_score > 25:
                            st.info("✅ Pressing modéré")
                        else:
                            st.warning("⚠️ Peu de pressing")
                
                # Progression
                if 'progressive_passes' in df.columns:
                    st.markdown("### 📈 Capacité de progression")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Passes progressives",
                            int(player_data.get('progressive_passes', 0))
                        )
                        
                        st.metric(
                            "Distance progressive",
                            f"{player_data.get('progressive_distance', 0):.1f}m"
                        )
                    
                    with col2:
                        st.metric(
                            "Carries progressifs",
                            int(player_data.get('progressive_carries', 0))
                        )
                        
                        st.metric(
                            "Distance de carry",
                            f"{player_data.get('carry_distance', 0):.1f}m"
                        )

# ==================== TAB 5: ML AVANCÉ (NOUVEAU) ====================
with tab5:
    st.header("🧠 Système ML Avancé")
    
    if not st.session_state.advanced_trained:
        st.warning("⚠️ Activez d'abord le système ML avancé via la sidebar")
    else:
        advanced = st.session_state.advanced_analyzer
        
        # Sous-tabs
        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "🔎 Recherche Avancée",
            "🎨 Profil Personnalisé",
            "🔮 Prédiction",
            "⚽ Style de Jeu"
        ])
        
        # SUBTAB 1: Recherche Avancée
        with subtab1:
            st.subheader("🔎 Recherche similaires (Algorithme avancé)")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                target_player = st.selectbox(
                    "Joueur cible",
                    sorted(df['player'].unique()),
                    key='advanced_search_player'
                )
            
            with col2:
                top_n = st.slider("Résultats", 5, 20, 10, key='advanced_n')
            
            if st.button("🔍 Rechercher (ML Avancé)", type="primary"):
                with st.spinner("Analyse en cours..."):
                    results = advanced.find_similar_players_advanced(
                        target_player,
                        df,
                        top_n=top_n
                    )
                    
                    if not results.empty:
                        st.success(f"✅ {len(results)} joueurs trouvés")
                        
                        # Graphique
                        fig = px.bar(
                            results.head(10),
                            x='similarity_score',
                            y='player',
                            orientation='h',
                            title='Score de similarité (Algorithme combiné)',
                            color='similarity_score',
                            color_continuous_scale='Viridis',
                            text='similarity_score'
                        )
                        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tableau
                        st.dataframe(results, use_container_width=True)
                    else:
                        st.warning("Aucun résultat")
        
        # SUBTAB 2: Profil Personnalisé
        with subtab2:
            st.subheader("🎨 Recherche par profil personnalisé")
            st.info("💡 Définissez les caractéristiques idéales que vous recherchez")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**⚽ Offensif**")
                target_goals = st.slider("Buts/90", 0.0, 2.0, 0.5, 0.1)
                target_assists = st.slider("Passes décisives/90", 0.0, 1.0, 0.3, 0.1)
                target_shots = st.slider("Tirs/90", 0.0, 5.0, 2.0, 0.5)
            
            with col2:
                st.markdown("**🎨 Création**")
                target_passes = st.slider("Passes/90", 0.0, 100.0, 50.0, 5.0)
                target_pass_rate = st.slider("% Passes réussies", 0.0, 100.0, 80.0, 5.0)
                target_dribbles = st.slider("Dribbles/90", 0.0, 10.0, 3.0, 0.5)
            
            with col3:
                st.markdown("**🛡️ Défensif**")
                target_tackles = st.slider("Tacles/90", 0.0, 5.0, 2.0, 0.5)
                target_interceptions = st.slider("Interceptions/90", 0.0, 3.0, 1.0, 0.5)
            
            tolerance = st.slider(
                "Tolérance",
                0.0, 0.5, 0.2, 0.05,
                help="Plus élevé = recherche plus flexible"
            )
            
            if st.button("🎯 Trouver des joueurs", type="primary"):
                with st.spinner("Recherche..."):
                    target_profile = {
                        'goals_per_90': target_goals,
                        'assists_per_90': target_assists,
                        'shots_per_90': target_shots,
                        'passes_per_90': target_passes,
                        'pass_completion_rate': target_pass_rate,
                        'dribbles_per_90': target_dribbles,
                        'tackles_per_90': target_tackles,
                        'interceptions_per_90': target_interceptions
                    }
                    
                    results = advanced.find_by_profile(
                        target_profile,
                        df,
                        top_n=15,
                        tolerance=tolerance
                    )
                    
                    if not results.empty:
                        st.success(f"✅ {len(results)} joueurs correspondent")
                        
                        # Scatter
                        if 'goals_per_90' in results.columns and 'assists_per_90' in results.columns:
                            fig = px.scatter(
                                results.head(10),
                                x='goals_per_90',
                                y='assists_per_90',
                                size='match_score',
                                color='match_score',
                                hover_data=['player', 'team'],
                                title='Joueurs correspondants',
                                color_continuous_scale='Plasma'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.dataframe(results, use_container_width=True)
                    else:
                        st.warning("Aucun résultat. Augmentez la tolérance.")
        
        # SUBTAB 3: Prédiction
        with subtab3:
            st.subheader("🔮 Prédiction de performance")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                predict_player = st.selectbox(
                    "Joueur",
                    sorted(df['player'].unique()),
                    key='predict_player'
                )
            
            with col2:
                months = st.slider("Mois à prédire", 3, 24, 6, 3)
            
            if st.button("🔮 Prédire", type="primary"):
                with st.spinner("Calcul..."):
                    prediction = advanced.predict_future_performance(
                        predict_player,
                        df,
                        months_ahead=months
                    )
                    
                    if 'error' not in prediction:
                        st.success("✅ Prédiction calculée")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Actuel",
                                f"{prediction['current_goals_per_90']:.3f}"
                            )
                        
                        with col2:
                            delta = prediction['predicted_goals_per_90'] - prediction['current_goals_per_90']
                            st.metric(
                                "Prédiction",
                                f"{prediction['predicted_goals_per_90']:.3f}",
                                f"{delta:+.3f}"
                            )
                        
                        with col3:
                            future_delta = prediction['future_prediction'] - prediction['current_goals_per_90']
                            st.metric(
                                f"Dans {months} mois",
                                f"{prediction['future_prediction']:.3f}",
                                f"{future_delta:+.3f}"
                            )
                        
                        with col4:
                            st.metric(
                                "Confiance",
                                f"{prediction['confidence']}%"
                            )
                        
                        # Graphique tendance
                        trend_data = pd.DataFrame({
                            'Période': ['Actuel', 'Prédiction', f'{months} mois'],
                            'Buts/90': [
                                prediction['current_goals_per_90'],
                                prediction['predicted_goals_per_90'],
                                prediction['future_prediction']
                            ]
                        })
                        
                        fig = px.line(
                            trend_data,
                            x='Période',
                            y='Buts/90',
                            markers=True,
                            title=f'Évolution prédite - {predict_player}',
                            line_shape='spline'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if prediction['trend'] == 'positive':
                            st.success("📈 Tendance positive")
                        else:
                            st.warning("📉 Tendance négative")
                    else:
                        st.error(f"❌ {prediction['error']}")
        
        # SUBTAB 4: Style de jeu
        with subtab4:
            st.subheader("⚽ Identification du style")
            
            style_player = st.selectbox(
                "Joueur",
                sorted(df['player'].unique()),
                key='style_player'
            )
            
            if st.button("🎯 Analyser le style", type="primary"):
                with st.spinner("Analyse..."):
                    style = advanced.identify_playing_style(style_player, df)
                    
                    if 'error' not in style:
                        st.success(f"✅ Style identifié")
                        
                        st.markdown(f"### 🎯 Style: **{style['primary_style']}**")
                        
                        st.markdown("**Caractéristiques:**")
                        for s in style['all_styles']:
                            st.markdown(f"- {s}")
                        
                        st.markdown("---")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("⚽ Offensif", f"{style['offensive_rating']:.1f}/10")
                        with col2:
                            st.metric("🛡️ Défensif", f"{style['defensive_rating']:.1f}/10")
                        with col3:
                            st.metric("🎨 Créatif", f"{style['creativity_rating']:.1f}/10")
                        
                        # Radar
                        fig = go.Figure(data=go.Scatterpolar(
                            r=[
                                style['offensive_rating'],
                                style['defensive_rating'],
                                style['creativity_rating']
                            ],
                            theta=['Offensif', 'Défensif', 'Créatif'],
                            fill='toself',
                            name=style_player
                        ))
                        
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                            title=f"Profil - {style_player}",
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"❌ {style['error']}")

# ==================== TAB 6: RECOMMANDATIONS ====================
with tab6:
    st.header("🤖 Système de Recommandation")
    
    if not st.session_state.recommender:
        st.warning("⚠️ Entraînez d'abord le système via la sidebar")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Par rôle tactique")
            role = st.selectbox(
                "Rôle",
                ['playmaker', 'target_man', 'winger', 'box_to_box', 'ball_winner', 'sweeper'],
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            if st.button("🔍 Rechercher par rôle"):
                with st.spinner("Recherche..."):
                    recs = st.session_state.recommender.recommend_by_role(role, df, top_n=10)
                    
                    if not recs.empty:
                        st.success(f"✅ {len(recs)} joueurs")
                        display_cols = ['player', 'team', 'match_score']
                        if 'goals_per_90' in recs.columns:
                            display_cols.extend(['goals_per_90', 'assists_per_90'])
                        st.dataframe(recs[display_cols], use_container_width=True)
                    else:
                        st.warning("Aucun résultat")
        
        with col2:
            st.subheader("Remplaçant")
            player_to_replace = st.selectbox("Joueur à remplacer", df['player'].unique())
            upgrade = st.slider("Facteur d'amélioration", 1.0, 1.5, 1.1, 0.1)
            
            if st.button("🔄 Trouver remplaçants"):
                with st.spinner("Recherche..."):
                    recs = st.session_state.recommender.recommend_replacement(
                        player_to_replace,
                        df,
                        top_n=10,
                        upgrade_factor=upgrade
                    )
                    
                    if not recs.empty:
                        st.success(f"✅ {len(recs)} candidats")
                        st.dataframe(recs[['player', 'team', 'match_score']], use_container_width=True)
                    else:
                        st.warning("Aucun résultat")

# ==================== TAB 7: EXPORT PDF ====================
with tab7:
    st.header("📄 Générer un rapport PDF")
    
    player_pdf = st.selectbox(
        "Sélectionnez un joueur",
        df['player'].unique(),
        key='pdf_select'
    )
    
    club_name = st.text_input("Nom du club", "Football Club")
    
    if st.button("📥 Générer le rapport PDF", type="primary"):
        with st.spinner("Génération..."):
            try:
                # ✅ CORRECTION: Filtrer uniquement les colonnes valides
                player_data = df[df['player'] == player_pdf].iloc[0]
                
                # Vérifier que player_data ne contient que des valeurs valides
                # Exclure les colonnes textuelles problématiques
                valid_cols = player_data.index.difference(['player', 'team'])
                player_data_clean = player_data[valid_cols]
                
                # Joueurs similaires
                similar = st.session_state.analyzer.find_similar_players(
                    player_pdf,
                    top_n=5,
                    position='all'
                )
                
                # Visualisations
                viz = FootballVisualizer()
                metrics = ['goals_per_90', 'assists_per_90', 'passes_per_90', 
                          'tackles_per_90', 'dribbles_per_90']
                
                # Moyenne uniquement des colonnes numériques
                numeric_metrics = [m for m in metrics if m in df.columns]
                
                visualizations = {
                    'radar': viz.create_radar_chart(
                        player_data,
                        numeric_metrics,
                        player_pdf,
                        df[numeric_metrics].mean()
                    )
                }
                
                # Générer PDF
                generator = ScoutingReportGenerator(club_name=club_name)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    generator.generate_player_report(
                        player_data,
                        similar,
                        visualizations,
                        tmp.name
                    )
                    
                    # Téléchargement
                    with open(tmp.name, 'rb') as f:
                        st.download_button(
                            label="📥 Télécharger le rapport PDF",
                            data=f,
                            file_name=f"rapport_{player_pdf.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    os.unlink(tmp.name)
                
                st.success("✅ Rapport généré!")
                
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
                st.info("💡 Vérifiez que les données du joueur sont complètes")
# Je les omets pour la longueur, mais gardez le code de la version précédente

with tab5:
    st.header("🧠 ML Avancé")
    st.info("Voir le code complet de la version précédente pour ce tab")

with tab6:
    st.header("🤖 Recommandations")
    st.info("Voir le code complet de la version précédente pour ce tab")

with tab7:
    st.header("📄 Export PDF")
    st.info("Voir le code complet de la version précédente pour ce tab")

# Footer
st.markdown("---")
footer_text = "🔥 Football Recruitment Pro"
if st.session_state.get('ultra_mode', False):
    footer_text += " | 🚀 MODE ULTRA ACTIVÉ"
footer_text += " | 💻 Propulsé par StatsBomb & ML"

st.markdown(f"""
    <div style='text-align: center; color: gray;'>
        <p>{footer_text}</p>
    </div>
""", unsafe_allow_html=True)
