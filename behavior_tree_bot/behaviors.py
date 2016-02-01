import sys, logging
sys.path.insert(0, '../')
from planet_wars import issue_order
from collections import defaultdict
from math import inf, sqrt

logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 10:
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


def spread_to_largest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = max(state.neutral_planets(), key=lambda p: p.growth_rate * 10 - p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def attack_largest_enemies (state):
    targets = sorted(state.enemy_planets(), key = lambda p: p.growth_rate, reverse = True)
    fleet_distribution = defaultdict(lambda: defaultdict(int))
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in targets:
            fleet_distribution[fleet.destination_planet]['danger_level'] += fleet.num_ships
    for fleet in state.my_fleets():
        if fleet.destination_planet in targets:
            fleet_distribution[fleet.destination_planet]['danger_level'] -= fleet.num_ships
    for target in targets:
        for planet in smallest_first(state):
            if not under_attack(state, planet):
                ships = planet.num_ships
                if ships < 50: continue
                danger_level = fleet_distribution[target.ID]['danger_level'] + target.num_ships + target.growth_rate * state.distance(target.ID, planet.ID) + 1
                reenforcements = min (ships, danger_level)
                if reenforcements > 0:
                    issue_order(state, planet.ID, target.ID, reenforcements)
                    fleet_distribution[target.ID]['danger_level'] -= reenforcements
    return True

def attack_largest_enemy (state):
    target = max (state.enemy_planets(), key = lambda p: p.growth_rate)
    danger = target.num_ships
    for fleet in state.enemy_fleets():
        if fleet.destination_planet == target.ID:
            danger += fleet.num_ships
            
    for fleet in state.my_fleets(): 
        if fleet.destination_planet == target.ID:
            danger -= fleet.num_ships

    for planet in smallest_first(state):
        if not under_attack(state, planet):
            ships = planet.num_ships
            if ships < 50: continue
            danger_level = danger + target.growth_rate * 10
            reenforcements = min (ships, danger_level)
            if reenforcements > 0:
                issue_order(state, planet.ID, target.ID, reenforcements)
                danger -= reenforcements
    return True

def attack_closest_enemy (state):
    target = closest_enemy(state)
    danger = target.num_ships
    for fleet in state.enemy_fleets():
        if fleet.destination_planet == target.ID:
            danger += fleet.num_ships
            
    for fleet in state.my_fleets(): 
        if fleet.destination_planet == target.ID:
            danger -= fleet.num_ships

    for planet in smallest_first(state):
        if not under_attack(state, planet):
            ships = planet.num_ships
            if ships < 50: continue
            danger_level = danger + target.growth_rate * 10
            reenforcements = min (ships, danger_level)
            if reenforcements > 0:
                issue_order(state, planet.ID, target.ID, reenforcements)
                danger -= reenforcements
    return True

def turtle(state):
    planets = [planet for planet in state.my_planets() if under_attack(state, planet)]
    danger = defaultdict(int)
    
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in planets:
            danger[fleet.destination_planet] += fleet.num_ships
            
    for fleet in state.my_fleets(): 
        if fleet.destination_planet in planets and fleet.turns_remaining <= fleet_distribution[fleet.destination_planet]['min_turns']:
            danger[fleet.destination_planet] -= fleet.num_ships
            
    elligable_planets = [planet for planet in smallest_first(state) if not under_attack(state, planet)]
    for planet in elligable_planets:
        for plnet in sorted (planets, key=lambda p: p.growth_rate - state.distance (p.ID, planet.ID)):
            ships = planet.num_ships
            danger_level = danger[plnet.ID] + plnet.growth_rate
            reenforcements = min(ships, danger_level)
            if reenforcements > 0:
                issue_order(state, planet.ID, plnet.ID, reenforcements)
                danger[plnet.ID] -= reenforcements

    return True

def aggressive_snipe(state):
    targets = sorted(state.neutral_planets(), key = lambda p: p.growth_rate, reverse = True)
    danger = defaultdict(int)
    min_turns = defaultdict(lambda: inf)
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in [target.ID for target in targets]:
            danger[fleet.destination_planet] += fleet.num_ships
            min_turns[fleet.destination_planet] = min(min_turns[fleet.destination_planet], fleet.turns_remaining)
    for fleet in state.my_fleets():
        if fleet.destination_planet in [target.ID for target in targets]:
            danger[fleet.destination_planet] -= fleet.num_ships
    valid_targets = [target for target in targets if under_attack(state, target)]
    if not valid_targets:
        logging.log (logging.DEBUG, "Snipe: No valid targets")
        return False
    else:
        logging.log(logging.DEBUG, 'yes valid targets')
    for target in valid_targets:
        logging.log(logging.DEBUG, 'target~')
        danger[target.ID] += target.growth_rate + 1
        for planet in smallest_first(state):
            logging.log(logging.DEBUG, 'planet~ : {} {}'.format(state.distance (planet.ID, target.ID), min_turns[target.ID]))
            distance = state.distance (planet.ID, target.ID)
            turns = min_turns[target.ID]
            if distance > turns and distance < turns + 4:
                logging.log(logging.DEBUG, 'sending_fleet: {} {}'.format(state.distance(planet.ID, target.ID), min_turns[target.ID]))
                ships = planet.num_ships
                danger_level = danger[target.ID]
                reenforcements = min (ships, danger_level)
                if reenforcements > 0:
                    issue_order(state, planet.ID, target.ID, reenforcements)
                    danger[target.ID] -= reenforcements
    return True

def snipe(state):
    targets = sorted(state.neutral_planets(), key = lambda p: p.growth_rate, reverse = True)
    danger = defaultdict(int)
    min_turns = defaultdict(lambda: inf)
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in [target.ID for target in targets]:
            danger[fleet.destination_planet] += fleet.num_ships
            min_turns[fleet.destination_planet] = min(min_turns[fleet.destination_planet], fleet.turns_remaining)
    for fleet in state.my_fleets():
        if fleet.destination_planet in [target.ID for target in targets]:
            danger[fleet.destination_planet] -= fleet.num_ships
    valid_targets = [target for target in targets if under_attack(state, target)]
    if not valid_targets:
        logging.log (logging.DEBUG, "Snipe: No valid targets")
        return False
    else:
        logging.log(logging.DEBUG, 'yes valid targets')
    for target in valid_targets:
        logging.log(logging.DEBUG, 'target~')
        danger[target.ID] += target.growth_rate + 1
        for planet in smallest_first(state):
            logging.log(logging.DEBUG, 'planet~ : {} {}'.format(state.distance (planet.ID, target.ID), min_turns[target.ID]))
            distance = state.distance (planet.ID, target.ID)
            turns = min_turns[target.ID]
            if distance == turns + 1:
                logging.log(logging.DEBUG, 'sending_fleet: {} {}'.format(state.distance(planet.ID, target.ID), min_turns[target.ID]))
                ships = planet.num_ships
                danger_level = danger[target.ID]
                reenforcements = min (ships, danger_level)
                if reenforcements > 0:
                    issue_order(state, planet.ID, target.ID, reenforcements)
                    danger[target.ID] -= reenforcements
    return True

def spread_to_small_close_planets (state):
    for planet in smallest_first(state):
        if under_attack (state, planet) or planet.num_ships < 50: continue
        planet_targets = sorted (state.neutral_planets(), key = lambda p: p.num_ships * 2 + state.distance(planet.ID, p.ID) * 3)
        for target in planet_targets:
            closest_enemy = get_closest_enemy(state, target)
            if not closest_enemy: return False
            if state.distance (closest_enemy.ID, target.ID) <= state.distance(planet.ID, target.ID): continue
            ships = planet.num_ships
            danger_level = target.num_ships + 1
            if ships > danger_level and danger_level > 0:
                issue_order(state, planet.ID, target.ID, danger_level)
    return True

def spread_to_closest (state):
    for planet in sorted (state.my_planets(), key = lambda p: p.num_ships, reverse=True):
        if under_attack (state, planet) or planet.num_ships < 50: continue
        planet_targets = sorted (state.neutral_planets(), key = lambda p: p.growth_rate - state.distance(planet.ID, p.ID), reverse = True)
        for target in planet_targets:
            closest_enemy = get_closest_enemy(state, target)
            if not closest_enemy: return False
            if state.distance (closest_enemy.ID, target.ID) <= state.distance(planet.ID, target.ID): continue
            danger = 0
            for fleet in state.my_fleets():
                if fleet.destination_planet == target.ID:
                    danger -= fleet.num_ships
            ships = planet.num_ships
            danger_level = danger + target.num_ships + 1
            if ships > danger_level and danger_level > 0:
                return issue_order(state, planet.ID, target.ID, danger_level)
    return True

def move_up (state):
    if not state.enemy_planets(): return False
    my_planets = state.my_planets()
    for planet in my_planets:
        if planet.num_ships < 50 or under_attack(state, planet): continue
        my_closest_enemy = get_closest_enemy(state, planet)
        min_dist = inf
        min_planet = planet
        for other_planet in my_planets:
            new_dist = state.distance(other_planet.ID, my_closest_enemy.ID)
            if new_dist < min_dist:
                min_planet = other_planet
                min_dist = new_dist
        if min_planet.ID != planet.ID:
            ships = planet.num_ships
            reenforcements = ships - 50
            if reenforcements > 0:
                issue_order(state, planet.ID, min_planet.ID, reenforcements)
    return True


def attack_largest_enemies (state):
    targets = sorted(state.enemy_planets(), key = lambda p: p.growth_rate, reverse = True)
    fleet_distribution = defaultdict(lambda: defaultdict(int))
    for fleet in state.enemy_fleets():
        if fleet.destination_planet in targets:
            fleet_distribution[fleet.destination_planet]['danger_level'] += fleet.num_ships
    for fleet in state.my_fleets():
        if fleet.destination_planet in targets:
            fleet_distribution[fleet.destination_planet]['danger_level'] -= fleet.num_ships
    for planet in smallest_first(state):
        if not under_attack(state, planet):
            for target in sorted (targets, key=lambda p: p.growth_rate - state.distance(p.ID, planet.ID), reverse=True):
                ships = planet.num_ships
                if ships < 50: continue
                danger_level = fleet_distribution[target.ID]['danger_level'] + target.num_ships + target.growth_rate * state.distance(target.ID, planet.ID) + 1
                reenforcements = min (ships, danger_level)
                if reenforcements > 0:
                    issue_order(state, planet.ID, target.ID, reenforcements)
                    fleet_distribution[target.ID]['danger_level'] -= reenforcements
    return True

def smallest_first(state):
    return sorted(state.my_planets(), key = lambda p: p.growth_rate)
    
def under_attack(state, planet):
    for fleet in state.enemy_fleets():
        if fleet.destination_planet == planet.ID:
            return True
    return False

def closest_enemy(state):
    def find_centroid(state):
        x,y = (0,0)
        for planet in state.my_planets():
            x = x + planet.x
            y = y + planet.y
        num_planets = len (state.my_planets())
        return (x/num_planets, y/num_planets)
    def dist(planet, point):
        x,y = point
        return sqrt ((x-planet.x)**2 + (y-planet.y)**2)
    centroid = find_centroid(state)
    return min (state.enemy_planets(), key=lambda p: dist(p, centroid))

def closest_enemies(state):
    def find_centroid(state):
        x,y = (0,0)
        for planet in state.my_planets():
            x = x + planet.x
            y = y + planet.y
        num_planets = len (state.my_planets())
        return (x/num_planets, y/num_planets)
    def dist(planet, point):
        x,y = point
        return sqrt ((x-planet.x)**2 + (y-planet.y)**2)
    centroid = find_centroid(state)
    return sorted (state.enemy_planets(), key=lambda p: dist(p, centroid))

def avg_distance_from_enemy (state, planet):
    def find_centroid_enemies(state):
        x,y = (0,0)
        for planet in state.enemy_planets():
            x = x + planet.x
            y = y + planet.y
        num_planets = len (state.enemy_planets())
        return (x/num_planets, y/num_planets)
    def dist(planet, point):
        x,y = point
        return sqrt ((x-planet.x)**2 + (y-planet.y)**2)
    centroid = find_centroid(state)
    return dist(planet, centroid)

def get_closest_enemy (state, planet):
    if not state.enemy_planets(): return None
    return min (state.enemy_planets(), key=lambda p: state.distance(p.ID, planet.ID))