"""
A program that given a .DMP file will generate reports of what exists for that version.

A .DMP file is the dump of the program memory generated through the windows task manager.
Task manager -> right click program -> Create dump file
"""

import glob
import os
import shutil


def main(path):
    for dump_file_path in glob.glob(os.path.join(path, '**', 'item_id.txt'), recursive=True):
        print(dump_file_path)
        with open(dump_file_path) as f:
            item_ids = f.read().split('\n')
        function_path = os.path.join(os.path.dirname(dump_file_path), 'functions')
        shutil.rmtree(function_path)

        # spawnitem

        spawn_path = os.path.join(function_path, 'spawn')
        os.makedirs(spawn_path, exist_ok=True)
        main_commands = []
        x = 0
        z = 0
        slot = 0
        commands = []
        for item_id in item_ids:
            if item_id:
                commands.append(f"spawnitem {item_id} {x} 131 {z}")

                slot += 1
                if slot == 27:
                    with open(os.path.join(spawn_path, f'chest{x}_{z}.mcfunction'), 'w') as f:
                        f.write('\n'.join(commands))
                    main_commands.append(f'execute @a[scores={{t={(x * 16 + z + 80) // 16}}}] ~ ~ ~ function spawn/chest{x}_{z}')
                    commands.clear()

                    z += 1
                    slot = 0
                    if z == 17:
                        z = 0
                        x += 1

        if commands:
            with open(os.path.join(spawn_path, f'chest{x}_{z}.mcfunction'), 'w') as f:
                f.write('\n'.join(commands))
            main_commands.append(f'execute @a[scores={{t={(x * 16 + z + 80) // 16}}}] ~ ~ ~ function spawn/chest{x}_{z}')
            commands.clear()

        main_commands.append('scoreboard players add @a t 1')

        with open(os.path.join(spawn_path, 'setup.mcfunction'), 'w') as f:
            f.write('\n'.join(
                [
                    'scoreboard objectives add t dummy',
                    'scoreboard players set @a t 0',
                    f'fill -1 128 -1 {x + 1} 140 17 barrier 0 hollow',
                    f'fill 0 128 0 {x} 128 16 chest',
                    f'fill 0 129 0 {x} 129 16 hopper'
                ]
            ))

        with open(os.path.join(spawn_path, 'main.mcfunction'), 'w') as f:
            f.write('\n'.join(main_commands))

        with open(os.path.join(function_path, 'start.mcfunction'), 'w') as f:
            f.write(
                'scoreboard players set @s t 0'
            )


if __name__ == '__main__':
    main('../../PyMCTCompiler/version_compiler')
