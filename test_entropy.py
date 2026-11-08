import os
from app.core.entropy import shannon_entropy, file_entropy

text_data = b"aaaaaaaaaaaaaaaaaaaa"
print("Text entropy:", shannon_entropy(text_data))

random_data = os.urandom(10000)
print("Random entropy:", shannon_entropy(random_data))

with open("sample.txt", "wb") as file:
    file.write(b"Hello, this is a normal text file.")

print("Sample file entropy:", file_entropy("sample.txt"))