#!/usr/bin/env python3
"""Run the fixed native Android matrix on owned ADB/AVDs; never mutate global config."""
from pathlib import Path
import argparse,hashlib,json,os,signal,socket,subprocess,sys,time,traceback,zipfile

p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--cases',help='Targeted diagnosis only; cannot produce a full-matrix PASS')
p.add_argument('--device',choices=['small','regular'],help='Targeted diagnosis only')
a=p.parse_args();root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tests/android-menu'))
from suite import Suite,PACKAGE,ACTIVITY
c=json.loads(a.config.read_text());build=json.loads(a.build.read_text());out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
expected_path=root/'design-inputs/packages/UI-FIGMA-ANDROID-MENU/U001/expected-copy.json';expected=json.loads(expected_path.read_text())
selected=a.cases.split(',') if a.cases else None
assert selected is None or len(set(selected))==len(selected) and all(x in [case['id'] for case in expected['cases']] for x in selected)
env=dict(os.environ,ANDROID_USER_HOME=c['android_user'],ANDROID_EMULATOR_HOME=c['emulator_home'],ANDROID_AVD_HOME=c['avds'],ANDROID_SDK_ROOT=c['sdk'],ANDROID_ADB_SERVER_PORT='5038',ADB_SERVER_SOCKET='tcp:127.0.0.1:5038')
adb=[c['sdk']+'/platform-tools/adb','-P','5038'];processes=[];settings=[];server_started=False
r={'started_at':time.time(),'apk':build.get('apk'),'source_head':build.get('source_head'),'expected_sha256':hashlib.sha256(expected_path.read_bytes()).hexdigest(),
   'mode':'targeted' if a.cases or a.device else 'full','expected_cases':32,'devices':[],'commands':[],'passed':False,'selected_passed':False,'cleanup_errors':[]}
def save():(out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def stop(n,f):
    signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN);r['interrupted']=True;raise InterruptedError('Signal '+str(n))
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
def command(args,limit=20,check=True):
    started=time.time();q=subprocess.run(args,env=env,capture_output=True,text=True,timeout=limit)
    row={'args':args,'started_at':started,'exit':q.returncode,'stdout':q.stdout,'stderr':q.stderr};r['commands'].append(row)
    if check and q.returncode:raise RuntimeError(str(row))
    return q.stdout.strip()
try:
    assert build['passed'] and hashlib.sha256(Path(build['apk']['path']).read_bytes()).hexdigest()==build['apk']['sha256'],'APK changed'
    r['test_head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    r['test_dirty']=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
    assert not r['test_dirty'],'Freeze actual test source first'
    assert r['test_head']==r['source_head'],'Build and tests must bind the same source HEAD'
    with zipfile.ZipFile(out/'test-inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
        for path in [Path(__file__),*sorted((root/'tests/android-menu').glob('*.py')),expected_path]:z.write(path,path.relative_to(root))
    for port in [5038,5580,5581,5582,5583]:
        with socket.socket() as sock:sock.bind(('127.0.0.1',port))
    command(adb+['start-server']);server_started=True
    for index,(key,device_expected) in enumerate(expected['devices'].items()):
        if a.device and key!=a.device:continue
        serial='emulator-'+str(5580+2*index);name='Harness_UI_'+('Small' if key=='small' else 'Regular')+'_20261009'
        device=dict(device_expected,key=key,name=name);item={'key':key,'name':name,'serial':serial,'cases':[]};r['devices'].append(item);save()
        # The selected existing AVD must reference the approved system image, not merely spoof matching dimensions.
        locator=Path(c['avds'])/(name+'.ini')
        locator_values=dict(line.split('=',1) for line in locator.read_text().splitlines() if '=' in line)
        avd_directory=Path(locator_values['path']).resolve()
        assert avd_directory.is_relative_to(Path(c['avds']).resolve()),'AVD must stay inside the dedicated trial directory'
        avd_config=avd_directory/'config.ini'
        config=avd_config.read_text();item['avd_config_sha256']=hashlib.sha256(config.encode()).hexdigest();item['avd_config']=config
        image_path=replaced=device_expected['system_image_package'].replace(';','/')+'/'
        assert any(line.strip()=='image.sysdir.1='+image_path for line in config.splitlines()),'AVD image package differs'
        cmd=[c['sdk']+'/emulator/emulator','-avd',name,'-port',str(5580+2*index),'-no-window','-no-audio','-no-snapshot','-no-boot-anim','-gpu','swiftshader']
        with (out/(serial+'.log')).open('wb') as log:process=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        processes.append((serial,process));item.update(pid=process.pid,boot_command=cmd,boot_started_at=time.time());save();end=time.monotonic()+240
        while time.monotonic()<end:
            assert process.poll() is None,'AVD exited'
            boot=command(adb+['-s',serial,'shell','getprop','sys.boot_completed'],limit=10,check=False)
            if boot=='1':break
            time.sleep(1)
        else:raise TimeoutError('Approved boot timeout')
        item['boot_completed_at']=time.time()
        dcmd=adb+['-s',serial]
        original={k:command(dcmd+['shell','settings','get','system',k]) for k in ['font_scale','accelerometer_rotation','user_rotation']}
        settings.append((serial,original,item));item['original_settings']=original
        suite=Suite(adb,env,serial,out/serial,device,build,root,original)
        actual={key:suite.shell(*cmd) for key,cmd in {'fingerprint':['getprop','ro.build.fingerprint'],'api':['getprop','ro.build.version.sdk'],'abi':['getprop','ro.product.cpu.abi'],'page_size':['getconf','PAGE_SIZE'],'size':['wm','size'],'density':['wm','density']}.items()}
        item['identity']=actual;save()
        assert actual['fingerprint']==device['fingerprint'] and int(actual['api'])==device['api'] and actual['abi']==device['abi'] and int(actual['page_size'])==device['page_size_bytes']
        assert actual['size']=='Physical size: '+str(device['pixels'][0])+'x'+str(device['pixels'][1])
        assert actual['density']=='Physical density: '+str(device['density_dpi'])
        for k,v in [('font_scale','1.0'),('accelerometer_rotation','0'),('user_rotation','0')]:suite.shell('settings','put','system',k,v)
        suite.command(['install','-r',build['apk']['path']])
        try:item['cases']=suite.run(selected)
        finally:
            item['cases']=suite.cases;suite.case_deadline=suite.suite_deadline=float('inf')
            try:
                (suite.out/'logcat.txt').write_text(suite.command(['logcat','-d','-v','threadtime','-t','1500']))
                suite.screenshot('final-or-failure')
            except Exception as error:item['diagnostic_error']=str(error)
            suite.save();save()
    pairs=[(item['key'],case['id']) for item in r['devices'] for case in item['cases'] if case['status']=='passed']
    required={(key,case['id']) for key in expected['devices'] for case in expected['cases']}
    selected_required={(key,case) for key in expected['devices'] if not a.device or key==a.device for case in selected or [v['id'] for v in expected['cases']]}
    assert len(pairs)==len(set(pairs)) and set(pairs)==selected_required
    r['selected_passed']=True;r['passed']=r['mode']=='full' and set(pairs)==required and len(pairs)==32
except Exception as error:r.update(error=str(error),traceback=traceback.format_exc())
finally:
    cleanup_end=time.monotonic()+120
    for serial,original,item in settings:
        item['restored_settings']={}
        for key,value in original.items():
            try:
                assert time.monotonic()<cleanup_end,'cleanup deadline'
                args=['delete','system',key] if value=='null' else ['put','system',key,value]
                command(adb+['-s',serial,'shell','settings']+args)
                restored=command(adb+['-s',serial,'shell','settings','get','system',key]);item['restored_settings'][key]=restored
                assert restored==value,(key,value,restored)
            except Exception as error:r['cleanup_errors'].append(str(error))
    for serial,process in processes:
        if process.poll() is None:
            try:command(adb+['-s',serial,'emu','kill']);process.wait(timeout=20)
            except Exception as error:
                r['cleanup_errors'].append(str(error));os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
    if server_started:
        try:command(adb+['kill-server'])
        except Exception as error:r['cleanup_errors'].append(str(error))
    if r['cleanup_errors']:r['passed']=r['selected_passed']=False
    r['finished_at']=time.time();save()
print(json.dumps({k:r.get(k) for k in ['passed','selected_passed','mode','error','cleanup_errors']},indent=2))
raise SystemExit(0 if r['selected_passed'] and not r['cleanup_errors'] else 1)
