# Video Downloader Của Zu

Video Downloader Của Zu là ứng dụng desktop hỗ trợ tiếng Anh và tiếng Việt
để tải từng video từ URL
HTTP/HTTPS mà `yt-dlp` hỗ trợ. Ngôn ngữ mặc định là English và được ghi nhớ
khi đổi. Chạy trên Windows x86 (32-bit) và Linux x86_64. Chỉ tải nội dung
bạn có quyền lưu. Ứng dụng không gỡ DRM hay vượt giới hạn truy cập.

## Chức năng

- Dán liên kết, chọn thư mục tải và giới hạn độ phân giải.
- Theo dõi dung lượng, tốc độ, phần trăm và thời gian ước tính; có thể hủy.
- Ghi nhớ thư mục tải và mở thư mục sau khi tải xong.
- Tải một video mỗi lần, không tự tải toàn bộ playlist.

`yt-dlp` hỗ trợ nhiều trang nhưng không thể bảo đảm mọi URL đều tải được.
Trang web có thể thay đổi, yêu cầu đăng nhập hoặc chặn tải. Không nhập URL
không đáng tin cậy nếu bạn không muốn kết nối tới trang đó.

## Chạy từ mã nguồn

Cài Python 3.10 trở lên và Tkinter, sau đó:

```sh
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python .\linktai.py
```

Arch Linux:

```sh
sudo pacman -S python tk
source .venv/bin/activate
python -m pip install -e .
python linktai.py
```

FFmpeg tùy chọn nhưng cần thiết để ghép hình và âm thanh khi trang chỉ cung
cấp chúng thành các luồng riêng. Cài `ffmpeg` từ trình quản lý gói của hệ
điều hành để mở khóa tải chất lượng cao. Nếu không có FFmpeg, ứng dụng chỉ
chọn luồng video đơn có sẵn.

Để tải đầy đủ nội dung YouTube, yt-dlp còn cần một JavaScript runtime được hỗ
trợ. Deno được bật mặc định; cài `deno` trên Arch Linux hoặc cài Deno cho
Windows và bảo đảm lệnh `deno` có trong `PATH`. Không phải mọi trang đều cần
runtime này.

## Tạo ứng dụng chạy độc lập

Build cần thực hiện trên đúng hệ điều hành và kiến trúc đích.

- **Windows x86:** cài Python 3.10+ bản 32-bit và Tkinter, rồi chạy
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build-windows-x86.ps1`
  trong PowerShell (bypass chỉ áp dụng cho tiến trình build); script tự tìm
  Python 32-bit hoặc nhận đường dẫn qua `-PythonPath`;
  file chạy độc lập nằm trong `dist\install.exe`. Người dùng có thể tải
  `install.exe` từ GitHub Releases và chạy trực tiếp. Đây là ứng dụng, không
  phải bộ cài đặt có wizard.
- **Arch Linux:** chạy `bash build-arch.sh`; cần Python, Tkinter và các gói
  build. Ứng dụng nằm trong
  `dist/video-downloader-cua-zu/video-downloader-cua-zu`.
- **Ubuntu/Linux Mint `.deb`:** `VERSION=0.1.3 bash packaging/linux/build-release.sh deb`
  trên Ubuntu 22.04 trở lên.
- **Fedora `.rpm`:** `VERSION=0.1.3 bash packaging/linux/build-release.sh rpm`.

## Cài đặt gói Linux

Gói phát hành được build tự động khi đẩy Git tag dạng `v*` lên GitHub. `.deb`
được build trên Ubuntu 22.04 cho Ubuntu/Linux Mint x86_64; `.rpm` được build
trong Fedora; gói Arch được build trong Arch Linux. Tải file tương ứng từ
[GitHub Releases](https://github.com/XxZuPenguinxX/Video-Downloader-Cua-Zu/releases).

**Ubuntu/Linux Mint:** sau khi tải file `.deb`, mở terminal trong thư mục tải:

```sh
sudo apt install ./video-downloader-cua-zu_VERSION_amd64.deb
```

Thay `VERSION` bằng số phiên bản trong tên file. Dùng `apt install` để cài
gói và xử lý phụ thuộc; `sudo install` chỉ là lệnh sao chép file, không thay
thế trình quản lý gói.

**Fedora:**

```sh
sudo dnf install ./video-downloader-cua-zu-VERSION-1.x86_64.rpm
```

**Arch Linux:** để cài trực tiếp gói `.pkg.tar.zst` đã tải:

```sh
sudo pacman -U ./video-downloader-cua-zu-VERSION-1-x86_64.pkg.tar.zst
```

Sau khi gói được đăng lên AUR, có thể dùng:

```sh
paru -S video-downloader-cua-zu
```

`paru -S video-downloader-cua-zu` chỉ hoạt động sau khi AUR recipe đã được gửi lên AUR;
`sudo pacman -S video-downloader-cua-zu` chỉ hoạt động nếu gói được đưa vào một repository
Pacman đã cấu hình (AUR không phải repository chính thức của Pacman). GitHub
Releases lưu gói tải trực tiếp, không tự tạo APT/DNF repository để dùng
`apt install video-downloader-cua-zu` hoặc
`dnf install video-downloader-cua-zu` mà không có đường dẫn file.

### Cập nhật gói AUR

Để gửi gói lên AUR lần đầu, cần tài khoản AUR, SSH key đã đăng ký trong hồ sơ
AUR và Git name/email đã cấu hình. Từ thư mục mã nguồn đã clone trên máy Arch,
chạy:

```sh
git clone ssh://aur@aur.archlinux.org/video-downloader-cua-zu.git
cp packaging/aur/PKGBUILD packaging/aur/.SRCINFO video-downloader-cua-zu/
cd video-downloader-cua-zu
# Thêm dòng Maintainer của bạn vào đầu PKGBUILD theo hướng dẫn AUR.
makepkg --printsrcinfo > .SRCINFO
makepkg --cleanbuild
git add PKGBUILD .SRCINFO
git commit -m "Initial import"
git push
```

Khi clone lần đầu, Git có thể báo repository AUR trống; đó là bình thường.
Package chỉ xuất hiện trên AUR sau khi push thành công. Không gửi PKGBUILD
khi dòng Maintainer vẫn còn thiếu hoặc chưa build thử.

Sau khi phát hành tag mới, cập nhật `pkgver` trong `packaging/aur/PKGBUILD`,
sinh `.SRCINFO` trên Arch Linux bằng `makepkg --printsrcinfo > .SRCINFO`, rồi
đẩy hai file đó lên repository AUR `video-downloader-cua-zu` bằng tài khoản
AUR của bạn. Người dùng sau đó có thể cập nhật bằng `paru -Syu`.

### Kiến trúc Linux

Gói Arch, Ubuntu, Linux Mint và Fedora hiện nhắm tới x86_64. Arch không còn
hỗ trợ i686, Fedora không phát hành hệ điều hành x86 32-bit và Linux Mint đã
bỏ bản desktop 32-bit; Windows x86 vẫn được build riêng.

FFmpeg không được đóng gói kèm. Khi phân phối binary, hãy build trên từng OS,
thử binary trên máy sạch và cung cấp FFmpeg theo giấy phép riêng của nó nếu
bạn quyết định phân phối FFmpeg.

## Kiểm thử

```sh
python -m unittest discover -s tests -v
```
