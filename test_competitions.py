# test_competitions.py
"""
Script pour tester les combinaisons competition_id/season_id disponibles
"""

import requests

def test_competition(comp_id, season_id, name):
    """Teste si une combinaison existe"""
    url = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{comp_id}/{season_id}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: ({comp_id}, {season_id}) - OK")
            return True
        else:
            print(f"❌ {name}: ({comp_id}, {season_id}) - NOT FOUND")
            return False
    except Exception as e:
        print(f"❌ {name}: ({comp_id}, {season_id}) - ERROR: {e}")
        return False

# Tester toutes les combinaisons
print("🔍 Test des compétitions StatsBomb...\n")

competitions_to_test = [
    # Premier League
    (9, 1, "Premier League 2015/16"),
    (9, 2, "Premier League 2016/17"),
    (9, 3, "Premier League 2017/18"),
    (9, 4, "Premier League 2018/19"),
    (9, 27, "Premier League 2003/04"),
    (9, 42, "Premier League 2020/21"),
    
    # La Liga
    (11, 1, "La Liga 2015/16"),
    (11, 2, "La Liga 2016/17"),
    (11, 21, "La Liga 2018/19"),
    (11, 90, "La Liga 2020/21"),
    
    # Champions League
    (16, 1, "Champions League 2015/16"),
    (16, 2, "Champions League 2016/17"),
    (16, 3, "Champions League 2017/18"),
    (16, 4, "Champions League 2018/19"),
    (16, 41, "Champions League 2020/21"),
    
    # World Cup
    (43, 3, "World Cup 2018"),
    (43, 106, "World Cup 2022"),
    
    # UEFA Euro
    (55, 43, "UEFA Euro 2020"),
    
    # FA WSL
    (37, 3, "FA WSL 2018/19"),
    (37, 4, "FA WSL 2019/20"),
    (37, 42, "FA WSL 2020/21"),
    
    # NWSL
    (49, 3, "NWSL 2018"),
]

valid_competitions = {}

for comp_id, season_id, name in competitions_to_test:
    if test_competition(comp_id, season_id, name):
        valid_competitions[name] = (comp_id, season_id)

print("\n" + "="*50)
print("✅ COMBINAISONS VALIDES À UTILISER :")
print("="*50)
for name, (comp_id, season_id) in valid_competitions.items():
    print(f'"{name}": ({comp_id}, {season_id}),')
