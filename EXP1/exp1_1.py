#在屏幕中左右各显示一张图像，并显示提示词：要求用户选择一张图像，并根据选择点击键盘按键N或M（此处可以设置为其它键盘按键）。等待用户点击键盘，输出根据键盘判定点击的图像是哪一张，并输出从显示图像到用户点击键盘的时间。请注意图像的选择，避免在显示中图像的压缩变形。

from PIL import Image
from psychopy import visual, core, event, monitors
import os

# === 1. 设置 ===
mon = monitors.Monitor('testMonitor')
mon.setSizePix([2560, 1440])
mon.setWidth(50)

win = visual.Window(
    size=[1280, 720],  # 可根据屏幕调整
    fullscr=False,
    color='black',
    units='pix',
    monitor=mon
)

# === 2. 准备两个大帅哥===
left_img_path = 'left.jpg'  # 彭于晏
right_img_path = 'right.jpg' # 吴彦祖

# 检查文件是否存在
if not os.path.exists(left_img_path) or not os.path.exists(right_img_path):
    print("照片放入当前目录！")
    core.quit()

# 读取图像原始尺寸
left_pil = Image.open(left_img_path)
right_pil = Image.open(right_img_path)

left_w, left_h = left_pil.size
right_w, right_h = right_pil.size

# 设定目标宽度，高度按比例缩放
target_width = 300

left_size = (target_width, target_width * left_h / left_w)
right_size = (target_width, target_width * right_h / right_w)

# 加载图像，保持原始比例，设置合适大小
left_img = visual.ImageStim(
    win, image=left_img_path,
    pos=(-400, 0),  # 左侧
    size=left_size  # 自动保持比例，也可手动设如 size=(300, 300)
)

right_img = visual.ImageStim(
    win, image=right_img_path,
    pos=(400, 0),  # 右侧
    size=right_size
)

# 提示文字
instr_text = visual.TextStim(
    win, text='知道大家是大帅哥，请选择大家觉得自己跟谁比较像：按 N 选彭于晏，按 M 选吴彦祖',
    pos=(0, -300), color='white', height=30
)

# === 3. 显示刺激并等待响应 ===
left_img.draw()
right_img.draw()
instr_text.draw()
start_time = win.flip()  


# 等待按键（N 或 M）
keys = event.waitKeys(keyList=['n', 'm'], timeStamped=True)  # 返回 (key, time)
key, press_time = keys[0]

# 计算反应时
rt = press_time - start_time

# === 4. 输出结果 ===
if key == 'n':
    choice = '左图'
elif key == 'm':
    choice = '右图'

print(f"用户选择了：{choice}")
print(f"反应时间：{rt:.3f} 秒")

# === 5. 结束 ===
core.wait(2)  # 显示结果2秒
win.close()
core.quit()