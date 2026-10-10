"""Approved A01–A16: real touches/keys, independent expected values, read-only evidence."""
from pathlib import Path
import hashlib, json, re, subprocess, time, traceback, zipfile
import xml.etree.ElementTree as ET
from visual import validate_visual

PACKAGE='io.harness.menu'
ACTIVITY=PACKAGE+'/.MainActivity'
COPY={'eyebrow':'A LITTLE EVERY DAY','title':'2048','tagline':'Make room for your next move.',
      'score-caption':'YOUR BEST','continue-label':'Continue','new-label':'New game',
      'reset-label':'Reset best score','footer':'Swipe. Combine. Keep going.'}

class Suite:
    def __init__(self,adb,env,serial,out,device,build,project,original):
        self.adb=adb+['-s',serial]; self.env=env;self.out=out;out.mkdir(parents=True)
        self.device=device;self.build=build;self.project=project;self.original=original
        self.commands=[];self.cases=[];self.shots=[];self.current=None;self.seq=0
        self.case_deadline=self.suite_deadline=float('inf')
    def command(self,args,check=True,binary=False,limit=20):
        remain=min(self.case_deadline,self.suite_deadline)-time.monotonic()
        if remain<=0:raise TimeoutError('Approved case/suite timeout')
        started=time.time()
        try:r=subprocess.run(self.adb+args,env=self.env,capture_output=True,timeout=min(limit,remain))
        except subprocess.TimeoutExpired:
            self.commands.append({'case':self.current,'args':args,'started_at':started,'timed_out':True});self.save();raise
        entry={'case':self.current,'args':args,'started_at':started,'exit':r.returncode,
               'stdout':'<binary>' if binary else r.stdout.decode(errors='replace'),'stderr':r.stderr.decode(errors='replace')}
        self.commands.append(entry)
        if check and r.returncode:raise RuntimeError(str(entry))
        return r.stdout if binary else r.stdout.decode(errors='replace').strip()
    def shell(self,*args,**kw):return self.command(['shell',*args],**kw)
    def until(self,read,predicate,label):
        end=min(self.case_deadline,self.suite_deadline,time.monotonic()+10);actual=None
        while time.monotonic()<end:
            actual=read()
            if predicate(actual):return actual
            time.sleep(.08)
        raise AssertionError(label+': '+str(actual))
    def check(self,label,actual,expected):
        result={'label':label,'actual':actual,'expected':expected,'passed':actual==expected}
        if self.cases:self.cases[-1]['assertions'].append(result)
        if actual!=expected:raise AssertionError(str(result))
    def observe(self,predicate=lambda o:True,after=0):
        deadline=min(self.case_deadline,self.suite_deadline,time.monotonic()+10);latest=None
        while time.monotonic()<deadline:
            raw=self.shell('run-as',PACKAGE,'cat','files/observation.json',check=False)
            try:latest=json.loads(raw)
            except ValueError:latest=None
            if latest and latest['capturedAt']>after and latest['frame']>0 and predicate(latest):
                self.seq+=1;(self.out/f'observation-{self.seq:04}.json').write_text(json.dumps(latest,indent=2)+'\n');return latest
            time.sleep(.08)
        raise AssertionError('Fresh expected observation missing: '+str(latest and latest['state']))
    def node(self,o,name):
        nodes=[n for n in o['nodes'] if n['name']==name]
        assert len(nodes)==1,(name,len(nodes));return nodes[0]
    def state(self,best=128,session='',modal=False,active=False,after=0):
        screen=('dialog/reset-resumable' if session else 'dialog/reset-empty') if modal else 'session/active' if active else ('menu/zero-resumable' if session else 'menu/zero-empty') if best==0 else ('menu/resumable' if session else 'menu/default')
        expected={'screen':screen,'best':best,'session':session,'modal':modal}
        o=self.observe(lambda o:o['state']==expected,after);self.check('state',o['state'],expected);return o
    def cold(self):
        previous=self.shell('pidof',PACKAGE,check=False)
        self.shell('am','force-stop',PACKAGE)
        gone=self.until(lambda:self.shell('pidof',PACKAGE,check=False),lambda p:p=='','force-stop process termination')
        self.check('force-stop removes process',gone,'')
        self.shell('run-as',PACKAGE,'rm','-f','files/observation.json')
        self.shell('am','start','-W','-n',ACTIVITY)
        pid=self.shell('pidof',PACKAGE);o=self.state()
        self.check('native actual pid',str(o['pid']),pid)
        if previous:self.check('new pid',pid!=previous,True)
        return o
    def touch(self,o,x,y):self.shell('input','tap',str(round(x)),str(round(y)));return o['capturedAt']
    def tap(self,name,o):
        b=self.node(o,name)['bounds'];return self.touch(o,(b[0]+b[2])/2,(b[1]+b[3])/2)
    def click_state(self,name,o,**expected):return self.state(after=self.tap(name,o),**expected)
    def new_game(self,o):
        before=o['state']['session'];t=self.tap('new-game',o)
        n=self.observe(lambda x:x['state']['screen']=='session/active',t)
        self.check('new nonempty identity',bool(n['state']['session']) and n['state']['session']!=before,True)
        self.check('new retains best',n['state']['best'],o['state']['best']);return n
    def menu(self,o):return self.click_state('menu-back',o,best=o['state']['best'],session=o['state']['session'])
    def reset(self,o):
        d=self.click_state('reset-best',o,best=o['state']['best'],session=o['state']['session'],modal=True)
        return self.click_state('confirm-reset',d,best=0,session=o['state']['session'])
    def prepared(self,best=128,session=False,active=False,modal=False):
        o=self.cold()
        if session:o=self.menu(self.new_game(o))
        if best==0:o=self.reset(o)
        if active:o=self.click_state('continue',o,best=best,session=o['state']['session'],active=True)
        if modal:o=self.click_state('reset-best',o,best=best,session=o['state']['session'],modal=True)
        return o
    def xml(self,name):
        self.shell('uiautomator','dump','--compressed','/sdcard/harness-menu.xml')
        raw=self.shell('cat','/sdcard/harness-menu.xml');(self.out/(name+'.xml')).write_text(raw)
        return list(ET.fromstring(raw).iter('node'))
    def screenshot(self,name,o=None):
        raw=self.command(['exec-out','screencap','-p'],binary=True)
        assert raw.startswith(b'\x89PNG\r\n\x1a\n');(self.out/(name+'.png')).write_bytes(raw)
        self.shots.append({'case':self.current,'path':name+'.png','sha256':hashlib.sha256(raw).hexdigest(),'state':o and o['state']});return raw
    def snapshot(self,name,o):
        xml=self.xml(name)
        # Accessibility query completes first; then require another real draw of the same state.
        # Capturing immediately after CPU onDraw can still read the previous compositor buffer.
        deadline=min(self.case_deadline,self.suite_deadline,time.monotonic()+10)
        fresh=self.observe(lambda v:v['state']==o['state'] and v['frame']>o['frame'],o['capturedAt'])
        while time.monotonic()<deadline:
            previous=fresh
            fresh=self.observe(lambda v:v['state']==o['state'] and v['frame']>previous['frame']
                               and v['capturedAt']-previous['capturedAt']>=350,previous['capturedAt'])
            if fresh['nodes']==previous['nodes'] and fresh['insets']==previous['insets']:break
        else:raise AssertionError('Native layout/insets did not settle within 10 seconds')
        self.check('layout stable across native frames',fresh['nodes']==previous['nodes'],True)
        # Initial system-bar insets may legitimately arrive after the first cold-start frame.
        # All subsequent comparisons use this actually settled observation, not the earlier geometry.
        o.clear();o.update(fresh)
        raw=self.screenshot(name,fresh)
        (self.out/(name+'.json')).write_text(json.dumps(fresh,indent=2)+'\n');return raw,xml
    def menu_assert(self,o):
        for name,text in COPY.items():self.check('exact '+name,self.node(o,name)['text']['copy'],text)
        self.check('best label',self.node(o,'best')['text']['copy'],str(o['state']['best']))
        enabled=bool(o['state']['session']);self.check('Continue enabled',self.node(o,'continue')['enabled'],enabled)
    def session_assert(self,o):
        for name,text in [('session-title',"Let's\nbegin."),('session-copy','Session started.'),('menu-label','Menu'),('tile-value-0','2'),('tile-value-1','2')]:
            self.check('session '+name,self.node(o,name)['text']['copy'],text)
        self.check('exact tiles',len([n for n in o['nodes'] if re.fullmatch('tile-[0-3]',n['name'])]),4)
        self.check('exact numbered tiles',len([n for n in o['nodes'] if n['name'].startswith('tile-value-')]),2)
    def foreground(self):
        text=self.shell('dumpsys','activity','activities')
        return [line.strip() for line in text.splitlines() if any(s in line for s in ['topResumedActivity','mResumedActivity'])]
    def resources(self,o):
        source=self.project/'design-inputs/packages/UI-FIGMA-ANDROID-MENU/U001'
        with zipfile.ZipFile(self.build['apk']['path']) as z:
            for name,relative in [('asset-arrow.png','assets/asset-arrow.png'),('asset-reset.png','assets/asset-reset.png'),('tokens.json','tokens.json')]:
                expected=hashlib.sha256((source/relative).read_bytes()).hexdigest()
                self.check('D -> APK '+name,hashlib.sha256(z.read('assets/ui/'+name)).hexdigest(),expected)
                self.check('APK -> actually loaded '+name,o['loaded'].get(name),expected)
        self.check('actual parsed tokens',o['tokens'],json.loads((source/'tokens.json').read_text()))
        for node,asset in [('arrow','asset-arrow.png'),('reset-icon','asset-reset.png')]:
            n=self.node(o,node);self.check('used ImageView '+node,[n.get('asset'),n.get('bitmapWidth'),n.get('bitmapHeight')],[asset,72,72])
    def accessibility(self,o,nodes):
        native=[n for n in nodes if n.get('package')==PACKAGE];labels={n.get('text'):n for n in native}
        if o['state']['modal']:
            for name in ['Cancel','Reset','A fresh start?']:self.check('modal native name '+name,name in labels,True)
            for name in ['Continue','New game','Reset best score','2048']:self.check('modal background absent '+name,name in labels,False)
            self.check('background a11y hidden',self.node(o,'content')['importantForAccessibility'],4)
        elif o['state']['screen']=='session/active':self.check('native Menu button',labels['Menu'].get('class'),'android.widget.Button')
        else:
            for name in ['Continue','New game','Reset best score']:self.check('native button '+name,labels[name].get('class'),'android.widget.Button')
            self.check('native disabled state',labels['Continue'].get('enabled'),str(bool(o['state']['session'])).lower())
    def case_A01(self):
        o=self.cold();self.snapshot('A01-default',o);self.menu_assert(o)
    def case_A02(self):
        o=self.cold();n=self.state(after=self.tap('continue',o));self.check('same process',n['process'],o['process']);self.menu_assert(n)
    def case_A03(self):
        o=self.cold();first=self.new_game(o);self.session_assert(first);self.snapshot('A03-first-session',first)
        second=self.new_game(self.menu(first));self.session_assert(second);self.snapshot('A03-replaced-session',second)
        self.check('replacement identity',second['state']['session']!=first['state']['session'],True)
    def case_A04(self):
        first=self.new_game(self.cold());o=self.menu(first);self.menu_assert(o);self.snapshot('A04-resumable',o)
    def case_A05(self):
        m=self.menu(self.new_game(self.cold()));sid=m['state']['session']
        for i in range(2):m=self.menu(self.click_state('continue',m,session=sid,active=True))
        self.menu_assert(m)
    def cancel_variants(self,session):
        for best in [128,0]:
            o=self.prepared(best,session);sid=o['state']['session'];d=self.click_state('reset-best',o,best=best,session=sid,modal=True)
            # The uncovered edge of the real background New control must be blocked by the overlay.
            b=self.node(d,'new-game')['bounds'];t=self.touch(d,b[0]+4,(b[1]+b[3])/2)
            d=self.state(best,sid,True,after=t);self.snapshot(f'{self.current}-best{best}-modal',d)
            m=self.click_state('cancel',d,best=best,session=sid);self.menu_assert(m)
    def case_A06(self):self.cancel_variants(False)
    def case_A07(self):
        m=self.prepared();m=self.reset(m);self.menu_assert(m);m=self.reset(m);self.menu_assert(m);self.snapshot('A07-zero-empty',m)
    def case_A08(self):self.cancel_variants(True)
    def case_A09(self):
        m=self.prepared(session=True);sid=m['state']['session']
        for i in range(2):
            m=self.reset(m);self.menu_assert(m);s=self.click_state('continue',m,best=0,session=sid,active=True);m=self.menu(s)
        self.snapshot('A09-zero-resumable',m)
    def case_A10(self):
        m=self.prepared(best=0);s=self.new_game(m);self.session_assert(s);self.check('zero new',s['state']['best'],0)
        old=s['state']['session'];s=self.new_game(self.menu(s));self.check('zero replacement',s['state']['session']!=old,True);self.check('zero retained',s['state']['best'],0)
    def case_A11(self):
        for best in [128,0]:
            for session in [False,True]:
                d=self.prepared(best,session,modal=True);sid=d['state']['session'];self.shell('input','keyevent','4')
                m=self.state(best,sid,after=d['capturedAt']);self.menu_assert(m)
            s=self.prepared(best,True,active=True);self.shell('input','keyevent','4')
            m=self.state(best,s['state']['session'],after=s['capturedAt']);self.menu_assert(m)
        self.shell('input','keyevent','4');f=self.until(self.foreground,lambda rows:bool(rows) and not any(PACKAGE in v for v in rows),'root Back foreground');self.check('root Back leaves foreground',any(PACKAGE in v for v in f),False)
        (self.out/'A11-system-foreground.json').write_text(json.dumps(f,indent=2)+'\n')
    def case_A12(self):
        for best in [128,0]:
            for label,session,active,modal in [('empty',False,False,False),('menu',True,False,False),('session',True,True,False),('empty-modal',False,False,True),('session-modal',True,False,True)]:
                before=self.prepared(best,session,active,modal);self.shell('input','keyevent','3')
                foreground=self.until(self.foreground,lambda rows:bool(rows) and not any(PACKAGE in v for v in rows),'Home foreground')
                self.check('Home yields system',any(PACKAGE in x for x in foreground),False)
                self.check('Home preserves actual pid',self.shell('pidof',PACKAGE),str(before['pid']))
                self.shell('am','start','-W','-n',ACTIVITY)
                after=self.observe(lambda v:v['state']==before['state'],before['capturedAt'])
                self.check('Home keeps process',after['process'],before['process']);self.check('Home keeps PID',after['pid'],before['pid'])
                self.snapshot(f'A12-{best}-{label}',after)
        old=after['process'];fresh=self.cold();self.check('cold process identity changes',fresh['process']!=old,True)
    def case_A13(self):
        for label,active,modal in [('menu',False,False),('session',True,False),('modal',False,True)]:
            o=self.prepared(0,True,active,modal)
            self.shell('settings','put','system','accelerometer_rotation','0');self.shell('settings','put','system','user_rotation','1')
            n=self.observe(lambda v:v['state']==o['state'],o['capturedAt']);self.check('portrait configuration',n['orientation'],1)
            self.check('portrait pixels',[n['width'],n['height']],self.device['pixels']);self.snapshot('A13-'+label,n)
            validate_visual(self,n,None,geometry_only=True)
            self.shell('settings','put','system','user_rotation','0');self.check('rotation restored for suite',self.shell('settings','get','system','user_rotation'),'0')
    def visual_states(self,scale):
        self.shell('settings','put','system','font_scale',str(scale))
        self.check('actual system font scale',float(self.shell('settings','get','system','font_scale')),scale)
        def inspect(label,o):
            self.check('actual configuration scale',round(o['fontScale'],3),scale)
            data,nodes=self.snapshot(f'{self.current}-{label}',o);self.accessibility(o,nodes);validate_visual(self,o,data)
        m=self.cold();inspect('default',m)
        d=self.click_state('reset-best',m,modal=True);inspect('reset-empty-128',d)
        z=self.click_state('confirm-reset',d,best=0);inspect('zero-empty',z)
        dz=self.click_state('reset-best',z,best=0,modal=True);inspect('reset-empty-0',dz)
        z=self.click_state('cancel',dz,best=0)
        s=self.new_game(z);inspect('session',s)
        z=self.menu(s);sid=z['state']['session'];inspect('zero-resumable',z)
        dz=self.click_state('reset-best',z,best=0,session=sid,modal=True);inspect('reset-resumable-0',dz)
        m=self.prepared(session=True);sid=m['state']['session'];inspect('resumable',m)
        d=self.click_state('reset-best',m,session=sid,modal=True);inspect('reset-resumable-128',d)
    def case_A14(self):self.visual_states(1.0)
    def case_A15(self):self.visual_states(1.3)
    def case_A16(self):
        o=self.cold();self.resources(o);self.accessibility(o,self.xml('A16-disabled'))
        m=self.menu(self.new_game(o));self.accessibility(m,self.xml('A16-enabled'))
        d=self.click_state('reset-best',m,session=m['state']['session'],modal=True);self.accessibility(d,self.xml('A16-modal'))
        for key,value in self.original.items():
            args=['delete','system',key] if value=='null' else ['put','system',key,value]
            self.shell('settings',*args);self.check('actual original setting '+key,self.shell('settings','get','system',key),value)
    def save(self):
        (self.out/'commands.json').write_text(json.dumps(self.commands,indent=2)+'\n')
        (self.out/'suite.json').write_text(json.dumps({'cases':self.cases,'screenshots':self.shots},indent=2)+'\n')
    def run(self,selected=None):
        self.suite_deadline=time.monotonic()+1800
        ids=selected or [f'A{i:02}' for i in range(1,17)]
        for i,case in enumerate(ids):
            self.current=case;limit=240 if case in ['A12','A14','A15','A16'] else 90
            self.case_deadline=time.monotonic()+limit
            row={'id':case,'status':'running','started_at':time.time(),'timeout_seconds':limit,'assertions':[]};self.cases.append(row);self.save()
            try:getattr(self,'case_'+case)();row['status']='passed'
            except Exception as error:
                row.update(status='failed',error=str(error),traceback=traceback.format_exc())
                for pending in ids[i+1:]:self.cases.append({'id':pending,'status':'not-run','reason':'earlier required case failed'})
                raise
            finally:row['finished_at']=time.time();self.save();print(self.device['name'],case,row['status'],flush=True)
        return self.cases
