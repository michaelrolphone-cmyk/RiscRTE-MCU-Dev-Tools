import json
import hashlib
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from app_manifest import validate_manifest
from build_all_apps import validate_inventory
from check_baseline import ROOT, audit, check_sdk, classify, git_blob
from check_release_parity import compare, validate_cohort
from native_app_symbols import validate_imports
from package_integrity import stamp_app_manifest
from app_build_profile import build_profile_arguments, select_build_profile


class PipelineTests(unittest.TestCase):
    def test_sdk_snapshot_and_inventory(self):
        check_sdk()
        rows = audit()['files']
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row['state'] == 'unchanged' for row in rows))
        provenance = json.loads((ROOT / 'docs/source-drift.json').read_text())['files']
        converged = [row for row in provenance if row['state'] == 'converged']
        unchanged = [row for row in provenance if row['state'] == 'unchanged']
        sdk_provenance = json.loads((ROOT / 'docs/source-drift.json').read_text())['sdk_files']
        self.assertEqual([row['path'] for row in converged],
                         ['Apps/serial_monitor.json', 'Apps/usb_debug.json',
                          'Apps/esp_rom_flasher.json'])
        self.assertEqual(len(unchanged), 5)
        self.assertEqual([row['path'] for row in sdk_provenance],
                         ['lib/NativeApps/include/T5UiApi.h',
                          'sdk/driver/RiscUsbControllerV1.h',
                          'sdk/driver/RiscUsbInterruptV1.h'])
        self.assertTrue(all(row['state'] == 'converged' and
                            row['upstream_commit'] ==
                            '82caa0997e913f01c1f5f9ab942d056bc9f04a82'
                            for row in sdk_provenance))

    def test_version_scoped_build_profiles(self):
        baseline = json.loads((ROOT / 'sdk/release-baseline.json').read_text())
        manifests = {row['id']: json.loads((ROOT / f"Apps/{row['id']}.json").read_text())
                     for row in json.loads((ROOT / 'mcu-dev-tools-manifest.json').read_text())['tools']}
        self.assertEqual({app_id: select_build_profile(manifest, baseline)
                          for app_id, manifest in manifests.items()},
                         {'serial_monitor': 'strip-unneeded', 'usb_debug': 'strip-unneeded',
                          'esp_rom_flasher': 'strip-unneeded'})
        self.assertEqual(build_profile_arguments('strip-unneeded'), ['--strip-unneeded'])
        self.assertEqual(build_profile_arguments('unstripped'), [])
        legacy = {'apps': [{'id': 'settings', 'file_name': 'settings.elf',
                            'version': '1.0.0', 'build_profile': 'unstripped'}]}
        self.assertEqual(select_build_profile({'file_name': 'settings.elf', 'version': '1.0.0'}, legacy),
                         'unstripped')
        with self.assertRaises(ValueError):
            select_build_profile({'file_name': 'settings.elf', 'version': '1.0.1'}, legacy)
        with self.assertRaises(ValueError):
            build_profile_arguments('unknown')

    def test_three_way_conflict_preservation(self):
        for base, local, upstream, state in [('a','a','a','unchanged'), ('a','b','b','converged'),
                                            ('a','a','b','upstream-only'), ('a','b','a','external-only'),
                                            ('a','b','c','conflict')]:
            self.assertEqual(classify(base, local, upstream), state)

    def test_git_blob_identity(self):
        self.assertEqual(git_blob(b''), 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')

    def test_all_app_manifests(self):
        for app in json.loads((ROOT / 'mcu-dev-tools-manifest.json').read_text())['tools']:
            self.assertEqual(app['source'], app['source_path'])
            self.assertEqual(app['manifest'], app['manifest_path'])
            source = ROOT / app['source_path']
            validate_manifest(source, pathlib.Path(app['file_name']))
            self.assertEqual(json.loads(source.with_suffix('.json').read_text())['version'], app['version'])

    def test_unknown_import_rejected(self):
        with self.assertRaises(ValueError):
            validate_imports(' 1: 00000000 0 FUNC GLOBAL DEFAULT UND privileged_unsafe', {'printf'})
        with self.assertRaises(ValueError):
            validate_imports(' 1: 00000000 0 FUNC WEAK DEFAULT UND privileged_unsafe', {'printf'})
        self.assertEqual(validate_imports(' 1: 00000000 0 FUNC GLOBAL DEFAULT UND printf', {'printf'}), {'printf'})

    def test_stamped_artifact_cannot_silently_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            elf = pathlib.Path(tmp) / 'sample.elf'
            elf.write_bytes(b'x' * 64)
            stamped = stamp_app_manifest({'file_name': elf.name, 'version': '1.0.0'}, elf)
            self.assertEqual(stamped['size_bytes'], 64)
            elf.write_bytes(b'y' * 64)
            with self.assertRaises(ValueError):
                stamp_app_manifest(stamped, elf)

    def test_inventory_cannot_escape_output_or_collide(self):
        good = {'id': 'settings', 'source_path': 'Apps/settings.c',
                'manifest_path': 'Apps/settings.json', 'file_name': 'settings.elf'}
        self.assertEqual(validate_inventory([good]), [good])
        for field, value in [('id', '../settings'), ('source_path', '../settings.c'),
                             ('manifest_path', '/tmp/settings.json'),
                             ('file_name', '../../settings.elf')]:
            with self.assertRaises(ValueError):
                validate_inventory([{**good, field: value}])
        with self.assertRaises(ValueError):
            validate_inventory([good, good])
        with self.assertRaises(ValueError):
            validate_inventory([{**good, 'additional_sources': [{'path': '../../unsafe.h'}]}])

    def test_release_parity_uses_actual_bytes_and_version(self):
        data = b'artifact'
        expected = {'version': '1.0.0', 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        self.assertTrue(compare(expected, {'version': '1.0.0'}, data))
        self.assertFalse(compare(expected, {'version': '1.0.1'}, data))
        self.assertFalse(compare(expected, {'version': '1.0.0'}, b'changed!'))

    def test_release_report_cannot_hide_nonrequired_apps(self):
        rows = [{'id': 'one', 'file_name': 'one.elf'}, {'id': 'two', 'file_name': 'two.elf'}]
        baseline = {'apps': rows, 'required_byte_parity': ['one']}
        validate_cohort(baseline, {'apps': rows}, {'tools': rows})
        for invalid in [rows[:1], rows + [rows[0]]]:
            with self.assertRaises(ValueError):
                validate_cohort(baseline, {'apps': invalid}, {'tools': rows})
        with self.assertRaises(ValueError):
            validate_cohort(baseline, {'apps': [{**rows[0], 'file_name': '../one.elf'}, rows[1]]}, {'tools': rows})

    def test_bad_manifest_name_rejected(self):
        with self.assertRaises(ValueError):
            validate_manifest(ROOT / 'Apps/usb_debug.c', pathlib.Path('wrong.elf'))


if __name__ == '__main__':
    unittest.main()
