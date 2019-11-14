import shutil

COMMAND= input("FROM or TO here")

if COMMAND=="FROM":
    shutil.copy("ui.py","/media/jopeha/Windows/Users/Jopeh/Documents/DG/ui.py")
elif COMMAND=="TO":
    shutil.copy("/media/jopeha/Windows/Users/Jopeh/Documents/DG/ui.py","ui.py")

print("MOVED ui ",COMMAND," here.")

