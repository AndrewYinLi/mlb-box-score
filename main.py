import mlbgame as mlb
import datetime
import msvcrt
import time
import sys
import argparse
# from multiprocessing import Pool
# Eventually run `boxscore()` in async such that user can view boxscore in realtime and query player stats

# Dictionary mapping city abbreviation to team plural
team_dict = {
	"LAA":"Angels",
	"HOU":"Astros",
	"OAK":"Athletics",
	"TOR":"Blue Jays",
	"ATL":"Braves",
	"MIL":"Brewers",
	"STL":"Cardinals",
	"CHC":"Cubs",
	"ARI":"Diamondbacks",
	"LAD":"Dodgers",
	"SF":"Giants",
	"CLE":"Indians",
	"SEA":"Mariners", 
	"MIA":"Marlins",
	"NYM":"Mets",
	"WAS":"Nationals",
	"BAL":"Orioles",
	"SD":"Padres",
	"PHI":"Phillies",
	"PIT":"Pirates",
	"TEX":"Rangers",
	"TB":"Rays",
	"BOS":"Red Sox",
	"CIN":"Reds",
	"COL":"Rockies",
	"KC":"Royals",
	"DET":"Tigers",
	"MIN":"Twins",
	"CWS":"White Sox",
	"NYY":"Yankees"
}

# Verify team plural is correct
def verify_team_plural(team_plural):
	team_plural = team_plural[0].upper() + team_plural[1:].lower() 
	for cur_plural in team_dict.values():
		if cur_plural[0] + cur_plural.replace(" ", "")[1:].lower() == team_plural:
			return cur_plural
	return None

# Get abbreviation from team plural (important to not call this a mascot)
def get_team_plural(city_abbreviation):
	city_abbreviation = city_abbreviation.upper()
	if city_abbreviation in team_dict:
		return team_dict[city_abbreviation]
	return None

# While we could update the part of the string that corresponds to the current inning's score and save the rest,
# generating the string from scratch handle edge cases such as rain-delay games being continued the next day, overturned calls, etc.
def get_box_score_str(innings_list, away_score_str, home_score_str):
	if len(innings_list) == 0: # No game or game hasn't yet started
		return ""
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

def bad_team_name_msg(input_team):
	print("Error: Invalid team query. Please input the team plural or city abbreviation as follows: ")
	correctUse = ""
	for city, plural in team_dict.items():
		correctUse += city + " or " + plural + ", "
	print(correctUse[:len(correctUse)-2] + ".")
	sys.exit(1)

def game_is_null_msg():
	print("Error: Game hasn't started yet or there isn't a game today.")
	sys.exit(1)

def real_time_game(team_query):
	if len(team_query) <= 3: # If city abbreviation
		team_plural = get_team_plural(team_query)
	else: # If team plural
		team_plural = verify_team_plural(team_query)
	if team_plural == None:
		bad_team_name_msg(team_query)
	# print(team_plural) # debug

	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = now.day
	try: # API can be buggy
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
	while True:
		if msvcrt.kbhit(): # On key-press, end program
			return
		try: # API can be buggy
			innings_list = mlb.box_score(game_id).__dict__["innings"] # Get list of innings. Each inning is a dict e.g. `{'inning': 1, 'home': 1, 'away': 0}`
		except:
			game_is_null_msg()
			return
		cur_box_score_str = get_box_score_str(innings_list, away_score_str, home_score_str)
		if cur_box_score_str == "": # API can be buggy
			game_is_null_msg()
			return
		elif cur_box_score_str != prev_box_score_str:
			print(cur_box_score_str)
			prev_box_score_str = cur_box_score_str

		game_events = mlb.game_events(game_id)
		cur_inning_num = len(game_events)
		event_index = 0
		is_top = True 
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