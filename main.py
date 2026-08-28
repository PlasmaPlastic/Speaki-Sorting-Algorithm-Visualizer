import pygame
import random
import time

WIDTH, HEIGHT = 1280, 720
SLICES = 100
TOP_BAR = 40
FPS = 120
STEPS_PER_FRAME = 5

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SSA - Main")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("consolas", 16)
font_menu = pygame.font.SysFont("consolas", 28, bold=True)
font_title = pygame.font.SysFont("consolas", 48, bold=True)
font_btn = pygame.font.SysFont("consolas", 18, bold=True)

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

def bubble_sort(arr):
    n=len(arr); comps=0; swaps=0
    for i in range(n):
        swapped=False
        for j in range(n-1-i):
            comps+=1
            if arr[j]["idx"]>arr[j+1]["idx"]:
                arr[j],arr[j+1]=arr[j+1],arr[j]
                swaps+=1; swapped=True; play_dot_sound(arr[j]["idx"])
                yield j,j+1,comps,swaps,"swap"
            else:
                yield j,j+1,comps,swaps,"compare"
        if not swapped: break

def selection_sort(arr):
    n=len(arr); comps=0; swaps=0
    for i in range(n):
        min_idx=i
        for j in range(i+1,n):
            comps+=1; yield min_idx,j,comps,swaps,"compare"
            if arr[j]["idx"]<arr[min_idx]["idx"]: min_idx=j
        if min_idx!=i:
            arr[i],arr[min_idx]=arr[min_idx],arr[i]
            swaps+=1; play_dot_sound(arr[i]["idx"])
            yield i,min_idx,comps,swaps,"swap"

def insertion_sort(arr):
    n=len(arr); comps=0; swaps=0
    for i in range(1,n):
        key=arr[i]; j=i-1
        while j>=0:
            comps+=1; yield j,j+1,comps,swaps,"compare"
            if arr[j]["idx"]>key["idx"]:
                arr[j+1]=arr[j]; swaps+=1; play_dot_sound(arr[j]["idx"])
                yield j,j+1,comps,swaps,"swap"; j-=1
            else: break
        arr[j+1]=key

def cocktail_sort(arr):
    n=len(arr); comps=0; swaps=0; start=0; end=n-1; swapped=True
    while swapped:
        swapped=False
        for i in range(start,end):
            comps+=1
            if arr[i]["idx"]>arr[i+1]["idx"]:
                arr[i],arr[i+1]=arr[i+1],arr[i]; swaps+=1; swapped=True; play_dot_sound(arr[i]["idx"])
                yield i,i+1,comps,swaps,"swap"
            else: yield i,i+1,comps,swaps,"compare"
        if not swapped: break
        end-=1
        for i in range(end,start-1,-1):
            comps+=1
            if arr[i]["idx"]>arr[i+1]["idx"]:
                arr[i],arr[i+1]=arr[i+1],arr[i]; swaps+=1; swapped=True; play_dot_sound(arr[i]["idx"])
                yield i,i+1,comps,swaps,"swap"
            else: yield i,i+1,comps,swaps,"compare"
        start+=1

def shell_sort(arr):
    n=len(arr); comps=0; swaps=0; gap=n//2
    while gap>0:
        for i in range(gap,n):
            temp=arr[i]; j=i
            while j>=gap:
                comps+=1; yield j-gap,j,comps,swaps,"compare"
                if arr[j-gap]["idx"]>temp["idx"]:
                    arr[j]=arr[j-gap]; swaps+=1; play_dot_sound(arr[j]["idx"])
                    yield j-gap,j,comps,swaps,"swap"; j-=gap
                else: break
            arr[j]=temp
        gap//=2

def quick_sort(arr):
    comps=[0]; swaps=[0]
    def _qs(low,high):
        if low>=high: return
        pivot=arr[high]["idx"]; i=low
        for j in range(low,high):
            comps[0]+=1; yield j,high,comps[0],swaps[0],"compare"
            if arr[j]["idx"]<pivot:
                arr[i],arr[j]=arr[j],arr[i]; swaps[0]+=1; play_dot_sound(arr[i]["idx"])
                yield i,j,comps[0],swaps[0],"swap"; i+=1
        arr[i],arr[high]=arr[high],arr[i]; swaps[0]+=1; play_dot_sound(arr[i]["idx"])
        yield i,high,comps[0],swaps[0],"swap"
        yield from _qs(low,i-1); yield from _qs(i+1,high)
    yield from _qs(0,len(arr)-1)

def merge_sort(arr):
    comps=[0]; swaps=[0]
    def _merge(l,r):
        if r-l<=1: return
        m=(l+r)//2; yield from _merge(l,m); yield from _merge(m,r)
        left=arr[l:m]; right=arr[m:r]; i=j=0; k=l
        while i<len(left) and j<len(right):
            comps[0]+=1; yield l+i,m+j,comps[0],swaps[0],"compare"
            if left[i]["idx"]<=right[j]["idx"]: arr[k]=left[i]; i+=1
            else: arr[k]=right[j]; j+=1; swaps[0]+=1; play_dot_sound(arr[k]["idx"])
            k+=1; yield k-1,k,comps[0],swaps[0],"swap"
        while i<len(left): arr[k]=left[i]; i+=1; k+=1; yield k-1,k,comps[0],swaps[0],"swap"
        while j<len(right): arr[k]=right[j]; j+=1; k+=1; yield k-1,k,comps[0],swaps[0],"swap"
    yield from _merge(0,len(arr))

def heap_sort(arr):
    comps=[0]; swaps=[0]; n=len(arr)
    def heapify(n,i):
        largest=i; l=2*i+1; r=2*i+2
        if l<n:
            comps[0]+=1; yield l,largest,comps[0],swaps[0],"compare"
            if arr[l]["idx"]>arr[largest]["idx"]: largest=l
        if r<n:
            comps[0]+=1; yield r,largest,comps[0],swaps[0],"compare"
            if arr[r]["idx"]>arr[largest]["idx"]: largest=r
        if largest!=i:
            arr[i],arr[largest]=arr[largest],arr[i]; swaps[0]+=1; play_dot_sound(arr[i]["idx"])
            yield i,largest,comps[0],swaps[0],"swap"
            yield from heapify(n,largest)
    for i in range(n//2-1,-1,-1): yield from heapify(n,i)
    for i in range(n-1,0,-1):
        arr[0],arr[i]=arr[i],arr[0]; swaps[0]+=1; play_dot_sound(arr[0]["idx"])
        yield 0,i,comps[0],swaps[0],"swap"
        yield from heapify(i,0)

def counting_sort(arr):
    comps=0; swaps=0; n=len(arr); max_idx=max(x["idx"] for x in arr); count=[0]*(max_idx+1)
    for x in arr: count[x["idx"]]+=1
    k=0
    for i in range(len(count)):
        while count[i]>0:
            for j in range(k,n):
                comps+=1; yield k,j,comps,swaps,"compare"
                if arr[j]["idx"]==i:
                    if j!=k: arr[k],arr[j]=arr[j],arr[k]; swaps+=1; play_dot_sound(arr[k]["idx"]); yield k,j,comps,swaps,"swap"
                    k+=1; break
            count[i]-=1

def radix_sort(arr):
    comps=0; swaps=0; max_idx=max(x["idx"] for x in arr); exp=1; n=len(arr)
    while max_idx//exp>0:
        output=[None]*n; count=[0]*10
        for i in range(n): digit=(arr[i]["idx"]//exp)%10; count[digit]+=1; comps+=1; yield i,digit,comps,swaps,"compare"
        for i in range(1,10): count[i]+=count[i-1]
        for i in range(n-1,-1,-1):
            digit=(arr[i]["idx"]//exp)%10; output[count[digit]-1]=arr[i]; count[digit]-=1; swaps+=1; play_dot_sound(arr[i]["idx"]); yield i,count[digit],comps,swaps,"swap"
        for i in range(n): arr[i]=output[i]
        exp*=10

ALGORITHMS=[
    ("Bubble Sort",bubble_sort),
    ("Selection Sort",selection_sort),
    ("Insertion Sort",insertion_sort),
    ("Cocktail Sort",cocktail_sort),
    ("Shell Sort",shell_sort),
    ("Quick Sort",quick_sort),
    ("Merge Sort",merge_sort),
    ("Heap Sort",heap_sort),
    ("Counting Sort",counting_sort),
    ("Radix Sort",radix_sort),
]

EXIT_RECT = pygame.Rect(WIDTH - 110, 5, 100, 30)

def draw_exit_button():
    hover = EXIT_RECT.collidepoint(pygame.mouse.get_pos())
    color = (220, 60, 60) if hover else (140, 30, 30)
    pygame.draw.rect(screen, color, EXIT_RECT, border_radius=6)
    pygame.draw.rect(screen, (255, 120, 120), EXIT_RECT, 2, border_radius=6)
    txt = font_btn.render("EXIT [X]", True, (255, 255, 255))
    screen.blit(txt, (EXIT_RECT.x + 12, EXIT_RECT.y + 6))
    return EXIT_RECT

def run_menu():
    selected = 0
    menu_rects = [pygame.Rect(WIDTH//2 - 200, 180 + i*48, 400, 40) for i in range(len(ALGORITHMS))]
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(ALGORITHMS)
                elif e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(ALGORITHMS)
                elif e.key == pygame.K_RETURN:
                    return selected
                elif e.key == pygame.K_ESCAPE:
                    return None
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, r in enumerate(menu_rects):
                    if r.collidepoint(e.pos):
                        return i

        screen.fill((15, 15, 25))
        title = font_title.render("SSA", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        subtitle = font_small.render("UP/DOWN: Select  ENTER/CLICK: Start  ESC: Quit", True, (180,180,180))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 130))

        for i, (name, _) in enumerate(ALGORITHMS):
            r = menu_rects[i]
            color = (100,255,150) if i==selected else (220,220,220)
            bg = (40,40,60) if i==selected else (25,25,35)
            pygame.draw.rect(screen, bg, r, border_radius=8)
            if i==selected:
                pygame.draw.rect(screen, (100,255,150), r, 2, border_radius=8)
            text = font_menu.render(f"{'├─' if i < len(ALGORITHMS)-1 else '└─'} {name}", True, color)
            screen.blit(text, (r.x+15, r.y+6))

        pygame.display.flip()
        clock.tick(60)

def run_sort_sequence(start_idx):
    current_idx = start_idx
    while True:
        name, func = ALGORITHMS[current_idx]
        slices = create_shuffled()
        gen = func(slices)
        comparisons=0; swaps=0
        start_time=time.perf_counter()
        finish_time=None
        final_played=False
        highlight_red=None; highlight_green=None
        auto_next_pending=False
        stopped_at_end=False

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        return True
                    if e.key == pygame.K_r:
                        slices=create_shuffled()
                        gen=func(slices)
                        comparisons=0; swaps=0
                        start_time=time.perf_counter()
                        finish_time=None; final_played=False
                        highlight_red=None; highlight_green=None
                        auto_next_pending=False; stopped_at_end=False
                if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
                    if EXIT_RECT.collidepoint(e.pos):
                        return True

            if not final_played:
                try:
                    for _ in range(STEPS_PER_FRAME):
                        r,g,comparisons,swaps,state=next(gen)
                        if state=="swap": highlight_red=r; highlight_green=g
                        else: highlight_red=None; highlight_green=r
                except StopIteration:
                    highlight_red=None; highlight_green=None
                    final_played=True; finish_time=time.perf_counter()
                    if spiki_sound is not None:
                        channel_final.play(spiki_sound)

            if final_played and finish_time is not None:
                elapsed_after=time.perf_counter()-finish_time
                if current_idx==len(ALGORITHMS)-1:
                    if elapsed_after>0.5: stopped_at_end=True
                else:
                    if elapsed_after>2.0 and not channel_final.get_busy():
                        auto_next_pending=True

            screen.fill((0,0,0))
            pygame.draw.rect(screen, (20,20,20), (0,0,WIDTH,TOP_BAR))
            elapsed=time.perf_counter()-start_time
            if stopped_at_end:
                info=f"{name}  Comparisons: {comparisons} | Swaps: {swaps} | Time: {elapsed:.2f}s  [FINISHED - ALL DONE]"
            elif final_played:
                if current_idx < len(ALGORITHMS)-1:
                    next_name=ALGORITHMS[current_idx+1][0]
                    info=f"{name}  Comparisons: {comparisons} | Swaps: {swaps} | Time: {elapsed:.2f}s  -> Next: {next_name} in 2s"
                else:
                    info=f"{name}  Comparisons: {comparisons} | Swaps: {swaps} | Time: {elapsed:.2f}s  [DONE]"
            else:
                info=f"{name}  Comparisons: {comparisons} | Swaps: {swaps} | Time: {elapsed:.2f}s  [R] reset"

            screen.blit(font_small.render(info, True, (255,255,255)), (8,10))
            draw_exit_button()

            for idx,s in enumerate(slices):
                screen.blit(s["img"], (idx*slice_w, TOP_BAR))

            if highlight_red is not None:
                x=highlight_red*slice_w+slice_w//2
                pygame.draw.line(screen, (255,80,80), (x,TOP_BAR), (x,HEIGHT), 3)
            if highlight_green is not None and highlight_green!=highlight_red:
                x=highlight_green*slice_w+slice_w//2
                pygame.draw.line(screen, (100,255,100), (x,TOP_BAR), (x,HEIGHT), 3)

            if stopped_at_end:
                overlay=pygame.Surface((WIDTH, HEIGHT-TOP_BAR), pygame.SRCALPHA)
                overlay.fill((20,20,40,100))
                screen.blit(overlay, (0,TOP_BAR))
                done_txt=font_title.render("ALL SORTS COMPLETE", True, (100,255,150))
                screen.blit(done_txt, (WIDTH//2 - done_txt.get_width()//2, HEIGHT//2 - 40))
                sub=font_menu.render("Press ESC or EXIT to return to menu", True, (255,255,255))
                screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

            pygame.display.flip()
            clock.tick(FPS)

            if auto_next_pending:
                break

            if stopped_at_end:
                waiting=True
                while waiting:
                    for e in pygame.event.get():
                        if e.type==pygame.QUIT: return False
                        if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: waiting=False
                        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                            if EXIT_RECT.collidepoint(e.pos): waiting=False
                    clock.tick(60)
                return True

        if auto_next_pending:
            current_idx+=1
            if current_idx>=len(ALGORITHMS): return True
            continue
        else:
            return True
 
def main():
    while True:
        idx=run_menu()
        if idx is None: break
        go_menu=run_sort_sequence(idx)
        if go_menu is False: break
    pygame.quit()

if __name__=="__main__":
    main()