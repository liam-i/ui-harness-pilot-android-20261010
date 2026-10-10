#!/usr/bin/env python3
"""Build the reviewed native Java project; preserve source and artifact identity."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,time,zipfile

p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];c=json.loads(a.config.read_text());out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
h=lambda data:hashlib.sha256(data).hexdigest()
record={'started_at':time.time(),'project':str(root),'passed':False,'steps':[],'host_config_sha256':h(a.config.read_bytes())}
def save():(out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
def interrupted(number,frame):
    signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN)
    record['interrupted']=True;raise InterruptedError('Build interrupted '+str(number))
signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
env=dict(os.environ,JAVA_HOME=c['jdk'],ANDROID_HOME=c['sdk'],ANDROID_SDK_ROOT=c['sdk'],GRADLE_USER_HOME=c['gradle_cache'],ANDROID_USER_HOME=c['android_user'])
env['PATH']=c['jdk']+'/bin:'+env.get('PATH','')
try:
    record['source_head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    record['source_dirty']=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
    assert not record['source_dirty'],'Build requires frozen clean source'
    names=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().rstrip('\0').split('\0')
    record['source_files']={n:h((root/n).read_bytes()) for n in names}
    with zipfile.ZipFile(out/'build-input-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for n in names:z.write(root/n,n)
    command=[c['gradle'],'--offline','--no-daemon','--console=plain','assembleDebug']
    step={'command':command,'timeout_seconds':900,'started_at':time.time()};record['steps'].append(step);save()
    with (out/'gradle.stdout').open('wb') as stdout,(out/'gradle.stderr').open('wb') as stderr:
        process=subprocess.Popen(command,cwd=root,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        step['pid']=process.pid;save()
        try:step['exit']=process.wait(timeout=900)
        except BaseException as error:
            step['timed_out']=isinstance(error,subprocess.TimeoutExpired)
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
            step['exit']=process.returncode;raise
    step['finished_at']=time.time();assert step['exit']==0,'Gradle failed; original output retained'
    apk=root/'app/build/outputs/apk/debug/app-debug.apk';assert apk.is_file()
    shutil.copyfile(apk,out/'app-debug.apk')
    with zipfile.ZipFile(apk) as z:
        assert z.read('classes.dex')[:3]==b'dex'
        record['apk_assets']={n:h(z.read(n)) for n in z.namelist() if n.startswith('assets/ui/')}
    record['apk']={'path':str(out/'app-debug.apk'),'sha256':h(apk.read_bytes()),'bytes':apk.stat().st_size}
    record['passed']=True
except Exception as error:record['error']=str(error)
finally:record['finished_at']=time.time();save()
print(json.dumps({k:record[k] for k in ['passed','source_head','apk','error'] if k in record},indent=2))
raise SystemExit(0 if record['passed'] else 1)
