# football_recruitment_app.py
"""
Application d'analyse de recrutement football avec Machine Learning
Utilise les données StatsBomb pour identifier des joueurs similaires
"""

import pandas as pd
import numpy as np
from statsbombpy import sb
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class FootballRecruitmentAnalyzer:
    """
    Classe principale pour l'analyse de recrutement
    """
    
    def __init__(self):
        self.player_stats = None
        self.scaler = StandardScaler()
        self.key_metrics = []
        
    def load_statsbomb_data(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """
        Charge les données StatsBomb pour une compétition/saison
        
        Args:
            competition_id: ID de la compétition (ex: 11 pour La Liga)
            season_id: ID de la saison (ex: 90 pour 2020/21)
            
        Returns:
            DataFrame avec les statistiques des joueurs
        """
        print(f"📥 Chargement des données - Competition: {competition_id}, Season: {season_id}")
        
        # Récupérer tous les matchs
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        
        all_players_stats = []
        
        # Parcourir chaque match
        for idx, match in matches.iterrows():
            match_id = match['match_id']
            
            try:
                # Récupérer les events du match
                events = sb.events(match_id=match_id)
                
                # Calculer les stats par joueur pour ce match
                match_stats = self._calculate_match_stats(events, match_id)
                all_players_stats.append(match_stats)
                
            except Exception as e:
                print(f"⚠️  Erreur pour match {match_id}: {e}")
                continue
        
        # Combiner toutes les stats
        if all_players_stats:
            self.player_stats = pd.concat(all_players_stats, ignore_index=True)
            self.player_stats = self._aggregate_season_stats(self.player_stats)
            print(f"✅ Données chargées: {len(self.player_stats)} joueurs")
            return self.player_stats
        else:
            print("❌ Aucune donnée chargée")
            return pd.DataFrame()
    
    def _calculate_match_stats(self, events: pd.DataFrame, match_id: int) -> pd.DataFrame:
        """
        Calcule les statistiques par joueur pour un match
        """
        stats_list = []
        
        # Grouper par joueur
        for player in events['player'].dropna().unique():
            player_events = events[events['player'] == player]
            
            stats = {
                'match_id': match_id,
                'player': player,
                'team': player_events['team'].iloc[0] if len(player_events) > 0 else None,
                
                # Statistiques de passes
                'passes': len(player_events[player_events['type'] == 'Pass']),
                'passes_completed': len(player_events[(player_events['type'] == 'Pass') & 
                                                       (player_events['pass_outcome'].isna())]),
                'key_passes': len(player_events[player_events['pass_shot_assist'] == True]),
                'assists': len(player_events[player_events['pass_goal_assist'] == True]),
                
                # Statistiques de tirs
                'shots': len(player_events[player_events['type'] == 'Shot']),
                'shots_on_target': len(player_events[(player_events['type'] == 'Shot') & 
                                                      (player_events['shot_outcome'].isin(['Goal', 'Saved']))]),
                'goals': len(player_events[(player_events['type'] == 'Shot') & 
                                           (player_events['shot_outcome'] == 'Goal')]),
                'xG': player_events[player_events['type'] == 'Shot']['shot_statsbomb_xg'].sum(),
                
                # Statistiques défensives
                'tackles': len(player_events[player_events['type'] == 'Duel']),
                'interceptions': len(player_events[player_events['type'] == 'Interception']),
                'clearances': len(player_events[player_events['type'] == 'Clearance']),
                'blocks': len(player_events[player_events['type'] == 'Block']),
                
                # Statistiques de dribbles
                'dribbles': len(player_events[player_events['type'] == 'Dribble']),
                'dribbles_completed': len(player_events[(player_events['type'] == 'Dribble') & 
                                                         (player_events['dribble_outcome'] == 'Complete')]),
                
                # Autres
                'fouls_committed': len(player_events[player_events['type'] == 'Foul Committed']),
                'fouls_won': len(player_events[player_events['type'] == 'Foul Won']),
            }
            
            stats_list.append(stats)
        
        return pd.DataFrame(stats_list)
    
    def _aggregate_season_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrège les statistiques sur la saison
        """
        # Grouper par joueur
        agg_stats = df.groupby(['player', 'team']).agg({
            'match_id': 'count',  # Nombre de matchs
            'passes': 'sum',
            'passes_completed': 'sum',
            'key_passes': 'sum',
            'assists': 'sum',
            'shots': 'sum',
            'shots_on_target': 'sum',
            'goals': 'sum',
            'xG': 'sum',
            'tackles': 'sum',
            'interceptions': 'sum',
            'clearances': 'sum',
            'blocks': 'sum',
            'dribbles': 'sum',
            'dribbles_completed': 'sum',
            'fouls_committed': 'sum',
            'fouls_won': 'sum',
        }).reset_index()
        
        agg_stats.rename(columns={'match_id': 'matches_played'}, inplace=True)
        
        # Calculer les moyennes par match
        for col in agg_stats.columns:
            if col not in ['player', 'team', 'matches_played']:
                agg_stats[f'{col}_per_90'] = (agg_stats[col] / agg_stats['matches_played']) * 90
        
        # Calculer les ratios
        agg_stats['pass_completion_rate'] = (agg_stats['passes_completed'] / 
                                              agg_stats['passes'].replace(0, 1)) * 100
        agg_stats['shot_accuracy'] = (agg_stats['shots_on_target'] / 
                                       agg_stats['shots'].replace(0, 1)) * 100
        agg_stats['dribble_success_rate'] = (agg_stats['dribbles_completed'] / 
                                              agg_stats['dribbles'].replace(0, 1)) * 100
        agg_stats['goal_conversion'] = (agg_stats['goals'] / 
                                         agg_stats['shots'].replace(0, 1)) * 100
        
        # Filtrer les joueurs avec peu de matchs
        agg_stats = agg_stats[agg_stats['matches_played'] >= 5]
        
        return agg_stats
    
    def select_features(self, position: str = 'all') -> List[str]:
        """
        Sélectionne les features pertinentes selon la position
        
        Args:
            position: 'forward', 'midfielder', 'defender', 'all'
        """
        base_features = ['passes_per_90', 'pass_completion_rate']
        
        if position == 'forward':
            self.key_metrics = base_features + [
                'goals_per_90', 'xG_per_90', 'shots_per_90', 
                'shot_accuracy', 'key_passes_per_90', 'dribbles_per_90'
            ]
        elif position == 'midfielder':
            self.key_metrics = base_features + [
                'key_passes_per_90', 'assists_per_90', 'tackles_per_90',
                'interceptions_per_90', 'dribbles_per_90'
            ]
        elif position == 'defender':
            self.key_metrics = base_features + [
                'tackles_per_90', 'interceptions_per_90', 'clearances_per_90',
                'blocks_per_90'
            ]
        else:  # all
            self.key_metrics = [
                'passes_per_90', 'pass_completion_rate', 'goals_per_90',
                'xG_per_90', 'assists_per_90', 'key_passes_per_90',
                'shots_per_90', 'tackles_per_90', 'interceptions_per_90',
                'dribbles_per_90', 'dribble_success_rate'
            ]
        
        return self.key_metrics
    
    def find_similar_players(self, 
                            target_player: str, 
                            top_n: int = 10,
                            position: str = 'all') -> pd.DataFrame:
        """
        Trouve les joueurs similaires à un joueur cible
        
        Args:
            target_player: Nom du joueur cible
            top_n: Nombre de joueurs similaires à retourner
            position: Position pour filtrer les features
            
        Returns:
            DataFrame avec les joueurs similaires et leur score de similarité
        """
        if self.player_stats is None:
            raise ValueError("Chargez d'abord les données avec load_statsbomb_data()")
        
        # Sélectionner les features
        features = self.select_features(position)
        
        # Préparer les données
        df = self.player_stats.copy()
        df = df.dropna(subset=features)
        
        # Vérifier que le joueur existe
        if target_player not in df['player'].values:
            raise ValueError(f"Joueur '{target_player}' non trouvé dans les données")
        
        # Normaliser les features
        X = df[features].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Trouver l'index du joueur cible
        target_idx = df[df['player'] == target_player].index[0]
        target_vector = X_scaled[df.index == target_idx]
        
        # Calculer la similarité cosinus
        similarities = cosine_similarity(target_vector, X_scaled)[0]
        
        # Créer un DataFrame avec les résultats
        results = df.copy()
        results['similarity_score'] = similarities
        results = results.sort_values('similarity_score', ascending=False)
        
        # Exclure le joueur lui-même et prendre les top_n
        results = results[results['player'] != target_player].head(top_n)
        
        return results[['player', 'team', 'matches_played', 'similarity_score'] + features]
    
    def cluster_players(self, 
                       n_clusters: int = 5, 
                       position: str = 'all') -> Tuple[pd.DataFrame, KMeans]:
        """
        Crée des clusters de joueurs avec des profils similaires
        
        Args:
            n_clusters: Nombre de clusters
            position: Position pour filtrer les features
            
        Returns:
            DataFrame avec les clusters et le modèle KMeans
        """
        if self.player_stats is None:
            raise ValueError("Chargez d'abord les données avec load_statsbomb_data()")
        
        # Sélectionner les features
        features = self.select_features(position)
        
        # Préparer les données
        df = self.player_stats.copy()
        df = df.dropna(subset=features)
        
        # Normaliser
        X = df[features].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X_scaled)
        
        return df, kmeans
    
    def visualize_player_profile(self, player_name: str, position: str = 'all'):
        """
        Crée un radar chart du profil du joueur
        """
        if self.player_stats is None:
            raise ValueError("Chargez d'abord les données")
        
        features = self.select_features(position)
        df = self.player_stats.copy()
        
        # Récupérer les données du joueur
        player_data = df[df['player'] == player_name]
        
        if player_data.empty:
            print(f"❌ Joueur '{player_name}' non trouvé")
            return
        
        # Normaliser entre 0 et 100
        values = []
        for feature in features:
            col_min = df[feature].min()
            col_max = df[feature].max()
            normalized = ((player_data[feature].values[0] - col_min) / (col_max - col_min)) * 100
            values.append(normalized)
        
        # Créer le radar chart
        angles = np.linspace(0, 2 * np.pi, len(features), endpoint=False).tolist()
        values += values[:1]  # Fermer le polygone
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values, 'o-', linewidth=2, label=player_name)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(features, size=10)
        ax.set_ylim(0, 100)
        ax.set_title(f'Profil de {player_name}', size=16, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)
        
        plt.tight_layout()
        return fig
    
    def create_scouting_report(self, player_name: str) -> Dict:
        """
        Crée un rapport de scouting complet
        """
        if self.player_stats is None:
            raise ValueError("Chargez d'abord les données")
        
        player_data = self.player_stats[self.player_stats['player'] == player_name]
        
        if player_data.empty:
            return {"error": f"Joueur '{player_name}' non trouvé"}
        
        player_data = player_data.iloc[0]
        
        report = {
            "Informations": {
                "Joueur": player_data['player'],
                "Équipe": player_data['team'],
                "Matchs joués": int(player_data['matches_played'])
            },
            "Statistiques offensives": {
                "Buts/90": round(player_data['goals_per_90'], 2),
                "xG/90": round(player_data['xG_per_90'], 2),
                "Assists/90": round(player_data['assists_per_90'], 2),
                "Passes clés/90": round(player_data['key_passes_per_90'], 2),
                "Tirs/90": round(player_data['shots_per_90'], 2),
                "Précision tirs (%)": round(player_data['shot_accuracy'], 1)
            },
            "Statistiques de création": {
                "Passes/90": round(player_data['passes_per_90'], 1),
                "Taux de passe (%)": round(player_data['pass_completion_rate'], 1),
                "Dribbles/90": round(player_data['dribbles_per_90'], 2),
                "Réussite dribbles (%)": round(player_data['dribble_success_rate'], 1)
            },
            "Statistiques défensives": {
                "Tacles/90": round(player_data['tackles_per_90'], 2),
                "Interceptions/90": round(player_data['interceptions_per_90'], 2),
                "Dégagements/90": round(player_data['clearances_per_90'], 2)
            }
        }
        
        return report


# Exemple d'utilisation
if __name__ == "__main__":
    
    # Initialiser l'analyseur
    analyzer = FootballRecruitmentAnalyzer()
    
    # Charger les données (exemple: La Liga 2020/21)
    print("🚀 Démarrage de l'analyse...")
    
    # Note: Utiliser les ID de compétitions/saisons disponibles dans StatsBomb Open Data
    # Competition 11 = La Liga, Season 90 = 2020/21
    df = analyzer.load_statsbomb_data(competition_id=11, season_id=90)
    
    if not df.empty:
        print("\n📊 Aperçu des données:")
        print(df[['player', 'team', 'matches_played', 'goals_per_90', 'xG_per_90']].head(10))
        
        # Trouver des joueurs similaires
        try:
            target = df['player'].iloc[0]  # Premier joueur comme exemple
            print(f"\n🔍 Recherche de joueurs similaires à: {target}")
            similar = analyzer.find_similar_players(target, top_n=5, position='forward')
            print("\nJoueurs similaires:")
            print(similar[['player', 'team', 'similarity_score']])
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
        
        # Clustering
        print("\n🎯 Création de clusters de joueurs...")
        clustered_df, kmeans = analyzer.cluster_players(n_clusters=4, position='all')
        print("\nDistribution des clusters:")
        print(clustered_df['cluster'].value_counts())
        
        print("\n✅ Analyse terminée!")
    else:
        print("❌ Échec du chargement des données")
