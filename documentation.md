---
title: Projekt KODA - Etap III
lang: pl-PL
standalone: true
author:
- Mateusz Kubiszewski
- Michał Rokita
- Emilian Gałązka
toc: true
ctoc: false
date: \today{}
forcelinenos: true
listingsbackground: eeeeee
linenos: left
...

# Wstęp

W drugim etapie projektu wykonaliśmy prototypowy koder i dekoder oparty na arytmetycznym kodowaniu całkowitoliczbowym. Program składa się z głównego modułu core  oraz funkcji main służącej do wyświetlania i GUI. Osobno znajduję się również folder ze skryptem do testowania poprawności algorytmu kompresji. Stworzony został również makefile, który pozwala na szybkie testowanie algorytmów za pomocą modułu poetry. 

# Zaimplementowany program

Biblioteka koduje i zapisuje zakodowane pliki z rozszerzeniem .artpack, następnie je pobiera i dekoduje ponownie na rozszerzenie źródłowe.
Moduł `core` zawiera implementację algorytmu kodera wraz z funkcjami pomocniczymi.

Pełny kod źródłowy jest dostępny pod adresem <https://github.com/mRokita/KODA>

Istotną cechą implementacji jest oparcie na generatorach języka Python - dane nie muszą być ładowane w całości do pamięci operacyjnej.


## Funkcje pomocnicze

Poniżej zostały opisane najważniejsze funkcje pomocnicze i klasy tworzące program.

1. `DataModel`  
	Klasa odpowiadająca za przechowywanie modelu danych - informacji na temat częstotliwości występowania poszczególnych symboli (bajty 0-255).
	Metoda `serialize` pozwala na serializację tych danych.

1. `iter_bits` (fragment kodu \ref{lst:iter_bits})  
	Zwraca iterator, który przechodzi przez kolejne bity zadanej listy bajtów.
	
1. `iter_bytes`  
	Zwraca iterator, który przechodzi przez kolejne bajty pliku.
	
1. `get_msb_0_condition(l, u, m_value) ,get_msb_1_condition(l, u, m_value), get_e3_condition(l, u, m_value)` (fragment kodu \ref{lst:conditions})  
	Na podstawie podanych granic przedziału zwracane są warunki po których następuje przeskalowanie przedziału

1. `get_conditions(l, u, m_value)`  
	Zwraca wartości wyżej wymienionych trzech warunków.
	
1. `def get_byte_count(data: Iterable[int])`  
	Zwraca ilość wystąpień każdej wartości na zwartych w strumieniu bajtów `data`.
	
1. `BitStream` (fragment kodu \ref{lst:BitStream})  
	Klasa, która pozwala na przetwarzanie bitów spływających w procesie kodowania na kolejne bajty zakodowanej wiadomości. Gdy zostanie zamknięta, ostatni bajt zostaje "zakończony" zerami.
	
## Funkcje wykonawcze


1. `_encode(data: Iterable[int], *, model: DataModel = None) -> bytearray` (fragment kodu \ref{lst:_encode})  
	Implementacja algorytmu kodowania arytmetycznego całkowitoliczbowego opisana w źródle \ref{l:sayood}
	
	
1. `_decode(data: bytearray, message_length: int, model: DataModel)` (fragment kodu \ref{lst:_decode})  
	Implementacja algorytmu dekodującego wiadomość wygenerowaną przez `_encode`.

1. `_pack_message(encoded_data: bytearray, message_length, model: DataModel) -> Iterable[int]`  (fragment kodu \ref{lst:_pack_message})  
	Serializuje wiadomość zakodowaną z użyciem `_decode` wraz z modelem i informacją o pliku.
	Zserializowane dane są wystarczające do dekompresji po rozpakowaniu przez  funkcję `_unpack_message`\label{t:pack}
1. `_unpack_message(packed_message: bytearray) -> Tuple[Iterable[int], int, DataModel]` (fragment kodu \ref{lst:_unpack_message})  
	Deserializacja modelu, długości wiadomości oraz wiadomości zserializowanej wcześniej z użyciem `_pack_message` (punkt \ref{t:pack}).

1. `compress_file(path: Path)`  
	Dokonuje kompresji pliku wejściowego, wywołuje funkcje encode i zapisuje plik z rozszerzeniem .artpack

1. `decompress_file(path: Path)`  
	Dokonuje dekompresji pliku .artpack i przywraca go do stanu przed kompresją

## Testy

Program jest pokryty testami automatycznymi, opartymi o narzędzie pytest.

W ramach testów automatycznych przetwarzane są czarno-białe obrazy testowe .pgm. 
W trakcie testów tworzone są tworzone pliki zawierające skompresowany obraz (.artpack) oraz zdekompresowany obraz (arpunpacked). 

Dla każdego obrazu policzone zostały również sumy kontrolne MD5 z użyciem polecenia GNU/Linux `md5sum`. 

# Wyniki i wnioski

Podane obrazy kompresują się. Przykładowo, oryginalna lena.pgm ma 257kb i lena.artpack 239kb, co daje kompresję ok 7%. Plik po dekompresji, lena(arpunpacked).pgm zajmuje 257kb, czyli oryginalną wartość.

Dla plików tekstowych uzyskaliśmy kompresję na poziomie 40%.

Zdekompresowane pliki w większości wypadków mają takie same sumy kontrolne MD5, jak pliki oryginalne, a co za tym idzie - identyczną zawartość.

W niektórych wypadkach sumy nie są identyczne - wynika to z tego, że dla niektórych danych koder dekoduje lub koduje nieprawidłowo ostatnie 1-2 bajty.

Nie udało nam się jeszcze ustalić, dlaczego tak się dzieje, jednak dodaliśmy możliwie proste przypadki pokazujące ten problem do zestawu testów automatycznych (fragment kodu \ref{lst:errtest}).

## Zaistniałe problemy

W obecnej implementacji istnieją przypadki gdy algorytm dekodujący myli się w odczytywaniu wiadomości. 

Udało się ustalić, że pomyłka zachodzi gdy symbol z bardzo małą ilością wystąpień znajduje się pomiędzy symbolami z bardzo dużą ilością wystąpień.  
Dekoder w takim wypadku podczas odczytywania symbolu z małą ilością wystąpień i liczenia liczby wskazującej na przedział w którym został umieszczony symbol, oblicza liczbę, która wskazuje na błędny przedział i odczytuje częściej pojawiający się symbol.

Implementacja algorytmu wydaje się być zgodna z książką i na chwilę obecną nie udało nam znaleźć się przyczyny błędu ani rozwiązania.

# Literatura

1. Khalid Sayood „Kompresja Danych - Wprowadzenie” (<https://acrobat.adobe.com/link/track?uri=urn:aaid:scds:US:f162ad5a-5686-4001-85a5-14fd8dfc90fc>) \label{l:sayood}

# Fragmenty kodu źródłowego

```{.python caption="Klasa BitStream" #lst:BitStream}
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
```

```{.python caption="Funkcja iter_bits" #lst:iter_bits}
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
```


```{.python caption="Funkcja _pack_message" #lst:_pack_message}
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
```


```{.python caption="Funkcja _unpack_message" #lst:_unpack_message}
def _unpack_message(packed_message: bytearray) -> Tuple[Iterable[int], int, DataModel]:
    msg_iter = iter(packed_message)
    assert bytes(islice(msg_iter, 0, 8)) == b"ARTPACK\n"
    message_length_len = next(msg_iter)
    message_length = int.from_bytes(islice(msg_iter, 0, message_length_len), "big")
    model = DataModel.from_serialized(msg_iter)
    m = bytes([next(msg_iter)])
    assert m == b"\n", m
    return msg_iter, message_length, model
```


```{.python caption="Funkcja _decode" #lst:_decode}
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
                print(f"Warning: file ended unexpectedly")
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
```

```{.python caption="Funkcje warunków skalowania" #lst:conditions}
def get_msb_0_condition(l, u, m_value):
    return (l & (1 << m_value - 1)) == 0 and (u & (1 << m_value - 1)) == 0


def get_msb_1_condition(l, u, m_value):
    return (l & (1 << m_value - 1)) > 0 and (u & (1 << m_value - 1)) > 0


def get_e3_condition(l, u, m_value):
    return l & (1 << m_value - 2) > 0 and u & (1 << m_value - 2) == 0
```

```{.python caption="Funkcja _encode" #lst:_encode} 
def _encode(data: Iterable[int], *, model: DataModel = None) -> bytearray:
    if not model:
        model = DataModel(get_byte_count(data))
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
```

```{.python caption="Testy, dla których koder zwraca niepoprawne wartości" #lst:errtest}

def test_failing_case_a():
    """
    test_koda.py:35 (test_failing_case_a)
    bytearray(b'1321331') != b'1321321'
    
    Expected :b'1321321'
    Actual   :bytearray(b'1321331')
    """
    m = DataModel({ord("1"): 43, ord("2"): 1, ord("3"): 9})
    assert (
        bytearray(_decode(_encode(b"1321321", model=m), model=m, message_length=7))
        == b"1321321"
    )


def test_failing_case_b():
    """
    test_koda.py:43 (test_failing_case_b)
    bytearray(b'113') != b'133'

    Expected :b'133'
    Actual   :bytearray(b'113')
    """
    m = DataModel({ord("1"): 44, ord("2"): 1, ord("3"): 531})
    assert (
        bytearray(_decode(_encode(b"133", model=m), model=m, message_length=3))
        == b"133"
    )
```