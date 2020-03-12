from multiprocessing import Process, Queue, freeze_support

from sledilnik.TrackerGame import TrackerGame
from sledilnik.classes.TrackerLiveData import TrackerLiveData

if __name__ == '__main__':
    freeze_support()
    queue = Queue()

    tracker = TrackerGame()
    tracker.fileNamesConfig.videoSource = 'ROBO_3.mp4'
    tracker.debug = True

    p = Process(target=tracker.start, args=(queue,))
    p.start()

    for _ in range(100):
        gameData: TrackerLiveData = queue.get()
        print(gameData.reprJSON())
