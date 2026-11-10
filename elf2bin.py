#!/usr/bin/env python3
"""Convert the sweet shim ELF (linked at 0) to a raw binary Image.
Replaces 'aarch64-linux-gnu-objcopy -O binary' + 'truncate -s image_size'.
The shim is position-independent and linked with . = 0. The raw image is the
PT_LOAD segments laid out at their virtual addresses, then padded to the value
in the Image header's image_size field (offset 16, LE u64) so ABL copies the
zero-filled .bss and the stacks too.
"""
import struct, sys

def load_elf(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:4] == b'\x7fELF', 'not an ELF'
    is64 = data[4] == 2
    assert is64, 'need 64-bit ELF'
    endian = '<' if data[5] == 1 else '>'
    e_phoff = struct.unpack_from(endian + 'Q', data, 0x20)[0]
    e_phentsize = struct.unpack_from(endian + 'H', data, 0x36)[0]
    e_phnum = struct.unpack_from(endian + 'H', data, 0x38)[0]
    segs = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type = struct.unpack_from(endian + 'I', data, off)[0]
        if p_type != 1:  # PT_LOAD
            continue
        p_offset = struct.unpack_from(endian + 'Q', data, off + 0x08)[0]
        p_vaddr  = struct.unpack_from(endian + 'Q', data, off + 0x10)[0]
        p_filesz = struct.unpack_from(endian + 'Q', data, off + 0x20)[0]
        p_memsz  = struct.unpack_from(endian + 'Q', data, off + 0x28)[0]
        segs.append((p_vaddr, p_offset, p_filesz, p_memsz))
    segs.sort(key=lambda s: s[0])
    return data, segs

def to_binary(elf_path, out_path):
    data, segs = load_elf(elf_path)
    end = max(v + memsz for v, off, fsz, memsz in segs)
    img = bytearray(end)
    for vaddr, offset, filesz, memsz in segs:
        img[vaddr:vaddr + filesz] = data[offset:offset + filesz]
    # pad to the image_size field in the header (offset 16), if larger than end
    image_size = struct.unpack_from('<Q', bytes(img), 16)[0]
    if image_size > len(img):
        img += bytes(image_size - len(img))
    with open(out_path, 'wb') as f:
        f.write(img)
    return len(img)

if __name__ == '__main__':
    n = to_binary(sys.argv[1], sys.argv[2])
    print(f'{sys.argv[2]}: {n} bytes')
