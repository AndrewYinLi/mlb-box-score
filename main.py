import mlbgame as mlb
import datetime
import msvcrt
# from multiprocessing import Pool
# Eventually run `boxscore()` in async such that user can view boxscore in realtime and query player stats

now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day

def boxscore(): 
	game_id = mlb.day(year, month, 13, home="Mariners", away="Mariners")[0].game_id # Remember to change 13 back to day
	while True:
		if msvcrt.kbhit():
			break
		print(mlb.box_score(game_id).__dict__)
		#test = 
		#print(test[0].__dict__)




def main():
	boxscore()
	

if __name__ == '__main__':
	main()