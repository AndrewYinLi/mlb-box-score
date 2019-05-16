import mlbgame as mlb
import datetime
import msvcrt
import time
import sys
import argparse
# from multiprocessing import Pool
# Eventually run `boxscore()` in async such that user can view boxscore in realtime and query player stats

# Dict mapping city abbreviation to team plural
team_dict = {
	"LAA":"Angels", "HOU":"Astros", "OAK":"Athletics", "TOR":"Blue Jays", "ATL":"Braves",
	"MIL":"Brewers", "STL":"Cardinals", "CHC":"Cubs", "ARI":"Diamondbacks", "LAD":"Dodgers",
	"SF":"Giants", "CLE":"Indians", "SEA":"Mariners", "MIA":"Marlins", "NYM":"Mets",
	"WAS":"Nationals", "BAL":"Orioles", "SD":"Padres", "PHI":"Phillies", "PIT":"Pirates",
	"TEX":"Rangers", "TB":"Rays", "BOS":"Red Sox", "CIN":"Reds", "COL":"Rockies",
	"KC":"Royals", "DET":"Tigers", "MIN":"Twins", "CWS":"White Sox", "NYY":"Yankees"
}

"""
Returns team plural correctly formatted regardless of whether.
`team_query` is a city abbreviation or team plural.
@param team_query: city abbreviation or team plural to get box score for.
@throws: Calls `bead_team_name_msg` is input is invalid.
@return: team plural for `team_query`.
"""
def get_team_plural(team_query):
	if len(team_query) <= 3: # If query was city abbreviation
		team_query = team_query.upper() # Reformat
		if team_query in team_dict: # Validate
			return team_dict[team_query]
	else: # If query was a plural
		team_query = team_query[0].upper() + team_query[1:].lower() # Reformat
		for cur_plural in team_dict.values():
			if cur_plural[0] + cur_plural.replace(" ", "")[1:].lower() == team_query:
				return cur_plural
	bad_team_name_msg(team_query) # If query was not found in team_dict

"""
Formats the box score such that it is aesthetically pleasing.
@param innings_list: list of dictionaries containing scores for each half of an inning.
@param away_score_str: The away team's city's abbreviation to append to and incorporate into the box score string.
@param home_score_str: The home team's city's abbreviation to append to and incorporate into the box score string.
@return: the box score formatted as a string.
"""
def get_box_score_str(innings_list, away_score_str, home_score_str):
	horizontal_top = "+=====+"
	horizontal_div = "+-----+"
	horizontal_bot = "+=====+"
	inning_header_str = "|     |"
	horizontal_border_col = "===+"
	horizontal_div_col = "---+"
	inning_num = 1
	for inning_dict in innings_list:
		# Get home and away scores and format innings not yet played
		away_inning_score = inning_dict["away"]
		if away_inning_score == "":
			away_inning_score = "-"
		home_inning_score = inning_dict["home"]
		if home_inning_score == "":
			home_inning_score = "-"
		# Formatting for double-digit scores and innings
		if (type(away_inning_score) == int and away_inning_score > 9) or (type(home_inning_score) == int and home_inning_score > 9) or inning_num > 9:
			horizontal_top += "-"
			horizontal_div += "-"
			horizontal_bot += "-"
			if type(away_inning_score) == int and away_inning_score < 10:
				away_score_str += " "
			if type(home_inning_score) == int and home_inning_score < 10:
				home_score_str += " "
			if inning_num < 10:
				inning_header_str += " "
		# Update borders, middle line, and score for inning
		horizontal_top += horizontal_border_col
		inning_header_str += " " + str(inning_num) + " |"
		away_score_str += " " + str(away_inning_score) + " |"
		horizontal_div += horizontal_div_col
		home_score_str += " " + str(home_inning_score) + " |"
		horizontal_bot += horizontal_border_col
		inning_num += 1
	return horizontal_top + "\n" + inning_header_str + "\n" + horizontal_div + "\n" + away_score_str + "\n" + horizontal_div + "\n" + home_score_str + "\n" + horizontal_bot

"""
@throws: Prints the correct way to format a team query and exits program.
"""
def bad_team_name_msg(input_team):
	print("Error: Invalid team query. Please input the team plural or city abbreviation as follows: ")
	correctUse = ""
	for city, plural in team_dict.items():
		correctUse += city + " or " + plural + ", "
	print(correctUse[:len(correctUse)-2] + ".")
	sys.exit(1)

"""
@throws: Prints that game is invalid exits program.
"""
def game_is_null_msg():
	print("Error: Game hasn't started yet or there isn't a game scheduled for today.")
	sys.exit(1)

"""
Continuously print the box score for an MLB game until it is over.
@param team_query: City abbreviation or team plural to get box score for.
"""
def real_time_game(team_query):
	team_plural = get_team_plural(team_query)
	#print(team_plural) # debug
	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = now.day
	try:
		game_id = mlb.day(year, month, day, home=team_plural, away=team_plural)[0].game_id
	except:
		game_is_null_msg()
		return
	#game_id = "2019_05_13_oakmlb_seamlb_1" # For debugging
	# Get team abbreviations correctly formatted
	game_id_split = game_id.split("_")
	away_abbreviation = game_id_split[3][0:3].upper()
	away_score_str = "| " + away_abbreviation + " |"
	home_abbreviation = game_id_split[4][0:3].upper()
	home_score_str = "| " + home_abbreviation + " |"
	inningIndex = 0
	prev_box_score_str = None
	is_top = True
	# Get current event_index
	event_index = 0
	game_events = mlb.game_events(game_id)
	cur_inning_num = len(game_events)	
	for inning_events in game_events: # Loop through all innings because API gives them out of order
		if inning_events.num == cur_inning_num: # If current inning inning
			if len(inning_events.bottom) > 0: # if bottom inning
				is_top = False
				event_index = len(inning_events.bottom) - 1
			elif len(inning_events.top) > 0: # if top inning
				event_index = len(inning_events.top) - 1
			# `event_index` defaults to 0
	# Continuously loop until game is over, user exits, or error
	while True:
		if msvcrt.kbhit(): # On key-press, end program
			return
		try: # API can be buggy
			innings_list = mlb.box_score(game_id).__dict__["innings"] # Get list of innings. Each inning is a dict e.g. `{'inning': 1, 'home': 1, 'away': 0}`
		except:
			game_is_null_msg()
			return
		cur_box_score_str = get_box_score_str(innings_list, away_score_str, home_score_str)
		if cur_box_score_str != prev_box_score_str:
			print(cur_box_score_str)
			prev_box_score_str = cur_box_score_str
		game_events = mlb.game_events(game_id)
		cur_inning_num = len(game_events)	
		for inning_events in game_events: # Loop through all innings because API gives them out of order
			if inning_events.num == cur_inning_num: # If current inning inning
				if len(inning_events.bottom) > 0: # if bottom inning
					if is_top: # If change in inning, flip `is_top` and reset `event_index`
						is_top = False
						event_index = 0
					if len(inning_events.bottom) > event_index:
						print(inning_events.bottom[event_index])
						event_index += 1
				elif len(inning_events.top) > 0: # if top inning
					if not is_top: # If change in inning, flip `is_top` and reset `event_index`
						is_top = True
						event_index = 0
					if len(inning_events.top) > event_index:
						print(inning_events.top[event_index])
						event_index += 1
		#print(mlb.game_events(game_id)[0].num) # Events for inning `num`
		#print(mlb.game_events(game_id)[0].top[0])
		#print(game_events)

def main(args):
	print("Fetching...")
	real_time_game(args.team_query) # Refactor this later to account for new argparse args

if __name__ == '__main__':
	# Define and parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("team_query", help="Team to get box score for.")
	args = parser.parse_args()
	main(args)