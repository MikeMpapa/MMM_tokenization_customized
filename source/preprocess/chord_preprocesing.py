from music21 import chord, key, roman, stream, note

def find_most_frequent_chord_progression(chord_list, chord_limit=5):
    sequence_dict = {}
    chord_list = [chord.split('/')[0] if '/' in chord else chord for chord in chord_list if chord != 'N']

    if len(chord_list) < chord_limit:
        chord_limit = len(chord_list)

    for i in range(chord_limit):
        sequence = ' '.join(chord_list[i:i+chord_limit])
        if sequence in sequence_dict:
            sequence_dict[sequence] += 1
        else:
            sequence_dict[sequence] = 1
    most_frequent_sequence = max(sequence_dict, key=sequence_dict.get)
    return most_frequent_sequence.split()




def standard_to_roman_og(key_signature, chord_progression):
    """
    Converts a chord progression in standard notation to Roman numeral notation.

    Parameters:
        key_signature (str): The key signature (e.g., 'C', 'G', 'Am').
        chord_progression (list): List of chords in standard notation (e.g., ['C', 'G', 'Am', 'F']).

    Returns:
        list: Chord progression in Roman numeral notation.
    """
    # Create a key object
    k = key.Key(key_signature)

    # Create a stream to hold the chord progression
    s = stream.Stream()

    # Add chords to the stream
    for chord_symbol in chord_progression:
        c = chord.Chord(chord_symbol)
        s.append(c)

    # Convert chords to Roman numerals
    roman_chords = [roman.romanNumeralFromChord(c, k).figure for c in s.chordify()]

    return roman_chords


def parse_chord(chord_symbol):
    """
    Parses a chord symbol into a music21 Chord object.

    Parameters:
        chord_symbol (str): The chord symbol (e.g., 'C', 'Gm', 'Em7').

    Returns:
        music21.chord.Chord: The corresponding music21 Chord object.
    """
    note_structure = {}

    #Minor/Major chords
    if chord_symbol[1]=='m':
        chord_symbol = chord_symbol[0].lower() + chord_symbol[2:]
        note_structure['root'] = chord_symbol[0]
    #Flat and sharp chords
    if 'b' == chord_symbol[1]:
        chord_symbol = chord_symbol[0] + '-' + chord_symbol[2:]

    # Flat chords
    if 'b' in chord_symbol:
        chord_symbol = chord_symbol.replace('b', '-')
    # Seventh chords
    if chord_symbol.endswith('7'):
        note_structure.append('P5')
        remaining_chord = chord_symbol[:-1]
        if remaining_chord.endswith('maj'):
            note_structure.append('M7')
            remaining_chord = remaining_chord[:-3]




    if chord_symbol.endswith('dim'):
        root = chord_symbol[:-2]
        # Create a Note object for the root note
        root_note = note.Note(root)
        # Compute the minor third by transposing the root note by 3 half steps
        minor_third = root_note.transpose(3)
        # Compute the diminished fifth by transposing the root note by 6 half steps
        diminished_fifth = root_note.transpose(6)




    if 'maj' in chord_symbol:
        print(chord_symbol)


    #Major 7th chord
    if 'maj' in chord_symbol:
        chord_symbol = chord_symbol.replace('maj', '^maj')

    #Mi



    if chord_symbol.endswith('m7'):
        root = chord_symbol[:-2]
        root_note = note.Note(root)
        minor_third = root_note.transpose('m3')
        perfect_fifth = root_note.transpose('P5')
        minor_seventh = root_note.transpose('m7')
        return chord.Chord([root_note, minor_third, perfect_fifth,minor_seventh])

    # Handle minor chords
    elif chord_symbol.endswith('m'):
        root = chord_symbol[:-1]

        root_note = note.Note(root)
        minor_third = root_note.transpose('m3')
        perfect_fifth = root_note.transpose('P5')

        return chord.Chord([root_note, minor_third, perfect_fifth])

    return chord.Chord(chord_symbol)

def standard_to_roman(key_signature, chord_progression):
    """
    Converts a chord progression in standard notation to Roman numeral notation.

    Parameters:
        key_signature (str): The key signature (e.g., 'C', 'G', 'Am').
        chord_progression (list): List of chords in standard notation (e.g., ['C', 'G', 'Am', 'F']).

    Returns:
        list: Chord progression in Roman numeral notation.
    """
    #convert to nottation acceptable by music21
    if 'm' == key_signature[-1]:
        key_signature = key_signature[:-1].lower()

    # Create a key object
    k = key.Key(key_signature)

    # Create a stream to hold the chord progression
    s = stream.Stream()

    # Add chords to the stream
    for chord_symbol in chord_progression:
        c = parse_chord(chord_symbol)
        s.append(c)

    # Convert chords to Roman numerals
    roman_chords = [roman.romanNumeralFromChord(c, k).figure for c in s.chordify()]

    return  roman_chords
