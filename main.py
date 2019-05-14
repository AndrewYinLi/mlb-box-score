import mlbgame as mlb
import datetime
import msvcrt
# from multiprocessing import Pool
# Eventually run `boxscore()` in async such that user can view boxscore in realtime and query player stats

def real_time_game(): 
	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = now.day
	#game_id = mlb.day(year, month, day, home="Mariners", away="Mariners")[0].game_id
	game_id = "2019_05_13_oakmlb_seamlb_1" # For debugging
	game_id_split = game_id.split("_")
	away_id = game_id_split[3][0:3].upper()
	home_id = game_id_split[4][0:3].upper()
	inningIndex = 0
	inningTop = True

	while True:
		if msvcrt.kbhit(): # On key-press, end program
			break


		print(mlb.overview(game_id))
		#print(mlb.box_score(game_id).__dict__)
		#print(len(mlb.game_events(game_id)))
		#print(mlb.game_events(game_id))
		#print(mlb.game_events(game_id)[0].num) # Get number of half-innings played
		#print(mlb.game_events(game_id)[0].top[0])



def main():
	real_time_game()
	

	

if __name__ == '__main__':
	main()