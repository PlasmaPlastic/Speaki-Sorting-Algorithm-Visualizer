
import pygame
import random
import time

WIDTH, HEIGHT = 1280, 720
SLICES = 100
TOP_BAR = 30
FPS = 120
STEPS_PER_FRAME = 5

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shell Sort - dot.mp3 + spiki.mp3")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("consolas", 16)

pygame.mixer.init()
pygame.mixer.set_num_channels(64)

try:
    dot_base_sound = pygame.mixer.Sound("dot.mp3")
except Exception:
    dot_base_sound = None

dot_channels = [pygame.mixer.Channel(i) for i in range(32)]
next_dot_ch = 0

def play_dot_sound(original_idx):
    global next_dot_ch
    if dot_base_sound is not None:
        ch = dot_channels[next_dot_ch % len(dot_channels)]
        ch.set_volume(0.6 + (original_idx / SLICES) * 0.4)
        ch.play(dot_base_sound)
        next_dot_ch += 1

try:
    spiki_sound = pygame.mixer.Sound("spiki.mp3")
except Exception:
    spiki_sound = None

channel_final = pygame.mixer.Channel(40)

def load_speaki():
    for p in ["speaki_final.png", "speaki.png"]:
        try:
            return pygame.image.load(p).convert()
        except Exception:
            pass
    return pygame.Surface((WIDTH, HEIGHT - TOP_BAR))

orig = pygame.transform.smoothscale(load_speaki(), (WIDTH, HEIGHT - TOP_BAR))
slice_w = WIDTH // SLICES
base_pieces = [orig.subsurface(pygame.Rect(i * slice_w, 0, slice_w, HEIGHT - TOP_BAR)).copy() for i in range(SLICES)]

def create_shuffled():
    arr = [{"img": base_pieces[i], "idx": i} for i in range(SLICES)]
    random.shuffle(arr)
    return arr


def shell_sort(arr):
    n = len(arr)
    comps = 0
    swaps = 0
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap:
                comps += 1
                yield j - gap, j, comps, swaps, "compare"
                if arr[j - gap]["idx"] > temp["idx"]:
                    arr[j] = arr[j - gap]
                    swaps += 1
                    play_dot_sound(arr[j]["idx"])
                    yield j - gap, j, comps, swaps, "swap"
                    j -= gap
                else:
                    break
            arr[j] = temp
        gap //= 2
ALGO_FUNC = shell_sort


slices = None
gen = None
comparisons = 0
swaps = 0
start_time = 0
finish_time = None
final_played = False
highlight_red = None
highlight_green = None

def reset_sort():
    global slices, gen, comparisons, swaps, start_time, finish_time, final_played, highlight_red, highlight_green
    slices = create_shuffled()
    gen = ALGO_FUNC(slices)
    comparisons = 0
    swaps = 0
    start_time = time.perf_counter()
    finish_time = None
    final_played = False
    highlight_red = None
    highlight_green = None

reset_sort()
running = True

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            reset_sort()

    if not final_played:
        try:
            for _ in range(STEPS_PER_FRAME):
                r, g, comparisons, swaps, state = next(gen)
                if state == "swap":
                    highlight_red = r
                    highlight_green = g
                else:
                    highlight_red = None
                    highlight_green = r
        except StopIteration:
            highlight_red = None
            highlight_green = None
            final_played = True
            finish_time = time.perf_counter()
            if spiki_sound is not None:
                channel_final.play(spiki_sound)

    if final_played and finish_time is not None:
        if time.perf_counter() - finish_time > 2:
            if not channel_final.get_busy():
                reset_sort()

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (20, 20, 20), (0, 0, WIDTH, TOP_BAR))

    elapsed = time.perf_counter() - start_time
    info = f"Shell Sort  Comparisons: {comparisons} | Swaps: {swaps} | Time: {elapsed:.2f}s  [R] reset"
    screen.blit(font_small.render(info, True, (255, 255, 255)), (8, 7))

    for idx, s in enumerate(slices):
        screen.blit(s["img"], (idx * slice_w, TOP_BAR))

    if highlight_red is not None:
        x = highlight_red * slice_w + slice_w // 2
        pygame.draw.line(screen, (255, 80, 80), (x, TOP_BAR), (x, HEIGHT), 3)

    if highlight_green is not None and highlight_green != highlight_red:
        x = highlight_green * slice_w + slice_w // 2
        pygame.draw.line(screen, (100, 255, 100), (x, TOP_BAR), (x, HEIGHT), 3)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
