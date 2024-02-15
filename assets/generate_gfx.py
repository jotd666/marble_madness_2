# generate equivalent of Mark C format _gfx.* from MAME tilesaving edition gfxrips

#from PIL import Image,ImageOps
import os,glob,collections,itertools

this_dir = os.path.abspath(os.path.dirname(__file__))

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
nb_tiles = 0x800
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
            # each 8x8 tile is 32 bytes each
            # each half-byte is a pixel 0-F being the index of the selected CLUT
            block = []
            for i in range(32):
                block.append(ord(fl.read(1)))
                block.append(ord(fh.read(1)))
            current = bytearray(block)


            tiles.append(current)

with open(os.path.join(this_dir,f"{game_name}_gfx.h"),"w") as f:
        inc_protect = f"__{game_name.upper()}_GFX_H__"
        f.write(f"""#ifndef {inc_protect}
#define {inc_protect}


#define NUM_TILES {nb_tiles}

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
