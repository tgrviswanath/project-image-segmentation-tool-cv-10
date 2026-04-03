"""
Generate sample images for cv-10 Image Segmentation Tool.
Run: pip install Pillow && python generate_samples.py
Output: 4 images — outdoor scene, kitchen, street, aerial view.
"""
from PIL import Image, ImageDraw
import os

OUT = os.path.dirname(__file__)


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def outdoor_scene():
    img = Image.new("RGB", (640, 480), (135, 190, 230))
    d = ImageDraw.Draw(img)
    # sky gradient bands
    for i, c in enumerate([(135, 190, 230), (155, 205, 240), (175, 215, 245)]):
        d.rectangle([0, i * 60, 640, (i + 1) * 60], fill=c)
    # mountains
    d.polygon([(0, 280), (160, 120), (320, 280)], fill=(120, 130, 150))
    d.polygon([(200, 280), (400, 100), (600, 280)], fill=(100, 115, 140))
    d.polygon([(400, 280), (560, 150), (640, 280)], fill=(130, 140, 160))
    # ground
    d.rectangle([0, 280, 640, 480], fill=(80, 150, 60))
    # river
    d.polygon([(200, 480), (240, 280), (280, 280), (320, 480)], fill=(80, 140, 200))
    # trees
    for tx in [50, 120, 500, 580]:
        d.rectangle([tx - 6, 260, tx + 6, 310], fill=(100, 70, 40))
        d.ellipse([tx - 30, 210, tx + 30, 275], fill=(40, 130, 40))
    # sun
    d.ellipse([540, 30, 600, 90], fill=(255, 230, 80))
    return img


def kitchen_scene():
    img = Image.new("RGB", (640, 480), (240, 230, 220))
    d = ImageDraw.Draw(img)
    # floor
    d.rectangle([0, 360, 640, 480], fill=(180, 160, 130))
    for x in range(0, 640, 80):
        d.line([x, 360, x, 480], fill=(160, 140, 110), width=1)
    # counter
    d.rectangle([0, 280, 640, 365], fill=(200, 180, 150))
    d.rectangle([0, 270, 640, 285], fill=(160, 140, 110))
    # cabinets
    for cx in range(0, 640, 160):
        d.rectangle([cx + 5, 80, cx + 150, 270], fill=(210, 195, 170), outline=(170, 150, 120), width=2)
        d.ellipse([cx + 70, 170, cx + 85, 185], fill=(180, 150, 80))
    # sink
    d.rectangle([240, 285, 400, 360], fill=(180, 200, 210))
    d.ellipse([300, 295, 340, 350], fill=(160, 180, 190))
    # stove
    d.rectangle([440, 285, 600, 360], fill=(60, 60, 60))
    for bx, by in [(470, 300), (530, 300), (470, 335), (530, 335)]:
        d.ellipse([bx - 15, by - 15, bx + 15, by + 15], fill=(40, 40, 40))
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(80, 80, 80))
    return img


def street_aerial():
    img = Image.new("RGB", (640, 640), (100, 100, 100))
    d = ImageDraw.Draw(img)
    # roads
    d.rectangle([260, 0, 380, 640], fill=(80, 80, 80))
    d.rectangle([0, 260, 640, 380], fill=(80, 80, 80))
    # road markings
    for y in range(0, 260, 60):
        d.rectangle([312, y, 328, y + 40], fill=(255, 255, 255))
    for y in range(380, 640, 60):
        d.rectangle([312, y, 328, y + 40], fill=(255, 255, 255))
    for x in range(0, 260, 60):
        d.rectangle([x, 312, x + 40, 328], fill=(255, 255, 255))
    for x in range(380, 640, 60):
        d.rectangle([x, 312, x + 40, 328], fill=(255, 255, 255))
    # buildings (top-down)
    for bx, by, bw, bh, bc in [
        (20, 20, 200, 200, (180, 170, 160)), (420, 20, 200, 200, (160, 150, 140)),
        (20, 420, 200, 200, (190, 180, 170)), (420, 420, 200, 200, (170, 160, 150)),
    ]:
        d.rectangle([bx, by, bx + bw, by + bh], fill=bc, outline=(120, 110, 100), width=3)
    # cars (top-down)
    for cx, cy, cc in [(290, 50, (200, 50, 50)), (290, 180, (50, 100, 200)),
                        (50, 300, (50, 180, 80)), (500, 310, (200, 180, 50))]:
        d.rectangle([cx, cy, cx + 20, cy + 40], fill=cc)
    return img


def living_room():
    img = Image.new("RGB", (640, 480), (230, 220, 210))
    d = ImageDraw.Draw(img)
    # floor
    d.rectangle([0, 360, 640, 480], fill=(160, 140, 110))
    # wall
    d.rectangle([0, 0, 640, 365], fill=(230, 220, 210))
    # sofa
    d.rectangle([60, 260, 380, 380], fill=(100, 80, 160))
    d.rectangle([60, 230, 380, 270], fill=(120, 100, 180))
    d.rectangle([60, 230, 100, 380], fill=(120, 100, 180))
    d.rectangle([340, 230, 380, 380], fill=(120, 100, 180))
    # coffee table
    d.rectangle([160, 370, 320, 395], fill=(140, 100, 60))
    # tv + stand
    d.rectangle([440, 80, 620, 240], fill=(20, 20, 20))
    d.rectangle([450, 90, 610, 230], fill=(30, 60, 100))
    d.rectangle([510, 240, 550, 280], fill=(40, 40, 40))
    d.rectangle([480, 275, 580, 285], fill=(60, 60, 60))
    # window
    d.rectangle([80, 60, 260, 200], fill=(180, 220, 255))
    d.line([170, 60, 170, 200], fill=(200, 190, 180), width=3)
    d.line([80, 130, 260, 130], fill=(200, 190, 180), width=3)
    return img


if __name__ == "__main__":
    print("Generating cv-10 samples...")
    save(outdoor_scene(), "sample_outdoor.jpg")
    save(kitchen_scene(), "sample_kitchen.jpg")
    save(street_aerial(), "sample_aerial.jpg")
    save(living_room(), "sample_living_room.jpg")
    print("Done — 4 images in samples/")
