import easyocr

# Create an OCR reader object
reader = easyocr.Reader(['en'])

# Read text from an image
result = reader.readtext('D:\pythonPokemmo-Hub\houtai_pokemmo\Func\pic\jyh\data.png')

# Print the extracted text
for detection in result:
    print(detection[1])