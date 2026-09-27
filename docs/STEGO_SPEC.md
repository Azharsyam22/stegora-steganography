# Stegora — Technical Specification

## Mandatory mode
1-bit RGB LSB. Alpha is preserved.

## Container
Minimum fixed header:
- MAGIC: 4 bytes `STGR`
- VERSION: 1 byte
- FLAGS: 1 byte
- PAYLOAD_TYPE: 1 byte
- RESERVED: 1 byte
- PAYLOAD_LEN: 4-byte unsigned big-endian

Then metadata:
- salt length
- IV length
- filename length
- MIME length
- salt
- IV
- filename
- MIME
- ciphertext/authentication data

Exact serialization must be implemented once and tested by round-trip.

## Capacity
For W×H pixels using RGB and one bit per RGB channel:
`raw_bits = W × H × 3`
`raw_bytes = floor(raw_bits / 8)`

But acceptance must use **framed container size**, not raw bytes alone.

If framed payload > capacity:
- reject before modifying the image,
- show required vs available bytes.

## Position generator
`stego-key -> SHA-256 -> seed -> deterministic PRNG -> unique RGB channel positions`

Same key + same image geometry + same algorithm version must reproduce the same sequence.

Different key should produce a different sequence with overwhelming practical likelihood.

Do not use security randomness for deterministic position reproduction.

## Embedding
For each payload bit:
- select keyed RGB channel,
- set channel LSB to payload bit,
- preserve all other bits,
- preserve alpha.

## Extraction
- reconstruct positions from stego-key,
- read fixed header,
- validate magic/version/length,
- read exact framed payload,
- parse metadata,
- derive AES key from password + stored salt,
- decrypt with AES-GCM,
- return original text/file.

Wrong key/password, malformed header, truncation, and authentication failure must fail safely.
