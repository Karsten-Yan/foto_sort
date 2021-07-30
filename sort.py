import os
import glob
from datetime import datetime
import exifread
import pandas as pd
from shutil import copy2

test = False

if test:

    wd = os.getcwd()
    k_dir = os.path.join(wd, "unsorted")
    i_dir = os.path.join(wd, "fnord")
    sortfolder = os.path.join(wd, "fotos")

else:

    wd = "/mnt/fritznas"
    k_dir = os.path.join(wd, "karsten", "fotos")
    i_dir = os.path.join(wd, "isabell", "fotos")
    sortfolder = os.path.join(wd, "fotos")
extension = [
    "jpeg",
    "png",
    "mp4",
    "jpg",
    "mov",
    "arw",
    "cr2",
    "m4v",
    "avi",
    "webp",
    "mkv",
    "png",
]
movie = ["mp4", "mov", "m4v", "avi", "mkv"]

statistics_path = os.path.join(sortfolder, "statistics.csv")

if not os.path.exists(statistics_path):
    statistics = pd.DataFrame()
else:
    statistics = pd.read_csv(statistics_path, index_col=0)

files = []
if os.path.exists(k_dir):
    for filename in glob.iglob(k_dir + "**/**", recursive=True):
        files.append(filename)
if os.path.exists(i_dir):
    for filename in glob.iglob(i_dir + "**/**", recursive=True):
        files.append(filename)

if not os.path.exists(sortfolder):
    os.makedirs(sortfolder)

for file in files:
    if os.path.isfile(file):
        if file.rsplit(".", 1)[1].lower() in extension:
            try:
                with open(file, "rb") as fh:
                    tags = exifread.process_file(fh)
                    cmod = tags["Image Model"].printable
                    make = tags["Image Make"].printable
                    dateTaken = tags["EXIF DateTimeOriginal"]
                    ctime = datetime.strptime(
                        dateTaken.printable, "%Y:%m:%d %H:%M:%S"
                    )
            except:
                cmod = "Generic_Model"
                make = "Generic_Make"
                ctime = datetime.fromtimestamp(os.path.getmtime(file))

            source = (
                make.strip().replace(" ", "_")
                + "_"
                + cmod.strip().replace(" ", "_")
            )

            if file.rsplit(".")[1].lower() in movie:
                ftype = "movie"
                source = "movie"
            else:
                ftype = "foto"

            month = ctime.strftime("%m_%B")
            year = ctime.strftime("%Y")
            day = ctime.strftime("%d")
            folder = os.path.join(sortfolder, year, month, source)

            if not os.path.exists(folder):
                os.makedirs(folder)

            file_name = os.path.basename(file)

            target = os.path.join(folder, file_name)

            sfile = starget = os.path.getsize(file)
            starget = 0
            if os.path.exists(target):
                starget = os.path.getsize(target)
                if sfile > starget:
                    os.remove(target)
                    copy2(file, target)
                else:
                    continue
            else:
                copy2(file, target)

            d = {
                "file_type": [ftype],
                "camera_maker": [make],
                "camera_model": [cmod],
                "creation_time": [ctime],
                "year": [year],
                "month": [month],
                "day": [day],
            }
            temp_stat = pd.DataFrame(d, index=[file_name])
            temp_stat["date"] = temp_stat["creation_time"].dt.to_period("D")
            statistics = pd.concat([statistics, temp_stat], axis=0)

        else:
            other = os.path.join(sortfolder, "other")

            if not os.path.exists(other):
                os.makedirs(other)

            target = os.path.join(other, os.path.basename(file))
            if not os.path.exists(target):
                copy2(file, target)

statistics.to_csv(statistics_path)
