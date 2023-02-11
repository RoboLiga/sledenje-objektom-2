from multiprocessing import Process, Queue, freeze_support

from sledilnik.TrackerGame import TrackerGame
from sledilnik.classes.TrackerLiveData import TrackerLiveData

if __name__ == '__main__':
    freeze_support()

    # Create queue for communication between processes
    queue = Queue()

    # Create tracker process
    tracker = TrackerGame()

    # Start tracker process
    p = Process(target=tracker.start, args=(queue,))
    p.start()

    # Read data from queue
    for _ in range(100):
        game_data: TrackerLiveData = queue.get()
        print(game_data.to_json())
