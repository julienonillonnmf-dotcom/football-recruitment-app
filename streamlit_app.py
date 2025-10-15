# streamlit_app.py
"""
Interface Streamlit pour l'application de recrutement football
Lance avec: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from football_recruitment_app import FootballRecruitmentAnalyzer

# Configuration de la page
st.set_page_config(
    page_title="Football Recruitment Analyzer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Titre
st.markdown('<h1 class="main-header">⚽ Football Recruitment Analyzer</h1>', unsafe_allow_html=True)
st.markdown("---")

# Initialiser l'analyseur dans session_state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = FootballRecruitmentAnalyzer()
    st.session_state.data_loaded = False

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Sélection de la compétition
    st.subheader("1. Sélection des données")
    
    competitions = {
        "La Liga 2020/21": (11, 90),
        "Premier League 2015/16": (2, 27),
        "UEFA Euro 2020": (55, 43),
        "Women's World Cup 2019": (72, 30)
    }
    
    selected_comp = st.selectbox(
        "Compétition",
        list(competitions.keys())
    )
    
    if st.button("📥 Charger les données", type="primary"):
        comp_id, season_id = competitions[selected_comp]
        
        with st.spinner("Chargement des données StatsBomb..."):
            try:
                df = st.session_state.analyzer.load_statsbomb_data(comp_id, season_id)
                if not df.empty:
                    st.session_state.player_stats = df
                    st.session_state.data_loaded = True
                    st.success(f"✅ {len(df)} joueurs chargés!")
                else:
                    st.error("❌ Erreur lors du chargement")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    st.markdown("---")
    
    # Sélection de la position
    st.subheader("2. Filtrage")
    position = st.selectbox(
        "Position",
        ["all", "forward", "midfielder", "defender"],
        format_func=lambda x: {
            "all": "Toutes positions",
            "forward": "Attaquant",
            "midfielder": "Milieu",
            "defender": "Défenseur"
        }[x]
    )
    
    st.markdown("---")
    st.info("💡 **Astuce**: Chargez d'abord les données, puis explorez les différents onglets.")

# Vérifier si les données sont chargées
if not st.session_state.data_loaded:
    st.warning("⚠️ Veuillez charger des données via la barre latérale pour commencer.")
    st.stop()

df = st.session_state.player_stats

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue d'ensemble", 
    "🔍 Recherche de joueurs similaires", 
    "🎯 Clustering", 
    "📈 Profils détaillés"
])

# TAB 1: Vue d'ensemble
with tab1:
    st.header("📊 Vue d'ensemble des données")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Nombre de joueurs", len(df))
    with col2:
        st.metric("Équipes", df['team'].nunique())
    with col3:
        st.metric("Total matchs", df['matches_played'].sum())
    with col4:
        st.metric("Total buts", int(df['goals'].sum()))
    
    st.markdown("---")
    
    # Top scoreurs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥇 Top 10 Buteurs")
        top_scorers = df.nlargest(10, 'goals_per_90')[['player', 'team', 'goals_per_90', 'xG_per_90']]
        
        fig = px.bar(
            top_scorers, 
            x='goals_per_90', 
            y='player',
            color='goals_per_90',
            orientation='h',
            title='Buts par 90 minutes',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top 10 Passeurs")
        top_assisters = df.nlargest(10, 'assists_per_90')[['player', 'team', 'assists_per_90', 'key_passes_per_90']]
        
        fig = px.bar(
            top_assisters, 
            x='assists_per_90', 
            y='player',
            color='assists_per_90',
            orientation='h',
            title='Assists par 90 minutes',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot xG vs Goals
    st.subheader("📈 xG vs Buts réels (par 90 min)")
    
    fig = px.scatter(
        df,
        x='xG_per_90',
        y='goals_per_90',
        size='shots_per_90',
        color='team',
        hover_name='player',
        hover_data=['team', 'matches_played'],
        title='Expected Goals vs Buts réels',
        labels={'xG_per_90': 'xG par 90min', 'goals_per_90': 'Buts par 90min'}
    )
    
    # Ajouter la ligne x=y
    max_val = max(df['xG_per_90'].max(), df['goals_per_90'].max())
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode='lines',
        name='xG = Buts',
        line=dict(color='red', dash='dash')
    ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des données
    st.subheader("📋 Données complètes")
    st.dataframe(
        df[['player', 'team', 'matches_played', 'goals_per_90', 'xG_per_90', 
            'assists_per_90', 'passes_per_90', 'pass_completion_rate']].sort_values('goals_per_90', ascending=False),
        use_container_width=True
    )

# TAB 2: Recherche de joueurs similaires
with tab2:
    st.header("🔍 Recherche de joueurs similaires")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        target_player = st.selectbox(
            "Sélectionnez un joueur",
            sorted(df['player'].unique())
        )
    
    with col2:
        n_similar = st.slider("Nombre de résultats", 3, 20, 10)
    
    if st.button("🔎 Rechercher", type="primary"):
        with st.spinner("Recherche en cours..."):
            try:
                similar_players = st.session_state.analyzer.find_similar_players(
                    target_player, 
                    top_n=n_similar,
                    position=position
                )
                
                st.success(f"✅ Trouvé {len(similar_players)} joueurs similaires à **{target_player}**")
                
                # Afficher les résultats
                st.subheader("Résultats")
                
                # Créer un graphique de similarité
                fig = px.bar(
                    similar_players,
                    x='similarity_score',
                    y='player',
                    orientation='h',
                    title='Score de similarité',
                    color='similarity_score',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau détaillé
                st.dataframe(similar_players, use_container_width=True)
                
                # Comparaison radar
                st.subheader("📊 Comparaison des profils")
                
                features = st.session_state.analyzer.select_features(position)
                
                # Sélectionner quelques joueurs pour la comparaison
                compare_players = st.multiselect(
                    "Sélectionnez des joueurs à comparer",
                    similar_players['player'].tolist()[:5],
                    default=similar_players['player'].tolist()[:3]
                )
                
                if compare_players:
                    # Créer le radar chart avec Plotly
                    fig = go.Figure()
                    
                    for player in [target_player] + compare_players:
                        player_data = df[df['player'] == player]
                        if not player_data.empty:
                            values = []
                            for feature in features:
                                col_min = df[feature].min()
                                col_max = df[feature].max()
                                normalized = ((player_data[feature].values[0] - col_min) / (col_max - col_min)) * 100
                                values.append(normalized)
                            
                            fig.add_trace(go.Scatterpolar(
                                r=values,
                                theta=features,
                                fill='toself',
                                name=player
                            ))
                    
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=True,
                        title="Comparaison des profils (normalisé 0-100)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

# TAB 3: Clustering
with tab3:
    st.header("🎯 Clustering de joueurs")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        n_clusters = st.slider("Nombre de clusters", 2, 10, 5)
        
        if st.button("🎲 Créer les clusters", type="primary"):
            with st.spinner("Création des clusters..."):
                try:
                    clustered_df, kmeans = st.session_state.analyzer.cluster_players(
                        n_clusters=n_clusters,
                        position=position
                    )
                    st.session_state.clustered_df = clustered_df
                    st.success("✅ Clusters créés!")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
    
    if 'clustered_df' in st.session_state:
        clustered_df = st.session_state.clustered_df
        
        # Distribution des clusters
        st.subheader("📊 Distribution des clusters")
        cluster_counts = clustered_df['cluster'].value_counts().sort_index()
        
        fig = px.bar(
            x=cluster_counts.index,
            y=cluster_counts.values,
            labels={'x': 'Cluster', 'y': 'Nombre de joueurs'},
            title='Répartition des joueurs par cluster',
            color=cluster_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Visualisation 2D avec PCA
        st.subheader("🗺️ Visualisation des clusters (PCA)")
        
        from sklearn.decomposition import PCA
        
        features = st.session_state.analyzer.select_features(position)
        X = clustered_df[features].values
        
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(st.session_state.analyzer.scaler.fit_transform(X))
        
        clustered_df['PC1'] = X_pca[:, 0]
        clustered_df['PC2'] = X_pca[:, 1]
        
        fig = px.scatter(
            clustered_df,
            x='PC1',
            y='PC2',
            color='cluster',
            hover_name='player',
            hover_data=['team', 'matches_played'],
            title=f'Clusters de joueurs (Variance expliquée: {pca.explained_variance_ratio_.sum():.2%})',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques par cluster
        st.subheader("📈 Statistiques moyennes par cluster")
        
        cluster_stats = clustered_df.groupby('cluster')[features].mean()
        
        fig = px.imshow(
            cluster_stats.T,
            labels=dict(x="Cluster", y="Métrique", color="Valeur"),
            title="Heatmap des caractéristiques moyennes par cluster",
            color_continuous_scale='RdYlGn',
            aspect='auto'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Joueurs par cluster
        st.subheader("👥 Joueurs par cluster")
        selected_cluster = st.selectbox("Sélectionnez un cluster", sorted(clustered_df['cluster'].unique()))
        
        cluster_players = clustered_df[clustered_df['cluster'] == selected_cluster][
            ['player', 'team', 'matches_played'] + features
        ].sort_values('matches_played', ascending=False)
        
        st.dataframe(cluster_players, use_container_width=True)

# TAB 4: Profils détaillés
with tab4:
    st.header("📈 Profils détaillés des joueurs")
    
    selected_player = st.selectbox(
        "Sélectionnez un joueur pour voir son profil complet",
        sorted(df['player'].unique()),
        key='profile_player'
    )
    
    if selected_player:
        # Créer le rapport de scouting
        report = st.session_state.analyzer.create_scouting_report(selected_player)
        
        if "error" not in report:
            # Afficher les informations de base
            st.subheader("ℹ️ Informations générales")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Joueur", report["Informations"]["Joueur"])
            with col2:
                st.metric("Équipe", report["Informations"]["Équipe"])
            with col3:
                st.metric("Matchs joués", report["Informations"]["Matchs joués"])
            
            st.markdown("---")
            
            # Statistiques par catégorie
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("⚽ Statistiques offensives")
                for key, value in report["Statistiques offensives"].items():
                    st.metric(key, value)
            
            with col2:
                st.subheader("🎨 Création de jeu")
                for key, value in report["Statistiques de création"].items():
                    st.metric(key, value)
            
            with col3:
                st.subheader("🛡️ Statistiques défensives")
                for key, value in report["Statistiques défensives"].items():
                    st.metric(key, value)
            
            st.markdown("---")
            
            # Radar chart du profil
            st.subheader("📊 Profil radar")
            
            features = st.session_state.analyzer.select_features(position)
            player_data = df[df['player'] == selected_player]
            
            if not player_data.empty:
                values = []
                for feature in features:
                    col_min = df[feature].min()
                    col_max = df[feature].max()
                    normalized = ((player_data[feature].values[0] - col_min) / (col_max - col_min)) * 100
                    values.append(normalized)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=features,
                    fill='toself',
                    name=selected_player
                ))
                
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title=f"Profil de {selected_player} (percentile)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(report["error"])

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>🔥 Propulsé par StatsBomb Open Data | 💻 Développé avec Streamlit</p>
    </div>
""", unsafe_allow_html=True)
