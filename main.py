import mlbgame as mlb
import datetime
import msvcrt
# from multiprocessing import Pool
# Eventually run `boxscore()` in async such that user can view boxscore in realtime and query player stats

away_score_str = ""
home_score_str = ""
horizontal_border = "+=====+"
horizontal_border_col = "===+"
horizontal_middle = "+-----+"
horizontal_middle_col = "---+"
def update_box_score_str(inning_dict):
	pass
	

def real_time_game(): 
	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = now.day
	#game_id = mlb.day(year, month, day, home="Mariners", away="Mariners")[0].game_id
	game_id = "2019_05_13_oakmlb_seamlb_1" # For debugging
	game_id_split = game_id.split("_")
	away_id = game_id_split[3][0:3].upper()
	away_score_str = "| " + away_id + " |"
	home_id = game_id_split[4][0:3].upper()
	home_score_str = "| " + home_id + " |"
	inningIndex = 0

	while True:
		if msvcrt.kbhit(): # On key-press, end program
			break

		innings_list = mlb.box_score(game_id).__dict__["innings"] # Get list of innings. Each inning is a dict e.g. `{'inning': 1, 'home': 1, 'away': 0}`
		update_box_score_str(innings_list[inningIndex])

		currentInningIndex = len(innings_list) - 1
		if currentInningIndex != inningIndex: # New inning
			print(innings_list[0])
		#print(len(mlb.game_events(game_id)))
		#print(mlb.game_events(game_id))
		#print(mlb.game_events(game_id)[0].num) # Get number of half-innings played
		#print(mlb.game_events(game_id)[0].top[0])



def main():
	real_time_game()
	

	

if __name__ == '__main__':
	main()