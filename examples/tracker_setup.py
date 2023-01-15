from sledilnik.TrackerSetup import TrackerSetup

if __name__ == '__main__':
    tracker_setup = TrackerSetup()
    tracker_setup.config['video_source'] = './ROBO_7.mp4'
    tracker_setup.start()
