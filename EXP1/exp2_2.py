#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炫酷版心理旋转实验 (Mental Rotation Task)
基于 Shepard & Metzler (1971) 经典范式
使用 3D 风格字母 'F'，支持 Same / Mirror 判断
自动绘制 RT vs 角度图，保存数据与图像
"""

from psychopy import visual, core, event, gui, data
import random
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ======================
# 1. 实验信息 & 被试信息
# ======================
exp_info = {'被试编号': '01', '姓名': ''}
dlg = gui.DlgFromDict(dictionary=exp_info, title="心理旋转实验")
if not dlg.OK:
    core.quit()

# 创建数据文件夹
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)
filename = os.path.join(data_dir, f"MR_sub{exp_info['被试编号']}_{data.getDateStr()}")

# ======================
# 2. 创建窗口
# ======================
win = visual.Window(
    size=[1024, 768],
    fullscr=False,  # 设为 True 可全屏
    color='black',
    units='pix',
    screen=0
)

# ======================
# 3. 刺激与参数
# ======================
# 使用粗体、3D风格的字母（通过偏移模拟立体感）
def make_3d_letter(win, pos, ori=0, color='white', text='F', flip_horiz=False):
    """创建带简单3D效果的字母"""
    # 主干
    main = visual.TextStim(win, text=text, pos=pos, ori=ori, 
                          color=color, height=80, bold=True, font='Arial', flipHoriz=flip_horiz)
    # 阴影（偏移模拟立体）
    shadow = visual.TextStim(win, text=text, pos=(pos[0]+4, pos[1]-4), ori=ori,
                            color='gray', height=80, bold=True, font='Arial', flipHoriz=flip_horiz)
    return [shadow, main]  # 先画阴影，再画主体

# 定义可用字母，不能有对称轴的字母
letters = [ 'F', 'G', 'J', 'K', 'L',  'P', 'Q', 'R', 'S',  'Z']

angles = [0,30, 60,90, 120,150, 180]
trials = []

# 构建试次：每个角度下，Same 和 Mirror 各 4 次（共 7 * 2 * 4 = 56试次）
for angle in angles:
    for _ in range(4):
        letter = random.choice(letters)
        trials.append({'angle': angle, 'same': True, 'letter': letter})
    for _ in range(4):
        letter = random.choice(letters)
        trials.append({'angle': angle, 'same': False, 'letter': letter})

random.shuffle(trials)

# 练习试次：随机 8 个试次
practice_trials = []
for _ in range(8):
    angle = random.choice(angles)
    same = random.choice([True, False])
    letter = random.choice(letters)
    practice_trials.append({'angle': angle, 'same': same, 'letter': letter})

# 指导语
instructions = visual.TextStim(
    win, text=
    "欢迎参加心理旋转实验！\n\n"
    "屏幕上会同时出现两个 3D 字母（随机选择）。\n"
    "请判断它们是否为**同一个物体**（只是旋转了角度）。\n\n"
    "按 F 键:是 Same \n"
    "按 J 键:否 Mirror 镜像 \n\n"
    "请又快又准地按键。\n\n"
    "首先是练习阶段，按空格键开始练习...",
    color='white', wrapWidth=800, height=30
)

instructions.draw()
win.flip()
event.waitKeys(keyList=['space'])

# ======================
# 4. 练习阶段
# ======================
practice_results = []
feedback_text = visual.TextStim(win, text='', color='white', height=40, pos=(0, -100))

for i, trial in enumerate(practice_trials):
    # 注视点 (动态脉动效果)
    for frame in range(30):  # ~0.5秒
        alpha = abs(np.sin(frame * 0.2))  # 脉动
        fixation = visual.TextStim(win, text='+', color='white', height=40)
        fixation.opacity = alpha
        fixation.draw()
        win.flip()
    
    # 准备刺激
    left_stims = make_3d_letter(win, pos=(-250, 0), ori=0, text=trial['letter'])
    
    if trial['same']:
        right_stims = make_3d_letter(win, pos=(250, 0), ori=trial['angle'], text=trial['letter'], flip_horiz=False)
    else:
        right_stims = make_3d_letter(win, pos=(250, 0), ori=trial['angle'], text=trial['letter'], flip_horiz=True)
    
    # 呈现刺激
    for stim in left_stims:
        stim.draw()
    for stim in right_stims:
        stim.draw()
    start_time = win.flip()
    
    # 等待反应
    keys = event.waitKeys(keyList=['f', 'j'], timeStamped=True, maxWait=5.0)
    if keys is None:
        rt = 5.0
        key = None
        correct = False
    else:
        key, press_time = keys[0]
        rt = press_time - start_time
        correct = (key == 'f' and trial['same']) or (key == 'j' and not trial['same'])
    
    # 反馈
    if correct:
        feedback_text.text = "正确！"
        feedback_text.color = 'green'
    else:
        feedback_text.text = "错误！"
        feedback_text.color = 'red'
    
    feedback_text.draw()
    win.flip()
    core.wait(1.0)
    
    # 记录练习数据（可选）
    practice_results.append({
        'trial': i + 1,
        'angle': trial['angle'],
        'same': trial['same'],
        'letter': trial['letter'],
        'response': key,
        'rt': rt,
        'correct': correct
    })

# 保存练习数据
df_practice = pd.DataFrame(practice_results)
df_practice.to_csv(filename + '_practice.csv', index=False, encoding='utf-8-sig')

# 练习结束提示
practice_end = visual.TextStim(
    win, text="练习结束！\n\n正式实验即将开始。\n\n按空格键开始正式实验...",
    color='yellow', height=30
)
practice_end.draw()
win.flip()
event.waitKeys(keyList=['space'])

# ======================
# 5. 正式实验流程
# ======================
results = []
fixation = visual.TextStim(win, text='+', color='white', height=40)

for i, trial in enumerate(trials):
    # 显示进度
    progress_text = visual.TextStim(win, text=f"Trial {i+1}/{len(trials)}", color='white', height=30, pos=(0, 300))
    progress_text.draw()
    win.flip()
    core.wait(1.0)
    
    # 注视点 (动态脉动效果)
    for frame in range(30):  # ~0.5秒
        alpha = abs(np.sin(frame * 0.2))  # 脉动
        fixation.opacity = alpha
        fixation.draw()
        win.flip()
    
    # 准备刺激
    left_stims = make_3d_letter(win, pos=(-250, 0), ori=0, text=trial['letter'])
    
    if trial['same']:
        right_stims = make_3d_letter(win, pos=(250, 0), ori=trial['angle'], text=trial['letter'], flip_horiz=False)
    else:
        right_stims = make_3d_letter(win, pos=(250, 0), ori=trial['angle'], text=trial['letter'], flip_horiz=True)
    
    # 呈现刺激
    for stim in left_stims:
        stim.draw()
    for stim in right_stims:
        stim.draw()
    start_time = win.flip()
    
    # 等待反应
    keys = event.waitKeys(keyList=['f', 'j'], timeStamped=True, maxWait=5.0)
    if keys is None:
        rt = 5.0
        key = None
        correct = False
        timeout_text = visual.TextStim(win, text="Too slow!", color='red', height=40, pos=(0, 0))
        timeout_text.draw()
        win.flip()
        core.wait(1.0)
    else:
        key, press_time = keys[0]
        rt = press_time - start_time
        correct = (key == 'f' and trial['same']) or (key == 'j' and not trial['same'])
    
    # 记录数据
    results.append({
        'trial': i + 1,
        'angle': trial['angle'],
        'same': trial['same'],
        'letter': trial['letter'],
        'response': key,
        'rt': rt,
        'correct': correct
    })
    
    # 空屏
    win.flip()
    core.wait(0.5)

# ======================
# 6. 结果分析与可视化
# ======================
df = pd.DataFrame(results)
df.to_csv(filename + '.csv', index=False, encoding='utf-8-sig')

# 只分析正确试次
df_correct = df[df['correct']]

# 按角度计算平均 RT 和正确率
rt_by_angle = df_correct.groupby('angle')['rt'].agg(['mean', 'std', 'count']).reset_index()
acc_by_angle = df.groupby('angle')['correct'].agg(['mean', 'std', 'count']).reset_index()

# 绘图：反应时 vs 旋转角度 和 正确率 vs 旋转角度
plt.style.use('seaborn-v0_8-darkgrid')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))

# 子图1：反应时
ax1.scatter(df_correct['angle'], df_correct['rt'], 
           alpha=0.6, color='cyan', edgecolors='white', s=60, label='Individual Trials')
ax1.errorbar(rt_by_angle['angle'], rt_by_angle['mean'], 
            yerr=rt_by_angle['std'], 
            fmt='o', color='red', ecolor='red', capsize=5, 
            markersize=10, label='Mean Reaction Time')
if len(rt_by_angle) > 1:
    coef = np.polyfit(rt_by_angle['angle'], rt_by_angle['mean'], 1)
    poly1d_fn = np.poly1d(coef)
    ax1.plot(rt_by_angle['angle'], poly1d_fn(rt_by_angle['angle']), 
            '--', color='orange', linewidth=2, label=f'Linear Fit (slope={coef[0]:.4f})')
ax1.set_xlabel('Rotation Angle (°)', fontsize=12)
ax1.set_ylabel('Reaction Time (s)', fontsize=12)
ax1.set_title('Reaction Time vs Rotation Angle', fontsize=14, color='white')
ax1.set_facecolor('black')
ax1.spines['bottom'].set_color('white')
ax1.spines['left'].set_color('white')
ax1.tick_params(colors='white')
ax1.legend(facecolor='black', labelcolor='white')

# 子图2：正确率
ax2.scatter(df['angle'], df['correct'], 
           alpha=0.6, color='cyan', edgecolors='white', s=60, label='Individual Trials')
ax2.errorbar(acc_by_angle['angle'], acc_by_angle['mean'], 
            yerr=acc_by_angle['std'], 
            fmt='o', color='red', ecolor='red', capsize=5, 
            markersize=10, label='Mean Accuracy')
ax2.set_xlabel('Rotation Angle (°)', fontsize=12)
ax2.set_ylabel('Accuracy', fontsize=12)
ax2.set_title('Accuracy vs Rotation Angle', fontsize=14, color='white')
ax2.set_facecolor('black')
ax2.spines['bottom'].set_color('white')
ax2.spines['left'].set_color('white')
ax2.tick_params(colors='white')
ax2.legend(facecolor='black', labelcolor='white')

# 保存图像
fig.savefig(filename + '_results.png', dpi=150, bbox_inches='tight', facecolor='black')
plt.show()

# ======================
# 7. 结束语
# ======================
end_text = visual.TextStim(
    win, text=
    "实验结束！\n\n"
    "感谢您的参与！\n\n"
    f"平均反应时: {df['rt'].mean():.3f} 秒\n"
    f"正确率: {df['correct'].mean()*100:.1f}%\n\n"
    "结果图已保存。",
    color='lightgreen', height=30
)
end_text.draw()
win.flip()
core.wait(4)

win.close()
core.quit()