import os
import glob
from datetime import datetime
import exifread
import pandas as pd
from shutil import copy2
import requests
from requests.auth import HTTPBasicAuth
import json

def post_to_gotify(token, message, title, url, priority=0):
    resp = requests.post(
         f"{url}{token}",
        json={"message": message, "priority": priority, "title": title},
    )
    return resp

test = False

def append_files(directory, file_list, name_start = ""):
    if os.path.exists(directory):
        for filename in glob.iglob(directory + "**/**", recursive=True):
            if filename.startswith(name_start):
                file_list.append(filename)

if test:

    wd = os.getcwd()
    k_dir = os.path.join(wd, "unsorted")
    i_dir = os.path.join(wd, "fnord")
    m_dir = os.path.join(wd, "gnampf")
    sortfolder = os.path.join(wd, "fotos")

else:

    wd = "/mnt/storage"
    k_dir = os.path.join(wd, "karsten", "fotos")
    i_dir = os.path.join(wd, "nextcloud","data","isabell","files","Photos")
    m_dir = os.path.join(wd, "manual_upload")
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

with open('/home/pi/foto_sort/config.json') as f:
    config = json.load(f)

files = []
append_files(k_dir, files)
append_files(i_dir, files)
append_files(m_dir, files)


if not os.path.exists(sortfolder):
    os.makedirs(sortfolder)

num_fotos_sorted = 0
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
                    num_fotos_sorted += 1
                else:
                    continue
            else:
                copy2(file, target)
                num_fotos_sorted += 1

        else:
            other = os.path.join(sortfolder, "other")

            if not os.path.exists(other):
                os.makedirs(other)

            target = os.path.join(other, os.path.basename(file))
            if not os.path.exists(target):
                copy2(file, target)

if num_fotos_sorted > 0:
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    gotify_message = f"{num_fotos_sorted} were sorted at {today}"
    resp = post_to_gotify(config["gotify_token", gotify_message, "new fotos", config["gotify_url"])
