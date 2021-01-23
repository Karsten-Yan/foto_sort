import os
import glob
from pathlib import Path
from datetime import datetime
import exifread
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

wd = os.getcwd()

unsorted_folder = os.path.join(wd, "unsorted")

extension = ["jpeg", "png", "mp4", "jpg", "mov", "arw", "cr2", "m4v", "avi",
             "webp", "mkv"]
movie = ["mp4", "mov", "m4v", "avi", "mkv"]

statistics_path = os.path.join(wd, "statistics.csv")

if not os.path.exists(statistics_path):
    statistics = pd.DataFrame()
else:
    statistics = pd.read_csv(statistics_path, index_col=0)
files = []
for filename in glob.iglob(unsorted_folder + '**/**', recursive=True):
    files.append(filename)
sortfolder = os.path.join(wd, "sorted")
if not os.path.exists(sortfolder):
    os.makedirs(sortfolder)
for file in files:
    if len(file.rsplit(".", 1)) > 1 and\
            file.rsplit(".", 1)[1].lower() in extension:

        try:
            with open(file, 'rb') as fh:
                tags = exifread.process_file(fh)
                cmod = tags["Image Model"].printable
                make = tags["Image Make"].printable
                dateTaken = tags["EXIF DateTimeOriginal"]
                ctime = datetime.strptime(dateTaken.printable,
                                          '%Y:%m:%d %H:%M:%S')
        except:
            file_info = Path(file)
            cmod = "Generic_Model"
            make = "Generic_Make"
            ctime = datetime.fromtimestamp(file_info.stat().st_mtime)

        source = make.strip().replace(" ", "_") + "_" + cmod.\
            strip().replace(" ", "_")

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
                Path(file).rename(target)
            else:
                pass
        else:
            Path(file).rename(target)

        temp_stat = pd.DataFrame([[ftype, make, cmod,
                                   ctime, year, month, day]],
                                 index=[file_name])
        temp_stat["date"] = temp_stat[3].dt.to_period("D")
        statistics = pd.concat([statistics, temp_stat], axis=0)

    elif len(file.rsplit(".", 1)) > 1 and len(file.rsplit(".", 1)[1]) < 5:
        other = os.path.join(sortfolder, "other")

        if not os.path.exists(other):
            os.makedirs(other)

        target = os.path.join(other, os.path.basename(file))
        if not os.path.exists(target):
            Path(file).rename(target)

statistics.to_csv(statistics_path)
plot_stats = statistics.copy()
plot_stats.columns = ["file_type", "camera_maker", "camera_model",
                      "timestamp", "year", "month", "day", "date"]
by_day = plot_stats[plot_stats.camera_maker != "Generic_Make"].\
    groupby(["camera_maker", "date"]).count().iloc[:, 0]
by_day =  by_day.reset_index()
by_day = by_day.pivot("date","camera_maker","file_type").to_timestamp()

fig, ax = plt.subplots(1,1)
sns.lineplot(data = by_day, ax=ax)
for label in ax.get_xticklabels():
    label.set_ha("right")
    label.set_rotation(45)
