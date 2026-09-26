# Stegora — PRD

## Users
Primary user: lecturer/student evaluator running the app on a laptop.

## Primary jobs
### Embed
Upload PNG/BMP → see metadata/capacity → choose text/file → enter password + stego-key → embed → download/display stego image → inspect metrics.

### Extract
Upload stego PNG → enter password + stego-key → extract → show recovered text/file or safe error.

### Analyze
Compare cover/stego → MSE/PSNR → RGB histogram → enhanced LSB → m-bit enrichment.

## UX principles
- One clear action at a time.
- Minimal navigation: Embed / Extract / Analyze.
- Soft neutral palette with one muted accent.
- No fake statistics.
- No decorative charts.
- No excessive gradients, glassmorphism, or huge hero copy.
- Error messages should explain what happened and what the user should do.
- Download controls appear only for actual generated files.

## Acceptance
A first-time evaluator should understand the basic story within seconds:
**Image → Secret → Credentials → Embed → Compare → Extract.**
