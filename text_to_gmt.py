file_name = input("Введите имя файла: ") 
with open(file_name, 'r', encoding='utf-8') as file_in: 
    text = file_in.readlines()

new_text = []
for word in text:
    word = word.rstrip('\n')
    word += '\t'
    new_text.append(word)

new_text = ''.join(new_text)

file_name_out = input("Введите имя файла: ")
with open(file_name_out, 'w', encoding='utf-8') as file_out:
    print(new_text, file=file_out)