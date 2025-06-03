# Step 1: choose the traits of the site
# Step 2: sort 10 microbes into site1, site2, or return
#        if (microbe falls in the range for 2 attributes) 
#           and (avoid the undesired trait of the site) = site1
#        elif (microbe falls in range of site 2 attribute) = site2
#        else return
# Step 3: select a prospect pool, were already given 6 microbes. select 1 of 3 prospects
#        if microbe had undesired trait of site1 = elimnate
#        elif (microbe falls in the range for 2 attributes) 
#           and (avoid the undesired trait of the site) = site1
# Step 4: out of 10 in the propsect pool, select 3 that form the treatment. 
#   should get the highest possible score for treatment effectiveness
#       20 points if the average permeability of 3 microbes fall within the range of the current site
#       20 points if the average mobility of 3 microbes fall within the range of the current site
#       20 points if the average energy of 3 microbes fall within the range of the current site
#       20 points if none of the microbes have undesired trait
#       20 points if at least one microbe has the desired trait.

import json
import itertools

def load_microbes(filepath):
    """Load microbe data from a JSON file."""
    with open(filepath, 'r') as file:
        return json.load(file)

def calculate_score(microbes, site_profile):
    """Calculate the treatment effectiveness score for a group of 3 microbes."""
    avg_permeability = sum(m['permeability'] for m in microbes)/ 3
    avg_mobility = sum(m['mobility'] for m in microbes)/ 3
    avg_energy = sum(m['energy'] for m in microbes)/ 3

    score = 0

    # Range checks
    if site_profile['permeability'][0] <= avg_permeability <= site_profile['permeability'][1]:
        score += 20
    if site_profile['mobility'][0] <= avg_mobility <= site_profile['mobility'][1]:
        score += 20
    if site_profile['energy'][0] <= avg_energy <= site_profile['energy'][1]:
        score += 20

    # Trait checks
    any_desirable = set(site_profile['desirable'])

    # 20 points if at least one microbe has a desired trait
    if any(any_desirable.intersection(set(m.get('desireable', []))) for m in microbes):
        score += 20

    return score

def find_top_microbes(filepath, site_profile):
    """Find the top 3-microbe group based on treatment effectiveness score."""
    microbes = load_microbes(filepath)
    best_score = 0
    best_combo = None

    for combo in itertools.combinations(microbes, 3):
        score = calculate_score(combo, site_profile)
        names = [m['name'] for m in combo]
        print(f"Combo {names} → Score: {score}")
        if score > best_score:
            best_score = score
            best_combo = combo

    return best_combo, best_score


site_profile = {
    "permeability": [1,2],
    "mobility": [2, 4],
    "energy": [8, 10],
    "desirable": ["Aerobic"]
}

top_microbes, score = find_top_microbes("microbe_data.json", site_profile)





# Microbe details
print("🔬 Selected Microbes:")
total_permeability = total_mobility = total_energy = 0

for m in top_microbes:
    total_permeability += m["permeability"]
    total_mobility += m["mobility"]
    total_energy += m["energy"]
    print(f"  🧫 {m['name']}")
    print(f"     - Permeability: {m['permeability']}")
    print(f"     - Mobility:     {m['mobility']}")
    print(f"     - Energy:       {m['energy']}")
    print(f"     - Traits:       {m['desireable']}\n")

# Averages
avg_permeability = round(total_permeability/3, 2)
avg_mobility = round(total_mobility/3, 2)
avg_energy = round(total_energy/3, 2)

print(f"\nTop 3 Microbes (Total Score: {score}/100):\n")

print("📊 Group Averages:")
print(f"  Avg Permeability: {avg_permeability}")
print(f"  Range:            {site_profile['permeability']}")
print(f"  Avg Mobility:     {avg_mobility}")
print(f"  Range:            {site_profile['mobility']}")
print(f"  Avg Energy:       {avg_energy}")
print(f"  Range:            {site_profile['energy']}\n")

