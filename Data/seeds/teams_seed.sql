-- ============================================================
-- Seeding initial des équipes de Ligue 1 — footballapp_db
-- USAGE : psql -U postgres -d footballapp_db -f Data/seeds/teams_seed.sql
--
-- Ce fichier est idempotent : il n'insère que si l'équipe est absente.
-- Utile pour : nouvelle installation locale, image Docker PostgreSQL.
-- ============================================================

INSERT INTO teams (name, logo_url) VALUES
    ('Angers',         'https://brandlogos.net/wp-content/uploads/2022/07/angers_sco-logo_brandlogos.net_1yevi-512x512.png'),
    ('Auxerre',        'https://brandlogos.net/wp-content/uploads/2018/12/aj_auxerre-logo_brandlogos.net_fwi5k-512x512.png'),
    ('Le Havre',       'https://brandlogos.net/wp-content/uploads/2018/12/le_havre_ac-logo_brandlogos.net_yx6ic-512x622.png'),
    ('Lens',           'https://brandlogos.net/wp-content/uploads/2018/12/rc-lens-logo-512x512.png'),
    ('Lille',          'https://brandlogos.net/wp-content/uploads/2021/01/lille-osc-logo-512x512.png'),
    ('Lorient',        'https://brandlogos.net/wp-content/uploads/2018/11/fc_lorient-logo_brandlogos.net_flntm-512x512.png'),
    ('Lyon',           'https://brandlogos.net/wp-content/uploads/2015/03/Olympique-Lyonnais-logo-512x594.png'),
    ('Marseille',      'https://brandlogos.net/wp-content/uploads/2014/12/olympique_de_marseille-logo_brandlogos.net_fnliw-512x657.png'),
    ('Metz',           'https://brandlogos.net/wp-content/uploads/2025/08/fc_metz-logo_brandlogos.net_umt95-512x737.png'),
    ('Monaco',         'https://brandlogos.net/wp-content/uploads/2018/11/AS-Monaco-FC-512x885.png'),
    ('Nantes',         'https://brandlogos.net/wp-content/uploads/2022/07/fc_nantes-logo_brandlogos.net_cawqm-512x512.png'),
    ('Nice',           'https://brandlogos.net/wp-content/uploads/2022/07/ogc_nice-logo_brandlogos.net_1nwir-512x512.png'),
    ('Paris FC',       'https://brandlogos.net/wp-content/uploads/2013/10/paris-fc-1969-vector-logo.png'),
    ('Paris SG',       'https://brandlogos.net/wp-content/uploads/2014/12/paris-saint-germain-logo-512x512.png'),
    ('Rennes',         'https://brandlogos.net/wp-content/uploads/2018/12/stade_rennais_fc-logo_brandlogos.net_eiekb-512x512.png'),
    ('Stade Brestois', 'https://brandlogos.net/wp-content/uploads/2022/07/stade_brestois_29-logo_brandlogos.net_llie5-512x512.png'),
    ('Strasbourg',     'https://brandlogos.net/wp-content/uploads/2019/01/rc_strasbourg_alsace-logo_brandlogos.net_sutxm-512x512.png'),
    ('Toulouse',       'https://brandlogos.net/wp-content/uploads/2022/07/toulouse_fc-logo_brandlogos.net_mpshb-512x512.png')
ON CONFLICT (name) DO NOTHING;
