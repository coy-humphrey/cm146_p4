

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def should_attack(state):
    return len(state.enemy_planets()) > 3

def play_defensive(state):
    return sum (planet.growth_rate for planet in state.my_planets()) > sum(planet.growth_rate for planet in state.enemy_planets())

def have_no_planets(state):
    return not bool(state.my_planets())

def enemy_has_planets(state):
    return bool(state.enemy_planets())

def should_spread(state):
    return len(state.my_planets()) < 4 and len(state.my_fleets()) < 4 and state.neutral_planets()

def significant_lead(state):
    myfleet = sum(planet.num_ships for planet in state.my_planets()) + sum(fleet.num_ships for fleet in state.my_fleets())
    theirfleet = sum(planet.num_ships for planet in state.enemy_planets()) + sum(fleet.num_ships for fleet in state.enemy_fleets())
    return myfleet > theirfleet * 1.5

def close_start(state):
    mine = len(state.my_planets())
    theirs = len(state.my_planets())
    if not mine or not theirs: return False
    if mine < 2 and theirs < 2:
        return state.distance(state.my_planets()[0].ID, state.enemy_planets()[0].ID) < 11