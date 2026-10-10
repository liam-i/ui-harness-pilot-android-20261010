"""Synthetic gate rejection tests; never substitute for native or hosted CI evidence."""
from pathlib import Path
from copy import deepcopy
import importlib.util,unittest

spec=importlib.util.spec_from_file_location('android_ci',Path(__file__).resolve().parents[2]/'harness/ui-design/ci/android-native.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

class ResultContractTests(unittest.TestCase):
    def setUp(self):
        self.head='a'*40;self.expected={'cases':[{'id':f'A{i:02}'} for i in range(1,17)],'cases_per_device':16,'total_device_cases':32,
            'devices':{k:{'pixels':px,'density_dpi':dpi,'api':37,'abi':'arm64-v8a','page_size_bytes':16384,'fingerprint':'TEST'} for k,px,dpi in [('small',[720,1280],320),('regular',[1080,2400],420)]}}
        self.build={'passed':True,'source_head':self.head,'source_dirty':'','started_at':1,'finished_at':5,
                    'steps':[{'exit':0,'timeout_seconds':900,'started_at':2,'finished_at':4}],
                    'apk':{'path':'TEST.apk','bytes':42,'sha256':'b'*64}}
        self.runtime={'passed':True,'selected_passed':True,'mode':'full','source_head':self.head,'test_head':self.head,'test_dirty':'',
            'expected_cases':32,'started_at':6,'finished_at':200,'apk':deepcopy(self.build['apk']),'cleanup_errors':[],'devices':[]}
        for j,(key,d) in enumerate(self.expected['devices'].items()):
            self.runtime['devices'].append({'key':key,'name':'Harness_UI_'+key.title()+'_20261009','serial':f'emulator-{5580+j*2}',
                'boot_started_at':7+j*80,'boot_completed_at':10+j*80,
                'identity':{'fingerprint':'TEST','api':'37','abi':'arm64-v8a','page_size':'16384','size':f"Physical size: {d['pixels'][0]}x{d['pixels'][1]}",'density':f"Physical density: {d['density_dpi']}"},
                'original_settings':{'font_scale':'1.0','accelerometer_rotation':'1','user_rotation':'0'},
                'restored_settings':{'font_scale':'1.0','accelerometer_rotation':'1','user_rotation':'0'},
                'cases':[{'id':v['id'],'status':'passed','started_at':11+j*80+i*3,'finished_at':13+j*80+i*3,
                          'timeout_seconds':240 if v['id'] in ['A12','A14','A15','A16'] else 90,
                          'assertions':[{'passed':True,'actual':1,'expected':1}]} for i,v in enumerate(self.expected['cases'])]})
    def verify(self):return runner.verify_native(self.build,self.runtime,self.expected,self.head)
    def test_complete_exact_matrix(self):self.assertTrue(self.verify()['passed'])
    def test_missing_empty_duplicate_extra_cases(self):
        original=deepcopy(self.runtime)
        for cases in [[],original['devices'][0]['cases'][:-1],original['devices'][0]['cases']*2,original['devices'][0]['cases']+[{'id':'A99','status':'passed'}]]:
            with self.subTest(cases=len(cases)):
                self.runtime=deepcopy(original);self.runtime['devices'][0]['cases']=cases
                with self.assertRaises(ValueError):self.verify()
    def test_skipped_cancelled_failed_not_run(self):
        for state in ['skipped','cancelled','failed','not-run','timed_out']:
            self.runtime['devices'][0]['cases'][0]['status']=state
            with self.assertRaises(ValueError):self.verify()
    def test_false_pass_after_timeout(self):
        self.runtime['devices'][0]['cases'][0]['finished_at']=150
        with self.assertRaises(ValueError):self.verify()
    def test_missing_wrong_duplicate_device(self):
        original=deepcopy(self.runtime)
        for devices in [original['devices'][:1],original['devices'][:1]*2]:
            self.runtime=deepcopy(original);self.runtime['devices']=devices
            with self.assertRaises(ValueError):self.verify()
        self.runtime=original;self.runtime['devices'][0]['identity']['api']='36'
        with self.assertRaises(ValueError):self.verify()
    def test_source_apk_or_test_identity(self):
        original=deepcopy(self.runtime)
        for key in ['source_head','test_head']:
            self.runtime=deepcopy(original);self.runtime[key]='c'*40
            with self.assertRaises(ValueError):self.verify()
        self.runtime=original;self.runtime['apk']['sha256']='d'*64
        with self.assertRaises(ValueError):self.verify()
    def test_failed_dirty_missing_build(self):
        original=deepcopy(self.build)
        for key,value in [('passed',False),('source_dirty',' M code'),('steps',[])]:
            self.build=deepcopy(original);self.build[key]=value
            with self.assertRaises(ValueError):self.verify()
        self.build=original;self.build['steps'][0]['exit']=1
        with self.assertRaises(ValueError):self.verify()
    def test_no_assertions_or_failed_assertion(self):
        case=self.runtime['devices'][0]['cases'][0];case['assertions']=[]
        with self.assertRaises(ValueError):self.verify()
        case['assertions']=[{'passed':False}]
        with self.assertRaises(ValueError):self.verify()
    def test_cleanup_failure_or_missing_restore(self):
        self.runtime['cleanup_errors']=['TEST failed cleanup']
        with self.assertRaises(ValueError):self.verify()
        self.runtime['cleanup_errors']=[];self.runtime['devices'][0]['restored_settings'].pop('font_scale')
        with self.assertRaises(ValueError):self.verify()
    def test_targeted_is_not_full_pass(self):
        self.runtime['mode']='targeted'
        with self.assertRaises(ValueError):self.verify()
    def test_empty_denominator_or_missing_result(self):
        self.expected['cases']=[]
        with self.assertRaises(ValueError):self.verify()
        with self.assertRaises(ValueError):runner.verify_native({},self.runtime,self.expected,self.head)
        with self.assertRaises(ValueError):runner.verify_native(self.build,{},self.expected,self.head)

if __name__=='__main__':unittest.main()
