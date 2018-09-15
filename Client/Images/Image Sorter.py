import os
path_way = os.path.dirname(os.path.realpath(__file__)) #Directory to the python file
files = os.listdir(path_way)
c=0
for file in files:
    if file[:5] == "frame":
        new_name = "IntroGif%i_800x450.png"%(c)
        print(file, new_name)
        c+= 1
        os.rename(path_way + "/" + file, path_way + "/" + new_name) 
