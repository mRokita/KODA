import math
import os
from collections import defaultdict
from itertools import islice, chain
from pathlib import Path
from typing import Dict, Iterable, Mapping, Literal, Union, Tuple, Optional
from rich.progress import track


def get_binary_representation(value):
    return "{0:b}".format(value)


def get_cumulated_count(count: Dict[int, int]):
    total_count = 0
    cum_count: Dict[int, int] = {-1: 0}
    for byte, occurrences in count.items():
        total_count += occurrences
        cum_count[byte] = total_count
    return cum_count


def iter_bytes(file_object) -> Iterable[int]:
    while (symbol := file_object.read(1)) != b"":
        yield int.from_bytes(symbol, "big")


def get_byte_count(data: Iterable[int]):
    count = defaultdict(lambda: 0)
    for symbol in data:
        count[symbol] += 1
    return count


def get_entropy(cumul_count: Dict[int, int]):
    total_count = sum(cumul_count.values())
    total_entropy = 0
    for occurrences in cumul_count.values():
        p = occurrences / total_count
        if p > 0:
            total_entropy -= p * math.log2(p)
    return total_entropy


class DataModel:
    """
    Data model, describes, how often symbols (bytes 0-255),
    occur in encoded files.
    """

    def __init__(self, byte_count: Mapping[int, int] = None):
        count = dict(byte_count)
        self.count = dict((i, count.get(i, 0)) for i in range(256))
        self._cumulated_count = get_cumulated_count(self.count)
        self.total_count = sum(self.count.values())
        self.m_value = math.ceil(math.log2(self.total_count * 4))
        self.entropy = get_entropy(self._cumulated_count)

    def get_cum_count(self, byte: int, include_self=True):
        if not include_self:
            byte -= 1
        return self._cumulated_count[byte]

    def serialize(self) -> bytearray:
        max_val = max(self.count.values())
        length = math.ceil(math.log2(max_val) / 8)
        return b"".join(
            [length.to_bytes(1, "big")]
            + [self.count[i].to_bytes(length, "big") for i in range(256)]
        )

    @classmethod
    def from_serialized(cls, data: Iterable[int]) -> "DataModel":
        data_iter = iter(data)
        length = next(data_iter)
        data_iter = islice(data_iter, 256 * length)
        count = dict()
        for byte, count_val in enumerate(zip(*[data_iter] * length)):
            val = int.from_bytes(count_val, "big")
            count[byte] = val
        return DataModel(count)


def get_total_count(frequency_table):
    return sum(frequency_table.values())


def get_msb_0_condition(l, u, m_value):
    return (l & (1 << m_value - 1)) == 0 and (u & (1 << m_value - 1)) == 0


def get_msb_1_condition(l, u, m_value):
    return (l & (1 << m_value - 1)) > 0 and (u & (1 << m_value - 1)) > 0


def get_e3_condition(l, u, m_value):
    return l & (1 << m_value - 2) > 0 and u & (1 << m_value - 2) == 0


def get_conditions(l, u, m_value):
    return (
        get_msb_0_condition(l, u, m_value),
        get_msb_1_condition(l, u, m_value),
        get_e3_condition(l, u, m_value),
    )


class BitStream:
    def __init__(self):
        self.bits = 0
        self.current_byte = 0
        self.message = ""

    def add(self, bit: int) -> Iterable[int]:
        if bit == 0:
            self.bits += 1
            self.current_byte *= 2
        elif bit == 1:
            self.bits += 1
            self.current_byte *= 2
            self.current_byte += 1
        if self.bits % 8 == 0:
            yield self.current_byte
            self.current_byte = 0

    def close(self) -> Optional[int]:
        if self.bits % 8 != 0:
            close_byte = self.current_byte * 2 ** (8 - (self.bits % 8))
            yield close_byte


def _encode(data: Iterable[int], *, model: DataModel) -> bytearray:
    m_value = model.m_value
    most_significant_bit = pow(2, m_value - 1)
    second_most_significant_bit = pow(2, m_value - 2)
    total_count = model.total_count
    scale3 = 0
    l = 0
    u = pow(2, m_value) - 1
    stream = BitStream()

    for byte in data:
        l_old = l
        u_old = u
        l = l_old + math.floor(
            ((u_old - l_old + 1) * model.get_cum_count(byte, include_self=False))
            / total_count
        )
        u = (
            l_old
            + math.floor(
                ((u_old - l_old + 1) * model.get_cum_count(byte)) / total_count
            )
            - 1
        )

        msb_0_condition, msb_1_condition, e3_condition = get_conditions(l, u, m_value)
        while msb_0_condition or msb_1_condition or e3_condition:
            if msb_0_condition:
                l = l << 1
                u = 1 ^ (u << 1)
                yield from stream.add(0)
                while scale3 > 0:
                    yield from stream.add(1)
                    scale3 -= 1
            elif msb_1_condition:
                l = (most_significant_bit ^ l) << 1
                u = 1 ^ ((most_significant_bit ^ u) << 1)
                yield from stream.add(1)
                while scale3 > 0:
                    yield from stream.add(0)
                    scale3 -= 1
            elif e3_condition:
                l = (second_most_significant_bit ^ l) << 1
                u = most_significant_bit ^ u
                u = 1 ^ ((second_most_significant_bit ^ u) << 1)
                scale3 += 1
            msb_0_condition, msb_1_condition, e3_condition = get_conditions(
                l, u, m_value
            )

    l_binary = get_binary_representation(l)
    yield from stream.add(int(l_binary[0]))
    while scale3 > 0:
        yield from stream.add(1)
        scale3 -= 1
    for l in range(m_value - len(l_binary)):
        yield from stream.add(0)
    for bit in l_binary[1:]:
        yield from stream.add(bit)
    yield from stream.close()


def iter_bits(
    data: Iterable[int], limit: int = None
) -> Iterable[Union[Literal[0], Literal[1]]]:
    loaded = 0
    for byte in data:
        for i in reversed(range(8)):
            yield (byte >> i) & 1
            loaded += 1
            if limit and loaded >= limit:
                return


def _pack_message(
    encoded_data: bytearray, message_length, model: DataModel
) -> Iterable[int]:
    banner = b"ARTPACK\n"
    message_length_len = math.ceil(math.log2(message_length) / 8)
    message_length_serialized = message_length_len.to_bytes(
        1, "big"
    ) + message_length.to_bytes(message_length_len, "big")
    model_serialized = model.serialize()
    yield from banner + message_length_serialized + model_serialized + b"\n"
    yield from encoded_data


def _unpack_message(packed_message: bytearray) -> Tuple[Iterable[int], int, DataModel]:
    msg_iter = iter(packed_message)
    assert bytes(islice(msg_iter, 0, 8)) == b"ARTPACK\n"
    message_length_len = next(msg_iter)
    message_length = int.from_bytes(islice(msg_iter, 0, message_length_len), "big")
    model = DataModel.from_serialized(msg_iter)
    m = bytes([next(msg_iter)])
    assert m == b"\n", m
    return msg_iter, message_length, model


def compress_file(
    path: Path, out_path: Path, iter_wrapper=lambda iter_: iter_
) -> Tuple[Path, DataModel]:
    with path.expanduser().open("rb") as fo:
        model = DataModel(get_byte_count(chain(iter_bytes(fo), b"\x00")))
    message_length = sum(model.count.values())
    if not out_path:
        out_path = path.expanduser().with_suffix(path.suffix + ".artpack")
    with path.expanduser().open("rb") as fo:
        pack_iter = iter(
            _pack_message(
                bytes(
                    _encode(iter_wrapper(chain(iter_bytes(fo), b"\x00")), model=model)
                ),
                message_length=message_length,
                model=model,
            )
        )
        with out_path.open("wb") as fo_out:
            while chunk := bytearray(islice(pack_iter, 0, 64)):
                fo_out.write(chunk)
    return out_path, model


def decompress_file(path: Path, out_path: Path = None):
    path = path.expanduser()
    assert path.suffix.endswith(".artpack")

    if not out_path:
        out_path = path.with_suffix(path.suffix.rsplit(".artpack", maxsplit=1)[0])
        if out_path.exists():
            out_path = out_path.with_stem(out_path.stem + "(artunpacked)")

    with path.expanduser().open("rb") as fo:
        encoded_msg, message_len, model = _unpack_message(iter_bytes(fo))
        data_iter = _decode(encoded_msg, message_length=message_len, model=model)
        with out_path.expanduser().open("wb") as fo_out:
            while chunk := bytearray(islice(data_iter, 0, 64)):
                fo_out.write(chunk)
            fo_out.truncate(message_len - 1)


def _decode(data: bytearray, message_length: int, model: DataModel):
    m_value = model.m_value
    most_significant_bit = pow(2, m_value - 1)
    second_most_significant_bit = pow(2, m_value - 2)
    total_count = model.total_count
    l = 0
    u = pow(2, m_value) - 1
    bit_iter = iter_bits(data)
    t = int("".join(str(i) for i in islice(bit_iter, 0, m_value)), 2)
    bytes_loaded = 0

    while True:
        current_number = math.floor(((t - l + 1) * total_count - 1) / (u - l + 1))
        current_byte = 0
        count = 0
        for k, v in model.count.items():
            if current_number >= count:
                current_byte = k
                count += v
            else:
                break
        yield current_byte
        bytes_loaded += 1

        if bytes_loaded == message_length:
            return

        l_old = l
        u_old = u
        l = l_old + math.floor(
            ((u_old - l_old + 1) * model.get_cum_count(current_byte, False))
            / total_count
        )
        u = (
            l_old
            + math.floor(
                ((u_old - l_old + 1) * model.get_cum_count(current_byte)) / total_count
            )
            - 1
        )

        msb_0_condition, msb_1_condition, e3_condition = get_conditions(l, u, m_value)
        while msb_0_condition or msb_1_condition or e3_condition:
            try:
                current_bit = next(bit_iter)
            except StopIteration:
                break
            if (t & (1 << m_value - 1)) == 0:
                t = t << 1
            elif (t & (1 << m_value - 1)) > 0:
                t = 1 ^ ((most_significant_bit ^ t) << 1)
            if (current_bit == 1 and t & 1 == 0) or (current_bit == 0 and t & 1 > 0):
                t = 1 ^ t
            if msb_0_condition:
                l = l << 1
                u = 1 ^ (u << 1)
            elif msb_1_condition:
                l = (most_significant_bit ^ l) << 1
                u = 1 ^ ((most_significant_bit ^ u) << 1)
            elif e3_condition:
                l = (second_most_significant_bit ^ l) << 1
                u = most_significant_bit ^ u
                u = 1 ^ ((second_most_significant_bit ^ u) << 1)
                t = most_significant_bit ^ t

            msb_0_condition, msb_1_condition, e3_condition = get_conditions(
                l, u, m_value
            )
