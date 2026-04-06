"""
Made by MexrlDev .. To work with Nes-Emu by egycnq

Script is used for : . . : . . : covering bin output from the source original or edited source to this cycle ( .bin → hex string → Lua variable )
"""

import os

# ========== EDIT THIS ==========
BIN_FILE = "name.bin"   # <<< Change this to your .bin filename in bin/ folder you create
# ===============================

def bin_to_hex_string(bin_path):
    """Read binary file, return space-separated uppercase hex bytes."""
    with open(bin_path, 'rb') as f:
        data = f.read()
    return ' '.join(f'{b:02X}' for b in data)

def write_lua_string(output_path, hex_string, var_name='sc'):
    """Write Lua variable assignment to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f'local {var_name} = "{hex_string}"\n')

def get_unique_filename(folder, base_name, extension=".txt"):
    """
    Generate a unique filename in the given folder.
    If base_name + extension exists, add (1), (2), etc.
    Returns full path.
    """
    counter = 1
    out_path = os.path.join(folder, f"{base_name}{extension}")
    while os.path.exists(out_path):
        out_path = os.path.join(folder, f"{base_name} ({counter}){extension}")
        counter += 1
    return out_path

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_folder = os.path.join(script_dir, "bin")
    output_folder = os.path.join(script_dir, "output")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    bin_path = os.path.join(input_folder, BIN_FILE)
    
    if not os.path.isfile(bin_path):
        print(f"Error: File not found: bin/{BIN_FILE}")
        print(f"Make sure '{BIN_FILE}' is inside the 'bin' folder next to this script.")
        return
    
    base_name = os.path.splitext(BIN_FILE)[0]
  
    out_path = get_unique_filename(output_folder, base_name, ".txt")
    
    print(f"Converting: bin/{BIN_FILE} -> {os.path.basename(out_path)}")
    hex_str = bin_to_hex_string(bin_path)
    write_lua_string(out_path, hex_str)
    print(f"  Saved {len(hex_str)//3:,} bytes as hex string ({len(hex_str):,} chars)")
    print("\nDone!")

if __name__ == '__main__':
    main()
