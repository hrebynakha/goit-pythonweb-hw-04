File copy async manager

Run main file to copy file from **venv** folder to **dest**

`rm -rf dest/ && python main.py --src=venv`

Output will be like:

```

Processing folders completed  ! ✅
Total elapsed time .......  : ⏱️  1.45
Total different extensions  : 🧩 24
Total duplicated file names : 📝 179
Total duplicates files ..   : 🔁 1053
Total folders processed ..  : 📂 403
Total files found  .......  : 📝 3266
Total copied files .......  : ✅ 2171
```

Run copy with progress bar (this will scan all files in dir and than run copy process):

`rm -rf dest/ && python main.py --src=venv --copy-type=after_scan`

```

Scanning folders... completed  ! ✅
📂 Creating extensions dir .. 🧩: 100%|████████████████████████████████████| 24/24 [00:00<00:00, 112.08it/s]
📄 Copying files to new dir  🔁: 100%|████████████████████████████████| 3266/3266 [00:00<00:00, 4231.76it/s]
Total elapsed time .......  : ⏱️  1.42
Total different extensions  : 🧩 24
Total duplicated file names : 📝 179
Total duplicates files ..   : 🔁 1072
Total folders processed ..  : 📂 403
Total files found  .......  : 📝 3266
Total copied files .......  : ✅ 2138
```

#### Problem:

When using the async module to copy files, there is a risk of losing files if two tasks try to check for the existence of a file with the same name in the target directory at the same time. Even if you call a function to check if the file exists in the target directory, the async tasks might simultaneously check the same path. Both tasks could receive a False result, indicating the file doesn't exist, even though it has already been copied by another task. This leads to a situation where the second file overwrites the first, resulting in data loss.
