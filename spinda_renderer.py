from spindafy import SpindaConfig
from argparse import ArgumentParser
from PIL import Image

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("pid")
    parser.add_argument("--scale", dest="scale", default=1, action="store", nargs="?", type=int)
    parser.add_argument("--save", action='store_true')
    parser.add_argument("--show", action='store_true')

    args = parser.parse_args()

    config = SpindaConfig.from_personality(int(args.pid, 16))
    img = config.render_pattern()

    img = img.resize((img.width*args.scale, img.height*args.scale), Image.Resampling.NEAREST)

    if args.save:
        img.save(hex(get_personality(config)) + ".png")
    if args.show or not args.save:
        img.show()