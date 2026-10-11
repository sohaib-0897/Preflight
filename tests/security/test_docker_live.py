"""Live checks require Docker plus an already-built operator native runner image.
These are skipped here; command construction tests do not substitute for isolation.
"""
import json
import os
import shutil
import subprocess
import uuid
import pytest
from preflight_eval.sandbox import docker_command, DockerBackend, InfrastructureFailure

pytestmark = pytest.mark.skipif(not shutil.which('docker'), reason='Docker executable absent; live isolation not verified')


def run_python(source):
    name='preflight-live-'+uuid.uuid4().hex
    image=os.environ.get('PREFLIGHT_SANDBOX_IMAGE','preflight-sandbox:0.1.0')
    args=docker_command(name,image)
    args[-1:-1]=['--entrypoint','python']
    args.extend(['-B','-c',source])
    try:
        return subprocess.run(args,capture_output=True,timeout=20)
    finally:
        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=10)


def test_live_native_fixture():
    assert DockerBackend().execute('refund','accurate',42)['assessment']['task_success']


def test_live_network_and_filesystem_boundaries():
    result=run_python('''import socket,os,json
out={'uid':os.getuid()}
try:
 open('/etc/preflight-probe','w').write('x')
 out['readonly']=False
except OSError: out['readonly']=True
out['network_denied']=True
for host in ['169.254.169.254','1.1.1.1']:
 s=socket.socket();s.settimeout(.2)
 try: s.connect((host,80));out['network_denied']=False
 except OSError: pass
 finally:s.close()
print(json.dumps(out))''')
    assert result.returncode == 0,result.stderr
    data=json.loads(result.stdout)
    assert data=={'uid':10001,'readonly':True,'network_denied':True}


def test_live_cgroup_caps_and_process_limits():
    result=run_python('''import json,resource
from pathlib import Path
status=Path('/proc/self/status').read_text()
print(json.dumps({'memory':Path('/sys/fs/cgroup/memory.max').read_text().strip(),'pids':Path('/sys/fs/cgroup/pids.max').read_text().strip(),'caps':next(x for x in status.splitlines() if x.startswith('CapEff:')).split()[1],'nofile':resource.getrlimit(resource.RLIMIT_NOFILE)[0]}))''')
    assert result.returncode==0,result.stderr
    data=json.loads(result.stdout)
    assert int(data['memory'])==128*1024*1024 and int(data['pids'])==32
    assert int(data['caps'],16)==0 and data['nofile']==128


def test_live_memory_exhaustion_is_contained():
    result=run_python("value=bytearray(256*1024*1024);print(len(value))")
    assert result.returncode in {137,1},result.stdout


def test_live_disk_quota():
    result=run_python("import sys\ntry:\n open('/tmp/large','wb').write(b'x'*(17*1024*1024))\nexcept OSError:\n sys.exit(0)\nsys.exit(1)")
    assert result.returncode==0,result.stderr


def test_live_timeout_and_cleanup():
    with pytest.raises(InfrastructureFailure):
        DockerBackend().execute('latency','slow',42,timeout=.001)
    # Native runner names are individually removed by the backend finally block.
    result=subprocess.run(['docker','ps','-q','--filter','label=preflight.sandbox=true'],capture_output=True,timeout=10,check=True)
    assert not result.stdout.strip(),'Run live tests on a dedicated development daemon'
