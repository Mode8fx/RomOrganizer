import sys
from os import path, mkdir, listdir, remove, walk, rename, rmdir

# the same folder where this program is stored
if getattr(sys, 'frozen', False):
	mainFolder = path.dirname(sys.executable) # EXE (executable) file
else:
	mainFolder = path.dirname(path.realpath(__file__)) # PY (source) file
sys.path.append(mainFolder)

driveLetter = path.splitdrive(mainFolder)[0]+"\\" # the drive where this program is stored (example: "C:\\")

########################
# EDIT BELOW THIS LINE #
########################

# Directories

# The folder when your current romsets are stored
romsetFolder = path.join(driveLetter, "Romsets")

# The folder containing your XMDB files
xmdbDir = path.join(driveLetter, "Rom Tools", "No-Intro Database")

# The folder containing your generated romsets (note: your original romset is used in the creation of all generated romsets, and the "Merged" romset is used in the creation of Sorted and 1G1R sets)
outputFolder = path.join(driveLetter, "Roms")



# Options (other options are given in the program itself)

# Ignore non-USA ROMs?
usaOnly = False