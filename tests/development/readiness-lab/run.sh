#!/usr/bin/env bash
# Build and boot a synthetic-only QEMU guest without NICs or host shares.
set -euo pipefail
umask 077
[[ $(id -u) != 0 ]]
assets=$(realpath "${1:?supply directory of reviewed local packages and wheel}")
audit=$(realpath "${2:?supply exact reviewed ws_readiness_audit.py}")
expected=${3:?supply approved audit SHA-256}
[[ $expected =~ ^[a-f0-9]{64}$ ]]
[[ $(sha256sum "$audit" | cut -d' ' -f1) == "$expected" ]]
[[ $(uname -m) == x86_64 ]]
here=$(dirname "$(realpath "$0")")
work=$(mktemp -d /tmp/ccpc-synthetic-guest.XXXXXXXX)
root="$work/root"
mkdir -p "$root"/{bin,dev,proc,sys,run,tmp,etc,lab,usr/lib,usr/bin,lib64}
# Copy only allowlisted runtime binaries and standard library, never a host
# filesystem snapshot, configuration directory, home, or volume.
install -m 0755 /usr/bin/busybox "$root/bin/busybox"
for name in sh dirname basename cat sed grep hostname uname mkdir chmod chown mount ip sleep which rm touch find cut id; do
    ln -s busybox "$root/bin/$name"
done
for glob in mariadb-client-core_ mariadb-server-core_ mariadb-server_ mariadb-common_ libaio1t64_ liburing2_; do
    packages=("$assets"/"$glob"*.deb)
    [[ ${#packages[@]} == 1 && -f ${packages[0]} ]]
    dpkg-deb -x "${packages[0]}" "$root"
done
kernels=("$assets"/linux-image-unsigned-*-generic_*.deb)
[[ ${#kernels[@]} == 1 && -f ${kernels[0]} ]]
dpkg-deb -x "${kernels[0]}" "$work/kernel"
boots=("$work"/kernel/boot/vmlinuz-*)
[[ ${#boots[@]} == 1 && -f ${boots[0]} ]]
python=$(readlink -f "$(command -v python3)")
stdlib=$(python3 -I -B -c 'import sysconfig; print(sysconfig.get_path("stdlib"))')
[[ $python == /usr/bin/python3.* && $stdlib == /usr/lib/python3.* ]]
install -m 0755 "$python" "$root/usr/bin/python3"
install -m 0755 /usr/bin/setpriv "$root/usr/bin/setpriv"
cp -a "$stdlib" "$root/usr/lib/"
copy_links() {
    local executable=$1 lib links
    [[ -f $executable ]]
    links=$(ldd "$executable")
    while IFS= read -r lib; do
        [[ $lib == /lib* || $lib == /usr/lib* ]] || exit 1
        install -D -m 0755 "$lib" "$root$lib"
    done < <(printf '%s\n' "$links" | awk '/=> \/|^[[:space:]]*\// {for(i=1;i<=NF;i++) if($i ~ /^\//) {print $i; break}}')
}
copy_links "$python"
copy_links /usr/bin/setpriv
copy_links "$root/usr/sbin/mariadbd"
copy_links "$root/usr/bin/my_print_defaults"
for so in "$stdlib"/lib-dynload/*.so; do copy_links "$so"; done
# Debian-family packages use both paths depending on usr-merge.
if [[ ! -e "$root/lib" ]]; then ln -s usr/lib "$root/lib"; fi
cp "$here/guest-init.sh" "$root/init"
chmod 0755 "$root/init"
cp "$here/test_mariadb_pr41.py" "$root/lab/"
cp "$audit" "$root/lab/ws_readiness_audit.py"
python3 -I -B -m zipfile -e "$assets/pymysql-1.1.2.whl" "$root/lab"
printf 'root:x:0:0:root:/:/bin/sh\nlab:x:1000:1000:synthetic lab:/tmp:/bin/sh\n' > "$root/etc/passwd"
printf 'root:x:0:\nlab:x:1000:\n' > "$root/etc/group"
printf '127.0.0.1 localhost synthetic-db-lab\n' > "$root/etc/hosts"
printf 'hosts: files\npasswd: files\ngroup: files\n' > "$root/etc/nsswitch.conf"
openssl req -x509 -newkey rsa:2048 -nodes -days 2 -subj /CN=Synthetic-CA \
    -keyout "$work/ca.key" -out "$root/lab/ca.pem" >"$work/openssl.log" 2>&1
openssl req -newkey rsa:2048 -nodes -subj /CN=127.0.0.1 -keyout "$root/lab/server.key" \
    -out "$work/server.csr" >>"$work/openssl.log" 2>&1
printf 'subjectAltName=IP:127.0.0.1\nextendedKeyUsage=serverAuth\n' > "$work/extensions"
openssl x509 -req -in "$work/server.csr" -CA "$root/lab/ca.pem" -CAkey "$work/ca.key" \
    -CAcreateserial -days 2 -extfile "$work/extensions" -out "$root/lab/server.pem" >>"$work/openssl.log" 2>&1
# Guest files are owned by root in initramfs and contain only disposable material.
chmod 0644 "$root/lab/"{server.key,server.pem,ca.pem}
find "$root" -type d -exec chmod a+rx {} +
find "$root" -type f -exec chmod a+r,u-s,g-s {} +
(
    cd "$root"
    find . -print0 | cpio --null -o -H newc --owner=0:0 2>"$work/cpio.log" | gzip -1 > "$work/initramfs.gz"
)
printf 'Disposable lab directory: %s\n' "$work"
env -i PATH=/usr/bin:/bin HOME="$work" timeout 180 qemu-system-x86_64 -nodefaults -machine q35,accel=tcg -m 1024 -smp 2 \
    -display none -serial stdio -monitor none -nic none -no-reboot \
    -kernel "${boots[0]}" -initrd "$work/initramfs.gz" \
    -append 'console=ttyS0 rdinit=/init loglevel=3 panic=1' </dev/null | tee "$work/guest.log"
grep -qx 'CCPC_SYNTHETIC_LAB_PASS' <(tr -d '\r' < "$work/guest.log")
