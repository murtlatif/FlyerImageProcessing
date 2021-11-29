files = [
    "produce.csv",
    "meat.csv",
    "grocery.csv",
    "bakery.csv",
    "dairy.csv",
]

handles = [open(file) for file in files]

# tempfiles is a list of file handles to your temp files. Order them however you like
f = open("data.csv", "w")
for i,file in enumerate(handles):
    if i == 0:
        f.write('label,text\n')
    print(files[i])
    for line in file:
        f.write(f"{i},{line}")