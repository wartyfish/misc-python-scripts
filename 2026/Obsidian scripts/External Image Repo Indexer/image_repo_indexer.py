from pathlib import Path

def build_image_gallery(repo: Path, index: Path, image_width: int=150) -> None:
    images = sorted(
        [f for f in repo.iterdir() if f.name != "Thumbs.db"],
        key=lambda f: f.stat().st_mtime, 
        reverse=True
    )
    
    lines = []
    for file in images:
        file_formatted = f'"file:///{str(file).replace(chr(92), "/")}"'
        image_link = f"[{file.name}]({file_formatted})"
        lines.append(image_link)
        lines.append(f'<figure><img src={file_formatted} width="{image_width}"></figure>')



    with open(index, "w", encoding="utf-8") as f:
        f.write("# Tie Dye Inspo Gallery\n")
        f.write("\n".join(lines))
        f.write("\n")
        f.write("***")
        f.write("[[Dashboard]] | [[Tie Dye Dashboard]]")
        print("Tie Dye Inspo note updated.")


def build_file_index(repo: Path, index: Path, thumbnail: bool = False) -> None:
    index = sorted(
        [f for f in repo.iterdir() if f.name != "Thumbs.db"],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    


if __name__ == "__main__":
    REPO = Path(r"P:\Obsidian vault backups\_Vault Image Repo\Tie Dye Inspo")
    INDEX = Path(r"C:\Users\Eem\Dropbox\Jamies Vault\03 Projects\Tie Dye\Image Index.md")
    THUMNAIL_WIDTH = 500

    build_image_gallery(REPO, INDEX, THUMNAIL_WIDTH)