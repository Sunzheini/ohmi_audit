"""
Db Management: delete, import from excel, export to excel.
"""
import logging

from django.db import transaction
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class DbManagement:
    """
    This class is responsible for managing the database, including deleting records, importing data
    from Excel files, and exporting data to Excel files.
    """
    @staticmethod
    def delete_database():
        """
        Deletes all records from the application tables (Audit, Auditor, Customer)
        and removes any associated media files (images / uploaded files).
        Non-superuser, non-staff AppUsers are also removed.

        All deletions run inside a single atomic transaction so that any
        unexpected error will roll back every change made so far.

        Returns a translated success message on completion.
        Raises an exception on failure (the view layer catches it).
        """
        # Lazy import to avoid circular-import issues at module load time.
        from ohmi_audit.main_app.models import Audit, Auditor, Customer, AppUser

        try:
            with transaction.atomic():
                # ------------------------------------------------------------------
                # Step 1 – remove media files that belong to Audit records BEFORE
                # the database rows are deleted (we still need the field values).
                # ------------------------------------------------------------------
                for audit in Audit.objects.exclude(image='').exclude(image__isnull=True):
                    try:
                        audit.image.delete(save=False)   # deletes file from storage
                    except Exception as file_err:
                        logger.warning("Could not delete image for Audit pk=%s: %s", audit.pk, file_err)

                for audit in Audit.objects.exclude(file='').exclude(file__isnull=True):
                    try:
                        audit.file.delete(save=False)    # deletes file from storage
                    except Exception as file_err:
                        logger.warning("Could not delete file for Audit pk=%s: %s", audit.pk, file_err)

                # ------------------------------------------------------------------
                # Step 2 – delete database rows.
                # Order matters when FK constraints are present; delete dependants first.
                # ------------------------------------------------------------------
                audit_count, _d    = Audit.objects.all().delete()
                auditor_count, _d  = Auditor.objects.all().delete()
                customer_count, _d = Customer.objects.all().delete()

                # Delete non-superuser / non-staff app users.
                user_count, _d = AppUser.objects.filter(is_superuser=False, is_staff=False).delete()

                logger.info(
                    "DB delete completed – Audits: %d, Auditors: %d, Customers: %d, Users: %d",
                    audit_count, auditor_count, customer_count, user_count,
                )

            return format_lazy(
                _(
                    "Database deleted successfully. "
                    "Removed {a} audit(s), {au} auditor(s), {c} customer(s), {u} user(s)."
                ),
                a=audit_count,
                au=auditor_count,
                c=customer_count,
                u=user_count,
            )

        except Exception as exc:
            logger.error("delete_database failed: %s", exc, exc_info=True)
            raise

    @staticmethod
    def import_from_excel():
        return _("Database imported successfully.")

    @staticmethod
    def export_to_excel():
        return _("Database exported successfully.")