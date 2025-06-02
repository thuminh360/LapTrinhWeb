from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    NguoiDung, ThucDon, DonHang, ChiTietDonHang, GioHang, BanAn,
    DatBan, DanhGia, PhienTroChuyen, TinNhan, BaoCaoDoanhThu
)

admin.site.register(NguoiDung)
admin.site.register(ThucDon)
admin.site.register(DonHang)
admin.site.register(ChiTietDonHang)
admin.site.register(GioHang)
admin.site.register(BanAn)
admin.site.register(DatBan)
admin.site.register(DanhGia)
admin.site.register(PhienTroChuyen)
admin.site.register(TinNhan)
admin.site.register(BaoCaoDoanhThu)