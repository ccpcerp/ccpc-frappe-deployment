#!/usr/bin/env python3
"""Stage A2, NEW ONLY, one-use continuation of Nov09 partial candidate site write.

Only ccpc_prod_erpnext; DO NOT run twice or after STOP. No app/worker starts,
migrations, OLD PROD/DEV changes, employee ports or networking beyond an
ephemeral no-network writer to the candidate-only sites volume.
"""
import base64
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import subprocess
import sys
import tarfile

PROJECT = 'ccpc_prod_erpnext'
DB = PROJECT + '-db-1'
SITE = 'ccpcerp.local'
APP_IMAGE = 'sha256:4580454f7c43dd7c97b41f2fa1ac59b468e7d07759217a2e38e7ee711ee651d8'
DB_IMAGE = 'sha256:efb4959ef2c835cd735dbc388eb9ad6aab0c78dd64febcd51bc17481111890c4'
REDIS_IMAGE = 'sha256:2cc044fc5a07c9b701f8f1255a309ae9ad7856e694ac03513bf3648c01e40763'
HOME = Path('/home/ccpcadmin')
BACKUP = HOME / '.ccpc-nov05-backup-transfer-20261106'
SECRET_DIR = HOME / '.ccpc-option-a-secrets-20261109'
SQLFILE = '20261105_020001-ccpcerp_local-database.sql.gz'
PUBFILE = '20261105_020001-ccpcerp_local-files.tar'
PRIVFILE = '20261105_020001-ccpcerp_local-private-files.tar'
CONFFILE = '20261105_020001-ccpcerp_local-site_config_backup.json'
HASHES = {
 SQLFILE: '8fb7a6fab1c5eade05515ad75372c9901dc9e2d8fdbc272655a3a97ab176db87',
 PUBFILE: '200764d74f208c9bc7d3d89fd20b713147e96b3a5bdc4d24c051db7af14ac0e6',
 PRIVFILE: '60768b87cc3e585ff4179f03b23dae87d065c5e1d076b39d8a33f2e2f1285daf',
 CONFFILE: 'b3ec5b32272476e01d6f29e6e69b5533aeb94e6b7d4dde591150018149742e1b',
}
OLD = {f'{p}-{s}-1' for p in ('ccpc_restore_rehearsal_20261107','ccpc_full_acceptance_20261107') for s in ('db','redis-cache','redis-queue')}
NEW = {f'{PROJECT}-{s}-1' for s in ('db','redis-cache','redis-queue')}
VOLUMES = {f'{p}_{v}' for p in ('ccpc_restore_rehearsal_20261107','ccpc_full_acceptance_20261107',PROJECT) for v in ('db-data','logs','redis-queue-data','sites')}
NETWORKS = {'bridge','host','none','ccpc_restore_rehearsal_20261107_default','ccpc_full_acceptance_20261107_default',PROJECT+'_default'}
DBCLI=['sudo','docker','exec','-i',DB,'mariadb','--defaults-extra-file=/run/secrets/db-client.cnf','--batch','--skip-column-names']


def stop(name):
    print('STOP:A2_SITE_'+name, flush=True)
    raise SystemExit(1)


def proc(cmd, data=None, timeout=45):
    try:
        return subprocess.run(cmd,input=data,stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,timeout=timeout,check=False)
    except (OSError, subprocess.TimeoutExpired):
        stop('COMMAND_TIMEOUT_OR_UNAVAILABLE')


def execute(cmd, data=None, timeout=45):
    r=proc(cmd,data,timeout)
    if r.returncode:
        stop('COMMAND_FAILED_RETAIN_STATE')
    return r.stdout.decode('utf8','replace').strip()


def docker(*args):
    return execute(['sudo','docker',*args])


def sql(query):
    return execute(DBCLI, query.encode('utf8'), timeout=45)


def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while block:=f.read(1024*1024):
            h.update(block)
    return h.hexdigest()


def inspect(kind,name):
    try:
        return json.loads(docker(kind,'inspect',name))[0]
    except (ValueError,IndexError,KeyError):
        stop('INSPECT_PARSE')


def inventory(kind):
    return set(docker(*kind).splitlines())


if os.uname().nodename.split('.')[0]!='ccpcerp-prod' or pwd.getpwuid(os.getuid()).pw_name!='ccpcadmin' or os.geteuid()==0:
    stop('WRONG_HOST_OR_USER')
if any(key in os.environ for key in ('DOCKER_HOST','DOCKER_CONTEXT','COMPOSE_FILE','COMPOSE_PROJECT_NAME','DB_PASSWORD')):
    stop('AMBIENT_OVERRIDE')
if docker('context','show')!='default' or docker('context','inspect','default','--format','{{.Endpoints.docker.Host}}')!='unix:///var/run/docker.sock':
    stop('DOCKER_TARGET')
if inventory(('ps','-a','--format','{{.Names}}'))!=OLD|NEW or inventory(('volume','ls','--format','{{.Name}}'))!=VOLUMES or inventory(('network','ls','--format','{{.Name}}'))!=NETWORKS:
    stop('HOST_INVENTORY_CHANGED')
for name in OLD|NEW:
    if docker('inspect','--format','{{.State.Running}}',name)!='true':
        stop('SUPPORT_SERVICE_STOPPED')
for tag,digest in (('ccpcerp:v16.50.0',APP_IMAGE),('mariadb:11.8',DB_IMAGE),('redis:8.6-alpine',REDIS_IMAGE)):
    if docker('image','inspect','--format','{{.Id}}',tag)!=digest:
        stop('IMAGE_HASH')
for name in NEW:
    obj=inspect('container',name)
    if obj.get('HostConfig',{}).get('PortBindings') or set(obj.get('NetworkSettings',{}).get('Networks',{}))!={PROJECT+'_default'}:
        stop('UNEXPECTED_PORT_OR_NETWORK')
    if obj.get('Image')!=(DB_IMAGE if name==DB else REDIS_IMAGE):
        stop('SERVICE_IMAGE')
network=inspect('network',PROJECT+'_default')
if network.get('Internal') is not True or network.get('Driver')!='bridge' or network.get('Labels',{}).get('com.docker.compose.project')!=PROJECT:
    stop('NETWORK_BOUNDARY')
if set(network.get('Containers',{}))!={inspect('container',n)['Id'] for n in NEW}:
    stop('NETWORK_MEMBERS')
try:
    subnets=network['IPAM']['Config']
    if len(subnets)!=1:
        stop('SUBNET_COUNT')
    subnet=ipaddress.ip_network(subnets[0]['Subnet'],strict=True)
except (KeyError,ValueError,TypeError):
    stop('SUBNET_PARSE')
if not isinstance(subnet,ipaddress.IPv4Network) or not any(subnet.subnet_of(s) for s in
    (ipaddress.ip_network('10.0.0.0/8'),ipaddress.ip_network('172.16.0.0/12'),ipaddress.ip_network('192.168.0.0/16'))):
    stop('SUBNET_NOT_PRIVATE')
hostmask=str(subnet.network_address)+'/'+str(subnet.netmask)

sitesvol=inspect('volume',PROJECT+'_sites')
if sitesvol.get('Labels',{}).get('com.docker.compose.project')!=PROJECT or sitesvol.get('Labels',{}).get('com.ccpc.stage')!='option-a-a2':
    stop('SITES_VOLUME_OWNER')
mountpoint=sitesvol.get('Mountpoint','')
if mountpoint != '/var/lib/docker/volumes/ccpc_prod_erpnext_sites/_data':
    stop('SITES_MOUNTPOINT')
# Root-only, read-only check of the exact partial state established by the
# 2026-11-09 diagnostic. No file content or attachment name is printed.
readcheck=r"""
import json,pathlib,stat,sys
root=pathlib.Path(sys.argv[1])
def check(path,kind,uid,mode):
 s=path.lstat()
 typ=stat.S_ISDIR if kind=='dir' else stat.S_ISREG
 assert typ(s.st_mode) and s.st_uid==uid and stat.S_IMODE(s.st_mode)==mode
assert root.is_dir() and not root.is_symlink()
check(root/'common_site_config.json','file',1000,0o600)
check(root/'apps.txt','file',1000,0o644)
site=root/'ccpcerp.local'
check(site,'dir',1000,0o755)
assert {p.name for p in root.iterdir()}=={'common_site_config.json','apps.txt','ccpcerp.local'}
assert not list(site.iterdir())
assert (root/'apps.txt').read_bytes()==b'frappe\nerpnext\nccpcerp\n'
common=json.loads((root/'common_site_config.json').read_bytes())
expected={
 'db_host':'db','db_port':3306,
 'redis_cache':'redis://redis-cache:6379',
 'redis_queue':'redis://redis-queue:6379',
 'redis_socketio':'redis://redis-queue:6379',
 'socketio_port':9000,'maintenance_mode':0,'pause_scheduler':1,
 'disable_scheduler':1,'mute_emails':1,'developer_mode':0,
}
assert common==expected
print('EXACT_PARTIAL_SITE_STATE_PASS')
"""
if execute(['sudo','python3','-c',readcheck,mountpoint])!='EXACT_PARTIAL_SITE_STATE_PASS':
    stop('PARTIAL_SITE_STATE_CHANGED')
if not SECRET_DIR.is_dir() or SECRET_DIR.is_symlink() or SECRET_DIR.stat().st_mode&0o777!=0o700:
    stop('SECRET_DIRECTORY')
secret_file=SECRET_DIR/'site-db.env'
if not secret_file.is_file() or secret_file.is_symlink() or secret_file.stat().st_mode&0o777!=0o600 or secret_file.stat().st_uid!=os.getuid():
    stop('EXPECTED_PARTIAL_SECRET_MISSING')
try:
    secret_data=secret_file.read_text(encoding='ascii')
except (OSError,UnicodeDecodeError):
    stop('PARTIAL_SECRET_READ')
if not re.fullmatch(r'DB_PASSWORD=[0-9a-f]{64}\n',secret_data):
    stop('PARTIAL_SECRET_FORMAT')
password=secret_data[len('DB_PASSWORD='):-1]
del secret_data
for name in ('mariadb-root-password','db-client.cnf'):
    f=SECRET_DIR/name
    if not f.is_file() or f.is_symlink() or f.stat().st_mode&0o777!=0o600:
        stop('ROOT_SECRET_MISSING')
if not BACKUP.is_dir() or BACKUP.is_symlink():
    stop('ARCHIVE_DIRECTORY')
for name,digest in HASHES.items():
    f=BACKUP/name
    if not f.is_file() or f.is_symlink() or sha256(f)!=digest:
        stop('ARCHIVE_DIGEST')
try:
    oldconfig=json.loads((BACKUP/CONFFILE).read_text())
except (ValueError,OSError,UnicodeDecodeError):
    stop('HISTORICAL_CONFIG')
schema=oldconfig.get('db_name')
encryption_key=oldconfig.get('encryption_key')
if not isinstance(schema,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,63}',schema):
    stop('SCHEMA_NAME')
if not isinstance(encryption_key,str) or len(encryption_key)<20:
    stop('HISTORICAL_ENCRYPTION_KEY')
if not isinstance(oldconfig.get('db_password'),str) or not oldconfig['db_password']:
    stop('HISTORICAL_PASSWORD')
del oldconfig

if sql('SELECT 1;')!='1' or docker('inspect','--format','{{.State.Health.Status}}',DB)!='healthy':
    stop('DB_ROOT_AUTH_OR_HEALTH')
if sql('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE();') != '0':
    # Statement without explicit DB selects no schema, so use a schema-scoped check below too.
    stop('SQL_CONTEXT_UNEXPECTED')
def qcount(query):
    try:
        return int(sql(query+';'))
    except ValueError:
        stop('COUNT_PARSE')

if qcount("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='"+schema+"' AND TABLE_TYPE='BASE TABLE'")!=741:
    stop('SCHEMA_TABLE_COUNT')
if qcount("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='"+schema+"' AND TABLE_TYPE='SEQUENCE'")!=6:
    stop('SCHEMA_SEQUENCES')
if qcount('SELECT COUNT(*) FROM '+chr(96)+schema+chr(96)+'.'+chr(96)+'tabCompany'+chr(96))!=4:
    stop('COMPANY_COUNT')
if qcount("SELECT COUNT(*) FROM mysql.global_priv WHERE User='"+schema+"'")!=1:
    stop('EXPECTED_EXISTING_APP_USER')

# Inspect but NEVER automatically extract arbitrary tar members. Exactly one
# direct private attachment and no public files were verified in the earlier
# successful independent Nov05 full-acceptance rehearsal.
def members(archive, section):
    output=[]
    try:
        with tarfile.open(BACKUP/archive,'r:') as tf:
            for member in tf.getmembers():
                parts=PurePosixPath(member.name).parts
                if parts and parts[0]=='.':
                    parts=parts[1:]
                if not parts:
                    if not member.isdir(): stop('TAR_ROOT_TYPE')
                    continue
                if parts[0]!=SITE or len(parts)>4:
                    stop('TAR_UNEXPECTED_PATH')
                if any(x in ('.','..','') or '\\' in x or any(ord(c)<32 for c in x) for x in parts):
                    stop('TAR_PATH_UNSAFE')
                if len(parts)==1:
                    if not member.isdir(): stop('TAR_SITE_TYPE')
                    continue
                if parts[1]!=section:
                    stop('TAR_SECTION_MISMATCH')
                if len(parts)<=3:
                    if len(parts)==3 and parts[2]!='files':
                        stop('TAR_WRONG_DIR')
                    if not member.isdir(): stop('TAR_DIR_TYPE')
                    continue
                if parts[2]!='files' or section!='private' or not member.isfile() or not member.isreg() or member.size>4*1024*1024:
                    stop('TAR_UNEXPECTED_FILE_TYPE')
                f=tf.extractfile(member)
                if f is None: stop('TAR_CONTENT')
                blob=f.read(4*1024*1024+1)
                if len(blob)!=member.size or len(blob)>4*1024*1024:
                    stop('TAR_FILE_SIZE')
                output.append((parts[3],base64.b64encode(blob).decode('ascii')))
    except (OSError,tarfile.TarError,EOFError):
        stop('TAR_INVALID')
    return output

if members(PUBFILE,'public'):
    stop('UNEXPECTED_PUBLIC_FILES')
priv=members(PRIVFILE,'private')
if len(priv)!=1:
    stop('EXPECTED_SINGLE_PRIVATE_ATTACHMENT')
print('A2_PARTIAL_PREFLIGHT_DB_NETWORK_BACKUP_AND_ARCHIVES_PASS',flush=True)

# The Nov09 A2 run already created the candidate DB password and account.
# Reuse the exact private secret without creating or altering any SQL user.
print('A2_PARTIAL_CANDIDATE_SECRET_AND_DB_ACCOUNT_REUSED',flush=True)
account="'"+schema+"'@'"+hostmask+"'"
if qcount("SELECT COUNT(*) FROM mysql.global_priv WHERE User='"+schema+"' AND Host='"+hostmask+"'")!=1:
    stop('EXPECTED_APP_USER_HOST_NOT_FOUND')
grants=sql('SHOW GRANTS FOR '+account+';')
grant_lines=grants.splitlines()
if len(grant_lines)!=2 or not any('ON *.*' in s and s.startswith('GRANT USAGE') for s in grant_lines) or not any(
    'ON '+chr(96)+schema+chr(96)+'.*' in s and s.startswith('GRANT ALL PRIVILEGES')
    for s in grant_lines) or any('GRANT OPTION' in s for s in grant_lines):
    stop('PARTIAL_ACCOUNT_GRANTS')
if qcount("SELECT COUNT(*) FROM mysql.global_priv WHERE User='"+schema+"'")!=1:
    stop('ACCOUNT_COUNT')
print('A2_PARTIAL_SCHEMA_SCOPED_APP_ACCOUNT_RECONFIRMED_PASS',flush=True)

site_config={
 'db_name':schema,'db_password':password,'encryption_key':encryption_key,
 'db_host':'db','db_port':3306,
 'maintenance_mode':0,'pause_scheduler':1,'disable_scheduler':1,
 'mute_emails':1,'developer_mode':0,
}
common={
 'db_host':'db','db_port':3306,
 'redis_cache':'redis://redis-cache:6379',
 'redis_queue':'redis://redis-queue:6379',
 'redis_socketio':'redis://redis-queue:6379',
 'socketio_port':9000,
 'maintenance_mode':0,'pause_scheduler':1,'disable_scheduler':1,
 'mute_emails':1,'developer_mode':0,
}
payload=json.dumps({'site':site_config,'common':common,'private':priv},
                   separators=(',',':')).encode('utf8')
del password, encryption_key, site_config, common

# Root inside an ephemeral --network=none container writes ONLY candidate
# sites volume, with all other capabilities dropped and rootfs read-only.
# The actual image startup entrypoint will later link compiled assets.
writer=r"""
import base64,json,os,pathlib,stat,sys
phase='PREFLIGHT'
try:
 p=json.loads(sys.stdin.buffer.read())
 root=pathlib.Path('/home/frappe/frappe-bench/sites')
 site=root/'ccpcerp.local'
 def check(path,kind,mode):
  s=path.lstat()
  typ=stat.S_ISDIR if kind=='dir' else stat.S_ISREG
  assert typ(s.st_mode) and s.st_uid==1000 and stat.S_IMODE(s.st_mode)==mode
 assert os.geteuid()==1000 and os.getegid()==1000
 check(root/'common_site_config.json','file',0o600)
 check(root/'apps.txt','file',0o644)
 check(site,'dir',0o755)
 assert {v.name for v in root.iterdir()}=={'common_site_config.json','apps.txt','ccpcerp.local'}
 assert not list(site.iterdir())
 assert len(p['private'])==1
 name,encoded=p['private'][0]
 assert name not in ('','.','..') and '/' not in name and '\\' not in name
 data=base64.b64decode(encoded,validate=True)
 assert len(data)<=4*1024*1024
 os.umask(0o077)
 def folder(parent,name):
  path=parent/name
  path.mkdir(mode=0o700)
  os.chmod(path,0o755)
  check(path,'dir',0o755)
  return path
 def output(parent,name,data):
  path=parent/name
  fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'wb') as f:
   f.write(data)
   f.flush()
   os.fsync(f.fileno())
  check(path,'file',0o600)
 phase='SITE_CONFIG'
 output(site,'site_config.json',(json.dumps(p['site'],sort_keys=True)+'\n').encode())
 phase='PUBLIC_DIRS'
 folder(folder(site,'public'),'files')
 phase='PRIVATE_DIRS'
 files=folder(folder(site,'private'),'files')
 phase='PRIVATE_ATTACHMENT'
 output(files,name,data)
 phase='POSTCHECK'
 assert {v.name for v in site.iterdir()}=={'site_config.json','public','private'}
 assert len(list(files.iterdir()))==1
 print('CANDIDATE_SITE_WRITE_PASS')
except Exception:
 print('CANDIDATE_SITE_WRITE_STOP_'+phase)
 sys.exit(1)
"""
cmd=[
 'sudo','docker','run','-i','--rm','--pull=never',
 '--name','ccpc_option_a_a2_partial_site_writer_20261109',
 '--network','none','--read-only','--user','1000:1000',
 '--cap-drop','ALL','--security-opt','no-new-privileges',
 '--pids-limit','64','--memory','256m',
 '--tmpfs','/tmp:rw,nosuid,nodev,size=16m',
 '--tmpfs','/home/frappe/frappe-bench/logs:rw,nosuid,nodev,size=8m',
 '--mount','type=volume,source='+PROJECT+'_sites,target=/home/frappe/frappe-bench/sites,volume-nocopy',
 '--entrypoint','/home/frappe/frappe-bench/env/bin/python',
 APP_IMAGE,'-c',writer
]
r=proc(cmd,payload,timeout=90)
if r.returncode!=0 or r.stdout.decode('utf8','replace').strip()!='CANDIDATE_SITE_WRITE_PASS':
    stop('PARTIAL_CONTINUATION_RETAIN_STATE')
print('A2_PARTIAL_SITE_CONFIG_AND_PRIVATE_ATTACHMENT_RESTORED_PASS',flush=True)
if inventory(('ps','-a','--format','{{.Names}}'))!=OLD|NEW or inventory(('volume','ls','--format','{{.Name}}'))!=VOLUMES or inventory(('network','ls','--format','{{.Name}}'))!=NETWORKS:
    stop('POST_RESTORE_RESOURCE_INVENTORY')
for name in OLD:
    if docker('inspect','--format','{{.State.Running}}',name)!='true':
        stop('POST_RESTORE_REHEARSAL_SERVICE')
print('A2_PARTIAL_SIX_REHEARSAL_SERVICES_PRESERVED',flush=True)
print('A2_PARTIAL_NO_APP_WORKERS_MIGRATION_OR_PUBLIC_PORTS',flush=True)
print('A2_PARTIAL_CANDIDATE_SITE_READY_FOR_APP_TEST',flush=True)
