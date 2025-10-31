# BÀI TẬP 2: CHỮ KÝ SỐ TRONG FILE PDF
##  Trần Thị Thu Hà - K225480106009
## Lớp K58KTP
## Hạn nộp 31/10/2025 - 23:59:59
-----------
# Yêu Cầu: 
Thực hiện báo cáo và thực hành: phân tích và hiện thực việc nhúng, xác thực chữ ký trong file PDF. Nêu rõ chuẩn tham chiếu PDF 1.7 và sử dụng công cụ thực thi như iText7, OpenSSL, PyPDF, pdf-lib. 

# Bài làm
### 1. Chuẩn bị một file PDF gốc cần ký
File: `original.pdf`
### 2. Tạo file sinh khóa RSA và chứng thư số
Sinh khóa RSA và chứng thư số mục đích là để xác thực chữ ký số và ký 
Tạo một file `genn_key.py`, sau khi chạy file này sẽ sinh ra hai file `signer_cert.pem` và file `signer_key.pem`
### 3. Tạo chữ ký và ký file PDF
- Ta sẽ thực hiện tạo Signature field (AcroForm) và reserve vùng /Contents (8192 bytes), xác định /ByteRange để loại trừ vùng /Contents khỏi hash) và tính Hash (SHA-256) trên vùng ByteRange. Sinh PKCS#7 detached signature và chèn blob DER PKCS#7 vào /Contents đúng offset bằng file `sign_pdf.py`. 
- Sau khi chạy lệnh `python sign_pdf.py` thì các bước trên đã được thực hiện và tạo ra một file mới đã được ký chữ ký số hợp lệ`signed_output.pdf`
- Đây là kết quả sau khi chạy file `sign_pdf.py`: Tạo ra một file tên `signed_output.pdf` có chữ ký số

  <img width="1905" height="967" alt="image" src="https://github.com/user-attachments/assets/8178931a-639d-43dd-862b-047574f0156e" />

#### Chèn thêm nội dung vào file pdf
- Tạo một file `update_pdf_incremental.py` sau đó thêm một đoạn nội dung vào file ví dụ "Xin chào". Chạy lệnh `python update_pdf_incremental.py` sẽ tạo ra file pdf đã được chèn thêm nội dung vào `signed_with_overlay.pdf`
  
  <img width="1700" height="679" alt="image" src="https://github.com/user-attachments/assets/3da18051-b26d-4b07-890a-6c089830fad4" />

- Đây là thông báo từ xác thực đã khác đi khi thêm nội dung vào file

  <img width="1900" height="830" alt="image" src="https://github.com/user-attachments/assets/da2abe2a-6058-4c89-ad2a-91f04c382f30" />

### 4. Xác thực chữ ký trên PDF đã ký
**Các bước kiểm tra xác thực chữ ký trên PDF:**
- Đọc Signature dictionary: /Contents, /ByteRange.
- Tách PKCS#7, kiểm tra định dạng.
- Tính hash và so sánh messageDigest.
- Verify signature bằng public key trong cert.
- Kiểm tra chain → root trusted CA.
- Kiểm tra OCSP/CRL.
- Kiểm tra timestamp token.
- Kiểm tra incremental update (phát hiện sửa đổi).
**Tạo một file `verify_pdf_signature.py`** file này sẽ thực hiện các bước ở trên và khi thực hiện chạy `python verify_pdf_signature.py` sẽ tạo ra file xác minh chữ ký trong file `signed_output.pdf`có hợp lệ hay không
**Kết quả**:
- Tạo ra file `verify_KQ_ok.txt` khi kiểm tra `signed_output.pdf` có chữ ký hợp lệ

  <img width="1248" height="332" alt="image" src="https://github.com/user-attachments/assets/7fdc6065-4529-4556-bf73-b12ecde9c907" />

- Tạo ra file `verify_file_overlay.txt` khi kiểm tra file `signed_with_overlay.pdf`

  <img width="1237" height="339" alt="image" src="https://github.com/user-attachments/assets/823bacb0-1b4a-40a8-88f1-33c4b3e2d490" />

### 5. Kết quả Demo
- Sau khi thực hiện các yêu cầu của đề bài, tạo ra các file:
  + `original.pdf`: Đây là file gốc chưa có chữ ký
  + `signed_output.pdf`: Đây là file đã được ký và chứa chữ ký số hợp lệ
  + `signed_with_overlay.pdf`: Đây là file chứa nội dung bị thay đổi sau khi đã ký chữ ký hợp lệ
  + `verify_file_overlay.txt`: Đây là file chứa kết quả xác minh không hợp lệ do nội dung đã bị thay đổi
  + `verify_KQ_ok.txt`: Đây là file chứa kết quả xác minh hợp lệ








