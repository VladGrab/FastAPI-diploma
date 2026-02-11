import os


async def write_file_image_to_disk(path: str, file):
    """
    Функция, записывающая объект изображения в файловое пространство
    """
    if os.path.exists(path) is True:
        count = 0
        temp_path = path
        while True:
            count += 1
            temp_path += f"_{count}"
            if os.path.exists(f"{temp_path}.jpg") is False:
                break
            temp_path = temp_path[:len(temp_path) - (len(str(count)) + 1)]
        path = f"{temp_path}.jpg"
    with open(f"{path}", "wb") as buffer:
        while content := await file.read(1024):
            buffer.write(content)
    return path


def delete_file_from_disk(path: str):
    """
    Удлаение объекта изображения с файлового пространства
    """
    file_path = os.path.join(path)
    if os.path.exists(file_path):
        os.remove(file_path)


def send_error_message(error_type: str, error_message: str):
    """Функция, формирующая требуемый формат вывода информации об ошибке"""
    string_dict = {
        "result": False,
        "error_type": error_type,
        "error_message": error_message
    }
    return str(string_dict)
