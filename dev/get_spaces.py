import os
import sys

import django


sys.path.extend(['..'])

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Rizya.settings")
django.setup()


from User.models import User
from Space.models import SpaceMan


user = User.objects.get(pk=1)
print(user.spaceman_set.dict(SpaceMan.d_user))
