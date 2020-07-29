# Rom Organizer

This is a program that uses No Intro database files to create an organized copy of a local romset. It can create merged sets (where a game folder is created containing all versions of a game that you own) or 1G1R sets (1 Game 1 Rom; each folder contains only the "best" version of a game; ideally, the latest non-demo/proto USA revision). Games are also sorted by primary region (e.g. if a USA version of a game exists, the game folder containing all versions will be placed in the USA folder).

So for example, your local romset containing:
```
D:/Romsets/Sega - Sega Genesis/My Game 1 (USA).zip
D:/Romsets/Sega - Sega Genesis/My Game 1 (Europe).zip
D:/Romsets/Sega - Sega Genesis/My Game 1 (Japan).zip
D:/Romsets/Sega - Sega Genesis/My Game 2 (Europe).zip
D:/Romsets/Sega - Sega Genesis/My Game 2 (Japan).zip
```
... provided you have a dataset file:
```
D:/Rom Tools/No-Intro Database/Sega - Sega Genesis.xmdb
```
... will be copied and sorted as:
```
D:/Roms/Merged and Sorted/Sega - Sega Genesis/USA/My Game 1/My Game 1 (USA).zip
D:/Roms/Merged and Sorted/Sega - Sega Genesis/USA/My Game 1/My Game 1 (Europe).zip
D:/Roms/Merged and Sorted/Sega - Sega Genesis/USA/My Game 1/My Game 1 (Japan).zip
D:/Roms/Merged and Sorted/Sega - Sega Genesis/Europe/My Game 2/My Game 2 (Europe).zip
D:/Roms/Merged and Sorted/Sega - Sega Genesis/Europe/My Game 2/My Game 2 (Japan).zip
```
All versions of My Game 1 are stored in the USA folder since a USA version exists, while all versions of My Game 2 are stored in the Europe folder because a USA version does not exist, but a European version (another English region) does.

This isn't very user-friendly or customizable; I only made it for my own personal use. But feel free to use it if you want; it won't break anything (your ROMs are only copied, not moved/deleted), but keep in mind that the local directories are hardcoded.
