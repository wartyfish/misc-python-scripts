import csv
from pathlib import Path
import shutil


dyes = []

with open("Dyes.csv") as f:
    for line in f:
        line = line.strip()
        parts = line.split(",")


        dyes.append(f"{parts[5]}.jpeg")

thumbs = Path(r"C:\Users\Eem\Desktop\pdf sandbox\thumbnails")
dest = Path(r"C:\Users\Eem\Desktop\pdf sandbox\dyes")

for f in thumbs.iterdir():
    current_filenames = [f for f in thumbs.iterdir() if f.name != "Thumbs.db"]

for i in range(len(dyes)):
    shutil.copy(current_filenames[i], dest / dyes[i])
    print(f"{current_filenames[i]} moved to {dest / dyes[i]}")
    
