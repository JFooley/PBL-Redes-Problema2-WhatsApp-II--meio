# Encriptação
def encrypt(text: str, key):
    secretText = ''

    for index, char in enumerate(text):
        secretText = secretText + chr(ord(char) + int(key[index % len(key)]))
    
    return secretText

# Decriptação
def decrypt(secretText: str, key):
    text = ''

    for index, char in enumerate(secretText):
        text = text + chr(ord(char) - int(key[index % len(key)]))
    
    return text