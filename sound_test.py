import pygame
import time
import os

# --- 配置 ---
SOUND_FILE = "correct.wav"
# ---

def play_sound():
    if not os.path.exists(SOUND_FILE):
        print(f"错误：找不到音效文件 '{SOUND_FILE}'！")
        print("请确保该文件与脚本在同一个文件夹下。")
        return

    print("正在初始化 Pygame Mixer...")
    try:
        pygame.mixer.init()
        print("Mixer 初始化成功。")
    except Exception as e:
        print(f"Mixer 初始化失败: {e}")
        return

    print(f"正在加载音效: {SOUND_FILE}")
    try:
        sound = pygame.mixer.Sound(SOUND_FILE)
        print("音效加载成功。")
    except Exception as e:
        print(f"音效加载失败: {e}")
        return

    print("准备播放音效...")
    try:
        sound.play()
        print("正在播放！你应该能听到声音。")
        # 等待音效播放完成
        while pygame.mixer.get_busy():
            time.sleep(0.1)
        print("播放结束。")
    except Exception as e:
        print(f"播放时发生错误: {e}")

if __name__ == "__main__":
    play_sound()
    # 在程序退出前留出一点时间，确保能看到所有打印信息
    time.sleep(3) 