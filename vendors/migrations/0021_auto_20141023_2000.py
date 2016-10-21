# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0020_auto_20140930_1435'),
    ]

    operations = [
        migrations.RunSQL(
            """ALTER TABLE "vendors_vendors" ALTER COLUMN "annual_revenue" DROP DEFAULT; """
            ),
        migrations.RunSQL("""ALTER TABLE "vendors_vendors"  ALTER COLUMN "annual_revenue" TYPE BIGINT USING annual_revenue::bigint;  """
            )
    ]
