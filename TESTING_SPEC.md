# Stegora — Testing Specification

## Minimum unit testing
At least 5 unit tests are required by the UTS brief. Target more than 5.

Recommended:
1. capacity calculation
2. container encode/decode
3. PRNG determinism
4. LSB embed/extract
5. alpha preservation
6. PBKDF2/AES round-trip
7. wrong credential failure
8. MSE/PSNR known fixture

## Mandatory matrix
5 different cover images × 3 message sizes = at least 15 combinations.

Record actual:
- image name
- format
- dimensions
- payload type
- payload bytes
- capacity
- utilization
- MSE
- PSNR
- extraction success
- exact match

## Mandatory analysis
- histogram comparison
- JPEG re-save fragility
- enhanced LSB visual steganalysis

## Enrichment
m-bit LSB comparison (e.g. 1/2/3/4-bit) showing capacity/PSNR trade-off.

## Evidence rule
Never invent metrics or test outcomes. Every reported number must come from an actual run.
