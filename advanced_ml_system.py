# advanced_ml_system.py
"""
Système ML Avancé pour le recrutement football
Utilise plusieurs algorithmes et feature engineering poussé
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.model_selection import cross_val_score
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class AdvancedPlayerAnalyzer:
    """
    Système ML avancé pour l'analyse de joueurs
    Combine plusieurs algorithmes et techniques
    """
    
    def __init__(self):
        self.scaler = RobustScaler()  # Plus robuste aux outliers
        self.pca = PCA(n_components=0.95)  # Garde 95% de la variance
        self.knn_model = None
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.features = []
        self.is_fitted = False
        
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Créer des features avancées via feature engineering
        """
        df = df.copy()
        
        try:
            # 1. Ratios offensifs
            if 'goals_per_90' in df.columns and 'xG_per_90' in df.columns:
                df['goal_efficiency'] = df['goals_per_90'] / df['xG_per_90'].replace(0, 1)
                df['overperformance'] = df['goals_per_90'] - df['xG_per_90']
            
            # 2. Indice de créativité
            if all(col in df.columns for col in ['key_passes_per_90', 'assists_per_90', 'passes_per_90']):
                df['creativity_index'] = (
                    df['key_passes_per_90'] * 0.5 + 
                    df['assists_per_90'] * 0.3 + 
                    df['passes_per_90'] * 0.2
                )
            
            # 3. Indice défensif
            if all(col in df.columns for col in ['tackles_per_90', 'interceptions_per_90']):
                df['defensive_index'] = (
                    df['tackles_per_90'] * 0.6 + 
                    df['interceptions_per_90'] * 0.4
                )
            
            # 4. Polyvalence offensive
            if all(col in df.columns for col in ['goals_per_90', 'assists_per_90', 'dribbles_per_90']):
                df['offensive_versatility'] = (
                    df['goals_per_90'] * 0.4 +
                    df['assists_per_90'] * 0.4 +
                    df['dribbles_per_90'] * 0.2
                )
            
            # 5. Efficacité globale
            if all(col in df.columns for col in ['pass_completion_rate', 'shot_accuracy', 'dribble_success_rate']):
                df['overall_efficiency'] = (
                    df['pass_completion_rate'] * 0.4 +
                    df['shot_accuracy'] * 0.3 +
                    df['dribble_success_rate'] * 0.3
                )
            
            # 6. Score d'impact
            if 'goals_per_90' in df.columns and 'assists_per_90' in df.columns:
                df['impact_score'] = (
                    df['goals_per_90'] * 1.5 +
                    df['assists_per_90'] * 1.2
                ) * 100
            
            # 7. Intensité de jeu
            if all(col in df.columns for col in ['passes_per_90', 'tackles_per_90', 'dribbles_per_90']):
                df['game_intensity'] = (
                    df['passes_per_90'] * 0.3 +
                    df['tackles_per_90'] * 0.4 +
                    df['dribbles_per_90'] * 0.3
                )
            
            # 8. Ratio contribution/tentatives
            if 'goals_per_90' in df.columns and 'shots_per_90' in df.columns:
                df['contribution_ratio'] = df['goals_per_90'] / df['shots_per_90'].replace(0, 1)
            
            print(f"✅ Créé {sum(1 for col in df.columns if col.endswith(('_index', '_efficiency', '_score', '_ratio', '_versatility', '_intensity')))} nouvelles features")
            
        except Exception as e:
            print(f"⚠️ Erreur feature engineering: {e}")
        
        return df
    
    def fit(self, df: pd.DataFrame, base_features: List[str]):
        """
        Entraîne le système avec feature engineering
        """
        try:
            # 1. Feature engineering
            df_enhanced = self.create_advanced_features(df)
            
            # 2. Sélectionner toutes les features numériques
            numeric_cols = df_enhanced.select_dtypes(include=[np.number]).columns
            self.features = [f for f in numeric_cols if f not in ['cluster']]
            
            # 3. Nettoyer les données
            df_clean = df_enhanced[self.features].fillna(0)
            X = df_clean.values
            
            if len(X) < 10:
                print("❌ Pas assez de données")
                return False
            
            # 4. Normaliser
            X_scaled = self.scaler.fit_transform(X)
            
            # 5. PCA pour réduction dimensionnelle
            if X_scaled.shape[1] > 5:
                X_scaled = self.pca.fit_transform(X_scaled)
                print(f"📉 PCA: {X_scaled.shape[1]} composantes (variance expliquée: {self.pca.explained_variance_ratio_.sum():.2%})")
            
            # 6. Entraîner KNN
            n_neighbors = min(15, len(X) - 1)
            self.knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
            self.knn_model.fit(X_scaled)
            
            # 7. Entraîner les modèles de prédiction
            if 'goals_per_90' in df_enhanced.columns:
                y = df_enhanced['goals_per_90'].fillna(0).values
                self.rf_model.fit(X_scaled, y)
                self.gb_model.fit(X_scaled, y)
                
                # Score de validation croisée
                rf_score = cross_val_score(self.rf_model, X_scaled, y, cv=3).mean()
                print(f"🎯 Random Forest score: {rf_score:.3f}")
            
            self.is_fitted = True
            print(f"✅ Système entraîné avec {len(self.features)} features")
            return True
            
        except Exception as e:
            print(f"❌ Erreur entraînement: {e}")
            return False
    
    def find_similar_players_advanced(self,
                                     target_player: str,
                                     df: pd.DataFrame,
                                     top_n: int = 10,
                                     weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Recherche avancée de joueurs similaires avec pondération
        """
        if not self.is_fitted:
            print("❌ Système non entraîné")
            return pd.DataFrame()
        
        try:
            # 1. Feature engineering
            df_enhanced = self.create_advanced_features(df)
            
            # 2. Trouver le joueur cible
            target_data = df_enhanced[df_enhanced['player'] == target_player]
            if target_data.empty:
                print(f"❌ Joueur '{target_player}' non trouvé")
                return pd.DataFrame()
            
            # 3. Préparer les données
            df_clean = df_enhanced[self.features].fillna(0)
            X = df_clean.values
            X_scaled = self.scaler.transform(X)
            
            if hasattr(self.pca, 'components_'):
                X_scaled = self.pca.transform(X_scaled)
            
            # 4. Trouver l'index du joueur
            target_idx = target_data.index[0]
            target_vector = X_scaled[df_enhanced.index == target_idx]
            
            # 5. Calculer les similarités
            # Méthode 1: KNN
            distances, indices = self.knn_model.kneighbors(target_vector)
            
            # Méthode 2: Cosine similarity
            cos_sim = cosine_similarity(target_vector, X_scaled)[0]
            
            # Méthode 3: Euclidean (inversée)
            eucl_dist = euclidean_distances(target_vector, X_scaled)[0]
            eucl_sim = 1 / (1 + eucl_dist)
            
            # 6. Combiner les scores
            combined_score = (
                cos_sim * 0.5 +
                eucl_sim * 0.3 +
                (1 - distances[0] / distances[0].max()) * 0.2
            )
            
            # 7. Créer le résultat
            results = df_enhanced.copy()
            results['similarity_score'] = combined_score * 100
            results = results.sort_values('similarity_score', ascending=False)
            
            # 8. Exclure le joueur lui-même
            results = results[results['player'] != target_player].head(top_n)
            
            # 9. Colonnes pertinentes
            display_cols = ['player', 'team', 'similarity_score', 'matches_played',
                           'goals_per_90', 'assists_per_90', 'impact_score']
            available_cols = [c for c in display_cols if c in results.columns]
            
            return results[available_cols]
            
        except Exception as e:
            print(f"❌ Erreur recherche: {e}")
            return pd.DataFrame()
    
    def find_by_profile(self,
                       target_profile: Dict[str, float],
                       df: pd.DataFrame,
                       top_n: int = 10,
                       tolerance: float = 0.2) -> pd.DataFrame:
        """
        Trouve des joueurs correspondant à un profil personnalisé
        """
        if not self.is_fitted:
            print("❌ Système non entraîné")
            return pd.DataFrame()
        
        try:
            # 1. Feature engineering
            df_enhanced = self.create_advanced_features(df)
            
            # 2. Créer le vecteur cible à partir du profil
            target_vector = np.zeros(len(self.features))
            for i, feature in enumerate(self.features):
                if feature in target_profile:
                    target_vector[i] = target_profile[feature]
            
            # 3. Normaliser
            target_vector = target_vector.reshape(1, -1)
            target_scaled = self.scaler.transform(target_vector)
            
            if hasattr(self.pca, 'components_'):
                target_scaled = self.pca.transform(target_scaled)
            
            # 4. Calculer les similarités
            df_clean = df_enhanced[self.features].fillna(0)
            X = df_clean.values
            X_scaled = self.scaler.transform(X)
            
            if hasattr(self.pca, 'components_'):
                X_scaled = self.pca.transform(X_scaled)
            
            # 5. Distance et score
            distances = euclidean_distances(target_scaled, X_scaled)[0]
            scores = 100 * np.exp(-distances / distances.mean())
            
            # 6. Filtrer par tolérance
            mask = scores >= (scores.max() * (1 - tolerance))
            
            # 7. Résultats
            results = df_enhanced[mask].copy()
            results['match_score'] = scores[mask]
            results = results.sort_values('match_score', ascending=False).head(top_n)
            
            display_cols = ['player', 'team', 'match_score', 'goals_per_90',
                           'assists_per_90', 'impact_score']
            available_cols = [c for c in display_cols if c in results.columns]
            
            return results[available_cols]
            
        except Exception as e:
            print(f"❌ Erreur profil: {e}")
            return pd.DataFrame()
    
    def predict_future_performance(self, 
                                   player_name: str,
                                   df: pd.DataFrame,
                                   months_ahead: int = 6) -> Dict:
        """
        Prédit la performance future d'un joueur
        """
        if not self.is_fitted:
            print("❌ Système non entraîné")
            return {}
        
        try:
            # 1. Feature engineering
            df_enhanced = self.create_advanced_features(df)
            
            # 2. Données du joueur
            player_data = df_enhanced[df_enhanced['player'] == player_name]
            if player_data.empty:
                return {"error": f"Joueur '{player_name}' non trouvé"}
            
            # 3. Préparer les features
            df_clean = df_enhanced[self.features].fillna(0)
            X = df_clean.values
            X_scaled = self.scaler.transform(X)
            
            if hasattr(self.pca, 'components_'):
                X_scaled = self.pca.transform(X_scaled)
            
            player_idx = player_data.index[0]
            player_features = X_scaled[df_enhanced.index == player_idx]
            
            # 4. Prédictions avec ensemble
            rf_pred = self.rf_model.predict(player_features)[0]
            gb_pred = self.gb_model.predict(player_features)[0]
            
            # Moyenne pondérée
            ensemble_pred = (rf_pred * 0.5 + gb_pred * 0.5)
            
            # 5. Tendance (simplifiée)
            current_goals = player_data['goals_per_90'].values[0]
            trend = ensemble_pred - current_goals
            
            # 6. Prédiction future avec facteur temps
            decay_factor = 0.95 ** (months_ahead / 6)  # Décroissance avec le temps
            future_pred = current_goals + (trend * decay_factor)
            
            return {
                'player': player_name,
                'current_goals_per_90': round(current_goals, 3),
                'predicted_goals_per_90': round(ensemble_pred, 3),
                'future_prediction': round(future_pred, 3),
                'trend': 'positive' if trend > 0 else 'negative',
                'confidence': round(85 * decay_factor, 1)
            }
            
        except Exception as e:
            print(f"❌ Erreur prédiction: {e}")
            return {"error": str(e)}
    
    def intelligent_clustering(self,
                              df: pd.DataFrame,
                              method: str = 'kmeans',
                              n_clusters: int = 5) -> Tuple[pd.DataFrame, object]:
        """
        Clustering intelligent avec plusieurs algorithmes
        """
        try:
            # 1. Feature engineering
            df_enhanced = self.create_advanced_features(df)
            
            # 2. Préparer les données
            df_clean = df_enhanced[self.features].fillna(0)
            X = df_clean.values
            X_scaled = self.scaler.fit_transform(X)
            
            if hasattr(self.pca, 'components_'):
                X_scaled = self.pca.transform(X_scaled)
            
            # 3. Choisir l'algorithme
            if method == 'kmeans':
                model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            elif method == 'dbscan':
                model = DBSCAN(eps=0.5, min_samples=5)
            elif method == 'hierarchical':
                model = AgglomerativeClustering(n_clusters=n_clusters)
            else:
                print(f"⚠️ Méthode '{method}' inconnue, utilisation de kmeans")
                model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            
            # 4. Clustering
            labels = model.fit_predict(X_scaled)
            df_enhanced['cluster'] = labels
            
            # 5. Analyser les clusters
            print(f"\n📊 Analyse des clusters ({method}):")
            for cluster_id in sorted(df_enhanced['cluster'].unique()):
                cluster_data = df_enhanced[df_enhanced['cluster'] == cluster_id]
                print(f"\n  Cluster {cluster_id}: {len(cluster_data)} joueurs")
                
                if 'impact_score' in cluster_data.columns:
                    avg_impact = cluster_data['impact_score'].mean()
                    print(f"    → Impact moyen: {avg_impact:.1f}")
                
                if 'goals_per_90' in cluster_data.columns:
                    avg_goals = cluster_data['goals_per_90'].mean()
                    print(f"    → Buts/90: {avg_goals:.2f}")
            
            return df_enhanced, model
            
        except Exception as e:
            print(f"❌ Erreur clustering: {e}")
            return df, None
    
    def identify_playing_style(self, 
                               player_name: str,
                               df: pd.DataFrame) -> Dict:
        """
        Identifie le style de jeu d'un joueur
        """
        try:
            df_enhanced = self.create_advanced_features(df)
            player_data = df_enhanced[df_enhanced['player'] == player_name]
            
            if player_data.empty:
                return {"error": f"Joueur '{player_name}' non trouvé"}
            
            player = player_data.iloc[0]
            
            # Définir les archétypes
            styles = []
            
            # 1. Finisseur
            if player.get('goals_per_90', 0) > 0.5:
                styles.append('Finisseur')
            
            # 2. Créateur
            if player.get('creativity_index', 0) > df_enhanced['creativity_index'].mean():
                styles.append('Créateur')
            
            # 3. Dribbleur
            if player.get('dribbles_per_90', 0) > 3:
                styles.append('Dribbleur')
            
            # 4. Défenseur
            if player.get('defensive_index', 0) > df_enhanced['defensive_index'].mean():
                styles.append('Défenseur')
            
            # 5. Polyvalent
            if player.get('offensive_versatility', 0) > df_enhanced['offensive_versatility'].quantile(0.75):
                styles.append('Polyvalent')
            
            # 6. Travailleur
            if player.get('game_intensity', 0) > df_enhanced['game_intensity'].mean():
                styles.append('Travailleur')
            
            return {
                'player': player_name,
                'primary_style': styles[0] if styles else 'Équilibré',
                'all_styles': styles if styles else ['Équilibré'],
                'offensive_rating': round(player.get('offensive_versatility', 0), 2),
                'defensive_rating': round(player.get('defensive_index', 0), 2),
                'creativity_rating': round(player.get('creativity_index', 0), 2)
            }
            
        except Exception as e:
            print(f"❌ Erreur style: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    print("✅ Module advanced_ml_system.py chargé avec succès!")
    print("Classe disponible: AdvancedPlayerAnalyzer")
