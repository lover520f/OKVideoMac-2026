#!/usr/bin/env python3
"""Regression gates for private release configuration; uses no network or real DSN."""
from pathlib import Path
import importlib.util
import io
import os
import plistlib
import subprocess
import sys
import tarfile
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "OKVideoMac/macOS/OKVideoMac/Scripts/configure-crash-reporting.py"
spec = importlib.util.spec_from_file_location("crash_configuration", SCRIPT)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
scan_spec = importlib.util.spec_from_file_location("release_scan", REPO / "Tools/SourceAudit/scan_release_artifacts.py")
scan = importlib.util.module_from_spec(scan_spec)
scan_spec.loader.exec_module(scan)
DSN = "https://public@example.invalid/1"

class ReleaseCrashConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="OKCrashReleaseConfig-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        self.private = self.root / "app.env"
        self.private.write_text("# Public ingest configuration only\nSENTRY_DSN=" + DSN + "\n")
        self.private.chmod(0o600)
        self.app = self.root / "OKVideoMac.app"
        (self.app / "Contents").mkdir(parents=True)
        self.info = self.app / "Contents/Info.plist"
        self.info.write_bytes(plistlib.dumps({"CFBundleVersion":"139", config.KEY:""}))

    def testPrivateReleaseInputInjectsOnlyPublicDSN(self):
        value=config.expected_dsn("distribution", self.private, self.checkout)
        config.apply(self.app,value)
        info=plistlib.loads(self.info.read_bytes())
        self.assertEqual(info, {"CFBundleVersion":"139",config.KEY:DSN})
        self.assertEqual(self.private.stat().st_mode & 0o777,0o600)

    def testLocalPackageClearsAnInheritedEndpoint(self):
        config.apply(self.app,DSN)
        config.apply(self.app,config.expected_dsn("local",None,self.checkout))
        self.assertEqual(plistlib.loads(self.info.read_bytes())[config.KEY],"")

    def testDistributionCannotSilentlyOmitUploadConfiguration(self):
        with self.assertRaises(ValueError): config.expected_dsn("distribution",None,self.checkout)

    def testLocalCannotAccidentallyUseProductionConfiguration(self):
        with self.assertRaises(ValueError): config.expected_dsn("local",self.private,self.checkout)

    def testRejectConfigurationInsideCheckout(self):
        inside=self.checkout/"ignored.env";inside.write_bytes(self.private.read_bytes());inside.chmod(0o600)
        with self.assertRaises(ValueError): config.configuration(inside,self.checkout)

    def testRejectGroupReadableFile(self):
        self.private.chmod(0o640)
        with self.assertRaises(ValueError): config.configuration(self.private,self.checkout)

    def testRejectSymlink(self):
        link=self.root/"linked.env";link.symlink_to(self.private)
        with self.assertRaises(OSError): config.configuration(link,self.checkout)

    def testFIFOAndDirectoryFailWithoutWaiting(self):
        fifo=self.root/"pipe";os.mkfifo(fifo,0o600)
        for path in [fifo,self.root]:
            result=subprocess.run([sys.executable,str(SCRIPT),"check","--mode","distribution","--repo",str(self.checkout),"--config",str(path)],capture_output=True,text=True,timeout=3)
            self.assertEqual(result.returncode,2)

    def testUnknownDuplicateAndEmptyKeysAreRejected(self):
        for text in ["", "SENTRY_DSN=\n", "SENTRY_DSN="+DSN+"\nSENTRY_DSN="+DSN, "SENTRY_DSN="+DSN+"\nSENTRY_AUTH_TOKEN="+"A"*32]:
            self.private.write_text(text)
            with self.assertRaises(ValueError): config.configuration(self.private,self.checkout)

    def testInvalidOrSecretBearingDSNRejected(self):
        for value in ["http://public@example.invalid/1", "https://public:secret@example.invalid/1", DSN+"?token=hidden", DSN+"#", "https://public@example.invalid/no-project", "https://public@example.invalid:99999/1", "https://public@example.invalid/1\n"]:
            with self.assertRaises(ValueError): config.validate_dsn(value)

    def testValuesNeverAppearInCommandOutput(self):
        result=subprocess.run([sys.executable,str(SCRIPT),"apply","--mode","distribution","--repo",str(self.checkout),"--config",str(self.private),"--app",str(self.app)],capture_output=True,text=True,check=True)
        self.assertNotIn(DSN,result.stdout+result.stderr)
        self.private.write_text("SENTRY_DSN=https://public:DO_NOT_LOG@example.invalid/1")
        previous=self.info.read_bytes()
        result=subprocess.run([sys.executable,str(SCRIPT),"apply","--mode","distribution","--repo",str(self.checkout),"--config",str(self.private),"--app",str(self.app)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertNotIn("DO_NOT_LOG",result.stdout+result.stderr)
        self.assertEqual(self.info.read_bytes(),previous)

    def testRejectOversizedPrivateInput(self):
        self.private.write_text("#"*(config.MAX_CONFIG_BYTES+1))
        with self.assertRaises(ValueError): config.configuration(self.private,self.checkout)

    def archive(self,data):
        path=self.root/"source.tar.gz"
        with tarfile.open(path,"w:gz") as archive:
            entry=tarfile.TarInfo("source/fixture.txt");entry.size=len(data)
            archive.addfile(entry,io.BytesIO(data))
        return path

    def testSourceArchiveWithPlaceholderPasses(self):
        config.verify_sources(self.archive(b'OKVIDEOMAC_CRASH_REPORT_DSN=""'),DSN)

    def testActualDSNInArchiveFailsIncludingAcrossChunks(self):
        for data in [DSN.encode(),b"x"*(1024*1024-4)+DSN.encode()]:
            with self.assertRaises(ValueError): config.verify_sources(self.archive(data),DSN)

    def testManagementTokenScannerAndPublicDSN(self):
        for token in [b"sntrys_"+b"A"*64,b"sntryu_"+b"B"*64,b"SENTRY_AUTH_TOKEN="+b"C"*64]:
            findings=scan.scan_stream(io.BytesIO(token),"fixture",())
            self.assertTrue(findings)
            self.assertNotIn(token.decode(),str(findings))
        self.assertFalse(scan.scan_stream(io.BytesIO(DSN.encode()),"fixture",()))

if __name__=="__main__": unittest.main()
