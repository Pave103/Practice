import unittest
import tempfile
import shutil
import os
from PIL import Image
from find_duplicates import find_duplicates


class TestFindDuplicates(unittest.TestCase):
    def setUp(self):
        self.test_dir1 = tempfile.mkdtemp()
        self.test_dir2 = tempfile.mkdtemp()

        # Создание тестовых изображений в первой папке
        self.image1_path = os.path.join(self.test_dir1, 'image1.png')
        self.image2_path = os.path.join(self.test_dir1, 'image2.png')
        self.image3_path = os.path.join(self.test_dir1, 'image3.png')

        self.create_image(self.image1_path, (100, 100), (255, 0, 0))
        self.create_image(self.image2_path, (100, 100), (255, 0, 0))
        self.create_image(self.image3_path, (100, 100), (0, 255, 0))

        # Создание тестовых изображений во второй папке
        self.image4_path = os.path.join(self.test_dir2, 'image4.png')
        self.image5_path = os.path.join(self.test_dir2, 'image5.png')

        self.create_image(self.image4_path, (100, 100), (255, 0, 0))  # Дубликат image1
        self.create_image(self.image5_path, (100, 100), (0, 0, 255))

    def create_image(self, path, size, color):
        image = Image.new('RGB', size, color)
        image.save(path)

    def tearDown(self):
        shutil.rmtree(self.test_dir1)
        shutil.rmtree(self.test_dir2)

    def test_find_duplicates_in_single_folder(self):
        duplicates = find_duplicates(self.test_dir1)

        # Проверяем, что дубликаты найдены правильно
        self.assertTrue(
            any(self.image1_path in paths and self.image2_path in paths for paths in duplicates.values())
        )
        self.assertFalse(
            any(self.image3_path in paths for paths in duplicates.values())
        )

    def test_find_duplicates_in_two_folders(self):
        duplicates = find_duplicates(self.test_dir1, self.test_dir2)

        # Проверяем, что дубликаты найдены правильно
        self.assertTrue(
            any(self.image1_path in paths and self.image2_path in paths and self.image4_path in paths for paths in
                duplicates.values())
        )
        self.assertFalse(
            any(self.image3_path in paths for paths in duplicates.values())
        )
        self.assertFalse(
            any(self.image5_path in paths for paths in duplicates.values())
        )


if __name__ == '__main__':
    unittest.main()