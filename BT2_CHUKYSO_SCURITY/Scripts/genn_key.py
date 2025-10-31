# gen_key_custom.py
# (Tạo cặp khóa & chứng chỉ tự ký – viết lại theo phong cách khác)
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os

def generate_self_signed_cert(common_name, org, location, state, country="VN", days_valid=365):
    """Tạo cặp khóa RSA + chứng chỉ tự ký (self-signed certificate)."""
    print("🧩 Bắt đầu tạo khóa và chứng chỉ tự ký...\n")

    # 1️⃣ Sinh private key (RSA 2048-bit)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    print("🔐 Đã sinh private key RSA 2048-bit.")

    # 2️⃣ Thông tin nhận dạng (Subject / Issuer)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, location),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    # 3️⃣ Tạo chứng chỉ tự ký (SHA-256)
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=days_valid))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    )
    certificate = cert_builder.sign(private_key, hashes.SHA256())
    print(f"📜 Đã tạo chứng chỉ tự ký SHA-256 (hạn {days_valid} ngày).")

    # 4️⃣ Tạo thư mục lưu
    base_dir = os.path.dirname(os.path.abspath(__file__))
    keys_dir = os.path.join(base_dir, "..", "keys")
    os.makedirs(keys_dir, exist_ok=True)

    # 5️⃣ Ghi ra file PEM
    key_path = os.path.join(keys_dir, "signer_key.pem")
    cert_path = os.path.join(keys_dir, "signer_cert.pem")

    with open(key_path, "wb") as kf:
        kf.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(cert_path, "wb") as cf:
        cf.write(certificate.public_bytes(serialization.Encoding.PEM))

    print(f"✅ Private key lưu tại: {key_path}")
    print(f"✅ Certificate lưu tại: {cert_path}")
    print("\n🎉 Hoàn tất tạo cặp khóa & chứng chỉ tự ký.")
    return key_path, cert_path


# --- Chạy thử (có thể chỉnh thông tin ở đây) ---
if __name__ == "__main__":
    generate_self_signed_cert(
        common_name="Tran Thi Thu Ha",
        org="58KTP",
        location="Thai Nguyen",
        state="Thai Nguyen"
    )
