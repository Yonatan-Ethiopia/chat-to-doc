

import subprocess
import glob
import database

db = database.initdb()

def convert(job_id, md_path):
    db.update_status(job_id, "CONVERTING")
    epub_path = f"/home/yonatan/Bdoc/epubs/{job_id}.epub"
    print(f"Converting {md_path}...")

    command = [
        "pandoc", 
        md_path, 
        "-o", epub_path, 
        "--toc",  
        "--css", "style.css",
    ]

    fonts = glob.glob("./alegrayfont/static/*.ttf")
    for font in fonts:
        command.extend(["--epub-embed-font", font])

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        db.update_status(job_id, "COMPLETED")
        print(f"Doc saved to {epub_path}")
        
    except subprocess.CalledProcessError as e:
        db.update_status(job_id, "FAILED")
        print(f"Pandoc failed with error:\n{e.stderr}")
    except Exception as e:
        db.update_status(job_id, "FAILED")
        print(f"General Error: {e}")


