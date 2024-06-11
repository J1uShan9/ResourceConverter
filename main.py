import json
import os
import re
import shutil
from PIL import Image


class Init:
    
    def __init__(self):
        self.input_dir = 'Input'
        self.output_dir = 'Output'
        self.textures_map = 'textures.json'


    def systemVaildCheck(self) -> bool:
        if os.sep == '\\':
            return True
        elif os.sep == '/':
            return False


    def pathCheck(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)


    def pathInit(self, path: str) -> str:
        path = path.replace(' ','').replace('!','')
        return re.sub(r'§.', '', path)


    def transparentCheck(self, img) -> bool:
        if img.mode == 'RGBA':
            pass
        else:
            img = img.convert('RGBA')

        for x in range(img.width):
            for y in range(img.height):
                r, g, b, a = img.getpixel((x, y))
                if not a == 0:
                    return False
        return True


    def dirInit(self) -> None:
        if os.path.exists(self.output_dir):
            try:
                shutil.rmtree(self.output_dir)
            except OSError as e:
                print(f"[Error] An error occurred while deleting the directory {self.output_dir}: {e.strerror}")
        else:
            os.makedirs(self.output_dir)

        if os.path.exists(self.input_dir):
            if os.listdir(self.input_dir):
                return
            print("Put your resource pack in input folder to run the program.")
            exit()
        else:
            os.makedirs(self.input_dir)
            print("Put your resource pack in input folder to run the program.")
            exit()


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


    def textures_converter(self) -> None:
        
        def _textures_convert_output(textures_tuplelist, base_type, save_type) -> None:

            for _, (je, be) in enumerate(textures_tuplelist):
                
                if not os.path.join('textures', base_type) in root:
                    continue
                
                # Convert Mapped Image Path
                image_name = self.splitImagePath(input_image_path)
                base_image_path = os.path.splitext(image_name)[0].split(os.sep)[1:]
                base_image_name = os.path.join(*base_image_path)
                
                if base_image_name == je:
                    base_image_name = be
                    
                    # Construct Output Image Path
                    output_image_path = os.path.join(output_sub_folder, save_type, f"{base_image_name}.png")
                    output_image_dir = os.path.dirname(output_image_path)
                    self.pathCheck(output_image_dir)
                    
                    # Save Image
                    shutil.copy2(input_image_path, output_image_path)
                    print(f"[{base_type.capitalize()}] Image converted into {output_image_path}")

        # Load Textures Mappings
        with open(self.textures_map, 'r') as f:
            data = json.load(f)
            
            # System Path Check
            if not self.systemVaildCheck():
                data = json.dumps(data).replace('\\', '/').replace('//', '/')
                data = json.loads(data)
            
            # Init Mapping TupleList
            blocks = list(data["blocks"].items())
            items = list(data["items"].items())
            entity = list(data["entity"].items())
            models = list(data["models"].items())
            particle = list(data["particle"].items())
            effect = list(data['effect'].items())

            for root, dirs, files in os.walk(self.input_dir):
                for filename in files:
                    input_image_path = os.path.join(root, filename)
                    
                    # Check Image Type
                    if not filename.lower().endswith('.png') or not 'textures' in root:
                        continue
                    
                    # Construct Output Sub Folder
                    relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                    output_sub_folder = os.path.join(self.output_dir, relative_sub_folder)
                    
                    _textures_convert_output(blocks, 'blocks', 'blocks')
                    _textures_convert_output(items, 'items', 'items')
                    _textures_convert_output(entity, 'entity', 'entity')
                    _textures_convert_output(models, 'models', 'models')
                    _textures_convert_output(particle, 'particle', 'particle')
                    _textures_convert_output(effect, 'mob_effect', 'ui')


    def destroystage_converter(self) -> None:
        
        for root, dirs, files in os.walk(self.input_dir):
            for filename in files:
                input_image_path = os.path.join(root, filename)
                    
                # Check Image Type
                if not filename.lower().endswith('.png'):
                    continue
                if not 'textures' in root:
                    continue
                
                # Find Image File: Destroy Stage 0-9
                for i in range(10):
                    if filename == f'destroy_stage_{i}.png':
                        input_image_path = os.path.join(root, filename)
                        
                        # Construct Output Sub Folder
                        relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                        output_sub_folder = os.path.join(self.output_dir, relative_sub_folder)
                        
                        # Construct Output Image Path
                        output_image_path = os.path.join(output_sub_folder, 'environment', filename)
                        output_image_dir = os.path.dirname(output_image_path)
                        self.pathCheck(output_image_dir)

                        # Save Image
                        shutil.copy2(input_image_path, output_image_path)
                        print(f"[Destroy Stage] Image converted into {output_image_path}")


    def cubemap_converter(self) -> None:
        
        for root, dirs, files in os.walk(self.input_dir):
            for filename in files:
                
                # Find Image File: Sky Overlay
                if filename in ['cloud1.png', 'cloud2.png', 'cloud3.png', 'starfield03.png']:
                    input_image_path = os.path.join(root, filename)
                    
                    # Construct Output Sub Folder
                    relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                    output_sub_folder = os.path.join(self.output_dir, relative_sub_folder)
                    self.pathCheck(output_sub_folder)
                    
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
                            self.pathCheck(output_image_dir)
                            output_image_path = os.path.join(output_image_dir, f"{name}.png")
                            
                            # Save Image
                            cropped_image.save(output_image_path)
                            print(f"[Sky Cubemap] Image cropped and saved into {output_image_path}")


    def icons_converter(self) -> None:
        
        for root, dirs, files in os.walk(self.input_dir):
            for filename in files:
                
                # Find Image File: icons.png 
                if filename == 'icons.png' and 'gui' in root:
                    input_image_path = os.path.join(root, filename)
                    
                    # Construct Output Sub Folder
                    relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                    output_sub_folder = os.path.join(self.output_dir, relative_sub_folder)
                    self.pathCheck(output_sub_folder)
                    
                    # Open Original Image
                    with Image.open(input_image_path) as original_image:
                        width, height = original_image.size
                        
                        if width != height or height > 1024:
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
                                self.pathCheck(output_image_dir)
                                output_image_path = os.path.join(output_image_dir, f'{name}.png')
                                
                                # Save Image
                                cropped_image.save(output_image_path)
                                print(f"[Icons] Image cropped and saved into {output_image_path}")
                                continue
                        
                            print(f"[Icons] Wrong transparent image has deleted: {name}")


    def hotbar_converter(self) -> None:
        
        def _hotbar_convert_output(image_name, root) -> None:
            
            # Find Image File: gui.png 
            if filename == image_name and 'gui' in root:
                input_image_path = os.path.join(root, filename)
                
                # Construct Output Sub Folder
                relative_sub_folder = self.pathInit(os.path.relpath(root, self.input_dir).split(os.sep)[0])
                output_sub_folder = os.path.join(self.output_dir, relative_sub_folder)
                self.pathCheck(output_sub_folder)
                
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
                        self.pathCheck(output_image_dir)
                        output_image_path = os.path.join(output_image_dir, f'{name}.png')
                        output_image_name = image_name.split('.')[0].capitalize()
                        
                        # Save Image
                        if not os.path.exists(os.path.abspath(output_image_path)):
                            cropped_image.save(output_image_path)
                            print(f'[{output_image_name}_Hotbar] Image cropped and saved into {output_image_path}')
                        else:
                            print(f'[{output_image_name}_Hotbar] Image existed in {output_image_path}')

        for root, dirs, files in os.walk(self.input_dir):
            for filename in files:
                
                if filename in ['gui.png', 'widgets.png']:
                    _hotbar_convert_output('gui.png', root)
                    _hotbar_convert_output('widgets.png', root)


if __name__ == '__main__':
    
    init = Init()
    rc = ResourceConverter()
    
    print("Java-Bedrock Resource Pack Converter  Copyright (C) 2024 JiuShang\n")
    init.dirInit()
    
    try:
        rc.textures_converter()  # Common Textures
        rc.destroystage_converter()  # Destroy Stages
        rc.icons_converter()  # Gui Icons
        rc.hotbar_converter()  # Hotbars
        rc.cubemap_converter()  # Cubemaps
        
    except Exception as e:
        print(f"[Error] An error occurred in: {e}")
        
    finally:
        print("\nAll files have been processed.")
        print("\nJava-Bedrock Resource Pack Converter  Copyright (C) 2024 JiuShang")
