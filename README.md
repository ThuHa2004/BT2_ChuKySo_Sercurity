# BÀI TẬP 2: CHỮ KÝ SỐ TRONG FILE PDF
##  Trần Thị Thu Hà - K225480106009
## Lớp K58KTP
## Hạn nộp 31/10/2025 - 23:59:59
-----------
# Yêu Cầu: 
Thực hiện báo cáo và thực hành: phân tích và hiện thực việc nhúng, xác thực chữ ký trong file PDF. Nêu rõ chuân tham chiếu PDF 1.7 và sử dụng công cụ thực thi như iText7, OpenSSL, PyPDF, pdf-lib. 

# Bài làm
### 1. Chuẩn bị một file PDF gốc cần ký
File: original.pdf 
### 2. Tạo file sinh khóa RSA và chứng thư số
Sinh khóa RSA và chứng thư số mục đích là để xác thực chữ ký số và ký 
Tạo một file `genn_key.py`, sau khi chạy file này sẽ sinh ra hai file `signer_cert.pem` và file `signer_key.pem`
