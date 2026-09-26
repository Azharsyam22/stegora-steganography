"""Interactive manual testing for T13 - PBKDF2 Key Derivation

Run this script and input your own passwords to test the PBKDF2 implementation.
Author: Hana (247006111170)
"""

import sys
from stegora.crypto import (
    derive_key,
    derive_key_with_new_salt,
    generate_salt,
    PBKDF2_ITERATIONS,
)


def print_separator():
    print("\n" + "="*70 + "\n")


def print_bytes_nice(data, label=""):
    """Print bytes in a nice formatted way."""
    if label:
        print(f"{label}:")
    print(f"  Hex: {data.hex()}")
    print(f"  Length: {len(data)} bytes")


def menu():
    """Show interactive menu."""
    print("\n" + "█"*70)
    print("█  T13 - PBKDF2 Interactive Testing                                 █")
    print("█  Author: Hana (247006111170)                                      █")
    print("█"*70)
    print("\nPilih test yang ingin dijalankan:\n")
    print("  1. Generate Salt (random)")
    print("  2. Derive Key (input password + salt)")
    print("  3. Derive Key with New Salt (input password)")
    print("  4. Test Determinism (same password + salt → same key)")
    print("  5. Test Different Passwords (compare 2 passwords)")
    print("  6. Simulate Embed/Extract Workflow")
    print("  7. Test Your Own Password")
    print("  8. Compare Multiple Passwords")
    print("  9. View Configuration")
    print("  0. Exit")
    print("\n" + "-"*70)


def test_1_generate_salt():
    """Test 1: Generate random salt."""
    print_separator()
    print("TEST 1: Generate Random Salt")
    print_separator()
    
    try:
        count = input("Berapa salt yang ingin di-generate? (default: 3): ").strip()
        count = int(count) if count else 3
    except ValueError:
        count = 3
    
    print(f"\nGenerating {count} random salt(s)...\n")
    
    salts = []
    for i in range(count):
        salt = generate_salt()
        salts.append(salt)
        print(f"Salt #{i+1}:")
        print_bytes_nice(salt)
        print()
    
    # Check uniqueness
    if len(set(salts)) == len(salts):
        print("✅ All salts are unique!")
    else:
        print("⚠️  Warning: Some salts are identical (very unlikely!)")
    
    input("\nPress Enter to continue...")


def test_2_derive_key():
    """Test 2: Derive key with user input."""
    print_separator()
    print("TEST 2: Derive Key from Password + Salt")
    print_separator()
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "default_password"
        print(f"Using default: '{password}'")
    
    print("\nPilih salt:")
    print("  1. Generate salt baru (random)")
    print("  2. Input salt manual (hex)")
    
    choice = input("Pilihan (1/2, default: 1): ").strip()
    
    if choice == "2":
        salt_hex = input("Masukkan salt (32 hex chars, 16 bytes): ").strip()
        try:
            salt = bytes.fromhex(salt_hex)
            if len(salt) != 16:
                print(f"⚠️  Salt harus 16 bytes, got {len(salt)}. Using random salt.")
                salt = generate_salt()
        except ValueError:
            print("⚠️  Invalid hex. Using random salt.")
            salt = generate_salt()
    else:
        salt = generate_salt()
    
    print("\n" + "-"*70)
    print("DERIVING KEY...")
    print("-"*70)
    print(f"Password: '{password}'")
    print_bytes_nice(salt, "Salt")
    print(f"\nRunning PBKDF2-HMAC-SHA256 with {PBKDF2_ITERATIONS:,} iterations...")
    
    import time
    start = time.time()
    key = derive_key(password, salt)
    elapsed = time.time() - start
    
    print(f"⏱️  Time: {elapsed:.3f} seconds\n")
    print_bytes_nice(key, "Derived Key")
    
    print("\n✅ Key derivation successful!")
    print(f"This key can be used for AES-256-GCM encryption.")
    
    input("\nPress Enter to continue...")


def test_3_derive_with_new_salt():
    """Test 3: Convenience function."""
    print_separator()
    print("TEST 3: Derive Key with Auto-Generated Salt")
    print_separator()
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "default_password"
        print(f"Using default: '{password}'")
    
    print("\n" + "-"*70)
    print("DERIVING KEY WITH NEW SALT...")
    print("-"*70)
    print(f"Password: '{password}'")
    print(f"\nRunning PBKDF2-HMAC-SHA256 with {PBKDF2_ITERATIONS:,} iterations...")
    
    import time
    start = time.time()
    key, salt = derive_key_with_new_salt(password)
    elapsed = time.time() - start
    
    print(f"⏱️  Time: {elapsed:.3f} seconds\n")
    print_bytes_nice(key, "Derived Key")
    print_bytes_nice(salt, "Generated Salt")
    
    print("\n💡 IMPORTANT:")
    print("   Salt ini harus disimpan bersama ciphertext!")
    print("   Tanpa salt ini, decryption tidak bisa dilakukan.")
    
    input("\nPress Enter to continue...")


def test_4_determinism():
    """Test 4: Test deterministic behavior."""
    print_separator()
    print("TEST 4: Test Determinism")
    print_separator()
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "test_password"
        print(f"Using default: '{password}'")
    
    salt = generate_salt()
    
    print("\n" + "-"*70)
    print("TESTING DETERMINISM...")
    print("-"*70)
    print(f"Password: '{password}'")
    print_bytes_nice(salt, "Salt")
    
    try:
        count = input("\nBerapa kali derive key? (default: 3): ").strip()
        count = int(count) if count else 3
    except ValueError:
        count = 3
    
    print(f"\nDeriving key {count} times with same password and salt...\n")
    
    keys = []
    for i in range(count):
        key = derive_key(password, salt)
        keys.append(key)
        print(f"Derivation #{i+1}: {key.hex()[:32]}...")
    
    # Check if all keys are identical
    if len(set(keys)) == 1:
        print("\n✅ DETERMINISTIC!")
        print("   All keys are IDENTICAL.")
        print("   Same password + salt always produces same key.")
        print("   This is CRITICAL for decryption to work!")
    else:
        print("\n❌ NOT DETERMINISTIC!")
        print("   Keys are different! This should not happen!")
    
    input("\nPress Enter to continue...")


def test_5_different_passwords():
    """Test 5: Compare different passwords."""
    print_separator()
    print("TEST 5: Compare Two Different Passwords")
    print_separator()
    
    password1 = input("\nMasukkan password pertama: ")
    password2 = input("Masukkan password kedua: ")
    
    if not password1:
        password1 = "password1"
        print(f"Using default password1: '{password1}'")
    if not password2:
        password2 = "password2"
        print(f"Using default password2: '{password2}'")
    
    # Use same salt for fair comparison
    salt = generate_salt()
    
    print("\n" + "-"*70)
    print("COMPARING PASSWORDS...")
    print("-"*70)
    print_bytes_nice(salt, "Shared Salt")
    
    print(f"\nPassword 1: '{password1}'")
    key1 = derive_key(password1, salt)
    print_bytes_nice(key1, "  Key 1")
    
    print(f"\nPassword 2: '{password2}'")
    key2 = derive_key(password2, salt)
    print_bytes_nice(key2, "  Key 2")
    
    print("\n" + "-"*70)
    if key1 == key2:
        print("⚠️  KEYS ARE IDENTICAL!")
        print("   The passwords might be the same.")
    else:
        print("✅ KEYS ARE DIFFERENT!")
        print("   Different passwords produce different keys.")
        print("   This ensures security - wrong password = wrong key.")
    
    input("\nPress Enter to continue...")


def test_6_embed_extract():
    """Test 6: Simulate embed/extract workflow."""
    print_separator()
    print("TEST 6: Simulate Embed/Extract Workflow")
    print_separator()
    
    password = input("\nMasukkan password untuk embedding: ")
    if not password:
        password = "secure_password_123"
        print(f"Using default: '{password}'")
    
    # === EMBEDDING PHASE ===
    print("\n" + "█"*70)
    print("█  PHASE 1: EMBEDDING (Encryption)")
    print("█"*70)
    
    print("\n1. User provides password")
    print("2. Generate fresh salt and derive encryption key")
    
    embed_key, embed_salt = derive_key_with_new_salt(password)
    
    print_bytes_nice(embed_key, "\n  Encryption Key")
    print_bytes_nice(embed_salt, "  Salt")
    
    print("\n3. ✅ Salt akan disimpan dalam STGR container")
    print("4. ✅ Key digunakan untuk encrypt pesan dengan AES-256-GCM")
    
    # Store salt (simulate)
    stored_salt = embed_salt
    stored_salt_hex = embed_salt.hex()
    
    input("\n[Embedding complete] Press Enter to continue to extraction...")
    
    # === EXTRACTION PHASE ===
    print("\n" + "█"*70)
    print("█  PHASE 2: EXTRACTION (Decryption)")
    print("█"*70)
    
    print("\n1. User provides password")
    print("2. Salt retrieved from STGR container")
    print(f"   Salt: {stored_salt_hex}")
    
    extract_password = input("\nMasukkan password untuk extraction: ")
    if not extract_password:
        extract_password = password
        print(f"Using same password: '{extract_password}'")
    
    print("\n3. Derive decryption key from password + stored salt")
    extract_key = derive_key(extract_password, stored_salt)
    
    print_bytes_nice(extract_key, "\n  Decryption Key")
    
    # Compare keys
    print("\n" + "-"*70)
    print("VERIFICATION:")
    print("-"*70)
    
    if embed_key == extract_key:
        print("✅ KEYS MATCH!")
        print("   Encryption key == Decryption key")
        print("   ✅ Decryption will SUCCEED")
        print("   ✅ Original message can be recovered")
    else:
        print("❌ KEYS DON'T MATCH!")
        print("   Encryption key ≠ Decryption key")
        print("   ❌ Decryption will FAIL")
        print("   ❌ Wrong password or corrupted salt")
        print("\n💡 This is expected if you entered a different password.")
    
    input("\nPress Enter to continue...")


def test_7_your_password():
    """Test 7: Test your own password."""
    print_separator()
    print("TEST 7: Test Your Own Password")
    print_separator()
    
    print("\nTest password Anda sendiri dengan PBKDF2!")
    print("Anda bisa lihat berapa lama derivation dan hasil key-nya.\n")
    
    password = input("Masukkan password Anda: ")
    if not password:
        print("❌ Password tidak boleh kosong!")
        input("\nPress Enter to continue...")
        return
    
    print(f"\nPassword: '{password}'")
    print(f"Length: {len(password)} characters")
    print(f"Bytes: {len(password.encode('utf-8'))} bytes (UTF-8)")
    
    confirm = input("\nDerive key dengan password ini? (y/n, default: y): ").lower()
    if confirm and confirm != 'y':
        print("Cancelled.")
        input("\nPress Enter to continue...")
        return
    
    print("\n" + "-"*70)
    print("DERIVING KEY...")
    print("-"*70)
    
    import time
    start = time.time()
    key, salt = derive_key_with_new_salt(password)
    elapsed = time.time() - start
    
    print(f"\n⏱️  Derivation time: {elapsed:.3f} seconds")
    print(f"💪 {PBKDF2_ITERATIONS:,} PBKDF2 iterations completed!")
    
    print_bytes_nice(key, "\nDerived Key")
    print_bytes_nice(salt, "Salt")
    
    print("\n✅ Your password has been successfully derived into a 256-bit key!")
    print("   This key can be used for AES-256-GCM encryption.")
    
    # Security check
    print("\n" + "-"*70)
    print("PASSWORD STRENGTH NOTES:")
    print("-"*70)
    if len(password) < 8:
        print("⚠️  Short password (< 8 chars) - consider using longer password")
    elif len(password) < 12:
        print("✓  Acceptable length")
    else:
        print("✅ Good length!")
    
    if password.isalnum():
        print("💡 Consider adding special characters for stronger password")
    else:
        print("✅ Contains special characters")
    
    input("\nPress Enter to continue...")


def test_8_compare_multiple():
    """Test 8: Compare multiple passwords."""
    print_separator()
    print("TEST 8: Compare Multiple Passwords")
    print_separator()
    
    try:
        count = input("\nBerapa password yang ingin dibandingkan? (default: 3): ").strip()
        count = int(count) if count else 3
        if count < 2:
            count = 2
        if count > 10:
            count = 10
    except ValueError:
        count = 3
    
    print(f"\nMasukkan {count} password untuk dibandingkan:\n")
    
    passwords = []
    for i in range(count):
        pwd = input(f"Password #{i+1}: ")
        if not pwd:
            pwd = f"password{i+1}"
            print(f"  Using default: '{pwd}'")
        passwords.append(pwd)
    
    # Use same salt for fair comparison
    salt = generate_salt()
    
    print("\n" + "-"*70)
    print("DERIVING KEYS...")
    print("-"*70)
    print_bytes_nice(salt, "Shared Salt")
    
    keys = {}
    for i, pwd in enumerate(passwords, 1):
        print(f"\nPassword #{i}: '{pwd}'")
        key = derive_key(pwd, salt)
        keys[pwd] = key
        print(f"  Key: {key.hex()[:48]}...")
    
    # Check uniqueness
    unique_keys = len(set(keys.values()))
    print("\n" + "-"*70)
    print("ANALYSIS:")
    print("-"*70)
    print(f"Total passwords: {len(passwords)}")
    print(f"Unique keys: {unique_keys}")
    
    if unique_keys == len(passwords):
        print("\n✅ All keys are UNIQUE!")
        print("   Each password produced a different key.")
    else:
        print("\n⚠️  Some keys are IDENTICAL!")
        print("   Some passwords might be the same.")
        
        # Find duplicates
        from collections import Counter
        key_counts = Counter(keys.values())
        duplicates = [key for key, count in key_counts.items() if count > 1]
        
        if duplicates:
            print("\n   Duplicate keys found for:")
            for dup_key in duplicates:
                dup_passwords = [pwd for pwd, k in keys.items() if k == dup_key]
                print(f"     - {', '.join(dup_passwords)}")
    
    input("\nPress Enter to continue...")


def test_9_config():
    """Test 9: Show configuration."""
    print_separator()
    print("CONFIGURATION")
    print_separator()
    
    print("\nT13 - PBKDF2 Key Derivation Configuration:")
    print("\n  Algorithm: PBKDF2-HMAC-SHA256")
    print(f"  Iterations: {PBKDF2_ITERATIONS:,}")
    print(f"  Salt Length: 16 bytes (128 bits)")
    print(f"  Key Length: 32 bytes (256 bits)")
    print(f"  Randomness: secrets.token_bytes() (cryptographically secure)")
    
    print("\n" + "-"*70)
    print("SECURITY PROPERTIES:")
    print("-"*70)
    print("  ✓ Deterministic: same password + salt → same key")
    print("  ✓ Salt randomness: fresh salt for each operation")
    print("  ✓ Key uniqueness: different password/salt → different key")
    print(f"  ✓ Computation cost: {PBKDF2_ITERATIONS:,} iterations (slow brute-force)")
    print("  ✓ Output size: 256 bits (suitable for AES-256-GCM)")
    
    print("\n" + "-"*70)
    print("DESIGN RATIONALE:")
    print("-"*70)
    print("  • 600,000 iterations: Project design choice")
    print("    - OWASP 2023: minimum 310,000 for PBKDF2-SHA256")
    print("    - NIST SP 800-63B: minimum 10,000")
    print("    - Good balance: security vs performance")
    print("\n  • 16-byte salt: NIST recommendation")
    print("    - 2^128 possible values")
    print("    - Prevents rainbow table attacks")
    print("\n  • PBKDF2-HMAC-SHA256:")
    print("    - Specified in assignment brief")
    print("    - Industry standard (RFC 2898)")
    print("    - Built into cryptography library")
    
    input("\nPress Enter to continue...")


def main():
    """Main interactive loop."""
    while True:
        menu()
        choice = input("Pilih menu (0-9): ").strip()
        
        if choice == '0':
            print("\n✨ Terima kasih sudah testing T13!")
            print("💪 PBKDF2 implementation ready for T14 (AES-256-GCM)!\n")
            break
        elif choice == '1':
            test_1_generate_salt()
        elif choice == '2':
            test_2_derive_key()
        elif choice == '3':
            test_3_derive_with_new_salt()
        elif choice == '4':
            test_4_determinism()
        elif choice == '5':
            test_5_different_passwords()
        elif choice == '6':
            test_6_embed_extract()
        elif choice == '7':
            test_7_your_password()
        elif choice == '8':
            test_8_compare_multiple()
        elif choice == '9':
            test_9_config()
        else:
            print("\n❌ Pilihan tidak valid. Silakan pilih 0-9.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Testing dibatalkan. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
