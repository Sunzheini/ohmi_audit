"""
Tests for DbManagement.delete_database and DbManagement.import_from_excel.

Organisation:
  ┌─ helpers / fixtures  (module-level)
  ├─ TestDeleteDatabase   – @pytest.mark.django_db
  ├─ TestMapHeaders       – pure unit, no DB
  ├─ TestBuildCustomerRecord – pure unit, no DB
  └─ TestImportFromExcel  – @pytest.mark.django_db
"""
import io
import pytest
import openpyxl
from pathlib import Path
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.utils import timezone

from common.db_management import DbManagement
from ohmi_audit.main_app.models import Audit, Auditor, Customer

UserModel = get_user_model()


# =============================================================================
# Module-level helpers
# =============================================================================

# The exact header row used in test_data.xlsx (trailing space on 'Company ID ' is intentional)
VALID_HEADERS = ('year', 'BG Vor.Nr.', 'Unternehmen-bg', 'Unternehmen-en', 'Company ID ', 'VAT')


def _make_xlsx(*rows):
    """
    Build an in-memory .xlsx file from a sequence of row tuples.
    Returns a BytesIO positioned at the start, ready to pass to openpyxl.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(list(row))
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def _make_valid_xlsx(*data_rows):
    """Shortcut: prepend the standard VALID_HEADERS row automatically."""
    return _make_xlsx(VALID_HEADERS, *data_rows)


def _customer_row(
    year=2026,
    bg_vor_nr='BG-001/24',
    name_bg='Тест ООД',
    name_en='TEST LTD',
    company_id=123456789,
    vat='BG123456789',
):
    """Return a single data row tuple with sensible defaults."""
    return (year, bg_vor_nr, name_bg, name_en, company_id, vat)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def superuser(db):
    return UserModel.objects.create_superuser(
        username='admin', email='admin@example.com',
        password='admin123', first_name='Admin',
    )


@pytest.fixture
def staff_user(db):
    return UserModel.objects.create_user(
        username='staff', email='staff@example.com',
        password='staff123', first_name='Staff', is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    return UserModel.objects.create_user(
        username='regular', email='regular@example.com',
        password='pass123', first_name='Regular',
    )


@pytest.fixture
def sample_audit(db):
    return Audit.objects.create(
        name='Test Audit',
        description='desc',
        date=timezone.now().date(),
        is_active=True,
    )


@pytest.fixture
def sample_auditor(db):
    return Auditor.objects.create(
        first_name='John', last_name='Doe',
        email='john@example.com', phone='+1234567890',
    )


@pytest.fixture
def sample_customer(db):
    """Customer matching the default _customer_row() values."""
    return Customer.objects.create(
        year=2026,
        BG_Vor_Nr='BG-001/24',
        company_name_bg='Тест ООД',
        company_name_en='TEST LTD',
        company_id=123456789,
        VAT_number='BG123456789',
    )


# =============================================================================
# delete_database
# =============================================================================

@pytest.mark.django_db
class TestDeleteDatabase:

    # ── deletion coverage ────────────────────────────────────────────────────

    def test_deletes_all_audits(self, sample_audit):
        DbManagement.delete_database()
        assert Audit.objects.count() == 0

    def test_deletes_all_auditors(self, sample_auditor):
        DbManagement.delete_database()
        assert Auditor.objects.count() == 0

    def test_deletes_all_customers(self, sample_customer):
        DbManagement.delete_database()
        assert Customer.objects.count() == 0

    def test_deletes_non_staff_non_superuser_users(self, regular_user):
        DbManagement.delete_database()
        assert not UserModel.objects.filter(pk=regular_user.pk).exists()

    def test_deletes_multiple_records(self, db):
        """Ensures bulk deletion works regardless of record count."""
        for i in range(5):
            Customer.objects.create(
                year=2026, BG_Vor_Nr=f'BG-{i:03d}/24',
                company_name_bg='Тест', company_name_en='Test',
                company_id=i, VAT_number=f'BG{i}',
            )
        DbManagement.delete_database()
        assert Customer.objects.count() == 0

    # ── preservation ─────────────────────────────────────────────────────────

    def test_preserves_superuser(self, superuser):
        DbManagement.delete_database()
        assert UserModel.objects.filter(pk=superuser.pk).exists()

    def test_preserves_staff_user(self, staff_user):
        DbManagement.delete_database()
        assert UserModel.objects.filter(pk=staff_user.pk).exists()

    # ── return value ─────────────────────────────────────────────────────────

    def test_returns_success_message(self, db):
        message = str(DbManagement.delete_database())
        assert 'deleted successfully' in message.lower()

    def test_message_contains_zero_counts_on_empty_db(self, db):
        message = str(DbManagement.delete_database())
        # No records exist so all counts should be 0
        assert 'Removed 0 audit(s)' in message

    def test_message_counts_match_deleted_records(self, sample_audit, sample_auditor, sample_customer):
        message = str(DbManagement.delete_database())
        assert 'Removed 1 audit(s), 1 auditor(s), 1 customer(s)' in message

    # ── media file cleanup ───────────────────────────────────────────────────

    def test_image_field_delete_called(self, db):
        """FieldFile.delete(save=False) should be invoked for audits that have an image."""
        audit = Audit.objects.create(
            name='Img Audit', date=timezone.now().date(), is_active=True,
        )
        # Give the audit a fake non-empty image name so it passes the exclude() filter
        Audit.objects.filter(pk=audit.pk).update(image='audit_images/fake.jpg')
        audit.refresh_from_db()

        with patch('django.db.models.fields.files.FieldFile.delete') as mock_file_delete:
            DbManagement.delete_database()

        mock_file_delete.assert_called()
        assert Audit.objects.count() == 0

    # ── atomic rollback ───────────────────────────────────────────────────────

    def test_rolls_back_on_error(self, sample_audit):
        """
        If an error occurs mid-transaction, all preceding deletions must be
        rolled back – sample_audit should still exist after the failed call.
        """
        # Make Auditor.objects.all() return a mock whose .delete() raises
        mock_qs = MagicMock()
        mock_qs.delete.side_effect = RuntimeError("forced rollback")

        with patch.object(Auditor.objects, 'all', return_value=mock_qs):
            with pytest.raises(RuntimeError, match="forced rollback"):
                DbManagement.delete_database()

        # Transaction was rolled back – the Audit row must still be there
        assert Audit.objects.filter(pk=sample_audit.pk).exists()


# =============================================================================
# _map_headers  (pure unit – no DB)
# =============================================================================

class TestMapHeaders:

    def test_basic_mapping(self):
        row = ('year', 'BG Vor.Nr.', 'Unternehmen-bg')
        result = DbManagement._map_headers(row)
        assert result == {'year': 0, 'bg vor.nr.': 1, 'unternehmen-bg': 2}

    def test_strips_whitespace(self):
        # 'Company ID ' has a trailing space – must become 'company id'
        row = ('  Year  ', '  Company ID  ')
        result = DbManagement._map_headers(row)
        assert 'year' in result
        assert 'company id' in result

    def test_lowercases_headers(self):
        row = ('YEAR', 'BG VOR.NR.', 'VAT')
        result = DbManagement._map_headers(row)
        assert 'year' in result
        assert 'bg vor.nr.' in result
        assert 'vat' in result

    def test_skips_none_cells(self):
        row = ('year', None, 'vat')
        result = DbManagement._map_headers(row)
        assert None not in result
        assert 'year' in result
        assert 'vat' in result

    def test_column_index_is_zero_based(self):
        row = ('year', 'bg vor.nr.', 'vat')
        result = DbManagement._map_headers(row)
        assert result['year'] == 0
        assert result['bg vor.nr.'] == 1
        assert result['vat'] == 2

    def test_real_excel_headers_normalised(self):
        """The actual VALID_HEADERS tuple must produce the keys expected by COLUMN_MAP."""
        result = DbManagement._map_headers(VALID_HEADERS)
        assert 'year' in result
        assert 'bg vor.nr.' in result
        assert 'unternehmen-bg' in result
        assert 'unternehmen-en' in result
        assert 'company id' in result   # trailing space stripped
        assert 'vat' in result


# =============================================================================
# _build_customer_record  (pure unit – no DB)
# =============================================================================

class TestBuildCustomerRecord:

    @staticmethod
    def _header_map():
        return DbManagement._map_headers(VALID_HEADERS)

    # ── happy path ───────────────────────────────────────────────────────────

    def test_valid_row_returns_all_fields(self):
        row = _customer_row()
        record = DbManagement._build_customer_record(row, self._header_map())

        assert record['year']            == 2026
        assert record['BG_Vor_Nr']       == 'BG-001/24'
        assert record['company_name_bg'] == 'Тест ООД'
        assert record['company_name_en'] == 'TEST LTD'
        assert record['company_id']      == 123456789
        assert record['VAT_number']      == 'BG123456789'

    def test_integer_fields_have_int_type(self):
        row = _customer_row()
        record = DbManagement._build_customer_record(row, self._header_map())
        assert isinstance(record['year'],       int)
        assert isinstance(record['company_id'], int)

    def test_string_fields_have_str_type(self):
        row = _customer_row()
        record = DbManagement._build_customer_record(row, self._header_map())
        assert isinstance(record['BG_Vor_Nr'],       str)
        assert isinstance(record['company_name_bg'], str)
        assert isinstance(record['company_name_en'], str)
        assert isinstance(record['VAT_number'],      str)

    def test_field_values_are_stripped(self):
        # Excel cells sometimes have surrounding whitespace
        row = ('  2026  ', '  BG-001/24  ', '  Тест ООД  ', '  TEST LTD  ', '  123456789  ', '  BG123456789  ')
        record = DbManagement._build_customer_record(row, self._header_map())
        assert record['BG_Vor_Nr']       == 'BG-001/24'
        assert record['company_name_en'] == 'TEST LTD'
        assert record['year']            == 2026

    # ── blank rows ───────────────────────────────────────────────────────────

    def test_all_none_row_returns_none(self):
        row = (None, None, None, None, None, None)
        assert DbManagement._build_customer_record(row, self._header_map()) is None

    def test_all_whitespace_row_returns_none(self):
        row = ('  ', '  ', '  ', '  ', '  ', '  ')
        assert DbManagement._build_customer_record(row, self._header_map()) is None

    # ── error cases ──────────────────────────────────────────────────────────

    def test_missing_required_column_raises_value_error(self):
        incomplete_map = {'year': 0}     # all other columns absent
        with pytest.raises(ValueError, match="not found in the Excel file"):
            DbManagement._build_customer_record(_customer_row(), incomplete_map)

    def test_empty_required_field_raises_value_error(self):
        # year is None – should raise with the field name in the message
        row = (None, 'BG-001/24', 'Тест', 'Test', 123, 'BG123')
        with pytest.raises(ValueError, match="year"):
            DbManagement._build_customer_record(row, self._header_map())

    def test_non_integer_year_raises_value_error(self):
        row = ('not_a_year', 'BG-001/24', 'Тест', 'Test', 123, 'BG123')
        with pytest.raises(ValueError, match="Invalid value"):
            DbManagement._build_customer_record(row, self._header_map())

    def test_non_integer_company_id_raises_value_error(self):
        row = (2026, 'BG-001/24', 'Тест', 'Test', 'not_an_id', 'BG123')
        with pytest.raises(ValueError, match="Invalid value"):
            DbManagement._build_customer_record(row, self._header_map())


# =============================================================================
# import_from_excel  (integration – needs DB)
# =============================================================================

@pytest.mark.django_db
class TestImportFromExcel:

    # ── creates / updates ────────────────────────────────────────────────────

    def test_creates_single_customer(self, db):
        xlsx = _make_valid_xlsx(_customer_row())
        DbManagement.import_from_excel(xlsx)
        assert Customer.objects.filter(BG_Vor_Nr='BG-001/24').exists()

    def test_creates_correct_field_values(self, db):
        xlsx = _make_valid_xlsx(_customer_row())
        DbManagement.import_from_excel(xlsx)
        c = Customer.objects.get(BG_Vor_Nr='BG-001/24')
        assert c.year            == 2026
        assert c.company_name_bg == 'Тест ООД'
        assert c.company_name_en == 'TEST LTD'
        assert c.company_id      == 123456789
        assert c.VAT_number      == 'BG123456789'

    def test_imports_multiple_rows(self, db):
        xlsx = _make_valid_xlsx(
            _customer_row(bg_vor_nr='BG-001/24'),
            _customer_row(bg_vor_nr='BG-002/24', name_en='SECOND LTD'),
            _customer_row(bg_vor_nr='BG-003/24', name_en='THIRD LTD'),
        )
        DbManagement.import_from_excel(xlsx)
        assert Customer.objects.count() == 3

    def test_updates_existing_customer_on_reimport(self, sample_customer):
        """Re-importing must update the row, not create a duplicate."""
        xlsx = _make_valid_xlsx(
            _customer_row(bg_vor_nr='BG-001/24', name_en='UPDATED NAME LTD')
        )
        DbManagement.import_from_excel(xlsx)

        assert Customer.objects.filter(BG_Vor_Nr='BG-001/24').count() == 1
        assert Customer.objects.get(BG_Vor_Nr='BG-001/24').company_name_en == 'UPDATED NAME LTD'

    def test_update_does_not_create_new_row(self, sample_customer):
        xlsx = _make_valid_xlsx(_customer_row(bg_vor_nr='BG-001/24'))
        DbManagement.import_from_excel(xlsx)
        assert Customer.objects.count() == 1   # still only one

    # ── blank row handling ───────────────────────────────────────────────────

    def test_skips_blank_rows_between_data(self, db):
        xlsx = _make_valid_xlsx(
            _customer_row(bg_vor_nr='BG-001/24'),
            (None, None, None, None, None, None),   # blank
            _customer_row(bg_vor_nr='BG-002/24', name_en='SECOND LTD'),
        )
        DbManagement.import_from_excel(xlsx)
        assert Customer.objects.count() == 2

    def test_trailing_blank_rows_ignored(self, db):
        xlsx = _make_valid_xlsx(
            _customer_row(bg_vor_nr='BG-001/24'),
            (None, None, None, None, None, None),
            (None, None, None, None, None, None),
        )
        DbManagement.import_from_excel(xlsx)
        assert Customer.objects.count() == 1

    # ── return message ───────────────────────────────────────────────────────

    def test_returns_string_message(self, db):
        xlsx = _make_valid_xlsx(_customer_row())
        message = str(DbManagement.import_from_excel(xlsx))
        assert isinstance(message, str)
        assert len(message) > 0

    def test_message_contains_created_count(self, db):
        xlsx = _make_valid_xlsx(
            _customer_row(bg_vor_nr='BG-001/24'),
            _customer_row(bg_vor_nr='BG-002/24', name_en='SECOND'),
        )
        message = str(DbManagement.import_from_excel(xlsx))
        assert 'Created: 2' in message

    def test_message_contains_updated_count(self, sample_customer):
        xlsx = _make_valid_xlsx(_customer_row(bg_vor_nr='BG-001/24'))
        message = str(DbManagement.import_from_excel(xlsx))
        assert 'Updated: 1' in message

    def test_message_contains_skipped_blank_count(self, db):
        xlsx = _make_valid_xlsx(
            _customer_row(bg_vor_nr='BG-001/24'),
            (None, None, None, None, None, None),   # blank
        )
        message = str(DbManagement.import_from_excel(xlsx))
        assert 'Skipped (blank): 1' in message

    def test_message_contains_error_count(self, db):
        xlsx = _make_valid_xlsx(
            ('not_int', None, None, None, None, None),  # bad row – year invalid
        )
        message = str(DbManagement.import_from_excel(xlsx))
        assert 'Errors: 1' in message

    # ── error handling ───────────────────────────────────────────────────────

    def test_empty_file_raises_value_error(self, db):
        empty_xlsx = _make_xlsx()   # workbook with no rows at all
        with pytest.raises(ValueError, match="empty"):
            DbManagement.import_from_excel(empty_xlsx)

    def test_bad_row_does_not_abort_valid_rows(self, db):
        """One invalid row must not block the valid rows around it."""
        xlsx = _make_valid_xlsx(
            _customer_row(bg_vor_nr='BG-001/24'),
            ('bad_year', None, None, None, None, None),  # invalid – year not int
            _customer_row(bg_vor_nr='BG-003/24', name_en='THIRD LTD'),
        )
        DbManagement.import_from_excel(xlsx)
        # Both valid rows were imported
        assert Customer.objects.count() == 2
        assert Customer.objects.filter(BG_Vor_Nr='BG-001/24').exists()
        assert Customer.objects.filter(BG_Vor_Nr='BG-003/24').exists()

    # ── end-to-end with real file ─────────────────────────────────────────────

    @pytest.mark.integration
    def test_real_test_data_file_imports(self, db):
        """
        End-to-end: import the actual test_data.xlsx from the project root.
        The file has 3 data rows (1 real company + 2 dummy rows).
        """
        test_file = Path(__file__).resolve().parents[2] / 'test_data.xlsx'
        with open(test_file, 'rb') as f:
            message = str(DbManagement.import_from_excel(f))

        assert Customer.objects.count() == 3
        assert Customer.objects.filter(BG_Vor_Nr='BG-017/24').exists()
        assert 'Created: 3' in message

