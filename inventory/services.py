import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

# Clase para obtener la tasa de cambio
class ExchangeRateService:
    # Margen de ganancia del 40%
    MARGIN_PERCENTAGE = Decimal('40')

    # Método para obtener la tasa de cambio
    def get_rate(self, currency_code: str) -> tuple[Decimal, bool]:
        try:
            response = httpx.get(settings.EXCHANGE_RATE_API_URL, timeout=5.0) 
            response.raise_for_status()
            data = response.json()
            rates = data.get('rates', {})

            # Si la moneda no se encuentra en la respuesta de la API se usa la tasa por defecto
            if currency_code not in rates:
                logger.warning("Moneda %s no encontrada en la respuesta de la API", currency_code)
                return Decimal(str(settings.DEFAULT_EXCHANGE_RATE)), True

            return Decimal(str(rates[currency_code])), False
        # Si hay un error al obtener la tasa de cambio, se usa la tasa por defecto
        except (httpx.RequestError, httpx.HTTPStatusError, Exception) as error:
            logger.error("Error al obtener tasa de cambio: %s. Usando tasa por defecto.", str(error))
            return Decimal(str(settings.DEFAULT_EXCHANGE_RATE)), True

    # Método para calcular el precio de venta del libro
    def calculate_selling_price(self, book, currency_code: str) -> dict:
        rate, used_fallback = self.get_rate(currency_code)

        cost_usd = Decimal(str(book.get("cost_usd", 0)))
        cost_local = (cost_usd * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        margin_multiplier = Decimal('1') + (self.MARGIN_PERCENTAGE / Decimal('100'))
        selling_price = (cost_local * margin_multiplier).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'book_id': book.get("id"),
            'cost_usd': float(cost_usd),
            'exchange_rate': float(rate),
            'cost_local': float(cost_local),
            'margin_percentage': int(self.MARGIN_PERCENTAGE),
            'selling_price_local': float(selling_price),
            'currency': currency_code,
            'used_fallback_rate': used_fallback,
            'calculation_timestamp': datetime.now(tz=timezone.utc).isoformat(),
        }
