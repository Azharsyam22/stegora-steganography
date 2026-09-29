"""
Stegora - Halaman Penyisipan
Menyisipkan teks atau berkas ke dalam citra menggunakan steganografi LSB.
"""
import io

import streamlit as st

from frontend.ui.components import footer, muted_text, page_title, section_header
from frontend.ui.state import (
    clear_embedding_history,
    save_embed_result,
    store_credentials,
)
from backend.image.io import ImageValidationError, validate_and_load_cover_image
from backend.image.metrics import calculate_mse, calculate_psnr
from backend.pipeline import EmbedError, embed_pipeline
from backend.stego.capacity import (
    calculate_raw_capacity,
    calculate_usable_capacity,
    check_payload_capacity,
    format_bytes,
    validate_payload_capacity,
)


def show():
    page_title(
        "Sisipkan Pesan",
        "Sembunyikan teks atau berkas di dalam citra menggunakan steganografi LSB"
    )

    section_header("1. Unggah Citra Penutup")
    cover_file = st.file_uploader(
        "Pilih citra (PNG, BMP)",
        type=["png", "bmp"],
        key="embed_cover",
        help="Pilih citra lossless berformat PNG atau BMP untuk menyisipkan pesan."
    )

    cover_valid = False
    payload_size = 0
    if cover_file:
        try:
            image, metadata = validate_and_load_cover_image(cover_file.getvalue())
            st.session_state.cover_image = image
            st.session_state.cover_metadata = metadata
            cover_valid = True

            raw_capacity = calculate_raw_capacity(metadata["width"], metadata["height"])
            usable_capacity = calculate_usable_capacity(
                metadata["width"], metadata["height"], container_overhead=64
            )

            col_image, col_details = st.columns([1, 2])
            with col_image:
                st.image(image, caption="Citra Penutup", use_container_width=True)
            with col_details:
                st.success(f"Berhasil dimuat: **{cover_file.name}**")
                st.markdown("**Informasi Citra**")
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.metric("Format", metadata["format"])
                    st.metric("Mode", metadata["mode"])
                with info_col2:
                    st.metric("Lebar", f"{metadata['width']} px")
                    st.metric("Tinggi", f"{metadata['height']} px")
                if metadata["has_alpha"]:
                    st.caption("Kanal alfa dipertahankan dan tidak digunakan untuk penyisipan.")

                st.markdown("**Kapasitas Steganografi**")
                capacity_col1, capacity_col2 = st.columns(2)
                with capacity_col1:
                    st.metric("Jumlah Piksel", f"{metadata['total_pixels']:,}")
                    st.metric("Kapasitas Mentah", format_bytes(raw_capacity["total_bytes"]))
                with capacity_col2:
                    st.metric(
                        "Kapasitas Tersedia",
                        format_bytes(usable_capacity["usable_capacity_bytes"])
                    )
                    st.metric("Efisiensi", f"{usable_capacity['efficiency_percent']:.1f}%")
                muted_text("Menggunakan LSB RGB 1-bit: 3 bit per piksel")
        except ImageValidationError as error:
            st.error(f"**Kesalahan validasi:** {error}")
            st.session_state.cover_image = None
        except Exception as error:
            st.error(f"**Kesalahan tidak terduga:** {error}")
            st.session_state.cover_image = None

    section_header("2. Pilih Muatan Data")
    payload_type = st.radio(
        "Jenis muatan data",
        ["Teks", "Berkas"],
        horizontal=True,
        help="Pilih apakah yang akan disembunyikan berupa teks atau berkas."
    )

    payload_text = None
    payload_file = None
    payload_fits = False
    if payload_type == "Teks":
        payload_text = st.text_area(
            "Masukkan pesan rahasia",
            placeholder="Ketik pesan rahasia di sini...",
            height=150,
            help="Teks akan dienkripsi sebelum disisipkan.",
            key="secret_text"
        )
        if payload_text:
            payload_size = len(payload_text.encode("utf-8"))
            st.caption(f"Ukuran pesan: **{format_bytes(payload_size)}**")
    else:
        payload_file = st.file_uploader(
            "Pilih berkas yang akan disembunyikan",
            key="embed_payload_file",
            help="Berkas berukuran kecil paling sesuai."
        )
        if payload_file:
            payload_size = payload_file.size
            st.caption(f"Berkas: **{payload_file.name}** — {format_bytes(payload_size)}")

    if cover_valid and payload_size > 0:
        capacity_check = check_payload_capacity(
            st.session_state.cover_metadata["width"],
            st.session_state.cover_metadata["height"],
            payload_size,
            container_overhead=64,
        )
        if capacity_check["fits"]:
            st.success(
                f"Muatan data muat (menggunakan "
                f"{capacity_check['utilization_percent']:.1f}% kapasitas)"
            )
            payload_fits = True
        else:
            st.error(
                f"Muatan data terlalu besar. Dibutuhkan: "
                f"{format_bytes(capacity_check['required_bytes'])}, tersedia: "
                f"{format_bytes(capacity_check['available_bytes'])}."
            )
            st.caption("Kurangi ukuran muatan data atau gunakan citra berkapasitas lebih besar.")

    section_header("3. Kredensial Keamanan")
    
    st.markdown("Masukkan **kata kunci** untuk enkripsi dan penentuan posisi penyisipan:")
    st.caption("Kata kunci ini digunakan untuk enkripsi AES-256-GCM dan menentukan posisi LSB secara deterministik.")
    
    # Generate button first
    col_gen_info, col_gen_btn = st.columns([4, 1])
    
    with col_gen_info:
        if 'generated_key' in st.session_state and st.session_state.generated_key:
            st.info(f"**Kata kunci ter-generate:** `{st.session_state.generated_key}`")
            st.caption("SIMPAN kata kunci ini! Tanpa kata kunci, data tidak dapat diekstrak.")
    
    with col_gen_btn:
        if st.button("Generate", use_container_width=True, help="Generate kata kunci acak yang kuat (16 karakter)"):
            import secrets
            import string
            # Generate 16-character strong password
            chars = string.ascii_letters + string.digits + "!@#$%^&*-_"
            strong_key = ''.join(secrets.choice(chars) for _ in range(16))
            st.session_state.generated_key = strong_key
            st.rerun()
    
    # Password input - will be auto-filled if generated_key exists
    password = st.text_input(
        "Kata Kunci / Password",
        type="password",
        key="embed_password",
        value=st.session_state.get('generated_key', ''),
        help="Gunakan kata kunci yang kuat (minimal 8 karakter). Simpan baik-baik untuk ekstraksi nanti.",
        placeholder="Masukkan kata kunci yang kuat atau klik Generate..."
    )
    
    # Use same password for stego_key (unified credential)
    stego_key = password

    section_header("4. Sisipkan Pesan")
    warnings = []
    if not cover_valid:
        warnings.append("Unggah citra penutup yang valid")
    if payload_type == "Teks" and not payload_text:
        warnings.append("Masukkan pesan teks")
    elif payload_type == "Berkas" and not payload_file:
        warnings.append("Unggah berkas yang akan disisipkan")
    if not password:
        warnings.append("Masukkan kata kunci")
    if cover_valid and payload_size > 0 and not payload_fits:
        warnings.append("Muatan data terlalu besar untuk citra ini")
    if warnings:
        st.warning(f"Perlu dilengkapi: {', '.join(warnings)}")

    button_col1, button_col2, button_col3 = st.columns([2, 1, 2])
    with button_col2:
        embed_button = st.button(
            "Sisipkan Pesan",
            type="primary",
            use_container_width=True,
            disabled=bool(warnings),
        )

    if embed_button and not warnings:
        try:
            with st.spinner("Pesan sedang disisipkan..."):
                if payload_type == "Teks":
                    payload_bytes = payload_text.encode("utf-8")
                    filename = "pesan.txt"
                    mime_type = "text/plain"
                else:
                    payload_bytes = payload_file.getvalue()
                    filename = payload_file.name
                    mime_type = payload_file.type or "application/octet-stream"

                validate_payload_capacity(
                    st.session_state.cover_metadata["width"],
                    st.session_state.cover_metadata["height"],
                    len(payload_bytes),
                )
                stego_image, embed_metadata = embed_pipeline(
                    st.session_state.cover_image,
                    payload_bytes,
                    password,
                    stego_key,
                    filename=filename,
                    mime_type=mime_type,
                )
                embed_metadata.update({
                    "payload_type": payload_type,
                    "cover_filename": cover_file.name,
                    "cover_width": st.session_state.cover_metadata["width"],
                    "cover_height": st.session_state.cover_metadata["height"],
                })
                store_credentials(password, stego_key)
                save_embed_result(stego_image, embed_metadata)
                st.success("Pesan berhasil disisipkan!")

                with st.expander("Statistik Penyisipan", expanded=False):
                    stat_col1, stat_col2 = st.columns(2)
                    with stat_col1:
                        st.metric("Ukuran Muatan Data", format_bytes(len(payload_bytes)))
                        st.metric("Ukuran Terenkripsi", format_bytes(embed_metadata["encrypted_size"]))
                    with stat_col2:
                        st.metric("Ukuran Kontainer", format_bytes(embed_metadata["container_size"]))
                        st.metric("Bit Disisipkan", f"{embed_metadata['num_bits']:,}")
        except Exception as error:
            st.error(f"**Penyisipan gagal:** {error}")
            st.session_state.stego_image = None

    if st.session_state.get("stego_image") is not None and st.session_state.get("cover_image") is not None:
        section_header("5. Hasil")
        result_col1, result_col2 = st.columns(2)
        with result_col1:
            st.markdown("**Citra Penutup**")
            st.image(st.session_state.cover_image, use_container_width=True)
            st.caption("Citra asli")
        with result_col2:
            st.markdown("**Citra Stego**")
            st.image(st.session_state.stego_image, use_container_width=True)
            st.caption("Citra berisi data tersembunyi")

        st.markdown("**Metrik Kualitas**")
        metadata = st.session_state.get("embed_metadata") or {}
        try:
            mse = calculate_mse(st.session_state.cover_image, st.session_state.stego_image)
            psnr = calculate_psnr(st.session_state.cover_image, st.session_state.stego_image, mse=mse)
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("MSE", f"{mse:.6f}", help="Mean Squared Error; semakin kecil semakin baik.")
            with metric_col2:
                psnr_label = "∞ dB (sama)" if psnr == float("inf") else f"{psnr:.2f} dB"
                st.metric("PSNR", psnr_label, help="Peak Signal-to-Noise Ratio; semakin besar semakin baik.")
            with metric_col3:
                utilization = (
                    metadata.get("container_size", 0) * 8 /
                    (st.session_state.cover_metadata["width"] * st.session_state.cover_metadata["height"] * 3)
                ) * 100
                st.metric("Kapasitas Terpakai", f"{utilization:.2f}%")
            if psnr == float("inf") or psnr >= 50:
                st.info("**Sangat baik** - Perubahan nyaris tidak terlihat")
            elif psnr >= 30:
                st.info("**Baik** - Kualitas dapat diterima")
            else:
                st.info("**Cukup** - Artefak mungkin terlihat")
        except Exception as error:
            st.warning(f"Metrik tidak dapat dihitung: {error}")

        image_buffer = io.BytesIO()
        st.session_state.stego_image.save(image_buffer, format="PNG")
        st.download_button(
            "Unduh Citra Stego",
            data=image_buffer.getvalue(),
            file_name="stego_image.png",
            mime="image/png",
            help="Unduh citra yang berisi data tersembunyi.",
        )
        st.caption("Simpan kata sandi dan kunci stego dengan aman. Keduanya diperlukan untuk mengekstrak pesan.")

    history = st.session_state.get("embed_history", [])
    if history:
        section_header("Riwayat Penyisipan")
        with st.expander(f"{len(history)} penyisipan terbaru", expanded=False):
            if st.button("Hapus Riwayat", key="clear_embed_history"):
                clear_embedding_history()
                st.rerun()
            for history_item in history:
                st.markdown(f"**{history_item['payload_filename']}** · {history_item['payload_type']}")
                mse_value = history_item["mse"]
                psnr_value = history_item["psnr"]
                mse_text = f"{mse_value:.6f}" if mse_value is not None else "Tidak tersedia"
                if psnr_value is None:
                    psnr_text = "Tidak tersedia"
                elif psnr_value == float("inf"):
                    psnr_text = "∞ dB"
                else:
                    psnr_text = f"{psnr_value:.2f} dB"
                st.caption(
                    f"{history_item['created_at']} · {history_item['cover_filename']} · "
                    f"{history_item['cover_width']}×{history_item['cover_height']} · "
                    f"{format_bytes(history_item['payload_size'])} · MSE {mse_text} · PSNR {psnr_text}"
                )
                st.download_button(
                    "Unduh Citra Stego",
                    data=history_item["image_bytes"],
                    file_name=history_item["download_name"],
                    mime="image/png",
                    key=f"embed_history_download_{history_item['record_id']}",
                )
                st.markdown("---")

    footer()
