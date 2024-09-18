
class TextToMorseConverter:
    def __init__(self):
        self.MORSE_CODE_DIC = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----', ',': '--..--', '.': '.-.-.-', '?': '..--..',
    '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'
}
        self.morse_code=""

    def text_to_morse(self, text):
        all_words=text.split()
        morse_words=[]

        for word in all_words:
            word=word.upper()
            morse_chars=[]

            for character in word:
                if character in self.MORSE_CODE_DIC:
                    morse_chars.append(self.MORSE_CODE_DIC[character])
                else:
                    message=f"Character now allowed: '{character}'. Only allowed characters: a-z, A-Z, 0-9, , . ? / - ( ) and spaces."
                    return message
            morse_word=' '.join(morse_chars)
            morse_words.append(morse_word)

        self.morse_code='   '.join(morse_words)
        return self.morse_code
