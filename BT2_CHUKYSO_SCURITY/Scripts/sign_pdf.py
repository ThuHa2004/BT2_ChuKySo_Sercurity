# sign_pdf.py (sửa để hỗ trợ nhiều phiên bản pyHanko / fallback bằng pikepdf)
from datetime import datetime
from pyhanko.sign import signers, fields
from pyhanko.stamp import TextStampStyle
from pyhanko.pdf_utils import images
from pyhanko.pdf_utils.text import TextBoxStyle
from pyhanko.pdf_utils.layout import SimpleBoxLayoutRule, AxisAlignment, Margins
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec
import os
import shutil
import tempfile

# === ĐƯỜNG DẪN CẤU HÌNH (chỉnh theo máy bạn) ===
PDF_INPUT = r"D:\BAITAP\BT_ATBMTT\BT2_CHUKYSO_SCURITY\original.pdf"
PDF_OUTPUT = r"D:\BAITAP\BT_ATBMTT\BT2_CHUKYSO_SCURITY\signed_output.pdf"
KEY_PATH = r"D:\BAITAP\BT_ATBMTT\BT2_CHUKYSO_SCURITY\keys\signer_key.pem"
CERT_PATH = r"D:\BAITAP\BT_ATBMTT\BT2_CHUKYSO_SCURITY\keys\signer_cert.pem"
SIGN_IMG = r"D:\BAITAP\BT_ATBMTT\BT2_CHUKYSO_SCURITY\Scripts\signature_image.png"

def step(title):
    print(f"🔹 {title}")

def try_open_writer(fp_path):
    """
    Thử mở IncrementalPdfFileWriter theo nhiều cách:
     1) với allow_hybrid_xrefs kwarg (nếu hỗ trợ)
     2) không kwarg rồi gán thuộc tính nội bộ (nếu có)
     3) fallback: rewrite bằng pikepdf rồi mở lại (nếu pikepdf có)
    Trả về: (writer, fileobj) - writer là IncrementalPdfFileWriter,
            fileobj là file object đang được mở (để đóng sau)
    Ném RuntimeError nếu không thể mở an toàn.
    """
    # Mở file nhị phân
    f = open(fp_path, "rb")
    # 1) thử truyền kwarg
    try:
        writer = IncrementalPdfFileWriter(f, allow_hybrid_xrefs=True)
        return writer, f
    except TypeError:
        # không hỗ trợ kwarg -> đóng file và tiếp
        f.close()

    # 2) mở không kwarg, thử gán thuộc tính nếu tồn tại
    f = open(fp_path, "rb")
    writer = IncrementalPdfFileWriter(f)
    # kiểm tra các tên thuộc tính khả dĩ
    attr_names = ("allow_hybrid_xrefs", "allow_hybrid_xref", "_allow_hybrid_xrefs", "allow_hybrid")
    for a in attr_names:
        if hasattr(writer, a):
            try:
                setattr(writer, a, True)
                return writer, f
            except Exception:
                # nếu gán thất bại, tiếp tục thử những tên khác
                pass
    # nếu tới đây vẫn chưa bật được -> đóng file và thử rewrite
    f.close()

    # 3) fallback: cố gắng rewrite file bằng pikepdf (loại bỏ hybrid xref)
    try:
        import pikepdf
    except Exception as e:
        raise RuntimeError(
            "Không thể enable hybrid xrefs và 'pikepdf' không được cài. "
            "Cài pikepdf bằng 'pip install pikepdf' hoặc nâng cấp pyHanko."
        ) from e

    # tạo temp file rewrite
    tmp_dir = tempfile.mkdtemp(prefix="pdf_rewrite_")
    tmp_out = os.path.join(tmp_dir, "rewritten.pdf")
    try:
        # mở và lưu lại (pikepdf sẽ rebuild xref)
        pdf = pikepdf.Pdf.open(fp_path)
        pdf.save(tmp_out)
        pdf.close()
        # mở rewritten file
        f2 = open(tmp_out, "rb")
        writer = IncrementalPdfFileWriter(f2)
        return writer, f2
    except Exception as e:
        # dọn dẹp và báo lỗi
        try:
            if os.path.exists(tmp_out):
                os.remove(tmp_out)
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass
        raise RuntimeError("Không thể rewrite PDF để loại bỏ hybrid xref.") from e

def main():
    step("B1: Mở file PDF gốc và chuẩn bị vùng chữ ký.")
    try:
        writer, fp = try_open_writer(PDF_INPUT)
    except RuntimeError as e:
        print("LỖI: ", e)
        return

    try:
        # Lấy số trang
        try:
            total_pages = int(writer.root["/Pages"]["/Count"])
        except Exception:
            total_pages = 1
        target_page = total_pages - 1

        # Tạo vùng chữ ký (Signature field) - vị trí bạn có thể chỉnh
        sig_field = SigFieldSpec(
            sig_field_name="DigitalSign_1",
            box=(280, 160, 580, 260),
            on_page=target_page
        )
        fields.append_signature_field(writer, sig_field)

        step("B2: Tạo signer RSA (2048-bit, SHA-256).")
        signer = signers.SimpleSigner.load(KEY_PATH, CERT_PATH, key_passphrase=None)
        vc = ValidationContext(trust_roots=[load_cert_from_pemder(CERT_PATH)])

        # Hiển thị chữ ký (ảnh + text) - không viền (border_width=0)
        step("B3: Tạo ảnh chữ ký và thông tin mô tả.")
        sign_image = images.PdfImage(SIGN_IMG)

        layout_img = SimpleBoxLayoutRule(
            x_align=AxisAlignment.ALIGN_MIN,
            y_align=AxisAlignment.ALIGN_MID,
            margins=Margins(right=20)
        )
        layout_text = SimpleBoxLayoutRule(
            x_align=AxisAlignment.ALIGN_MIN,
            y_align=AxisAlignment.ALIGN_MID,
            margins=Margins(left=160)
        )

        text_style = TextBoxStyle(font_size=12)
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        sign_info = (
            "MSSV: K225480106009\n"
            "SDT: 0362995977\n"
            f"Ngày ký: {current_date}\n"
        )

        stamp = TextStampStyle(
            stamp_text=sign_info,
            background=sign_image,
            background_layout=layout_img,
            inner_content_layout=layout_text,
            text_box_style=text_style,
            border_width=0,
            background_opacity=1.0
        )

        step("B4: Thiết lập metadata chữ ký.")
        meta = signers.PdfSignatureMetadata(
            field_name="DigitalSign_1",
            reason="Ký nộp bài thực hành: Chữ ký số trong PDF",
            location="Việt Nam",
            md_algorithm="sha256"
        )

        step("B5: Thực hiện ký số và chèn PKCS#7 vào PDF.")
        pdf_signer = signers.PdfSigner(
            signature_meta=meta,
            signer=signer,
            stamp_style=stamp
        )

        with open(PDF_OUTPUT, "wb") as signed_out:
            pdf_signer.sign_pdf(writer, output=signed_out)

        step("B6: Ghi incremental update và hoàn tất quá trình ký.")
        print(f"✅ Đã ký PDF thành công! File lưu tại: {PDF_OUTPUT}")

    finally:
        # đóng file object writer đang dùng
        try:
            fp.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
