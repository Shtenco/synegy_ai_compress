import unittest

from federation.archive_manifest import FederationArchiveManifest


class FederationArchiveAdapterTests(unittest.TestCase):
    def test_reencoding_preserves_semantic_digest(self):
        canonical = b"same authoritative content"
        first = FederationArchiveManifest.from_bytes(
            object_id="obj-a",
            object_class="BENCHMARK_EVIDENCE",
            producer_repo="Shtenco/midas_ai",
            semantic_owner_repo="Shtenco/midas_ai",
            canonical_bytes=canonical,
            archive_bytes=b"SGH1-encoded",
            codec_id="GabrielHorn-SGH1",
            codec_version="1",
            storage_tier="COLD_IMMUTABLE_ARCHIVE",
        )
        second = FederationArchiveManifest.from_bytes(
            object_id="obj-a-reencoded",
            object_class="BENCHMARK_EVIDENCE",
            producer_repo="Shtenco/midas_ai",
            semantic_owner_repo="Shtenco/midas_ai",
            canonical_bytes=canonical,
            archive_bytes=b"GRAAL-encoded",
            codec_id="GRAAL-IGC",
            codec_version="1",
            storage_tier="COLD_IMMUTABLE_ARCHIVE",
        )
        self.assertEqual(first.canonical_content_sha256, second.canonical_content_sha256)
        self.assertNotEqual(first.archive_sha256, second.archive_sha256)
        self.assertEqual(first.semantic_authority, "NONE")
        self.assertTrue(first.verify_decoded(canonical))
        self.assertFalse(first.verify_archive(b"tampered"))


if __name__ == "__main__":
    unittest.main()
