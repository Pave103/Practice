import os
from PIL import Image, UnidentifiedImageError
import imagehash
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt

def find_duplicates(folder1, folder2=None):
    image_hashes = {}
    duplicates = {}

    def add_images_from_folder(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                try:
                    with Image.open(file_path) as img:
                        img_hash = imagehash.phash(img)
                        color_hash = imagehash.colorhash(img)
                        combined_hash = (img_hash, color_hash)
                        if combined_hash in image_hashes:
                            image_hashes[combined_hash].append(file_path)
                        else:
                            image_hashes[combined_hash] = [file_path]
                except UnidentifiedImageError:
                    print(f"Cannot identify image file {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    # Use ThreadPoolExecutor for concurrent processing
    def process_folder(folder):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(add_images_from_folder, folder)]
            for future in as_completed(futures):
                future.result()

    process_folder(folder1)
    if folder2:
        process_folder(folder2)

    duplicates = {hash_value: paths for hash_value, paths in image_hashes.items() if len(paths) > 1}

    if duplicates:
        for img_hash, paths in duplicates.items():
            print("Найден дубликат:")
            print(f"Хэш - {img_hash}; Файлы - {paths}")

            # Visualize duplicates
            plt.figure(figsize=(10, 5))
            for i, path in enumerate(paths):
                try:
                    with Image.open(path) as img:
                        plt.subplot(1, len(paths), i + 1)
                        plt.imshow(img)
                        plt.title(f'Duplicate {i + 1}')
                        plt.axis('off')
                except UnidentifiedImageError:
                    print(f"Cannot identify image file {path}")
                except Exception as e:
                    print(f"Error loading image {path}: {e}")
            plt.show()

    return duplicates

if __name__ == '__main__':
    folder1 = 'Dublicates'
    find_duplicates(folder1)