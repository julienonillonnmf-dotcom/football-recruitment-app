# advanced_visualizations.py
"""
Visualisations avancées pour le football
Version complète prête à l'emploi
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')


class FootballVisualizer:
    """Crée des visualisations football professionnelles"""
    
    @staticmethod
    def create_radar_chart(player_data: pd.Series,
                          metrics: List[str],
                          player_name: str,
                          league_avg: pd.Series = None) -> plt.Figure:
        """Crée un radar chart pour un joueur"""
        try:
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # Préparer les données
            values = []
            for metric in metrics:
                val = player_data.get(metric, 0)
                if pd.notna(val):
                    values.append(float(val))
                else:
                    values.append(0)
            
            # Normaliser entre 0 et 100
            max_vals = [100 if 'rate' in m or 'accuracy' in m else 10 for m in metrics]
            normalized = [min((v / mv) * 100, 100) for v, mv in zip(values, max_vals)]
            
            # Angles
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            normalized += normalized[:1]
            angles += angles[:1]
            
            # Plot
            ax.plot(angles, normalized, 'o-', linewidth=2, label=player_name, color='#1f77b4')
            ax.fill(angles, normalized, alpha=0.25, color='#1f77b4')
            
            # Moyenne ligue si disponible
            if league_avg is not None:
                avg_values = []
                for metric in metrics:
                    val = league_avg.get(metric, 0)
                    avg_values.append(float(val) if pd.notna(val) else 0)
                avg_normalized = [min((v / mv) * 100, 100) for v, mv in zip(avg_values, max_vals)]
                avg_normalized += avg_normalized[:1]
                
                ax.plot(angles, avg_normalized, 'o--', linewidth=2, 
                       label='Moyenne Ligue', color='gray', alpha=0.5)
                ax.fill(angles, avg_normalized, alpha=0.1, color='gray')
            
            # Configuration
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics], size=10)
            ax.set_ylim(0, 100)
            ax.set_title(f'Profil de {player_name}', size=16, pad=20, weight='bold')
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            ax.grid(True)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"❌ Erreur radar chart: {e}")
            fig, ax = plt.subplots(figsize=(10, 10))
            ax.text(0.5, 0.5, f'Erreur: {e}', ha='center', va='center')
            return fig
    
    @staticmethod
    def create_comparison_bars(players: pd.DataFrame,
                              metrics: List[str],
                              title: str = 'Comparaison') -> plt.Figure:
        """Crée des barres de comparaison"""
        try:
            n_metrics = len(metrics)
            n_cols = 2
            n_rows = (n_metrics + 1) // 2
            
            fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, 
                                    figsize=(14, n_rows * 3))
            if n_rows == 1:
                axes = axes.reshape(1, -1)
            
            colors = sns.color_palette('husl', len(players))
            
            for idx, metric in enumerate(metrics):
                row = idx // n_cols
                col = idx % n_cols
                ax = axes[row, col]
                
                if metric in players.columns:
                    values = players[metric].fillna(0).values
                    names = players['player'].values
                    
                    bars = ax.barh(names, values, color=colors)
                    
                    for i, (bar, val) in enumerate(zip(bars, values)):
                        ax.text(val, i, f' {val:.2f}', 
                               va='center', fontsize=9)
                    
                    ax.set_xlabel(metric.replace('_', ' ').title(), fontsize=10)
                    ax.grid(axis='x', alpha=0.3)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                else:
                    ax.text(0.5, 0.5, f'{metric}\nNon disponible', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.axis('off')
            
            # Cacher axes vides
            for idx in range(n_metrics, n_rows * n_cols):
                row = idx // n_cols
                col = idx % n_cols
                axes[row, col].axis('off')
            
            fig.suptitle(title, fontsize=16, weight='bold')
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"❌ Erreur comparison bars: {e}")
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.text(0.5, 0.5, f'Erreur: {e}', ha='center', va='center')
            return fig
    
    @staticmethod
    def create_ranking_chart(df: pd.DataFrame,
                           metric: str,
                           top_n: int = 15,
                           title: str = None) -> plt.Figure:
        """Crée un graphique de classement"""
        try:
            if metric not in df.columns:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.text(0.5, 0.5, f'Métrique "{metric}" non disponible',
                       ha='center', va='center')
                return fig
            
            df_sorted = df.nlargest(top_n, metric)
            
            fig, ax = plt.subplots(figsize=(12, max(8, top_n * 0.4)))
            
            y_pos = np.arange(len(df_sorted))
            values = df_sorted[metric].fillna(0).values
            names = df_sorted['player'].values
            
            # Colormap
            colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(values)))
            
            bars = ax.barh(y_pos, values, color=colors)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            ax.invert_yaxis()
            
            for i, (bar, val) in enumerate(zip(bars, values)):
                ax.text(val, i, f' {val:.2f}',
                       va='center', fontsize=10, weight='bold')
            
            ax.set_xlabel(metric.replace('_', ' ').title(), 
                         fontsize=12, weight='bold')
            ax.set_title(title or f'Top {top_n} - {metric}',
                        fontsize=16, weight='bold', pad=20)
            ax.grid(axis='x', alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"❌ Erreur ranking chart: {e}")
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, f'Erreur: {e}', ha='center', va='center')
            return fig
    
    @staticmethod
    def create_scatter_comparison(df: pd.DataFrame,
                                 x_metric: str,
                                 y_metric: str,
                                 size_metric: str = None,
                                 color_by: str = 'team',
                                 highlight_players: List[str] = None) -> plt.Figure:
        """Crée un scatter plot de comparaison"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            if x_metric not in df.columns or y_metric not in df.columns:
                ax.text(0.5, 0.5, 'Métriques non disponibles',
                       ha='center', va='center')
                return fig
            
            # Tailles
            if size_metric and size_metric in df.columns:
                sizes = df[size_metric].fillna(0) * 10
            else:
                sizes = 100
            
            # Couleurs
            if color_by in df.columns:
                unique_vals = df[color_by].unique()
                n_colors = min(len(unique_vals), 10)
                color_map = dict(zip(unique_vals, sns.color_palette('tab10', n_colors)))
                colors = df[color_by].map(color_map).fillna('gray')
            else:
                colors = 'steelblue'
            
            # Plot principal
            ax.scatter(df[x_metric], df[y_metric],
                      s=sizes, c=colors, alpha=0.6, edgecolors='black', linewidth=0.5)
            
            # Highlight
            if highlight_players:
                highlight_df = df[df['player'].isin(highlight_players)]
                ax.scatter(highlight_df[x_metric], highlight_df[y_metric],
                          s=200, c='red', marker='*', edgecolors='black', 
                          linewidth=2, zorder=5, label='Joueurs sélectionnés')
                
                for idx, row in highlight_df.iterrows():
                    ax.annotate(row['player'],
                               (row[x_metric], row[y_metric]),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=9, weight='bold')
            
            ax.set_xlabel(x_metric.replace('_', ' ').title(), fontsize=12)
            ax.set_ylabel(y_metric.replace('_', ' ').title(), fontsize=12)
            ax.set_title(f'{y_metric} vs {x_metric}', fontsize=14, weight='bold')
            ax.grid(True, alpha=0.3)
            
            if highlight_players:
                ax.legend()
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"❌ Erreur scatter: {e}")
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, f'Erreur: {e}', ha='center', va='center')
            return fig
    
    @staticmethod
    def create_performance_timeline(df: pd.DataFrame,
                                   player_name: str,
                                   metrics: List[str]) -> plt.Figure:
        """Crée une timeline de performance (si données temporelles)"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            player_data = df[df['player'] == player_name]
            
            if player_data.empty:
                ax.text(0.5, 0.5, f'Joueur "{player_name}" non trouvé',
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Si pas de données temporelles, afficher un message
            ax.text(0.5, 0.5, 
                   'Timeline nécessite des données par match\n(Fonctionnalité future)',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=12)
            
            return fig
            
        except Exception as e:
            print(f"❌ Erreur timeline: {e}")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, f'Erreur: {e}', ha='center', va='center')
            return fig


if __name__ == "__main__":
    print("✅ Module advanced_visualizations.py chargé avec succès!")
    print("Classe disponible: FootballVisualizer")
