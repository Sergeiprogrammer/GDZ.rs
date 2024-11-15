from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


# Генерация пары ключей (приватного и публичного)
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Сохранение приватного ключа
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Сохранение публичного ключа
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


# Функция для шифрования
def encrypt_message(public_key_pem, message):
    public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())

    encrypted_message = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_message


# Функция для дешифрования
def decrypt_message(private_key_pem, encrypted_message):
    private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())

    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_message.decode()


# Пример использования
if __name__ == "__main__":
    # Генерация ключей
    private_key, public_key = generate_keys()

    # Сообщение для шифрования
    message = "Это секретное сообщение"

    # Шифрование
    encrypted_message = encrypt_message(public_key, message)
    print("Зашифрованное сообщение:", encrypted_message)

    # Дешифрование
    decrypted_message = decrypt_message(private_key, encrypted_message)
    print("Расшифрованное сообщение:", decrypted_message)
