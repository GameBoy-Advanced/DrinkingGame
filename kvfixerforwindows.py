from os import listdir


files = filter(lambda a: a[-3:]==".kv",listdir("."))

#command=input("'IN' to turn unicode chars in kv files to hex things, 'OUT' to turn hexes into real chars 'X' or literally anything else to cancel")

char_uni=[(i,"u"+str(hex(ord(i)))) for i in "äöå"]

for i in char_uni:
   a=f"T\{i[1]}"
#if command=="IN":
