# advanced_visualizations.py
"""
Visualisations avancées pour profils de joueurs
Graphiques professionnels et détaillés
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Configuration style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class AdvancedPlayerVisualizations:
    """Créateur de visualisations avancées pour joueurs"""
    
    @staticmethod
    def create_complete_player_profile(player_data: pd.Series, 
                                       league_data: pd.DataFrame,
                                       player_name: str) -> plt.Figure:
        """
        📊 PROFIL COMPLET : Combinaison de 6 graphiques
        - Radar chart (performances globales)
        - Bar chart comparatif (vs moyenne ligue)
        - Heatmap positions
        - Timeline progression
        - Distribution stats clés
        - Tableau récapitulatif
        """
        try:
            fig = plt.figure(figsize=(20, 12))
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
            
            # 1. RADAR CHART (grand, en haut à gauche)
            ax_radar = fig.add_subplot(gs[0:2, 0], projection='polar')
            AdvancedPlayerVisualizations._create_radar_chart(
                ax_radar, player_data, league_data, player_name
            )
            
            # 2. BAR CHART COMPARATIF (en haut au milieu)
            ax_bar = fig.add_subplot(gs[0, 1])
            AdvancedPlayerVisualizations._create_comparison_bars(
                ax_bar, player_data, league_data
            )
            
            # 3. HEATMAP POSITIONS (en haut à droite)
            ax_heat = fig.add_subplot(gs[0, 2])
            AdvancedPlayerVisualizations._create_position_heatmap(
                ax_heat, player_data
            )
            
            # 4. STATS PAR CATÉGORIE (milieu gauche)
            ax_cat = fig.add_subplot(gs[1, 1])
            AdvancedPlayerVisualizations._create_category_breakdown(
                ax_cat, player_data
            )
            
            # 5. DISTRIBUTION (milieu droite)
            ax_dist = fig.add_subplot(gs[1, 2])
            AdvancedPlayerVisualizations._create_percentile_chart(
                ax_dist, player_data, league_data
            )
            
            # 6. TABLEAU STATISTIQUES (en bas)
            ax_table = fig.add_subplot(gs[2, :])
            AdvancedPlayerVisualizations._create_stats_table(
                ax_table, player_data
            )
            
            # Titre principal
            fig.suptitle(
                f'📊 PROFIL DÉTAILLÉ - {player_name}',
                fontsize=20, fontweight='bold', y=0.98
            )
            
            return fig
            
        except Exception as e:
            print(f"❌ Erreur profil complet: {e}")
            return plt.figure(figsize=(10, 6))
    
    @staticmethod
    def _create_radar_chart(ax, player_data, league_data, player_name):
        """Radar chart avec 8-12 métriques clés"""
        try:
            # Sélection des métriques selon disponibilité
            metrics = []
            labels = []
            
            metric_map = {
                'goals_per_90': 'Buts/90',
                'xG_per_90': 'xG/90',
                'assists_per_90': 'Assists/90',
                'key_passes_per_90': 'Passes clés/90',
                'pass_completion_rate': 'Précision passes',
                'dribbles_per_90': 'Dribbles/90',
                'tackles_per_90': 'Tacles/90',
                'interceptions_per_90': 'Interceptions/90',
                'progressive_passes': 'Passes prog.',
                'shots_per_90': 'Tirs/90',
            }
            
            for col, label in metric_map.items():
                if col in player_data.index and col in league_data.columns:
                    try:
                        # Normaliser par rapport à la ligue (percentile)
                        player_val = float(player_data[col])
                        league_vals = league_data[col].dropna()
                        
                        if len(league_vals) > 0:
                            percentile = (league_vals < player_val).sum() / len(league_vals) * 100
                            metrics.append(percentile)
                            labels.append(label)
                    except:
                        continue
            
            if len(metrics) < 3:
                ax.text(0.5, 0.5, 'Données insuffisantes\npour le radar chart',
                       ha='center', va='center', transform=ax.transAxes)
                return
            
            # Créer le radar
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            metrics += metrics[:1]
            angles += angles[:1]
            
            ax.plot(angles, metrics, 'o-', linewidth=2, label=player_name, color='#FF6B6B')
            ax.fill(angles, metrics, alpha=0.25, color='#FF6B6B')
            
            # Ajouter cercles de référence
            for perc in [25, 50, 75]:
                ax.plot(angles, [perc] * len(angles), '--', alpha=0.3, color='gray', linewidth=0.5)
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, size=9)
            ax.set_ylim(0, 100)
            ax.set_yticks([25, 50, 75, 100])
            ax.set_yticklabels(['25%', '50%', '75%', '100%'], size=8)
            ax.grid(True, alpha=0.3)
            ax.set_title('Performance Relative (Percentiles)', pad=20, fontweight='bold')
            
        except Exception as e:
            print(f"⚠️ Erreur radar: {e}")
    
    @staticmethod
    def _create_comparison_bars(ax, player_data, league_data):
        """Barres comparatives joueur vs moyenne ligue"""
        try:
            metrics = {
                'Buts/90': 'goals_per_90',
                'Assists/90': 'assists_per_90',
                'Tirs/90': 'shots_per_90',
                'Tacles/90': 'tackles_per_90',
                'Précision%': 'pass_completion_rate',
            }
            
            player_vals = []
            league_avgs = []
            labels = []
            
            for label, col in metrics.items():
                if col in player_data.index and col in league_data.columns:
                    try:
                        player_vals.append(float(player_data[col]))
                        league_avgs.append(float(league_data[col].mean()))
                        labels.append(label)
                    except:
                        continue
            
            if not labels:
                ax.text(0.5, 0.5, 'Données insuffisantes', ha='center', va='center')
                return
            
            x = np.arange(len(labels))
            width = 0.35
            
            ax.bar(x - width/2, player_vals, width, label='Joueur', color='#4ECDC4')
            ax.bar(x + width/2, league_avgs, width, label='Moyenne Ligue', color='#95E1D3', alpha=0.7)
            
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.legend()
            ax.set_title('Comparaison vs Moyenne Ligue', fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
        except Exception as e:
            print(f"⚠️ Erreur barres: {e}")
    
    @staticmethod
    def _create_position_heatmap(ax, player_data):
        """Heatmap des zones d'activité (9 zones)"""
        try:
            zones = [
                ['zone_att_left', 'zone_att_center', 'zone_att_right'],
                ['zone_mid_left', 'zone_mid_center', 'zone_mid_right'],
                ['zone_def_left', 'zone_def_center', 'zone_def_right']
            ]
            
            heatmap_data = []
            for row in zones:
                row_data = []
                for zone in row:
                    if zone in player_data.index:
                        try:
                            row_data.append(float(player_data[zone]))
                        except:
                            row_data.append(0)
                    else:
                        row_data.append(0)
                heatmap_data.append(row_data)
            
            heatmap_array = np.array(heatmap_data)
            
            if heatmap_array.sum() == 0:
                ax.text(0.5, 0.5, 'Données de position\nnon disponibles',
                       ha='center', va='center')
                return
            
            # Normaliser
            if heatmap_array.max() > 0:
                heatmap_array = heatmap_array / heatmap_array.max() * 100
            
            im = ax.imshow(heatmap_array, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
            
            # Labels
            ax.set_xticks([0, 1, 2])
            ax.set_xticklabels(['Gauche', 'Centre', 'Droit'])
            ax.set_yticks([0, 1, 2])
            ax.set_yticklabels(['Attaque', 'Milieu', 'Défense'])
            
            # Valeurs dans les cellules
            for i in range(3):
                for j in range(3):
                    text = ax.text(j, i, f'{heatmap_array[i, j]:.0f}',
                                 ha="center", va="center", color="black", fontsize=10, fontweight='bold')
            
            ax.set_title('Heatmap - Zones d\'Activité (%)', fontweight='bold')
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            
        except Exception as e:
            print(f"⚠️ Erreur heatmap: {e}")
    
    @staticmethod
    def _create_category_breakdown(ax, player_data):
        """Graphique par catégories (Attaque, Création, Défense)"""
        try:
            categories = {
                'Attaque': ['goals_per_90', 'shots_per_90', 'xG_per_90'],
                'Création': ['assists_per_90', 'key_passes_per_90', 'progressive_passes'],
                'Défense': ['tackles_per_90', 'interceptions_per_90', 'clearances_per_90'],
            }
            
            category_scores = {}
            
            for cat, metrics in categories.items():
                scores = []
                for metric in metrics:
                    if metric in player_data.index:
                        try:
                            val = float(player_data[metric])
                            scores.append(val)
                        except:
                            pass
                
                if scores:
                    category_scores[cat] = np.mean(scores)
            
            if not category_scores:
                ax.text(0.5, 0.5, 'Données insuffisantes', ha='center', va='center')
                return
            
            # Graphique en barres horizontales
            categories_list = list(category_scores.keys())
            values = list(category_scores.values())
            colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
            
            bars = ax.barh(categories_list, values, color=colors[:len(categories_list)])
            
            # Ajouter valeurs
            for i, (bar, val) in enumerate(zip(bars, values)):
                ax.text(val, i, f'  {val:.2f}', va='center', fontweight='bold')
            
            ax.set_xlabel('Score Moyen')
            ax.set_title('Performance par Catégorie', fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
        except Exception as e:
            print(f"⚠️ Erreur catégories: {e}")
    
    @staticmethod
    def _create_percentile_chart(ax, player_data, league_data):
        """Graphique en barres des percentiles"""
        try:
            metrics = {
                'Buts': 'goals_per_90',
                'xG': 'xG_per_90',
                'Passes': 'passes_per_90',
                'Dribbles': 'dribbles_per_90',
                'Tacles': 'tackles_per_90',
            }
            
            percentiles = []
            labels = []
            
            for label, col in metrics.items():
                if col in player_data.index and col in league_data.columns:
                    try:
                        player_val = float(player_data[col])
                        league_vals = league_data[col].dropna()
                        
                        if len(league_vals) > 0:
                            perc = (league_vals < player_val).sum() / len(league_vals) * 100
                            percentiles.append(perc)
                            labels.append(label)
                    except:
                        continue
            
            if not percentiles:
                ax.text(0.5, 0.5, 'Données insuffisantes', ha='center', va='center')
                return
            
            colors = ['#2ecc71' if p >= 75 else '#f39c12' if p >= 50 else '#e74c3c' for p in percentiles]
            
            bars = ax.barh(labels, percentiles, color=colors)
            
            # Ajouter valeurs
            for i, (bar, perc) in enumerate(zip(bars, percentiles)):
                ax.text(perc, i, f' {perc:.0f}%', va='center', fontweight='bold')
            
            ax.set_xlim(0, 100)
            ax.set_xlabel('Percentile')
            ax.set_title('Classement Relatif (Percentiles)', fontweight='bold')
            ax.axvline(50, color='gray', linestyle='--', alpha=0.5, label='Médiane')
            ax.axvline(75, color='green', linestyle='--', alpha=0.5, label='Top 25%')
            ax.legend(loc='lower right', fontsize=8)
            ax.grid(axis='x', alpha=0.3)
            
        except Exception as e:
            print(f"⚠️ Erreur percentiles: {e}")
    
    @staticmethod
    def _create_stats_table(ax, player_data):
        """Tableau récapitulatif des statistiques principales"""
        try:
            ax.axis('off')
            
            # Préparer les données du tableau
            stats_to_show = {
                '⚽ ATTAQUE': [
                    ('Buts/90', 'goals_per_90'),
                    ('xG/90', 'xG_per_90'),
                    ('Tirs/90', 'shots_per_90'),
                    ('Précision tirs (%)', 'shot_accuracy'),
                ],
                '🎯 CRÉATION': [
                    ('Assists/90', 'assists_per_90'),
                    ('Passes clés/90', 'key_passes_per_90'),
                    ('Passes progressives', 'progressive_passes'),
                    ('Taux passe (%)', 'pass_completion_rate'),
                ],
                '🛡️ DÉFENSE': [
                    ('Tacles/90', 'tackles_per_90'),
                    ('Interceptions/90', 'interceptions_per_90'),
                    ('Récupérations', 'ball_recoveries'),
                    ('Duels gagnés (%)', 'duels_won'),
                ],
                '🏃 MOBILITÉ': [
                    ('Dribbles/90', 'dribbles_per_90'),
                    ('Dribbles réussis (%)', 'dribble_success_rate'),
                    ('Carries', 'carries'),
                    ('Distance carries', 'carry_distance'),
                ],
            }
            
            table_data = []
            
            for category, metrics in stats_to_show.items():
                # En-tête de catégorie
                table_data.append([category, '', ''])
                
                for label, col in metrics:
                    if col in player_data.index:
                        try:
                            val = float(player_data[col])
                            if 'rate' in col or 'accuracy' in col or '%' in label:
                                table_data.append(['  ' + label, f'{val:.1f}%', ''])
                            elif 'distance' in col:
                                table_data.append(['  ' + label, f'{val:.0f}m', ''])
                            else:
                                table_data.append(['  ' + label, f'{val:.2f}', ''])
                        except:
                            table_data.append(['  ' + label, 'N/A', ''])
                    else:
                        table_data.append(['  ' + label, 'N/A', ''])
            
            # Créer le tableau
            if table_data:
                table = ax.table(
                    cellText=table_data,
                    colLabels=['Statistique', 'Valeur', ''],
                    cellLoc='left',
                    loc='center',
                    colWidths=[0.5, 0.25, 0.25]
                )
                
                table.auto_set_font_size(False)
                table.set_fontsize(9)
                table.scale(1, 2)
                
                # Style
                for i, key in enumerate(table_data):
                    if key[0] in stats_to_show.keys():
                        for j in range(3):
                            cell = table[(i+1, j)]
                            cell.set_facecolor('#E8E8E8')
                            cell.set_text_props(weight='bold')
                
                ax.set_title('📋 Statistiques Détaillées', fontweight='bold', pad=10)
            
        except Exception as e:
            print(f"⚠️ Erreur tableau: {e}")
    
    @staticmethod
    def create_comparison_chart(players_data: pd.DataFrame,
                               player_names: list,
                               metrics: list = None) -> plt.Figure:
        """
        📊 Graphique de comparaison entre plusieurs joueurs
        """
        try:
            if metrics is None:
                metrics = ['goals_per_90', 'assists_per_90', 'passes_per_90',
                          'tackles_per_90', 'dribbles_per_90']
            
            fig, axes = plt.subplots(2, 3, figsize=(18, 10))
            axes = axes.flatten()
            
            for idx, metric in enumerate(metrics[:6]):
                ax = axes[idx]
                
                if metric not in players_data.columns:
                    ax.text(0.5, 0.5, f'{metric}\nnon disponible',
                           ha='center', va='center')
                    continue
                
                # Filtrer les joueurs
                data = players_data[players_data['player'].isin(player_names)]
                
                if data.empty:
                    continue
                
                # Créer le graphique
                values = []
                names = []
                for name in player_names:
                    player_data = data[data['player'] == name]
                    if not player_data.empty and metric in player_data.columns:
                        try:
                            val = float(player_data[metric].iloc[0])
                            values.append(val)
                            names.append(name.split()[-1])  # Nom de famille
                        except:
                            continue
                
                if values:
                    colors = plt.cm.viridis(np.linspace(0, 1, len(values)))
                    bars = ax.bar(names, values, color=colors)
                    
                    # Ajouter valeurs
                    for bar, val in zip(bars, values):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
                    
                    ax.set_title(metric.replace('_', ' ').title(), fontweight='bold')
                    ax.grid(axis='y', alpha=0.3)
                    
                    if len(names) > 3:
                        ax.tick_params(axis='x', rotation=45)
            
            # Supprimer les axes vides
            for idx in range(len(metrics), 6):
                fig.delaxes(axes[idx])
            
            fig.suptitle('🔀 Comparaison de Joueurs', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            print(f"❌ Erreur comparaison: {e}")
            return plt.figure(figsize=(10, 6))


if __name__ == "__main__":
    print("✅ Module advanced_visualizations.py chargé !")
    print("📊 Visualisations professionnelles disponibles")
