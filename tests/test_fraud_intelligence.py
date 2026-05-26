import pytest
from PIL import Image
import io
from app.modules.fraud_intelligence.phash_matcher import FraudIntelligenceEngine
from app.modules.fraud_intelligence.schemas import FraudFingerprint

def generate_dummy_image_bytes(color="red") -> bytes:
    """Helper to generate an in-memory image for testing."""
    img = Image.new('RGB', (100, 100), color=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_generate_phash():
    engine = FraudIntelligenceEngine()
    img_bytes = generate_dummy_image_bytes()
    phash = engine.generate_phash(img_bytes)
    assert phash is not None
    assert len(phash) == 16 # hex string length for 64-bit hash

def test_matching_logic():
    engine = FraudIntelligenceEngine(exact_match_threshold=5)
    
    # Generate an image and its hash
    img_bytes = generate_dummy_image_bytes(color="blue")
    input_hash = engine.generate_phash(img_bytes)
    
    # Mock a database with the same image
    db = [
        FraudFingerprint(
            phash=input_hash,
            fraud_type="Test Fraud"
        ),
        FraudFingerprint(
            phash="0000000000000000",
            fraud_type="Irrelevant"
        )
    ]
    
    matches = engine.find_matches(input_hash, db)
    
    assert len(matches) == 1
    assert matches[0].fraud_type == "Test Fraud"
    assert matches[0].hamming_distance == 0
    assert matches[0].match_confidence == 1.0

def test_no_matches_above_threshold():
    engine = FraudIntelligenceEngine(exact_match_threshold=5)
    
    img_bytes = generate_dummy_image_bytes(color="green")
    input_hash = engine.generate_phash(img_bytes)
    
    db = [
        FraudFingerprint(
            phash="0000000000000000", # Completely different hash
            fraud_type="Irrelevant"
        )
    ]
    
    matches = engine.find_matches(input_hash, db)
    assert len(matches) == 0
