import os, re, shutil
from datetime import datetime, timedelta
from pathlib import Path

"""
Reformats obsidian daily note filenames to YYYY-MM-DD.md format.

Header infomation extrated from former filenames at added to H1 header, with the format:
YYYY-MM-DD Day [ — optional subheader]
"""

def run():
    ORIGINAL    = Path(r"C:\Users\jamie\Dropbox\Jamies Vault")
    COPY        = Path(r"C:\Users\jamie\OneDrive\Desktop\Jamies Vault")
    ISO_DATE    = re.compile(r"^(\d{4}-\d{2}-\d{2})")
    HEADING     = re.compile(r"[-—]\s(.*).md")
    WEEKDAYS    = dict(enumerate(["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]))

    shutil.rmtree(COPY)

    # Create copy to modify. Leave original untouched
    shutil.copytree(ORIGINAL, COPY)

    for root, subfolder, filenames in os.walk(COPY / "01 - Daily" / "Daily Notes"):

        for filename in filenames:
            if match := re.match(ISO_DATE, filename):
                target = Path(root) / filename
                title = ""
                try:
                    date = datetime.strptime(match.group(), "%Y-%m-%d")
                    ISO_date = date.strftime("%Y-%m-%d")
                    

                    yesterday = (date - timedelta(days=1)).strftime("%Y-%m-%d")
                    tomorrow  = (date + timedelta(days=1)).strftime("%Y-%m-%d")


                    day = WEEKDAYS[date.weekday()] 
                    title = f"# {date.strftime("%d/%m/%Y")} {day}"
                    
                    
                except Exception as e:
                    print(e)
                     

                with open(Path(root) / filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()
        
                    old_header = lines[0].strip()

                    if subheader := re.search(HEADING, old_header):
                        subheader = subheader.group(1).strip()
                        title += f" — {subheader}"

                    content = "".join(lines[4:])
        


                with open(Path(root) / filename, "w", encoding="utf-8") as f:
                    f.write(f"{title}\n")
                    f.write(f"← [[{yesterday}]] | [[{tomorrow}]] →\n")
                    f.write(content)
                    print("Changes made successfully to", filename)


                

            
if __name__ == "__main__":
    run()

    if False:
        ORIGINAL    = Path(r"C:\Users\jamie\Dropbox\Jamies Vault")
        COPY        = Path(r"C:\Users\jamie\OneDrive\Desktop\Jamies Vault")
        ISO_DATE    = re.compile(r"^(\d{4}-\d{2}-\d{2})")
        HEADING     = re.compile(r"[-—]\s(.*)")
        WEEKDAYS    = dict(enumerate(["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]))

        
        shutil.rmtree(COPY)

        # Create copy to modify. Leave original untouched
        shutil.copytree(ORIGINAL, COPY)

        with open(COPY / "01 - Daily" / "Daily Notes" / "2026" / "2026-01-21.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
            old_header = lines[0].strip()

            if subheader := re.search(HEADING, old_header):
                subheader = subheader.group(1)
            else:
                subheader = None

            

            content = lines[4:]
            

        

