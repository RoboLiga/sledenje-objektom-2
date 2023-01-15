from sledilnik.TrackerGame import TrackerGame

if __name__ == '__main__':
    tracker_game = TrackerGame()
    tracker_game.config['video_source'] = 'ROBO_7.mp4'
    tracker_game.debug = True
    tracker_game.start()
