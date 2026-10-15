"""Actual native rendering RED/GREEN using system accessibility, before menu implementation."""
from pathlib import Path
import argparse,json,os,signal,socket,subprocess,time,hashlib,traceback
import xml.etree.ElementTree as ET

p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--build',required=True);p.add_argument('--output',required=True);a=p.parse_args()
c=json.loads(Path(a.config).read_text());b=json.loads(Path(a.build).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
assert b['passed'] and hashlib.sha256(Path(b['apk']['path']).read_bytes()).hexdigest()==b['apk']['sha256']
env=dict(os.environ,ANDROID_USER_HOME=c['android_user'],ANDROID_EMULATOR_HOME=c['emulator_home'],ANDROID_AVD_HOME=c['avds'],ANDROID_SDK_ROOT=c['sdk'],ANDROID_ADB_SERVER_PORT='5038',ADB_SERVER_SOCKET='tcp:127.0.0.1:5038')
adb=[c['sdk']+'/platform-tools/adb','-P','5038'];device=adb+['-s','emulator-5580'];process=None;owned=False;original={}
r={'started_at':time.time(),'apk':b['apk'],'source_head':b['source_head'],'commands':[],'passed':False,'cleanup_errors':[],'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def save():(out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def run(args,limit=20,binary=False):
    q=subprocess.run(args,env=env,capture_output=True,timeout=limit)
    entry={'args':args,'exit':q.returncode,'stderr':q.stderr.decode(errors='replace')}
    if not binary:entry['stdout']=q.stdout.decode(errors='replace')
    r['commands'].append(entry);save();assert q.returncode==0,entry
    return q.stdout if binary else q.stdout.decode().strip()
def stop(sig,frame):
    signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN)
    raise InterruptedError('Signal '+str(sig))
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:
    for port in [5038,5580,5581]:
        with socket.socket() as sock:sock.bind(('127.0.0.1',port))
    run(adb+['start-server']);owned=True
    cmd=[c['sdk']+'/emulator/emulator','-avd','Harness_UI_Small_20261009','-port','5580','-no-window','-no-audio','-no-snapshot','-no-boot-anim','-gpu','swiftshader']
    with (out/'emulator.log').open('wb') as log:process=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    r['emulator_pid']=process.pid;r['emulator_command']=cmd;save();end=time.monotonic()+240
    while time.monotonic()<end:
        assert process.poll() is None,'emulator terminated'
        q=subprocess.run(device+['shell','getprop','sys.boot_completed'],env=env,capture_output=True,text=True,timeout=10)
        if q.returncode==0 and q.stdout.strip()=='1':break
        time.sleep(1)
    else:raise TimeoutError('AVD boot timeout')
    for key in ['font_scale','accelerometer_rotation','user_rotation']:original[key]=run(device+['shell','settings','get','system',key])
    r['original_settings']=original;save()
    for key,value in [('font_scale','1.0'),('accelerometer_rotation','0'),('user_rotation','0')]:run(device+['shell','settings','put','system',key,value])
    run(device+['install','-r',b['apk']['path']],60)
    run(device+['shell','am','force-stop','io.harness.menu'])
    run(device+['shell','am','start','-W','-n','io.harness.menu/.MainActivity'])
    activities=run(device+['shell','dumpsys','activity','activities']);(out/'activities.txt').write_text(activities)
    assert any('io.harness.menu/.MainActivity' in line and any(x in line for x in ['Resumed','topResumed','mFocusedApp']) for line in activities.splitlines()),'App not foreground; not a behavior RED'
    run(device+['shell','uiautomator','dump','/sdcard/harness-native-initial.xml'])
    xml=run(device+['shell','cat','/sdcard/harness-native-initial.xml']);(out/'window.xml').write_text(xml)
    (out/'screen.png').write_bytes(run(device+['exec-out','screencap','-p'],binary=True))
    labels={n.get('text') for n in ET.fromstring(xml).iter('node')}
    r['assertions']=[{'expected':text,'present':text in labels} for text in ['2048','New game','128']]
    r['passed']=all(x['present'] for x in r['assertions'])
    r['classification']='GREEN' if r['passed'] else 'behavior-RED: actual native foreground lacks required approved controls/text'
except Exception as error:r.update(error=str(error),traceback=traceback.format_exc(),classification='execution-error; not RED')
finally:
    for key,value in original.items():
        try:
            tail=['delete','system',key] if value=='null' else ['put','system',key,value]
            run(device+['shell','settings']+tail)
            assert run(device+['shell','settings','get','system',key])==value
        except Exception as error:r['cleanup_errors'].append(str(error))
    if process and process.poll() is None:
        try:run(device+['emu','kill']);process.wait(timeout=20)
        except Exception as error:
            r['cleanup_errors'].append(str(error));os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    if owned:
        try:run(adb+['kill-server'])
        except Exception as error:r['cleanup_errors'].append(str(error))
    r['finished_at']=time.time();save()
print(json.dumps({k:r[k] for k in ['passed','classification','assertions','error','cleanup_errors'] if k in r},indent=2))
raise SystemExit(0 if r['passed'] and not r['cleanup_errors'] else 1)
