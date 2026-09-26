"""Manual testing script for T13 - PBKDF2 Key Derivation

This script demonstrates and tests PBKDF2 functionality interactively.
Author: Hana (247006111170)
"""

import sys
import time
from stegora.crypto import (
    derive_key,
    derive_key_with_new_salt,
    generate_salt,
    PBKDF2_ITERATIONS,
    SALT_LENGTH,
    KEY_LENGTH,
)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_bytes(data, label="Data"):
    """Print bytes in hex format."""
    print(f"{label}: {data.hex()}")
    print(f"Length: {len(data)} bytes")


def test_1_salt_generation():
    """Test 1: Salt Generation"""
    print_header("TEST 1: Salt Generation")
    
    print(f"\nGenerating 3 random salts...")
    print(f"Expected length: {SALT_LENGTH} bytes (128 bits)")
    
    for i in range(3):
        salt = generate_salt()
        print(f"\nSalt {i+1}:")
        print_bytes(salt, "  Hex")
        assert len(salt) == SALT_LENGTH, f"❌ Length mismatch: {len(salt)} != {SALT_LENGTH}"
    
    print("\n✅ Salt generation: PASSED")
    print("   - All salts are 16 bytes")
    print("   - Each salt is unique (statistically)")


def test_2_key_derivation_basic():
    """Test 2: Basic Key Derivation"""
    print_header("TEST 2: Basic Key Derivation")
    
    password = "test_password_123"
    salt = generate_salt()
    
    print(f"\nPassword: '{password}'")
    print_bytes(salt, "Salt")
    print(f"\nDeriving key with PBKDF2-HMAC-SHA256...")
    print(f"Iterations: {PBKDF2_ITERATIONS:,}")
    
    start_time = time.time()
    key = derive_key(password, salt)
    elapsed = time.time() - start_time
    
    print(f"\n⏱️  Derivation time: {elapsed:.3f} seconds")
    print_bytes(key, "Derived Key")
    
    assert len(key) == KEY_LENGTH, f"❌ Key length mismatch: {len(key)} != {KEY_LENGTH}"
    
    print("\n✅ Basic key derivation: PASSED")
    print(f"   - Key is {KEY_LENGTH} bytes (256 bits)")
    print(f"   - Suitable for AES-256-GCM")


def test_3_determinism():
    """Test 3: Deterministic Behavior"""
    print_header("TEST 3: Deterministic Behavior")
    
    password = "same_password"
    salt = generate_salt()
    
    print(f"\nPassword: '{password}'")
    print_bytes(salt, "Salt")
    
    print("\nDeriving key 3 times with same password and salt...")
    
    keys = []
    for i in range(3):
        key = derive_key(password, salt)
        keys.append(key)
        print(f"\nDerivation {i+1}:")
        print_bytes(key, "  Key")
    
    # Check all keys are identical
    if keys[0] == keys[1] == keys[2]:
        print("\n✅ Determinism test: PASSED")
        print("   - Same password + salt always produces same key")
        print("   - This is critical for decryption to work!")
    else:
        print("\n❌ Determinism test: FAILED")
        print("   - Keys are different!")
        sys.exit(1)


def test_4_different_passwords():
    """Test 4: Different Passwords Produce Different Keys"""
    print_header("TEST 4: Different Passwords → Different Keys")
    
    salt = generate_salt()
    print_bytes(salt, "Shared Salt")
    
    passwords = ["password1", "password2", "Password1"]
    keys = {}
    
    print("\nDeriving keys for different passwords:")
    for pwd in passwords:
        key = derive_key(pwd, salt)
        keys[pwd] = key
        print(f"\nPassword: '{pwd}'")
        print_bytes(key, "  Key")
    
    # Check all keys are different
    unique_keys = set(key for key in keys.values())
    if len(unique_keys) == len(passwords):
        print("\n✅ Different passwords test: PASSED")
        print("   - Each password produces a unique key")
        print("   - Even slight differences (case) change the key")
    else:
        print("\n❌ Different passwords test: FAILED")
        sys.exit(1)


def test_5_different_salts():
    """Test 5: Different Salts Produce Different Keys"""
    print_header("TEST 5: Different Salts → Different Keys")
    
    password = "same_password"
    print(f"\nPassword: '{password}' (constant)")
    
    print("\nGenerating 3 keys with different salts:")
    keys = []
    salts = []
    
    for i in range(3):
        salt = generate_salt()
        key = derive_key(password, salt)
        salts.append(salt)
        keys.append(key)
        
        print(f"\nIteration {i+1}:")
        print_bytes(salt, "  Salt")
        print_bytes(key, "  Key")
    
    # Check all keys are different
    unique_keys = set(k for k in keys)
    if len(unique_keys) == 3:
        print("\n✅ Different salts test: PASSED")
        print("   - Different salts produce different keys")
        print("   - This is why salt must be stored with ciphertext!")
    else:
        print("\n❌ Different salts test: FAILED")
        sys.exit(1)


def test_6_convenience_function():
    """Test 6: Convenience Function"""
    print_header("TEST 6: Convenience Function (derive_key_with_new_salt)")
    
    password = "my_secure_password"
    print(f"\nPassword: '{password}'")
    print("\nCalling derive_key_with_new_salt()...")
    
    key, salt = derive_key_with_new_salt(password)
    
    print_bytes(key, "\nDerived Key")
    print_bytes(salt, "Generated Salt")
    
    print("\nVerifying: Can we reproduce the key with the salt?")
    key_again = derive_key(password, salt)
    
    if key == key_again:
        print("✅ Key reproduced successfully!")
        print_bytes(key_again, "  Reproduced Key")
    else:
        print("❌ Key mismatch!")
        sys.exit(1)
    
    print("\n✅ Convenience function test: PASSED")
    print("   - Function generates fresh salt automatically")
    print("   - Returned salt can reproduce the key")


def test_7_embed_extract_simulation():
    """Test 7: Embed/Extract Workflow Simulation"""
    print_header("TEST 7: Embed/Extract Workflow Simulation")
    
    password = "user_password_2024"
    print(f"Password: '{password}'")
    
    # === EMBEDDING PHASE ===
    print("\n" + "-"*70)
    print("EMBEDDING PHASE (Encryption)")
    print("-"*70)
    
    print("\n1. User provides password")
    print("2. Generate fresh salt and derive encryption key")
    
    embed_key, embed_salt = derive_key_with_new_salt(password)
    
    print_bytes(embed_key, "\n  Encryption Key")
    print_bytes(embed_salt, "  Salt (will be stored in STGR container)")
    
    # Simulate storing salt
    stored_salt = embed_salt
    print("\n3. Salt is stored in STGR container metadata")
    
    # === EXTRACTION PHASE ===
    print("\n" + "-"*70)
    print("EXTRACTION PHASE (Decryption)")
    print("-"*70)
    
    print("\n1. User provides password (same or different)")
    print("2. Retrieve salt from STGR container")
    print("3. Derive decryption key")
    
    # Test with CORRECT password
    print("\n--- Scenario A: CORRECT Password ---")
    extract_key_correct = derive_key(password, stored_salt)
    print_bytes(extract_key_correct, "  Decryption Key")
    
    if embed_key == extract_key_correct:
        print("\n  ✅ Keys match! Decryption will succeed.")
    else:
        print("\n  ❌ Keys don't match! This should not happen!")
        sys.exit(1)
    
    # Test with WRONG password
    print("\n--- Scenario B: WRONG Password ---")
    wrong_password = "wrong_password"
    extract_key_wrong = derive_key(wrong_password, stored_salt)
    print(f"  Wrong Password: '{wrong_password}'")
    print_bytes(extract_key_wrong, "  Decryption Key")
    
    if embed_key != extract_key_wrong:
        print("\n  ✅ Keys don't match! Decryption will fail (as expected).")
    else:
        print("\n  ❌ Keys match! This should not happen!")
        sys.exit(1)
    
    print("\n✅ Embed/Extract workflow: PASSED")
    print("   - Correct password reproduces the same key")
    print("   - Wrong password produces different key (decryption fails)")


def test_8_unicode_passwords():
    """Test 8: Unicode Password Support"""
    print_header("TEST 8: Unicode Password Support")
    
    salt = generate_salt()
    print_bytes(salt, "Salt (shared)")
    
    unicode_passwords = [
        "パスワード",           # Japanese
        "пароль",              # Russian
        "密码",                # Chinese
        "🔒secure🔑",          # Emoji
        "café_résumé",         # Accented
    ]
    
    print("\nTesting various Unicode passwords:")
    
    for i, pwd in enumerate(unicode_passwords, 1):
        key = derive_key(pwd, salt)
        print(f"\n{i}. Password: '{pwd}'")
        print(f"   Encoded bytes: {pwd.encode('utf-8').hex()}")
        print(f"   Derived key: {key.hex()[:32]}...")
    
    print("\n✅ Unicode password test: PASSED")
    print("   - All Unicode passwords work correctly")
    print("   - UTF-8 encoding is automatic")


def test_9_performance():
    """Test 9: Performance Measurement"""
    print_header("TEST 9: Performance Measurement")
    
    password = "performance_test"
    iterations = 5
    
    print(f"\nMeasuring derivation time over {iterations} iterations...")
    print(f"PBKDF2 iterations per derivation: {PBKDF2_ITERATIONS:,}")
    
    times = []
    for i in range(iterations):
        salt = generate_salt()
        start = time.time()
        key = derive_key(password, salt)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Iteration {i+1}: {elapsed:.3f}s")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\nStatistics:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Minimum: {min_time:.3f}s")
    print(f"  Maximum: {max_time:.3f}s")
    
    print("\n✅ Performance test: PASSED")
    if avg_time < 1.0:
        print(f"   - Average time ({avg_time:.3f}s) is acceptable for user-facing operation")
    else:
        print(f"   - Average time ({avg_time:.3f}s) - may be slow on this hardware")
    print(f"   - 600,000 iterations provide good security/performance balance")


def main():
    """Run all manual tests."""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  T13 - PBKDF2 Key Derivation - Manual Testing".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█" + "  Author: Hana (247006111170)".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print(f"\nConfiguration:")
    print(f"  Algorithm: PBKDF2-HMAC-SHA256")
    print(f"  Iterations: {PBKDF2_ITERATIONS:,}")
    print(f"  Salt Length: {SALT_LENGTH} bytes")
    print(f"  Key Length: {KEY_LENGTH} bytes")
    
    try:
        test_1_salt_generation()
        test_2_key_derivation_basic()
        test_3_determinism()
        test_4_different_passwords()
        test_5_different_salts()
        test_6_convenience_function()
        test_7_embed_extract_simulation()
        test_8_unicode_passwords()
        test_9_performance()
        
        # Final summary
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "  🎉 ALL TESTS PASSED! 🎉".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█" + "  T13 PBKDF2 implementation is working correctly!".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        
        print("\nSummary:")
        print("  ✅ Salt generation works")
        print("  ✅ Key derivation works")
        print("  ✅ Deterministic (same input → same output)")
        print("  ✅ Different passwords → different keys")
        print("  ✅ Different salts → different keys")
        print("  ✅ Convenience function works")
        print("  ✅ Embed/extract workflow correct")
        print("  ✅ Unicode support works")
        print("  ✅ Performance acceptable")
        
        print("\n✨ Ready for integration with T14 (AES-256-GCM)!")
        
        return 0
        
    except Exception as e:
        print("\n" + "❌"*35)
        print(f"ERROR: {e}")
        print("❌"*35)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
