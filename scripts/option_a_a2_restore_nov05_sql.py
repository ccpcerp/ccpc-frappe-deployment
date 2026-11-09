#!/usr/bin/env python3
"""One-use, owner-approved Nov 05 SQL restore ONLY into isolated NEW A2 candidate.

Never rerun on STOP after schema creation. No OLD PROD/DEV, baseline/clone writes,
site files, app backend, worker, scheduler, migration, HTTP or exposed ports.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import subprocess
import sys

PROJECT = 'ccpc_prod_erpnext'
DB = PROJECT + '-db-1'
ROOT = Path('/home/ccpcadmin')
BACKUP = ROOT / '.ccpc-nov05-backup-transfer-20261106'
SECRET = ROOT / '.ccpc-option-a-secrets-20261109'
DB_ID = 'sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4'
APP_ID = 'sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'
REDIS_ID = 'sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763'
ARCHIVES = {
 '20261105_020001-ccpcerp_local-database.sql.gz': '8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87',
 '20261105_020001-ccpcerp_local-files.tar': '200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6',
 '20261105_020001-ccpcerp_local-private-files.tar': '60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf',
 '20261105_020001-ccpcerp_local-site_config_backup.json': 'b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b',
}
OLD = {f'{p}-{svc}-1' for p in ('ccpc_restore_rehearsal_20261107','ccpc_full_acceptance_20261107')
       for svc in ('db','redis-cache','redis-queue')}
NEW = {f'{PROJECT}-{svc}-1' for svc in ('db','redis-cache','redis-queue')}
ALL = OLD | NEW
VOLUMES = {f'{p}_{suffix}' for p in ('ccpc_restore_rehearsal_20261107',
            'ccpc_full_acceptance_20261107',PROJECT)
           for suffix in ('db-data','logs','redis-queue-data','sites')}
NETWORKS = {'bridge','host','none','ccpc_restore_rehearsal_20261107_default',
            'ccpc_full_acceptance_20261107_default',PROJECT+'_default'}
DBCLI = ['sudo','docker','exec',DB,'mariadb',
         '--defaults-extra-file=/run/secrets/db-client.cnf','--batch','--skip-column-names']


def stop(code):
    print('STOP:A2_SQL_'+code, flush=True)
    raise SystemExit(1)


def run(cmd, timeout=30):
    try:
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=timeout)
    except (OSError,subprocess.TimeoutExpired):
        stop('LOCAL_COMMAND_TIMEOUT_OR_MISSING')
    if r.returncode:
        stop('LOCAL_COMMAND_FAILED')
    return r.stdout.decode('utf-8','replace').strip()


def docker(*args):
    return run(['sudo','docker',*args])


def sql(query, schema=None):
    cmd = DBCLI[:]
    if schema:
        cmd.append('--database='+schema)
    return run(cmd+['--execute='+query],timeout=90)


def sha256_file(path):
    h=hashlib.sha256()
    with path.open('rb') as fp:
        while chunk:=fp.read(1024*1024):
            h.update(chunk)
    return h.hexdigest()


def names(args):
    return set(docker(*args).splitlines())


if os.uname().nodename.split('.')[0]!='ccpcerp-prod' or pwd.getpwuid(os.getuid()).pw_name!='ccpcadmin' or os.geteuid()==0:
    stop('WRONG_HOST_OR_USER')
if any(key in os.environ for key in ('DOCKER_HOST','DOCKER_CONTEXT','COMPOSE_FILE',
                                    'COMPOSE_PROJECT_NAME','DB_PASSWORD')):
    stop('AMBIENT_DOCKER_OR_PASSWORD')
if docker('context','show')!='default' or docker('context','inspect','default',
                       '--format','{{.Endpoints.docker.Host}}')!='unix:///var/run/docker.sock':
    stop('DOCKER_CONTEXT')
if names(('ps','-a','--format','{{.Names}}'))!=ALL or names(('volume','ls','--format','{{.Name}}'))!=VOLUMES or names(('network','ls','--format','{{.Name}}'))!=NETWORKS:
    stop('RESOURCE_INVENTORY')
for name in ALL:
    if docker('inspect','--format','{{.State.Running}}',name)!='true':
        stop('EXPECTED_SERVICE_STOPPED')
for image,digest in (('ccpcerp:v16.50.0',APP_ID),('mariadb:11.8',DB_ID),
                     ('redis:8.6-alpine',REDIS_ID)):
    if docker('image','inspect','--format','{{.Id}}',image)!=digest:
        stop('IMAGE_ID')
for name in NEW:
    obj=json.loads(docker('inspect',name))[0]
    if obj.get('HostConfig',{}).get('PortBindings') or set(obj.get('NetworkSettings',{}).get('Networks',{}))!={PROJECT+'_default'}:
        stop('UNSAFE_NETWORK_OR_PORTS')
    if obj.get('Image')!=(DB_ID if name==DB else REDIS_ID):
        stop('CANDIDATE_IMAGE')
network=json.loads(docker('network','inspect',PROJECT+'_default'))[0]
if network.get('Internal') is not True or network.get('Driver')!='bridge' or network.get('Labels',{}).get('com.docker.compose.project')!=PROJECT:
    stop('NETWORK_NOT_INTERNAL')
if set(network.get('Containers',{}))!={json.loads(docker('inspect',name))[0]['Id'] for name in NEW}:
    stop('NETWORK_MEMBERS')
for suffix in ('db-data','logs','redis-queue-data','sites'):
    vol=json.loads(docker('volume','inspect',PROJECT+'_'+suffix))[0]
    if vol.get('Labels',{}).get('com.docker.compose.project')!=PROJECT:
        stop('VOLUME_OWNERSHIP')
if not SECRET.is_dir() or SECRET.is_symlink() or SECRET.stat().st_mode&0o777!=0o700:
    stop('CANDIDATE_SECRET_DIR')
for name in ('db-client.cnf','mariadb-root-password'):
    p=SECRET/name
    if not p.is_file() or p.is_symlink() or p.stat().st_mode&0o777!=0o600:
        stop('CANDIDATE_SECRET_FILE')
if not BACKUP.is_dir() or BACKUP.is_symlink():
    stop('ARCHIVE_DIRECTORY')
for name,digest in ARCHIVES.items():
    p=BACKUP/name
    if not p.is_file() or p.is_symlink() or sha256_file(p)!=digest:
        stop('APPROVED_NOV05_SHA256')
try:
    historical=json.loads((BACKUP/'20261105_020001-ccpcerp_local-site_config_backup.json').read_text())
except (OSError,ValueError,UnicodeDecodeError):
    stop('BACKUP_CONFIG_JSON')
schema=historical.get('db_name')
if not isinstance(schema,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,63}',schema) or schema.lower() in ('mysql','sys','test','information_schema','performance_schema'):
    stop('SCHEMA_NAME')
if not historical.get('encryption_key') or not historical.get('db_password'):
    stop('BACKUP_KEY_OR_PASSWORD_MISSING')
del historical
if sql('SELECT 1')!='1':
    stop('ROOT_AUTH')
if set(sql('SHOW DATABASES').splitlines())!={'information_schema','mysql','performance_schema','sys'}:
    stop('CANDIDATE_DATABASE_NOT_EMPTY')
if docker('inspect','--format','{{.State.Health.Status}}',DB)!='healthy':
    stop('DB_HEALTH')
sql_archive=BACKUP/'20261105_020001-ccpcerp_local-database.sql.gz'
try:
    total=0
    with gzip.open(sql_archive,'rb') as fp:
        while chunk:=fp.read(1024*1024):
            total+=len(chunk)
            if total>512*1024*1024:
                stop('DECOMPRESSED_SQL_TOO_LARGE')
    if not total:
        stop('EMPTY_SQL')
except (OSError,EOFError,gzip.BadGzipFile):
    stop('GZIP_INVALID')
print('A2_SQL_PREFLIGHT_PROTECTED_CONTAINERS_ARCHIVE_AND_EMPTY_DB_PASS',flush=True)

# First write: never drop, retry or clean up after a partial import.
sql('CREATE DATABASE '+chr(96)+schema+chr(96)+' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
print('A2_SQL_CANDIDATE_SCHEMA_CREATED',flush=True)
try:
    with gzip.open(sql_archive,'rb') as fp:
        child=subprocess.Popen(['sudo','docker','exec','-i',DB,'mariadb',
                                '--defaults-extra-file=/run/secrets/db-client.cnf',
                                '--database='+schema],
                               stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        try:
            while chunk:=fp.read(1024*1024):
                child.stdin.write(chunk)
            child.stdin.close()
            rc=child.wait(timeout=180)
        except (OSError,BrokenPipeError,subprocess.TimeoutExpired):
            child.kill()
            child.wait()
            stop('PARTIAL_IMPORT_KEEP_DATABASE')
        if rc:
            stop('PARTIAL_IMPORT_CLIENT_ERROR')
except (OSError,EOFError,gzip.BadGzipFile):
    stop('PARTIAL_IMPORT_STREAM_ERROR')
print('A2_SQL_IMPORT_CLIENT_EXIT_ZERO',flush=True)

for key,query,expected in (
 ('BASE_TABLES',"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND TABLE_TYPE='BASE TABLE'",741),
 ('SEQUENCES',"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND TABLE_TYPE='SEQUENCE'",6),
 ('VIEWS',"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND TABLE_TYPE='VIEW'",0),
 ('COMPANIES',"SELECT COUNT(*) FROM tabCompany",4),
 ('DOCTYPES',"SELECT COUNT(*) FROM tabDocType",814),
 ('USERS',"SELECT COUNT(*) FROM tabUser",7),
 ('SINGLES',"SELECT COUNT(*) FROM tabSingles",1000),
):
    try:
        count=int(sql(query,schema))
    except ValueError:
        stop('COUNT_INVALID_'+key)
    if count!=expected:
        stop('COUNT_MISMATCH_'+key)
print('A2_SQL_RESTORED_741_TABLES_6_SEQUENCES_4_COMPANIES_PASS',flush=True)
print('A2_SQL_RESTORED_814_DOCTYPES_7_USERS_1000_SINGLES_PASS',flush=True)
if names(('ps','-a','--format','{{.Names}}'))!=ALL or names(('volume','ls','--format','{{.Name}}'))!=VOLUMES or names(('network','ls','--format','{{.Name}}'))!=NETWORKS:
    stop('AFTER_RESOURCE_INVENTORY')
for name in OLD:
    if docker('inspect','--format','{{.State.Running}}',name)!='true':
        stop('AFTER_REHEARSAL_SERVICE')
print('A2_SQL_SIX_REHEARSAL_SERVICES_PRESERVED',flush=True)
print('A2_SQL_NO_APP_FILES_MIGRATION_OR_WORKERS_STARTED',flush=True)
print('A2_SQL_NOV05_CANDIDATE_RESTORE_COMPLETE',flush=True)
