#!/bin/sh
set -e

IMAGE_NAME=Ferris-Linux-live

#detected limine
if [ -d "build/os_sysroot/boot/limine" ]; then

	xorriso -as mkisofs -R -r -J -b boot/limine/limine-bios-cd.bin \
			-no-emul-boot -boot-load-size 4 -boot-info-table -hfsplus \
			-apm-block-size 2048 --efi-boot boot/limine/limine-uefi-cd.bin \
			-efi-boot-part --efi-boot-image --protective-msdos-label \
			build/os_sysroot -o $IMAGE_NAME.iso

	if [ ! -d "limine-10.6.1-binary" ]; then
		wget https://github.com/limine-bootloader/limine/archive/refs/tags/v10.6.1-binary.tar.gz
		tar -xf v10.6.1-binary.tar.gz
		cd limine-10.6.1-binary
		make
		rm -rf ../limine-bin
		cp -rf limine ../limine-bin
		cd ..
	fi

	./limine-bin bios-install $IMAGE_NAME.iso

fi

qemu-system-x86_64 -cdrom $IMAGE_NAME.iso -M q35 -m 4G -enable-kvm