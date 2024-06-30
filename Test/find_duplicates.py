import os
from PIL import Image, UnidentifiedImageError
import imagehash
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

class DuplicateViewer:
    def __init__(self, duplicates):
        self.duplicates = duplicates
        self.keys = list(duplicates.keys())
        self.index = 0

        self.fig, self.axs = plt.subplots()
        self.fig.subplots_adjust(bottom=0.2)

        self.axprev = plt.axes([0.1, 0.05, 0.1, 0.075])
        self.axnext = plt.axes([0.8, 0.05, 0.1, 0.075])

        self.bnext = Button(self.axnext, 'Next')
        self.bprev = Button(self.axprev, 'Previous')

        self.bnext.on_clicked(self.next)
        self.bprev.on_clicked(self.prev)

        self.update_figure()

    def next(self, event):
        self.index = (self.index + 1) % len(self.keys)
        self.update_figure()

    def prev(self, event):
        self.index = (self.index - 1) % len(self.keys)
        self.update_figure()

    def update_figure(self):
        self.fig.clear()
        self.axprev = plt.axes([0.1, 0.05, 0.1, 0.075])
        self.axnext = plt.axes([0.8, 0.05, 0.1, 0.075])
        self.bnext = Button(self.axnext, 'Next')
        self.bprev = Button(self.axprev, 'Previous')
        self.bnext.on_clicked(self.next)
        self.bprev.on_clicked(self.prev)

        paths = self.duplicates[self.keys[self.index]]
        num_images = len(paths)
        self.axs = self.fig.subplots(1, num_images)

        if num_images == 1:
            self.axs = [self.axs]

        for i, path in enumerate(paths):
            try:
                with Image.open(path) as img:
                    self.axs[i].imshow(img)
                    self.axs[i].set_title(os.path.basename(path))
                    self.axs[i].axis('off')
            except UnidentifiedImageError:
                print(f"Cannot identify image file {path}")
            except FileNotFoundError:
                print(f"File not found: {path}")
            except PermissionError:
                print(f"Permission denied: {path}")
            except Exception as e:
                print(f"Error loading image {path}: {e}")

        self.fig.suptitle(f'Group {self.index + 1}/{len(self.keys)}')
        self.fig.canvas.draw_idle()


def find_duplicates(folder1, folder2=None):
    image_hashes = {}
    duplicates = {}

    def add_image(file_path):
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
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except PermissionError:
            print(f"Permission denied: {file_path}")
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    def process_folder(folder):
        files = [os.path.join(folder, filename) for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename))]
        num_files = len(files)

        if num_files > 1000:
            num_threads = os.cpu_count()
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(add_image, file_path) for file_path in files]
                for future in as_completed(futures):
                    future.result()
        else:
            print(f"Processing {num_files} files without threading.")
            for file_path in files:
                add_image(file_path)

    process_folder(folder1)
    if folder2:
        process_folder(folder2)

    duplicates = {hash_value: paths for hash_value, paths in image_hashes.items() if len(paths) > 1}

    if duplicates:
        for img_hash, paths in duplicates.items():
            print("Найден дубликат:")
            print(f"Хэш - {img_hash}; Файлы - {paths}")

        viewer = DuplicateViewer(duplicates)
        plt.show()

    return duplicates

if __name__ == '__main__':
    folder1 = 'Dublicates'
    find_duplicates(folder1)