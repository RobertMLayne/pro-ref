
# Optional helper to capture screenshots of the running app
import time, pathlib
from PIL import ImageGrab

def capture(name='screenshot'):
    time.sleep(2)
    img = ImageGrab.grab()
    out = pathlib.Path('docs/images') / f'{name}.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print('Saved', out)

if __name__ == '__main__':
    capture('ui')
