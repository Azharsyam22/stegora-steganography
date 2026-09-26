"""Interactive manual testing for T14 - AES-256-GCM Encryption/Decryption

Run this script and input your own data to test the AES-GCM implementation.
Author: Hana (247006111170)
"""

import sys
import time
from stegora.crypto import (
    # T13 - PBKDF2
    derive_key_with_new_salt,
    derive_key,
    # T14 - AES-GCM
    encrypt,
    decrypt,
    encrypt_text,
    decrypt_text,
    generate_iv,
    IV_LENGTH,
    TAG_LENGTH,
    AuthenticationError,
    DecryptionError,
)


def print_separator():
    print("\n" + "="*70 + "\n")


def print_bytes_nice(data, label="", max_display=64):
    """Print bytes in a nice formatted way."""
    if label:
        print(f"{label}:")
    hex_str = data.hex()
    if len(hex_str) > max_display:
        print(f"  Hex: {hex_str[:max_display]}... (truncated)")
    else:
        print(f"  Hex: {hex_str}")
    print(f"  Length: {len(data)} bytes")


def menu():
    """Show interactive menu."""
    print("\n" + "█"*70)
    print("█  T14 - AES-256-GCM Interactive Testing                            █")
    print("█  Author: Hana (247006111170)                                      █")
    print("█"*70)
    print("\nPilih test yang ingin dijalankan:\n")
    print("  1. Encrypt Text Message")
    print("  2. Encrypt & Decrypt Round-Trip")
    print("  3. Test Wrong Password (Authentication Failure)")
    print("  4. Test Tampered Ciphertext")
    print("  5. Test Semantic Security (Same Text → Different Ciphertext)")
    print("  6. Complete Workflow (T13 + T14)")
    print("  7. Encrypt Binary Data")
    print("  8. Test Multiple Messages")
    print("  9. View Configuration")
    print("  0. Exit")
    print("\n" + "-"*70)


def test_1_encrypt_text():
    """Test 1: Basic text encryption."""
    print_separator()
    print("TEST 1: Encrypt Text Message")
    print_separator()
    
    # Get password
    password = input("\nMasukkan password: ")
    if not password:
        password = "default_password"
        print(f"Using default: '{password}'")
    
    # Get message
    message = input("Masukkan pesan yang ingin dienkripsi: ")
    if not message:
        message = "Hello, this is a secret message!"
        print(f"Using default: '{message}'")
    
    print("\n" + "-"*70)
    print("ENCRYPTING...")
    print("-"*70)
    
    # Derive key from password (T13)
    print("Step 1: Deriving key from password (PBKDF2)...")
    start = time.time()
    key, salt = derive_key_with_new_salt(password)
    pbkdf2_time = time.time() - start
    print(f"  ⏱️  PBKDF2 time: {pbkdf2_time:.3f}s")
    print_bytes_nice(key, "  Key", 32)
    print_bytes_nice(salt, "  Salt", 32)
    
    # Encrypt message (T14)
    print("\nStep 2: Encrypting message (AES-256-GCM)...")
    start = time.time()
    ciphertext, iv = encrypt_text(message, key)
    encrypt_time = time.time() - start
    print(f"  ⏱️  Encryption time: {encrypt_time:.4f}s")
    print_bytes_nice(iv, "  IV (Nonce)", 32)
    print_bytes_nice(ciphertext, "  Ciphertext")
    
    print("\n" + "-"*70)
    print("ENCRYPTION SUCCESSFUL!")
    print("-"*70)
    print(f"Original message length: {len(message)} chars ({len(message.encode('utf-8'))} bytes)")
    print(f"Ciphertext length: {len(ciphertext)} bytes")
    print(f"Overhead: {len(ciphertext) - len(message.encode('utf-8'))} bytes (authentication tag)")
    
    print("\n💡 IMPORTANT:")
    print("   To decrypt this message, you need:")
    print("   1. Password (for deriving key)")
    print("   2. Salt (stored with ciphertext)")
    print("   3. IV (stored with ciphertext)")
    print("   4. Ciphertext")
    
    input("\nPress Enter to continue...")


def test_2_round_trip():
    """Test 2: Complete encryption and decryption round trip."""
    print_separator()
    print("TEST 2: Encrypt & Decrypt Round-Trip")
    print_separator()
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "test_password"
        print(f"Using default: '{password}'")
    
    message = input("Masukkan pesan: ")
    if not message:
        message = "Secret message for testing!"
        print(f"Using default: '{message}'")
    
    print("\n" + "█"*70)
    print("█  PHASE 1: ENCRYPTION")
    print("█"*70)
    
    # Derive key
    print("\n1. Deriving key from password...")
    key, salt = derive_key_with_new_salt(password)
    print_bytes_nice(key, "  Key", 32)
    print_bytes_nice(salt, "  Salt", 32)
    
    # Encrypt
    print("\n2. Encrypting message...")
    ciphertext, iv = encrypt_text(message, key)
    print_bytes_nice(iv, "  IV", 32)
    print_bytes_nice(ciphertext, "  Ciphertext")
    
    print("\n✅ Encryption complete!")
    print(f"   Original: {len(message)} chars")
    print(f"   Encrypted: {len(ciphertext)} bytes")
    
    input("\n[Press Enter to continue to decryption...]")
    
    print("\n" + "█"*70)
    print("█  PHASE 2: DECRYPTION")
    print("█"*70)
    
    # Derive same key
    print("\n1. Deriving key from same password...")
    key_again = derive_key(password, salt)
    print_bytes_nice(key_again, "  Key", 32)
    
    if key == key_again:
        print("   ✅ Keys match!")
    else:
        print("   ❌ Keys don't match! (This should not happen!)")
    
    # Decrypt
    print("\n2. Decrypting ciphertext...")
    try:
        decrypted = decrypt_text(ciphertext, key_again, iv)
        print(f"  Decrypted message: '{decrypted}'")
        
        print("\n" + "-"*70)
        print("VERIFICATION:")
        print("-"*70)
        
        if decrypted == message:
            print("✅ ROUND-TRIP SUCCESSFUL!")
            print(f"   Original:  '{message}'")
            print(f"   Decrypted: '{decrypted}'")
            print("   Messages match perfectly!")
        else:
            print("❌ ROUND-TRIP FAILED!")
            print(f"   Original:  '{message}'")
            print(f"   Decrypted: '{decrypted}'")
            print("   Messages don't match!")
        
    except AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
    except Exception as e:
        print(f"❌ Decryption Error: {e}")
    
    input("\nPress Enter to continue...")


def test_3_wrong_password():
    """Test 3: Test authentication failure with wrong password."""
    print_separator()
    print("TEST 3: Wrong Password (Authentication Failure)")
    print_separator()
    
    correct_password = input("\nMasukkan password untuk enkripsi: ")
    if not correct_password:
        correct_password = "correct_password"
        print(f"Using default: '{correct_password}'")
    
    message = input("Masukkan pesan: ")
    if not message:
        message = "This is a secret!"
        print(f"Using default: '{message}'")
    
    print("\n" + "█"*70)
    print("█  ENCRYPTION with CORRECT password")
    print("█"*70)
    
    # Encrypt with correct password
    key1, salt1 = derive_key_with_new_salt(correct_password)
    ciphertext, iv = encrypt_text(message, key1)
    
    print(f"\n✅ Message encrypted with password: '{correct_password}'")
    print_bytes_nice(ciphertext, "Ciphertext")
    
    input("\n[Press Enter to attempt decryption...]")
    
    print("\n" + "█"*70)
    print("█  SCENARIO A: Decryption with CORRECT password")
    print("█"*70)
    
    print(f"\nAttempting decryption with: '{correct_password}'")
    try:
        key_correct = derive_key(correct_password, salt1)
        decrypted = decrypt_text(ciphertext, key_correct, iv)
        print(f"✅ SUCCESS! Decrypted: '{decrypted}'")
    except AuthenticationError:
        print("❌ Authentication failed!")
    
    input("\n[Press Enter for next scenario...]")
    
    print("\n" + "█"*70)
    print("█  SCENARIO B: Decryption with WRONG password")
    print("█"*70)
    
    wrong_password = input("\nMasukkan password SALAH untuk dekripsi: ")
    if not wrong_password:
        wrong_password = "wrong_password"
        print(f"Using default: '{wrong_password}'")
    
    print(f"\nAttempting decryption with: '{wrong_password}'")
    try:
        key_wrong = derive_key(wrong_password, salt1)
        decrypted = decrypt_text(ciphertext, key_wrong, iv)
        print(f"❌ UNEXPECTED! Decrypted: '{decrypted}'")
        print("   This should not happen!")
    except AuthenticationError as e:
        print("✅ EXPECTED BEHAVIOR!")
        print(f"   Authentication failed: {e}")
        print("   Wrong password was correctly detected!")
    
    input("\nPress Enter to continue...")


def test_4_tampered_ciphertext():
    """Test 4: Test tamper detection."""
    print_separator()
    print("TEST 4: Tampered Ciphertext Detection")
    print_separator()
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "password123"
        print(f"Using default: '{password}'")
    
    message = "Important data that must not be tampered!"
    print(f"Message: '{message}'")
    
    print("\n" + "-"*70)
    print("ENCRYPTING...")
    print("-"*70)
    
    # Encrypt
    key, salt = derive_key_with_new_salt(password)
    ciphertext, iv = encrypt_text(message, key)
    
    print_bytes_nice(ciphertext, "Original Ciphertext")
    
    print("\n" + "█"*70)
    print("█  SCENARIO A: Decrypt UNTAMPERED ciphertext")
    print("█"*70)
    
    try:
        decrypted = decrypt_text(ciphertext, key, iv)
        print(f"✅ SUCCESS! Decrypted: '{decrypted}'")
    except AuthenticationError:
        print("❌ Authentication failed! (Unexpected)")
    
    input("\n[Press Enter to tamper with ciphertext...]")
    
    print("\n" + "█"*70)
    print("█  SCENARIO B: Decrypt TAMPERED ciphertext")
    print("█"*70)
    
    # Tamper with ciphertext
    tampered = bytearray(ciphertext)
    tamper_position = len(tampered) // 2
    original_byte = tampered[tamper_position]
    tampered[tamper_position] ^= 0xFF  # Flip all bits
    tampered_ciphertext = bytes(tampered)
    
    print(f"\nTampering with ciphertext...")
    print(f"  Position: byte #{tamper_position}")
    print(f"  Original byte: 0x{original_byte:02x}")
    print(f"  Tampered byte: 0x{tampered[tamper_position]:02x}")
    print_bytes_nice(tampered_ciphertext, "\nTampered Ciphertext")
    
    print(f"\nAttempting to decrypt tampered ciphertext...")
    try:
        decrypted = decrypt_text(tampered_ciphertext, key, iv)
        print(f"❌ SECURITY FAILURE! Decrypted: '{decrypted}'")
        print("   Tampered ciphertext should be rejected!")
    except AuthenticationError as e:
        print("✅ EXPECTED BEHAVIOR!")
        print(f"   Authentication failed: {e}")
        print("   Tampering was detected successfully!")
        print("   AES-GCM authentication tag verification works!")
    
    input("\nPress Enter to continue...")


def test_5_semantic_security():
    """Test 5: Test semantic security."""
    print_separator()
    print("TEST 5: Semantic Security")
    print_separator()
    
    print("\nSemantic security: encrypting the same message multiple times")
    print("should produce DIFFERENT ciphertexts (due to random IV).")
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "password"
        print(f"Using default: '{password}'")
    
    message = input("Masukkan pesan: ")
    if not message:
        message = "Same message every time"
        print(f"Using default: '{message}'")
    
    try:
        count = int(input("Berapa kali enkripsi? (default: 3): ") or "3")
    except ValueError:
        count = 3
    
    print("\n" + "-"*70)
    print(f"ENCRYPTING SAME MESSAGE {count} TIMES...")
    print("-"*70)
    print(f"Message: '{message}'")
    
    # Derive key once
    key, salt = derive_key_with_new_salt(password)
    print_bytes_nice(key, "\nKey (same for all)", 32)
    
    results = []
    for i in range(count):
        ciphertext, iv = encrypt_text(message, key)
        results.append((ciphertext, iv))
        print(f"\nEncryption #{i+1}:")
        print_bytes_nice(iv, "  IV", 32)
        print_bytes_nice(ciphertext, "  Ciphertext", 64)
    
    print("\n" + "-"*70)
    print("ANALYSIS:")
    print("-"*70)
    
    # Check IV uniqueness
    ivs = [iv for _, iv in results]
    unique_ivs = len(set(ivs))
    print(f"Total encryptions: {count}")
    print(f"Unique IVs: {unique_ivs}")
    
    if unique_ivs == count:
        print("✅ All IVs are unique!")
    else:
        print("⚠️  Some IVs are repeated (very unlikely!)")
    
    # Check ciphertext uniqueness
    ciphertexts = [ct for ct, _ in results]
    unique_cts = len(set(ciphertexts))
    print(f"Unique ciphertexts: {unique_cts}")
    
    if unique_cts == count:
        print("✅ All ciphertexts are different!")
        print("   SEMANTIC SECURITY VERIFIED!")
        print("   Same plaintext → different ciphertexts")
    else:
        print("⚠️  Some ciphertexts are identical!")
    
    # Verify all decrypt to same message
    print("\nVerifying all decrypt to same message...")
    all_match = True
    for i, (ct, iv) in enumerate(results, 1):
        decrypted = decrypt_text(ct, key, iv)
        if decrypted != message:
            print(f"❌ Encryption #{i} decrypts to different message!")
            all_match = False
    
    if all_match:
        print("✅ All ciphertexts decrypt to original message!")
    
    input("\nPress Enter to continue...")


def test_6_complete_workflow():
    """Test 6: Complete T13 + T14 workflow."""
    print_separator()
    print("TEST 6: Complete Workflow (T13 PBKDF2 + T14 AES-GCM)")
    print_separator()
    
    print("\nThis test demonstrates the complete encryption workflow:")
    print("  Password → PBKDF2 → Key → AES-GCM → Ciphertext")
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "my_secure_password_2024"
        print(f"Using default: '{password}'")
    
    message = input("Masukkan pesan: ")
    if not message:
        message = "This is a complete workflow test!"
        print(f"Using default: '{message}'")
    
    print("\n" + "█"*70)
    print("█  COMPLETE ENCRYPTION WORKFLOW")
    print("█"*70)
    
    print("\n[T13] Step 1: Password-Based Key Derivation (PBKDF2)")
    print("-"*70)
    start = time.time()
    key, salt = derive_key_with_new_salt(password)
    pbkdf2_time = time.time() - start
    print(f"  Algorithm: PBKDF2-HMAC-SHA-256")
    print(f"  Iterations: 600,000")
    print(f"  Time: {pbkdf2_time:.3f}s")
    print_bytes_nice(salt, "  Salt (16 bytes)", 32)
    print_bytes_nice(key, "  Derived Key (32 bytes)", 32)
    
    print("\n[T14] Step 2: Authenticated Encryption (AES-256-GCM)")
    print("-"*70)
    start = time.time()
    ciphertext, iv = encrypt_text(message, key)
    encrypt_time = time.time() - start
    print(f"  Algorithm: AES-256-GCM")
    print(f"  Time: {encrypt_time:.4f}s")
    print_bytes_nice(iv, "  IV/Nonce (12 bytes)", 32)
    print(f"  Plaintext: '{message}' ({len(message.encode('utf-8'))} bytes)")
    print_bytes_nice(ciphertext, "  Ciphertext + Tag")
    
    print("\n✅ Encryption Complete!")
    print(f"   Total time: {pbkdf2_time + encrypt_time:.3f}s")
    print(f"   PBKDF2: {pbkdf2_time:.3f}s ({pbkdf2_time/(pbkdf2_time + encrypt_time)*100:.1f}%)")
    print(f"   AES-GCM: {encrypt_time:.4f}s ({encrypt_time/(pbkdf2_time + encrypt_time)*100:.1f}%)")
    
    print("\n💾 Data to Store:")
    print("   1. Salt (16 bytes) - for PBKDF2")
    print("   2. IV (12 bytes) - for AES-GCM")
    print("   3. Ciphertext (N + 16 bytes) - encrypted data + auth tag")
    print(f"   Total overhead: {16 + 12 + 16} = 44 bytes")
    
    input("\n[Press Enter to decrypt...]")
    
    print("\n" + "█"*70)
    print("█  COMPLETE DECRYPTION WORKFLOW")
    print("█"*70)
    
    print("\n[T13] Step 1: Key Derivation from Stored Salt")
    print("-"*70)
    start = time.time()
    key_decrypt = derive_key(password, salt)
    pbkdf2_time2 = time.time() - start
    print(f"  Using same password + stored salt")
    print(f"  Time: {pbkdf2_time2:.3f}s")
    print_bytes_nice(key_decrypt, "  Derived Key", 32)
    
    if key == key_decrypt:
        print("  ✅ Keys match!")
    
    print("\n[T14] Step 2: Authenticated Decryption")
    print("-"*70)
    start = time.time()
    try:
        decrypted = decrypt_text(ciphertext, key_decrypt, iv)
        decrypt_time = time.time() - start
        print(f"  Time: {decrypt_time:.4f}s")
        print(f"  Decrypted: '{decrypted}'")
        
        print("\n✅ Decryption Complete!")
        print(f"   Total time: {pbkdf2_time2 + decrypt_time:.3f}s")
        
        if decrypted == message:
            print("\n🎉 COMPLETE WORKFLOW SUCCESSFUL!")
            print("   Original and decrypted messages match!")
        
    except AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
    
    input("\nPress Enter to continue...")


def test_7_binary_data():
    """Test 7: Encrypt binary data."""
    print_separator()
    print("TEST 7: Encrypt Binary Data")
    print_separator()
    
    print("\nAES-GCM can encrypt any binary data, not just text.")
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "binary_test"
        print(f"Using default: '{password}'")
    
    print("\nCreating binary data...")
    # Create binary data (all byte values 0-255)
    binary_data = bytes(range(256))
    print(f"Binary data: {len(binary_data)} bytes (0x00 to 0xFF)")
    print(f"First 16 bytes: {binary_data[:16].hex()}")
    print(f"Last 16 bytes: {binary_data[-16:].hex()}")
    
    print("\n" + "-"*70)
    print("ENCRYPTING BINARY DATA...")
    print("-"*70)
    
    key, salt = derive_key_with_new_salt(password)
    ciphertext, iv = encrypt(binary_data, key)
    
    print_bytes_nice(ciphertext, "Ciphertext", 64)
    
    print("\n" + "-"*70)
    print("DECRYPTING BINARY DATA...")
    print("-"*70)
    
    try:
        decrypted = decrypt(ciphertext, key, iv)
        print(f"Decrypted: {len(decrypted)} bytes")
        print(f"First 16 bytes: {decrypted[:16].hex()}")
        print(f"Last 16 bytes: {decrypted[-16:].hex()}")
        
        if decrypted == binary_data:
            print("\n✅ Binary data round-trip successful!")
            print("   All 256 bytes match perfectly!")
        else:
            print("\n❌ Binary data mismatch!")
        
    except AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
    
    input("\nPress Enter to continue...")


def test_8_multiple_messages():
    """Test 8: Encrypt multiple messages with same key."""
    print_separator()
    print("TEST 8: Multiple Messages with Same Key")
    print_separator()
    
    print("\nEncrypting multiple different messages with the same key.")
    print("Each encryption uses a fresh random IV for security.")
    
    password = input("\nMasukkan password: ")
    if not password:
        password = "multitest"
        print(f"Using default: '{password}'")
    
    messages = []
    try:
        count = int(input("Berapa pesan? (default: 3): ") or "3")
    except ValueError:
        count = 3
    
    print()
    for i in range(count):
        msg = input(f"Message #{i+1}: ")
        if not msg:
            msg = f"Message number {i+1}"
            print(f"  Using default: '{msg}'")
        messages.append(msg)
    
    print("\n" + "-"*70)
    print("ENCRYPTING ALL MESSAGES...")
    print("-"*70)
    
    # Derive key once
    key, salt = derive_key_with_new_salt(password)
    print("Using same key for all messages:")
    print_bytes_nice(key, "  Key", 32)
    
    encrypted_messages = []
    for i, msg in enumerate(messages, 1):
        ciphertext, iv = encrypt_text(msg, key)
        encrypted_messages.append((msg, ciphertext, iv))
        print(f"\nMessage #{i}: '{msg}'")
        print_bytes_nice(iv, "  IV", 32)
        print_bytes_nice(ciphertext, "  Ciphertext", 48)
    
    print("\n" + "-"*70)
    print("DECRYPTING ALL MESSAGES...")
    print("-"*70)
    
    all_success = True
    for i, (original, ciphertext, iv) in enumerate(encrypted_messages, 1):
        try:
            decrypted = decrypt_text(ciphertext, key, iv)
            match = "✅" if decrypted == original else "❌"
            print(f"\nMessage #{i}: {match}")
            print(f"  Original:  '{original}'")
            print(f"  Decrypted: '{decrypted}'")
            if decrypted != original:
                all_success = False
        except AuthenticationError:
            print(f"\nMessage #{i}: ❌ Authentication failed!")
            all_success = False
    
    print("\n" + "-"*70)
    if all_success:
        print("✅ All messages encrypted and decrypted successfully!")
        print("   Same key can be reused safely with different IVs!")
    else:
        print("❌ Some messages failed!")
    
    input("\nPress Enter to continue...")


def test_9_config():
    """Test 9: Show configuration."""
    print_separator()
    print("CONFIGURATION")
    print_separator()
    
    print("\nT14 - AES-256-GCM Configuration:")
    print("\n  Algorithm: AES-256-GCM (Galois/Counter Mode)")
    print(f"  Key Size: 32 bytes (256 bits)")
    print(f"  IV Size: {IV_LENGTH} bytes (96 bits - GCM recommendation)")
    print(f"  Tag Size: {TAG_LENGTH} bytes (128 bits - authentication)")
    print(f"  Randomness: secrets.token_bytes() (cryptographically secure)")
    
    print("\n" + "-"*70)
    print("SECURITY PROPERTIES:")
    print("-"*70)
    print("  ✓ Confidentiality: Plaintext is encrypted")
    print("  ✓ Authentication: Tag prevents tampering")
    print("  ✓ Integrity: Any modification is detected")
    print("  ✓ Semantic security: Fresh IV → different ciphertext")
    print("  ✓ Key verification: Wrong key → authentication failure")
    print("  ✓ Tamper detection: Modified ciphertext → authentication failure")
    
    print("\n" + "-"*70)
    print("GCM MODE ADVANTAGES:")
    print("-"*70)
    print("  • Authenticated Encryption with Associated Data (AEAD)")
    print("  • Single-pass operation (efficient)")
    print("  • Parallel processing capable")
    print("  • NIST approved (SP 800-38D)")
    print("  • Widely used in TLS 1.2/1.3")
    
    print("\n" + "-"*70)
    print("OVERHEAD:")
    print("-"*70)
    print(f"  Per message: {IV_LENGTH} + {TAG_LENGTH} = {IV_LENGTH + TAG_LENGTH} bytes")
    print(f"  - IV: {IV_LENGTH} bytes (must be stored)")
    print(f"  - Authentication Tag: {TAG_LENGTH} bytes (appended to ciphertext)")
    
    print("\n" + "-"*70)
    print("INTEGRATION WITH T13:")
    print("-"*70)
    print("  T13 (PBKDF2) provides the 32-byte key for T14 (AES-GCM)")
    print("  Workflow: Password → PBKDF2 → Key → AES-GCM → Ciphertext")
    
    input("\nPress Enter to continue...")


def main():
    """Main interactive loop."""
    while True:
        menu()
        choice = input("Pilih menu (0-9): ").strip()
        
        if choice == '0':
            print("\n✨ Terima kasih sudah testing T14!")
            print("💪 AES-256-GCM implementation ready for integration!\n")
            break
        elif choice == '1':
            test_1_encrypt_text()
        elif choice == '2':
            test_2_round_trip()
        elif choice == '3':
            test_3_wrong_password()
        elif choice == '4':
            test_4_tampered_ciphertext()
        elif choice == '5':
            test_5_semantic_security()
        elif choice == '6':
            test_6_complete_workflow()
        elif choice == '7':
            test_7_binary_data()
        elif choice == '8':
            test_8_multiple_messages()
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
