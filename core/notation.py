"""X"""
from enum import Enum
from typing import Any, Tuple, List, Dict
from dataclasses import dataclass
from math import isclose


A4_FREQUENCY = 440  # Note reference: A4 = 440 Hz


class MusicalInterval(Enum):
    OCTAVE = 2 ** (12 / 12)  # 2
    TONE = 2 ** (1 / 6)  # 8 ** (1/24)
    SEMITONE = 2 ** (1 / 12)  # 4 ** (1/24)
    QUARTERTONE = 2 ** (1 / 24)  # 2 ** (1/24)


@dataclass
class Symbol:
    simplified: str
    unicode: str


@dataclass
class Accidental:

    """Accidentals are symbols that pair with a notes to create new notes.
    Three common accidentals are:
    * the sharp: half-step higher,
    * the flat: half-step lower,
    * the natural.
    In Iranian music:
    * the sori: quarter-step higher
    * the koron: quarter-step lower"""

    name: str
    symbol: Symbol
    frequency_ratio: float

    def __str__(self) -> str:
        return self.symbol.simplified


@dataclass
class Octave:
    """An octave (perfect octave, the diapason) is the interval between one musical
    pitch and another with double its frequency"""

    name: str
    number: int

    def __str__(self) -> str:
        return str(self.number)

    def __repr__(self) -> str:
        return f"octave {self.number} {self.name}"

    def _eq_to_name(self, other_name: str) -> bool:
        return self.name == other_name

    def _eq_to_number(self, other_number: int) -> bool:
        return self.number == other_number

    def _eq_to_octave(self, other: "Octave") -> bool:
        return self.name == other.name and self.number == other.number

    def __eq__(self, other: Any) -> bool:
        type_dispatch = {
            str: self._eq_to_name,
            int: self._eq_to_number,
            Octave: self._eq_to_octave,
        }
        other_type = type(other)
        if other_type not in type_dispatch:
            raise NotImplementedError(
                f"Type {other_type} is not supported for comparison"
            )
        return type_dispatch[other_type](other)


class AccidentalSymbol(Enum):
    SHARP = Symbol("#", "\u266F")
    SORI = Symbol("s", "\U0001D1E9")
    NATURAL = Symbol("", "")
    KORON = Symbol("k", "\U0001D1EA")
    FLAT = Symbol("b", "\u266F")


class AccidentalNote(Enum):
    SHARP = Accidental("sharp", AccidentalSymbol.SHARP, MusicalInterval.SEMITONE.value)
    SORI = Accidental("sori", AccidentalSymbol.SORI, MusicalInterval.QUARTERTONE.value)
    NATURAL = Accidental("natural", AccidentalSymbol.NATURAL, 1)
    KORON = Accidental(
        "koron", AccidentalSymbol.KORON, 1 / MusicalInterval.QUARTERTONE.value
    )
    FLAT = Accidental("flat", AccidentalSymbol.FLAT, 1 / MusicalInterval.SEMITONE.value)


class OctaveRegister(Enum):
    SUBSUBCONTRA = Octave("subsubcontra", -1)
    SUBCONTRA = Octave("sub-contra", 0)
    CONTRA = Octave("contra", 1)
    GREAT = Octave("great", 2)
    SMALL = Octave("small", 3)
    ONELINED = Octave("one-lined", 4)
    TWOLINED = Octave("two-lined", 5)
    THREELINED = Octave("three-lined", 6)
    FOURLINED = Octave("four-lined", 7)
    FIVELINED = Octave("five-lined", 8)
    SIXLINED = Octave("six-lined", 9)


@dataclass
class Note:
    name: str
    letter: str
    accidental: str
    octave: int
    frequency: float

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Note {self.name} - {self.frequency} Hz"

    def __post_init__(self):
        letter, accidental, octave = self.decompose_name(self.name)
        assert letter == self.letter
        assert accidental == self.accidental
        assert octave == self.octave

    @staticmethod
    def transposition_by_an_octave(note_name: str) -> str:
        letter, accidental, octave = Note.decompose_name(note_name)
        new_octave = octave + 1
        return f"{letter}{accidental}{new_octave}"

    @staticmethod
    def decompose_name(name: str) -> Tuple[str, str, int]:
        """Return letter, accidental and octave from the name

        It also validates the name correctness thouroughly.
        """
        if not name[-1].isdigit():
            raise ValueError(f"Octave must be an number/int - note:{name}")
        octave = int(name[-1])
        if not -1 <= octave <= 9:
            raise ValueError(f"octave is out of range - note:{name}, octave:{octave}")

        if len(name[:-1]) == 1:
            letter, accidental = name[0].upper(), ""
        elif len(name[:-1]) == 2:
            letter, accidental = name[0].upper(), name[1].lower()
        else:
            raise ValueError(f"name cannot be more that 3 characters - note:{name}")

        if letter not in ["A", "B", "C", "D", "E", "F", "G"]:
            raise ValueError(f"invalid letter - note:{name}, letter:{letter}")
        if accidental not in ["#", "s", "", "k", "b"]:
            raise ValueError(
                f"invalid accidental - note:{name}, accidental:{accidental}"
            )

        return letter, accidental, octave

    @staticmethod
    def from_name(name: str, a4_frequency: float = A4_FREQUENCY) -> "Note":
        """Create and return an object of type Note from the given name"""
        letter, accidental, octave = Note.decompose_name(name)
        frequency = FrequencyComputer.compute_frequency(
            letter, accidental, octave, a4_frequency
        )
        return Note(name, letter, accidental, octave, frequency)

    def _eq_to_name(self, other_name: str) -> bool:
        # TODO: Should convert self and other both to a standard form
        # for instance to make sure E# == F is True
        return self.name == other_name

    def _eq_to_frequency(self, other_frequency: float) -> bool:
        return isclose(self.frequency, other_frequency)

    def _eq_to_note(self, other: "Note") -> bool:
        return self._eq_to_name(other.name) and self._eq_to_frequency(other.frequency)

    def __eq__(self, other: Any) -> bool:
        type_dispatch = {
            str: self._eq_to_name,
            float: self._eq_to_frequency,
            Note: self._eq_to_note,
        }
        other_type = type(other)
        if other_type not in type_dispatch.keys():
            raise NotImplementedError(
                f"Type {other_type} is not supported for comparison"
            )
        return type_dispatch[other_type](other)


class FrequencyComputer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def standard_notes_quartertones() -> List[str]:
        """Return an ordered list of 24 notes in an Octave, equally separated by quartertone

        In this context a set of "standard notes" is defined as the following.
        An equal temperament tuning system, where the octave is divided into 24 equal
        parts (quartertone), results in 24 notes. A set of "standard notes of
        quartertone" is a set that maps bijectively to corresponding frequencies.
        * where "sharp" of a note and "flat" of another are the same note, opt for "sharp"
        * where "koron" of a note and "sori" of another are the same note, opt for "sori"
        * "E#" and "B#" are not considered as they are represented by "F" and "C"
        """
        return [
            "C",
            "Cs",
            "C#",
            "Dk",
            "D",
            "Ds",
            "D#",
            "Ek",
            "E",
            "Es",
            "F",
            "Fs",
            "F#",
            "Gk",
            "G",
            "Gs",
            "G#",
            "Ak",
            "A",
            "As",
            "A#",
            "Bk",
            "B",
            "Bs",
        ]

    @staticmethod
    def conversion_to_standard_note() -> Dict[str, str]:
        """Return a dict for converting identical notes."""
        return {
            "E#": "F",
            "B#": "C",
            "Cb": "B",
            "Fb": "E",
            "Db": "C#",
            "Eb": "D#",
            "Gb": "F#",
            "Ab": "G#",
            "Bb": "A#",
            "Ck": "Bs",
            "Fk": "Es",
        }

    @staticmethod
    def standardize_note(letter: str, accidental: str, octave: int) -> Tuple[str, int]:
        """Return a standard note, given any input note

        Makes sure that the note belong set of "standard notes"
        """
        # Using decompose_name to assur name is valid
        _ = Note.decompose_name(f"{letter}{accidental}{octave}")

        note = f"{letter}{accidental}"
        if note == "B#":
            octave += 1
        note = FrequencyComputer.conversion_to_standard_note().get(note, note)

        if len(note) == 1:
            letter, accidental = note, ""
        if len(note) == 2:
            letter, accidental = note[0], note[1]
        return letter, accidental, octave

    @staticmethod
    def compute_frequency(
        letter: str, accidental: str, octave: int, a4_frequency: float = A4_FREQUENCY
    ) -> float:
        """Calculate the frequency of a note."""
        # pylint: disable=invalid-name
        letter, accidental, octave = FrequencyComputer.standardize_note(
            letter, accidental, octave
        )
        standard_notes = FrequencyComputer.standard_notes_quartertones()
        note_index = standard_notes.index(f"{letter}{accidental}")
        A_index = standard_notes.index("A")
        quartertone_steps_from_A4 = note_index - A_index + (octave - 4) * 24
        return a4_frequency * (2 ** (quartertone_steps_from_A4 / 24))