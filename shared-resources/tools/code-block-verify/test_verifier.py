import importlib.util
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch
import verify
from build_report import classify

class VerifierTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('tsc'), 'TypeScript compiler not installed')
    def test_independent_fences_do_not_share_names(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); proj=root/'ts-09'; proj.mkdir()
            (proj/'tsconfig.json').write_text('{"compilerOptions":{"target":"ES2022","module":"ESNext"},"include":["src/*.ts"]}')
            blocks=[{'id':'00001','module':'09-nodejs-backend','lang':'ts','content':'const c = { inc: () => 1 }; c.inc();'},
                    {'id':'00002','module':'09-nodejs-backend','lang':'ts','content':'const c = { req: { url: "example" } }; c.req.url;'}]
            results={b['id']:{'l1':None} for b in blocks}
            with patch.object(verify,'WORK',d), patch.object(verify,'HERE',d):
                verify.verify_ts_l1(blocks,results,lambda _:None)
            self.assertEqual([r['l1']['status'] for r in results.values()],['PASS','PASS'])

    def test_both_streams_retained(self):
        with tempfile.TemporaryDirectory() as d, patch.object(verify,'HERE',d):
            rc, out=verify.run([verify.sys.executable,'-c','import sys; print("stdout"); print("stderr",file=sys.stderr)'])
            self.assertEqual(rc,0)
            self.assertIn('stdout',out)
            self.assertIn('stderr',out)

    def test_utf8_diagnostics_decode_on_legacy_console_hosts(self):
        with tempfile.TemporaryDirectory() as d, patch.object(verify,'HERE',d):
            rc, out = verify.run([verify.sys.executable, '-c',
                                  'import sys; sys.stderr.buffer.write("编译错误".encode("utf-8"))'])
            self.assertEqual(rc, 0)
            self.assertIn('编译错误', out)
    def test_json_does_not_require_yaml(self):
        import builtins
        original = builtins.__import__
        def without_yaml(name, *args, **kwargs):
            if name == 'yaml': raise ImportError('absent for test')
            return original(name, *args, **kwargs)
        with tempfile.TemporaryDirectory() as d:
            Path(d,'b00001.json').write_text('{"ok":true}')
            result={'00001':{'l1':None}}
            with patch.object(verify,'BLOCKS',d), patch('builtins.__import__',side_effect=without_yaml):
                verify.verify_datafmt_l1([{'id':'00001','lang':'json'}],result)
            self.assertEqual(result['00001']['l1']['status'],'PASS')
    def test_rustfmt_shim_without_component_is_unavailable(self):
        with patch.object(verify.shutil,'which',return_value='/bin/rustfmt'), patch.object(verify,'run',return_value=(1,"rustfmt is not installed")) as probe:
            self.assertFalse(verify.tool_availability()['rust_l1'])
            probe.assert_called_once_with(['rustfmt','--version'],timeout=15)
    def test_rustfmt_installed_component_is_available(self):
        with patch.object(verify.shutil,'which',return_value='/bin/rustfmt'), patch.object(verify,'run',return_value=(0,'rustfmt 1.8')):
            self.assertTrue(verify.tool_availability()['rust_l1'])
    def test_php_commands_retain_block_identity(self):
        with tempfile.TemporaryDirectory() as d:
            block={'id':'00042','lang':'php','content':'<?php echo 1;'}
            Path(d,'b00042.php').write_text(block['content'])
            result={'00042':{'l1':None,'l2':None}}
            with patch.object(verify,'WORK',d), patch.object(verify,'BLOCKS',d), patch.object(verify,'run',return_value=(0,'')) as runner:
                verify.verify_phplike_l1([block],result)
                verify.verify_php_l2([block],result)
                for call in runner.call_args_list:
                    self.assertIn('b00042.', ' '.join(call.args[0]))
            self.assertEqual(result['00042']['l1']['status'],'PASS')
            self.assertEqual(result['00042']['l2']['status'],'PASS')
    def test_missing_tool_is_not_pass(self):
        with tempfile.TemporaryDirectory() as d, patch.object(verify,'HERE',d):
            rc,out=verify.run(['nonexistent-dq-tool-123456'])
            self.assertEqual(rc,127)
    def test_timeout_requires_review(self):
        self.assertEqual(classify({'l1':{'status':'PASS'},'l2':{'status':'TIMEOUT'}}),'NEEDS_REVIEW')
    def test_unverified_is_not_success(self):
        self.assertEqual(classify({'l1':{'status':'SKIP_NOTOOL'},'l2':None}),'NOT_VERIFIED')
    def test_tsc_config_failure_never_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); proj=root/'ts-09'; proj.mkdir(); (proj/'tsconfig.json').write_text('{}')
            block={'id':'00001','module':'09-nodejs-backend','lang':'ts','content':'const x = 1'}
            result={'00001':{'l1':None}}
            with patch.object(verify,'WORK',d), patch.object(verify,'run',return_value=(1,'error TS5058: missing config')):
                verify.verify_ts_l1([block],result,lambda _:None)
            self.assertEqual(result['00001']['l1']['status'],'ERROR_TOOL')
    def test_absolute_tsc_diagnostic_is_associated(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); proj=root/'ts-09'; proj.mkdir(); (proj/'tsconfig.json').write_text('{}')
            block={'id':'00001','module':'09-nodejs-backend','lang':'ts','content':'const x ='}
            result={'00001':{'l1':None}}
            with patch.object(verify,'WORK',d), patch.object(verify,'run',return_value=(2,'/tmp/dq-verify/ts-09/src/b00001.ts(1,10): error TS1109: Expression expected.')):
                verify.verify_ts_l1([block],result,lambda _:None)
            self.assertEqual(result['00001']['l1']['status'],'FAIL')

    def test_global_tsc_error_does_not_clear_unreported_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); proj=root/'ts-09'; proj.mkdir(); (proj/'tsconfig.json').write_text('{}')
            blocks=[{'id':bid,'module':'09-nodejs-backend','lang':'ts','content':'const value = 1'}
                    for bid in ('00001','00002')]
            results={b['id']:{'l1':None} for b in blocks}
            output='src/b00001.ts(1,1): error TS1109: Expression expected.\nerror TS2688: Cannot find type definition file.'
            with patch.object(verify,'WORK',d), patch.object(verify,'run',return_value=(2,output)) as runner:
                verify.verify_ts_l1(blocks,results,lambda _:None)
            self.assertEqual(results['00001']['l1']['status'],'FAIL')
            self.assertEqual(results['00002']['l1']['status'],'ERROR_TOOL')
            self.assertEqual(runner.call_args.args[0][-2:],['--moduleDetection','force'])

if __name__=='__main__': unittest.main()
