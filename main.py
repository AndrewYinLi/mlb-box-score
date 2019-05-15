import mlbgame as mlb
import datetime
import msvcrt
import time
# from multiprocessing import Pool
# Eventually run `boxscore()` in async such that user can view boxscore in realtime and query player stats

# While we could update the part of the string that corresponds to the current inning's score and save the rest,
# generating the string from scratch handle edge cases such as rain-delay games being continued the next day, overturned calls, etc.
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

def real_time_game(): 
	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = now.day
	game_id = mlb.day(year, month, day, home="Mariners", away="Mariners")[0].game_id
	#game_id = "2019_05_13_oakmlb_seamlb_1" # For debugging
	# Get team abbreviations correctly formatted
	game_id_split = game_id.split("_")
	away_id = game_id_split[3][0:3].upper()
	away_score_str = "| " + away_id + " |"
	home_id = game_id_split[4][0:3].upper()
	home_score_str = "| " + home_id + " |"
	inningIndex = 0
	prev_box_score_str = None
	while True:
		if msvcrt.kbhit(): # On key-press, end program
			break
		innings_list = mlb.box_score(game_id).__dict__["innings"] # Get list of innings. Each inning is a dict e.g. `{'inning': 1, 'home': 1, 'away': 0}`
		cur_box_score_str = get_box_score_str(innings_list, away_score_str, home_score_str)
		if cur_box_score_str != prev_box_score_str:
			print(cur_box_score_str)
			prev_box_score_str = cur_box_score_str

		game_events = mlb.game_events(game_id)
		cur_inning_num = len(game_events)
		event_index = 0
		is_top = True 
		for inning_events in game_events:
			if inning_events.num == cur_inning_num:
				if len(inning_events.bottom) > 0: # if bottom inning
					if is_top:
						is_top = False
						event_index = 0
					if len(inning_events.bottom) > event_index:
						print(inning_events.bottom[event_index])
						event_index += 1
				elif len(inning_events.top) > 0: # if top inning
					if len(inning_events.topm) > event_index:
						print(inning_events.top[event_index])
						event_index += 1
		print(mlb.game_events(game_id)[0].num) # Events for inning `num`
		print(mlb.game_events(game_id)[0].top[0])
		#print(game_events)

def main():
	real_time_game()

if __name__ == '__main__':
	main()