import os
import shutil
from datetime import datetime



def setup_workspace():
    folder_name = "workspace"
    subfolders = ["source_files", "backups", "moved_files", "logs"]
    sample_files = ["notes.txt", "report.txt", "data.csv", "script.py"]

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully!")
    else:
        print(f"Folder '{folder_name}' already exists.")

    for sub in subfolders:
        subpath = os.path.join(folder_name, sub)
        if not os.path.exists(subpath):
            os.mkdir(subpath)
            print(f"Subfolder '{sub}' created successfully.")
        else:
            print(f"Subfolder '{sub}' already exists.")

    source_path = os.path.join(folder_name, "source_files")
    for file in sample_files:
        filepath = os.path.join(source_path, file)
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                pass
            print(f"File '{file}' created successfully in 'source_files'.")
        else:
            print(f"File '{file}' already exists in 'source_files'.")



def show_sourcefiles():
    folder_name = "workspace"
    if not os.path.exists(folder_name):
        print(f"{folder_name} does not exist. Please create the project structure using option 1.")
        return
    path = os.path.join(folder_name,"source_files")
    if not os.path.exists(path):
        print("There is no folder of source_files to check. Please create the complete project structure using option 1.")
        return
    else:
        items = os.listdir(path)
        found = False
        for item in items:
            itempath = os.path.join(path,item)
            if os.path.isfile(itempath):
                print(item)
                found = True
        if found:
            print("All the source files in the folder are printed successfully!")
        else:
            print("No files found in the folder")




def create_time_backup():
    folder_name = "workspace"
    if not os.path.exists(folder_name):
        print(f"{folder_name} does not exist. Please create the project structure using option 1.")
        return
    path = os.path.join(folder_name, "source_files")
    if not os.path.exists(path):
        print("There is no folder of source_files to create backup from. Please create the complete project structure using option 1.")
        return

    backuppath = os.path.join(folder_name, "backups")
    if not os.path.exists(backuppath):
        print("There is no folder of backups. Please create the complete project structure using option 1.")
        return

    items = os.listdir(path)
    files = []
    for item in items:
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            files.append(item)

    if not files:
        print("There are currently no files in source_files that you can create a backup of.")
        return

    while True:
        filename = input("Enter file name (or 'q' to cancel): ").strip()
        if filename.lower() == 'q':
            print("Operation cancelled.")
            break
        if filename in files:
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            name, ext = os.path.splitext(filename)
            completename = name + "_" + date_str + ext
            source = os.path.join(path, filename)
            destination = os.path.join(backuppath, completename)
            if os.path.exists(destination):
                print(f"A backup named {completename} already exists.")
                break
            shutil.copy2(source, destination)
            print(f"Backup created: {completename}")
            break
        else:
            print("Invalid file name, try again")



def create_quick_copy():
    folder_name = "workspace"
    path = os.path.join(folder_name, "source_files")
    if not os.path.exists(folder_name):
        print(f"{folder_name} does not exist. Please create the project structure using option 1.")
        return
    if not os.path.exists(path):
        print("There is no folder of source_files to copy from. Please create the complete project structure using option 1.")
        return

    backuppath = os.path.join(folder_name, "backups")
    if not os.path.exists(backuppath):
        print("There is no folder of backups. Please create the complete project structure using option 1.")
        return

    items = os.listdir(path)
    files = []
    for item in items:
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            files.append(item)

    if not files:
        print("There are currently no files in source_files that you can copy.")
        return

    while True:
        filename = input("Enter file name (or 'q' to cancel): ").strip()
        if filename.lower() == 'q':
            print("Operation cancelled.")
            break
        if filename in files:
            source = os.path.join(path, filename)
            destination = os.path.join(backuppath, f"copy_{filename}")
            if os.path.exists(destination):
                print(f"A quick copy named copy_{filename} already exists.")
                break
            shutil.copy(source, destination)
            print(f"Quick copy created: copy_{filename}")
            break
        else:
            print("Invalid file name, try again")




def move_file():
    folder_name = "workspace"
    path = os.path.join(folder_name, "source_files")
    if not os.path.exists(folder_name):
        print(f"{folder_name} does not exist. Please create the project structure using option 1.")
        return
    if not os.path.exists(path):
        print("There is no folder of source_files to move from. Please create the complete project structure using option 1.")
        return

    movedpath = os.path.join(folder_name, "moved_files")
    if not os.path.exists(movedpath):
        print("There is no folder of moved_files. Please create the complete project structure using option 1.")
        return

    items = os.listdir(path)
    files = []
    for item in items:
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            files.append(item)

    if not files:
        print("There are currently no files in source_files that you can move.")
        return

    while True:
        filename = input("Enter file name (or 'q' to cancel): ").strip()
        if filename.lower() == 'q':
            print("Operation cancelled.")
            break
        if filename in files:
            source = os.path.join(path, filename)
            destination = os.path.join(movedpath, filename)
            if os.path.exists(destination):
                print(f"A file named {filename} already exists in moved_files. Please try again later.")
                break
            shutil.move(source, destination)
            print(f"File moved to moved_files: {filename}")
            break
        else:
            print("Invalid file name, try again")



def show_backup_files():
    folder_name = "workspace"
    if not os.path.exists(folder_name):
        print(f"{folder_name} does not exist. Please create the project structure using option 1.")
        return
    
    backuppath = os.path.join(folder_name, "backups")
    if not os.path.exists(backuppath):
        print("There is no folder of backups. Please create the complete project structure using option 1.")
        return
    else:
        items = os.listdir(backuppath)
        found = False
        for item in items:
            itempath = os.path.join(backuppath,item)
            if os.path.isfile(itempath):
                print(item)
                found = True
        if found:
            print("All the backup files are printed successfully!")
        else:
            print("No backup files found in the folder")



def date_time():
    current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Current Date & Time: {current}")



def create_daily_log():
    folder_name = "workspace"
    logspath = os.path.join(folder_name, "logs")
    if not os.path.exists(folder_name):
        print(f"{folder_name} does not exist. Please create the project structure using option 1.")
        return
    if not os.path.exists(logspath):
        print("There is no folder of logs. Please create the complete project structure using option 1.")
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"log_{date_str}.txt"
    log_filepath = os.path.join(logspath, log_filename)

    if os.path.exists(log_filepath):
        print("Today's log file already exists.")
        return

    full_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_filepath, "w") as f:
        f.write(f"Smart Backup Manager log created on {full_time}\n")
    print(f"Log file created: {log_filename}")




def paths_of_backup():
    folder_name = "workspace"
    backuppath = os.path.join(folder_name, "backups")
    if not os.path.exists(folder_name):
        print(f"{folder_name} does not exist. Please create the project structure using option 1.")
        return
    if not os.path.exists(backuppath):
        print("There is no folder of backups. Please create the complete project structure using option 1.")
        return

    items = os.listdir(backuppath)
    files = []
    for item in items:
        itempath = os.path.join(backuppath, item)
        if os.path.isfile(itempath):
            files.append(itempath)

    if not files:
        print("No backup files found.")
        return

    for file in files:
        print(os.path.abspath(file))


def main():
    choice = -1
    while (True):
        print("""
        1.  Setup Workspace
        2.  Show Source Files
        3.  Create Timestamp Backup (copy2)
        4.  Create Quick Copy
        5.  Move a file to moved_files
        6.  Show Backup Files
        7.  Show Current Date & Time
        8.  Create Daily Log File
        9.  Show Full Paths of Backup Files
        10. Exit
        """)
        choice_str = input("Enter your choice: ")
        if choice_str.isdigit():
            choice = int(choice_str)
            if 1 <= choice <= 10:

                if choice == 1:
                    setup_workspace()

                elif choice == 2:
                    show_sourcefiles()

                elif choice == 3:
                    create_time_backup()

                elif choice == 4:
                    create_quick_copy()

                elif choice == 5:
                    move_file()
                    
                elif choice == 6:
                    show_backup_files()

                elif choice == 7:
                    date_time()

                elif choice == 8:
                    create_daily_log()

                elif choice == 9:
                    paths_of_backup()

                elif choice == 10:
                    print("Exiting the program!")
                    break

                continue

        print("Invalid input try again!")



if __name__ == "__main__":
    main()
