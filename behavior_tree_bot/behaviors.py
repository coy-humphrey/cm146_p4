import sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from collections import defaultdict


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
		
def turtle(state):
	planets = sorted(state.my_planets(), key = lambda p: p.growth_rate, reverse = True) #get and sort our list of planets
	fleet_distribution = defaultdict(int)
	min_turns = 9999
	max_turns = 0
	
	for fleet in state.enemy_fleets():
		if fleet.destination_planet in planets:
			fleet_distribution[fleet.destination_planet] += fleet.num_ships
			min_turns = min(min_turns, fleet.turns_remaining)

			
	for fleet in state.my_fleets():
		if fleet.turns_remaining > min_turns:
			continue
			
		if fleet.destination_planet in planets:
			fleet_distribution[fleet.destination_planet] -= fleet.num_ships
			
	elligable_planets = [planet for planet in smallest_first(state) if not under_attack(planet, fleet_distribution)]
	
	for planet in elligable_planets:
		for plnet in planets:
			if under_attack(plnet, fleet_distribution):
				ships = planet.num_ships
				danger_level = fleet_distribution[plnet]
				reenforcements = min(ships, danger_level)
				
				reenforcements = max(reenforcements, 0)
				
				if reenforcements > 0:
					issue_order(state, planet.ID, plnet.ID, reenforcements)
	return True
	
def smallest_first(state):
	return sorted(state.my_planets(), key = lambda p: p.growth_rate)
	
def under_attack(planet, fleet_distribution):
	if planet in fleet_distribution:
		return fleet_distribution[planet] > 0
	return False
