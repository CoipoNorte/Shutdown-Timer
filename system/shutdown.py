import os
import sys

def shutdown_computer(force):
    if sys.platform == "win32":
        if force:
            os.system("shutdown /s /f /t 0")
        else:
            os.system("shutdown /s /t 0")
    elif sys.platform == "darwin":
        if force:
            os.system("sudo shutdown -h now")
        else:
            os.system("osascript -e 'tell app \"System Events\" to shut down'")
    else:
        if force:
            os.system("shutdown -h now")
        else:
            os.system("shutdown -h +0")