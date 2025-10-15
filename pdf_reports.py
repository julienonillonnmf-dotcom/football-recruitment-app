# pdf_reports.py
"""
Générateur de rapports PDF pour le scouting
Version complète prête à l'emploi
"""

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class ScoutingReportGenerator:
    """Génère des rapports PDF complets"""
    
    def __init__(self, club_name: str = "Football Club"):
        self.club_name = club_name
        
    def generate_player_report(self,
                              player_data: pd.Series,
                              similar_players: pd.DataFrame,
                              visualizations: Dict[str, plt.Figure],
                              output_path: str):
        """Génère un rapport complet sur un joueur"""
        try:
            with PdfPages(output_path) as pdf:
                # Page 1: Garde
                self._create_cover_page(pdf, player_data)
                
                # Page 2: Résumé
                self._create_executive_summary(pdf, player_data)
                
                # Page 3: Stats détaillées
                self._create_stats_page(pdf, player_data)
                
                # Pages visualisations
                for viz_name, fig in visualizations.items():
                    if fig is not None:
                        try:
                            pdf.savefig(fig, bbox_inches='tight')
                            plt.close(fig)
                        except:
                            pass
                
                # Page comparaison
                if not similar_players.empty:
                    self._create_comparison_page(pdf, player_data, similar_players)
                
                # Page recommandations
                self._create_recommendations_page(pdf, player_data)
                
                # Métadonnées
                d = pdf.infodict()
                d['Title'] = f'Rapport - {player_data.get("player", "Joueur")}'
                d['Author'] = self.club_name
                d['Subject'] = 'Analyse de joueur'
                d['CreationDate'] = datetime.now()
            
            print(f"✅ Rapport PDF généré: {output_path}")
            
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            raise e
    
    def _create_cover_page(self, pdf: PdfPages, player_data: pd.Series):
        """Page de garde"""
        try:
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            ax.text(0.5, 0.7, 'RAPPORT DE SCOUTING',
                   ha='center', fontsize=28, weight='bold',
                   transform=ax.transAxes)
            
            player_name = player_data.get('player', 'Joueur Inconnu')
            ax.text(0.5, 0.55, player_name,
                   ha='center', fontsize=36, weight='bold',
                   color='#1f77b4', transform=ax.transAxes)
            
            info_text = f"""
            Équipe: {player_data.get('team', 'N/A')}
            Matchs joués: {player_data.get('matches_played', 'N/A')}
            """
            
            ax.text(0.5, 0.35, info_text,
                   ha='center', fontsize=14,
                   transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
            
            ax.text(0.5, 0.1,
                   f'{self.club_name}\n{datetime.now().strftime("%d/%m/%Y")}',
                   ha='center', fontsize=12, style='italic',
                   transform=ax.transAxes)
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            print(f"❌ Erreur cover page: {e}")
    
    def _create_executive_summary(self, pdf: PdfPages, player_data: pd.Series):
        """Résumé exécutif"""
        try:
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            ax.text(0.5, 0.95, 'RÉSUMÉ EXÉCUTIF',
                   ha='center', fontsize=20, weight='bold',
                   transform=ax.transAxes)
            
            # Points forts
            strengths = self._identify_strengths(player_data)
            y_pos = 0.85
            
            ax.text(0.1, y_pos, '✓ POINTS FORTS',
                   fontsize=16, weight='bold', color='green',
                   transform=ax.transAxes)
            
            y_pos -= 0.05
            for strength in strengths[:5]:
                ax.text(0.15, y_pos, f'• {strength}',
                       fontsize=12, transform=ax.transAxes)
                y_pos -= 0.04
            
            # Points faibles
            y_pos -= 0.05
            weaknesses = self._identify_weaknesses(player_data)
            
            ax.text(0.1, y_pos, '⚠ POINTS À AMÉLIORER',
                   fontsize=16, weight='bold', color='orange',
                   transform=ax.transAxes)
            
            y_pos -= 0.05
            for weakness in weaknesses[:5]:
                ax.text(0.15, y_pos, f'• {weakness}',
                       fontsize=12, transform=ax.transAxes)
                y_pos -= 0.04
            
            # Verdict
            y_pos -= 0.05
            verdict = self._generate_verdict(player_data)
            
            ax.text(0.1, y_pos, 'VERDICT',
                   fontsize=16, weight='bold',
                   transform=ax.transAxes)
            
            y_pos -= 0.05
            ax.text(0.1, y_pos, verdict,
                   fontsize=11, transform=ax.transAxes,
                   wrap=True,
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            print(f"❌ Erreur summary: {e}")
    
    def _create_stats_page(self, pdf: PdfPages, player_data: pd.Series):
        """Page de statistiques"""
        try:
            fig, axes = plt.subplots(3, 2, figsize=(8.27, 11.69))
            fig.suptitle('STATISTIQUES DÉTAILLÉES', fontsize=20, weight='bold')
            
            categories = {
                'Offensif': ['goals_per_90', 'xG_per_90', 'shots_per_90', 'shot_accuracy'],
                'Création': ['assists_per_90', 'key_passes_per_90', 'passes_per_90'],
                'Dribbles': ['dribbles_per_90', 'dribble_success_rate'],
                'Défensif': ['tackles_per_90', 'interceptions_per_90'],
                'Physique': ['fouls_committed', 'fouls_won'],
                'Global': ['matches_played']
            }
            
            for idx, (category, metrics) in enumerate(categories.items()):
                ax = axes.flatten()[idx]
                
                values = []
                labels = []
                
                for metric in metrics:
                    if metric in player_data.index:
                        val = player_data[metric]
                        if pd.notna(val):
                            try:
                                values.append(float(val))
                                labels.append(metric.replace('_', ' ').title())
                            except (ValueError, TypeError):
                                # Ignorer les valeurs non numériques
                                pass
                
                if values:
                    bars = ax.barh(labels, values, color='steelblue', alpha=0.7)
                    
                    for bar, val in zip(bars, values):
                        ax.text(val, bar.get_y() + bar.get_height()/2,
                               f' {val:.2f}', va='center', fontsize=9)
                    
                    ax.set_title(category, fontsize=12, weight='bold')
                    ax.grid(axis='x', alpha=0.3)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                else:
                    ax.text(0.5, 0.5, 'Données non disponibles',
                           ha='center', va='center', transform=ax.transAxes)
                    ax.axis('off')
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            print(f"❌ Erreur stats page: {e}")
    
    def _create_comparison_page(self, pdf: PdfPages, player_data: pd.Series, similar: pd.DataFrame):
        """Page de comparaison"""
        try:
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.suptitle('JOUEURS SIMILAIRES', fontsize=20, weight='bold', y=0.98)
            
            ax = fig.add_subplot(111)
            ax.axis('tight')
            ax.axis('off')
            
            if not similar.empty:
                cols = ['player', 'team', 'similarity_score']
                available_cols = [c for c in cols if c in similar.columns]
                
                if available_cols:
                    table_data = similar[available_cols].head(10).copy()
                    
                    # Formater les valeurs
                    if 'similarity_score' in table_data.columns:
                        table_data['similarity_score'] = table_data['similarity_score'].apply(lambda x: f'{x:.2f}' if pd.notna(x) else 'N/A')
                    
                    table = ax.table(
                        cellText=table_data.values,
                        colLabels=table_data.columns,
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 0.9]
                    )
                    
                    table.auto_set_font_size(False)
                    table.set_fontsize(9)
                    table.scale(1, 2)
                    
                    for (i, j), cell in table.get_celld().items():
                        if i == 0:
                            cell.set_facecolor('#1f77b4')
                            cell.set_text_props(weight='bold', color='white')
                        else:
                            cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            print(f"❌ Erreur comparison: {e}")
    
    def _create_recommendations_page(self, pdf: PdfPages, player_data: pd.Series):
        """Page de recommandations"""
        try:
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            ax.text(0.5, 0.95, 'RECOMMANDATIONS',
                   ha='center', fontsize=20, weight='bold',
                   transform=ax.transAxes)
            
            recommendations = self._generate_recommendations(player_data)
            
            y_pos = 0.85
            for i, rec in enumerate(recommendations, 1):
                ax.text(0.1, y_pos, f'{i}. {rec}',
                       fontsize=12, transform=ax.transAxes, wrap=True)
                y_pos -= 0.08
            
            ax.text(0.5, 0.15,
                   'Rapport généré par Football Analytics AI',
                   ha='center', fontsize=10, style='italic',
                   color='gray', transform=ax.transAxes)
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
        except Exception as e:
            print(f"❌ Erreur recommendations: {e}")
    
    def _identify_strengths(self, player_data: pd.Series) -> List[str]:
        """Identifie les points forts"""
        strengths = []
        
        try:
            # ✅ Utiliser des conversions sécurisées
            goals_per_90 = self._safe_float(player_data.get('goals_per_90', 0))
            pass_rate = self._safe_float(player_data.get('pass_completion_rate', 0))
            dribble_rate = self._safe_float(player_data.get('dribble_success_rate', 0))
            tackles = self._safe_float(player_data.get('tackles_per_90', 0))
            assists = self._safe_float(player_data.get('assists_per_90', 0))
            
            if goals_per_90 > 0.5:
                strengths.append('Excellent finisseur')
            if pass_rate > 85:
                strengths.append('Très bonne précision de passe')
            if dribble_rate > 65:
                strengths.append('Excellent dribbleur')
            if tackles > 3:
                strengths.append('Bon récupérateur')
            if assists > 0.3:
                strengths.append('Très bon créateur')
        except Exception as e:
            print(f"⚠️ Erreur dans _identify_strengths: {e}")
        
        return strengths if strengths else ['Profil équilibré']
    
    def _identify_weaknesses(self, player_data: pd.Series) -> List[str]:
        """Identifie les points faibles"""
        weaknesses = []
        
        try:
            shot_acc = self._safe_float(player_data.get('shot_accuracy', 50))
            pass_rate = self._safe_float(player_data.get('pass_completion_rate', 80))
            fouls = self._safe_float(player_data.get('fouls_committed', 0))
            
            if shot_acc < 35:
                weaknesses.append('Précision des tirs à améliorer')
            if pass_rate < 75:
                weaknesses.append('Précision de passe insuffisante')
            if fouls > 2:
                weaknesses.append('Discipline à travailler')
        except Exception as e:
            print(f"⚠️ Erreur dans _identify_weaknesses: {e}")
        
        return weaknesses if weaknesses else ['Peu de faiblesses identifiées']
    
    def _generate_verdict(self, player_data: pd.Series) -> str:
        """Génère un verdict"""
        try:
            # Calculer un score simplifié
            goals = self._safe_float(player_data.get('goals_per_90', 0))
            assists = self._safe_float(player_data.get('assists_per_90', 0))
            pass_rate = self._safe_float(player_data.get('pass_completion_rate', 0))
            
            score = (goals * 20) + (assists * 15) + (pass_rate * 0.5)
            
            if score >= 40:
                return "Joueur de haut niveau. Recommandation forte."
            elif score >= 25:
                return "Bon joueur avec potentiel. À surveiller."
            elif score >= 15:
                return "Joueur moyen. Rôle de rotation possible."
            else:
                return "Profil en dessous des standards."
        except Exception as e:
            print(f"⚠️ Erreur dans _generate_verdict: {e}")
            return "Évaluation nécessaire."
    
    def _generate_recommendations(self, player_data: pd.Series) -> List[str]:
        """Génère des recommandations"""
        recs = []
        
        try:
            matches = int(self._safe_float(player_data.get('matches_played', 0)))
            goals = self._safe_float(player_data.get('goals_per_90', 0))
            assists = self._safe_float(player_data.get('assists_per_90', 0))
            tackles = self._safe_float(player_data.get('tackles_per_90', 0))
            
            recs.append(f"Expérience: {matches} matchs cette saison")
            
            if goals > 0.4:
                recs.append("Utiliser comme option offensive prioritaire")
            
            if assists > 0.25:
                recs.append("Peut jouer un rôle de créateur")
            
            if tackles > 2:
                recs.append("Contribue en phase défensive")
            
            recs.append("Intégration progressive sur 3-6 mois")
        except Exception as e:
            print(f"⚠️ Erreur dans _generate_recommendations: {e}")
            recs = ["Analyse détaillée recommandée"]
        
        return recs
    
    def _safe_float(self, value) -> float:
        """Convertit une valeur en float de manière sécurisée"""
        try:
            if pd.isna(value):
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0


if __name__ == "__main__":
    print("✅ Module pdf_reports.py chargé avec succès!")
    print("Classe disponible: ScoutingReportGenerator")
