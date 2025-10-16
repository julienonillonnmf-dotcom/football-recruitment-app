# recommendation_system.py
"""
Système de recommandation intelligent pour le recrutement
Version complète prête à l'emploi
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class PlayerRecommendationSystem:
    """Système de recommandation multi-algorithmes"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.knn_model = None
        self.performance_model = None
        self.features = []
        self.is_fitted = False
        self.data_for_fit = None  # Pour stocker les données d'entraînement
        
    def fit(self, df: pd.DataFrame, features: List[str]):
        """Entraîne les modèles de recommandation"""
        try:
            self.features = features
            
            # Vérifier que les features existent
            available_features = [f for f in features if f in df.columns]
            if not available_features:
                print("❌ Aucune feature disponible")
                return
            
            self.features = available_features
            
            # Préparer les données
            df_clean = df[self.features].fillna(0)
            X = df_clean.values
            
            if len(X) < 2:
                print("❌ Pas assez de données pour entraîner")
                return
            
            # Stocker les données pour référence
            self.data_for_fit = df.copy()
            
            # Scaler
            X_scaled = self.scaler.fit_transform(X)
            
            # Modèle KNN
            n_neighbors = min(10, len(X) - 1)
            self.knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
            self.knn_model.fit(X_scaled)
            
            # Modèle de performance
            if 'goals_per_90' in df.columns:
                y = df['goals_per_90'].fillna(0).values
                self.performance_model = RandomForestRegressor(
                    n_estimators=50,
                    max_depth=5,
                    random_state=42
                )
                self.performance_model.fit(X_scaled, y)
            
            self.is_fitted = True
            print(f"✅ Modèle entraîné avec {len(self.features)} features")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'entraînement: {e}")
            self.is_fitted = False
    
    def recommend_by_profile(self,
                            target_profile: Dict[str, float],
                            df: pd.DataFrame,
                            top_n: int = 10,
                            filters: Optional[Dict] = None) -> pd.DataFrame:
        """Recommande des joueurs basés sur un profil"""
        if not self.is_fitted:
            print("❌ Modèle non entraîné")
            return pd.DataFrame()
        
        try:
            # Créer le vecteur cible
            target_vector = np.array([
                target_profile.get(f, 0) for f in self.features
            ]).reshape(1, -1)
            
            # Vérifier que le vecteur a la bonne dimension
            if target_vector.shape[1] != len(self.features):
                print(f"❌ Dimension incorrecte: attendu {len(self.features)}, reçu {target_vector.shape[1]}")
                return pd.DataFrame()
            
            target_scaled = self.scaler.transform(target_vector)
            
            # Appliquer les filtres
            filtered_df = df.copy()
            if filters:
                if 'max_age' in filters and 'age' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['age'] <= filters['max_age']]
                if 'min_matches' in filters and 'matches_played' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['matches_played'] >= filters['min_matches']]
            
            if filtered_df.empty:
                return pd.DataFrame()
            
            # Préparer les données filtrées
            X_filtered = filtered_df[self.features].fillna(0).values
            
            # Vérifier les dimensions
            if X_filtered.shape[1] != target_vector.shape[1]:
                print(f"❌ Dimensions incompatibles: X={X_filtered.shape}, target={target_vector.shape}")
                return pd.DataFrame()
            
            X_filtered_scaled = self.scaler.transform(X_filtered)
            
            # Calculer les similarités directement (plus fiable que KNN sur données filtrées)
            similarities = cosine_similarity(target_scaled, X_filtered_scaled)[0]
            
            # Créer le résultat
            results = filtered_df.copy()
            results['match_score'] = (1 - similarities) * 100  # Convertir distance en score
            results['match_score'] = 100 - results['match_score']  # Inverser pour que 100 = parfait
            results['match_score'] = results['match_score'].clip(0, 100)
            
            # Trier et limiter
            results = results.sort_values('match_score', ascending=False).head(top_n)
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur recommandation: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def recommend_by_role(self,
                         role: str,
                         df: pd.DataFrame,
                         top_n: int = 10) -> pd.DataFrame:
        """Recommande des joueurs pour un rôle tactique"""
        
        role_profiles = {
            'box_to_box': {
                'passes_per_90': 50, 'pass_completion_rate': 85,
                'tackles_per_90': 2.5, 'interceptions_per_90': 1.5,
                'goals_per_90': 0.15, 'key_passes_per_90': 1.5
            },
            'playmaker': {
                'passes_per_90': 70, 'pass_completion_rate': 90,
                'key_passes_per_90': 3.0, 'assists_per_90': 0.3
            },
            'target_man': {
                'goals_per_90': 0.6, 'xG_per_90': 0.5,
                'shots_per_90': 3.5, 'shot_accuracy': 45
            },
            'winger': {
                'goals_per_90': 0.4, 'assists_per_90': 0.4,
                'dribbles_per_90': 4.0, 'dribble_success_rate': 60
            },
            'ball_winner': {
                'tackles_per_90': 4.0, 'interceptions_per_90': 2.5
            },
            'sweeper': {
                'passes_per_90': 60, 'pass_completion_rate': 88,
                'clearances_per_90': 3.0, 'interceptions_per_90': 2.0
            }
        }
        
        if role not in role_profiles:
            print(f"❌ Rôle '{role}' non reconnu")
            return pd.DataFrame()
        
        return self.recommend_by_profile(role_profiles[role], df, top_n)
    
    def recommend_replacement(self,
                            departing_player: str,
                            df: pd.DataFrame,
                            top_n: int = 10,
                            upgrade_factor: float = 1.0) -> pd.DataFrame:
        """Recommande des remplaçants"""
        try:
            player_data = df[df['player'] == departing_player]
            
            if player_data.empty:
                print(f"❌ Joueur '{departing_player}' non trouvé")
                return pd.DataFrame()
            
            # Créer profil cible
            target_profile = {}
            for feature in self.features:
                if feature in player_data.columns:
                    value = player_data[feature].values[0]
                    if pd.notna(value):
                        target_profile[feature] = float(value) * upgrade_factor
            
            # Exclure le joueur actuel
            filtered_df = df[df['player'] != departing_player].copy()
            
            return self.recommend_by_profile(target_profile, filtered_df, top_n)
            
        except Exception as e:
            print(f"❌ Erreur remplacement: {e}")
            return pd.DataFrame()
    
    def predict_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prédit la performance future"""
        if not self.performance_model:
            print("❌ Modèle de performance non disponible")
            return df
        
        try:
            X = df[self.features].fillna(0).values
            X_scaled = self.scaler.transform(X)
            
            df = df.copy()
            df['predicted_goals_per_90'] = self.performance_model.predict(X_scaled)
            
            if 'goals_per_90' in df.columns:
                actual = df['goals_per_90'].replace(0, 0.01)
                df['potential_improvement'] = (
                    (df['predicted_goals_per_90'] - df['goals_per_90']) / actual * 100
                )
            
            return df
            
        except Exception as e:
            print(f"❌ Erreur prédiction: {e}")
            return df
    
    def create_transfer_shortlist(self,
                                 requirements: Dict,
                                 df: pd.DataFrame,
                                 budget: Optional[float] = None) -> Dict:
        """Crée une shortlist complète"""
        try:
            shortlist = {}
            total_cost = 0.0
            
            for position, req in requirements.items():
                role = req.get('role', position)
                count = req.get('count', 1)
                
                recommendations = self.recommend_by_role(role, df, top_n=count * 3)
                
                if recommendations.empty:
                    continue
                
                # Filtrer par budget
                if budget and 'market_value' in recommendations.columns:
                    available_budget = budget - total_cost
                    recommendations = recommendations[
                        recommendations['market_value'] <= available_budget / count
                    ]
                
                selected = recommendations.head(count)
                
                if 'market_value' in selected.columns:
                    total_cost += selected['market_value'].sum()
                
                shortlist[position] = selected
            
            shortlist['summary'] = {
                'total_players': sum(len(v) for k, v in shortlist.items() if k != 'summary' and isinstance(v, pd.DataFrame)),
                'total_cost': total_cost,
                'remaining_budget': budget - total_cost if budget else None
            }
            
            return shortlist
            
        except Exception as e:
            print(f"❌ Erreur shortlist: {e}")
            return {}


if __name__ == "__main__":
    print("✅ Module recommendation_system.py chargé avec succès!")
    print("Classe disponible: PlayerRecommendationSystem")
