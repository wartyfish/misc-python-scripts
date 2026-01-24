import os, re, shutil
from datetime import datetime, timedelta
from pathlib import Path

"""
Reformats obsidian daily note filenames to YYYY-MM-DD.md format.

Header infomation extrated from former filenames at added to H1 header, with the format:
YYYY-MM-DD Day [ — optional subheader]
"""

def run():

    p           = Path(r"C:\Users\Eem\Desktop\Jamies Vault\01 - Daily\Daily Notes")
    ISO_DATE    = re.compile(r"^(\d{4}-\d{2}-\d{2})")
    HEADING     = re.compile(r"[-—]\s(.*).md")
    WEEKDAYS    = dict(enumerate(["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]))

    # Create copy to modify. Leave original untouched
    shutil.copytree(Path(r"C:\Users\Eem\Desktop\backup vault 2401 delete later\Jamies Vault"), Path(r"C:\Users\Eem\Desktop\Jamies Vault"))

    for root, subfolder, filenames in os.walk(p):

        for filename in filenames:
            if match := re.match(ISO_DATE, filename):
                target = Path(root) / filename
                title = ""
                try:
                    date = datetime.strptime(match.group(), "%Y-%m-%d")
                    strf_date = date.strftime("%Y-%m-%d")

                    yesterday = (date - timedelta(days=1)).strftime("%Y-%m-%d")
                    tomorrow  = (date + timedelta(days=1)).strftime("%Y-%m-%d")

                    renamed = Path(root) / f"{date.strftime(strf_date)}.md"

                    target.rename(renamed)

                    day = WEEKDAYS[date.weekday()] 
                    title = f"# {strf_date} {day}"
                    
                    
                except Exception as e:
                    print(e)
            
                header = re.search(HEADING, filename)
                if header:
                    title += f" — {header.group(1)}"

                

                with open(renamed, "r", encoding="utf-8") as f:
                    text = f.read()

                with open(renamed, "w", encoding="utf-8") as f:
                    f.write(title + "\n\n")
                    f.write(f"← [[{yesterday}]]\n→ [[{tomorrow}]]\n")
                    f.write(text)
                    print("Changes made successfully to", filename)

                

            
if __name__ == "__main__":
    run()
