from itertools import chain
from pathlib import Path

from koda.core import (
    BitStream,
    DataModel,
    _decode,
    _encode,
    _pack_message,
    _unpack_message,
    compress_file,
    decompress_file,
    iter_bits,
)


def test_encode():
    assert bytearray(
        _encode(b"1321", model=DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9}))
    ) == bytearray([0b11000100, 0b10000000])
    assert bytearray(
        _encode(b"1321321", model=DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9}))
    ) == bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000])
    assert (
        bytearray(
            _decode(
                bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000]),
                model=DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9}),
                message_length=7,
            )
        )
        == b"1321321"
    )


def test_failing_case_a():
    m = DataModel({ord("1"): 43, ord("2"): 1, ord("3"): 9})
    assert (
        bytearray(_decode(_encode(b"1321321", model=m), model=m, message_length=7))
        == b"1321321"
    )


def test_failing_case_b():
    m = DataModel({ord("1"): 44, ord("2"): 1, ord("3"): 531})

    print(bytes(_encode(b"133", model=m)))
    assert (
        bytearray(_decode(_encode(b"133", model=m), model=m, message_length=3))
        == b"133"
    )


def test_bit_stream():
    s = BitStream()
    assert tuple(
        iter_bits(
            bytearray(
                chain(
                    s.add(0),
                    s.add(1),
                    s.add(0),
                    s.add(0),
                    s.add(1),
                    s.add(0),
                    s.add(0),
                    s.add(1),
                    s.add(0),
                    s.add(1),
                    s.close(),
                )
            ),
            10,
        )
    ) == (0, 1, 0, 0, 1, 0, 0, 1, 0, 1)


def test_serialize():
    m = DataModel({ord("1"): 40, ord("2"): 1, ord("3"): 9})
    s = m.serialize()
    assert DataModel.from_serialized(s).count == m.count
    assert bytes(
        _pack_message(
            bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000]), 1024, m
        )
    ) == (
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
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\xc5\x13@\x00")
    message, message_length, model = _unpack_message(
        _pack_message(
            bytearray([0b11000101, 0b00010011, 0b01000000, 0b00000000]), 1024, m
        )
    )
    assert bytearray(message) == b"\xc5\x13@\x00"
    assert model.count == m.count
    assert message_length == 1024


def test_compress():
    res_dir = Path(__file__).parent / "res"
    for p in res_dir.iterdir():
        if p.suffix == '.pgm':
            compress_file(Path(p))
            decompress_file(Path(p.with_suffix(".pgm.artpack")))
