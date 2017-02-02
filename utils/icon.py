import sys
import os

moduleDir = sys.modules[__name__].__file__
iconPath = '%s' % os.environ['RFSCRIPT']

ok = '%s/icons/%s' % (iconPath, 'OK_icon.png')
no = '%s/icons/%s' % (iconPath, 'X_icon.png')
dir = '%s/icons/%s' % (iconPath, 'dir_icon.png')
nodir = '%s/icons/%s' % (iconPath, 'nodir_icon.png')
maya = '%s/icons/%s' % (iconPath, 'maya_icon.png')

# sg
sgWtg = '%s/icons/%s' % (iconPath, 'wtg_icon.png')
sgAprv = '%s/icons/%s' % (iconPath, 'aprv_icon.png')
sgFix = '%s/icons/%s' % (iconPath, 'fix_icon.png')
sgHold = '%s/icons/%s' % (iconPath, 'hld_icon.png')
sgIp = '%s/icons/%s' % (iconPath, 'ip_icon.png')
sgLate = '%s/icons/%s' % (iconPath, 'late_icon.png')
sgRevise = '%s/icons/%s' % (iconPath, 'rev_icon.png')
sgRdy = '%s/icons/%s' % (iconPath, 'rdy_icon.png')
sgNa = '%s/icons/%s' % (iconPath, 'sgna_icon.png')
