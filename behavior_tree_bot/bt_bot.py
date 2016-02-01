#!/usr/bin/env python
#

"""
// The do_turn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist.
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.log (logging.DEBUG, "Hello world!!")
try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)
    from behavior_tree_bot.behaviors import *
    from behavior_tree_bot.checks import *
    from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

    from planet_wars import PlanetWars, finish_turn
except:
    traceback.print_exc(file=sys.stdout)
    logging.exception("Error in import stage.")

def setup_behavior_tree():
    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')
    
    snipe_if_possible = Selector(name='Snipe if Possible')
    snipeAction = Action(snipe)
    snipe_if_possible.child_nodes = [snipeAction, Check(lambda state: True)]

    move_up_if_possible = Selector(name='Move up if possible')
    moveAction = Action(move_up)
    move_up_if_possible.child_nodes = [moveAction, Check(lambda state: True)]

    try_attack = Sequence(name='Try attack')
    shouldAttack = Check(should_attack)
    attack = Action(attack_largest_enemies)
    try_attack.child_nodes = [shouldAttack, attack]

    aggressive_if_possible = Selector(name='AggressiveSnipe if possible')
    aggressiveSnipe = Action(aggressive_snipe)
    aggressive_if_possible.child_nodes = [aggressiveSnipe, Check(lambda state: True)]

    spread_if_possible = Selector(name='Spread if Possible')
    try_spread_closest = Sequence(name='Try Spread')
    spread_closest = Action(spread_to_closest)
    neutral_available = Check(if_neutral_planet_available)
    try_spread_closest.child_nodes = [neutral_available, spread_closest]
    spread_if_possible.child_nodes = [try_spread_closest, Check (lambda state: True)]

    defensive_plan = Sequence(name='Defensive Strategy')
    turtleAction = Action(turtle)
    should_play_defensive = Check(play_defensive)
    attackClosest = Action (attack_closest_enemy)
    enemyHasPlanet = Check(enemy_has_planets)
    defensive_offense = Selector(name='Defensive Offense')
    all_out_offense = Sequence(name='Allout')
    winning = Check(significant_lead)
    all_out_offense.child_nodes = [winning, attack.copy()]
    defensive_offense.child_nodes = [all_out_offense, attackClosest]
   
    defensive_plan.child_nodes = [should_play_defensive, snipe_if_possible, turtleAction, move_up_if_possible, enemyHasPlanet, defensive_offense]

    offensive_plan = Sequence(name='Offensive Strategy')
    offensive_plan.child_nodes = [snipe_if_possible, try_attack, move_up_if_possible]

    spread_plan = Sequence(name='Spread strategy')
    shouldSpread = Check(should_spread)
    spread = Action(spread_to_small_close_planets)
    spread_plan.child_nodes = [shouldSpread, snipe_if_possible, aggressive_if_possible, spread, move_up_if_possible]

    close_start_plan = Sequence(name='Close start strategy')
    is_close_start = Check (close_start)
    close_start_plan.child_nodes = [is_close_start, snipe_if_possible, aggressive_if_possible, attack.copy()]

    root.child_nodes = [close_start_plan, spread_plan, defensive_plan, offensive_plan, Check(lambda state: True)]

    logging.info('\n' + root.tree_to_string())
    return root


if __name__ == '__main__':
    try:
        behavior_tree = setup_behavior_tree()
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                behavior_tree.execute(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
