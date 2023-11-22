############################################################################################################################################
###Deadman's Switch - A Python script to encrypt, compress, and shred files################################################################# 
##and directories at regular intervals using a deadman's switch#############################################################################            
############################################################################################################################################

import os
import logging
import getpass
import subprocess
from pydantic import FilePath
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
try:
    subprocess.check_call(["python", "-m", "pip", "install", "cryptography"])
except ImportError:
    pass
except Exception as e:
    print(f"An error occurred: {e}")

import random
import string
import argparse
import time
def read_key_from_file(key_file_path):
    """
    Read the encryption key from the file.

    Args:
        key_file_path (str): Path to the key file.

    Returns:
        bytes: The encryption key read from the file.
    """
    with open(key_file_path, 'rb') as key_file:
        key = key_file.read()
    return key


def generate_random_key(key_file_path):
    """
    Generate a random encryption key and save it to a file.

    Args:
        key_file_path (str): Path to save the key file.
    """
    key = Fernet.generate_key()
    with open(key_file_path, 'wb') as key_file:
        key_file.write(key)


def generate_key(key_file_path):
    """
    Generate a new encryption key using a password and save it to a file.

    Args:
        key_file_path (str): Path to save the key file.
    """
    salt = os.urandom(16)
    password = getpass.getpass("Enter password: ").encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(password)
    with open(key_file_path, 'wb') as key_file:
        key_file.write(key)


def generate_random_passphrase(passphrase_file_path):
    """
    Generate a random passphrase and save it to a file.

    Args:
        passphrase_file_path (str): Path to save the passphrase file.
    """
    passphrase = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    with open(passphrase_file_path, 'w') as passphrase_file:
        passphrase_file.write(passphrase)


def encrypt_data(file_path, key):
    """
    Encrypt the data in the file using the provided key.

    Args:
        file_path (str): Path to the file to be encrypted.
        key (bytes): The encryption key.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    chunk_size = 64 * 1024
    cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()

    with open(file_path, 'rb') as file:
        with open(file_path + '.enc', 'wb') as encrypted_file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                padded_data = padder.update(chunk) + padder.finalize()
                encrypted_chunk = encryptor.update(padded_data)
                encrypted_file.write(encrypted_chunk)


def decrypt_data(file_path, key):
    """
    Decrypt the data in the file using the provided key.

    Args:
        file_path (str): Path to the file to be decrypted.
        key (bytes): The encryption key.

    Raises:
        FileNotFoundError: If the encrypted file does not exist.
    """
    chunk_size = 64 * 1024
    cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)))
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()

    with open(file_path + '.enc', 'rb') as encrypted_file:
        with open(file_path, 'wb') as decrypted_file:
            while True:
                chunk = encrypted_file.read(chunk_size)
                if not chunk:
                    break
                decrypted_chunk = decryptor.update(chunk)
                unpadded_data = unpadder.update(decrypted_chunk) + unpadder.finalize()
                decrypted_file.write(unpadded_data)


def compress_data(file_path):
    """
    Compress the data in the file using ZIP compression.

    Args:
        file_path (str): Path to the file to be compressed.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    with zipfile.ZipFile(file_path + '.zip', 'w') as zip_file:
        zip_file.write(file_path, os.path.basename(file_path))


def decompress_data(file_path):
    """
    Decompress the data in the file using ZIP decompression.

    Args:
        file_path (str): Path to the file to be decompressed.

    Raises:
        FileNotFoundError: If the compressed file does not exist.
    """
    with zipfile.ZipFile(file_path + '.zip', 'r') as zip_file:
        zip_file.extractall(os.path.dirname(file_path))


def shred_file(file_path):
    """
    Overwrite the file with random data multiple times to securely delete its contents.

    Args:
        file_path (str): Path to the file to be shredded.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    with open(file_path, 'ab') as file:
        file_size = os.path.getsize(file_path)
        for _ in range(3):
            file.seek(0)
            file.write(os.urandom(file_size))


def delete_file(file_path):
    """
    Delete the file from the system.

    Args:
        file_path (str): Path to the file to be deleted.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    os.remove(file_path)


def delete_directory(directory_path):
    """
    Delete the directory and its contents from the system.

    Args:
        directory_path (str): Path to the directory to be deleted.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    shutil.rmtree(directory_path)


def delete_empty_directories(directory_path):
    """
    Delete empty directories recursively.

    Args:
        directory_path (str): Path to the directory to be checked and deleted.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    for root, _, files in os.walk(directory_path, topdown=False):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.remove(file_path)
        os.rmdir(root)


def handle_passphrase(file_path, cipher, key_file_path, passphrase):
    """
    Handle the passphrase.

    Args:
        file_path (str): Path to the file.
        cipher (Fernet): The Fernet cipher object.
        key_file_path (str): Path to the key file.
        passphrase (str): The passphrase.

    Raises:
        FileNotFoundError: If the file or key file does not exist.
    """
    logging.info("Passphrase detected!")
    attempts = 0
    while attempts < 3:
        user_input = getpass.getpass("Enter passphrase: ")
        if user_input == passphrase:
            encrypt_and_shred_self(file_path, cipher)
            shred_file(key_file_path)
            delete_file(key_file_path)
            logging.info("System actions avoided for 48 hours. Thank you Dr. Falken.")
            return
        else:
            attempts += 1
            logging.info("Invalid passphrase. Please try again.")
    current_time = datetime.datetime.now()
    shockandpwn_time = datetime.datetime(2022, 1, 1)  # Replace with the desired shockandPWN time
    time_left = shockandpwn_time - current_time
    logging.info(f"Maximum passphrase attempts reached. Time left until shockandPWN: {time_left}")


def encrypt_and_shred_self(file_path, cipher):
    """
    Encrypt and shred the script itself.

    Args:
        file_path (str): Path to the script file.
        cipher (Fernet): The Fernet cipher object.

    Raises:
        FileNotFoundError: If the script file does not exist.
    """
    encrypt_data(file_path, cipher)
    shred_file(file_path)


def encrypt_and_shred_file(file_path, cipher):
    """
    Encrypt and shred a file.

    Args:
        file_path (str): Path to the file to be encrypted and shredded.
        cipher (Fernet): The Fernet cipher object.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    encrypt_data(file_path, cipher)
    shred_file(file_path)


def encrypt_and_shred_directory(directory_path, cipher):
    """
    Encrypt and shred all files in a directory.

    Args:
        directory_path (str): Path to the directory to be encrypted and shredded.
        cipher (Fernet): The Fernet cipher object.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            encrypt_and_shred_file(file_path, cipher)


def deadmans_switch():
    """
    Main function to handle the deadman's switch.

    This function parses command-line arguments, configures logging, reads the encryption key from a file,
    creates a Fernet cipher object, and performs encryption, compression, and shredding operations based on the
    provided arguments. It also checks for a passphrase at regular intervals and performs actions accordingly.
    """
    # Encryption logic goes here
    pass


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Encrypt, compress, and shred files and directories.')
    parser.add_argument('file_paths', type=str, nargs='+', help='Paths to the files or directories to encrypt, compress, and shred')
    parser.add_argument('key_file_path', type=str, help='Path to the encryption key file')
    parser.add_argument('--decrypt', action='store_true', help='Decrypt the files or directories instead of encrypting, compressing, and shredding')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--interval', type=int, default=24, help='Interval in hours to check for the passphrase (default: 24)')
    parser.add_argument('--passphrase', type=str, default='200OK', help='Passphrase to trigger the actions (default: 200OK)')
    parser.add_argument('--generate-passphrase', action='store_true', help='Generate a random passphrase and save it to a file')
    parser.add_argument('--passphrase-file', type=str, default='passphrase.txt', help='Path to the passphrase file (default: passphrase.txt)')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

    # Read the encryption key from the file
    try:
        encryption_key = read_key_from_file(args.key_file_path)
    except FileNotFoundError:
        logging.error(f"Encryption key file not found: {args.key_file_path}")
        return

    # Create a Fernet cipher object with the key
    def encrypt_compress_and_shred_files_and_directories(file_paths, cipher):
        """
        Encrypt, compress, and shred files and directories.

        Args:
            file_paths (list): List of file paths to encrypt, compress, and shred.
            cipher (Fernet): The Fernet cipher object.
        """
        for file_path in file_paths:
            encrypt_and_shred_file(file_path, cipher)
        encrypt_and_shred_directory(file_paths, cipher)


def decrypt_files_and_directories(file_paths, cipher):
    """
    Decrypt files and directories.

    Args:
        file_paths (list): List of file paths to decrypt.
        cipher (Fernet): The Fernet cipher object.
    """
    for file_path in file_paths:
        decrypt_data(file_path, cipher)
        shred_file(file_path)


def check_passphrase(passphrase, file_paths, key_file_path, cipher):
    """
    Check for a passphrase and perform actions accordingly.

    Args:
        passphrase (str): The passphrase.
        file_paths (list): List of file paths to encrypt, compress, and shred.
        key_file_path (str): Path to the encryption key file.
        cipher (Fernet): The Fernet cipher object.
    """
    user_input = getpass.getpass("Enter passphrase: ")
    if user_input == passphrase:
        encrypt_and_shred_self(file_paths, cipher)
        shred_file(key_file_path)
        delete_file(key_file_path)
        logging.info("System actions avoided for 48 hours. Thank you Dr. Falken.")
        def main():
            """
            Main function to encrypt, compress, and shred files and directories.
            """
            # Parse command-line arguments
            parser = argparse.ArgumentParser(description='Encrypt, compress, and shred files and directories.')
            parser.add_argument('file_paths', type=str, nargs='+', help='Paths to the files or directories to encrypt, compress, and shred')
            parser.add_argument('key_file_path', type=str, help='Path to the encryption key file')
            parser.add_argument('--decrypt', action='store_true', help='Decrypt the files or directories instead of encrypting, compressing, and shredding')
            parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
            parser.add_argument('--interval', type=int, default=24, help='Interval in hours to check for the passphrase (default: 24)')
            parser.add_argument('--passphrase', type=str, default='200OK', help='Passphrase to trigger the actions (default: 200OK)')
            parser.add_argument('--generate-passphrase', action='store_true', help='Generate a random passphrase and save it to a file')
            parser.add_argument('--passphrase-file', type=str, default='passphrase.txt', help='Path to the passphrase file (default: passphrase.txt)')
            args = parser.parse_args()

            # Configure logging
            logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

            # Read the encryption key from the file
            try:
                encryption_key = read_key_from_file(args.key_file_path)
            except FileNotFoundError:
                logging.error(f"Encryption key file not found: {args.key_file_path}")
                return

            # Create a Fernet cipher object with the key
            cipher = Fernet(encryption_key)

            if args.generate_passphrase:
                generate_random_passphrase(args.passphrase_file)
                logging.info(f"Passphrase generated and saved to {args.passphrase_file}")
                return

            if args.decrypt:
                for file_path in args.file_paths:
                    if os.path.isfile(file_path):
                        try:
                            decrypt_data(file_path, cipher)
                            decompress_data(file_path)
                        except FileNotFoundError:
                            logging.error(f"File not found: {file_path}")
                    elif os.path.isdir(file_path):
                        try:
                            encrypt_and_shred_directory(file_path, cipher)
                            delete_empty_directories(file_path)
                        except FileNotFoundError:
                            logging.error(f"Directory not found: {file_path}")
                    else:
                        logging.error(f"Invalid file or directory path: {file_path}")
            else:
                for file_path in args.file_paths:
                    if os.path.isfile(file_path):
                        try:
                            compress_data(file_path + '.zip')
                            encrypt_and_shred_file(file_path + '.zip', cipher)
                            shred_file(file_path + '.zip')
                        except FileNotFoundError:
                            logging.error(f"File not found: {file_path}")
                    elif os.path.isdir(file_path):
                        try:
                            encrypt_and_shred_directory(file_path, cipher)
                            delete_empty_directories(file_path)
                        except FileNotFoundError:
                            logging.error(f"Directory not found: {file_path}")
                    else:
                        logging.error(f"Invalid file or directory path: {file_path}")

            # Check for passphrase at regular intervals
            while True:
                for file_path in args.file_paths:
                    try:
                        handle_passphrase(file_path, cipher, args.key_file_path, args.passphrase)
                    except FileNotFoundError:
                        logging.error(f"File not found: {file_path}")
                logging.info(f"Waiting for {args.interval} hours...")
                time.sleep(args.interval * 3600)


        def generate_random_passphrase(passphrase_file):
            """
            Generate a random passphrase and save it to a file.

            Args:
                passphrase_file (str): Path to the passphrase file.
            """
            # Generate a random passphrase
            passphrase = "random_passphrase"

            # Save the passphrase to the file
            with open(passphrase_file, 'w') as file:
                file.write(passphrase)


        def decrypt_data(file_path, cipher):
            """
            Decrypt data in a file.

            Args:
                file_path (str): Path to the file to be decrypted.
                cipher (Fernet): The Fernet cipher object.
            """
            # Decryption logic goes here
            pass


        def decompress_data(file_path):
            """
            Decompress a file.

            Args:
                file_path (str): Path to the file to be decompressed.
            """
            # Decompression logic goes here
            pass


        def compress_file(file_path):
            """
            Compress a file.

            Args:
                file_path (str): Path to the file to be compressed.
            """
            shutil.make_archive(file_path, 'zip', file_path)


        def encrypt_and_shred_file(file_path, cipher):
            """
            Encrypt, compress, and shred a file.

            Args:
                file_path (str): Path to the file to be encrypted, compressed, and shredded.
                cipher (Fernet): The Fernet cipher object.
            """
            encrypt_data(file_path, cipher)
            compress_file(file_path)
            shred_file(file_path)


        def encrypt_and_shred_directory(directory_path, cipher):
            """
            Encrypt, compress, and shred all files in a directory.

            Args:
                directory_path (str): Path to the directory to be encrypted, compressed, and shredded.
                cipher (Fernet): The Fernet cipher object.
            """
            for root, _, files in os.walk(directory_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    encrypt_and_shred_file(file_path, cipher)


        def delete_empty_directories(directory_path):
            """
            Delete empty directories recursively.

            Args:
                directory_path (str): Path to the directory to delete empty directories from.
            """
            # Delete empty directories recursively
            pass


        def handle_passphrase(file_path, cipher, key_file_path, passphrase):
            """
            Handle the passphrase detection.

            Args:
                file_path (str): Path to the file to check for the passphrase.
                cipher (Fernet): The Fernet cipher object.
                key_file_path (str): Path to the encryption key file.
                passphrase (str): The passphrase to trigger the actions.
            """
            # Handle the passphrase detection logic
            pass


        def read_key_from_file(key_file_path):
            """
            Read the encryption key from a file.

            Args:
                key_file_path (str): Path to the encryption key file.

            Returns:
                bytes: The encryption key.
            """
            # Read the encryption key from the file
            with open(key_file_path, 'rb') as key_file:
                encryption_key = key_file.read()
            return encryption_key


        if __name__ == "__main__":
            main()