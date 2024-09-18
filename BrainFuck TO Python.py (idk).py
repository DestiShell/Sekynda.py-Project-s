import os

class BrainfuckError(Exception):
    pass

def check_brainfuck_code(code: str):
    """
    Проверяет код на правильность синтаксиса (сбалансированные скобки)
    """
    stack = []
    for i, char in enumerate(code):
        if char == '[':
            stack.append(i)
        elif char == ']':
            if not stack:
                raise BrainfuckError(f"Неправильный код: лишняя закрывающая скобка на позиции {i}.")
            stack.pop()

    if stack:
        raise BrainfuckError("Неправильный код: не хватает закрывающих скобок.")

def python_to_brainfuck(text: str) -> str:
    bf_code = []
    previous_value = 0

    for char in text:
        ascii_value = ord(char)
        diff = ascii_value - previous_value

        if diff > 0:
            bf_code.append('+' * diff)
        elif diff < 0:
            bf_code.append('-' * abs(diff))

        bf_code.append('.')
        previous_value = ascii_value

    return ''.join(bf_code)

def brainfuck_interpreter(code: str) -> str:
    tape = [0] * 30000
    ptr = 0
    output = ""
    code_ptr = 0
    loop_stack = []

    try:
        check_brainfuck_code(code)  # Проверка кода на корректность

        while code_ptr < len(code):
            command = code[code_ptr]

            if command == '>':
                ptr += 1
            elif command == '<':
                ptr -= 1
            elif command == '+':
                tape[ptr] = (tape[ptr] + 1) % 256
            elif command == '-':
                tape[ptr] = (tape[ptr] - 1) % 256
            elif command == '.':
                output += chr(tape[ptr])
            elif command == ',':
                tape[ptr] = ord(input("Input a character: ")[0])
            elif command == '[':
                if tape[ptr] == 0:
                    open_brackets = 1
                    while open_brackets != 0:
                        code_ptr += 1
                        if code[code_ptr] == '[':
                            open_brackets += 1
                        elif code[code_ptr] == ']':
                            open_brackets -= 1
                else:
                    loop_stack.append(code_ptr)
            elif command == ']':
                if tape[ptr] != 0:
                    code_ptr = loop_stack[-1]
                else:
                    loop_stack.pop()

            code_ptr += 1

    except BrainfuckError as e:
        return f"Ошибка в Brainfuck коде: {e}"

    return output

def brainfuck_to_python(text: str) -> str:
    """
    Преобразует Brainfuck код в Python код (текст).
    """
    return text  # В данном случае не будет преобразования, т.к. реализация требует особых условий

def save_to_file(filename: str, content: str):
    with open(filename, 'w') as file:
        file.write(content)

def read_from_file(filename: str) -> str:
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return file.read()
    else:
        return ""

def execute_python_code_from_file(filename: str):
    python_code = read_from_file(filename)
    if not python_code:
        return "Файл не найден или пуст."

    try:
        # Convert the Python code to Brainfuck
        brainfuck_code = python_to_brainfuck(python_code)
        print("Brainfuck код:")
        print(brainfuck_code)
        save_to_file("brainfuck_code.txt", brainfuck_code)

        # Execute the Brainfuck code
        interpreted_text = brainfuck_interpreter(brainfuck_code)
        print("Результат выполнения Brainfuck кода:")
        print(interpreted_text)

        # Convert the output from Brainfuck back to Python code
        python_code_from_output = brainfuck_to_python(interpreted_text)
        print("Python код из результата Brainfuck:")
        print(python_code_from_output)

        # Save and execute the Python code from the output
        save_to_file("python_code_output.txt", python_code_from_output)

        exec(python_code_from_output)

        return "Код успешно выполнен и сохранён в python_code_output.txt."

    except Exception as e:
        return f"Ошибка выполнения: {e}"

def main():
    filename = "python_code.txt"
    result = execute_python_code_from_file(filename)
    print(result)

if __name__ == "__main__":
    main()
