import pytz
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta

from django.contrib.humanize.templatetags.humanize import intcomma
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now

from .models import ThucDon, DonHang, ChiTietDonHang, DatBan, BanAn, BaoCaoDoanhThu, DanhGia, GioHang, TinNhan, PhienTroChuyen, NguoiDung
from django.contrib import messages
from decimal import Decimal


def login_view(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request)  # Điều hướng dựa trên vai trò nếu đã đăng nhập

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Đăng nhập thành công.')
            return redirect_based_on_role(request)  # Điều hướng dựa trên vai trò sau khi đăng nhập
        else:
            messages.error(request, 'Tên người dùng hoặc mật khẩu không đúng.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công.')
    return redirect('myapp:login')

@login_required
def menu_management(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập trang này.", status=403)

    thuc_don = ThucDon.objects.all()
    return render(request, 'menu_quanly.html', {'thuc_don': thuc_don})

@login_required
def menu_khachhang(request):
    if request.user.vai_tro != 'khach_hang':
        return HttpResponse("Bạn không có quyền truy cập trang này.", status=403)

    thuc_don = ThucDon.objects.all()
    return render(request, 'menu_khachhang.html', {'thuc_don': thuc_don})

@login_required
def redirect_based_on_role(request):
    if request.user.vai_tro == 'quan_ly':
        return redirect('myapp:menu_management')
    elif request.user.vai_tro == 'nhan_vien':
        return redirect('myapp:menu_nhanvien')
    elif request.user.vai_tro == 'khach_hang':
        return redirect('myapp:menu_khachhang')
    else:
        return redirect('myapp:logout')

@login_required
def add_menu_item(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập.", status=403)

    if request.method == "POST":
        ten_mon = request.POST.get('ten_mon')
        gia_tien = request.POST.get('gia_tien')
        hinh_anh = request.FILES.get('hinh_anh')

        try:
            mon = ThucDon(ten_mon=ten_mon, gia_tien=gia_tien, hinh_anh=hinh_anh)
            mon.save()
            messages.success(request, "Thêm món thành công!")
        except Exception as e:
            messages.error(request, f"Lỗi khi thêm món: {str(e)}")

        return redirect('mapp:menu_management')
    return redirect('mapp:menu_management')

@login_required
def edit_menu_item(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập.", status=403)

    if request.method == "POST":
        ma_mon = request.POST.get('ma_mon')
        mon = get_object_or_404(ThucDon, ma_mon=ma_mon)

        mon.ten_mon = request.POST.get('ten_mon')
        mon.gia_tien = request.POST.get('gia_tien')
        if request.FILES.get('hinh_anh'):
            mon.hinh_anh = request.FILES.get('hinh_anh')

        try:
            mon.save()
            messages.success(request, "Sửa món thành công!")
        except Exception as e:
            messages.error(request, f"Lỗi khi sửa món: {str(e)}")

        return redirect('menu_management')
    return redirect('menu_management')

@login_required
def toggle_menu_item_visibility(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập.", status=403)

    if request.method == "POST":
        ma_mon = request.POST.get('ma_mon')
        da_an = request.POST.get('da_an') == 'true'
        mon = get_object_or_404(ThucDon, ma_mon=ma_mon)

        try:
            mon.da_an = da_an
            mon.save()
            action = "Ẩn" if da_an else "Hiện"
            messages.success(request, f"{action} món thành công!")
        except Exception as e:
            messages.error(request, f"Lỗi khi {action.lower()} món: {str(e)}")

    return redirect('myapp:menu_management')

@login_required
def menu_nhanvien(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập trang này.", status=403)

    thuc_don = ThucDon.objects.all()
    return render(request, 'menu_management.html', {'thuc_don': thuc_don})





def order_list(request):
    # Lấy tất cả đơn hàng
    don_hang_list = DonHang.objects.all().order_by('-ngay_tao')

    # Lấy tất cả món ăn
    thuc_don = ThucDon.objects.all()

    # Các lựa chọn cho dropdown
    loai_don_hang_choices = DonHang.LOAI_DON_HANG
    trang_thai_choices = DonHang.TRANG_THAI
    thanh_toan_choices = DonHang.THANH_TOAN

    context = {
        'don_hang_list': don_hang_list,
        'thuc_don': thuc_don,
        'loai_don_hang_choices': loai_don_hang_choices,
        'trang_thai_choices': trang_thai_choices,
        'thanh_toan_choices': thanh_toan_choices,

        'intcomma': intcomma,  # Dùng để định dạng số trong template
    }
    return render(request, 'quanlydonhang_ql.html', context)


from django.contrib.auth.decorators import login_required


@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            ten_khach_hang = request.POST.get('ten_khach_hang')
            loai_don_hang = request.POST.get('loai_don_hang')
            trang_thai = request.POST.get('trang_thai')
            thanh_toan = request.POST.get('thanh_toan')
            dia_chi = request.POST.get('dia_chi', '')
            ngay_tao = request.POST.get('ngay_tao')

            total_money = Decimal(0)
            order_details = []
            thuc_don = ThucDon.objects.all()

            for mon in thuc_don:
                checkbox = request.POST.get(f'mon_an_{mon.ma_mon}')
                quantity = request.POST.get(f'so_luong_{mon.ma_mon}', '0')
                if checkbox and int(quantity) > 0:
                    quantity = int(quantity)
                    subtotal = mon.gia_tien * quantity
                    total_money += subtotal
                    order_details.append({
                        'mon_an': mon,
                        'so_luong': quantity,
                        'gia_tien': mon.gia_tien,
                    })


            don_hang = DonHang.objects.create(
                ten_khach_hang=ten_khach_hang,
                loai_don_hang=loai_don_hang,
                trang_thai=trang_thai,
                thanh_toan=thanh_toan,
                dia_chi=dia_chi if loai_don_hang == 'truc_tuyen' else '',
                ngay_tao=ngay_tao,
                tong_tien=total_money,
            )

            for detail in order_details:
                ChiTietDonHang.objects.create(
                    don_hang=don_hang,
                    mon_an=detail['mon_an'],
                    so_luong=detail['so_luong'],
                    gia_tien=detail['gia_tien'],
                )

            messages.success(request, f'Đơn hàng {don_hang.ma_don_hang} đã được tạo thành công.')
            return redirect('myapp:order_list')

        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra: {str(e)}')
            return redirect('myapp:order_list')

    return redirect('myapp:order_list')


@login_required
def update_order_status(request):
    if request.method == 'POST':
        ma_don_hang = request.POST.get('ma_don_hang')
        trang_thai = request.POST.get('trang_thai')

        try:
            don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang)
            if trang_thai in dict(DonHang.TRANG_THAI).keys():
                don_hang.trang_thai = trang_thai
                don_hang.save()
                messages.success(request, 'Cập nhật trạng thái thành công!')
            else:
                messages.error(request, 'Trạng thái không hợp lệ!')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật trạng thái: {str(e)}')

        return redirect('myapp:order_list')

    return redirect('myapp:order_list')

@login_required
def update_payment_status(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập.", status=403)
    if request.method == 'POST':
        ma_don_hang = request.POST.get('ma_don_hang')
        thanh_toan = request.POST.get('thanh_toan')
        try:
            don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang)
            if thanh_toan in dict(DonHang.THANH_TOAN).keys():
                don_hang.thanh_toan = thanh_toan
                don_hang.save()
                messages.success(request, 'Cập nhật trạng thái thanh toán thành công!')
            else:
                messages.error(request, 'Trạng thái thanh toán không hợp lệ!')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật trạng thái thanh toán: {str(e)}')
        return redirect('myapp:order_list')
    return redirect('myapp:order_list')

@login_required
def order_detail(request, ma_don_hang):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập.", status=403)
    don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang)
    chi_tiet = ChiTietDonHang.objects.filter(don_hang=don_hang).select_related('mon_an')
    context = {
        'don_hang': don_hang,
        'chi_tiet': chi_tiet,
    }
    return render(request, 'order_detail.html', context)


@login_required
def table_management(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      ban_an_list = BanAn.objects.all().order_by('so_ban')
      context = {
          'ban_an_list': ban_an_list,
      }
      return render(request, 'quanlyban.html', context)

@login_required
def update_table_status(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      if request.method == 'POST':
          ma_ban = request.POST.get('ma_ban')
          trang_thai = request.POST.get('trang_thai')

          if trang_thai not in ['trong', 'co_nguoi']:
              messages.error(request, 'Trạng thái không hợp lệ.')
              return redirect('myapp:table_management')

          try:
              ban_an = get_object_or_404(BanAn, ma_ban=ma_ban)
              ban_an.trang_thai = trang_thai
              ban_an.save()
              messages.success(request, 'Cập nhật trạng thái bàn thành công!')
          except Exception as e:
              messages.error(request, f'Lỗi khi cập nhật trạng thái: {str(e)}')

      return redirect('myapp:table_management')

@login_required
def create_table(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      if request.method == 'POST':
          so_ban = request.POST.get('so_ban')
          suc_chua = request.POST.get('suc_chua')

          try:
              suc_chua = int(suc_chua)
              if suc_chua <= 0:
                  messages.error(request, 'Sức chứa phải lớn hơn 0.')
                  return redirect('myapp:table_management')

              if not so_ban.strip():
                  messages.error(request, 'Số bàn không được để trống.')
                  return redirect('myapp:table_management')

              if BanAn.objects.filter(so_ban=so_ban).exists():
                  messages.error(request, f'Bàn {so_ban} đã tồn tại.')
                  return redirect('myapp:table_management')

              BanAn.objects.create(
                  so_ban=so_ban,
                  suc_chua=suc_chua,
                  trang_thai='trong'
              )
              messages.success(request, f'Thêm bàn {so_ban} thành công!')
          except ValueError:
              messages.error(request, 'Sức chứa phải là số nguyên dương.')
          except Exception as e:
              messages.error(request, f'Lỗi khi thêm bàn: {str(e)}')

      return redirect('myapp:table_management')

@login_required
def edit_table(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      if request.method == 'POST':
          ma_ban = request.POST.get('ma_ban')
          so_ban = request.POST.get('so_ban')
          suc_chua = request.POST.get('suc_chua')

          try:
              suc_chua = int(suc_chua)
              if suc_chua <= 0:
                  messages.error(request, 'Sức chứa phải lớn hơn 0.')
                  return redirect('myapp:table_management')

              if not so_ban.strip():
                  messages.error(request, 'Số bàn không được để trống.')
                  return redirect('myapp:table_management')

              ban_an = get_object_or_404(BanAn, ma_ban=ma_ban)
              if so_ban != ban_an.so_ban and BanAn.objects.filter(so_ban=so_ban).exists():
                  messages.error(request, f'Bàn {so_ban} đã tồn tại.')
                  return redirect('myapp:table_management')

              ban_an.so_ban = so_ban
              ban_an.suc_chua = suc_chua
              ban_an.save()
              messages.success(request, f'Sửa bàn {so_ban} thành công!')

          except Exception as e:
              messages.error(request, f'Lỗi khi sửa bàn: {str(e)}')

      return redirect('myapp:table_management')


@login_required
def table_detail(request, ma_ban):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập.", status=403)

    ban_an = get_object_or_404(BanAn, ma_ban=ma_ban)
    dat_ban_list = DatBan.objects.filter(ban_an=ban_an).order_by('-thoi_gian_dat')

    if request.method == 'POST':
        ten_khach = request.POST.get('ten_khach_hang')
        sdt = request.POST.get('so_dien_thoai')
        so_nguoi = request.POST.get('so_nguoi')
        thoi_gian = request.POST.get('thoi_gian_dat')

        so_nguoi = int(so_nguoi) if so_nguoi else 0

        # Kiểm tra dữ liệu
        if so_nguoi <= 0 or so_nguoi > ban_an.suc_chua:
            messages.error(request, f'Số người phải từ 1 đến {ban_an.suc_chua}.')
            return redirect('myapp:table_detail', ma_ban=ma_ban)



        # Kiểm tra thời gian

        thoi_gian = datetime.strptime(thoi_gian, '%Y-%m-%dT%H:%M')
        if thoi_gian < timezone.now():
            messages.error(request, 'Ngày đặt phải lớn hơn ngày hiện tại.')
            return redirect('myapp:table_detail', ma_ban=ma_ban)

        # Tạo đặt bàn
        DatBan.objects.create(
            ban_an=ban_an,
            ten_khach_hang=ten_khach,
            so_dien_thoai_khach_hang=sdt,
            so_nguoi=so_nguoi,
            thoi_gian_dat=thoi_gian,
            trang_thai='cho_xac_nhan'
        )
        messages.success(request, f'Đặt bàn {ban_an.so_ban} thành công!')
        return redirect('myapp:table_detail', ma_ban=ma_ban)

    return render(request, 'quanlydatban.html', {
        'ban_an': ban_an,
        'dat_ban_list': dat_ban_list
    })

@login_required
def update_booking_status(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        return HttpResponse("Bạn không có quyền truy cập.", status=403)

    if request.method == 'POST':
        ma_dat_ban = request.POST.get('ma_dat_ban')
        trang_thai = request.POST.get('trang_thai')
        ma_ban = request.POST.get('ma_ban')

        dat_ban = get_object_or_404(DatBan, ma_dat_ban=ma_dat_ban)
        if trang_thai in ['cho_xac_nhan', 'da_xac_nhan', 'da_huy']:
            dat_ban.trang_thai = trang_thai
            dat_ban.save()
            if trang_thai == 'da_xac_nhan':
                dat_ban.ban_an.trang_thai = 'co_nguoi'
                dat_ban.ban_an.save()
            elif trang_thai == 'da_huy':
                if not DatBan.objects.filter(
                        ban_an=dat_ban.ban_an,
                        trang_thai__in=['cho_xac_nhan', 'da_xac_nhan']
                ).exists():
                    dat_ban.ban_an.trang_thai = 'trong'
                    dat_ban.ban_an.save()
            messages.success(request, 'Cập nhật trạng thái thành công!')
        else:
            messages.error(request, 'Trạng thái không hợp lệ!')
        return redirect('myapp:table_detail', ma_ban=ma_ban)

    return redirect('myapp:table_management')

@login_required
def booking_management(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      ngay_dat = request.GET.get('ngay_dat')
      if not ngay_dat:
          ngay_dat = timezone.now().date()
      ban_an_list = BanAn.objects.all().order_by('so_ban')

      # Lấy tất cả đặt bàn cho mỗi bàn trong ngày chọn
      for ban in ban_an_list:
          bookings = DatBan.objects.filter(ban_an=ban, thoi_gian_dat__date=ngay_dat)
          ban.bookings = bookings

      context = {
          'ban_an_list': ban_an_list,
          'ngay_dat': ngay_dat,
      }
      return render(request, 'quanlydatban.html', context)

@login_required
def create_booking(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      if request.method == 'POST':
          ten_khach_hang = request.POST.get('ten_khach_hang')
          so_dien_thoai_khach_hang = request.POST.get('so_dien_thoai_khach_hang')
          ma_ban = request.POST.get('ban_an')
          thoi_gian_dat = request.POST.get('thoi_gian_dat')
          so_nguoi = request.POST.get('so_nguoi')
          trang_thai = request.POST.get('trang_thai')

          try:
              ban_an = get_object_or_404(BanAn, ma_ban=ma_ban)
              so_nguoi = int(so_nguoi)
              if so_nguoi > ban_an.suc_chua:
                  messages.error(request, f'Số người vượt quá sức chứa của {ban_an.so_ban} ({ban_an.suc_chua} người).')
                  return redirect('myapp:booking_management')

              DatBan.objects.create(
                  ten_khach_hang=ten_khach_hang,
                  so_dien_thoai_khach_hang=so_dien_thoai_khach_hang,
                  ban_an=ban_an,
                  thoi_gian_dat=thoi_gian_dat,
                  so_nguoi=so_nguoi,
                  trang_thai=trang_thai
              )
              messages.success(request, f'Đặt bàn thành công!')
          except Exception as e:
              messages.error(request, f'Lỗi khi thêm đặt bàn: {str(e)}')

      return redirect('myapp:booking_management')

@login_required
def update_booking_status(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      if request.method == 'POST':
          ma_dat_ban = request.POST.get('ma_dat_ban')
          trang_thai = request.POST.get('trang_thai')

          if trang_thai not in ['cho_xac_nhan', 'da_xac_nhan', 'da_huy']:
              messages.error(request, 'Trạng thái không hợp lệ.')
              return redirect('myapp:booking_management')

          try:
              dat_ban = get_object_or_404(DatBan, ma_dat_ban=ma_dat_ban)
              dat_ban.trang_thai = trang_thai
              dat_ban.save()
              messages.success(request, 'Cập nhật trạng thái đặt bàn thành công!')
          except Exception as e:
           messages.error(request, f'Lỗi khi cập nhật trạng thái: {str(e)}')

          return redirect('myapp:booking_management')

@login_required
def cancel_booking(request):
      if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
          return HttpResponse("Bạn không có quyền truy cập.", status=403)

      if request.method == 'POST':
          ma_dat_ban = request.POST.get('ma_dat_ban')
          try:
              dat_ban = get_object_or_404(DatBan, ma_dat_ban=ma_dat_ban)
              dat_ban.trang_thai = 'da_huy'
              dat_ban.save()
              messages.success(request, f'Hủy đặt bàn  thành công!')
          except Exception as e:
              messages.error(request, f'Lỗi khi hủy đặt bàn: {str(e)}')

      return redirect('myapp:booking_management')

# View Quản lý doanh thu
@login_required
def revenue_management(request):
    if request.user.vai_tro != 'quan_ly':
        return HttpResponse("Bạn không có quyền truy cập trang này.", status=403)

    # Giá trị mặc định cho bộ lọc
    ky_bao_cao = request.GET.get('ky_bao_cao', 'hang_ngay')
    ngay_bat_dau = request.GET.get('ngay_bat_dau')
    ngay_ket_thuc = request.GET.get('ngay_ket_thuc')

    # Xác thực và đặt khoảng thời gian
    today = timezone.now().date()
    if not ngay_bat_dau:
        ngay_bat_dau = today - timedelta(days=30)  # Mặc định: 30 ngày trước
    else:
        try:
            ngay_bat_dau = datetime.strptime(ngay_bat_dau, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Ngày bắt đầu không hợp lệ.')
            ngay_bat_dau = today - timedelta(days=30)

    if not ngay_ket_thuc:
        ngay_ket_thuc = today
    else:
        try:
            ngay_ket_thuc = datetime.strptime(ngay_ket_thuc, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Ngày kết thúc không hợp lệ.')
            ngay_ket_thuc = today

    if ngay_bat_dau > ngay_ket_thuc:
        messages.error(request, 'Ngày bắt đầu phải trước ngày kết thúc.')
        ngay_bat_dau, ngay_ket_thuc = ngay_ket_thuc, ngay_bat_dau

    # Truy vấn đơn hàng đã hoàn thành
    orders = DonHang.objects.filter(
        trang_thai='hoan_thanh',
        thanh_toan='da_thanh_toan',
        ngay_tao__date__gte=ngay_bat_dau,
        ngay_tao__date__lte=ngay_ket_thuc
    )

    # Nhóm theo kỳ báo cáo
    if ky_bao_cao == 'hang_ngay':
        orders_by_period = orders.annotate(period=TruncDate('ngay_tao')).values('period').annotate(
            total_revenue=Sum('tong_tien'),
            order_count=Count('ma_don_hang')
        ).order_by('period')
    elif ky_bao_cao == 'hang_tuan':
        orders_by_period = orders.annotate(period=TruncWeek('ngay_tao')).values('period').annotate(
            total_revenue=Sum('tong_tien'),
            order_count=Count('ma_don_hang')
        ).order_by('period')
    elif ky_bao_cao == 'hang_thang':
        orders_by_period = orders.annotate(period=TruncMonth('ngay_tao')).values('period').annotate(
            total_revenue=Sum('tong_tien'),
            order_count=Count('ma_don_hang')
        ).order_by('period')

    # Tính tổng doanh thu và số đơn hàng
    total_revenue = sum(item['total_revenue'] or 0 for item in orders_by_period)
    total_orders = sum(item['order_count'] for item in orders_by_period)

    context = {
        'ky_bao_cao': ky_bao_cao,
        'ngay_bat_dau': ngay_bat_dau,
        'ngay_ket_thuc': ngay_ket_thuc,
        'orders_by_period': orders_by_period,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'ky_bao_cao_choices': BaoCaoDoanhThu.KY_BAO_CAO,
        'intcomma': intcomma,
    }
    return render(request, 'quanlydoanhthu.html', context)


@login_required
def manage_reviews(request):
    if request.user.vai_tro not in ['quan_ly', 'nhan_vien']:
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('myapp:order_list')

    dsdanh_gia = DanhGia.objects.all().order_by('-ngay_tao')
    edit_id = request.GET.get('edit_id')  # Lấy mã đánh giá đang chỉnh sửa

    if request.method == 'POST':
        ma_danh_gia = request.POST.get('ma_danh_gia')
        phan_hoi = request.POST.get('phan_hoi', '').strip()
        danh_gia = get_object_or_404(DanhGia, ma_danh_gia=ma_danh_gia)

        if phan_hoi:
            danh_gia.phan_hoi = phan_hoi
            danh_gia.save()
            messages.success(request, f'Phản hồi cho đánh giá {ma_danh_gia} đã được lưu.')
        else:
            messages.error(request, 'Phản hồi không được để trống.')

        return redirect('myapp:manage_reviews')

    return render(request, 'quanlydanhgia.html', {
        'dsdanh_gia': dsdanh_gia,
        'edit_id': edit_id,
    })
#Chuc nang dat ban - khach hang
# Thiết lập logging
import logging
logger = logging.getLogger(__name__)

@login_required
def place_order(request):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('myapp:redirect_based_on_role')

    if request.method != "POST":
        messages.error(request, 'Yêu cầu không hợp lệ.')
        return render(request, 'error.html', {'message': 'Yêu cầu không hợp lệ.'})

    try:
        selected_items = request.POST.getlist('selected_items')
        loai_don_hang = request.POST.get('loai_don_hang')
        phuong_thuc_thanh_toan = request.POST.get('phuong_thuc_thanh_toan')
        dia_chi = request.POST.get('dia_chi', '')
        so_ban = request.POST.get('so_ban', '')
        so_dien_thoai = request.POST.get('so_dien_thoai', '')
        thoi_gian_dat = request.POST.get('thoi_gian_dat', '')

        logger.debug(f"Form data: selected_items={selected_items}, loai_don_hang={loai_don_hang}, "
                     f"phuong_thuc_thanh_toan={phuong_thuc_thanh_toan}, dia_chi={dia_chi}, "
                     f"so_ban={so_ban}, so_dien_thoai={so_dien_thoai}, thoi_gian_dat={thoi_gian_dat}")

        if not selected_items:
            messages.error(request, 'Vui lòng chọn ít nhất một món.')
            return render(request, 'error.html', {'message': 'Vui lòng chọn ít nhất một món.'})

        # Kiểm tra thời gian quán
        current_time = timezone.now()
        hours, minutes = current_time.hour, current_time.minute
        current_time_in_minutes = hours * 60 + minutes
        opening_time = 7 * 60 + 30  # 7h30
        closing_time = 22 * 60      # 22h
        if loai_don_hang in ['truc_tuyen', 'tai_quan'] and (
            current_time_in_minutes < opening_time or current_time_in_minutes > closing_time
        ):
            messages.error(request, 'Quán chỉ nhận đơn Trực Tuyến và Tại Quán từ 7h30 đến 22h.')
            return render(request, 'error.html', {
                'message': 'Quán chỉ nhận đơn Trực Tuyến và Tại Quán từ 7h30 đến 22h.'
            })

        # Kiểm tra field bắt buộc
        if loai_don_hang == 'truc_tuyen' and (not dia_chi.strip() or not so_dien_thoai.strip()):
            messages.error(request, 'Vui lòng nhập địa chỉ và số điện thoại cho đơn Trực Tuyến.')
            return render(request, 'error.html', {
                'message': 'Vui lòng nhập địa chỉ và số điện thoại cho đơn Trực Tuyến.'
            })
        if loai_don_hang == 'tai_quan' and not so_ban.strip():
            messages.error(request, 'Vui lòng nhập số bàn cho đơn Tại Quán.')
            return render(request, 'error.html', {
                'message': 'Vui lòng nhập số bàn cho đơn Tại Quán.'
            })
        if loai_don_hang == 'mang_di' and (not so_dien_thoai.strip() or not thoi_gian_dat):
            messages.error(request, 'Vui lòng nhập số điện thoại và thời gian đến lấy cho đơn Mang Đi.')
            return render(request, 'error.html', {
                'message': 'Vui lòng nhập số điện thoại và thời gian đến lấy cho đơn Mang Đi.'
            })

        # Chuyển thoi_gian_dat thành datetime
        thoi_gian_dat_dt = None
        if thoi_gian_dat:
            try:
                thoi_gian_dat_dt = timezone.datetime.fromisoformat(thoi_gian_dat.replace('T', ' '))
                if loai_don_hang == 'mang_di':
                    hours, minutes = thoi_gian_dat_dt.hour, thoi_gian_dat_dt.minute
                    time_in_minutes = hours * 60 + minutes
                    if time_in_minutes < opening_time or time_in_minutes > closing_time:
                        messages.error(request, 'Thời gian đến lấy phải từ 7h30 đến 22h.')
                        return render(request, 'error.html', {
                            'message': 'Thời gian đến lấy phải từ 7h30 đến 22h.'
                        })
            except ValueError as e:
                logger.error(f"Lỗi định dạng thoi_gian_dat: {str(e)}")
                messages.error(request, 'Thời gian đến lấy không hợp lệ.')
                return render(request, 'error.html', {
                    'message': 'Thời gian đến lấy không hợp lệ.'
                })

        # Tính tổng tiền và phí ship
        gio_hang = GioHang.objects.filter(nguoi_dung=request.user, mon_an__ma_mon__in=selected_items)
        if not gio_hang.exists():
            messages.error(request, 'Giỏ hàng trống hoặc món đã chọn không hợp lệ.')
            return render(request, 'error.html', {
                'message': 'Giỏ hàng trống hoặc món đã chọn không hợp lệ.'
            })

        tong_tien = sum(item.mon_an.gia_tien * item.so_luong for item in gio_hang)
        phi_ship = 25000 if loai_don_hang == 'truc_tuyen' else 0
        tong_tien += phi_ship

        # Tạo đơn hàng
        don_hang = DonHang(
            nguoi_dung=request.user,
            loai_don_hang=loai_don_hang,
            dia_chi=dia_chi if loai_don_hang == 'truc_tuyen' else '',
            so_ban=so_ban if loai_don_hang == 'tai_quan' else '',
            so_dien_thoai=so_dien_thoai if loai_don_hang in ['truc_tuyen', 'mang_di'] else '',
            thoi_gian_dat=thoi_gian_dat_dt if loai_don_hang == 'mang_di' else None,
            phi_ship=phi_ship,
            tong_tien=tong_tien,
            phuong_thuc_thanh_toan=phuong_thuc_thanh_toan,
            trang_thai='cho_xac_nhan'
        )
        don_hang.save()

        # Tạo chi tiết đơn hàng
        for item in gio_hang:
            ChiTietDonHang.objects.create(
                don_hang=don_hang,
                mon_an=item.mon_an,
                so_luong=item.so_luong,
                gia_tien=item.mon_an.gia_tien
            )
            item.delete()  # Xóa món khỏi giỏ hàng

        logger.info(f"Đơn hàng {don_hang.ma_don_hang} được tạo thành công bởi {request.user.username}")
        return render(request, 'success.html', {
            'ma_don_hang': don_hang.ma_don_hang,
            'message': f'Đơn hàng {don_hang.ma_don_hang} được đặt thành công!',
            'redirect_url': '/orders/'
        })

    except Exception as e:
        logger.error(f"Lỗi khi đặt hàng: {str(e)}", exc_info=True)
        messages.error(request, f'Lỗi server khi đặt hàng: {str(e)}')
        return render(request, 'error.html', {
            'message': f'Lỗi server khi đặt hàng: {str(e)}'
        })

@login_required

def order_history(request):
    logger.info(
        f"User {request.user.username} accessing order_history, Role: {request.user.vai_tro if hasattr(request.user, 'vai_tro') else 'Not set'}"
    )

    # Kiểm tra vai trò người dùng
    if not hasattr(request.user, 'vai_tro') or request.user.vai_tro != 'khach_hang':
        logger.warning(
            f"User {request.user.username} does not have role 'khach_hang'. Redirecting to redirect_based_on_role."
        )
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:redirect_based_on_role')

    # Lấy danh sách đơn hàng
    don_hang_list = DonHang.objects.filter(nguoi_dung=request.user).order_by('-ngay_tao')
    ngay_hien_tai = timezone.now()

    # Xử lý logic kiểm tra đánh giá
    don_hang_data = []
    for don_hang in don_hang_list:
        thoi_gian_da_qua = (ngay_hien_tai - don_hang.ngay_tao).days
        danh_gia = DanhGia.objects.filter(don_hang=don_hang).first()
        can_review = (
            don_hang.trang_thai == 'hoan_thanh' and
            not danh_gia and
            thoi_gian_da_qua <= 10
        )
        don_hang_data.append({
            'don_hang': don_hang,
            'thoi_gian_da_qua': thoi_gian_da_qua,
            'danh_gia': danh_gia,
            'can_review': can_review,
        })

    context = {'don_hang_data': don_hang_data}
    return render(request, 'order_history.html', context)



@login_required
def book_table(request):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('myapp:redirect_based_on_role')

    # Lấy ngày từ query string, mặc định là hôm nay
    ngay_dat = request.GET.get('ngay_dat')
    if ngay_dat:
        try:
            ngay_dat = datetime.strptime(ngay_dat, '%Y-%m-%d').date()
        except ValueError:
            ngay_dat = timezone.now().date()
    else:
        ngay_dat = timezone.now().date()

    # Lấy tất cả bàn
    ban_an_list = BanAn.objects.all().order_by('so_ban')

    # Gán bookings để kiểm tra trạng thái "Đã đặt" theo ngày chọn
    for ban in ban_an_list:
        ban.bookings = DatBan.objects.filter(
            ban_an=ban,
            thoi_gian_dat__date=ngay_dat,
            trang_thai__in=['cho_xac_nhan', 'da_xac_nhan']
        )

    context = {
        'ban_an_list': ban_an_list,
        'ngay_dat': ngay_dat,
    }
    return render(request, 'book_table.html', context)

@login_required
def book_table_form(request, ma_ban):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, 'Bạn không có quyền truy cập.')
        return redirect('myapp:redirect_based_on_role')

    ban_an = get_object_or_404(BanAn, ma_ban=ma_ban)
    if ban_an.trang_thai != 'trong':
        messages.error(request, f'Bàn {ban_an.so_ban} hiện không trống.')
        return redirect('myapp:book_table')

    if request.method == 'POST':
        ten_khach_hang = request.POST.get('ten_khach_hang')
        so_dien_thoai_khach_hang = request.POST.get('so_dien_thoai_khach_hang')
        so_nguoi = request.POST.get('so_nguoi')
        thoi_gian_dat = request.POST.get('thoi_gian_dat')

        try:
            # Kiểm tra dữ liệu
            so_nguoi = int(so_nguoi) if so_nguoi else 0
            if so_nguoi <= 0 or so_nguoi > ban_an.suc_chua:
                messages.error(request, f'Số người phải từ 1 đến {ban_an.suc_chua}.')
                return redirect('myapp:book_table_form', ma_ban=ma_ban)

            if not ten_khach_hang.strip() or not so_dien_thoai_khach_hang.strip():
                messages.error(request, 'Vui lòng nhập tên và số điện thoại.')
                return redirect('myapp:book_table_form', ma_ban=ma_ban)

            # Kiểm tra thời gian
            thoi_gian = datetime.strptime(thoi_gian_dat, '%Y-%m-%dT%H:%M')
            thoi_gian = timezone.make_aware(thoi_gian)
            if thoi_gian < timezone.now():
                messages.error(request, 'Thời gian đặt phải lớn hơn thời gian hiện tại.')
                return redirect('myapp:book_table_form', ma_ban=ma_ban)

            # Kiểm tra giờ quán (7h30 - 22h)
            hours, minutes = thoi_gian.hour, thoi_gian.minute
            time_in_minutes = hours * 60 + minutes
            opening_time = 7 * 60 + 30  # 7h30
            closing_time = 22 * 60      # 22h
            if time_in_minutes < opening_time or time_in_minutes > closing_time:
                messages.error(request, 'Thời gian đặt phải từ 7h30 đến 22h.')
                return redirect('myapp:book_table_form', ma_ban=ma_ban)

            # Kiểm tra bàn có đặt trùng thời gian
            if DatBan.objects.filter(
                ban_an=ban_an,
                thoi_gian_dat__date=thoi_gian.date(),
                thoi_gian_dat__hour=thoi_gian.hour,
                trang_thai__in=['cho_xac_nhan', 'da_xac_nhan']
            ).exists():
                messages.error(request, f'Bàn {ban_an.so_ban} đã được đặt vào thời gian này.')
                return redirect('myapp:book_table_form', ma_ban=ma_ban)

            # Tạo đặt bàn
            dat_ban = DatBan.objects.create(
                nguoi_dung=request.user,
                ban_an=ban_an,
                ten_khach_hang=ten_khach_hang,
                so_dien_thoai_khach_hang=so_dien_thoai_khach_hang,
                so_nguoi=so_nguoi,
                thoi_gian_dat=thoi_gian,
                trang_thai='cho_xac_nhan'
            )

            # Cập nhật trạng thái bàn
            ban_an.trang_thai = 'co_nguoi'
            ban_an.save()

            logger.info(f"Khách hàng {request.user.username} đặt bàn {ban_an.so_ban} vào {thoi_gian}")
            messages.success(request, f'Đặt bàn {ban_an.so_ban} thành công! Vui lòng chờ xác nhận.')
            return redirect('myapp:book_table')

        except ValueError as e:
            logger.error(f"Lỗi định dạng dữ liệu: {str(e)}")
            messages.error(request, 'Dữ liệu không hợp lệ.')
            return redirect('myapp:book_table_form', ma_ban=ma_ban)
        except Exception as e:
            logger.error(f"Lỗi khi đặt bàn: {str(e)}", exc_info=True)
            messages.error(request, f'Lỗi server: {str(e)}')
            return redirect('myapp:book_table_form', ma_ban=ma_ban)

    context = {
        'ban_an': ban_an,
        'ban_an_list': BanAn.objects.all().order_by('so_ban'),  # Gửi danh sách bàn để hiển thị grid
    }
    return render(request, 'book_table.html', context)
#_______________________________________
#Chuc nang tro chuyện
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from .models import NguoiDung, PhienTroChuyen, TinNhan
from django.db.models import Q
import logging

# Thiết lập logging
logger = logging.getLogger(__name__)

@login_required
def message_view(request, phien_id=None):
    logger.debug(f"User: {request.user.username}, Vai_tro: {request.user.vai_tro}, Phien_id: {phien_id}")

    # Lấy danh sách phiên
    search_query = request.GET.get('search', '')
    if request.user.vai_tro == 'khach_hang':
        phien_list = PhienTroChuyen.objects.filter(khach_hang=request.user).order_by('-ngay_tao')
    else:  # nhan_vien hoặc quan_ly
        phien_list = PhienTroChuyen.objects.all().order_by('-ngay_tao')
    if search_query:
        phien_list = phien_list.filter(khach_hang__username__icontains=search_query)
    logger.debug(f"Phien_list for {request.user.username}: {[{p.ma_phien: p.khach_hang.username} for p in phien_list]}, count={phien_list.count()}")

    # Lấy phiên được chọn
    selected_phien = None
    tin_nhan_list = []
    if request.user.vai_tro == 'khach_hang' and not phien_id:
        try:
            selected_phien = PhienTroChuyen.objects.filter(khach_hang=request.user).first()
            if not selected_phien:
                if request.user.username == "admin":  # Ngăn admin tạo phiên với vai trò khach_hang
                    logger.error(f"Tài khoản admin {request.user.username} không được tạo phiên với vai_tro khach_hang")
                    messages.error(request, 'Tài khoản không được phép tạo phiên trò chuyện.')
                    return render(request, 'trochuyen_khach.html', {
                        'phien_list': phien_list,
                        'selected_phien': None,
                        'tin_nhan_list': [],
                        'user': request.user,
                        'no_phien_message': 'Tài khoản không được phép tạo phiên.'
                    })
                selected_phien = PhienTroChuyen.objects.create(
                    khach_hang=request.user,
                    ngay_tao=timezone.now()
                )
                logger.info(f"Tạo phiên mới: ma_phien={selected_phien.ma_phien}, khach_hang={request.user.username}")
            phien_id = selected_phien.ma_phien
        except Exception as e:
            logger.error(f"Lỗi tạo phiên: {str(e)}", exc_info=True)
            messages.error(request, 'Lỗi khi tạo phiên trò chuyện.')
            return render(request, 'trochuyen_khach.html', {
                'phien_list': phien_list,
                'selected_phien': None,
                'tin_nhan_list': [],
                'user': request.user,
                'no_phien_message': 'Lỗi khi tạo phiên trò chuyện.'
            })

    if phien_id:
        try:
            if request.user.vai_tro == 'khach_hang':
                selected_phien = get_object_or_404(PhienTroChuyen, ma_phien=phien_id, khach_hang=request.user)
            else:  # nhan_vien hoặc quan_ly
                selected_phien = get_object_or_404(PhienTroChuyen, ma_phien=phien_id)
                # Kiểm tra khach_hang phải có vai_tro='khach_hang'
                if selected_phien.khach_hang.vai_tro != 'khach_hang':
                    logger.error(f"Phiên {phien_id} có khach_hang sai: {selected_phien.khach_hang.username}, vai_tro: {selected_phien.khach_hang.vai_tro}")
                    messages.error(request, 'Phiên trò chuyện không hợp lệ: Khách hàng không đúng.')
                    return redirect('myapp:message')
            tin_nhan_list = TinNhan.objects.filter(phien_tro_chuyen=selected_phien).order_by('thoi_gian_gui')
            logger.debug(f"Loaded phien: ma_phien={phien_id}, khach_hang={selected_phien.khach_hang.username}, tin_nhan_count={tin_nhan_list.count()}")
        except Exception as e:
            logger.error(f"Lỗi tải phiên {phien_id}: {str(e)}", exc_info=True)
            messages.error(request, 'Lỗi khi tải phiên trò chuyện.')
            return redirect('myapp:message')

    # Xử lý gửi tin nhắn
    if request.method == 'POST' and selected_phien:
        noi_dung = request.POST.get('noi_dung', '').strip()
        hinh_anh = request.FILES.get('hinh_anh')
        if noi_dung or hinh_anh:
            try:
                tin_nhan = TinNhan.objects.create(
                    phien_tro_chuyen=selected_phien,
                    nguoi_gui=request.user,
                    noi_dung=noi_dung,
                    hinh_anh=hinh_anh
                )
                logger.info(f"Tin nhắn mới: ma_phien={selected_phien.ma_phien}, nguoi_gui={request.user.username}, noi_dung={noi_dung[:50]}")
                messages.success(request, 'Gửi tin nhắn thành công.')
            except Exception as e:
                logger.error(f"Lỗi gửi tin nhắn: {str(e)}", exc_info=True)
                messages.error(request, 'Lỗi khi gửi tin nhắn.')
        else:
            messages.error(request, 'Vui lòng nhập nội dung hoặc chọn hình ảnh.')
        return redirect('myapp:message', phien_id=phien_id)

    # Thông báo nếu không có phiên
    no_phien_message = None
    if not phien_list and request.user.vai_tro in ['nhan_vien', 'quan_ly']:
        no_phien_message = 'Chưa có phiên trò chuyện nào.'
    elif not phien_list and request.user.vai_tro == 'khach_hang':
        no_phien_message = 'Chưa có phiên trò chuyện. Bắt đầu ngay!'

    template = 'trochuyen_khach.html' if request.user.vai_tro == 'khach_hang' else 'trochuyen_quanly.html'
    context = {
        'phien_list': phien_list,
        'selected_phien': selected_phien,
        'tin_nhan_list': tin_nhan_list,
        'user': request.user,
        'no_phien_message': no_phien_message,
    }
    return render(request, template, context)
 #________Chuc nang đặt món

@login_required
def menu_khachhang(request):
    if request.user.vai_tro != 'khach_hang':
        return HttpResponse("Bạn không có quyền truy cập trang này.", status=403)

    # Lấy danh sách món ăn chưa ẩn
    thuc_don = ThucDon.objects.filter(da_an=False)

    # Lấy danh sách danh mục duy nhất
    danh_muc_list = ThucDon.objects.filter(da_an=False).values_list('danh_muc', flat=True).distinct()

    # Lấy giỏ hàng
    don_hang = DonHang.objects.filter(
        nguoi_dung=request.user,
        trang_thai='cho_xac_nhan',
        loai_don_hang='truc_tuyen'
    ).first()
    gio_hang = []
    tong_mon_gio_hang = 0
    if don_hang:
        gio_hang = ChiTietDonHang.objects.filter(don_hang=don_hang)
        tong_mon_gio_hang = sum(item.so_luong for item in gio_hang)

    context = {
        'thuc_don': thuc_don,
        'danh_muc_list': danh_muc_list,
        'tong_mon_gio_hang': tong_mon_gio_hang,
        'gio_hang': gio_hang,
    }
    return render(request, 'menu_khachhang.html', context)


@login_required
def add_to_cart(request):
    if request.user.vai_tro != 'khach_hang':
        return HttpResponse("Bạn không có quyền truy cập.", status=403)

    if request.method == "POST":
        ma_mon = request.POST.get('ma_mon')
        so_luong = int(request.POST.get('so_luong', 1))
        mon = get_object_or_404(ThucDon, ma_mon=ma_mon)

        # Lấy hoặc tạo đơn hàng cho người dùng
        don_hang, created = DonHang.objects.get_or_create(
            nguoi_dung=request.user,
            trang_thai='cho_xac_nhan',
            loai_don_hang='truc_tuyen',
            defaults={'tong_tien': 0}
        )

        # Lấy hoặc tạo chi tiết đơn hàng
        chi_tiet, chi_tiet_created = ChiTietDonHang.objects.get_or_create(
            don_hang=don_hang,
            mon_an=mon,
            defaults={'so_luong': so_luong, 'gia_tien': mon.gia_tien}
        )

        if not chi_tiet_created:
            chi_tiet.so_luong += so_luong
            chi_tiet.save()

        # Cập nhật tổng tiền
        don_hang.tong_tien = sum(item.gia_tien * item.so_luong for item in ChiTietDonHang.objects.filter(don_hang=don_hang))
        don_hang.save()

        messages.success(request, f"Đã thêm {mon.ten_mon} vào giỏ hàng!")
        return redirect('myapp:menu_khachhang')

    return redirect('myapp:menu_khachhang')

@login_required
def view_cart(request):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:redirect_based_on_role')

    # Lấy hoặc tạo đơn hàng cho người dùng hiện tại
    don_hang, created = DonHang.objects.get_or_create(
        nguoi_dung=request.user,
        trang_thai='cho_xac_nhan',
        loai_don_hang='truc_tuyen',
        defaults={'tong_tien': 0}
    )

    # Lấy chi tiết giỏ hàng
    gio_hang = ChiTietDonHang.objects.filter(don_hang=don_hang)
    tong_tien = sum(item.gia_tien * item.so_luong for item in gio_hang) if gio_hang.exists() else 0

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        gio_hang_data = [
            {
                'mon_an': {
                    'ma_mon': item.mon_an.ma_mon,
                    'ten_mon': item.mon_an.ten_mon,
                    'gia_tien': float(item.gia_tien),
                    'hinh_anh': item.mon_an.hinh_anh.url if item.mon_an.hinh_anh else None,
                },
                'so_luong': item.so_luong,
            }
            for item in gio_hang
        ]
        return JsonResponse({
            'gio_hang': gio_hang_data,
            'tong_tien': float(tong_tien),
        })

    context = {
        'gio_hang': gio_hang,
        'tong_tien': tong_tien,
    }
    return render(request, 'view_cart.html', context)


@login_required
def update_cart(request):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:redirect_based_on_role')

    if request.method == "POST":
        ma_mon = request.POST.get('ma_mon')
        action = request.POST.get('action')
        try:
            gio_hang = GioHang.objects.get(nguoi_dung=request.user, mon_an__ma_mon=ma_mon)
            if action == 'increase':
                gio_hang.so_luong += 1
                gio_hang.save()
            elif action == 'decrease':
                gio_hang.so_luong -= 1
                if gio_hang.so_luong <= 0:
                    gio_hang.delete()
                    return JsonResponse({'status': 'deleted', 'message': ''})
                gio_hang.save()
            all_gio_hang = GioHang.objects.filter(nguoi_dung=request.user)
            tong_tien = sum(item.mon_an.gia_tien * item.so_luong for item in all_gio_hang)
            return JsonResponse({
                'status': 'success',
                'so_luong': gio_hang.so_luong,
                'tong_tien': float(tong_tien),
                'message': ''
            })
        except GioHang.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Món không tồn tại.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)

@login_required
def place_order_mon(request):
    # Kiểm tra trạng thái đăng nhập
    if not request.user.is_authenticated:
        logger.warning("User is not authenticated")
        return HttpResponse("Vui lòng đăng nhập để tiếp tục.", status=401)

    # Kiểm tra vai trò
    logger.info(
        f"User: {request.user.username}, Vai tro: {request.user.vai_tro if hasattr(request.user, 'vai_tro') else 'Not set'}")
    if not hasattr(request.user, 'vai_tro') or request.user.vai_tro != 'khach_hang':
        logger.warning(
            f"User {request.user.username} does not have role 'khach_hang'. Current role: {request.user.vai_tro if hasattr(request.user, 'vai_tro') else 'Not set'}")
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:redirect_based_on_role')

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)

    try:
        logger.info(f"Received place_order request from user {request.user.username}")
        selected_items = request.POST.getlist('selected_items')
        dia_chi = request.POST.get('dia_chi', '').strip()
        loai_don_hang = request.POST.get('loai_don_hang', 'truc_tuyen')
        so_ban = request.POST.get('so_ban', '').strip()
        so_dien_thoai = request.POST.get('so_dien_thoai', '').strip()
        thoi_gian_dat = request.POST.get('thoi_gian_dat', '')


        logger.debug(
            f"Selected items: {selected_items}, Loai don hang: {loai_don_hang}, Dia chi: {dia_chi}, So dien thoai: {so_dien_thoai}, Thoi gian dat: {thoi_gian_dat}")

        if not selected_items:
            return JsonResponse({'status': 'error', 'message': 'Vui lòng chọn ít nhất một món để đặt hàng.'})

        # Lấy thời gian hiện tại bằng timezone.now() và ép buộc múi giờ +07
        current_time = now()
        logger.info(f"Raw system time from now(): {current_time}, Timezone: {current_time.tzinfo}")
        # Ép buộc múi giờ +07
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time = current_time.astimezone(tz)
        logger.info(f"Adjusted system time to +07: {current_time}, Timezone: {current_time.tzinfo}")
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_in_minutes = current_hour * 60 + current_minute
        logger.info(f"Adjusted time in minutes: {current_time_in_minutes}")
        opening_time = 7 * 60 + 30  # 7h30
        closing_time = 22 * 60  # 22h

        if loai_don_hang in ['truc_tuyen', 'tai_quan']:
            if current_time_in_minutes < opening_time or current_time_in_minutes > closing_time:
                logger.warning(
                    f"Order rejected: Current time {current_time_in_minutes} is outside operating hours ({opening_time}-{closing_time})")
                return JsonResponse(
                    {'status': 'error', 'message': 'Quán chỉ nhận đơn Trực Tuyến và Tại Quán từ 7h30 đến 22h.'})

        if loai_don_hang == 'truc_tuyen':
            if not dia_chi or not any(city in dia_chi.lower() for city in ['đà nẵng', 'da nang']):
                return JsonResponse({'status': 'error', 'message': 'Chúng tôi chỉ giao hàng tại Đà Nẵng.'})
            if not so_dien_thoai:
                return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập số điện thoại.'})
        elif loai_don_hang == 'tai_quan':
            if not so_ban:
                return JsonResponse({'status': 'error', 'message': 'Vui lòng chọn số bàn.'})
        elif loai_don_hang == 'mang_di':
            if not so_dien_thoai:
                return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập số điện thoại.'})
            if not thoi_gian_dat:
                return JsonResponse({'status': 'error', 'message': 'Vui lòng chọn thời gian đến lấy.'})

        phi_ship = 25000 if loai_don_hang == 'truc_tuyen' else 0
        gio_hang_items = GioHang.objects.filter(nguoi_dung=request.user, mon_an__ma_mon__in=selected_items)
        if not gio_hang_items.exists():
            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy món hàng nào trong giỏ.'})

        if not NguoiDung.objects.filter(pk=request.user.pk).exists():
            logger.error(f"User with ID {request.user.pk} does not exist")
            return JsonResponse({'status': 'error', 'message': 'Người dùng không tồn tại.'}, status=400)

        for item in gio_hang_items:
            if not ThucDon.objects.filter(pk=item.mon_an_id).exists():
                logger.error(f"ThucDon with ID {item.mon_an_id} does not exist for GioHang item")
                return JsonResponse({'status': 'error', 'message': f'Món ăn với ID {item.mon_an_id} không tồn tại.'},
                                    status=400)

        tong_tien = sum(item.mon_an.gia_tien * item.so_luong for item in gio_hang_items) + phi_ship

        # Xử lý thoi_gian_dat để tránh lỗi định dạng
        thoi_gian_dat_value = None
        if loai_don_hang in ['tai_quan', 'mang_di'] and thoi_gian_dat:
            try:
                thoi_gian_dat_value = datetime.strptime(thoi_gian_dat, '%Y-%m-%dT%H:%M')
                thoi_gian_dat_value = pytz.timezone('Asia/Ho_Chi_Minh').localize(thoi_gian_dat_value)
                logger.info(f"Parsed thoi_gian_dat: {thoi_gian_dat_value}")
            except ValueError as e:
                logger.error(f"Invalid thoi_gian_dat format: {thoi_gian_dat}, Error: {str(e)}")
                return JsonResponse({'status': 'error',
                                     'message': 'Thời gian đến lấy không hợp lệ. Vui lòng chọn thời gian theo định dạng YYYY-MM-DD HH:MM.'},
                                    status=400)


        don_hang = DonHang(
            nguoi_dung=request.user,
            loai_don_hang=loai_don_hang,
            trang_thai='da_xac_nhan',
            thanh_toan='chua_thanh_toan',
            dia_chi=dia_chi if loai_don_hang == 'truc_tuyen' else '',
            so_dien_thoai=so_dien_thoai if loai_don_hang in ['truc_tuyen', 'mang_di'] else (
                request.user.so_dien_thoai if request.user.so_dien_thoai else ''),
            phi_ship=phi_ship,
            tong_tien=tong_tien,
            thoi_gian_dat=thoi_gian_dat_value,
            ngay_tao=now()
        )
        don_hang.save()
        logger.info(f"Created DonHang with ID: {don_hang.ma_don_hang}")

        for item in gio_hang_items:
            ChiTietDonHang.objects.create(
                don_hang=don_hang,
                mon_an=item.mon_an,
                so_luong=item.so_luong,
                gia_tien=item.mon_an.gia_tien
            )
            item.delete()


        return JsonResponse({'status': 'success', 'ma_don_hang': don_hang.ma_don_hang})

    except Exception as e:
        logger.error(f"Error in place_order: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': f'Lỗi khi tạo đơn hàng: {str(e)}'}, status=500)


@login_required
def order_detail_khach(request, ma_don_hang):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:redirect_based_on_role')

    don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang, nguoi_dung=request.user)
    chi_tiet_don_hang = ChiTietDonHang.objects.filter(don_hang=don_hang)

    # Log trạng thái đơn hàng để kiểm tra
    logger.info(f"Order {ma_don_hang} status: {don_hang.trang_thai}")

    context = {
        'don_hang': don_hang,
        'chi_tiet_don_hang': chi_tiet_don_hang,
    }
    return render(request, 'order_detail_khach.html', context)

@login_required
def cancel_order(request, ma_don_hang):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:redirect_based_on_role')

    don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang, nguoi_dung=request.user)

    if request.method == 'POST':
        if don_hang.trang_thai != 'da_xac_nhan':
            messages.error(request, "Không thể hủy đơn hàng vì đã được xử lý.")
        else:
            don_hang.trang_thai = 'da_huy'
            don_hang.save()
            messages.success(request, f"Đã hủy đơn hàng #{ma_don_hang}.")
        return redirect('myapp:order_history')

    return redirect('myapp:order_detail', ma_don_hang=ma_don_hang)

@login_required
def reorder(request, ma_don_hang):
    if request.user.vai_tro != 'khach_hang':
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:redirect_based_on_role')

    don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang, nguoi_dung=request.user)
    chi_tiet_don_hang = ChiTietDonHang.objects.filter(don_hang=don_hang)

    for chi_tiet in chi_tiet_don_hang:
        mon_an = chi_tiet.mon_an
        if not mon_an.da_an:
            gio_hang, created = GioHang.objects.get_or_create(
                nguoi_dung=request.user,
                mon_an=mon_an,
                defaults={'so_luong': chi_tiet.so_luong}
            )
            if not created:
                gio_hang.so_luong += chi_tiet.so_luong
                gio_hang.save()

    messages.success(request, "Đã thêm các món từ đơn hàng vào giỏ hàng.")
    return redirect('myapp:view_cart')

@login_required
def rate_order(request, ma_don_hang):
    logger.info(
        f"User {request.user.username} attempting to access rate_order for order {ma_don_hang}, Role: {request.user.vai_tro if hasattr(request.user, 'vai_tro') else 'Not set'}"
    )

    # Kiểm tra vai trò người dùng
    if not hasattr(request.user, 'vai_tro') or request.user.vai_tro != 'khach_hang':
        logger.warning(f"User {request.user.username} does not have role 'khach_hang'. Redirecting to order_history.")
        messages.error(request, "Bạn không có quyền truy cập trang này. Vui lòng đăng nhập với tài khoản khách hàng.")
        return redirect('myapp:order_history')

    # Lấy đơn hàng
    don_hang = get_object_or_404(DonHang, ma_don_hang=ma_don_hang, nguoi_dung=request.user)

    # Kiểm tra trạng thái đơn hàng
    if don_hang.trang_thai != 'hoan_thanh':
        messages.error(request, "Chỉ có thể đánh giá các đơn hàng đã hoàn thành.")
        return redirect('myapp:order_history')

    # Kiểm tra thời gian 10 ngày
    thoi_gian_da_qua = (timezone.now() - don_hang.ngay_tao).days
    if thoi_gian_da_qua > 10:
        messages.error(request, "Đã quá 10 ngày kể từ khi đơn hàng được tạo. Bạn không thể đánh giá đơn hàng này.")
        return redirect('myapp:order_history')

    # Kiểm tra xem đã có đánh giá chưa
    danh_gia = DanhGia.objects.filter(don_hang=don_hang).first()
    if danh_gia:
        messages.error(request, "Đơn hàng này đã được đánh giá.")
        return redirect('myapp:order_history')

    if request.method == 'POST':
        diem_danh_gia = int(request.POST.get('diem_danh_gia', 0))
        binh_luan = request.POST.get('binh_luan', '').strip()
        hinh_anh = request.FILES.get('hinh_anh')

        # Kiểm tra điểm đánh giá
        if not (1 <= diem_danh_gia <= 5):
            messages.error(request, "Số sao phải từ 1 đến 5.")
            return redirect('myapp:rate_order', ma_don_hang=ma_don_hang)

        try:
            # Tạo đánh giá
            DanhGia.objects.create(
                nguoi_dung=request.user,
                don_hang=don_hang,
                diem_danh_gia=diem_danh_gia,
                binh_luan=binh_luan,
                hinh_anh=hinh_anh,
                ngay_tao=timezone.now()
            )
            messages.success(request, "Cảm ơn bạn đã đánh giá đơn hàng!")
            return redirect('myapp:order_history')
        except Exception as e:
            logger.error(f"Error in rate_order while creating DanhGia: {str(e)}")
            messages.error(request, f"Lỗi khi gửi đánh giá: {str(e)}")
            return redirect('myapp:rate_order', ma_don_hang=ma_don_hang)

    # Render form nếu là GET
    context = {
        'don_hang': don_hang,
        'thoi_gian_da_qua': thoi_gian_da_qua,
    }
    return render(request, 'rate_order.html', context)


def public_reviews(request):
    logger.info("Accessing public_reviews")

    # Lấy danh sách đánh giá, sắp xếp theo mới nhất
    danh_gia_list = DanhGia.objects.all().order_by('-ngay_tao')

    # Tính toán số lượng đánh giá và tỷ lệ phần trăm cho từng mức sao
    total_reviews = danh_gia_list.count()
    rating_counts = {}
    rating_percentages = {}
    for star in range(1, 6):
        count = danh_gia_list.filter(diem_danh_gia=star).count()
        rating_counts[star] = count
        percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_percentages[star] = round(percentage, 1)

    context = {
        'danh_gia_list': danh_gia_list,
        'total_reviews': total_reviews,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages,
    }
    logger.info(f"Rendering public_reviews.html with {total_reviews} reviews")
    return render(request, 'public_reviews.html', context)

