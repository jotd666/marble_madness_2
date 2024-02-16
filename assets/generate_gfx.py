# generate equivalent of Mark C format _gfx.* from MAME tilesaving edition gfxrips

from PIL import Image,ImageOps
import os,glob,collections,itertools

this_dir = os.path.abspath(os.path.dirname(__file__))
dumpdir = "dumps"
if not os.path.exists(dumpdir):
    os.mkdir(dumpdir)
for s in ["tiles","sprites"]:
    d = os.path.join(dumpdir,s)
    if not os.path.exists(d):
        os.mkdir(d)

palette = []
with open("palette.bin","rb") as f:
    mask = 0b11111
    for i in range(0x100):
        m = f.read(1)
        f.read(1)
        l = f.read(1)
        f.read(1)
        raw = (ord(m)<<8)+ord(l)
        b=(raw & mask)<<3
        g = ((raw>>5) & mask)<<3
        r = ((raw>>10) & mask)<<3

        palette.append((r,g,b))

def dump_image(subdir,size,s,palette,i):
    d = os.path.join(dumpdir,subdir)
    img = Image.new("RGB",size)
    c = iter(s)
    for y in range(size[1]):
        for x in range(size[0]):
            color = next(c)
            p = palette[color]
            img.putpixel((x,y),p)
    img=ImageOps.scale(img,5,resample=Image.Resampling.NEAREST)
    img.save(os.path.join(d,f"{i:06d}.png"))

def count_color(image):
    rval = set()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            p = image.getpixel((x,y))
            rval.add(p)

    return len(rval)

def write_tiles(blocks,size,f):
    for i,data in enumerate(blocks):
        f.write(f"  // ${i:X}\n  {{\n   ")
        offset = 0
        for k in range(size[1]):
            for j in range(size[0]):
                f.write("0x{:02x},".format(data[offset+j]))
            f.write("    // ")
            for j in range(size[0]):
                f.write(text_bitmap[data[offset+j] % 64])
            f.write("\n   ")
            offset+=size[0]
        f.write("   },\n")


game_name = "marble_madness_2"
text_bitmap = " .=#/:_%()@&*+:;!12345678abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
nb_tiles = 0x1000
tiles = []

for tile_name_l,tile_name_h in zip(["pf0l.3p",
"pf1l.3m",
"pf2l.3k",
"pf3l.3j",
],["pf0h.1p",
"pf1h.1m",
"pf2h.1k",
"pf3h.1j"]):
    tiles_file_l = os.path.join(this_dir,os.pardir,"mame",tile_name_l) # not included (copyright reasons LOL!)
    tiles_file_h = os.path.join(this_dir,os.pardir,"mame",tile_name_h) # not included (copyright reasons LOL!)

    with open(tiles_file_l,"rb") as fl,open(tiles_file_h,"rb") as fh:
        for _ in range(nb_tiles):
            # each 8x8 tile is 64 bytes each, using chunky pixel palette-indexed
            # value (simple is great!!)
            block = []
            for i in range(32):
                block.append(ord(fl.read(1)))
                block.append(ord(fh.read(1)))
            current = bytearray(block)

            tiles.append(current)

sprites = []
nb_sprites = 0x100

for sprite_name_h,sprite_name_l in zip(["mo0l.7p",
"mo1l.10p"],
[
"mo0h.12p",
"mo1h.14p",
]):
    tiles_file_h = os.path.join(this_dir,os.pardir,"mame",sprite_name_h) # not included (copyright reasons LOL!)
    tiles_file_l = os.path.join(this_dir,os.pardir,"mame",sprite_name_l) # not included (copyright reasons LOL!)

    with open(tiles_file_l,"rb") as fl,open(tiles_file_h,"rb") as fh:
        for _ in range(nb_sprites):
            block = []
            for i in range(128*4):
                block.append(ord(fl.read(1)))
                block.append(ord(fh.read(1)))
            current = bytearray(block)

            sprites.append(current)

nb_tiles = len(tiles)

##for i,t in enumerate(tiles,1):
##    dump_image("tiles",(8,8),t,palette,i)

for i,s in enumerate(sprites,1):
    dump_image("sprites",(32,32),s,palette,i)

if False:
    with open(os.path.join(this_dir,f"{game_name}_gfx.h"),"w") as f:
            inc_protect = f"__{game_name.upper()}_GFX_H__"
            f.write(f"""#ifndef {inc_protect}
    #define {inc_protect}


    #define NUM_TILES {nb_tiles}
    #define NUM_SPRITES {nb_sprites}

    #endif //  {inc_protect}
    """
    )
    with open(os.path.join(this_dir,f"{game_name}_gfx.c"),"w") as f:
        f.write(f"""#include "{game_name}_gfx.h"

    // tile data
    """)
        sz = (8,8)
        f.write(f"uint8_t tile[NUM_TILES][{sz[0]*sz[1]}] =\n{{")

        write_tiles(tiles,sz,f)

        f.write("};\n")
        sz = (16,16)
        f.write(f"uint8_t sprite[NUM_SPRITES][{sz[0]*sz[1]}] =\n{{")

        write_tiles(sprites,sz,f)

        f.write("};\n")
