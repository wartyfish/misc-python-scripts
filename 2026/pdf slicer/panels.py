from pathlib import Path
from PIL import Image

colour_codes = {value: index for index, value in enumerate(
    ["M", "Y", "O", "R", "Pi", "P", "B", "BG", "G", "Br", "Gy", "Bk"]
    )}

thumbs = Path(r"C:\Users\Eem\Desktop\pdf sandbox\dyes")


dyes = [
    "Raven",
    "Shiitake",
    "Timber wolf",
    "Black Cherry"
]


filepaths = []

for img in thumbs.iterdir():
    for dye in dyes:
        if dye.lower() in img.name.lower():
            filepaths.append(img)


filepaths = sorted(
    filepaths,
    key=lambda c: colour_codes[c.name.split("_")[1]]
)           



# settings
grid_size = (2, 2)
spacing = 5 # px
thumb_size = (300, 300)

images = [Image.open(p).resize(thumb_size) for p in filepaths]

# determine canvas size
width = grid_size[0] * thumb_size[0] + (grid_size[0] - 1) * spacing
height = grid_size[1] * thumb_size[1] + (grid_size[1] -1) * spacing

# create blank canvas
canvas = Image.new("RGB", (width, height), color=(0, 0, 0))

# paste images into grid
for index, img in enumerate(images):
    row = index // grid_size[0]
    col = index % grid_size[0]

    x = col * (thumb_size[0] + spacing)
    y = row * (thumb_size[1] + spacing)

    canvas.paste(img, (x, y))

# save result
canvas.save("output_grid.jpeg")