# Stegora — UI/UX Specification

## Visual direction
Modern security utility / digital laboratory.

Tone:
- elegant
- soft
- precise
- technical
- restrained

## Suggested palette
- Background `#F7F8F6`
- Surface `#FFFFFF`
- Text `#26343B`
- Muted `#6C777C`
- Accent `#718E88`
- Accent soft `#E5EEEC`
- Border `#D9E0DE`

Use Streamlit theme configuration for base colors and limited custom CSS for spacing/surfaces. Streamlit supports theme customization through `.streamlit/config.toml`.

## Navigation
- Embed
- Extract
- Analyze

No extra pages unless they materially help the assignment.

## Embed screen
1. Cover image uploader
2. Image facts: format, dimensions, channels, capacity
3. Payload selector: Text / File
4. Password
5. Stego-key
6. Capacity status
7. Embed button
8. Result: cover vs stego
9. MSE / PSNR
10. Download stego

## Extract screen
1. Stego image
2. Password
3. Stego-key
4. Extract
5. Result / safe error
6. Download recovered file if applicable

## Analyze screen
1. Cover/stego selector or result state
2. MSE/PSNR
3. Histogram comparison
4. Enhanced LSB
5. m-bit enrichment

## Anti-AI visual rules
Avoid:
- neon cyberpunk
- purple/blue gradient overload
- excessive rounded cards
- fake metrics
- random badges
- meaningless charts
- giant marketing headlines
- decorative animations
- excessive emojis

The UI should communicate the actual steganography workflow.
