import os
from zipfile import ZipFile

def zip_folders_and_files(zip_filename, items_to_zip, merge_folders=False):
    with ZipFile(zip_filename, 'w') as zipf:
        for item in items_to_zip:
            if os.path.isfile(item):
                zipf.write(item, os.path.basename(item))
            elif os.path.isdir(item):
                if merge_folders:
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, item)
                            zipf.write(file_path, arcname)
                else:
                    zipf.write(item, os.path.basename(item))

if __name__ == "__main__":
    folders_and_files = ['python', 'client.py', 'decoder.py', 'ShadowScript.cmd', 'LICENSE']
    zip_filename = 'ShadowScriptClient.zip'
    # python client.py --url shadowscript-production.up.railway.app --room  --retry-interval 10 --debug

    # Set merge_folders to True if you want to merge the contents of folders
    merge_folders = False
    
    WIN_config = {
        "room" : "room1",
        "url" : "shadowscript-production.up.railway.app" , 
        "retryinterval": "10", # in seconds
        "debug":"--debug" if True else ""
    }  
    
    zip_folders_and_files(zip_filename, folders_and_files, merge_folders)

    print(f'{zip_filename} created successfully.')
