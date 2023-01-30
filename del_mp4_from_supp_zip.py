'''Deletes mp4 files from zipped files in a folder'''

import argparse
import os
import zipfile
import shutil


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--indir', default='./', help='input directory')
    parser.add_argument(
        '-o', '--outdir', default='./out', help='directory where data should be saved')
    
    args = parser.parse_args()
    indir = args.indir
    outdir = args.outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir) 

    for filename in os.listdir(indir):
        if filename.endswith(".zip"):
            print(filename)

            # Extracts the zip file and remove the mp4 files.
            with zipfile.ZipFile(os.path.join(indir, filename), "r") as zip_ref:
                members_to_keep = [member for member in zip_ref.namelist() if not member.endswith(".mp4")]
                zip_ref.extractall(outdir, members_to_keep)


            # Zips the remaining files.
            with zipfile.ZipFile(os.path.join(outdir, filename), "w") as zip_ref:
                for member in members_to_keep:
                    zip_ref.write(os.path.join(outdir, member), member)

            # Cleans up the temp files.
            for member in members_to_keep:
                member_path = os.path.join(outdir, member)
                if os.path.isdir(member_path):
                    shutil.rmtree(member_path)
                if os.path.isfile(member_path):
                    os.remove(member_path)