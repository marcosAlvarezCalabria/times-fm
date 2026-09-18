"""
Servicio de ingesta y normalización de datos de ventas (Shopify, TPV y CSV genéricos).
"""

import csv
from datetime import datetime, timedelta
import io
import re
from typing import Any, Dict, List, Optional, Tuple
from dateutil import parser as date_parser

from ..types import (
    DailySalesPoint,
    IngestionSummary,
    NormalizedSeries,
    SalesRecord,
)


class NormalizationService:
    """Normaliza y estructura fuentes de datos heterogéneas para el modelo TimesFM."""

    DATE_ALIASES = ["created at", "sale_date", "date", "fecha", "timestamp", "day", "order date"]
    PRODUCT_ALIASES = ["lineitem name", "product", "producto", "item", "sku", "title", "name", "description"]
    QTY_ALIASES = ["lineitem quantity", "quantity", "qty", "cantidad", "units", "units_sold", "volume"]
    REVENUE_ALIASES = ["total sales", "gross sales", "net sales", "revenue", "ingresos", "ventas", "total", "amount"]

    def parse_csv_content(self, raw_text: str) -> Tuple[List[NormalizedSeries], IngestionSummary]:
        """Parsea una cadena de texto CSV e infiere la estructura de columnas."""
        reader = csv.reader(io.StringIO(raw_text.strip()))
        rows = list(reader)
        if not rows:
            raise ValueError("El archivo CSV está vacío.")

        headers = [h.strip().lower() for h in rows[0]]
        date_idx = self._find_column(headers, self.DATE_ALIASES)
        prod_idx = self._find_column(headers, self.PRODUCT_ALIASES)
        qty_idx = self._find_column(headers, self.QTY_ALIASES)
        rev_idx = self._find_column(headers, self.REVENUE_ALIASES)

        if date_idx is None or qty_idx is None:
            raise ValueError(
                f"No se pudieron detectar columnas mínimas de Fecha y Cantidad en: {headers}."
            )

        records: List[SalesRecord] = []
        for line_num, row in enumerate(rows[1:], start=2):
            if not row or len(row) <= max(date_idx, qty_idx):
                continue
            try:
                date_str = self._normalize_date(row[date_idx])
                prod_name = row[prod_idx].strip() if prod_idx is not None and prod_idx < len(row) else "General"
                prod_id = re.sub(r"[^A-Za-z0-9_-]", "-", prod_name).upper()[:24] or "PROD-GEN"
                qty = max(0.0, float(re.sub(r"[^\d.-]", "", row[qty_idx]) or 0.0))
                rev = 0.0
                if rev_idx is not None and rev_idx < len(row):
                    rev = max(0.0, float(re.sub(r"[^\d.-]", "", row[rev_idx]) or 0.0))
                else:
                    rev = qty * 10.0

                records.append(SalesRecord(
                    sale_date=date_str,
                    product_id=prod_id,
                    product_name=prod_name,
                    units_sold=qty,
                    revenue=rev
                ))
            except Exception:
                continue

        if not records:
            raise ValueError("No se encontraron registros de venta válidos tras el parseo.")

        return self._consolidate_series(records, detected_format="CSV")

    def _find_column(self, headers: List[str], aliases: List[str]) -> Optional[int]:
        for idx, h in enumerate(headers):
            for alias in aliases:
                if alias in h:
                    return idx
        return None

    def _normalize_date(self, val: str) -> str:
        clean_val = val.strip()
        dt = date_parser.parse(clean_val, fuzzy=True)
        return dt.strftime("%Y-%m-%d")

    def _consolidate_series(
        self, records: List[SalesRecord], detected_format: str
    ) -> Tuple[List[NormalizedSeries], IngestionSummary]:
        products_map: Dict[str, Dict[str, Any]] = {}
        all_dates: set = set()

        for rec in records:
            all_dates.add(rec.sale_date)
            if rec.product_id not in products_map:
                products_map[rec.product_id] = {
                    "name": rec.product_name,
                    "daily": {},
                    "total_units": 0.0,
                    "total_revenue": 0.0
                }
            entry = products_map[rec.product_id]
            curr_units, curr_rev = entry["daily"].get(rec.sale_date, (0.0, 0.0))
            entry["daily"][rec.sale_date] = (curr_units + rec.units_sold, curr_rev + rec.revenue)
            entry["total_units"] += rec.units_sold
            entry["total_revenue"] += rec.revenue

        sorted_dates = sorted(list(all_dates))
        min_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d").date()
        max_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d").date()
        total_days = (max_date - min_date).days + 1

        normalized_list: List[NormalizedSeries] = []
        for pid, data in products_map.items():
            full_history: List[DailySalesPoint] = []
            for i in range(total_days):
                curr = min_date + timedelta(days=i)
                ds = curr.strftime("%Y-%m-%d")
                u, r = data["daily"].get(ds, (0.0, 0.0))
                full_history.append(DailySalesPoint(date=ds, units_sold=round(u, 2), revenue=round(r, 2)))

            avg_daily = data["total_units"] / max(1, total_days)
            normalized_list.append(NormalizedSeries(
                product_id=pid,
                product_name=data["name"],
                history=full_history,
                total_units=round(data["total_units"], 2),
                total_revenue=round(data["total_revenue"], 2),
                average_daily_sales=round(avg_daily, 2)
            ))

        summary = IngestionSummary(
            total_rows_parsed=len(records),
            products_count=len(normalized_list),
            date_start=sorted_dates[0],
            date_end=sorted_dates[-1],
            detected_format=detected_format,
            sample_products=[p.product_name for p in normalized_list[:5]]
        )
        return normalized_list, summary
