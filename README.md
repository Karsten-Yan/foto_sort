# foto_sort

Python script for automatic foto sorting. 

Put unsorted fotos into folder "unsorted", parallel to sort.py. Script searches recursively through the unsorted folder recursively and sorts them into folder "sorted". 

Automatically creates several subfolders according to year, month and camera used. Takes creation data from exif metadata and fallsback to modification date if exif data was stripped (e.g.: when sent via messaging apps). Also sorts movies into a different folder.
