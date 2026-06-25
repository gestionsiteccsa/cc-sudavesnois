"""Tests pour le module home.data.collecte_data."""

from django.test import SimpleTestCase

from home.data.collecte_data import (
    city_data,
    get_available_cities,
    get_dates_verre,
    get_jour_ordures,
    validate_city_data,
)


class CollecteDataTestCase(SimpleTestCase):
    def test_validate_city_data_ok(self):
        anomalies = validate_city_data()
        self.assertEqual(anomalies, [], f"Anomalies: {anomalies}")

    def test_get_available_cities_returns_sorted(self):
        cities = get_available_cities()
        self.assertEqual(cities, sorted(cities))
        self.assertIn("Fourmies", cities)
        self.assertIn("Anor", cities)

    def test_get_dates_verre_mono_jour(self):
        dates = get_dates_verre("Anor")
        self.assertIsNotNone(dates)
        self.assertEqual(len(dates), 24)  # 12 mois x 2 ans
        # Triees par ordre chronologique
        self.assertEqual(dates, sorted(dates))

    def test_get_dates_verre_fourmies_avec_jour(self):
        dates_lundi = get_dates_verre("Fourmies", "lundi")
        self.assertIsNotNone(dates_lundi)
        self.assertGreater(len(dates_lundi), 0)
        self.assertEqual(dates_lundi, sorted(dates_lundi))

    def test_get_dates_verre_unknown_commune(self):
        self.assertIsNone(get_dates_verre("Atlantis"))

    def test_get_jour_ordures_string(self):
        # Pour Anor, c'est un string "mercredi"
        jour, rue = get_jour_ordures("Anor")
        self.assertEqual(jour, "mercredi")
        self.assertIsNone(rue)

    def test_get_jour_ordures_fourmies_par_rue(self):
        jour, rue = get_jour_ordures("Fourmies", "rue gambetta")
        self.assertEqual(jour, "lundi")
        self.assertEqual(rue, "rue gambetta")

    def test_get_jour_ordures_unknown_commune(self):
        self.assertEqual(get_jour_ordures("Atlantis"), (None, None))

    def test_get_jour_ordures_case_insensitive(self):
        jour, _ = get_jour_ordures("Fourmies", "RUE GAMBETTA")
        self.assertEqual(jour, "lundi")

    def test_dates_format_iso(self):
        for commune in get_available_cities():
            dates = get_dates_verre(commune)
            if dates:
                for d in dates:
                    # Doit etre parseable en YYYY-MM-DD
                    import datetime

                    datetime.datetime.strptime(d, "%Y-%m-%d")

    def test_city_data_not_empty(self):
        self.assertGreater(len(city_data), 0)
        for commune, data in city_data.items():
            self.assertIn("verre", data, f"{commune} sans 'verre'")
            self.assertIn("ordures", data, f"{commune} sans 'ordures'")
