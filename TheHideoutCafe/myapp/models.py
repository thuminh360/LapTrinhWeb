from django.db import models
from django.contrib.auth.models import AbstractUser

class NguoiDung(AbstractUser):
    VAI_TRO = (
        ('khach_hang', 'Khách Hàng'),
        ('nhan_vien', 'Nhân Viên'),
        ('quan_ly', 'Quản Lý'),
    )
    ma_nguoi_dung = models.AutoField(primary_key=True)
    vai_tro = models.CharField(max_length=20, choices=VAI_TRO, default='khach_hang')
    diem_tich_luy = models.IntegerField(default=0)
    email = models.EmailField(blank=True, null=True)
    so_dien_thoai = models.CharField(max_length=15, blank=True, null=True)
    ho_ten = models.CharField(max_length=100, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='nguoi_dung_groups',
        blank=True,
        help_text='Các nhóm mà người dùng này thuộc về.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='nguoi_dung_permissions',
        blank=True,
        help_text='Các quyền cụ thể của người dùng này.'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Không yêu cầu thêm trường nào ngoài ten_dang_nhap và password

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Người Dùng"
        verbose_name_plural = "Người Dùng"

# Bảng Thực Đơn
class ThucDon(models.Model):
    DANH_MUC = (
        ('Cà Phê', 'Cà Phê'),
        ('Trà Sữa', 'Trà Sữa'),
        ('Nước Ép', 'Nước Ép'),
        ('Đồ Ăn', 'Đồ Ăn'),
    )
    ma_mon = models.AutoField(primary_key=True)
    ten_mon = models.CharField(max_length=100)
    danh_muc = models.CharField(max_length=50, choices=DANH_MUC, default='Cà Phê')

    gia_tien = models.DecimalField(max_digits=10, decimal_places=0)
    hinh_anh = models.ImageField(upload_to='hinh_anh_mon_an/', null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    da_an = models.BooleanField(default=False)

    def __str__(self):
        return self.ten_mon

    class Meta:
        verbose_name = "Thực Đơn"
        verbose_name_plural = "Thực Đơn"
#bảng giỏ hàng
class GioHang(models.Model):
    nguoi_dung = models.ForeignKey('NguoiDung', on_delete=models.CASCADE, related_name='gio_hang')
    mon_an = models.ForeignKey('ThucDon', on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField(default=1)
    ngay_them = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mon_an.ten_mon} (x{self.so_luong}) của {self.nguoi_dung.username}"

    class Meta:
        verbose_name = "Giỏ Hàng"
        verbose_name_plural = "Giỏ Hàng"
        unique_together = ['nguoi_dung', 'mon_an']
# Bảng Đơn Hàng
class DonHang(models.Model):
    LOAI_DON_HANG = (
        ('truc_tuyen', 'Trực Tuyến'),
        ('tai_quan', 'Tại Quán'),
        ('mang_di', 'Mang Đi'),
    )
    TRANG_THAI = (
        ('da_xac_nhan', 'Đã xác nhận'),
        ('dang_che_bien', 'Đang chế biến'),
        ('dang_giao', 'Đang giao'),
        ('hoan_thanh', 'Đã hoàn thành'),
        ('da_huy', 'Đã hủy'),
    )
    THANH_TOAN = (
        ('da_thanh_toan', 'Đã thanh toán'),
        ('chua_thanh_toan', 'Chưa thanh toán'),
    )
    ma_don_hang = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey('NguoiDung', on_delete=models.SET_NULL, null=True, related_name='don_hang')
    loai_don_hang = models.CharField(max_length=20, choices=LOAI_DON_HANG)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default='da_xac_nhan')
    thanh_toan = models.CharField(max_length=20, choices=THANH_TOAN, default='chua_thanh_toan')
    dia_chi = models.TextField(blank=True, null=True)
    so_dien_thoai = models.CharField(max_length=15, blank=True, null=True)
    thoi_gian_dat = models.DateTimeField(blank=True, null=True)
    phi_ship = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    tong_tien = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    ngay_tao = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Đơn Hàng {self.ma_don_hang} - {self.ten_khach_hang or 'Khách vãng lai'}"
    class Meta:
        verbose_name = "Đơn Hàng"
        verbose_name_plural = "Đơn Hàng"

# Bảng Chi Tiết Đơn Hàng
class ChiTietDonHang(models.Model):
    ma_chi_tiet = models.AutoField(primary_key=True)
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE, related_name='chi_tiet_don_hang')
    mon_an = models.ForeignKey(ThucDon, on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField()
    tuy_chinh = models.TextField(blank=True, null=True)
    gia_tien = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.mon_an.ten_mon} trong Đơn Hàng {self.don_hang.ma_don_hang}"

    class Meta:
        verbose_name = "Chi Tiết Đơn Hàng"
        verbose_name_plural = "Chi Tiết Đơn Hàng"


# Bảng Bàn Ăn
class BanAn(models.Model):
    TRANG_THAI = (
        ('trong', 'Trống'),
        ('co_nguoi', 'Có Người'),
    )
    ma_ban = models.AutoField(primary_key=True)
    so_ban = models.CharField(max_length=10, unique=True)
    suc_chua = models.PositiveIntegerField()
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default='trong')

    def __str__(self):
        return f"Bàn {self.so_ban}"

    class Meta:
        verbose_name = "Bàn Ăn"
        verbose_name_plural = "Bàn Ăn"

# Bảng Đặt Bàn
class DatBan(models.Model):
    TRANG_THAI = (
        ('cho_xac_nhan', 'Chờ Xác Nhận'),
        ('da_xac_nhan', 'Đã Xác Nhận'),
        ('da_huy', 'Đã Hủy'),
    )
    ma_dat_ban = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='dat_ban', null=True, blank=True)
    ban_an = models.ForeignKey(BanAn, on_delete=models.CASCADE)
    thoi_gian_dat = models.DateTimeField()
    so_nguoi = models.PositiveIntegerField()
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default='cho_xac_nhan')
    ten_khach_hang = models.CharField(max_length=100, blank=True, null=True)
    so_dien_thoai_khach_hang = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Đặt Bàn {self.ban_an.so_ban} vào {self.thoi_gian_dat}"

    class Meta:
        verbose_name = "Đặt Bàn"
        verbose_name_plural = "Đặt Bàn"

# Bảng Đánh Giá
class DanhGia(models.Model):
    ma_danh_gia = models.AutoField(primary_key=True)
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='danh_gia')
    don_hang = models.OneToOneField(DonHang, on_delete=models.CASCADE)
    diem_danh_gia = models.PositiveIntegerField()
    binh_luan = models.TextField(blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    phan_hoi = models.TextField(blank=True, null=True)
    da_an = models.BooleanField(default=False)
    hinh_anh = models.ImageField(upload_to='danh_gia/', null=True, blank=True)

    def __str__(self):
        return f"Đánh Giá cho Đơn Hàng {self.don_hang.ma_don_hang} bởi {self.nguoi_dung.username}"

    class Meta:
        verbose_name = "Đánh Giá"
        verbose_name_plural = "Đánh Giá"

# Bảng Mã Giảm Giá
class MaGiamGia(models.Model):
    ma_giam_gia = models.AutoField(primary_key=True)
    ma_code = models.CharField(max_length=20, unique=True)
    gia_tri = models.DecimalField(max_digits=10, decimal_places=0)
    ngay_het_han = models.DateTimeField()
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, related_name='ma_giam_gia', null=True, blank=True)

    def __str__(self):
        return self.ma_code

    class Meta:
        verbose_name = "Mã Giảm Giá"
        verbose_name_plural = "Mã Giảm Giá"




# Bảng Phiên Trò Chuyện
class PhienTroChuyen(models.Model):
    ma_phien = models.AutoField(primary_key=True)
    khach_hang = models.ForeignKey(
        NguoiDung, on_delete=models.CASCADE,
        related_name='phien_tro_chuyen_khach_hang',
        limit_choices_to={'vai_tro': 'khach_hang'}
    )
    cua_hang = models.ForeignKey(
        NguoiDung, on_delete=models.CASCADE,
        related_name='phien_tro_chuyen_quan',
        limit_choices_to={'vai_tro__in': ['nhan_vien', 'quan_ly'],},
        null=True, blank=True
    )
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Phiên với {self.khach_hang.username}"

    class Meta:
        verbose_name = "Phiên Trò Chuyện"
        verbose_name_plural = "Phiên Trò Chuyện"
# Bảng Tin Nhắn
class TinNhan(models.Model):

    ma_tin_nhan = models.AutoField(primary_key=True)
    phien_tro_chuyen = models.ForeignKey(PhienTroChuyen, on_delete=models.CASCADE, related_name='tin_nhan')
    nguoi_gui = models.ForeignKey(NguoiDung, on_delete=models.CASCADE)
    thoi_gian_gui = models.DateTimeField(auto_now_add=True)
    noi_dung = models.TextField(blank=True, null=True)  # Cho phép noi_dung rỗng khi gửi hình
    hinh_anh = models.ImageField(upload_to='tin_nhan_images/', blank=True, null=True)  # Thêm trường hình ảnh

    def __str__(self):
        return f"Tin Nhắn trong Phiên {self.phien_tro_chuyen.ma_phien} "

    class Meta:
        verbose_name = "Tin Nhắn"
        verbose_name_plural = "Tin Nhắn"
# Bảng Báo Cáo Doanh Thu
class BaoCaoDoanhThu(models.Model):
    KY_BAO_CAO = (
        ('hang_ngay', 'Hàng Ngày'),
        ('hang_tuan', 'Hàng Tuần'),
        ('hang_thang', 'Hàng Tháng'),
    )
    ma_bao_cao = models.AutoField(primary_key=True)
    ky_bao_cao = models.CharField(max_length=20, choices=KY_BAO_CAO)
    tong_doanh_thu = models.DecimalField(max_digits=15, decimal_places=0)
    ngay_bat_dau = models.DateTimeField()
    ngay_ket_thuc = models.DateTimeField()

    def __str__(self):
        return f"Báo Cáo {self.ky_bao_cao} từ {self.ngay_bat_dau} đến {self.ngay_ket_thuc}"

    class Meta:
        verbose_name = "Báo Cáo Doanh Thu"
        verbose_name_plural = "Báo Cáo Doanh Thu"