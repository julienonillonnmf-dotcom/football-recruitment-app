# advanced_metrics.py
"""
Métriques avancées pour l'analyse de recrutement football
Version complète prête à l'emploi
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class AdvancedMetrics:
    """Calcule des métriques avancées de football"""
    
    @staticmethod
    def calculate_progressive_actions(events: pd.DataFrame) -> Dict:
        """Calcule les actions progressives"""
        metrics = {
            'progressive_passes': 0,
            'progressive_carries': 0,
            'progressive_distance': 0.0
        }
        
        try:
            if 'location' in events.columns and 'pass_end_location' in events.columns:
                passes = events[events['type'] == 'Pass'].copy()
                
                for idx, pass_event in passes.iterrows():
                    if pd.notna(pass_event.get('location')) and pd.notna(pass_event.get('pass_end_location')):
                        start_x = pass_event['location'][0] if isinstance(pass_event['location'], (list, tuple)) else 0
                        end_x = pass_event['pass_end_location'][0] if isinstance(pass_event['pass_end_location'], (list, tuple)) else 0
                        
                        progression = end_x - start_x
                        if progression > 10:
                            metrics['progressive_passes'] += 1
                            metrics['progressive_distance'] += progression
            
            if 'carry_end_location' in events.columns:
                carries = events[events['type'] == 'Carry'].copy()
                for idx, carry in carries.iterrows():
                    if pd.notna(carry.get('location')) and pd.notna(carry.get('carry_end_location')):
                        start_x = carry['location'][0] if isinstance(carry['location'], (list, tuple)) else 0
                        end_x = carry['carry_end_location'][0] if isinstance(carry['carry_end_location'], (list, tuple)) else 0
                        
                        progression = end_x - start_x
                        if progression > 5:
                            metrics['progressive_carries'] += 1
        except Exception as e:
            print(f"Erreur progressive actions: {e}")
        
        return metrics
    
    @staticmethod
    def calculate_defensive_metrics(events: pd.DataFrame) -> Dict:
        """Métriques défensives avancées"""
        metrics = {
            'pressures': 0,
            'successful_pressures': 0,
            'pressure_success_rate': 0.0,
            'ball_recoveries': 0,
            'tackles_won': 0,
            'aerial_duels_won': 0,
            'blocks': 0
        }
        
        try:
            metrics['pressures'] = len(events[events['type'] == 'Pressure'])
            metrics['ball_recoveries'] = len(events[events['type'] == 'Ball Recovery'])
            metrics['blocks'] = len(events[events['type'] == 'Block'])
            
            if 'duel_outcome' in events.columns:
                duels = events[events['type'] == 'Duel']
                won_duels = duels[duels['duel_outcome'] == 'Won']
                metrics['tackles_won'] = len(won_duels)
                
                if 'duel_type' in events.columns:
                    aerial = duels[duels['duel_type'].str.contains('Aerial', na=False)]
                    metrics['aerial_duels_won'] = len(aerial[aerial['duel_outcome'] == 'Won'])
            
            if metrics['pressures'] > 0 and 'pressure_outcome' in events.columns:
                successful = events[(events['type'] == 'Pressure') & events['pressure_outcome'].notna()]
                metrics['successful_pressures'] = len(successful)
                metrics['pressure_success_rate'] = (metrics['successful_pressures'] / metrics['pressures']) * 100
        except Exception as e:
            print(f"Erreur defensive metrics: {e}")
        
        return metrics
    
    @staticmethod
    def calculate_creativity_metrics(events: pd.DataFrame) -> Dict:
        """Métriques de créativité"""
        metrics = {
            'through_balls': 0,
            'switches_of_play': 0,
            'crosses_into_box': 0,
            'shot_creating_actions': 0,
            'key_passes': 0
        }
        
        try:
            passes = events[events['type'] == 'Pass']
            
            if 'pass_through_ball' in events.columns:
                metrics['through_balls'] = len(passes[passes['pass_through_ball'] == True])
            
            if 'pass_switch' in events.columns:
                metrics['switches_of_play'] = len(passes[passes['pass_switch'] == True])
            
            if 'pass_cross' in events.columns:
                metrics['crosses_into_box'] = len(passes[passes['pass_cross'] == True])
            
            if 'pass_shot_assist' in events.columns:
                metrics['key_passes'] = len(passes[passes['pass_shot_assist'] == True])
                metrics['shot_creating_actions'] = metrics['key_passes']
        except Exception as e:
            print(f"Erreur creativity metrics: {e}")
        
        return metrics
    
    @staticmethod
    def calculate_zones_activity(events: pd.DataFrame, player: str) -> Dict:
        """Calcule l'activité par zone du terrain"""
        zones = {
            'defensive_third': 0,
            'middle_third': 0,
            'attacking_third': 0
        }
        
        try:
            player_events = events[events['player'] == player].copy()
            
            if 'location' in player_events.columns:
                for idx, event in player_events.iterrows():
                    if pd.notna(event.get('location')):
                        x = event['location'][0] if isinstance(event['location'], (list, tuple)) else 0
                        
                        if x < 40:
                            zones['defensive_third'] += 1
                        elif x < 80:
                            zones['middle_third'] += 1
                        else:
                            zones['attacking_third'] += 1
            
            total = sum(zones.values())
            if total > 0:
                return {k: round(v/total * 100, 1) for k, v in zones.items()}
        except Exception as e:
            print(f"Erreur zones activity: {e}")
        
        return zones
    
    @staticmethod
    def calculate_expected_assists(events: pd.DataFrame) -> float:
        """Calcule les Expected Assists (xA)"""
        xA = 0.0
        
        try:
            passes = events[events['type'] == 'Pass'].copy()
            
            if 'pass_shot_assist' in passes.columns and 'shot_statsbomb_xg' in events.columns:
                key_passes = passes[passes['pass_shot_assist'] == True]
                
                for idx, pass_event in key_passes.iterrows():
                    next_events = events[events.index > idx].head(3)
                    shots = next_events[next_events['type'] == 'Shot']
                    
                    if not shots.empty and pd.notna(shots.iloc[0].get('shot_statsbomb_xg')):
                        xA += shots.iloc[0]['shot_statsbomb_xg']
        except Exception as e:
            print(f"Erreur expected assists: {e}")
        
        return round(xA, 2)
    
    @staticmethod
    def calculate_player_efficiency_score(stats: pd.Series) -> float:
        """Score d'efficacité global (0-100)"""
        try:
            weights = {
                'goals_per_90': 0.15,
                'xG_per_90': 0.10,
                'assists_per_90': 0.10,
                'key_passes_per_90': 0.08,
                'pass_completion_rate': 0.10,
                'dribble_success_rate': 0.08,
                'tackles_per_90': 0.08,
                'interceptions_per_90': 0.08,
                'shot_accuracy': 0.08,
                'matches_played': 0.05
            }
            
            score = 0.0
            for metric, weight in weights.items():
                if metric in stats.index and pd.notna(stats.get(metric)):
                    value = float(stats[metric])
                    
                    if 'rate' in metric or 'accuracy' in metric:
                        normalized = min(value / 100, 1)
                    elif metric == 'matches_played':
                        normalized = min(value / 30, 1)
                    else:
                        normalized = min(value / 10, 1)
                    
                    score += normalized * weight * 100
            
            return round(score, 1)
        except Exception as e:
            print(f"Erreur efficiency score: {e}")
            return 50.0


def add_advanced_metrics_to_dataframe(df: pd.DataFrame, all_events: Dict) -> pd.DataFrame:
    """
    Ajoute les métriques avancées au DataFrame
    
    Args:
        df: DataFrame avec stats de base
        all_events: Dict {player_name: events_df}
    
    Returns:
        DataFrame enrichi
    """
    advanced = AdvancedMetrics()
    
    # Initialiser les colonnes
    new_columns = [
        'progressive_passes', 'progressive_carries', 'pressures_per_90',
        'pressure_success_rate', 'through_balls', 'switches_of_play',
        'attacking_third_pct', 'xA', 'efficiency_score'
    ]
    
    for col in new_columns:
        if col not in df.columns:
            df[col] = 0.0
    
    for idx, row in df.iterrows():
        player = row['player']
        matches = row.get('matches_played', 1)
        
        if player in all_events:
            try:
                events = all_events[player]
                
                # Métriques progressives
                progressive = advanced.calculate_progressive_actions(events)
                df.at[idx, 'progressive_passes'] = progressive['progressive_passes']
                df.at[idx, 'progressive_carries'] = progressive['progressive_carries']
                
                # Métriques défensives
                defensive = advanced.calculate_defensive_metrics(events)
                df.at[idx, 'pressures_per_90'] = (defensive['pressures'] / matches) if matches > 0 else 0
                df.at[idx, 'pressure_success_rate'] = defensive['pressure_success_rate']
                
                # Métriques de créativité
                creativity = advanced.calculate_creativity_metrics(events)
                df.at[idx, 'through_balls'] = creativity['through_balls']
                df.at[idx, 'switches_of_play'] = creativity['switches_of_play']
                
                # Zones
                zones = advanced.calculate_zones_activity(events, player)
                df.at[idx, 'attacking_third_pct'] = zones.get('attacking_third', 0)
                
                # xA
                df.at[idx, 'xA'] = advanced.calculate_expected_assists(events)
                
                # Score d'efficacité
                df.at[idx, 'efficiency_score'] = advanced.calculate_player_efficiency_score(row)
            except Exception as e:
                print(f"Erreur pour {player}: {e}")
    
    return df


if __name__ == "__main__":
    print("✅ Module advanced_metrics.py chargé avec succès!")
    print("Classes disponibles: AdvancedMetrics")
    print("Fonctions disponibles: add_advanced_metrics_to_dataframe")
