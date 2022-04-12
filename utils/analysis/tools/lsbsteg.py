#!/usr/bin/env python3
import sys
import argparse
import hashlib
from PIL import Image

encryption_support = True
try:
    from Crypto import Random
    from Crypto.Cipher import AES
except ImportError:
    encryption_support = False

HASH_SIZE = 32
SIZE_FIELD_LEN = 64


def bits_from_int(i, width=1):
    bits = bin(i)[2:].zfill(width)
    return [int(b) for b in bits]


def bits_from_str(s):
    return bits_from_bytes(s.encode('utf-8'))


def bits_from_bytes(bytes):
    bits = []
    for b in bytes:
        bits.extend([((b >> i) & 1) for i in range(7, -1, -1)])

    return bits


def bytes_from_bits(bits):
    bytes = []

    lenBits = len(bits)
    for i in range(0, lenBits, 8):
        byte = bits[i:i+8]
        bytes.append(sum([(byte[8-b-1] << b) for b in range(7, -1, -1)]))

    return bytes


def set_bit(target, index, value):
    mask = 1 << index
    target &= ~mask
    return target | mask if value else target


def aes_pad(msg):
    pad_len = AES.block_size - (len(msg) % AES.block_size)
    return msg + pad_len * chr(pad_len)


def aes_unpad(msg):
    return msg[:-msg[-1]]


def encrypt(msg, passphraze):
    passphraze = hashlib.sha256(bytes(passphraze, 'utf-8')).digest()

    hash = hashlib.sha256(bytes(msg, 'utf-8')).digest()
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(passphraze, AES.MODE_CBC, iv)

    return hash + iv + cipher.encrypt(aes_pad(msg))


def decrypt(msg, passphraze):
    passphraze = hashlib.sha256(bytes(passphraze, 'utf-8')).digest()

    hash = msg[:HASH_SIZE]
    iv = msg[HASH_SIZE:HASH_SIZE+AES.block_size]

    cipher = AES.new(passphraze, AES.MODE_CBC, iv)
    msg = aes_unpad(cipher.decrypt(msg[HASH_SIZE+AES.block_size:]))

    return msg, hash == hashlib.sha256(msg).digest()


def embed_message(bits, img):
    pixels = img.load()
    width, height = img.size
    pixel_comps = len(pixels[0, 0])

    padding = []
    if SIZE_FIELD_LEN % pixel_comps != 0:
        padding = (pixel_comps - SIZE_FIELD_LEN % pixel_comps) * [0]

    bits = bits_from_int(len(bits), SIZE_FIELD_LEN) + padding + bits
    if len(bits) > width * height * pixel_comps:
        raise Exception('The message you are trying to embed is too long')

    bits = iter(bits)
    for x in range(width):
        for y in range(height):
            pixel = list(pixels[x, y])
            for i, b in enumerate(pixel):
                bit = next(bits, None)
                if bit is None:
                    pixels[x, y] = tuple(pixel)
                    return

                pixel[i] = set_bit(b, 0, bit)

            pixels[x, y] = tuple(pixel)


def extract_length(pixels, width, height):
    bits = []
    for x in range(width):
        for y in range(height):
            if len(bits) >= SIZE_FIELD_LEN:
                return int(''.join(map(str, bits[:SIZE_FIELD_LEN])), 2), x, y

            pixel = list(pixels[x, y])
            bits.extend([(b & 1) for b in pixel])


def extract_message(img):
    pixels = img.load()

    width, height = img.size
    length, offset_x, offset_y = extract_length(pixels, width, height)

    bits = []
    for x in range(offset_x, width):
        for y in range(offset_y, height):
            pixel = list(pixels[x, y])
            for b in pixel:
                if len(bits) == length:
                    return bytes(bytes_from_bits(bits))

                bits.append(b & 1)


def embed(args, image):
    bits = []
    if hasattr(args, 'key'):
        bits = bits_from_bytes(encrypt(args.message, args.key))
    else:
        bits = bits_from_str(args.message)

    embed_message(bits, image)
    image.save(args.output if args.output else args.image)


def extract(args, image):
    message = extract_message(image)

    if hasattr(args, 'key'):
        message, ok = decrypt(message, args.key)
        if not ok:
            raise Exception('Could not decrypt message with the provided key')

    print(message.decode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    subparsers = parser.add_subparsers(help='actions')
    parser.add_argument('-v', '--version', help='show version info and exit',
                        version='%(prog)s 0.1', action='version')

    # embed subparser
    em = subparsers.add_parser('embed', help='embed message into image')
    em.add_argument('image', metavar='IMAGE', help='source image')
    em.add_argument('message', metavar='MESSAGE', help='message to embed')
    em.add_argument('-o', '--output', metavar='OUT', help='output image')
    em.set_defaults(func=embed)

    # extract subparser
    ex = subparsers.add_parser('extract', help='extract message from image')
    ex.add_argument('image', metavar='IMAGE', help='image containing message')
    ex.set_defaults(func=extract)

    if encryption_support:
        em.add_argument('-k', '--key', metavar='KEY', help='encryption key')
        ex.add_argument('-k', '--key', metavar='KEY', help='decryption key')

    args = parser.parse_args()

    try:
        image = Image.open(args.image)
    except:
        sys.exit('Could not open source image')

    if image.mode in ['1', '1;I', '1;R']:
        sys.exit('Cannot embed messages in black and white images')
    if image.mode == 'P':
        sys.exit('Cannot embed messages in palette-mapped image')

    try:
        args.func(args, image)
    except Exception as e:
        sys.exit(e)
