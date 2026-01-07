import curses
import os
import subprocess
import json

current_path = os.path.abspath(".")

class select_menu:
    def __init__(self):
        self.items = os.listdir('recipes')
        self.items.sort(key=lambda x: x[0])
        self.selected_indices = []  
    
    def run(self,str):
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(True)
        
        max_height, max_width = screen.getmaxyx()  
        visible_rows = max_height - 2             
        current_row_idx = 0                         
        scroll_offset = 0                         
        
        while True:
            screen.clear()
            
            screen.addstr(0,0,str)

            top_visible_item = scroll_offset
            bottom_visible_item = min(scroll_offset + visible_rows, len(self.items) + 1)
            
            for idx in range(top_visible_item, bottom_visible_item):
                rel_idx = idx - scroll_offset + 1 
                option = self.items[idx]
                mark = 'X' if idx in self.selected_indices else ' '
                
                try:
                    if idx == current_row_idx:
                        screen.addstr(rel_idx, 0, f"[{mark}] {option}", curses.A_REVERSE)
                    else:
                        screen.addstr(rel_idx, 0, f"[{mark}] {option}")
                except curses.error:
                    pass
            
            key = screen.getch()
            
            if key == ord('q'):
                break
            elif key == curses.KEY_UP:
                if current_row_idx > 0:
                    current_row_idx -= 1
                    if current_row_idx < scroll_offset:
                        scroll_offset -= 1
            elif key == curses.KEY_DOWN:
                if current_row_idx < len(self.items) - 1:
                    current_row_idx += 1
                    if current_row_idx >= scroll_offset + visible_rows:
                        scroll_offset += 1
            elif key == ord(' ') or key == ord('\n'):
                if current_row_idx not in self.selected_indices:
                    self.selected_indices.append(current_row_idx)
                else:
                    self.selected_indices.remove(current_row_idx)
        curses.nocbreak()
        screen.keypad(False)
        curses.echo() 
        curses.endwin()
        return [self.items[i] for i in sorted(self.selected_indices)]

menu = select_menu()
initrd_packages = menu.run("Select initrd packages, press q to end, select minimal stuff which you need (without bootloader and linux)")            
menu.selected_indices = []
main_packages = menu.run("Select os packages, press q to end, choose whatever you want (with linux and bootloader)")

print("\nInitrd packages:", initrd_packages)
print("Main packages:", main_packages)

build_initrd_json = {"repo": "https://github.com/ferris-linux/ferris-linux.git", "packages": initrd_packages}
build_os_json = {"repo": "https://github.com/ferris-linux/ferris-linux.git", "packages": main_packages}

os.system("rm -rf build/build/sysroot && rm -rf build/initramfs.cpio && mkdir -p build ")
os.chdir("build")

os.system("rm -rf ferris-strap")

try:
    subprocess.check_call(["git", "clone", "https://github.com/ferris-linux/ferris-strap.git", "ferris-strap", "--depth=1"])
except subprocess.CalledProcessError:
    print("Git is not installed/corrupted")
    exit(1)

# build ferris-strap

os.chdir("ferris-strap")
os.system("cargo build --release")

os.chdir("..")
os.system("cp -rf ferris-strap/target/release/ferris-strap ./ferris-strap-bin")

with open("initrd_sysroot.json", 'w', encoding='utf-8') as file:
    json.dump(build_initrd_json, file, ensure_ascii=False, indent=4)

with open("os_sysroot.json", 'w', encoding='utf-8') as file:
    json.dump(build_os_json, file, ensure_ascii=False, indent=4)

os.system("rm -rf build/output/repo")
os.system("./ferris-strap-bin initrd_sysroot.json")
os.system("strip --strip-debug build/sysroot/usr/lib/* && strip --strip-unneeded build/sysroot/usr/bin/* && find build/sysroot/usr/lib -name \*.la -delete")
os.system("rm -rf build/sysroot/usr/share/info build/sysroot/usr/share/doc build/sysroot/usr/share/info build/sysroot/usr/share/man")
os.system("rm -rf build/sysroot/usr/lib/*.a")
os.system("cd build/sysroot && find . | cpio -oH newc > ../../initramfs.img")
os.system("rm -rf build/sysroot")
os.system("./ferris-strap-bin os_sysroot.json")
os.system("strip --strip-debug build/sysroot/usr/lib/* && strip --strip-unneeded build/sysroot/usr/bin/* && find build/sysroot/usr/lib -name \*.la -delete")
os.system("rm -rf build/sysroot/usr/share/info build/sysroot/usr/share/doc build/sysroot/usr/share/info build/sysroot/usr/share/man")
os.system("rm -rf os_sysroot && cp -rf build/sysroot os_sysroot")
os.system("cp -rf initramfs.img os_sysroot/boot")