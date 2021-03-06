from __future__ import absolute_import, division, print_function

import struct

def send_packet(sender, packet, extra=bytes()):
    size = len(extra) + 4 + len(packet)
    data = extra + struct.pack('>L', size) + packet
    sender(data)

    return data

def recv_packet(reader, extra=None):
    if extra is not None:
        prefix = reader(extra)
    header = reader(4)
    length, = struct.unpack('>L', header)
    if extra is not None:
        data = reader(length - 4 - extra)
    else:
        data = reader(length - 4)

    if extra is not None:
        return prefix, header, data
    else:
        return header, data

def send_encrypted_packet(sender, cipher, cmd, packet):
    cipher.reset()

    header = struct.pack('>BH', cmd, len(packet))
    data = cipher.encrypt(header + packet)
    data += cipher.finish(4)
    sender(data)

    cipher.nonce += 1

    return data

def recv_encrypted_packet(reader, cipher):
    cipher.reset()

    header = reader(3)
    header = cipher.decrypt(header)

    cmd, length = struct.unpack('>BH', header)

    data = reader(length)
    data = cipher.decrypt(data)

    mac = reader(4)
    assert cipher.finish(4) == mac

    cipher.nonce += 1
    return cmd, data

