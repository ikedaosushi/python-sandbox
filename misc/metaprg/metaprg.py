from pathlib import Path

etc_dir = Path('/etc')
init_dir = 'init.d'
print(etc_dir / init_dir / 'reboot')
# => /etc/init.d/reboot

class myPath():
    def __init__(self, path):
        self._path = path
    
    def __truediv__(self, add_path):
        self._path = self._path + '/' + add_path
        return self

    def __str__(self):
        return self._path

etc_dir = myPath('/etc')
init_dir = 'init.d'
print(etc_dir / init_dir / 'reboot')
# => /etc/init.d/reboot