# YoutubeToMP3
YoutubeToMP3 downloader which also allows to download MP3 in bulk

Local copy of moviepy required as I modified the file tools.py to remove unnecessary console outputs

App is built using Python 3.12 with Tkiner


----------------------------------------------------------------------------------------------
V1.0
Initial release

----------------------------------------------------------------------------------------------
V1.1
Moved the validation for the URL format for bulk download into function loading the txt file. 

Added information how many files are being downloaded from the list (for example if 1 url of 6 was in incorrect format - it will say Downloading 5 of 6 files)


Added extra validation for the text functions - to make sure text is being passed over as a parameter


Restricted filename to contain only necessary special characters