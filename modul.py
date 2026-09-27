import os
from build123d import *

# ==========================================
# THÔNG SỐ THIẾT KẾ CƠ KHÍ CHUẨN IN 3D FDM
# ==========================================
SERVO_W = 20.0      # Chiều rộng Servo tiêu chuẩn (mm)
SERVO_L = 40.0      # Chiều dài Servo (mm)
SERVO_H = 40.0      # Chiều cao Servo (mm)
HORN_R = 10.0       # Bán kính tròn của cùi răng servo horn
CLEARANCE = 0.2     # Dung sai lắp ráp cho nhựa co ngót
WALL_T = 4.5        # Độ dày thành chịu lực tối thiểu cho robot 80cm
BOLT_R = 1.6        # Bán kính lỗ vít M3 (Đường kính 3.2mm)
INSERT_R = 2.1      # Bán kính lỗ cấy ren đồng nhiệt M3 (Đường kính 4.2mm)

# Tạo thư mục đầu ra
os.makedirs("output_cad", exist_ok=True)

# ==========================================
# PART 1: BRACKET_HIP (Gá hông bắt vào thân)
# ==========================================
def design_hip_bracket():
    with BuildPart() as p:
        # Khối hộp bao ngoài Servo Hip
        Box(SERVO_W + WALL_T*2, SERVO_L + WALL_T*2, SERVO_H + WALL_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # Khoét rỗng lòng đặt servo và khe đi dây
        with BuildPart(mode=Mode.SUBTRACT):
            Box(SERVO_W + CLEARANCE*2, SERVO_L + CLEARANCE*2, SERVO_H + 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
            Box(SERVO_W - 4, SERVO_L + 10, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Tạo tai cánh gá bắt vít vào khung sườn chính robot
        with BuildPart(mode=Mode.ADD):
            Box(SERVO_W + WALL_T*6, 15, WALL_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
                
        # Đục lỗ vít M3 và lỗ đóng ren cấy nhiệt brass insert
        with BuildPart(mode=Mode.SUBTRACT):
            # Lỗ gá khung thân sườn (2 bên tai)
            with Locations(Pos((SERVO_W + WALL_T*4)/2, 0, WALL_T/2), Pos(-(SERVO_W + WALL_T*4)/2, 0, WALL_T/2)):
                Cylinder(radius=BOLT_R, height=20)
            # Lỗ bắt tai servo hông
            with Locations(Pos(0, (SERVO_L + WALL_T)/2, SERVO_H - 5), Pos(0, -(SERVO_L + WALL_T)/2, SERVO_H - 5)):
                Cylinder(radius=INSERT_R, height=15, rotation=(90, 0, 0))
                
    return p.part

# ==========================================
# PART 2: LINK_THIGH (XƯƠNG ĐÙI CHỊU LỰC CHỮ I)
# ==========================================
def design_thigh_link():
    length_thigh = 200.0 # Chiều dài tâm trục theo yêu cầu robot 80cm
    with BuildPart() as p:
        # Thân xương dạng dầm chữ I để tăng mô-men chống uốn khi robot dập chân
        Box(WALL_T * 3, length_thigh + 40, WALL_T * 4, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        
        # Đầu tròn liên kết với trục gá Servo Hip hông
        with Locations(Pos(0, -length_thigh/2, 0)):
            Cylinder(radius=HORN_R + WALL_T, height=SERVO_W + WALL_T, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            
        # Đầu gá tích hợp luôn khoang chứa hộp động cơ Servo gối (Knee Servo)
        with Locations(Pos(0, length_thigh/2, 0)):
            Box(SERVO_W + WALL_T*2, SERVO_L + WALL_T*2, SERVO_H + WALL_T*2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            
        # Các bước cắt gọt khoét rãnh giảm trọng lượng và tạo không gian lắp đặt
        with BuildPart(mode=Mode.SUBTRACT):
            # Khoét lòng xương chữ I hai bên sườn
            with Locations(Pos(WALL_T*1.2, 0, 0), Pos(-WALL_T*1.2, 0, 0)):
                Box(WALL_T, length_thigh - 30, WALL_T * 2.5, align=(Align.CENTER, Align.CENTER, Align.CENTER))
            # Khoét hộp chứa Servo Knee
            with Locations(Pos(0, length_thigh/2, 0)):
                Box(SERVO_W + CLEARANCE*2, SERVO_L + CLEARANCE*2, SERVO_H + 10, align=(Align.CENTER, Align.CENTER, Align.CENTER))
                Cylinder(radius=BOLT_R, height=SERVO_W + 50, rotation=(0, 90, 0))
            # Hốc đặt Servo Horn tròn ở đầu hông
            with Locations(Pos(0, -length_thigh/2, (SERVO_W + WALL_T)/2 - 2)):
                Cylinder(radius=HORN_R, height=4)
                Cylinder(radius=BOLT_R, height=30)
                
    return p.part

# ==========================================
# PART 3: LINK_KNEE (CẲNG CHÂN TIẾP ĐỊA CÔN)
# ==========================================
def design_knee_shin():
    length_shin = 220.0 # Chiều dài cẳng chân dưới tiếp đất
    with BuildPart() as p:
        # Tạo phôi côn to ở gối nhỏ dần về bàn chân để tối ưu phân phối ứng suất lực
        Cone(bottom_radius=18, top_radius=10, height=length_shin, align=(Align.CENTER, Align.CENTER, Align.MIN))
        
        # Cùm chữ U bắt vào trục xoay bản lề của khớp gối
        with Locations(Pos(0, 0, length_shin)):
            Box(SERVO_W + WALL_T*2 + CLEARANCE*2, 35, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
        # Khoét rãnh cùm chữ U để ôm vừa khít đầu xương đùi
        with BuildPart(mode=Mode.SUBTRACT):
            with Locations(Pos(0, 0, length_shin - 2)):
                Box(SERVO_W + CLEARANCE*2, 40, 45, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Trục chốt xuyên tâm bản lề bản xoay
                Cylinder(radius=BOLT_R, height=SERVO_W + 30, rotation=(0, 90, 0))
                # Lỗ đóng tán đồng cấy nhiệt bắt vít cố định đĩa truyền lực servo
                with Locations(Pos((SERVO_W+WALL_T)/2, 0, 20), Pos(-(SERVO_W+WALL_T)/2, 0, 20)):
                    Cylinder(radius=INSERT_R, height=10, rotation=(0, 90, 0))
                    
        # Bo tròn hình cầu tại gót bàn chân (Foot pad) để bọc đệm cao su bám sàn cứu hộ
        with Locations(Pos(0, 0, 0)):
            Sphere(radius=12, mode=Mode.ADD)
            
    return p.part

# ==========================================
# THỰC THI XUẤT FILE VẬT LÝ (.STEP VÀ .STL)
# ==========================================
print("[XZORT CAD] Đang xử lý hình học không gian...")
hip = design_hip_bracket()
thigh = design_thigh_link()
knee = design_knee_shin()

print("[XZORT CAD] Đang xuất file lưới in 3D và file lắp ráp gốc...")

# SỬA LỖI: Sử dụng bộ hàm xuất tập trung toàn cục (Exporter Functions) chuẩn API mới
export_step(hip, "output_cad/XZORT_Part1_Hip_Bracket.step")
export_stl(hip, "output_cad/XZORT_Part1_Hip_Bracket.stl")

export_step(thigh, "output_cad/XZORT_Part2_Thigh_Link.step")
export_stl(thigh, "output_cad/XZORT_Part2_Thigh_Link.stl")

export_step(knee, "output_cad/XZORT_Part3_Knee_Shin.step")
export_stl(knee, "output_cad/XZORT_Part3_Knee_Shin.stl")

# Tạo cụm lắp ráp mô phỏng tổng thể (Assembly)
assembly = Compound(label="XZORT_Full_Leg_Assembly", children=[
    hip.moved(Location(Pos(0, -100, 20), (0, 90, 0))),
    thigh.moved(Location(Pos(0, 0, 0), (0, 0, 0))),
    knee.moved(Location(Pos(0, 100, -220), (0, 35, 0))) # Giả lập tư thế khuỵu chân chịu lực 35 độ
])
export_step(assembly, "output_cad/XZORT_Assembly_Full_Leg.step")

print("\n[THÀNH CÔNG MỸ MÃN] Toàn bộ file đã được lưu vào thư mục '/output_cad/'!")
