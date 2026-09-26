# Stegora — Architecture

## Streamlit routing
Use current Streamlit multipage navigation with `st.Page` + `st.navigation` where available.

Suggested:
```text
app.py
pages/
  embed.py
  extract.py
  analyze.py
```

The entrypoint owns shared navigation/theme. Core logic must not be mixed into page scripts.

## Project structure
```text
stegora/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── pages/
│   ├── embed.py
│   ├── extract.py
│   └── analyze.py
├── stegora/
│   ├── ui/
│   │   ├── theme.py
│   │   └── components.py
│   ├── crypto/
│   │   ├── pbkdf2.py
│   │   └── aes_gcm.py
│   ├── stego/
│   │   ├── capacity.py
│   │   ├── container.py
│   │   ├── positions.py
│   │   ├── lsb.py
│   │   └── extraction.py
│   ├── image/
│   │   ├── io.py
│   │   └── metrics.py
│   └── analysis/
│       ├── histogram.py
│       ├── lsb_plane.py
│       └── mbits.py
└── tests/
```

## Dependency direction
UI → application services → core modules.

Core modules must not import Streamlit.

## Embed flow
Image → validation → capacity → crypto → container → positions → LSB → output → metrics.

## Extract flow
Image → positions → header → container → crypto → recovered payload.
