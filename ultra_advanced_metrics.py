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
    def extract_all_metrics(events: pd.DataFrame, match_id: int) -> pd.DataFrame:
        """
        Extrait TOUTES les métriques disponibles pour un match
        CORRECTION: Retourne DataFrame au lieu de Dict
        """
        try:
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
            
            # CORRECTION: Toujours retourner un DataFrame
            if stats_list:
                return pd.DataFrame(stats_list)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Erreur extraction match {match_id}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def _safe_get_dict_value(obj, key, default=''):
        """Helper pour accéder aux dictionnaires imbriqués de manière sûre"""
        try:
            if isinstance(obj, dict) and key in obj:
                val = obj[key]
                if isinstance(val, dict) and 'name' in val:
                    return val['name']
                return val
            return default
        except:
            return default
    
    @staticmethod
    def _extract_pass_metrics(events: pd.DataFrame) -> Dict:
        """🎯 PASSES : 20+ métriques détaillées"""
        passes = events[events['type'] == 'Pass']
        
        metrics = {
            # Basique
            'passes': len(passes),
            'passes_completed': len(passes[passes['pass_outcome'].isna()]),
            'assists': len(passes[passes.get('pass_goal_assist', pd.Series([False])) == True]) if 'pass_goal_assist' in passes.columns else 0,
            'key_passes': len(passes[passes.get('pass_shot_assist', pd.Series([False])) == True]) if 'pass_shot_assist' in passes.columns else 0,
            
            # Types de passes
            'short_passes': 0,
            'medium_passes': 0,
            'long_passes': 0,
            
            # Passes spéciales
            'through_balls': len(passes[passes.get('pass_through_ball', False) == True]) if 'pass_through_ball' in passes.columns else 0,
            'crosses': len(passes[passes.get('pass_cross', False) == True]) if 'pass_cross' in passes.columns else 0,
            'switches': len(passes[passes.get('pass_switch', False) == True]) if 'pass_switch' in passes.columns else 0,
            'cutbacks': len(passes[passes.get('pass_cut_back', False) == True]) if 'pass_cut_back' in passes.columns else 0,
            
            # Passes sous pression
            'passes_under_pressure': len(passes[passes.get('under_pressure', False) == True]) if 'under_pressure' in passes.columns else 0,
            
            # Hauteur des passes
            'ground_passes': 0,
            'high_passes': 0,
            
            # Direction
            'forward_passes': 0,
            'backward_passes': 0,
            'lateral_passes': 0,
            
            # Passes progressives
            'progressive_passes': 0,
            'progressive_distance': 0.0,
        }
        
        # Longueur des passes
        if 'pass_length' in passes.columns:
            for length in passes['pass_length'].dropna():
                try:
                    if length < 15:
                        metrics['short_passes'] += 1
                    elif length < 30:
                        metrics['medium_passes'] += 1
                    else:
                        metrics['long_passes'] += 1
                except:
                    continue
        
        # Hauteur (accès sécurisé)
        if 'pass_height' in passes.columns:
            for height in passes['pass_height'].dropna():
                height_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(height, 'name')
                if height_name == 'Ground Pass':
                    metrics['ground_passes'] += 1
                elif height_name == 'High Pass':
                    metrics['high_passes'] += 1
        
        # Calcul des passes directionnelles avec coordonnées
        if 'location' in passes.columns and 'pass_end_location' in passes.columns:
            for idx, row in passes.iterrows():
                try:
                    start = row.get('location')
                    end = row.get('pass_end_location')
                    
                    if pd.notna(start) and pd.notna(end) and isinstance(start, (list, tuple, np.ndarray)) and isinstance(end, (list, tuple, np.ndarray)):
                        if len(start) >= 2 and len(end) >= 2:
                            x_diff = float(end[0]) - float(start[0])
                            y_diff = float(end[1]) - float(start[1])
                            
                            # Passes progressives
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
        """⚽ TIRS : 15+ métriques détaillées"""
        shots = events[events['type'] == 'Shot']
        
        metrics = {
            # Basique
            'shots': len(shots),
            'goals': len(shots[shots['shot_outcome'] == 'Goal']),
            'shots_on_target': len(shots[shots['shot_outcome'].isin(['Goal', 'Saved'])]),
            'xG': shots['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in shots.columns else 0,
            
            # Types de tirs
            'shots_open_play': 0,
            'shots_free_kick': 0,
            'shots_penalty': 0,
            
            # Partie du corps
            'shots_right_foot': 0,
            'shots_left_foot': 0,
            'shots_head': 0,
            
            # Technique
            'shots_first_time': len(shots[shots.get('shot_first_time', False) == True]) if 'shot_first_time' in shots.columns else 0,
            'shots_one_on_one': len(shots[shots.get('shot_one_on_one', False) == True]) if 'shot_one_on_one' in shots.columns else 0,
            
            # Résultats détaillés
            'shots_saved': len(shots[shots['shot_outcome'] == 'Saved']),
            'shots_blocked': len(shots[shots['shot_outcome'] == 'Blocked']),
            'shots_off_target': len(shots[shots['shot_outcome'] == 'Off T']),
            'shots_post': len(shots[shots['shot_outcome'] == 'Post']),
        }
        
        # Types (accès sécurisé)
        if 'shot_type' in shots.columns:
            for shot_type in shots['shot_type'].dropna():
                type_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(shot_type, 'name')
                if type_name == 'Open Play':
                    metrics['shots_open_play'] += 1
                elif type_name == 'Free Kick':
                    metrics['shots_free_kick'] += 1
                elif type_name == 'Penalty':
                    metrics['shots_penalty'] += 1
        
        # Partie du corps (accès sécurisé)
        if 'shot_body_part' in shots.columns:
            for body_part in shots['shot_body_part'].dropna():
                part_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(body_part, 'name')
                if part_name == 'Right Foot':
                    metrics['shots_right_foot'] += 1
                elif part_name == 'Left Foot':
                    metrics['shots_left_foot'] += 1
                elif part_name == 'Head':
                    metrics['shots_head'] += 1
        
        return metrics
    
    @staticmethod
    def _extract_defensive_metrics(events: pd.DataFrame) -> Dict:
        """🛡️ DÉFENSE : 15+ métriques détaillées"""
        metrics = {
            'tackles': len(events[events['type'] == 'Duel']),
            'interceptions': len(events[events['type'] == 'Interception']),
            'clearances': len(events[events['type'] == 'Clearance']),
            'blocks': len(events[events['type'] == 'Block']),
            'ball_recoveries': len(events[events['type'] == 'Ball Recovery']),
            'ball_recoveries_offensive_third': 0,
            'ball_recoveries_middle_third': 0,
            'ball_recoveries_defensive_third': 0,
            'errors': len(events[events['type'] == 'Error']),
            'dispossessed': len(events[events['type'] == 'Dispossessed']),
            'miscontrol': len(events[events['type'] == 'Miscontrol']),
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
                    loc = row.get('location')
                    if pd.notna(loc) and isinstance(loc, (list, tuple, np.ndarray)) and len(loc) >= 2:
                        x = float(loc[0])
                        if x < 40:
                            metrics['ball_recoveries_defensive_third'] += 1
                        elif x < 80:
                            metrics['ball_recoveries_middle_third'] += 1
                        else:
                            metrics['ball_recoveries_offensive_third'] += 1
                except:
                    continue
        
        # Gardien (accès sécurisé)
        gk_events = events[events['type'] == 'Goal Keeper']
        if 'goalkeeper_type' in gk_events.columns:
            for gk_type in gk_events['goalkeeper_type'].dropna():
                gk_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(gk_type, 'name')
                if gk_name == 'Punch':
                    metrics['goalkeeper_punches'] += 1
                elif gk_name == 'Claim':
                    metrics['goalkeeper_claims'] += 1
                elif gk_name == 'Smother':
                    metrics['goalkeeper_smother'] += 1
        
        return metrics
    
    @staticmethod
    def _extract_dribble_carry_metrics(events: pd.DataFrame) -> Dict:
        """🏃 DRIBBLES & CARRIES : 10+ métriques"""
        dribbles = events[events['type'] == 'Dribble']
        carries = events[events['type'] == 'Carry']
        
        metrics = {
            'dribbles': len(dribbles),
            'dribbles_completed': 0,
            'dribbles_past_opponent': 0,
            'carries': len(carries),
            'carry_distance': 0.0,
            'progressive_carries': 0,
            'carries_into_box': 0,
            'carries_into_final_third': 0,
            'nutmegs': len(dribbles[dribbles.get('dribble_nutmeg', False) == True]) if 'dribble_nutmeg' in dribbles.columns else 0,
        }
        
        # Dribbles réussis (accès sécurisé)
        if 'dribble_outcome' in dribbles.columns:
            for outcome in dribbles['dribble_outcome'].dropna():
                outcome_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(outcome, 'name')
                if outcome_name == 'Complete':
                    metrics['dribbles_completed'] += 1
                    metrics['dribbles_past_opponent'] += 1
        
        # Carries
        if 'location' in carries.columns and 'carry_end_location' in carries.columns:
            for idx, row in carries.iterrows():
                try:
                    start = row.get('location')
                    end = row.get('carry_end_location')
                    
                    if pd.notna(start) and pd.notna(end) and isinstance(start, (list, tuple, np.ndarray)) and isinstance(end, (list, tuple, np.ndarray)):
                        if len(start) >= 2 and len(end) >= 2:
                            x_diff = float(end[0]) - float(start[0])
                            distance = np.sqrt((float(end[0]) - float(start[0]))**2 + (float(end[1]) - float(start[1]))**2)
                            metrics['carry_distance'] += distance
                            
                            if x_diff > 5:
                                metrics['progressive_carries'] += 1
                            
                            if float(end[0]) > 102 and 18 <= float(end[1]) <= 62:
                                metrics['carries_into_box'] += 1
                            
                            if float(end[0]) > 80:
                                metrics['carries_into_final_third'] += 1
                except:
                    continue
        
        return metrics
    
    @staticmethod
    def _extract_duel_metrics(events: pd.DataFrame) -> Dict:
        """⚔️ DUELS : 10+ métriques"""
        duels = events[events['type'] == 'Duel']
        
        metrics = {
            'duels_total': len(duels),
            'duels_won': 0,
            'duels_lost': 0,
            'aerial_duels': 0,
            'aerial_duels_won': 0,
            'ground_duels': 0,
            'ground_duels_won': 0,
            'loose_ball_duels': 0,
            'loose_ball_duels_won': 0,
        }
        
        # Duels (accès sécurisé)
        if 'duel_outcome' in duels.columns:
            for outcome in duels['duel_outcome'].dropna():
                outcome_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(outcome, 'name')
                if outcome_name == 'Won':
                    metrics['duels_won'] += 1
                elif outcome_name == 'Lost':
                    metrics['duels_lost'] += 1
        
        # Par type
        for idx, row in duels.iterrows():
            try:
                duel_type = row.get('duel_type')
                outcome = row.get('duel_outcome')
                
                type_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(duel_type, 'name')
                outcome_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(outcome, 'name')
                
                if 'Aerial' in type_name:
                    metrics['aerial_duels'] += 1
                    if outcome_name == 'Won':
                        metrics['aerial_duels_won'] += 1
                elif 'Ground' in type_name:
                    metrics['ground_duels'] += 1
                    if outcome_name == 'Won':
                        metrics['ground_duels_won'] += 1
                elif 'Loose Ball' in type_name:
                    metrics['loose_ball_duels'] += 1
                    if outcome_name == 'Won':
                        metrics['loose_ball_duels_won'] += 1
            except:
                continue
        
        return metrics
    
    @staticmethod
    def _extract_positional_metrics(events: pd.DataFrame) -> Dict:
        """📍 POSITION & ZONE : 10+ métriques"""
        metrics = {
            'actions_defensive_third': 0,
            'actions_middle_third': 0,
            'actions_attacking_third': 0,
            'zone_def_left': 0,
            'zone_def_center': 0,
            'zone_def_right': 0,
            'zone_mid_left': 0,
            'zone_mid_center': 0,
            'zone_mid_right': 0,
            'zone_att_left': 0,
            'zone_att_center': 0,
            'zone_att_right': 0,
            'touches': len(events),
            'touches_in_box': 0,
        }
        
        for idx, row in events.iterrows():
            try:
                loc = row.get('location')
                if pd.notna(loc) and isinstance(loc, (list, tuple, np.ndarray)) and len(loc) >= 2:
                    x, y = float(loc[0]), float(loc[1])
                    
                    # Tiers
                    if x < 40:
                        metrics['actions_defensive_third'] += 1
                        zone_x = 'def'
                    elif x < 80:
                        metrics['actions_middle_third'] += 1
                        zone_x = 'mid'
                    else:
                        metrics['actions_attacking_third'] += 1
                        zone_x = 'att'
                    
                    # 9 zones
                    zone_y = 'left' if y < 27 else ('center' if y < 53 else 'right')
                    metrics[f'zone_{zone_x}_{zone_y}'] += 1
                    
                    # Surface
                    if x > 102 and 18 <= y <= 62:
                        metrics['touches_in_box'] += 1
            except:
                continue
        
        return metrics
    
    @staticmethod
    def _extract_pressure_metrics(events: pd.DataFrame) -> Dict:
        """💪 PRESSION : 5+ métriques"""
        pressures = events[events['type'] == 'Pressure']
        
        metrics = {
            'pressures': len(pressures),
            'pressures_successful': 0,
            'pressures_defensive_third': 0,
            'pressures_middle_third': 0,
            'pressures_attacking_third': 0,
        }
        
        for idx, row in pressures.iterrows():
            try:
                loc = row.get('location')
                if pd.notna(loc) and isinstance(loc, (list, tuple, np.ndarray)) and len(loc) >= 2:
                    x = float(loc[0])
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
        """⭐ ÉVÉNEMENTS SPÉCIAUX : 10+ métriques"""
        metrics = {
            'fouls_committed': len(events[events['type'] == 'Foul Committed']),
            'fouls_won': len(events[events['type'] == 'Foul Won']),
            'yellow_cards': 0,
            'red_cards': 0,
            '50_50': len(events[events['type'] == '50/50']),
            'bad_behaviour': len(events[events['type'] == 'Bad Behaviour']),
            'substitutions': len(events[events['type'] == 'Substitution']),
            'offsides': len(events[events['type'] == 'Offside']),
        }
        
        # Cartons (accès sécurisé)
        fouls = events[events['type'] == 'Foul Committed']
        if 'foul_committed_card' in fouls.columns:
            for card in fouls['foul_committed_card'].dropna():
                card_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(card, 'name')
                if card_name == 'Yellow Card':
                    metrics['yellow_cards'] += 1
                elif card_name == 'Red Card':
                    metrics['red_cards'] += 1
        
        return metrics
    
    @staticmethod
    def _extract_expected_metrics(events: pd.DataFrame) -> Dict:
        """📊 xG & xA AVANCÉS : 5+ métriques"""
        shots = events[events['type'] == 'Shot']
        passes = events[events['type'] == 'Pass']
        
        metrics = {
            'xG_total': shots['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in shots.columns else 0,
            'xG_open_play': 0,
            'xG_set_piece': 0,
            'xA_total': 0,
            'xA_from_crosses': 0,
        }
        
        # xG par type
        if 'shot_type' in shots.columns and 'shot_statsbomb_xg' in shots.columns:
            for idx, row in shots.iterrows():
                try:
                    xg_val = row.get('shot_statsbomb_xg')
                    shot_type = row.get('shot_type')
                    
                    if pd.notna(xg_val):
                        type_name = UltraAdvancedMetricsExtractor._safe_get_dict_value(shot_type, 'name')
                        if type_name == 'Open Play':
                            metrics['xG_open_play'] += float(xg_val)
                        elif type_name:
                            metrics['xG_set_piece'] += float(xg_val)
                except:
                    continue
        
        # xA
        if 'pass_shot_assist' in passes.columns:
            key_passes = passes[passes['pass_shot_assist'] == True]
            
            for idx, kp in key_passes.iterrows():
                try:
                    next_events = events[events.index > idx].head(5)
                    next_shots = next_events[next_events['type'] == 'Shot']
                    
                    if not next_shots.empty and 'shot_statsbomb_xg' in next_shots.columns:
                        xg = next_shots.iloc[0].get('shot_statsbomb_xg')
                        if pd.notna(xg):
                            metrics['xA_total'] += float(xg)
                            
                            if kp.get('pass_cross', False):
                                metrics['xA_from_crosses'] += float(xg)
                except:
                    continue
        
        return metrics


if __name__ == "__main__":
    print("✅ Module ultra_advanced_metrics.py chargé !")
    print("📊 Extrait 100+ métriques depuis StatsBomb")
    print("🚀 3x plus de données que le système de base !")
