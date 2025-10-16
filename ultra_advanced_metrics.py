# ultra_advanced_metrics.py
"""
Extraction ULTRA simplifiée et robuste
Version qui ne crash JAMAIS
"""

import pandas as pd
import numpy as np
from typing import Dict
import warnings
warnings.filterwarnings('ignore')


class UltraAdvancedMetricsExtractor:
    """Extracteur robuste de métriques avancées"""
    
    @staticmethod
    def extract_all_metrics(events: pd.DataFrame, match_id: int) -> pd.DataFrame:
        """
        Extrait les métriques avec gestion d'erreur maximale
        Retourne TOUJOURS un DataFrame valide
        """
        try:
            if events is None or len(events) == 0:
                return pd.DataFrame()
            
            stats_list = []
            
            for player in events['player'].dropna().unique():
                player_events = events[events['player'] == player]
                
                if len(player_events) == 0:
                    continue
                
                # Statistiques de base garanties
                stats = {
                    'match_id': match_id,
                    'player': player,
                    'team': player_events['team'].iloc[0] if len(player_events) > 0 else None,
                }
                
                # Métriques de base (toujours présentes)
                stats.update(UltraAdvancedMetricsExtractor._safe_basic_metrics(player_events))
                
                # Métriques avancées (avec protection)
                stats.update(UltraAdvancedMetricsExtractor._safe_pass_metrics(player_events))
                stats.update(UltraAdvancedMetricsExtractor._safe_shot_metrics(player_events))
                stats.update(UltraAdvancedMetricsExtractor._safe_defensive_metrics(player_events))
                stats.update(UltraAdvancedMetricsExtractor._safe_progression_metrics(player_events))
                
                stats_list.append(stats)
            
            return pd.DataFrame(stats_list) if stats_list else pd.DataFrame()
            
        except Exception as e:
            print(f"⚠️ Erreur ULTRA match {match_id}: {str(e)[:100]}")
            return pd.DataFrame()
    
    @staticmethod
    def _safe_basic_metrics(events: pd.DataFrame) -> Dict:
        """Métriques de base garanties à 100%"""
        try:
            return {
                'passes': len(events[events['type'] == 'Pass']),
                'passes_completed': len(events[(events['type'] == 'Pass') & (events['pass_outcome'].isna())]),
                'shots': len(events[events['type'] == 'Shot']),
                'goals': len(events[(events['type'] == 'Shot') & (events['shot_outcome'] == 'Goal')]),
                'tackles': len(events[events['type'] == 'Duel']),
                'interceptions': len(events[events['type'] == 'Interception']),
                'clearances': len(events[events['type'] == 'Clearance']),
                'dribbles': len(events[events['type'] == 'Dribble']),
            }
        except:
            return {}
    
    @staticmethod
    def _safe_pass_metrics(events: pd.DataFrame) -> Dict:
        """Métriques de passes avec protection totale"""
        try:
            passes = events[events['type'] == 'Pass']
            
            metrics = {
                'key_passes': 0,
                'assists': 0,
                'through_balls': 0,
                'crosses': 0,
                'long_passes': 0,
                'progressive_passes': 0,
            }
            
            # Compteurs simples
            if 'pass_shot_assist' in passes.columns:
                metrics['key_passes'] = len(passes[passes['pass_shot_assist'] == True])
            
            if 'pass_goal_assist' in passes.columns:
                metrics['assists'] = len(passes[passes['pass_goal_assist'] == True])
            
            if 'pass_through_ball' in passes.columns:
                metrics['through_balls'] = len(passes[passes['pass_through_ball'] == True])
            
            if 'pass_cross' in passes.columns:
                metrics['crosses'] = len(passes[passes['pass_cross'] == True])
            
            # Passes longues (si longueur disponible)
            if 'pass_length' in passes.columns:
                try:
                    metrics['long_passes'] = len(passes[passes['pass_length'] > 30])
                except:
                    pass
            
            # Passes progressives (si coordonnées disponibles)
            if 'location' in passes.columns and 'pass_end_location' in passes.columns:
                count = 0
                for _, row in passes.iterrows():
                    try:
                        start = row['location']
                        end = row['pass_end_location']
                        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
                            if len(start) >= 2 and len(end) >= 2:
                                if end[0] - start[0] > 10:
                                    count += 1
                    except:
                        continue
                metrics['progressive_passes'] = count
            
            return metrics
        except:
            return {}
    
    @staticmethod
    def _safe_shot_metrics(events: pd.DataFrame) -> Dict:
        """Métriques de tirs avec protection totale"""
        try:
            shots = events[events['type'] == 'Shot']
            
            metrics = {
                'shots_on_target': len(shots[shots['shot_outcome'].isin(['Goal', 'Saved'])]),
                'xG': 0.0,
                'shots_right_foot': 0,
                'shots_left_foot': 0,
                'shots_head': 0,
            }
            
            # xG
            if 'shot_statsbomb_xg' in shots.columns:
                try:
                    metrics['xG'] = float(shots['shot_statsbomb_xg'].sum())
                except:
                    pass
            
            # Partie du corps
            if 'shot_body_part' in shots.columns:
                for body_part in shots['shot_body_part'].dropna():
                    try:
                        if isinstance(body_part, dict):
                            part = body_part.get('name', '')
                            if part == 'Right Foot':
                                metrics['shots_right_foot'] += 1
                            elif part == 'Left Foot':
                                metrics['shots_left_foot'] += 1
                            elif part == 'Head':
                                metrics['shots_head'] += 1
                    except:
                        continue
            
            return metrics
        except:
            return {}
    
    @staticmethod
    def _safe_defensive_metrics(events: pd.DataFrame) -> Dict:
        """Métriques défensives avec protection totale"""
        try:
            metrics = {
                'blocks': len(events[events['type'] == 'Block']),
                'ball_recoveries': len(events[events['type'] == 'Ball Recovery']),
                'errors': len(events[events['type'] == 'Error']),
                'dispossessed': len(events[events['type'] == 'Dispossessed']),
                'fouls_committed': len(events[events['type'] == 'Foul Committed']),
                'fouls_won': len(events[events['type'] == 'Foul Won']),
            }
            
            return metrics
        except:
            return {}
    
    @staticmethod
    def _safe_progression_metrics(events: pd.DataFrame) -> Dict:
        """Métriques de progression avec protection totale"""
        try:
            dribbles = events[events['type'] == 'Dribble']
            carries = events[events['type'] == 'Carry']
            
            metrics = {
                'dribbles_completed': 0,
                'carries': len(carries),
                'progressive_carries': 0,
            }
            
            # Dribbles réussis
            if 'dribble_outcome' in dribbles.columns:
                for outcome in dribbles['dribble_outcome'].dropna():
                    try:
                        if isinstance(outcome, dict):
                            if outcome.get('name') == 'Complete':
                                metrics['dribbles_completed'] += 1
                    except:
                        continue
            
            # Carries progressifs
            if 'location' in carries.columns and 'carry_end_location' in carries.columns:
                count = 0
                for _, row in carries.iterrows():
                    try:
                        start = row['location']
                        end = row['carry_end_location']
                        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
                            if len(start) >= 2 and len(end) >= 2:
                                if end[0] - start[0] > 5:
                                    count += 1
                    except:
                        continue
                metrics['progressive_carries'] = count
            
            return metrics
        except:
            return {}


if __name__ == "__main__":
    print("✅ Module ultra_advanced_metrics.py SIMPLIFIÉ chargé !")
    print("🛡️ Version ultra-robuste qui ne crashe jamais")
