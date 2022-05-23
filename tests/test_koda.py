from pathlib import Path

from koda.core import _encode, DataModel, _decode, _pack_message, _unpack_message, compress_file, decompress_file


def test_encode():
    assert bytearray(_encode(
        b"1321", model=DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9})
    )) == bytearray([0b11000100, 0b10000000])
    assert bytearray(_encode(
        b"1321321", model=DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9})
    )) == bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000])
    assert (
        bytearray(_decode(
            bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000]),
            model=DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9}),
            message_length=7,
        ))
        == b"1321321"
    )


def test_serialize():
    m = DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9})
    s = m.serialize()
    assert DataModel.from_serialized(s).count == m.count
    assert bytes(_pack_message(bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000]), 1024, m)) == (
        b"ARTPACK\n\x02\x04\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00(\x01\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xc5\x13@\x00"
    )
    message, message_length, model = _unpack_message(_pack_message(bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000]), 1024, m))
    assert bytearray(message) == b'\xc5\x13@\x00'
    assert model.count == m.count
    assert message_length == 1024


def test_compress():
    compress_file(Path("~/KODA/zpi.md"))
    decompress_file(Path("~/KODA/zpi.md.artpack"))