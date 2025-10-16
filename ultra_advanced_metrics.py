# ultra_advanced_metrics.py
"""
Extraction ULTRA AVANCÉE de TOUTES les données StatsBomb
Exploite 100+ métriques au lieu de 35
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class UltraAdvancedMetricsExtractor:
    """
    Extrait TOUTES les métriques possibles depuis StatsBomb
    Passe de 35 à 100+ features !
    """
    
    @staticmethod
    def extract_all_metrics(events: pd.DataFrame, match_id: int) -> Dict:
        """
        Extrait TOUTES les métriques disponibles pour un match
        """
        stats_list = []
        
        for player in events['player'].dropna().unique():
            player_events = events[events['player'] == player]
            
            # Créer un dictionnaire avec TOUTES les métriques
            stats = {
                'match_id': match_id,
                'player': player,
                'team': player_events['team'].iloc[0] if len(player_events) > 0 else None,
            }
            
            # ==================== PASSES (20+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_pass_metrics(player_events))
            
            # ==================== TIRS (15+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_shot_metrics(player_events))
            
            # ==================== DÉFENSE (15+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_defensive_metrics(player_events))
            
            # ==================== DRIBBLES & CARRIES (10+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_dribble_carry_metrics(player_events))
            
            # ==================== DUELS (10+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_duel_metrics(player_events))
            
            # ==================== POSITION & ZONE (10+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_positional_metrics(player_events))
            
            # ==================== PRESSION (5+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_pressure_metrics(player_events))
            
            # ==================== ÉVÉNEMENTS SPÉCIAUX (10+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_special_events(player_events))
            
            # ==================== xG & xA AVANCÉS (5+ métriques) ====================
            stats.update(UltraAdvancedMetricsExtractor._extract_expected_metrics(player_events))
            
            stats_list.append(stats)
        
        return pd.DataFrame(stats_list)
    
    @staticmethod
    def _extract_pass_metrics(events: pd.DataFrame) -> Dict:
        """
        🎯 PASSES : 20+ métriques détaillées
        """
        passes = events[events['type'] == 'Pass']
        
        metrics = {
            # Basique
            'passes': len(passes),
            'passes_completed': len(passes[passes['pass_outcome'].isna()]),
            'assists': len(passes[passes.get('pass_goal_assist', pd.Series([False])) == True]) if 'pass_goal_assist' in passes.columns else 0,
            'key_passes': len(passes[passes.get('pass_shot_assist', pd.Series([False])) == True]) if 'pass_shot_assist' in passes.columns else 0,
            
            # 🆕 NOUVEAU : Types de passes
            'short_passes': len(passes[passes.get('pass_length', 0) < 15]) if 'pass_length' in passes.columns else 0,
            'medium_passes': len(passes[(passes.get('pass_length', 0) >= 15) & (passes.get('pass_length', 0) < 30)]) if 'pass_length' in passes.columns else 0,
            'long_passes': len(passes[passes.get('pass_length', 0) >= 30]) if 'pass_length' in passes.columns else 0,
            
            # 🆕 NOUVEAU : Passes spéciales
            'through_balls': len(passes[passes.get('pass_through_ball', False) == True]) if 'pass_through_ball' in passes.columns else 0,
            'crosses': len(passes[passes.get('pass_cross', False) == True]) if 'pass_cross' in passes.columns else 0,
            'switches': len(passes[passes.get('pass_switch', False) == True]) if 'pass_switch' in passes.columns else 0,
            'cutbacks': len(passes[passes.get('pass_cut_back', False) == True]) if 'pass_cut_back' in passes.columns else 0,
            
            # 🆕 NOUVEAU : Passes sous pression
            'passes_under_pressure': len(passes[passes.get('under_pressure', False) == True]) if 'under_pressure' in passes.columns else 0,
            
            # 🆕 NOUVEAU : Hauteur des passes
            'ground_passes': len(passes[passes.get('pass_height', {}).get('name') == 'Ground Pass']) if 'pass_height' in passes.columns else 0,
            'high_passes': len(passes[passes.get('pass_height', {}).get('name') == 'High Pass']) if 'pass_height' in passes.columns else 0,
            
            # 🆕 NOUVEAU : Direction
            'forward_passes': 0,  # Calculé avec les coordonnées
            'backward_passes': 0,
            'lateral_passes': 0,
            
            # 🆕 NOUVEAU : Passes progressives
            'progressive_passes': 0,  # Distance gagnée vers le but > 10m
            'progressive_distance': 0.0,
        }
        
        # Calcul des passes directionnelles avec coordonnées
        if 'location' in passes.columns and 'pass_end_location' in passes.columns:
            for idx, row in passes.iterrows():
                try:
                    if pd.notna(row.get('location')) and pd.notna(row.get('pass_end_location')):
                        start = row['location']
                        end = row['pass_end_location']
                        
                        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)) and len(start) >= 2 and len(end) >= 2:
                            x_diff = end[0] - start[0]
                            y_diff = end[1] - start[1]
                            
                            # Passes progressives (vers le but adverse)
                            if x_diff > 10:
                                metrics['progressive_passes'] += 1
                                metrics['progressive_distance'] += x_diff
                            
                            # Direction
                            if abs(x_diff) > abs(y_diff):
                                if x_diff > 0:
                                    metrics['forward_passes'] += 1
                                else:
                                    metrics['backward_passes'] += 1
                            else:
                                metrics['lateral_passes'] += 1
                except:
                    continue
        
        return metrics
    
    @staticmethod
    def _extract_shot_metrics(events: pd.DataFrame) -> Dict:
        """
        ⚽ TIRS : 15+ métriques détaillées
        """
        shots = events[events['type'] == 'Shot']
        
        metrics = {
            # Basique
            'shots': len(shots),
            'goals': len(shots[shots['shot_outcome'] == 'Goal']),
            'shots_on_target': len(shots[shots['shot_outcome'].isin(['Goal', 'Saved'])]),
            'xG': shots['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in shots.columns else 0,
            
            # 🆕 NOUVEAU : Types de tirs
            'shots_open_play': len(shots[shots.get('shot_type', {}).get('name') == 'Open Play']) if 'shot_type' in shots.columns else 0,
            'shots_free_kick': len(shots[shots.get('shot_type', {}).get('name') == 'Free Kick']) if 'shot_type' in shots.columns else 0,
            'shots_penalty': len(shots[shots.get('shot_type', {}).get('name') == 'Penalty']) if 'shot_type' in shots.columns else 0,
            
            # 🆕 NOUVEAU : Partie du corps
            'shots_right_foot': len(shots[shots.get('shot_body_part', {}).get('name') == 'Right Foot']) if 'shot_body_part' in shots.columns else 0,
            'shots_left_foot': len(shots[shots.get('shot_body_part', {}).get('name') == 'Left Foot']) if 'shot_body_part' in shots.columns else 0,
            'shots_head': len(shots[shots.get('shot_body_part', {}).get('name') == 'Head']) if 'shot_body_part' in shots.columns else 0,
            
            # 🆕 NOUVEAU : Technique
            'shots_first_time': len(shots[shots.get('shot_first_time', False) == True]) if 'shot_first_time' in shots.columns else 0,
            'shots_one_on_one': len(shots[shots.get('shot_one_on_one', False) == True]) if 'shot_one_on_one' in shots.columns else 0,
            
            # 🆕 NOUVEAU : Résultats détaillés
            'shots_saved': len(shots[shots['shot_outcome'] == 'Saved']),
            'shots_blocked': len(shots[shots['shot_outcome'] == 'Blocked']),
            'shots_off_target': len(shots[shots['shot_outcome'] == 'Off T']),
            'shots_post': len(shots[shots['shot_outcome'] == 'Post']),
        }
        
        return metrics
    
    @staticmethod
    def _extract_defensive_metrics(events: pd.DataFrame) -> Dict:
        """
        🛡️ DÉFENSE : 15+ métriques détaillées
        """
        metrics = {
            # Basique
            'tackles': len(events[events['type'] == 'Duel']),
            'interceptions': len(events[events['type'] == 'Interception']),
            'clearances': len(events[events['type'] == 'Clearance']),
            'blocks': len(events[events['type'] == 'Block']),
            
            # 🆕 NOUVEAU : Récupérations
            'ball_recoveries': len(events[events['type'] == 'Ball Recovery']),
            'ball_recoveries_offensive_third': 0,
            'ball_recoveries_middle_third': 0,
            'ball_recoveries_defensive_third': 0,
            
            # 🆕 NOUVEAU : Erreurs
            'errors': len(events[events['type'] == 'Error']),
            'dispossessed': len(events[events['type'] == 'Dispossessed']),
            'miscontrol': len(events[events['type'] == 'Miscontrol']),
            
            # 🆕 NOUVEAU : Gardien (si applicable)
            'goalkeeper_saves': len(events[events['type'] == 'Goal Keeper']),
            'goalkeeper_punches': 0,
            'goalkeeper_claims': 0,
            'goalkeeper_smother': 0,
        }
        
        # Récupérations par zone
        recoveries = events[events['type'] == 'Ball Recovery']
        if 'location' in recoveries.columns:
            for idx, row in recoveries.iterrows():
                try:
                    if pd.notna(row.get('location')) and isinstance(row['location'], (list, tuple)) and len(row['location']) >= 2:
                        x = row['location'][0]
                        if x < 40:
                            metrics['ball_recoveries_defensive_third'] += 1
                        elif x < 80:
                            metrics['ball_recoveries_middle_third'] += 1
                        else:
                            metrics['ball_recoveries_offensive_third'] += 1
                except:
                    continue
        
        # Gardien détails
        gk_events = events[events['type'] == 'Goal Keeper']
        if 'goalkeeper_type' in gk_events.columns:
            for gk_type in gk_events['goalkeeper_type'].dropna():
                if isinstance(gk_type, dict) and 'name' in gk_type:
                    if gk_type['name'] == 'Punch':
                        metrics['goalkeeper_punches'] += 1
                    elif gk_type['name'] == 'Claim':
                        metrics['goalkeeper_claims'] += 1
                    elif gk_type['name'] == 'Smother':
                        metrics['goalkeeper_smother'] += 1
        
        return metrics
    
    @staticmethod
    def _extract_dribble_carry_metrics(events: pd.DataFrame) -> Dict:
        """
        🏃 DRIBBLES & CARRIES : 10+ métriques
        """
        dribbles = events[events['type'] == 'Dribble']
        carries = events[events['type'] == 'Carry']
        
        metrics = {
            # Dribbles
            'dribbles': len(dribbles),
            'dribbles_completed': len(dribbles[dribbles.get('dribble_outcome', {}).get('name') == 'Complete']) if 'dribble_outcome' in dribbles.columns else 0,
            'dribbles_past_opponent': len(dribbles[dribbles.get('dribble_outcome', {}).get('name') == 'Complete']) if 'dribble_outcome' in dribbles.columns else 0,
            
            # 🆕 NOUVEAU : Carries (courses avec ballon)
            'carries': len(carries),
            'carry_distance': carries['carry_end_location'].apply(
                lambda x: np.sqrt((x[0] - 0)**2 + (x[1] - 0)**2) if pd.notna(x) and isinstance(x, (list, tuple)) and len(x) >= 2 else 0
            ).sum() if 'carry_end_location' in carries.columns else 0,
            'progressive_carries': 0,
            'carries_into_box': 0,
            'carries_into_final_third': 0,
            
            # 🆕 NOUVEAU : Nutmegs
            'nutmegs': len(dribbles[dribbles.get('dribble_nutmeg', False) == True]) if 'dribble_nutmeg' in dribbles.columns else 0,
        }
        
        # Carries progressifs
        if 'location' in carries.columns and 'carry_end_location' in carries.columns:
            for idx, row in carries.iterrows():
                try:
                    if pd.notna(row.get('location')) and pd.notna(row.get('carry_end_location')):
                        start = row['location']
                        end = row['carry_end_location']
                        
                        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)) and len(start) >= 2 and len(end) >= 2:
                            x_diff = end[0] - start[0]
                            
                            if x_diff > 5:
                                metrics['progressive_carries'] += 1
                            
                            # Dans la surface
                            if end[0] > 102 and 18 <= end[1] <= 62:
                                metrics['carries_into_box'] += 1
                            
                            # Dans le dernier tiers
                            if end[0] > 80:
                                metrics['carries_into_final_third'] += 1
                except:
                    continue
        
        return metrics
    
    @staticmethod
    def _extract_duel_metrics(events: pd.DataFrame) -> Dict:
        """
        ⚔️ DUELS : 10+ métriques
        """
        duels = events[events['type'] == 'Duel']
        
        metrics = {
            'duels_total': len(duels),
            'duels_won': len(duels[duels.get('duel_outcome', {}).get('name') == 'Won']) if 'duel_outcome' in duels.columns else 0,
            'duels_lost': len(duels[duels.get('duel_outcome', {}).get('name') == 'Lost']) if 'duel_outcome' in duels.columns else 0,
            
            # 🆕 NOUVEAU : Types de duels
            'aerial_duels': 0,
            'aerial_duels_won': 0,
            'ground_duels': 0,
            'ground_duels_won': 0,
            'loose_ball_duels': 0,
            'loose_ball_duels_won': 0,
        }
        
        # Duels par type
        if 'duel_type' in duels.columns:
            for idx, row in duels.iterrows():
                try:
                    duel_type = row.get('duel_type', {})
                    outcome = row.get('duel_outcome', {})
                    
                    if isinstance(duel_type, dict) and 'name' in duel_type:
                        if 'Aerial' in duel_type['name']:
                            metrics['aerial_duels'] += 1
                            if isinstance(outcome, dict) and outcome.get('name') == 'Won':
                                metrics['aerial_duels_won'] += 1
                        elif 'Ground' in duel_type['name']:
                            metrics['ground_duels'] += 1
                            if isinstance(outcome, dict) and outcome.get('name') == 'Won':
                                metrics['ground_duels_won'] += 1
                        elif 'Loose Ball' in duel_type['name']:
                            metrics['loose_ball_duels'] += 1
                            if isinstance(outcome, dict) and outcome.get('name') == 'Won':
                                metrics['loose_ball_duels_won'] += 1
                except:
                    continue
        
        return metrics
    
    @staticmethod
    def _extract_positional_metrics(events: pd.DataFrame) -> Dict:
        """
        📍 POSITION & ZONE : 10+ métriques
        """
        metrics = {
            # Actions par tiers du terrain
            'actions_defensive_third': 0,
            'actions_middle_third': 0,
            'actions_attacking_third': 0,
            
            # 🆕 NOUVEAU : Heatmap zones (divisé en 9 zones)
            'zone_def_left': 0,
            'zone_def_center': 0,
            'zone_def_right': 0,
            'zone_mid_left': 0,
            'zone_mid_center': 0,
            'zone_mid_right': 0,
            'zone_att_left': 0,
            'zone_att_center': 0,
            'zone_att_right': 0,
            
            # 🆕 NOUVEAU : Touches de balle
            'touches': len(events),
            'touches_in_box': 0,
        }
        
        # Calcul par zone
        for idx, row in events.iterrows():
            try:
                if pd.notna(row.get('location')) and isinstance(row['location'], (list, tuple)) and len(row['location']) >= 2:
                    x, y = row['location'][0], row['location'][1]
                    
                    # Tiers
                    if x < 40:
                        metrics['actions_defensive_third'] += 1
                    elif x < 80:
                        metrics['actions_middle_third'] += 1
                    else:
                        metrics['actions_attacking_third'] += 1
                    
                    # 9 zones
                    zone_x = 'def' if x < 40 else ('mid' if x < 80 else 'att')
                    zone_y = 'left' if y < 27 else ('center' if y < 53 else 'right')
                    metrics[f'zone_{zone_x}_{zone_y}'] += 1
                    
                    # Dans la surface
                    if x > 102 and 18 <= y <= 62:
                        metrics['touches_in_box'] += 1
            except:
                continue
        
        return metrics
    
    @staticmethod
    def _extract_pressure_metrics(events: pd.DataFrame) -> Dict:
        """
        💪 PRESSION : 5+ métriques
        """
        pressures = events[events['type'] == 'Pressure']
        
        metrics = {
            'pressures': len(pressures),
            'pressures_successful': 0,
            'pressures_defensive_third': 0,
            'pressures_middle_third': 0,
            'pressures_attacking_third': 0,
        }
        
        # Par zone
        if 'location' in pressures.columns:
            for idx, row in pressures.iterrows():
                try:
                    if pd.notna(row.get('location')) and isinstance(row['location'], (list, tuple)) and len(row['location']) >= 2:
                        x = row['location'][0]
                        
                        if x < 40:
                            metrics['pressures_defensive_third'] += 1
                        elif x < 80:
                            metrics['pressures_middle_third'] += 1
                        else:
                            metrics['pressures_attacking_third'] += 1
                except:
                    continue
        
        return metrics
    
    @staticmethod
    def _extract_special_events(events: pd.DataFrame) -> Dict:
        """
        ⭐ ÉVÉNEMENTS SPÉCIAUX : 10+ métriques
        """
        metrics = {
            # Fautes
            'fouls_committed': len(events[events['type'] == 'Foul Committed']),
            'fouls_won': len(events[events['type'] == 'Foul Won']),
            'yellow_cards': len(events[events.get('foul_committed_card', {}).get('name') == 'Yellow Card']) if 'foul_committed_card' in events.columns else 0,
            'red_cards': len(events[events.get('foul_committed_card', {}).get('name') == 'Red Card']) if 'foul_committed_card' in events.columns else 0,
            
            # 🆕 NOUVEAU : Corners & coups francs
            '50_50': len(events[events['type'] == '50/50']),
            'bad_behaviour': len(events[events['type'] == 'Bad Behaviour']),
            
            # 🆕 NOUVEAU : Remplacements
            'substitutions': len(events[events['type'] == 'Substitution']),
            
            # 🆕 NOUVEAU : Offside
            'offsides': len(events[events['type'] == 'Offside']),
        }
        
        return metrics
    
    @staticmethod
    def _extract_expected_metrics(events: pd.DataFrame) -> Dict:
        """
        📊 xG & xA AVANCÉS : 5+ métriques
        """
        shots = events[events['type'] == 'Shot']
        passes = events[events['type'] == 'Pass']
        
        metrics = {
            'xG_total': shots['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in shots.columns else 0,
            'xG_open_play': 0,
            'xG_set_piece': 0,
            
            # 🆕 NOUVEAU : xA (Expected Assists)
            'xA_total': 0,
            'xA_from_crosses': 0,
        }
        
        # xG par type
        if 'shot_type' in shots.columns and 'shot_statsbomb_xg' in shots.columns:
            for idx, row in shots.iterrows():
                try:
                    xg_val = row['shot_statsbomb_xg']
                    shot_type = row.get('shot_type', {})
                    
                    if pd.notna(xg_val) and isinstance(shot_type, dict) and 'name' in shot_type:
                        if shot_type['name'] == 'Open Play':
                            metrics['xG_open_play'] += xg_val
                        else:
                            metrics['xG_set_piece'] += xg_val
                except:
                    continue
        
        # xA (passes qui mènent à des tirs)
        if 'pass_shot_assist' in passes.columns:
            key_passes = passes[passes['pass_shot_assist'] == True]
            
            # Pour chaque passe clé, chercher le tir suivant pour récupérer son xG
            for idx, kp in key_passes.iterrows():
                try:
                    # Chercher les événements suivants
                    next_events = events[events.index > idx].head(5)
                    next_shots = next_events[next_events['type'] == 'Shot']
                    
                    if not next_shots.empty and 'shot_statsbomb_xg' in next_shots.columns:
                        xg = next_shots.iloc[0]['shot_statsbomb_xg']
                        if pd.notna(xg):
                            metrics['xA_total'] += xg
                            
                            # Si c'est un centre
                            if kp.get('pass_cross', False):
                                metrics['xA_from_crosses'] += xg
                except:
                    continue
        
        return metrics


def integrate_ultra_metrics(df: pd.DataFrame, all_events_dict: Dict) -> pd.DataFrame:
    """
    Intègre toutes les métriques ultra-avancées dans le DataFrame
    
    Args:
        df: DataFrame avec stats de base
        all_events_dict: Dict {player_name: events_df}
    
    Returns:
        DataFrame avec 100+ colonnes !
    """
    print("🚀 Extraction des métriques ultra-avancées...")
    
    # Pour chaque joueur, extraire toutes les métriques
    enhanced_rows = []
    
    for idx, row in df.iterrows():
        player = row['player']
        
        if player in all_events_dict:
            events = all_events_dict[player]
            
            # Extraire toutes les métriques
            extractor = UltraAdvancedMetricsExtractor()
            ultra_metrics = extractor.extract_all_metrics(events, row.get('match_id', 0))
            
            # Fusionner avec les données existantes
            enhanced_row = row.to_dict()
            if not ultra_metrics.empty:
                ultra_row = ultra_metrics[ultra_metrics['player'] == player]
                if not ultra_row.empty:
                    enhanced_row.update(ultra_row.iloc[0].to_dict())
            
            enhanced_rows.append(enhanced_row)
        else:
            enhanced_rows.append(row.to_dict())
    
    result = pd.DataFrame(enhanced_rows)
    
    print(f"✅ Extraction terminée : {len(result.columns)} colonnes au total !")
    return result


if __name__ == "__main__":
    print("✅ Module ultra_advanced_metrics.py chargé !")
    print("📊 Extrait 100+ métriques depuis StatsBomb")
    print("🚀 3x plus de données que le système de base !")
