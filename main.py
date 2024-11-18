import json
import os
import re
import shutil

from PIL import Image


class Init:
    
    def __init__(self):
        self.input_dir = 'Input'
        self.output_dir = 'Output'
        self.textures_mapping_path = 'textures.json'


    def systemVaildCheck(self) -> bool:
        """
        Windows: True
        Linux: False
        """
        return os.sep == '\\'

    def pathCreateCheck(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)
     
    def transparentCheck(self, img) -> bool:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        for x in range(img.width):
            for y in range(img.height):
                r, g, b, a = img.getpixel((x, y))
                if not a == 0:
                    return False
        return True
    
    def pathInit(self, path: str) -> str:
        path = path.replace(' ','').replace('!','')
        return re.sub(r'§.', '', path)

    def dirInit(self) -> None:
        self.pathCreateCheck(self.output_dir)

        if os.path.exists(self.input_dir):
            if not os.listdir(self.input_dir):
                print("Put your resource pack in input folder to run the program.")
                exit()
        else:
            self.pathCreateCheck(self.input_dir)
            print("Put your resource pack in input folder to run the program.")
            exit()
            
    def mappingInit(self) -> dict:
        with open(self.textures_mapping_path, 'r', encoding='utf-8') as f:
            raw_mapping : dict = json.load(f)
        new_mapping = {}
        for key, value in raw_mapping.items():
            if key.startswith('textures/block/'):
                new_key = key.replace('textures/block/', 'textures/blocks/')
                new_mapping[new_key] = value
            if key.startswith('textures/item/'):
                new_key = key.replace('textures/item/', 'textures/items/')
                new_mapping[new_key] = value

        raw_mapping.update(new_mapping)
        return raw_mapping

    def splitImagePath(self, relative_path, subpath: str ='textures') -> str:
        path_components = relative_path.split(os.sep)
        try:
            index = path_components.index(subpath)
        except ValueError:
            return relative_path
        
        after_subpath = os.path.sep.join(path_components[index + 1:])
        return after_subpath



class ResourceConverter(Init):
    
    def __init__(self):
        super().__init__()
        self.texture_mapping = self.mappingInit()
        if self.systemVaildCheck():
            self.texture_mapping = json.dumps(self.texture_mapping).replace('/', '\\\\')
            self.texture_mapping = json.loads(self.texture_mapping)


    def textures_convert(self) -> None:
        
        for root, _, files in os.walk(self.input_dir):
            for filename in files:
                input_image_path = os.path.join(root, filename)
                
                # Check Image Type
                if not filename.lower().endswith('.png') or not 'textures' in root:
                    continue
                
                # Construct Output Sub Folder
                relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                output_sub_folder = os.path.join(self.output_dir, relative_sub_folder)
                
                # Process Image
                for (base_type, target_type) in self.texture_mapping.items():
                    if base_type in input_image_path:
                        self.textures_process(base_type, target_type, input_image_path, output_sub_folder)

    def textures_process(self, base_type: str, target_type: str, input_image_path: str, output_sub_folder: str) -> None:
        
        # Construct Output Image Path
        output_image_path = os.path.join(output_sub_folder, target_type)
        self.pathCreateCheck(os.path.dirname(output_image_path))
        
        # Save Image
        shutil.copy2(input_image_path, output_image_path)
        print(f"[{base_type.split(os.sep)[0].capitalize()}] Image converted into {output_image_path}")


    def cubemap_convert(self) -> None:
        
        for root, _, files in os.walk(self.input_dir):
            for filename in files:
                
                # Find Image File: Sky Overlay
                if filename in ['cloud1.png', 'cloud2.png', 'cloud3.png', 'starfield03.png']:
                    input_image_path = os.path.join(root, filename)
                    
                    # Construct Output Sub Folder
                    relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                    output_sub_folder = os.path.join(self.output_dir, relative_sub_folder, 'textures')
                    self.pathCreateCheck(output_sub_folder)
                    
                    # Open Original Image
                    with Image.open(input_image_path) as original_image:
                        width, height = original_image.size
                        new_size = max(width, height) // 3
                        
                        positions = [
                            ('cubemap_0', new_size, new_size),  # mid_bottom
                            ('cubemap_1', new_size*2, new_size),  # right_bottom
                            ('cubemap_2', new_size*2, 0),  # right_top
                            ('cubemap_3', 0, new_size),  # left_bottom
                            ('cubemap_4', new_size, 0),  # mid_top
                            ('cubemap_5', 0, 0)  # left_top
                        ]
                        
                        # Crop Image
                        for _, (name, x, y) in enumerate(positions):
                            box = (x, y, x + new_size, y + new_size)
                            cropped_image = original_image.crop(box)
                            
                            # Construct Output Image Path
                            output_image_sub_dir = filename.split('.')[0]
                            output_image_dir = os.path.join(output_sub_folder, 'environment', 'overworld_cubemap', output_image_sub_dir)
                            self.pathCreateCheck(output_image_dir)
                            output_image_path = os.path.join(output_image_dir, f"{name}.png")
                            
                            # Save Image
                            cropped_image.save(output_image_path)
                            print(f"[Sky Cubemap] Image cropped and saved into {output_image_path}")


    def icons_convert(self) -> None:

        for root, _, files in os.walk(self.input_dir):
            for filename in files:
                
                # Find Image File: icons.png 
                if filename == 'icons.png' and 'gui' in root:
                    input_image_path = os.path.join(root, filename)
                    
                    # Construct Output Sub Folder
                    relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                    output_sub_folder = os.path.join(self.output_dir, relative_sub_folder, 'textures')
                    self.pathCreateCheck(output_sub_folder)
                    
                    # Open Original Image
                    with Image.open(input_image_path) as original_image:
                        width, height = original_image.size
                        
                        if width != height or height > 2048:
                            raise Exception(f'Wrong Format in {filename}')
                        
                        rate = width // 256
                        offset_width = 9
                        positions = []
                        
                        # line 0
                        positions.append(('cross_hair', 0, 0, 16, 16))

                        # line 1
                        name_1 = [
                            'heart_background', 'heart_blink', 'heart_?', 'heart_?',
                            'heart', 'heart_half', 'heart_flash', 'heart_flash_half',
                            'poison_heart', 'poison_heart_half', 'poison_heart_flash', 'poison_heart_flash_half',
                            'wither_heart', 'wither_heart_half', 'wither_heart_flash', 'wither_heart_flash_half',
                            'absorption_heart', 'absorption_heart_half'
                        ]
                        
                        for i in range(18):
                            if i in [2, 3]:   # Unknown images
                                continue
                            
                            x = 16 + i * offset_width
                            y = offset_width * 0
                            xn = x + offset_width
                            yn = offset_width * 1
                            name = name_1[i]
                            positions.append((name, x, y, xn, yn))
                        
                        # line 2
                        name_2 = [
                            'armor_empty', 'armor_half', 'armor_full', 'armor_?',
                            'heart_?', 'heart_?', 'heart_?', 'heart_?',
                            'horse_heart', 'horse_heart_half', 'horse_heart_flash', 'horse_heart_flash_half'
                        ]
                        
                        for i in range(12):
                            if i in [3, 4, 5, 6, 7]:   # Unknown images
                                continue
                            
                            x = 16 + i * offset_width
                            y = offset_width * 1
                            xn = x + offset_width
                            yn = offset_width * 2
                            name = name_2[i]
                            positions.append((name, x, y, xn, yn))
                        
                        # line 3
                        name_3 = [
                            'bubble', 'bubble_pop'
                        ]
                        
                        for i in range(2):
                            
                            x = 16 + i * offset_width
                            y = offset_width * 2
                            xn = x + offset_width
                            yn = offset_width * 3
                            name = name_3[i]
                            positions.append((name, x, y, xn, yn))
                        
                        # line 4    
                        name_4 = [
                            'hunger_background', 'hunger_blink', 'hunger_?', 'hunger_?',
                            'hunger_full', 'hunger_half', 'hunger_flash', 'hunger_flash_half',
                            'hunger_effect_full', 'hunger_effect_half', 'hunger_effect_flash', 'hunger_effect_flash_half',
                            'hunger_?', 'hunger_effect_background'
                        ]
                        
                        for i in range(14):
                            if i in [2, 3, 12]:   # Unknown images
                                continue
                            
                            x = 16 + i * offset_width
                            y = offset_width * 3
                            xn = x + offset_width
                            yn = offset_width * 4
                            name = name_4[i]
                            positions.append((name, x, y, xn, yn))
                        
                        # line 5
                        positions.append(('experiencebarempty', 0, 64, 182, 69))
                        positions.append(('experiencebarfull', 0, 69, 182, 74))
                        
                        # Crop Image
                        for _, (name, x, y, xn, yn) in enumerate(positions):
                            box = (x*rate, y*rate, xn*rate, yn*rate)
                            cropped_image = original_image.crop(box)
                            
                            if not self.transparentCheck(cropped_image):
                                
                                # Construct Output Image Path
                                output_image_dir = os.path.join(output_sub_folder, 'ui')
                                self.pathCreateCheck(output_image_dir)
                                output_image_path = os.path.join(output_image_dir, f'{name}.png')
                                
                                # Save Image
                                cropped_image.save(output_image_path)
                                print(f"[Icons] Image cropped and saved into {output_image_path}")
                                continue
                            
                            print(f"[Icons] Wrong transparent image has deleted: {name}")


    def hotbar_convert(self) -> None:
        
        for root, _, files in os.walk(self.input_dir):
            for filename in files:
                if filename in ['gui.png', 'widgets.png']:
                    self.horbat_process('gui.png', root, filename)
                    self.horbat_process('widgets.png', root, filename)

    def horbat_process(self, image_name: str, root: str, filename: str) -> None:
        
        # Find Image File: gui.png 
        if filename == image_name and 'gui' in root:
            input_image_path = os.path.join(root, filename)
            
            # Construct Output Sub Folder
            relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
            output_sub_folder = os.path.join(self.output_dir, relative_sub_folder, 'textures')
            self.pathCreateCheck(output_sub_folder)
            
            # Open Original Image
            with Image.open(input_image_path) as original_image:
                width, height = original_image.size
                
                if width != height or height > 1024:
                    raise Exception(f'Wrong Format in {filename}')
                
                rate = width // 256
                offset_width = 20
                positions = []
                
                # line 0
                name_0 = [
                    'hotbar_start_cap',
                    'hotbar_0', 'hotbar_1', 'hotbar_2',
                    'hotbar_3', 'hotbar_4', 'hotbar_5',
                    'hotbar_6', 'hotbar_7', 'hotbar_8',
                    'hotbar_end_cap'
                ]
                
                for i in range(11):
                    
                    x = 1 + (i-1) * offset_width
                    y = 0
                    xn = x + offset_width
                    yn = 22
                    name = name_0[i]
                    
                    if i in [0, 10]:
                        x = i * 18
                        xn = x + 1
                    
                    positions.append((name, x, y, xn, yn))

                positions.append(('selected_hotbar_slot', 0, 22, 24, 46))
                
                # Crop Image
                for _, (name, x, y, xn, yn) in enumerate(positions):
                    box = (x*rate, y*rate, xn*rate, yn*rate)
                    cropped_image = original_image.crop(box)
                    
                    self.transparentCheck(cropped_image)
                    
                    # Construct Output Image Path
                    output_image_dir = os.path.join(output_sub_folder, 'ui')
                    self.pathCreateCheck(output_image_dir)
                    output_image_path = os.path.join(output_image_dir, f'{name}.png')
                    output_image_name = image_name.split('.')[0].capitalize()
                    
                    # Save Image
                    if not os.path.exists(os.path.abspath(output_image_path)):
                        cropped_image.save(output_image_path)
                        print(f'[{output_image_name}_Hotbar] Image cropped and saved into {output_image_path}')
                    else:
                        print(f'[{output_image_name}_Hotbar] Image existed in {output_image_path}')



if __name__ == '__main__':
    
    init = Init()
    rc = ResourceConverter()
    
    print("Java-Bedrock Resource Pack Converter  Copyright (C) 2024 JiuShang\n")
    init.dirInit()
    
    try:
        rc.textures_convert()  # Common Textures
        rc.icons_convert()  # Gui Icons
        rc.hotbar_convert()  # Hotbars
        rc.cubemap_convert()  # Cubemaps
    
    except Exception as e:
        print(f"[Error] An error occurred in: {e}")
    
    finally:
        print("\nAll files have been processed.")
        print("\nJava-Bedrock Resource Pack Converter  Copyright (C) 2024 JiuShang")
