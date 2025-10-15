# streamlit_app.py
"""
Application Streamlit avec toutes les nouvelles fonctionnalités
Version complète avec ML, visualisations avancées et export PDF
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tempfile
import os

# Imports des modules de base
from football_recruitment_app import FootballRecruitmentAnalyzer

# 🆕 NOUVEAUX IMPORTS
from recommendation_system import PlayerRecommendationSystem
from advanced_visualizations import FootballVisualizer
from pdf_reports import ScoutingReportGenerator

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
    </style>
""", unsafe_allow_html=True)

# Initialisation
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = FootballRecruitmentAnalyzer()
    st.session_state.data_loaded = False
    st.session_state.recommender = None

# Titre
st.markdown('<h1 class="main-header">⚽ Football Recruitment Pro</h1>', 
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
    
    if st.button("📥 Charger les données", type="primary"):
        comp_id, season_id = competitions[selected_comp]
        
        with st.spinner("Chargement StatsBomb..."):
            try:
                df = st.session_state.analyzer.load_statsbomb_data(comp_id, season_id)
                if not df.empty:
                    st.session_state.player_stats = df
                    st.session_state.data_loaded = True
                    st.success(f"✅ {len(df)} joueurs chargés!")
                else:
                    st.error("❌ Erreur de chargement")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    # 🆕 NOUVEAU : Entraînement du système ML
    if st.session_state.data_loaded:
        st.markdown("---")
        st.subheader("2. Machine Learning")
        
        if st.button("🎓 Entraîner le système de recommandation"):
            with st.spinner("Entraînement du modèle..."):
                try:
                    df = st.session_state.player_stats
                    recommender = PlayerRecommendationSystem()
                    
                    features = [
                        'goals_per_90', 'assists_per_90', 'passes_per_90',
                        'pass_completion_rate', 'tackles_per_90', 
                        'interceptions_per_90', 'dribbles_per_90'
                    ]
                    
                    recommender.fit(df, features)
                    st.session_state.recommender = recommender
                    st.success("✅ Système prêt!")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        
        if st.session_state.recommender:
            st.info("🤖 Système ML actif")
    
    st.markdown("---")
    st.subheader("3. Filtrage")
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
    st.stop()

df = st.session_state.player_stats

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Vue d'ensemble",
    "🔍 Joueurs similaires",
    "🎯 Clustering",
    "📈 Profils détaillés",
    "🤖 Recommandations",  # 🆕 NOUVEAU
    "📄 Export PDF"  # 🆕 NOUVEAU
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
        st.metric("Matchs", int(df['matches_played'].sum()))
    with col4:
        st.metric("Buts", int(df['goals'].sum()))
    
    st.markdown("---")
    
    # Top scoreurs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥇 Top 10 Buteurs")
        top_scorers = df.nlargest(10, 'goals_per_90')[['player', 'team', 'goals_per_90']]
        
        fig = px.bar(
            top_scorers,
            x='goals_per_90',
            y='player',
            orientation='h',
            title='Buts par 90 minutes',
            color='goals_per_90',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top 10 Passeurs")
        top_assists = df.nlargest(10, 'assists_per_90')[['player', 'team', 'assists_per_90']]
        
        fig = px.bar(
            top_assists,
            x='assists_per_90',
            y='player',
            orientation='h',
            title='Passes décisives par 90 min',
            color='assists_per_90',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

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
            
            # 🆕 NOUVELLES VISUALISATIONS
            st.markdown("---")
            st.subheader("🎨 Visualisations Avancées")
            
            viz = FootballVisualizer()
            player_data = df[df['player'] == selected_player].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Radar Chart"):
                    metrics = [
                        'goals_per_90', 'assists_per_90', 'passes_per_90',
                        'tackles_per_90', 'dribbles_per_90'
                    ]
                    fig = viz.create_radar_chart(player_data, metrics, selected_player, df.mean())
                    st.pyplot(fig)
            
            with col2:
                if st.button("📈 Classement"):
                    metric = st.selectbox("Métrique", ['goals_per_90', 'assists_per_90'])
                    fig = viz.create_ranking_chart(df, metric, top_n=15)
                    st.pyplot(fig)

# ==================== TAB 5: RECOMMANDATIONS (NOUVEAU) ====================
with tab5:
    st.header("🤖 Système de Recommandation Intelligent")
    
    if not st.session_state.recommender:
        st.warning("⚠️ Veuillez d'abord entraîner le système via la sidebar")
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
                        st.success(f"✅ {len(recs)} joueurs trouvés")
                        st.dataframe(recs[['player', 'team', 'match_score', 'goals_per_90', 'assists_per_90']])
                    else:
                        st.warning("Aucun résultat")
        
        with col2:
            st.subheader("Recherche de remplaçant")
            player_to_replace = st.selectbox("Joueur à remplacer", df['player'].unique())
            upgrade = st.slider("Facteur d'amélioration", 1.0, 1.5, 1.1, 0.1)
            
            if st.button("🔄 Trouver des remplaçants"):
                with st.spinner("Recherche..."):
                    recs = st.session_state.recommender.recommend_replacement(
                        player_to_replace,
                        df,
                        top_n=10,
                        upgrade_factor=upgrade
                    )
                    
                    if not recs.empty:
                        st.success(f"✅ {len(recs)} candidats trouvés")
                        st.dataframe(recs[['player', 'team', 'match_score']])
                    else:
                        st.warning("Aucun résultat")

# ==================== TAB 6: EXPORT PDF (NOUVEAU) ====================
with tab6:
    st.header("📄 Générer un rapport PDF")
    
    player_pdf = st.selectbox(
        "Sélectionnez un joueur",
        df['player'].unique(),
        key='pdf_select'
    )
    
    club_name = st.text_input("Nom du club", "Football Club")
    
    if st.button("📥 Générer le rapport PDF", type="primary"):
        with st.spinner("Génération du rapport en cours..."):
            try:
                # Données
                player_data = df[df['player'] == player_pdf].iloc[0]
                
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
                
                visualizations = {
                    'radar': viz.create_radar_chart(
                        player_data,
                        metrics,
                        player_pdf,
                        df.mean()
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
                
                st.success("✅ Rapport généré avec succès!")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {e}")
                st.info("💡 Astuce: Vérifiez que toutes les données sont disponibles")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>🔥 Football Recruitment Pro | 💻 Propulsé par StatsBomb & ML</p>
    </div>
""", unsafe_allow_html=True)
