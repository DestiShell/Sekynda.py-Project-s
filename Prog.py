import asyncio
import ipaddress
import os
from mcstatus import JavaServer

# Функция для проверки порта
async def check_port(ip, port):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=10
        )
        writer.close()
        await writer.wait_closed()
        return (ip, port, True)
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return (ip, port, False)

# Функция для проверки всех портов на одном IP
async def check_ports(ip, start_port, end_port):
    tasks = [check_port(ip, port) for port in range(start_port, end_port + 1)]
    available_ports = []
    for future in asyncio.as_completed(tasks):
        ip, port, is_open = await future
        if is_open:
            available_ports.append(port)
    return available_ports

# Функция для записи доступных портов в файл ports.txt
async def write_ports(ip, ports):
    with open("ports.txt", "a") as file:
        for port in ports:
            file.write(f"{ip}:{port}\n")

# Функция для проверки группы IP-адресов
async def check_ip_group(ip_addresses, start_port, end_port):
    for ip in ip_addresses:
        print(f"Проверка IP-адреса: {ip}")
        available_ports = await check_ports(ip, start_port, end_port)
        if available_ports:
            print(f"Найдено {len(available_ports)} доступных портов на {ip}")
            await write_ports(ip, available_ports)
        else:
            print(f"Нет доступных портов на {ip}")


# Функция для получения информации о сервере Minecraft
async def check_server(ip_port):
    try:
        print(f"Получение информации о сервере {ip_port}")
        ip, port = ip_port.split(":")
        server = JavaServer.lookup(f"{ip}:{port}")
        status = await server.async_status()
        version = status.version.name
        motd = status.description
        players_online = status.players.online

        # Запись в info.txt
        with open("info.txt", "a", encoding="utf-8") as file:
            file.write(f"{ip_port} - Версия: {version}, MOTD: {motd}, Онлайн: {players_online}\n")
        print(f"Записана информация в info.txt для {ip_port}")

        # Если версия Velocity, записываем в velocity.txt
        if "Velocity" in version:
            with open("velocity.txt", "a", encoding="utf-8") as file:
                file.write(f"{ip_port} - Версия: {version}, MOTD: {motd}, Онлайн: {players_online}\n")
            print(f"Записана информация в velocity.txt для {ip_port}")

    except Exception as e:
        print(f"Ошибка проверки {ip_port}: {str(e)}")

# Функция для проверки и записи информации о MOTD с символом "!" в lonya.txt
def check_lonya_file():
    try:
        with open("velocity.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()

        with open("lonya.txt", "a", encoding="utf-8") as file:
            for line in lines:
                if "!" in line:
                    file.write(line)
                    print(f"Записана информация в lonya.txt: {line.strip()}")
    except Exception as e:
        print(f"Ошибка при проверке файла velocity.txt: {str(e)}")

# Основная функция для проверки всех IP-адресов
async def main():
    ip_range = ('212.80.7.0', '212.80.7.255')  # Задайте диапазон IP-адресов
    start_port = 20000  # Начальный порт
    end_port = 27000  # Конечный порт
    chunk_size = 200  # Размер группы IP-адресов для параллельной проверки

    start_ip = ipaddress.IPv4Address(ip_range[0])
    end_ip = ipaddress.IPv4Address(ip_range[1])

    # Генерация списка IP-адресов
    ip_addresses = [str(ipaddress.IPv4Address(ip_int)) for ip_int in range(int(start_ip), int(end_ip) + 1)]

    # Разбиение IP-адресов на группы для параллельной проверки
    ip_chunks = [ip_addresses[i:i + chunk_size] for i in range(0, len(ip_addresses), chunk_size)]

    # Проверка IP-адресов
    print("Начало проверки IP-адресов...")
    tasks = [check_ip_group(chunk, start_port, end_port) for chunk in ip_chunks]
    await asyncio.gather(*tasks)

    # Получение и запись информации о серверах Minecraft
    print("Начало получения информации о серверах...")
    with open("ports.txt", "r") as file:
        ip_ports = file.read().splitlines()

    tasks = [check_server(ip_port) for ip_port in ip_ports]
    await asyncio.gather(*tasks)

    print("Проверка завершена.")

# Проверка наличия файлов и их создание при необходимости
def check_files():
    for filename in ["ports.txt", "info.txt", "velocity.txt", "lonya.txt"]:
        if not os.path.exists(filename):
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    pass  # просто создаем пустой файл
            except Exception as e:
                print(f"Не удалось создать файл {filename}: {e}")
                return False
    return True

if __name__ == "__main__":
    if check_files():
        asyncio.run(main())