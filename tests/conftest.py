import pytest
from engine.sales_agent import crm

@pytest.fixture(autouse=True)
def isolated_crm(tmp_path, monkeypatch):
    monkeypatch.setattr(crm, 'DB_PATH', str(tmp_path / 'crm.sqlite3'))
    crm.init_crm_db()
    for i in range(4):
        crm.LeadManager.add_lead(dict(company_name=f'Synthetic {i}', website='https://example.com',
            niche='Synthetic reporting', country='TEST', contact_email=f'test{i}@example.com', tier='TEST',
            pain_point='TEST', custom_hook='TEST', personalized_subject='Synthetic pilot test',
            personalized_body='Synthetic data only', status='DRAFT'))
