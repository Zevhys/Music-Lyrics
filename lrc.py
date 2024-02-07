import pylrc
import sys
import time
import pathlib
import signal
import os
import vlc

os.system('cls')

# Check that the user has specified the .lrc file
if (len(sys.argv) != 2):
  exit(0)

# Parse the .lrc file using pylrc
lrc_file = open(sys.argv[1])
lrc_string = ''.join(lrc_file.readlines())
lrc_file.close()

subs = pylrc.parse(lrc_string)

# Generate the .mp3 filename
# an alternative is https://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python
filename = pathlib.PurePosixPath(sys.argv[1]).stem
mp3_file = filename + '.mp3'

def SongFinished(event):
    global song_has_finished
    print("Event reports - finished")
    song_has_finished = True
    # Show the cursor
    sys.stdout.write("\033[?25h")

song_has_finished = False

# Prepare VLC
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new_path(mp3_file) #Your audio file here
player.set_media(media)
events = player.event_manager()
events.event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)

# handle ctrl-c
def sigint_handler(signum, frame):
    player.stop()
    # Show cursor
    sys.stdout.write("\033[?25h")
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# Start playing the song
print('\nPlaying "' + subs.title + '" by "' + subs.artist + '"')
player.play()

# Hide the cursor
sys.stdout.write("\033[?25l")

line = 0
num_lines = len(subs)
line_printed = False

# wait for the song to finish
while song_has_finished == False:
    sec = player.get_time() / 1000

    # should we show the next lyrics?
    if line+1 == num_lines or sec < subs[line+1].time:
        # make sure that we only show the lyric once
        if line_printed == False:
            print("\r" + subs[line].text.rstrip() + " " * (60 - len(subs[line].text)), end='', flush=True)

            line_printed = True
    else:
        line += 1
        line_printed = False

    # try to reduce the CPU usage a bit...
    time.sleep(0.1)
