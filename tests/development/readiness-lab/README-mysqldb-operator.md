# Native MySQLdb operator compatibility probe

This extends the NIC-free synthetic lab in [README.md](README.md). It runs the exact
operator wrapper connection function and transaction code against MariaDB
11.8.6, using the native mysqlclient package pinned by Frappe at 2.2.7.
The application audit callback is substituted with a fixed parameterized SELECT
probe. No real Frappe tables, live database, Docker daemon or host secrets are used.

For the optional operator-path probe, use the original lab package directory
and a separately prepared synthetic client directory containing a compiled
`MySQLdb/` package for the host system Python ABI and its `libmariadb.so.3`.
Do not copy any host Python virtualenv or system configuration wholesale.

The validated build used CPython 3.14.4, Ubuntu GCC 15 and Ubuntu's MariaDB
client libraries. mysqlclient sdist `mysqlclient-2.2.7.tar.gz` SHA-256 is
`24ae22b59416d5fcce7e99c9d37548350b4565baac82f95e149cac6ce4163845`.
Extract the toolchain, Python headers, MariaDB headers and client library from
trusted public packages into a private temporary directory. With the extracted
toolchain's `usr` directory as `build`, extracted sdist's `src/MySQLdb` as
`source_dir`, and a fresh private `client` directory, the build used:

```bash
cp -a "$source_dir" "$client/MySQLdb"
install -m 0755 "$build/lib/x86_64-linux-gnu/libmariadb.so.3" "$client/libmariadb.so.3"
extension=$(python3 -B -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')
LD_LIBRARY_PATH="$build/lib/x86_64-linux-gnu" \
  "$build/bin/x86_64-linux-gnu-gcc-15" -shared -fPIC -O2 \
  "-I$build/include" "-I$build/include/python3.14" "-I$build/include/mariadb" \
  "-B$build/lib/gcc/x86_64-linux-gnu/15/" \
  '-Dversion_info=(2,2,7,"final",0)' '-D__version__=2.2.7' \
  "$source_dir/_mysql.c" "$client/libmariadb.so.3" -o "$client/MySQLdb/_mysql$extension"
```

Run from the exact reviewed repository checkout, after verifying the source
hashes. Use only previously prepared synthetic lab packages as the first input.

```bash
bash tests/development/readiness-lab/run.sh /private/synthetic-assets \
  scripts/development/operator/ws_readiness_audit.py \
  556a52f95724c34199c8378886909d9f9dbabf25d3b4f35cec6f6d270f4bb927 \
  scripts/development/operator/run_dev_ws_preflight.py \
  53500835d347e34a5edfc35fdb739802ad5a12eff6de36093257a25db6c09494 \
  "$client"
```

Observed PASS in the disposable guest: exact connection arguments and wire flags,
active snapshot and parameterized SELECT, server-side write denial (1792),
wrong identity rejection before application SELECT, plus the existing TLS and
33-table grant probe. Live DEVELOPMENT binding and Frappe runtime behavior were
not tested.
