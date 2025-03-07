import sys
import os
import time
import shutil
import argparse
import logging

def add_logfile(direct):

    if not os.path.exists(direct):
        os.makedirs(direct)
    
    log_file = os.path.join(direct, 'logfile.log')

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def copying_from_src(source, dest):
    if not os.path.exists(dest):
        os.makedirs(dest)
        print(f"Folder {dest} created.")
        logging.info(f"Folder {dest} created.")

    source_dir = os.listdir(source)
    dest_dir = os.listdir(dest)

    for file_name in source_dir:
        source_path = os.path.join(source, file_name)
        replica_path = os.path.join(dest, file_name)

        if os.path.isfile(source_path):
            if file_name not in dest_dir:
                shutil.copy2(source_path, replica_path)
                print(f"File {file_name} copied!")
                logging.info(f"File {file_name} copied!")
            else:
                source_mtime = os.path.getmtime(source_path)
                dest_mtime = os.path.getmtime(replica_path)
                if source_mtime > dest_mtime:
                    shutil.copy2(source_path, replica_path)
                    print(f"File {file_name} in source is newer. Copying...")
                    logging.info(f"File {file_name} in source is newer. Copying...")

        elif os.path.isdir(source_path):
            if file_name not in dest_dir:
                shutil.copytree(source_path, replica_path)
                print(f"Folder {file_name} copied.")
                logging.info(f"Folder {file_name} copied.")
            else:
                for root, dirs, files in os.walk(source_path):
                    relative_path = os.path.relpath(root, source)
                    dest_root = os.path.join(dest, relative_path)

                    if not os.path.exists(dest_root):
                        os.makedirs(dest_root)
                        print(f"Created folder {dest_root}")
                        logging.info(f"Created folder {dest_root}")

                    for file in files:
                        source_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_root, file)

                        if not os.path.exists(dest_file) or os.path.getmtime(source_file) > os.path.getmtime(dest_file):
                            shutil.copy2(source_file, dest_file)
                            print(f"Copying file {file} to {dest_root}")
                            logging.info(f"Copying file {file} to {dest_root}")

def delete_from_dest(source, dest):
    source_dir = os.listdir(source)
    dest_dir = os.listdir(dest)

    for file_name in dest_dir:
        replica_path = os.path.join(dest, file_name)
        if os.path.isfile(replica_path):
            if file_name not in source_dir:
                os.remove(replica_path)
                print(f"File {file_name} removed.")
                logging.info(f"File {file_name} removed.")
        elif os.path.isdir(replica_path):
            if file_name not in source_dir:
                shutil.rmtree(replica_path)
                print(f"Folder {file_name} removed.")
                logging.info(f"Folder {file_name} removed.")
            for roots, dirs, files in os.walk(replica_path):

                relative_path = os.path.relpath(roots, dest)
                source_root = os.path.join(source, relative_path)

                for file in files:
                    source_file = os.path.join(source_root, file)
                    dest_file = os.path.join(roots, file)

                    if not os.path.exists(source_file):
                        os.remove(dest_file)
                        print(f"Deleted file {dest_file}")
                        logging.info(f"Deleted file {dest_file}")
                
                for dir in dirs:
                    dest_dir_path = os.path.join(roots, dir)
                    source_dir_path = os.path.join(source_root, dir)

                    if not os.path.exists(source_dir_path):
                        shutil.rmtree(dest_dir_path)
                        print(f"Folder {dest_dir_path} removed from destination.")
                        logging.info(f"Folder {dest_dir_path} removed from destination.")

def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders (source -> replica).")
    parser.add_argument("source", help="Path to the source folder")
    parser.add_argument("replica", help="Path to the replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("logfile", help="Path to the directory where the log file should be stored")

    args = parser.parse_args()

    add_logfile(args.logfile)

    try:
        while True:
            copying_from_src(args.source, args.replica)
            delete_from_dest(args.source, args.replica)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("STOP")
        exit(1)

if __name__ == '__main__':
    main()
